# Arab Youth Space Hackathon 2026 - Research & Context Notes

Based on a comprehensive review of all notebooks, PDFs, and training materials across the project directories, here are the synthesized insights, methodologies, and technical context for your "Green Liwa" Precision Agriculture project.

## 1. Code Structures, Algorithms & Methodologies
*   **Data Engineering Stack:** Heavy reliance on the modern Cloud-Native EO stack (`pystac-client`, `planetary-computer`, `stackstac`) combined with `rasterio`, `xarray`, `rioxarray`, and `h5py` for multi-dimensional data scaling.
*   **Sentinel-2 Processing:** 
    *   **Cloud Masking:** Explicit use of the Scene Classification Layer (SCL) to map and mask `CLOUD_SHADOWS (3)` and `CLOUD_HIGH_PROBABILITY (9)` using `xarray`.
    *   **Radiometric Calibration:** Conversion of raw Digital Numbers (DN) to Bottom-of-Atmosphere (BOA) reflectance using XML metadata parameters.
*   **Hyperspectral Subsetting (Tanager/EnMAP):** Loading all 400+ bands causes memory bloat. The methodology extracts central wavelengths from metadata and applies nearest-neighbor lookups for specific physical wavelengths (e.g., extracting exactly 705nm for the Red-Edge).
*   **Phenology Tracking:** Using `scipy.signal.find_peaks` and Gaussian filtering on time-series data to detect the Start of Season (SOS), Peak of Season (POS), and End of Season (EOS).
*   **Spectral Unmixing:** Non-negative Matrix Factorization (NMF) via `scikit-learn` is used to find pure spectral endmembers (e.g., isolating soil vs. crop) and calculate fractional pixel abundances.

## 2. Geospatial Processing (GDAL) & Spatial ML
*   **Core GDAL Workflows:**
    *   `gdalwarp` for coregistration, resampling (nearest, average, cubic), and vector clipping.
    *   `gdalbuildvrt` for mosaicing and stacking without duplicating pixel data.
    *   `gdal_calc.py` for band math (calculating indices). *Crucial Trap:* Always cast 8-bit integers to float during calculations to avoid overflow.
    *   `gdal_retile.py` for generating overlapping training chips (e.g., 256x256) for ML models.
*   **Spatial Machine Learning Rules:** When doing Train/Validation/Test splits, standard random shuffling (`shuffle=True`) is strictly prohibited to prevent spatial and temporal data leakage between correlated neighboring pixels.

## 3. Deep Learning & Foundation Models
*   **Foundation Models over Scratch Training:** The materials heavily emphasize using pre-trained foundational models rather than training from scratch:
    *   *Understanding Imagery:* DINOv3, Clay, Prithvi-EO.
    *   *Segmentation & Detection:* SAM / SAM3, RTM-DET, RF-DETR, YOLO.
    *   *Vision + Language:* GeoChat, TerraScope.
*   **Mask R-CNN & ResNet50 (Al-Ghaf Root):** Deep learning (specifically Mask R-CNN with a Feature Pyramid Network) is highlighted for precise, irregularly shaped canopy mapping rather than simple bounding boxes. This is highly applicable for orchard or individual tree tracking in precision agriculture.

## 4. Hyperspectral Insights & Precision Agriculture Applications
*   **The Red Edge (700-750nm):** Healthy vegetation strongly absorbs red/blue and reflects NIR. Hyperspectral data can detect subtle shifts in the "red edge" caused by water stress or nutrient deficiency (e.g., date-palm water stress) *weeks* before damage is visible to the naked eye.
*   **Critical Indices for Liwa:**
    *   **NDRE (Normalized Difference Red Edge):** Early chlorophyll/nitrogen stress detection.
    *   **NDMI (Normalized Difference Moisture Index):** Tracks water content inside leaves using SWIR bands; vital for monitoring irrigation deficits.
    *   **BSI (Bare Soil Index) & SI1-3 (Salinity Indices):** Utilizing the 1600nm to 2200nm SWIR range to differentiate exposed soil from crop fields and measure salinity, which is perfectly aligned with your land reclamation goals.
*   **Standard Processing Chain:** For raw hyperspectral data, the mandatory pipeline is: Radiometric Calibration -> Spectral/Spatial Binning -> Atmospheric Correction (removing aerosols/water vapor) -> Geometric Correction (Orthorectification).
*   **Biochemical Mapping:** Shortwave Infrared (SWIR) bands are utilized to detect biochemicals like cellulose, lignin, and starches, allowing differentiation between photosynthetic vegetation, dry/dead vegetation, and bare soil.

---
> [!TIP]
> **For the Green Liwa Project:** Your proposed 3-stage solution (Satellite land selection -> Desalination -> Smart irrigation) maps perfectly to the methodologies here. You can leverage the `NDRE` and `NDMI` indices on Sentinel-2 or Hyperspectral data for the smart irrigation feedback loop, and use the `BSI` and `Salinity Indices (SI)` for the initial land suitability mapping. You could also utilize a foundational model like Prithvi-EO to speed up the suitability scoring of the 1km x 1km grids.
