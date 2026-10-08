# Data Sources Reference

## Primary Satellite Data

### Sentinel-2 MSI Level-2A
- **Provider:** Copernicus / ESA
- **Access:** Microsoft Planetary Computer STAC API
- **Endpoint:** `https://planetarycomputer.microsoft.com/api/stac/v1`
- **Collection:** `sentinel-2-l2a`
- **Bands:** 13 bands (10m/20m/60m)
- **Temporal:** 2015-present, 5-day revisit (2 satellites)
- **License:** Free and open (CC-BY-4.0)
- **Format:** Cloud-Optimized GeoTIFF (COG) on AWS S3
- **STAC Example:**
  ```python
  catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                        modifier=pc.sign_inplace)
  items = catalog.search(collections=["sentinel-2-l2a"], bbox=[53.5,22.8,54.2,23.3],
                         datetime="2024-10-01/2025-09-30", query={"eo:cloud_cover":{"lt":30}})
  ```

### Landsat 8/9 Collection 2 Level-2
- **Provider:** USGS / NASA
- **Access:** Planetary Computer STAC
- **Collection:** `landsat-c2-l2`
- **Bands:** 11 bands (30m) + Thermal (100m resampled to 30m)
- **Temporal:** 1982-present (L8: 2013+, L9: 2021+), 16-day revisit
- **License:** Public domain
- **Use Case:** Surface temperature (ST_B10), long-term trends

---

## Hyperspectral Data

### EnMAP (Environmental Mapping and Analysis Program)
- **Provider:** DLR (German Aerospace Center)
- **Access:** DLR Geoservice STAC API (requires registration)
- **Endpoint:** `https://enmap.geoservice.dlr.de/stac`
- **Registration:** https://enmap.geoservice.dlr.de
- **Collection:** `enmap`
- **Bands:** 205 bands (VNIR: 400-1000nm, 95 bands; SWIR: 1000-2500nm, 110 bands)
- **Spectral Resolution:** ~6.5nm (VNIR), ~10nm (SWIR)
- **Spatial Resolution:** 30m
- **Swath:** 30km
- **Temporal:** 2022-present, ~4-day revisit
- **License:** Free for scientific use (registration required)
- **Data Format:** GeoTIFF (L2A surface reflectance)
- **Documentation:** https://www.enmap.org/

### Planet Tanager (Open Archive)
- **Provider:** Planet Labs
- **Access:** Planet STAC API (open archive)
- **Endpoint:** `https://stac.planet.com/tanager/open`
- **Collection:** `tanager`
- **Bands:** 205 bands (400-1700nm)
- **Spectral Resolution:** ~5nm
- **Spatial Resolution:** 20m
- **Swath:** ~20km
- **Temporal:** 2023-present (growing archive)
- **License:** Open archive (CC-BY-4.0 for open data)
- **Developer Portal:** https://developers.planet.com/docs/data/tanager/
- **Note:** During PoC phase, only open archive data available. Commercial data in incubation.

### PRISMA (Hyperspectral Precursor of the Application Mission)
- **Provider:** ASI (Italian Space Agency)
- **Access:** ASI catalog / PEPS
- **Bands:** 237 bands (400-2500nm)
- **Resolution:** 30m
- **Status:** Operational since 2019

### EMIT (Earth Surface Mineral Dust Source Investigation)
- **Provider:** NASA JPL
- **Access:** NASA LP DAAC / Planetary Computer
- **Collection:** `emit`
- **Bands:** 285 bands (380-2500nm)
- **Resolution:** 60m
- **Platform:** International Space Station
- **License:** Open

---

## Auxiliary Data

### Copernicus DEM (Digital Elevation Model)
- **Provider:** Copernicus / ESA
- **Access:** Planetary Computer / AWS / OpenTopography
- **Resolution:** 30m (GLO-30), 90m (GLO-90)
- **Coverage:** Global
- **License:** Free (CC-BY-4.0)
- **STAC Collection:** `cop-dem-glo-30`
- **Use:** Topography, slope, aspect, drainage, viewshed

### Global Fields Boundary Dataset
- **Provider:** Fields of The World (v3 model)
- **Access:** Hackathon data page (GeoParquet on-demand)
- **Format:** GeoParquet
- **Coverage:** Global, 2024-2025
- **License:** CC-BY
- **Attributes:** Field ID, geometry, crop type (where available), confidence
- **Use:** Field-level analysis, spatial CV splits, parcel statistics

