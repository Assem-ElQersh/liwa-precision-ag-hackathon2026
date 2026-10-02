# Methodology Documentation

## Overview

This document describes the technical methodology for the Phase 1 PoC: **Satellite-based Crop Intelligence for Liwa Oasis**.

---

## 1. Area of Interest (AOI)

**Location:** Liwa Oasis, Abu Dhabi, UAE  
**Coordinates:** Bounding box `[53.5, 22.8, 54.2, 23.3]` (EPSG:4326)  
**Area:** ~418 km² total arable land in UAE (0.5-0.7% of total)  
**Target:** Pivot irrigation circles and row crops in Liwa crescent

**AOI File:** `data/aoi/liwa_aoi.geojson`

---

## 2. Data Acquisition

### 2.1 Primary: Sentinel-2 L2A (Multispectral)
- **Source:** Microsoft Planetary Computer STAC API
- **Collection:** `sentinel-2-l2a`
- **Bands:** B02(490nm), B03(560nm), B04(665nm), B05(705nm), B06(740nm), B07(783nm), B08(842nm), B8A(865nm), B11(1610nm), B12(2190nm), SCL
- **Resolution:** 10m (VIS/NIR), 20m (Red Edge/SWIR), 60m (Coastal/Water Vapor)
- **Temporal:** 5-day revisit, Oct 2024 – Sep 2025 (growing season)
- **Filter:** Cloud cover < 30%
- **Access:** Signed COG URLs via `/vsicurl/` streaming

### 2.2 Secondary: Landsat 8/9 C2 L2
- **Source:** Planetary Computer
- **Use:** Thermal band (ST_B10) for surface temperature, longer temporal baseline
- **Resolution:** 30m

### 2.3 Hyperspectral: EnMAP
- **Source:** DLR Geoservice (requires registration)
- **Collection:** `enmap`
- **Bands:** 205 bands, 400-2500nm (VNIR: 400-1000nm, SWIR: 1000-2500nm)
- **Resolution:** 30m
- **Use:** Soil mineralogy, detailed salinity mapping, vegetation biochemistry

### 2.4 Hyperspectral: Planet Tanager (Open Archive)
- **Source:** Planet STAC (`stac.planet.com/tanager/open`)
- **Collection:** `tanager`
- **Bands:** 205 bands, 400-1700nm
- **Resolution:** 20m
- **Use:** Complementary hyperspectral, higher spatial resolution than EnMAP

### 2.5 Auxiliary Data
- **Copernicus DEM 30m:** Topography, slope, drainage networks
- **Global Fields Boundary (GeoParquet):** Field parcel boundaries for 2024-2025
- **ERA5-Land / CHIRPS:** Rainfall, temperature, ET0 reanalysis

---

## 3. Preprocessing Pipeline

### 3.1 Sentinel-2 Preprocessing
```python
# 1. STAC Search
items = search_sentinel2(bbox=LIWA_BBOX, timerange="2024-10-01/2025-09-30", max_cloud=30)

# 2. Stack as COG DataArray (lazy)
stack = stackstac.stack(items, assets=bands, bounds=LIWA_BBOX, resolution=10, epsg=32640)

# 3. Cloud Masking (SCL)
masked = apply_scl_mask(stack, scl_band="SCL")
# SCL classes masked: 0,1,3,8,9,10,11

# 4. Monthly Composites
monthly = create_monthly_composite(masked, method="median")

# 5. Spectral Indices
indices = compute_all_indices(monthly)
```

### 3.2 Coregistration
All data reprojected to **EPSG:32640 (UTM Zone 40N)** at **10m resolution** for Sentinel-2 alignment.

### 3.3 Hyperspectral Preprocessing
- EnMAP: L2A surface reflectance, geometric correction
- Tanager: Radiance to reflectance conversion
- Spectral smoothing (Savitzky-Golay)
- Bad band removal (water absorption, edges)

---

## 4. Spectral Index Computation

### 4.1 Vegetation Indices (13)
| Index | Formula | Sensitivity |
|-------|---------|-------------|
| NDVI | (NIR-Red)/(NIR+Red) | General biomass |
| EVI | 2.5×(NIR-Red)/(NIR+6Red-7.5Blue+1) | Atmosphere/soil resistant |
| SAVI | (NIR-Red)/(NIR+Red+0.5)×1.5 | Soil background |
| NDRE | (NIR-RedEdge)/(NIR+RedEdge) | Chlorophyll |
| NDRE2 | (NIR-RedEdge2)/(NIR+RedEdge2) | Chlorophyll |
| CIred_edge | NIR/RedEdge - 1 | Chlorophyll |
| GNDVI | (NIR-Green)/(NIR+Green) | Chlorophyll |
| REIP | 700+40×((Red+RedEdge3)/2-RedEdge)/(RedEdge2-RedEdge) | Red edge position |

### 4.2 Water Stress Indices (6)
| Index | Formula | Interpretation |
|-------|---------|----------------|
| NDWI | (Green-NIR)/(Green+NIR) | Canopy water |
| NDWI_Gao | (NIR-SWIR1)/(NIR+SWIR1) | Canopy water |
| MSI | SWIR1/NIR | Moisture stress ↑ = stress |
| NMDI | (NIR-(SWIR1-SWIR2))/(NIR+(SWIR1-SWIR2)) | Drought |
| LSWI | (NIR-SWIR1)/(NIR+SWIR1) | Equivalent to NDWI_Gao |
| MNDWI | (Green-SWIR1)/(Green+SWIR1) | Open water |

