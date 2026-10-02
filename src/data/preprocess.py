"""Preprocessing utilities for satellite data."""
import xarray as xr
import numpy as np
import rioxarray
from typing import List, Optional
from shapely.geometry import mapping
import geopandas as gpd


SCL_CLOUD_CLASSES = [0, 1, 3, 8, 9, 10, 11]  # NO_DATA, SATURATED, CLOUD_SHADOW, CLOUD_MED, CLOUD_HIGH, CIRRUS, SNOW


def apply_scl_mask(
    stack: xr.DataArray,
    scl_band: str = "SCL",
    cloud_classes: Optional[List[int]] = None
) -> xr.DataArray:
    """Apply Sentinel-2 Scene Classification Layer cloud mask."""
    if cloud_classes is None:
        cloud_classes = SCL_CLOUD_CLASSES
    
    scl = stack.sel(band=scl_band)
    
    # Create cloud mask
    cloud_mask = xr.zeros_like(scl, dtype=bool)
    for cls in cloud_classes:
        cloud_mask = cloud_mask | (scl == cls)
    
    # Apply to data bands
    data_bands = [b for b in stack.band.values if b != scl_band]
    masked = stack.sel(band=data_bands).copy()
    
    for band in data_bands:
        masked.loc[dict(band=band)] = masked.sel(band=band).where(~cloud_mask)
    
    # Add cloud mask as coordinate
    masked = masked.assign_coords(cloud_mask=(("time", "y", "x"), cloud_mask.values))
    
    # Log cloud coverage
    cloud_pct = cloud_mask.mean(dim=["y", "x"]) * 100
    print(f"Cloud coverage per scene: {cloud_pct.values}")
    
    return masked


def create_monthly_composite(
    stack: xr.DataArray,
    method: str = "median",
    min_valid: int = 2
) -> xr.DataArray:
    """Create monthly composites from time series."""
    if method == "median":
        monthly = stack.resample(time="MS").median(skipna=True)
    elif method == "max":
        monthly = stack.resample(time="MS").max(skipna=True)
    elif method == "min":
        monthly = stack.resample(time="MS").min(skipna=True)
    elif method == "mean":
        monthly = stack.resample(time="MS").mean(skipna=True)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Filter months with too few valid observations
    valid_count = stack.notnull().sum(dim="time")
    monthly = monthly.where(valid_count >= min_valid)
    
    print(f"Monthly composites: {monthly.sizes['time']} months")
    for t in monthly.time.values:
        print(f"  {str(t)[:7]}")
    
    return monthly


def clip_to_aoi(
    stack: xr.DataArray,
    aoi_path: str,
    crs: Optional[str] = None
) -> xr.DataArray:
    """Clip stack to Area of Interest."""
    aoi = gpd.read_file(aoi_path)
    if crs and aoi.crs != crs:
        aoi = aoi.to_crs(crs)
    
    clipped = stack.rio.clip([mapping(geom) for geom in aoi.geometry], crs=stack.rio.crs, drop=True)
    return clipped


def coregister_stack(
    reference: xr.DataArray,
    target: xr.DataArray,
    resampling: str = "bilinear"
) -> xr.DataArray:
    """Coregister target stack to reference grid."""
    # Reproject target to reference CRS and resolution
    target_reproj = target.rio.reproject_match(reference, resampling=resampling)
    return target_reproj


def compute_spectral_indices(stack: xr.DataArray) -> xr.DataArray:
    """Compute common spectral indices from Sentinel-2 bands."""
    eps = 1e-6
    indices = {}
    
    # Band shortcuts
    B02 = stack.sel(band="B02")
    B03 = stack.sel(band="B03")
    B04 = stack.sel(band="B04")
    B05 = stack.sel(band="B05")
    B06 = stack.sel(band="B06")
    B07 = stack.sel(band="B07")
    B08 = stack.sel(band="B08")
    B8A = stack.sel(band="B8A")
    B11 = stack.sel(band="B11")
    B12 = stack.sel(band="B12")
    
    # Vegetation
    indices["NDVI"] = (B08 - B04) / (B08 + B04 + eps)
    indices["EVI"] = 2.5 * (B08 - B04) / (B08 + 6*B04 - 7.5*B02 + 1 + eps)
    indices["SAVI"] = (B08 - B04) / (B08 + B04 + 0.5) * 1.5
    indices["NDRE"] = (B08 - B05) / (B08 + B05 + eps)
    indices["NDRE2"] = (B08 - B06) / (B08 + B06 + eps)
    indices["CIred_edge"] = B08 / B05 - 1
    
    # Water
    indices["NDWI"] = (B03 - B08) / (B03 + B08 + eps)
    indices["NDWI_Gao"] = (B08 - B11) / (B08 + B11 + eps)
    indices["MSI"] = B11 / B08
    indices["NMDI"] = (B08 - (B11 - B12)) / (B08 + (B11 - B12) + eps)
    
    # Salinity
    indices["SI"] = (B11 - B04) / (B11 + B04 + eps)
    indices["SI3"] = (B12 - B11) / (B12 + B11 + eps)
    indices["BI"] = (B11**2 + B04**2)**0.5
    
    # Convert to DataArray
    index_da = xr.concat(list(indices.values()), dim="index")
    index_da = index_da.assign_coords(index=list(indices.keys()))
    index_da.name = "spectral_indices"
    
    return index_da
