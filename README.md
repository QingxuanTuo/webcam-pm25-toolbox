# 01 Webcam-Based Air Quality Data Collection Pipeline

This project automatically collects **webcam images from Milan** and stores them in Google Drive.  
The dataset will be used for air quality research, particularly **PM2.5 estimation based on image data**.

---

## Pipeline Overview

```text
GitHub Actions (scheduled workflow)
        ↓
Runs daily at 02:00 UTC (≈ 03:00 Milan time)
        ↓
Execute webcam_download.py
        ↓
Scrape Milan webcam images
        ↓
Save to local images/ directory
        ↓
Upload to Google Drive via rclone
```
---

## Data Source

- Website: https://www.meteogiuliacci.it/meteo-webcam/webcam-milano  
- Data type: Hourly webcam images of Milan

---

## Core Script

**webcam_download.py** This script is responsible for automatically scraping and saving webcam images.

### Main functionalities:

- Extract image URLs containing `"hour"`
- Download images via `requests`
- Rename images based on date and hour

---
##  Automation & Monitoring

To ensure the pipeline runs correctly, it is recommended to perform regular checks:

### 1. GitHub Actions Status

Navigate to: GitHub → Actions

Verify that recent workflow runs are marked as: **Success**

This indicates that the automated data collection is functioning properly.

---

### 2. Google Drive Data Integrity

Check the corresponding Google Drive folder and ensure that:

- A new folder is generated each day
- Each folder contains multiple images (typically around 20 images per day)

Consistent data updates confirm that the pipeline is operating as expected.

## Data Storage Structure

```text
images/
└── DD_MM_YYYY/
    └── giuliacci/
        ├── YYYYMMDD-0400.jpg
        ├── YYYYMMDD-0500.jpg
        ├── ...
        └── YYYYMMDD-2300.jpg
```
##  Workflow Configuration

The pipeline is implemented using a scheduled GitHub Actions workflow:

- Defined in: `.github/workflows/webcam.yml`
- Runtime environment: `ubuntu-latest` with Python 3.10

The workflow automates:

- Running the image scraping script (`webcam_download.py`)
- Managing dependencies (`requests`, `beautifulsoup4`)

Sensitive credentials (e.g., rclone configuration) are securely stored using GitHub Secrets (`RCLONE_CONF`).

# 02 EEA PM2.5 Downloader – Milan Monitoring Station

## Overview

This notebook (`eea_pm25_downloader.ipynb`) provides a complete workflow for downloading and preprocessing hourly PM2.5 data from the European Environment Agency (EEA) Air Quality e-Reporting database.

The notebook automatically downloads air quality data for Milan, filters the data for a specific monitoring station, restricts the data to a selected time range, and exports a clean CSV file for further analysis and modelling.

This notebook is the first step of the overall project workflow.

---

## Data Source

Data are obtained from the European Environment Agency (EEA) Air Quality Download Service:

https://eeadmz1-downloads-webapp.azurewebsites.net/

Dataset used:
- Up-to-date data (E2a)
- Hourly aggregation
- Pollutant: PM2.5
- Country: Italy
- City: Milano (greater city)

---

## Monitoring Station

Although multiple monitoring stations are available in Milan, this project uses data from the following station:

**Sampling Point ID:**  
IT/SPO.IT0477A_6001_BETA

This station was selected because it provides consistent hourly PM2.5 measurements suitable for comparison with webcam images.

---

## Workflow Description

The notebook performs the following steps:

1. Define download parameters (country, city, pollutant, time range).
2. Send a request to the EEA API and retrieve parquet file URLs.
3. Download all parquet files corresponding to Milan monitoring stations.
4. Merge all parquet files into a single dataset.
5. Filter the dataset to keep only the selected monitoring station.
6. Filter the dataset by the selected time period.
7. Convert timestamps and remove timezone information.
8. Export the cleaned dataset as a CSV file.

---

## Input and Output

### Input
- EEA Air Quality data (downloaded automatically as parquet files)

### Output
- `PM25_MI_hourly.csv`

This CSV file contains the following fields:

- Samplingpoint
- Pollutant
- Start
- End
- Value (PM2.5 concentration)
- Unit
- AggType
- Validity
- Verification
- ResultTime
- DataCapture
- FkObservationLog

The `Start` column represents the start time of each hourly measurement interval.

---

## How to Use

1. Open `eea_pm25_downloader.ipynb`
2. Modify the time range in the parameter section:

        api_start = "YYYY-MM-DDTHH:MM:SSZ"
        api_end   = "YYYY-MM-DDTHH:MM:SSZ"


# 03 ERA5 Meteorological Data Collection and Processing

## Overview

This module provides a complete workflow for downloading, processing, and integrating meteorological data from ERA5 reanalysis datasets.