### 4.3 Soil Salinity Indices (8) — **Critical for Liwa**
| Index | Formula | Interpretation |
|-------|---------|----------------|
| SI | (SWIR1-Red)/(SWIR1+Red) | **Primary salinity** |
| SI1 | SWIR1/NIR | Salt crust |
| SI2 | (SWIR2-Red)/(SWIR2+Red) | Salinity |
| SI3 | (SWIR2-SWIR1)/(SWIR2+SWIR1) | Salt crust |
| SRSI | SWIR1/Green | Simplified |
| CSRI | (SWIR1/NIR)×(1-NDVI) | Crop-salt stress |
| BI | √(SWIR1²+Red²) | Brightness |
| NDVI-SI combo | NDVI × (1-SI) | Vegetation-salinity |

---

## 5. Time Series Analysis

### 5.1 Monthly Composites
- Median composite per month (robust to outliers)
- Minimum 2 valid observations per month
- 12 months: Oct 2024 – Sep 2025

### 5.2 Phenology Metrics
- **SOS (Start of Season):** First date NDVI > 20% of peak
- **POS (Peak of Season):** Maximum NDVI date
- **EOS (End of Season):** Last date NDVI > 20% of peak
- **LOS (Length of Season):** EOS - SOS (days)
- **Peak Value:** Maximum NDVI

### 5.3 Anomaly Detection
- Rolling 5-month z-score
- Flag anomalies > 2σ from seasonal baseline
- Identify unexpected stress events

---

## 6. Machine Learning

### 6.1 Baseline: Random Forest
- **Features:** 20+ spectral indices (monthly median + std)
- **Target:** Salinity class (Low/Moderate/High/Severe) or Stress class
- **CV:** 5-fold spatial block CV (24×24 pixel blocks, 2px buffer)
- **Hyperparameters:** n_estimators=200, max_depth=20, class_weight=balanced

### 6.2 Baseline: Logistic Regression
- **Features:** Standardized indices
- **Regularization:** L2 (C=1.0)
- **Multi-class:** Multinomial

### 6.3 Deep Learning: Spectral MLP
- **Architecture:** Input(bands) → 32 → ReLU → 16 → ReLU → Output(classes)
- **Input:** Hyperspectral (EnMAP: 205 bands, Tanager: 205 bands) or Indices
- **Training:** Adam, lr=0.001, batch=64, early stopping (patience=10)
- **Validation:** Spatial block split (same as RF)

### 6.4 Spatial Cross-Validation
Following hackathon DL notebook methodology:
- 24×24 pixel tiles
- 2-pixel buffer exclusion
- Fold assignment: `(row//24 + 2*(col//24)) % 5`
- Train: folds 0,1,2 | Val: fold 3 | Test: fold 4

---

## 7. Change Detection

### 7.1 Index Differencing
- **NDVI Change:** NDVI_t2 - NDVI_t1
- **Threshold:** -0.1 (vegetation loss), +0.1 (vegetation gain)
- **Binary Mask:** Change < threshold → 1 (changed)

### 7.2 Patch-Based Analysis
- 4×4 grid (16 patches) → 2×2 refinement (4 patches) → 2×2 final
- Transition scoring: max |Δindex| between consecutive dates
- Rank patches by transition strength

---

## 8. Output Generation

### 8.1 GeoTIFF Products (COG)
| Product | Description | Format |
|---------|-------------|--------|
| `ndvi_monthly_*.tif` | Monthly NDVI composites | COG, Float32 |
| `salinity_si.tif` | Salinity Index (median) | COG, Float32 |
| `water_ndwi.tif` | Water Index (median) | COG, Float32 |
| `stress_class.tif` | RF classification (0-3) | COG, Byte |
| `change_mask.tif` | NDVI change > threshold | COG, Byte |
| `phenology_sos.tif` | Start of Season (DOY) | COG, UInt16 |

### 8.2 Statistics & Reports
- Per-field statistics (mean, std, min, max per index)
- Confusion matrices (spatial CV)
- Phenology calendar per field
- Anomaly detection log

---

## 9. Validation Strategy

| Aspect | Method |
|--------|--------|
| **Spatial Independence** | Block-based CV (no pixel leakage) |
| **Ground Truth** | FAO Harmonized World Soil Database, UAE soil surveys |
| **Literature Benchmarks** | Published salinity thresholds for UAE desert soils |
| **Cross-Sensor** | Compare Sentinel-2 vs EnMAP vs Tanager on overlap |
| **Temporal Consistency** | Check seasonal patterns match crop calendar |

---

## 10. Reproducibility

- **Environment:** `requirements.txt` pinned versions
- **Data Access:** STAC catalogs (no manual downloads)
- **Random Seeds:** 42 (ML), 42 (DL), 42 (spatial splits)
- **Pipeline:** Notebooks 00→07 executable in order
- **Outputs:** COG format, documented in `outputs/`

---

## 11. Limitations & Future Work

### Limitations
- No ground truth for Liwa specifically (using proxy data)
- EnMAP/Tanager coverage not guaranteed for all dates
- Single growing season (no inter-annual validation)
- Cloud gaps in Sentinel-2 time series

### Incubation Phase (Phase 3)
- Commercial Planet data (3m, daily)
- gIQ analytics platform
- Satellite 813 / MBZ-SAT data
- Field IoT sensor deployment (Leen's hardware)
- Pilot irrigation optimization

---

## References

1. Hackathon training materials (GDAL, Hyperspectral, ML, DL, Time Series)
2. Planetary Computer STAC API documentation
3. DLR EnMAP Product Guide
4. Planet Tanager Open Archive Specification
5. FAO Soil Salinity Assessment Guidelines
6. UAE Water Security Strategy 2036
7. "Remote Sensing of Soil Salinity" - Metternicht & Zinck (2003)
8. "Hyperspectral Indices for Salinity" - Various IEEE papers
