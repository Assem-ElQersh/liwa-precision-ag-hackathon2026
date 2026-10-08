# Arab Youth Space Hackathon: 813 Challenge - Data Documentation

This document serves as the master reference for all data resources, execution strategies, and constraints for the **Green Liwa (ليوا الخضراء)** team competing in the **Precision Agriculture & Crop Intelligence** theme.

## 1. Hackathon Data Constraints & Phases
The hackathon rolls out data access progressively. It is critical to design the Proof of Concept (PoC) around what is currently guaranteed.

- **Phase 1: Preparatory & Open Exploration**
  - Open multispectral data (Sentinel-2, Landsat).
  - Open hyperspectral data (EnMAP) & Planet Tanager open-archive.
- **Phase 2: PoC Development (Current Phase)**
  - Use **any open Earth observation data** (Sentinel-1, Sentinel-2, Landsat).
  - Use Planet Tanager open-archive data only (per GitHub examples).
  - *Constraint:* Satellite data must form the core of the PoC. Commercial Planet data and gIQ access are NOT provided in this phase.
- **Phase 3: Incubation (Selected Teams)**
  - Commercial Planet data may be provided.
  - Satellite 813 and MBZ-SAT data upon availability.

### 🚫 Mistakes That Sink a PoC
*   **Waiting for premium data:** Build an open-data baseline immediately. Upgrade later.
*   **Downloading the largest AOI:** Match resolution and extent to the actual field size (Liwa Oasis farms).
*   **Using one image for change:** Use justified baseline and comparison observations.
*   **Ignoring quality flags:** Apply cloud/shadow masks before interpreting results.
*   **Reporting index as ground truth:** Call it a proxy or screening result.
*   **Random train/test splits:** Separate training and testing spatially to prevent data leakage.
*   **Treating hyperspectral like RGB:** Remove noisy bands (e.g., water vapor windows), standardize, and compare against a baseline.
*   **Starting with Deep Learning blindly:** Establish an explainable baseline first.

---

## 2. Exhaustive Data Sources & Access Tier Matrix

To ensure zero friction during execution, all Earth Observation data sources are categorized below by their exact access method, API authentication requirements, and current availability:

### 🟢 Tier 1: Fully Open & Direct Access (No Credentials Required)
These datasets are immediately accessible programmatically via open STAC APIs or Cloud-Optimized GeoTIFF (COG) URLs.

| Dataset | Provider | Bands / Resolution | API / Access Method | Access URL / Collection |
|---|---|---|---|---|
| **Sentinel-2 L2A** | Copernicus / Microsoft | 13 bands (10m / 20m) | Open STAC API (`planetary-computer`) | `https://planetarycomputer.microsoft.com/api/stac/v1` (`sentinel-2-l2a`) |
| **Landsat 8/9** | USGS / Microsoft | 11 bands + Thermal (30m) | Open STAC API (`planetary-computer`) | `https://planetarycomputer.microsoft.com/api/stac/v1` (`landsat-c2-l2`) |
| **Planet Tanager-1** | Planet Labs | 426 bands (30m, 380–2500nm) | Open STAC Catalog (CC-BY 4.0) | `https://www.planet.com/data/stac/tanager-core-imagery/catalog.json` |
| **Global Fields** | Fields of The World | GeoParquet Vector Boundaries | Direct HTTP Download | Pre-computed 2024/2025 agricultural field parcels |
| **Copernicus DEM** | Copernicus | Elevation / Slope (30m) | Open STAC API | `planetary-computer` (`cop-dem-glo-30`) |
| **ESA WorldCover** | ESA | Land Cover Classes (10m) | Open STAC API | `planetary-computer` (`esa-worldcover`) |
| **NASA EMIT** | NASA LP DAAC | 285 bands (60m) | Open NASA Earthdata / STAC | `https://earthdata.nasa.gov` |

---

### 🟡 Tier 2: Free Self-Serve Registration Required
These datasets are free for research/academic use but require registering an account to obtain an API key or session token.

| Dataset | Provider | Bands / Resolution | Registration / Download Portal | Auth Method / Credentials |
|---|---|---|---|---|
| **EnMAP L2A & SPECTRAL_EARTH** | DLR (Germany) | 224 bands (30m COG) | `https://download.geoservice.dlr.de/ENMAP/files/` (`L2A/`, `SPECTRAL_EARTH/`) | Active Account: `azzoma` (SSO Enabled) |
| **ASI PRISMA** | ASI (Italy) | 240 bands (30m, 400–2500nm) | `https://prisma.asi.it/` | Free portal account for L1/L2 scene ordering |
| **Copernicus CDSE** | European Union | Full Sentinel constellation | `https://dataspace.copernicus.eu/` | OData / S3 API tokens via `sentinelhub` or `openeo` |
| **USGS EarthExplorer** | USGS | Historical Landsat archive | `https://earthexplorer.usgs.gov/` | Free USGS EROS login for bulk scene downloads |
| **Bayanat.ae & Abu Dhabi Open Data** | UAE Government | Spatial vectors & Ag statistics | `https://bayanat.ae` | Free portal download (agricultural holdings & crop statistics) |