The purpose of this step is to generate a clean, analysis-ready dataset that complements webcam imagery and PM2.5 observations, enabling more robust air quality modelling.

Two ERA5 datasets are used:

- ERA5 single levels reanalysis  
- ERA5 pressure levels reanalysis  

These datasets together provide both **surface-level conditions** and **upper-air atmospheric structure**.

---

## Data Source

Data are obtained from the Copernicus Climate Data Store (CDS):

https://cds.climate.copernicus.eu/

### Dataset 1 – ERA5 Single Levels

- Data type: Hourly time series (point-based)  
- Location: Milan (user-defined coordinates)  

Selected variables:

- 2m temperature (T2M)  
- 10m u-component of wind (U10)  
- 10m v-component of wind (V10)  
- Surface pressure (SP)  
- Total precipitation (TP)  
- Boundary layer height (BLH)  

These variables describe **local meteorological conditions affecting PM2.5 dispersion and accumulation**.

---

### Dataset 2 – ERA5 Pressure Levels

- Data type: Hourly gridded data  

Selected pressure levels:

- 850 hPa (lower atmosphere)  
- 500 hPa (mid-troposphere)  

Selected variables:

- Temperature (T)  
- U-component of wind (U)  
- V-component of wind (V)  
- Geopotential (GP)  

These variables represent **large-scale atmospheric dynamics and stability**, which influence pollution transport and vertical mixing.

---

## Workflow Description

The ERA5 processing pipeline consists of the following steps:

### Step 1 – Data Download

Data are retrieved using the CDS API:

- Single-level data are downloaded as CSV files (time series at a specific location)  
- Pressure-level data are downloaded as NetCDF files (multi-dimensional gridded data)  

---

### Step 2 – Data Extraction

- ZIP archives are automatically extracted  
- Relevant files are identified:  

  - CSV for single-level data  
  - NetCDF for pressure-level data  

---

### Step 3 – Data Preprocessing

**Single-Level Data**

- Convert timestamps to standard datetime format  
- Remove timezone information  
- Rename variables to concise names (e.g., T2M, U10)  
- Select relevant columns  

---

**Pressure-Level Data**

- Read NetCDF files using `xarray`  
- Aggregate spatial grid values (average over ROI)  
- Convert from long format to wide format  
- Generate derived variables:
T_500, U_500, V_500, GP_500
T_850, U_850, V_850, GP_850

---

### Step 4 – Data Integration

- Merge single-level and pressure-level datasets using the time column  
- Ensure consistent timestamp format:
YYYY-MM-DD HH:MM:SS


---

## Input and Output

### Input

- ERA5 single-level CSV data (downloaded automatically)  
- ERA5 pressure-level NetCDF data (downloaded automatically)  

---

### Output
era5_all_merged.csv

# 04 Data Integration: PM2.5 and ERA5 Dataset

## Overview

This step integrates the PM2.5 air quality data with ERA5 meteorological data to produce a unified, analysis-ready dataset. The merged dataset will be used for subsequent modelling tasks, including the estimation of PM2.5 concentrations from webcam imagery.

---

## Input Data

The integration step uses the following datasets:

- PM2.5 dataset (EEA):
  - `PM25_MI_hourly.csv`
- ERA5 meteorological dataset:
  - `era5_all_merged.csv`

---

## Temporal Alignment

PM2.5 measurements are reported as hourly intervals with a **Start** and **End** time:
Start → End


In this project, the **Start timestamp is used for alignment** with ERA5 data.

Reason:

- ERA5 data are provided at hourly resolution
- The Start time represents the beginning of the measurement interval
- Using Start ensures consistent temporal matching between datasets

---

## Workflow Description

The integration process performs the following steps:

1. Load PM2.5 and ERA5 datasets
2. Convert timestamps to a consistent datetime format
3. Align datasets based on the hourly timestamp
4. Extract relevant PM2.5 fields (Value, Unit)
5. Merge PM2.5 data with ERA5 variables
6. Export the final merged dataset

---

## Output

The final dataset is saved as:
pm25_era5_merged.csv


This dataset contains both air quality observations and meteorological variables, and is ready for machine learning and analysis.

---

## Features

The merged dataset includes the following variables:

### PM2.5 Variables
- Value (PM2.5 concentration)
- Unit

### ERA5 Surface Variables
- T2M (2m temperature)
- U10 (10m u wind component)
- V10 (10m v wind component)
- SP (surface pressure)
- TP (total precipitation)
- BLH (boundary layer height)

### ERA5 Pressure-Level Variables
- GP_500, GP_850 (geopotential)
- T_500, T_850 (temperature)
- U_500, U_850 (wind u-component)
- V_500, V_850 (wind v-component)

---

## Script

The integration is implemented in the following script:
merge_pm25_era5.py
