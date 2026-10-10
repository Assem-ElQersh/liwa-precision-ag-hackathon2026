# Liwa Precision Agriculture — Arab Youth Space Hackathon 2026

**Team:** ليوا الخضراء (Green Liwa)  
**Theme:** Precision Agriculture & Crop Intelligence  
**Track:** PoC Submission & Pitching  
**Deadline:** 11 October 2026  

---

## Problem Statement

> **Identify areas of vegetation stress and soil salinity in Liwa, Abu Dhabi agricultural fields so that field managers can prioritize inspection and optimize irrigation in desert reclamation zones.**

The UAE has only **0.5–0.7%** arable land (~400–600 km²). In Liwa Oasis, desert agriculture faces three critical challenges:
1. **Unknown soil conditions** — salinity, moisture, groundwater distribution
2. **Water scarcity** — no freshwater infrastructure, reliance on energy-intensive desalination
3. **Irrigation inefficiency** — flood irrigation wastes 30–50% water through evaporation

---

## Solution Overview: Three-Phase Integrated System

| Phase | Component | Technology | Status |
|-------|-----------|------------|--------|
| **1** | **Satellite Survey** | Hyperspectral (EnMAP, Tanager) + Multispectral (Sentinel-2) | 🛰️ **PoC Core** |
| **2** | **Solar Desalination** | Off-grid PV-powered RO unit for saline/groundwater | 🔧 Hardware (Leen) |
| **3** | **AI Precision Irrigation** | Soil sensors + ML-driven drip irrigation per plant | 🤖 Software (Assem) |

**This repository contains the Phase 1 PoC: Satellite-based crop intelligence for Liwa.**

---

## Repository Structure

```
liwa-precision-ag-hackathon2026/
├── .gitignore
├── README.md
├── requirements.txt
├── LICENSE
├── data/
│   ├── raw/                 # Downloaded satellite data (gitignored)
│   ├── processed/           # Generated indices, masks (gitignored)
│   ├── external/            # Reference datasets (CSV)
│   └── aoi/                 # AOI GeoJSON files
├── notebooks/
│   ├── 00_data_access.ipynb          # STAC search, COG streaming
│   ├── 01_gdal_fundamentals.ipynb    # GDAL 15 worked examples
│   ├── 02_hyperspectral_analysis.ipynb  # EnMAP/Tanager cube analysis
│   ├── 03_spectral_indices.ipynb     # NDVI, NDWI, SI, MSI, NMDI...
│   ├── 04_time_series_analysis.ipynb # Monthly composites, phenology
│   ├── 05_ml_baselines.ipynb         # Sklearn: RF, LR, classification
│   ├── 06_deep_learning_eo.ipynb     # PyTorch MLP on hyperspectral
│   └── 07_change_detection.ipynb     # NDBI, patch-based change
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── stac_client.py
│   │   ├── downloader.py
│   │   └── preprocess.py
│   ├── features/
│   │   ├── __init__.py
│   │   ├── spectral_indices.py
│   │   └── hyperspectral.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── baseline.py
│   │   └── deep_learning.py
│   └── utils/
│       ├── __init__.py
│       ├── visualization.py
│       └── metrics.py
├── outputs/
│   ├── figures/             # Maps, charts for presentation
│   └── predictions/         # GeoTIFF outputs
├── presentation/
│   └── slides.pdf
├── docs/
│   ├── methodology.md
│   ├── data_sources.md
│   └── hackathon_research_notes.md
└── training_materials/
    ├── gdal/
    ├── hyperspectral/
    ├── machine_learning/
    ├── deep_learning/
    └── time_series/
```

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Assem-ElQersh/liwa-precision-ag-hackathon2026.git
cd liwa-precision-ag-hackathon2026

# Install dependencies
pip install -r requirements.txt

# Install GDAL system dependency (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y gdal-bin libgdal-dev

# Or on Colab: runtime installs automatically in notebooks