---

### 🔴 Tier 3: Request-Only / Incubation Phase Only (NOT Provided in Phase 2 PoC)
These resources are strictly reserved for top teams selected for Phase 3 Incubation (Nov 2026 – Feb 2027). **Do NOT build PoC code that depends on these resources.**

| Dataset / Platform | Provider | Access Restriction | Status in Phase 2 PoC |
|---|---|---|---|
| **Commercial Planet VHR (3–5m)** | Planet Labs | 4–8 multispectral daily imagery | ❌ Excluded — Provided only to selected Incubation teams |
| **Space42 gIQ Platform Access** | Space42 | Pre-configured cloud GPU platform | ❌ Excluded — Granted during Phase 3 Incubation |
| **Satellite 813 Mission Data** | UAESA / Space42 | 205 bands (20m, 400–1700nm) | ❌ Excluded — Subject to operational availability in Phase 3 |
| **MBZ-SAT Imagery** | MBRSC / UAE | High-resolution satellite data | ❌ Excluded — Subject to operational availability in Phase 3 |

---

## 3. How to Prepare Environment & Resolve Common Execution Errors

### 1. Fix Directory Creation Bugs (`pyogrio` / `geopandas` `No such file or directory`)
When executing notebooks in Google Colab or new environments, directory trees do not exist by default. Always execute:
```python
import os
# Ensure directory tree exists before writing GeoJSON or GeoTIFF outputs
os.makedirs("../data/aoi", exist_ok=True)
os.makedirs("../data/raw", exist_ok=True)
os.makedirs("../data/processed", exist_ok=True)
os.makedirs("../outputs/figures", exist_ok=True)
os.makedirs("../outputs/predictions", exist_ok=True)
```

### 2. Fix `leafmap` Titiler Endpoint Conflict
Always include this in the first code cell of every session before importing `leafmap`:
```python
import os
os.environ["TITILER_ENDPOINT"] = "https://titiler.xyz"
```

### 3. Handle Large Tanager HDF5 Files (1–5 GB) Efficiently
Instead of saving large files locally, stream HDF5 scenes into memory or use 1 MB chunked HTTP streaming:
```python
import h5py
import io
import requests

# Direct in-memory reading without saving to disk
response = requests.get(hdf5_url, stream=True)
with h5py.File(io.BytesIO(response.content), "r") as f:
    sr_data = f["HDFEOS/GRIDS/HYP/Data Fields/surface_reflectance"][:]
```


---

## 4. Recommended Pretrained Models & Repositories
Pretrained models are allowed provided we disclose them and respect their licenses. The following GitHub repositories provide excellent open-source foundations for hyperspectral agriculture:

