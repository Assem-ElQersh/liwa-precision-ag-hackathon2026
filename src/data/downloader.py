"""COG download and streaming utilities."""
import os
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
from osgeo import gdal

gdal.UseExceptions()

# Configure GDAL for cloud access
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"] = "EMPTY_DIR"
os.environ["GDAL_HTTP_MAX_RETRY"] = "3"
os.environ["GDAL_HTTP_RETRY_DELAY"] = "1"


def download_cog(url: str, output_path: str, progress: bool = True) -> str:
    """Download a COG to local file using GDAL."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Use GDAL translate for download
    ds = gdal.Open(f"/vsicurl/{url}")
    if ds is None:
        raise RuntimeError(f"Failed to open COG: {url}")
    
    driver = gdal.GetDriverByName("COG")
    out_ds = driver.CreateCopy(str(output_path), ds, options=["COMPRESS=DEFLATE"])
    out_ds = None
    ds = None
    
    return str(output_path)


def stream_cog_window(
    url: str,
    window: Tuple[int, int, int, int],  # xoff, yoff, xsize, ysize
    band: int = 1,
    as_array: bool = True
) -> np.ndarray:
    """Stream a window from a COG without downloading full file."""
    ds = gdal.Open(f"/vsicurl/{url}")
    if ds is None:
        raise RuntimeError(f"Failed to open COG: {url}")
    
    xoff, yoff, xsize, ysize = window
    band_obj = ds.GetRasterBand(band)
    arr = band_obj.ReadAsArray(xoff, yoff, xsize, ysize)
    
    ds = None
    return arr


def get_cog_info(url: str) -> dict:
    """Get metadata from COG without downloading."""
    ds = gdal.Open(f"/vsicurl/{url}")
    if ds is None:
        raise RuntimeError(f"Failed to open COG: {url}")
    
    info = {
        "width": ds.RasterXSize,
        "height": ds.RasterYSize,
        "bands": ds.RasterCount,
        "projection": ds.GetProjection(),
        "geotransform": ds.GetGeoTransform(),
        "band_types": [],
        "nodata_values": [],
    }
    
    for i in range(1, ds.RasterCount + 1):
        band = ds.GetRasterBand(i)
        info["band_types"].append(gdal.GetDataTypeName(band.DataType))
        info["nodata_values"].append(band.GetNoDataValue())
    
    ds = None
    return info


def create_local_cog(
    input_path: str,
    output_path: str,
    compress: str = "DEFLATE",
    blocksize: int = 512,
    overviews: bool = True
) -> str:
    """Convert local raster to Cloud-Optimized GeoTIFF."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    ds = gdal.Open(input_path)
    if ds is None:
        raise RuntimeError(f"Failed to open input: {input_path}")
    
    driver = gdal.GetDriverByName("COG")
    options = [
        f"COMPRESS={compress}",
        f"BLOCKSIZE={blocksize}",
        "OVERVIEWS=IGNORE_EXISTING" if overviews else "OVERVIEWS=NONE"
    ]
    
    out_ds = driver.CreateCopy(str(output_path), ds, options=options)
    out_ds = None
    ds = None
    
    return str(output_path)