# Launch Jupyter
jupyter lab
```

**Start with:** `notebooks/00_data_access.ipynb` → Search and access Liwa data

---

## Data Sources

| Source | Type | Resolution | Bands | Access |
|--------|------|------------|-------|--------|
| **Sentinel-2 L2A** | Multispectral | 10m / 20m | 13 | Planetary Computer (open) |
| **Landsat 8/9** | Multispectral + Thermal | 30m | 11 | Planetary Computer (open) |
| **EnMAP** | Hyperspectral | 30m | 205 (VNIR-SWIR) | DLR Geoservice (registration) |
| **Planet Tanager** | Hyperspectral | 20m | 205 (400–1700nm) | Open Archive (STAC) |
| **Copernicus DEM** | Elevation | 30m | 1 | Open |
| **Global Fields** | Vector (Parquet) | Field-level | - | Open |

**Liwa AOI:** `data/aoi/liwa_aoi.geojson` — Bounding box `[53.5, 22.8, 54.2, 23.3]` (EPSG:4326)

---

## Key Spectral Indices for Liwa

| Category | Index | Formula | Purpose |
|----------|-------|---------|---------|
| **Vegetation** | NDVI | (NIR-Red)/(NIR+Red) | General vegetation health |
| | EVI | 2.5×(NIR-Red)/(NIR+6Red-7.5Blue+1) | Atmospheric resistance |
| | SAVI | (NIR-Red)/(NIR+Red+0.5)×1.5 | Soil background correction |
| | NDRE | (NIR-RedEdge)/(NIR+RedEdge) | Chlorophyll sensitivity |
| **Water** | NDWI | (Green-NIR)/(Green+NIR) | Canopy water content |
| | MSI | SWIR/NIR | Moisture stress |
| | NMDI | (NIR-(SWIR1-SWIR2))/(NIR+(SWIR1-SWIR2)) | Drought monitoring |
| **Salinity** | SI | (SWIR-Red)/(SWIR+Red) | **Primary salinity indicator** |
| | SI3 | (SWIR2-SWIR1)/(SWIR2+SWIR1) | Salt crust detection |
| | BI | √(SWIR²+Red²) | Surface brightness |
| | CSRI | (SWIR/NIR)×(1-NDVI) | Combined crop-salt stress |

---

## Notebook Pipeline

```mermaid
graph LR
    A[00_data_access] --> B[01_gdal_fundamentals]
    B --> C[02_hyperspectral_analysis]
    C --> D[03_spectral_indices]
    D --> E[04_time_series_analysis]
    E --> F[05_ml_baselines]
    F --> G[06_deep_learning_eo]
    G --> H[07_change_detection]
    H --> I[Outputs: Maps + Models]
