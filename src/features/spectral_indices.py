"""Multispectral index computation for Sentinel-2."""
import xarray as xr
import numpy as np
from typing import Dict, Optional


THRESHOLDS = {
    'NDVI': {'bare': 0.1, 'sparse': 0.2, 'moderate': 0.4, 'dense': 0.6},
    'EVI': {'bare': 0.05, 'sparse': 0.15, 'moderate': 0.3, 'dense': 0.5},
    'SAVI': {'bare': 0.1, 'sparse': 0.2, 'moderate': 0.35, 'dense': 0.5},
    'NDWI': {'water': 0.3, 'wet': 0.1, 'dry': -0.1, 'stressed': -0.3},
    'MSI': {'low_stress': 0.5, 'moderate': 1.0, 'high_stress': 1.5},
    'NMDI': {'wet': 0.3, 'normal': 0.0, 'dry': -0.3, 'severe': -0.5},
    'SI': {'low': 0.0, 'moderate': 0.2, 'high': 0.4, 'severe': 0.6},
    'SI3': {'low': -0.2, 'moderate': 0.0, 'high': 0.2, 'severe': 0.4},
    'BI': {'dark': 0.1, 'normal': 0.3, 'bright': 0.5, 'very_bright': 0.7},
}


def compute_all_indices(stack: xr.DataArray) -> xr.DataArray:
    """Compute all spectral indices from Sentinel-2 stack."""
    eps = 1e-6
    
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
    
    indices = {}
    
    # Vegetation
    indices["NDVI"] = (B08 - B04) / (B08 + B04 + eps)
    indices["EVI"] = 2.5 * (B08 - B04) / (B08 + 6*B04 - 7.5*B02 + 1 + eps)
    indices["SAVI"] = (B08 - B04) / (B08 + B04 + 0.5) * 1.5
    indices["NDRE"] = (B08 - B05) / (B08 + B05 + eps)
    indices["NDRE2"] = (B08 - B06) / (B08 + B06 + eps)
    indices["CIred_edge"] = B08 / B05 - 1
    indices["GNDVI"] = (B08 - B03) / (B08 + B03 + eps)
    
    # Water
    indices["NDWI"] = (B03 - B08) / (B03 + B08 + eps)
    indices["NDWI_Gao"] = (B08 - B11) / (B08 + B11 + eps)
    indices["MSI"] = B11 / B08
    indices["NMDI"] = (B08 - (B11 - B12)) / (B08 + (B11 - B12) + eps)
    indices["LSWI"] = (B08 - B11) / (B08 + B11 + eps)
    indices["MNDWI"] = (B03 - B11) / (B03 + B11 + eps)
    
    # Salinity (critical for Liwa)
    indices["SI"] = (B11 - B04) / (B11 + B04 + eps)
    indices["SI1"] = B11 / B08
    indices["SI2"] = (B12 - B04) / (B12 + B04 + eps)
    indices["SI3"] = (B12 - B11) / (B12 + B11 + eps)
    indices["SRSI"] = B11 / B03
    indices["CSRI"] = (B11 / B08) * (1 - (B08 - B04) / (B08 + B04 + eps))
    indices["BI"] = (B11**2 + B04**2)**0.5
    
    # Convert to DataArray
    index_da = xr.concat(list(indices.values()), dim="index")
    index_da = index_da.assign_coords(index=list(indices.keys()))
    index_da.name = "spectral_indices"
    
    return index_da


def classify_index(index_data: xr.DataArray, index_name: str) -> xr.DataArray:
    """Classify index values into categories using thresholds."""
    if index_name not in THRESHOLDS:
        return None
    
    thresh = THRESHOLDS[index_name]
    classes = xr.zeros_like(index_data, dtype=np.uint8)
    
    if index_name in ['NDVI', 'EVI', 'SAVI', 'NDRE', 'GNDVI']:
        # Vegetation: 0=bare, 1=sparse, 2=moderate, 3=dense, 4=very_dense
        classes = xr.where(index_data < thresh['bare'], 0, classes)
        classes = xr.where((index_data >= thresh['bare']) & (index_data < thresh['sparse']), 1, classes)
        classes = xr.where((index_data >= thresh['sparse']) & (index_data < thresh['moderate']), 2, classes)
        classes = xr.where((index_data >= thresh['moderate']) & (index_data < thresh['dense']), 3, classes)
        classes = xr.where(index_data >= thresh['dense'], 4, classes)
        
    elif index_name in ['NDWI', 'NDWI_Gao', 'LSWI', 'MNDWI']:
        # Water: 0=water, 1=wet, 2=normal, 3=dry, 4=stressed
        classes = xr.where(index_data >= thresh['water'], 0, classes)
        classes = xr.where((index_data < thresh['water']) & (index_data >= thresh['wet']), 1, classes)
        classes = xr.where((index_data < thresh['wet']) & (index_data >= thresh['dry']), 2, classes)
        classes = xr.where((index_data < thresh['dry']) & (index_data >= thresh['stressed']), 3, classes)
        classes = xr.where(index_data < thresh['stressed'], 4, classes)
        
    elif index_name in ['MSI']:
        # Moisture stress: 0=low, 1=moderate, 2=high, 3=severe
        classes = xr.where(index_data < thresh['low_stress'], 0, classes)
        classes = xr.where((index_data >= thresh['low_stress']) & (index_data < thresh['moderate']), 1, classes)
        classes = xr.where((index_data >= thresh['moderate']) & (index_data < thresh['high_stress']), 2, classes)
        classes = xr.where(index_data >= thresh['high_stress'], 3, classes)
        
    elif index_name in ['NMDI']:
        # Drought: 0=wet, 1=normal, 2=dry, 3=severe
        classes = xr.where(index_data >= thresh['wet'], 0, classes)
        classes = xr.where((index_data < thresh['wet']) & (index_data >= thresh['normal']), 1, classes)
        classes = xr.where((index_data < thresh['normal']) & (index_data >= thresh['dry']), 2, classes)
        classes = xr.where(index_data < thresh['severe'], 3, classes)
        
    elif index_name in ['SI', 'SI1', 'SI2', 'CSRI']:
        # Salinity: 0=low, 1=moderate, 2=high, 3=severe
        classes = xr.where(index_data < thresh['low'], 0, classes)
        classes = xr.where((index_data >= thresh['low']) & (index_data < thresh['moderate']), 1, classes)
        classes = xr.where((index_data >= thresh['moderate']) & (index_data < thresh['high']), 2, classes)
        classes = xr.where(index_data >= thresh['severe'], 3, classes)
        
    elif index_name in ['SI3']:
        classes = xr.where(index_data < thresh['low'], 0, classes)
        classes = xr.where((index_data >= thresh['low']) & (index_data < thresh['moderate']), 1, classes)
        classes = xr.where((index_data >= thresh['moderate']) & (index_data < thresh['high']), 2, classes)
        classes = xr.where(index_data >= thresh['severe'], 3, classes)
        
    elif index_name in ['BI']:
        classes = xr.where(index_data < thresh['dark'], 0, classes)
        classes = xr.where((index_data >= thresh['dark']) & (index_data < thresh['normal']), 1, classes)
        classes = xr.where((index_data >= thresh['normal']) & (index_data < thresh['bright']), 2, classes)
        classes = xr.where(index_data >= thresh['very_bright'], 3, classes)
    
    return classes
