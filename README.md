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