```

1. **00_data_access** — STAC search, COG streaming, data inventory
2. **01_gdal_fundamentals** — GDAL CLI mastery (inspect, warp, calc, VRT, COG)
3. **02_hyperspectral_analysis** — Cube reading, spectral signatures, unmixing
4. **03_spectral_indices** — 20+ indices for vegetation, water, salinity
5. **04_time_series_analysis** — Monthly composites, phenology, anomalies
6. **05_ml_baselines** — Random Forest, Logistic Regression baselines
7. **06_deep_learning_eo** — PyTorch MLP on hyperspectral (AVIRIS example)
8. **07_change_detection** — NDBI differencing, patch-based analysis

---

## Team

| Member | Role | Expertise |
|--------|------|-----------|
| **Youmna Abdelkarim** | Team Lead | Coordination, project management |
| **Assem ElQersh** | Data Science Lead | Satellite analysis, ML/DL, GDAL |
| **Malak Sameh** | Satellite Data Research | EnMAP, Tanager, Sentinel-2 data access |
| **Leen Sheikh Mohamed** | Hardware & Mechanical | Solar desalination, sensor enclosure, CAD |
| **Maha AlDhaheri** | Policy, Finance & Strategy | UAE water security, funding, business case |

---

## Methodology

### Phase 1: Satellite Survey (PoC)
1. **AOI Definition** — Liwa agricultural fields (~418 km² total, focus on pivot irrigation circles)
2. **Data Acquisition** — Sentinel-2 monthly (Oct 2024–Sep 2025), EnMAP/Tanager hyperspectral snapshots
3. **Preprocessing** — Cloud masking (SCL), atmospheric correction, coregistration
4. **Index Computation** — 20+ indices targeting salinity, water stress, vegetation health
5. **Time Series Analysis** — Phenology detection, anomaly identification, trend analysis
6. **ML Classification** — Random Forest on indices → stress/salinity classes
7. **Deep Learning** — MLP on hyperspectral cubes → per-pixel crop health
8. **Change Detection** — NDVI differencing, BFAST-style break detection
9. **Output Generation** — GeoTIFF maps, statistics, validation metrics

### Validation Strategy
- **Spatial split** — Field-level train/test separation (no pixel leakage)
- **Ground truth** — FAO soil database, UAE soil surveys, literature values
- **Cross-validation** — 5-fold spatial CV on field parcels
- **Metrics** — Macro-F1, per-class accuracy, confusion matrices

---

## PoC Submission Requirements ✅

| Requirement | Status | Location |
|-------------|--------|----------|
| Public GitHub repo | ✅ | This repo |
| README.md | ✅ | Root |
| Jupyter notebook (end-to-end) | ✅ | `notebooks/00_data_access.ipynb` → `07_change_detection.ipynb` |
| Pinned requirements.txt | ✅ | Root |
| Example input/output | ✅ | `data/external/`, `outputs/` |
| No credentials/restricted imagery | ✅ | `.gitignore` enforced |
| Presentation slides (PDF) | 📝 | `presentation/slides.pdf` |

---

## Master Provenance Ledger

| The Empirical Finding / Metric | Exact Script/Notebook Name | Analytical Deduction (What this rules out/forces next) |
| :--- | :--- | :--- |
| Onboarding rules require baseline multispectral image before hyperspectral/DL | `https://spaceacademy-hackathons.space.gov.ae/onboarding` | Forces Sentinel-2 MSI baseline before attempting Tanager/EnMAP deep models. |
| Commercial Planet & gIQ data excluded from Phase 2 PoC | `https://spaceacademy-hackathons.space.gov.ae/onboarding` | Rules out relying on proprietary commercial Planet data for PoC submission. |
| Prior team DEMO metrics used synthetic/mock datasets | `liwa_green_poc_AR.pdf` | Rules out using prior team outputs as ground truth. Forces all pipelines to process real Sentinel-2/Tanager STAC imagery. |
| Malak's South Liwa screening (`Green-Liwa`) evaluated 28 km² bare dune site ($53.89^\circ E, 23.07^\circ N$) | `Green-Liwa/South_Liwa_Salinity_Screening (1).ipynb` | Demonstrates that optical SI/NDSI on uncultivated bare sand can be confounded by soil brightness (53rd percentile rank). |
| VOGI / NDRE necessity on active date palm fields | `Green-Liwa/South_Liwa_Site_Selection_Report-1.pdf` | While bare sand reclamation screening uses SI/NDSI, active date palm farms require VOGI ($R_{740}/R_{720}$) and NDRE for chlorophyll water stress detection. |
| GCP Earth Engine Project ID registered | `horizontal-cab-473909-s3` | Enables GEE Python API integration (`ee.Initialize(project='horizontal-cab-473909-s3')`). |
| `leafmap` Planetary Computer Titiler endpoint conflict | `notebooks/00_data_access.ipynb` | Forces `os.environ["TITILER_ENDPOINT"] = "https://titiler.xyz"` setting prior to map rendering. |
| Tanager atmospheric water vapor noise windows at 1350–1450nm and 1800–1950nm | `notebooks/02_hyperspectral_analysis.ipynb` | Mandates spectral band filtering function `is_water_vapor(wl)` leaving 143 clean bands. |
| Spatial autocorrelation leakage between adjacent pixels | `notebooks/05_ml_baselines.ipynb` | Mandates parcel/field-level spatial cross-validation rather than random pixel splitting on real scenes. |
| 5 EnMAP L2A scenes downloaded in Kaggle (408.3–440.6 MB each, total 2.14 GB) | `notebooks/08_kaggle_enmap_dataset_downloader.ipynb` | Validates DLR STAC discovery (`collections=["ENMAP_HSI_L2A"]`) and HTTP Basic Auth (`Azzoma`), creating Kaggle dataset `assemelqersh/enmap-liwa-l2a`. |
| Planet Tanager 426-band HDF5 surface reflectance array structure | `https://hypercoast.org/examples/tanager/` | Mandates reading `HDFEOS/GRIDS/HYP/Data Fields/surface_reflectance` and scaling center wavelengths from $\mu m$ to $nm$ (`eo:center_wavelength * 1000`). |
| CDSE STAC v1.1.0 & OAuth2 Keycloak token endpoints (`cdse-public`) | `https://stac.dataspace.copernicus.eu/v1/` | Enables direct Sentinel-2 STAC CQL2 filtering and zipper downloads inside Kaggle (`notebooks/00_data_access.ipynb`). |
| CDSE Browser dataset ID `S2_L2A_CDAS` & OData productType `S2MSI2A` | `https://browser.dataspace.copernicus.eu/` | Confirms SCL Class 5 (Bare Soil/Desert) and Process API payload structure (`POST https://sh.dataspace.copernicus.eu/api/v1/process`). |
| `sentinel2-liwa-l2a`, `tanager-liwa-l2a`, and `copernicus-dem-liwa` STAC downloaders & `dataset-metadata.json` packagers verified | `notebooks/00_data_access.ipynb` | Standardizes all 4 target EO datasets into `/kaggle/working/` for seamless conversion to Kaggle Datasets prior to EDA. |
| Workspace-wide dynamic dependency check (`install_if_missing`) injected into all project notebooks | All `.ipynb` notebooks in `notebooks/`, `Green-Liwa`, `813-hyperspectral-hackathon-main` | Prevents `ModuleNotFoundError` for `planetary_computer`, `pystac_client`, `rasterio`, `geopandas`, `folium`, and `h5py` across Kaggle environments. |
| Modular dataset download architecture implemented (`00a_sentinel2_downloader`, `00b_tanager_downloader`, `00c_copernicus_dem_downloader`, `00d_cdse_sentinel2_downloader`, `08_kaggle_enmap_dataset_downloader`) | `notebooks/00a_sentinel2_downloader.ipynb` through `00d_cdse_sentinel2_downloader.ipynb` | Prevents Kaggle output directory path contamination and ensures each dataset is packaged and published independently as its own Kaggle dataset (`assemelqersh/*`). |
| Element84 Earth Search STAC endpoint (`https://earth-search.aws.element84.com/v1`) verified (HTTP 200 for all bands) | `notebooks/00a_sentinel2_downloader.ipynb` | Bypasses Planetary Computer 403 SAS token forbidden error and guarantees public AWS S3 COG band downloads for Sentinel-2. |
| `sentinel2-liwa-l2a` dataset creation empirically validated on Kaggle (2.3 GB across 4 multi-band scenes) | `notebooks/00a_sentinel2_downloader.ipynb` | Confirms complete 7-band Sentinel-2 time series acquisition over Liwa Oasis on Kaggle. |
| `tanager-liwa-l2a` dataset creation empirically validated on Kaggle (899.47 MB 426-band HDF5 cube) | `notebooks/00b_tanager_downloader.ipynb` | Confirms complete 426-band Tanager-1 hyperspectral surface reflectance acquisition over Liwa Oasis on Kaggle. |
| `copernicus-dem-liwa` dataset creation empirically validated on Kaggle (92.8 MB across 2 30m DEM tiles) | `notebooks/00c_copernicus_dem_downloader.ipynb` | Confirms complete 30m Copernicus GLO-30 topographic elevation data acquisition over Liwa Oasis on Kaggle. |
| CDSE Zipper API download streaming (`zipper.dataspace.copernicus.eu`) integrated into `00d_cdse_sentinel2_downloader.ipynb` | `notebooks/00d_cdse_sentinel2_downloader.ipynb` | Ensures actual Sentinel-2 L2A `.zip` product archives are written into `/kaggle/working/` for dataset creation. |
| `cdse-sentinel2-liwa` dataset creation empirically validated on Kaggle (1.42 GB across 2 SAFE zip archives) | `notebooks/00d_cdse_sentinel2_downloader.ipynb` | Confirms complete CDSE Keycloak authenticated SAFE zip archive streaming over Liwa Oasis on Kaggle. |
| All 5 Kaggle dataset URLs & absolute `/kaggle/input/` paths recorded in `docs/data_sources.md` & `notebooks/00_data_access.ipynb` | `docs/data_sources.md` & `notebooks/00_data_access.ipynb` | Establishes immutable project reference for dataset URLs and candidate mount paths. |
| Hyperspectral EDA pipeline (water vapor masking 1350–1450nm/1800–1950nm & 4-component NMF unmixing) verified | `notebooks/02_hyperspectral_analysis.ipynb` | Enables sub-pixel date palm canopy vs. bare sand vs. saline crust unmixing across mounted EnMAP and Tanager cubes. |
| Multispectral & Hyperspectral vegetation and soil salinity index calculations (NDVI, SAVI, SI, NDRE) verified | `notebooks/03_spectral_indices.ipynb` | Establishes baseline vegetation health and soil salinity mapping over Sentinel-2 and hyperspectral imagery. |
| End-to-end execution of `02_hyperspectral_analysis.ipynb` and `03_spectral_indices.ipynb` empirically validated | `notebooks/02_hyperspectral_analysis.ipynb` & `notebooks/03_spectral_indices.ipynb` | Confirms complete local and Kaggle runtime readiness for EDA, hyperspectral unmixing, and spectral index visualization. |
| EPSG:4326 DEM topographic slope gradient calculation unit mismatch (degrees vs meters) | `notebooks/00_kaggle_master_eda.ipynb` | Scaling transform step sizes by latitude cosine ($111000 \cdot \cos(\text{lat})$) converts degree grid spacing to meters, eliminating uniform $90^\circ$ saturation and rendering accurate $0^\circ-25^\circ$ dune slopes. |
| Copernicus DEM 30m Topographic Slope distribution (Min=$0.0^\circ$, Max=$41.1^\circ$, Mean=$4.4^\circ$) | `notebooks/00_kaggle_master_eda.ipynb` | Identifies flat interdune sabkha basins ($<3.0^\circ$) where saline agricultural runoff and groundwater accumulate versus steep dune slipfaces ($>15.0^\circ$). |
| Sentinel-2 L2A Vegetation Health (NDVI Max=$0.8563$, Mean=$0.0831$; SAVI Max=$0.7182$, Mean=$0.0800$) | `notebooks/00_kaggle_master_eda.ipynb` | Confirms highly localized date palm cultivation along the Liwa crescent oasis embedded within a high-albedo desert sand background ($0.0-0.1$ NDVI). |
| EnMAP 224-Band Hyperspectral NMF Endmember Curves | `notebooks/00_kaggle_master_eda.ipynb` | Resolves distinct Red Edge ($680-750\text{nm}$) and SWIR gypsum/halite absorption ($1450\text{nm}, 1900\text{nm}$) signatures across 4 sub-pixel land cover components. |
| Production dataset path routing refactored for `04_time_series_analysis`, `05_ml_baselines`, `06_deep_learning_eo`, `07_change_detection` | `notebooks/04_time_series_analysis.ipynb` through `07_change_detection.ipynb` | Replaces tutorial placeholder data (California Housing, Breast Cancer, 1992 AVIRIS Indiana) with mounted Kaggle datasets (`/kaggle/input/**/`). |
| Sentinel-2 Multi-temporal Vegetation Phenology (4 scenes Sept 2025: S2B/S2C tiles 39QYF, 39QZF, 40QBL) | `notebooks/04_time_series_analysis.ipynb` | Mean NDVI ($0.0109-0.0855$) bounds vegetative fraction to $<3\%$ across desert tiles; S2C single-pixel saturation ($0.9997$ NDVI) dictates prioritizing SAVI ($0.7083-0.8351$) for robust soil-adjusted canopy monitoring. |
| Random Forest 5-Fold Spatial CV Baseline (Accuracy=$0.9999 \pm 0.0002$, Macro-F1=$0.9973 \pm 0.0054$, Class Balance: Sand $99.12\%$, Stressed $0.66\%$, Healthy $0.22\%$) | `notebooks/05_ml_baselines.ipynb` | Statistically verifies $>99\%$ bare sand background dominance; confirms non-linear decision tree boundaries accurately isolate sparse date palm canopies from stressed sabkha margins without false-positive desert alarms. |

