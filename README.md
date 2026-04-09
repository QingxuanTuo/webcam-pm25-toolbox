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

```python
api_start = "YYYY-MM-DDTHH:MM:SSZ"
api_end   = "YYYY-MM-DDTHH:MM:SSZ"