### ERA5-Land Reanalysis
- **Provider:** ECMWF / Copernicus Climate Change Service
- **Access:** CDS API / Planetary Computer / Google Earth Engine
- **Variables:** Temperature, precipitation, ET0, soil moisture, wind
- **Resolution:** 0.1° (~9km), hourly
- **Temporal:** 1981-present
- **License:** Free (Copernicus license)

### CHIRPS (Climate Hazards Group InfraRed Precipitation with Station Data)
- **Provider:** UC Santa Barbara / USGS
- **Access:** Google Earth Engine / CHIRPS website
- **Resolution:** 0.05° (~5km), daily
- **Temporal:** 1981-present
- **License:** Free

### FAO Harmonized World Soil Database (HWSD)
- **Provider:** FAO / IIASA / ISRIC / ISSCAS / JRC
- **Access:** FAO website
- **Resolution:** 30 arc-second (~1km)
- **Attributes:** Soil units, texture, pH, salinity (EC), sodicity (ESP), organic carbon
- **License:** Free for non-commercial
- **Use:** Ground truth proxy for salinity validation

### UAE Soil Surveys
- **Provider:** Environment Agency Abu Dhabi (EAD) / ICBA
- **Access:** Request-based / Published reports
- **Notable:** ICBA UAE Soil Salinity Maps, EAD Liwa groundwater studies

---

## Data Access Patterns

### 1. STAC Search (Recommended)
```python
from pystac_client import Client
import planetary_computer as pc

catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",
                      modifier=pc.sign_inplace)

search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[53.5, 22.8, 54.2, 23.3],
    datetime="2024-10-01/2025-09-30",
    query={"eo:cloud_cover": {"lt": 30}},
    max_items=50
)
items = list(search.items())
```

### 2. COG Streaming (No Download)
```python
import stackstac

stack = stackstac.stack(
    items,
    assets=["B02","B03","B04","B08","B11","B12","SCL"],
    bounds=[53.5, 22.8, 54.2, 23.3],
    resolution=10,
    epsg=32640,
    chunksize=2048
)
# Lazy loading - only reads when .compute() or .values called
```

### 3. GDAL /vsicurl/ (Direct Cloud Access)
```python
from osgeo import gdal

# Inspect metadata
gdal.Info("/vsicurl/https://sentinel-cogs.s3.us-west-2.amazonaws.com/.../B04.tif")

# Extract window
gdal.Translate("window.tif", "/vsicurl/https://.../B04.tif",
               srcWin=[1000, 1000, 512, 512])
```

### 4. HyperCoast (Hyperspectral Visualization)
```python
import hypercoast

# EnMAP
ds = hypercoast.read_enmap("path/to/enmap/data")
m = hypercoast.Map()
m.add_enmap(ds, vmin=0, vmax=0.3)
m.add("spectral")  # Click pixel → spectral signature

# Tanager
ds = hypercoast.read_tanager("path/to/tanager/data")
m.add_tanager(ds)
m.add("spectral")
```

---

## Liwa-Specific Data Notes

### Sentinel-2 Coverage for Liwa
- **Path/Row:** Multiple overlapping tiles (43RGP, 43RHP, etc.)
- **Revisit:** ~5 days with both S2A/S2B
- **Cloud Cover:** Generally low in UAE desert (<10% typical), but check summer months
- **Best Periods:** Oct-Apr (growing season), clear skies

### EnMAP Coverage for Liwa
- **Check:** DLR Geoservice catalog for acquisitions over 23.0°N, 53.8°E
- **Tasking:** Possible for registered users (request specific acquisition)
- **Archive:** Search existing scenes since 2022

### Tanager Coverage for Liwa
- **Check:** Planet STAC open archive for 22.8-23.3°N, 53.5-54.2°E
- **Archive Growth:** New scenes added regularly
- **Quality:** Radiance data, requires atmospheric correction for reflectance

---

## Data Volume Estimates

| Dataset | Scene Size | Time Series (12 months) | Notes |
|---------|------------|------------------------|-------|
| Sentinel-2 L2A (10 bands, 10m) | ~240 MB/scene | ~2.9 GB (12 scenes) | Stream via COG |
| EnMAP L2A (205 bands, 30m) | ~1.2 GB/scene | ~1.2 GB (1 scene) | Download required |
| Tanager (205 bands, 20m) | ~800 MB/scene | Variable | Stream via COG |
| Copernicus DEM 30m | ~50 MB/tile | One-time | Local cache |