---





## Training Materials

All preparatory training materials from the hackathon are organized in `training_materials/`:

```
training_materials/
├── gdal/
│   ├── GDAL_End_to_End_SpaceAcademy2026.pdf
│   └── GDAL_End_to_End_SpaceAcademy2026.pptx
├── hyperspectral/
│   ├── Hyperspectral_Imaging_SpaceAcademy2026.pdf
│   ├── UASA_hackathon_intro_hyperspectral_RS.pdf
│   └── W1_intro_to_RS.pdf
├── machine_learning/
│   ├── W6_intro_to_ML.pdf
│   └── W6_intro_to_ML.pptx
├── deep_learning/
│   ├── AYSH2026_kickoff_training_9_9_2026.pdf
│   └── hackathon_webinar_talk_en.pdf
└── time_series/
    ├── Ghaf_Root_Sep26.pdf
    └── lecture.pdf
```

Reference datasets in `data/external/`:
- `california_housing.csv` — Regression example
- `breast_cancer.csv` — Classification example

---

## Timeline

| Date | Milestone |
|------|-----------|
| **Sep 20** | Team registered & approved |
| **Sep 27** | Team confirmed, tasks assigned |
| **Oct 3** | Mid-check meeting |
| **Oct 11** | **PoC Submission Deadline** |
| **Oct 15+** | Pitching & Judging |
| **Nov+** | Incubation (top 7 teams) |

---

## License

- **Code:** MIT License — see [LICENSE](LICENSE)
- **Documentation:** CC-BY-4.0
- **Data:** Respective provider licenses (Copernicus, DLR, Planet)

---

## Acknowledgments

- **Arab Youth Space Hackathon 2026** organizers
- **Space42** / **UAESA** for training materials
- **Microsoft Planetary Computer** for Sentinel-2/Landsat access
- **DLR** for EnMAP open data policy
- **Planet** for Tanager open archive

---

## Contact

**Team Lead:** Youmna Abdelkarim — yomnahazem112@gmail.com  
**Technical Lead:** Assem ElQersh — assem.elqersh@gmail.com  
**GitHub:** https://github.com/Assem-ElQersh/liwa-precision-ag-hackathon2026

---

*"From space, we see the invisible. From data, we grow the impossible."*
