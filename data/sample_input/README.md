# Sample Input Data — Liwa Oasis Area of Interest (AOI)

## Overview
This directory contains a lightweight, fully georeferenced sample input scene enabling instant, offline execution of the PoC analysis pipeline without requiring multi-gigabyte satellite archive downloads or cloud credentials.

## Files
1. `example_scene.tif`:
   - **Sensor:** Sentinel-2 MSI Surface Reflectance (L2A equivalent).
   - **Dimensions:** 200 x 200 pixels at 10 m spatial resolution (2 km x 2 km ground footprint).
   - **Coordinate Reference System (CRS):** UTM Zone 39N (EPSG:32639), WGS84.
   - **Bands:**
     - Band 1: `B02_Blue` (490 nm, DN scaled by 10,000)
     - Band 2: `B03_Green` (560 nm, DN scaled by 10,000)
     - Band 3: `B04_Red` (665 nm, DN scaled by 10,000)
     - Band 4: `B08_NIR` (842 nm, DN scaled by 10,000)
   - **Coverage:** Center-pivot date palm cultivation cluster and surrounding arid sand dunes in Liwa, Abu Dhabi, UAE.

2. `liwa_aoi.geojson`:
   - Bounding polygon defining the Liwa Oasis primary study region `[53.5°E, 22.8°N]` to `[54.2°E, 23.3°N]`.

3. `sample_metadata.json`:
   - Technical specifications, calibration scale factors, and dataset provenance.