*   **[AABNassim/spectral_earth](https://github.com/AABNassim/spectral_earth):** Pretrained hyperspectral models (ResNet, ViT) trained on EnMAP data. Excellent starting point for fine-tuning land-cover or crop-type classification.
*   **[mc2295/hyperspectralplants](https://github.com/mc2295/hyperspectralplants):** Deep learning architectures for plant health classification using hyperspectral cubes.
*   **[ridvansalihkuzu/hyperview_eagleeyes](https://github.com/ridvansalihkuzu/hyperview_eagleeyes):** Implementations for soil parameter estimation using hyperspectral satellite images. Highly relevant for **soil salinity mapping** in the UAE.
*   **[fadi-07/Awesome-Wheat-HSI-DeepLearning](https://github.com/fadi-07/Awesome-Wheat-HSI-DeepLearning):** A curated list of deep learning methodologies (CNNs, Transformers) for hyperspectral crop disease and nutrient estimation.

---

## 5. Execution Strategy (Cloud-Native)

**Do NOT download hyperspectral datasets locally.** Tanager and EnMAP HDF5 files range from 1–5 GB per scene. 

### Recommended Environment: Google Colab
The hackathon explicitly provides Colab integrations for all starter notebooks.
1.  Colab has native, fast connections to Google Cloud Storage and Planetary Computer buckets.
2.  It resolves the complex geospatial environment setups (GDAL, `pystac-client`, `leafmap`, `xarray`) seamlessly.
3.  We will use Python to query the STAC API, calculate indices in the cloud, and only download the resulting statistics (e.g., CSVs or lightweight PNG maps).

### ⚠️ Critical Note: The `leafmap` Titiler Endpoint Conflict
When running Planetary Computer (Sentinel-2) cells before Planet Tanager cells in the same session, `leafmap` caches a `PlanetaryComputerEndpoint` that breaks subsequent COG layer loading.
**The Fix:** Always run this before any map cell:
```python
import os
os.environ["TITILER_ENDPOINT"] = "https://titiler.xyz"
```

### Water Vapor Band Exclusion
When processing Tanager data, always exclude the atmospheric water vapor windows to prevent noisy predictions:
```python
def is_water_vapor(wl):
    return (1350 <= wl <= 1450) or (1800 <= wl <= 1950)
```

---

## 6. Official Problem Statement Template & Application

Per the Onboarding Guide, every project must be framed using the standardized problem statement template:
> *"We want to [identify, measure, classify, predict, or monitor] **[phenomenon]** in **[location]** during **[period]** so that **[user]** can make **[decision]**."*

### Green Liwa Official Problem Statement:
> **"We want to monitor date palm vegetation stress and map soil salinity dynamics in the Liwa Oasis during the 2024–2025 agricultural season using Sentinel-2 MSI time series and open hyperspectral data (Planet Tanager / EnMAP) so that farm managers and agricultural authorities in Abu Dhabi can target irrigation efficiency and soil remediation interventions."**

---

## 7. Official 12-Step Participant Workflow
1. **Choose one official theme**: Theme 02 (Precision Agriculture & Crop Intelligence).
2. **Write precise problem statement**: Defined above.
3. **Choose small Area of Interest (AOI)**: Liwa Oasis agricultural fields (clipped via Global Fields Geoparquet).
4. **Visit hackathon data page**: Review all available resources on `/data`.
5. **Read GitHub repo overview**: Explored starter repository `813-hyperspectral-hackathon`.
6. **Open EO quick-start notebook**: Verified STAC, COGs, and band structures.
7. **Run quick-start notebook unchanged**: Environment verification.
8. **Open theme-specific notebook**: `01_agriculture_crop_intelligence.ipynb`.
9. **Start with Sentinel-2 or Landsat**: Establish open-data baseline (NDVI, NDWI, Red-Edge).
10. **Produce one simple result**: Baseline Sentinel-2 crop health map & stress index.
11. **Record data provenance**: Document sensors, dates, band numbers, and processing steps.
12. **Add hyperspectral/DL only when justified**: Use Tanager/EnMAP narrow bands to detect soil salinity (NSI/SWIR) & early stress before broad-band detection.

---

## 8. 16-Point Quick-Start Compliance Checklist
- [x] Selected Theme 02: Precision Agriculture & Crop Intelligence.
- [x] Formulated precise problem statement with target user and decision.
- [x] Selected manageable AOI (Liwa Oasis, Abu Dhabi).
- [x] Identified 2024–2025 time range.
- [x] Reviewed hackathon data portal (`/data`).
- [x] Analyzed official GitHub starter notebooks.
- [x] Established Sentinel-2 open data baseline.
- [x] Verified cloud-native STAC streaming approach (Google Colab / Kaggle).
- [x] Identified hyperspectral justification (narrow-band spectral signature for soil salinity & early date palm water stress).
- [x] Implemented water vapor window band filtering (1350–1450 nm & 1800–1950 nm).
- [x] Solved `leafmap` titiler endpoint cache conflict (`TITILER_ENDPOINT = "https://titiler.xyz"`).
- [x] Spatially separated training and testing fields to eliminate spatial data leakage.
- [x] Ensured strict compliance with non-commercial data restriction during Phase 2.
- [x] Created master provenance ledger in `README.md`.
- [x] Zero API key leaks or hardcoded local path assumptions.
- [x] Reproducible notebook design ready for cloud execution.

---

## 9. Official FAQs & Rules

*   **Can we use external public datasets?**
    *   Yes — any open dataset is allowed.
*   **Are pretrained models allowed?**
    *   Yes, provided you disclose them and respect their licenses.
*   **What output formats are expected?**
    *   Will be disclosed during the submission phase.
*   **PoC Phase Data Usage Rule:**
    *   You can use *any* open EO data (not limited to Planet open archive). However, satellite data **must** form the core of the PoC.

---
*Document auto-generated during the planning and research phase.*