---

## Licensing Summary

| Source | License | PoC Use | Incubation |
|--------|---------|---------|------------|
| Sentinel-2 | CC-BY-4.0 | ✅ | ✅ |
| Landsat | Public Domain | ✅ | ✅ |
| EnMAP | Scientific Use | ✅ (register) | ✅ |
| Planet Tanager (Open) | CC-BY-4.0 | ✅ | ✅ |
| Planet (Commercial) | Commercial | ❌ | ✅ (selected teams) |
| Copernicus DEM | CC-BY-4.0 | ✅ | ✅ |
| Global Fields | CC-BY | ✅ | ✅ |
| ERA5/CHIRPS | Free | ✅ | ✅ |

---

## Quick Links

- **Planetary Computer:** https://planetarycomputer.microsoft.com/
- **DLR EnMAP:** https://enmap.geoservice.dlr.de/
- **Planet Tanager:** https://developers.planet.com/docs/data/tanager/
- **Copernicus Data Space:** https://dataspace.copernicus.eu/
- **HyperCoast:** https://github.com/giswqs/hypercoast
- **StackSTAC:** https://stackstac.readthedocs.io/
- **GDAL:** https://gdal.org/


---

## Published Kaggle Datasets & Absolute Mount Paths

All 5 core Earth Observation datasets over Liwa Oasis are published on Kaggle under user `assemelqirsh`:

### Dataset URLs

1. **Planet Tanager-1 426-Band Hyperspectral:** https://www.kaggle.com/datasets/assemelqirsh/tanager-liwa-l2a
2. **Sentinel-2 L2A Multispectral Time-Series:** https://www.kaggle.com/datasets/assemelqirsh/sentinel2-liwa-l2a
3. **EnMAP 224-Band L2A Hyperspectral Cubes:** https://www.kaggle.com/datasets/assemelqirsh/enmap-liwa-l2a
4. **Copernicus DEM 30m Elevation:** https://www.kaggle.com/datasets/assemelqirsh/copernicus-dem-liwa
5. **CDSE Authenticated Sentinel-2 SAFE Zip Archives:** https://www.kaggle.com/datasets/assemelqirsh/cdse-sentinel2-liwa

### Absolute Kaggle Mount Paths

When mounted on Kaggle notebooks, datasets are accessible via standard input paths:

- **CDSE Sentinel-2 Archives:**
  - Base Directory: `/kaggle/input/cdse-sentinel2-liwa` or `/kaggle/input/datasets/assemelqirsh/cdse-sentinel2-liwa`
  - Manifest / Metadata: `/kaggle/input/datasets/assemelqirsh/cdse-sentinel2-liwa/S2C_MSIL1C_...SAFE/manifest.safe`

- **EnMAP L2A Hyperspectral:**
  - Base Directory: `/kaggle/input/enmap-liwa-l2a/enmap_liwa_dataset` or `/kaggle/input/datasets/assemelqirsh/enmap-liwa-l2a/enmap_liwa_dataset`
  - Spectral Image Cubes: `/kaggle/input/datasets/assemelqirsh/enmap-liwa-l2a/enmap_liwa_dataset/ENMAP01-.../SPECTRAL_IMAGE.TIF`

- **Sentinel-2 L2A Time-Series:**
  - Base Directory: `/kaggle/input/sentinel2-liwa-l2a` or `/kaggle/input/datasets/assemelqirsh/sentinel2-liwa-l2a`
  - Scene Bands: `/kaggle/input/datasets/assemelqirsh/sentinel2-liwa-l2a/S2_L2A_.../B02.tif`

- **Planet Tanager-1 HDF5:**
  - Base Directory: `/kaggle/input/tanager-liwa-l2a` or `/kaggle/input/datasets/assemelqirsh/tanager-liwa-l2a`
  - Reflectance HDF5: `/kaggle/input/datasets/assemelqirsh/tanager-liwa-l2a/20250224_145149_32_4001_surface_reflectance.h5`

- **Copernicus DEM 30m:**
  - Base Directory: `/kaggle/input/copernicus-dem-liwa` or `/kaggle/input/datasets/assemelqirsh/copernicus-dem-liwa`
  - DEM Rasters: `/kaggle/input/datasets/assemelqirsh/copernicus-dem-liwa/Copernicus_DSM_COG_10_N23_00_E054_00_DEM.tif`
