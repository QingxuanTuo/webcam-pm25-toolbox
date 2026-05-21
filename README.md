# Webcam-Based PM2.5 Dataset Generation and Multi-Source Environmental Data Fusion

A complete geoinformatics and environmental data processing pipeline for generating a unified hourly environmental dataset by integrating:

- Webcam image features
- PM2.5 air quality observations
- ERA5 reanalysis meteorological data
- ARPA Lombardia ground weather station data

The project provides a reproducible and extensible framework for:

- PM2.5 prediction
- Air quality analysis
- Environmental monitoring
- Machine learning research
- Urban environmental studies


# Project Overview

This project combines:

- Computer Vision
- Environmental data acquisition
- Meteorological data processing
- Multi-source spatiotemporal data fusion

using automated Python workflows.

The complete pipeline includes:

1. Webcam image processing
2. PM2.5 data download
3. ERA5 meteorological data download
4. ARPA ground station integration
5. Multi-source dataset integration
6. Data cleaning and feature engineering
7. Final machine-learning-ready dataset generation



# Project Features



## 1. Webcam Image Processing

The project uses fixed urban webcams as visual environmental data sources.

An interactive ROI (Region of Interest) selection tool based on `matplotlib` and `ipywidgets` allows users to manually select:

- Sky regions
- Urban regions

The system automatically extracts several image features related to air quality, including:

- RGB mean values
- Saturation mean
- Blue/Red ratio
- Image contrast

Image timestamps are automatically parsed from filenames and converted from Europe/Rome local time to UTC.

Final output:

```text
data/interim/image_features.csv
```



## 2. PM2.5 Data Download

Hourly PM2.5 observations are automatically downloaded from the European Environment Agency (EEA) API.

The workflow includes:

- API requests
- Parquet file download
- Monitoring station filtering
- UTC time conversion
- Clean hourly PM2.5 dataset generation

Final output:

```text
data/interim/PM25_MI_hourly.csv
```



## 3. ERA5 Meteorological Data Download and Processing

ERA5 reanalysis meteorological data are downloaded from the Copernicus Climate Data Store (CDS).

### Single-Level Variables

The project downloads:

- 2m temperature (T2M)
- 2m dew point temperature (D2M)
- 10m wind components (U10, V10)
- Surface pressure (SP)
- Total precipitation (TP)
- Boundary layer height (BLH)
- Total cloud cover (TCC)
- Cloud base height (CBH)

### Pressure-Level Variables

The project also downloads:

- Geopotential height at 500 hPa and 850 hPa
- Temperature
- Wind components

### Derived Variables

Additional variables are computed:

- Relative humidity (RH)
- Wind speed (WS10)

Final output:

```text
data/interim/era5_all_merged.csv
```



## 4. ARPA Lombardia Weather Station Integration

The project integrates multiple ARPA Lombardia weather station CSV files.

Supported variables include:

- Air temperature
- Relative humidity
- Wind direction
- Wind speed
- Gust wind speed

The system automatically:

- Maps sensor IDs
- Replaces invalid values
- Converts timestamps to UTC
- Merges multiple weather station tables

Final output:

```text
data/interim/arpa_merged.csv
```


## 5. Multi-Source Dataset Integration

The system integrates:

- Webcam image features
- PM2.5 observations
- ERA5 meteorological data
- ARPA ground station observations

using UTC hourly timestamps.

Final output:

```text
data/interim/merged_dataset.csv
```

This dataset represents the raw integrated environmental dataset before cleaning and feature engineering.



## 6. Data Cleaning and Feature Engineering

After dataset integration, the merged dataset undergoes:

- Data quality assessment
- Missing-value handling
- Outlier analysis
- Temporal consistency checks
- Feature engineering
- Validation and visualization

### Data Quality Assessment

Includes:

- Missing-value analysis
- Duplicate timestamp detection
- Physical invalid-value detection
- IQR-based outlier detection
- Temporal continuity checks

### Data Cleaning

Includes:

- Datetime conversion
- Dataset sorting
- Missing-value interpolation
- Wind-direction filling
- Duplicate removal
- Numeric conversion

### Feature Engineering

Generated features include:

- hour
- day
- weekday
- month
- hour_sin
- hour_cos
- is_daytime
- wind_dir_sin
- wind_dir_cos

### Validation and Visualization

Includes:

- Variable distribution visualization
- Correlation analysis
- PM2.5 time-series visualization
- Final dataset validation

Final output:

```text
data/processed/final_dataset.csv
```

Final dataset characteristics:

- 220 rows
- 41 columns
- No missing values
- No duplicate timestamps
- Ready for machine learning and environmental analysis



# Project Structure

```text
webcam-pm25-toolbox/
│
├── config/
│   └── roi.json
│
├── data/
│   ├── raw/
│   │   ├── arpa/
│   │   ├── era5/
│   │   ├── images/
│   │   └── pm25/
│   │
│   ├── interim/
│   │   ├── arpa_merged.csv
│   │   ├── era5_all_merged.csv
│   │   ├── image_features.csv
│   │   ├── merged_dataset.csv
│   │   └── PM25_MI_hourly.csv
│   │
│   └── processed/
│       └── final_dataset.csv
│
├── notebooks/
│   ├── 01_Webcam-Based PM2.5 Dataset Pipeline.ipynb
│   └── 02_Dataset Cleaning and Preprocessing.ipynb
│
├── src/
│   ├── webcam_download.py
│   ├── roi_viewer.py
│   ├── image_features.py
│   ├── eea_pm25_download.py
│   ├── era5_download.py
│   ├── merge_arpa_data.py
│   └── merge_all_data.py
│
├── requirements.txt
│
└── README.md
```



# Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```



## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```



## 3. Install Dependencies

```bash
pip install -r requirements.txt
```



# ERA5 CDS API Configuration

ERA5 download requires a Copernicus Climate Data Store (CDS) account.



## Step 1 — Create CDS Account

Register at:

```text
https://cds.climate.copernicus.eu/
```



## Step 2 — Obtain API Key

After login:

- Open your CDS profile
- Copy your API key



## Step 3 — Create `.cdsapirc`

Create the following file in your home directory.

### Windows

```text
C:\Users\YOUR_USERNAME\.cdsapirc
```

### Linux / macOS

```text
~/.cdsapirc
```

File content:

```text
url: https://cds.climate.copernicus.eu/api
key: YOUR_UID:YOUR_API_KEY
```


# Main Third-Party Python Libraries

```text
pandas
numpy
matplotlib
pillow
xarray
requests
ipywidgets
jupyter
beautifulsoup4
cdsapi
imageio
```



# Workflow



## Step 1 — Multi-Source Data Download, Processing, and Integration

Open and run:

```text
notebooks/01_Webcam-Based PM2.5 Dataset Pipeline.ipynb
```

This notebook contains the complete dataset construction workflow, including:

- Webcam image loading
- Interactive ROI selection
- Image feature extraction
- PM2.5 data download and processing
- ERA5 meteorological data download and processing
- ARPA Lombardia weather station integration
- UTC hourly multi-source dataset integration

Generated intermediate datasets include:

```text
data/interim/image_features.csv
data/interim/PM25_MI_hourly.csv
data/interim/era5_all_merged.csv
data/interim/arpa_merged.csv
data/interim/merged_dataset.csv
```

where:

```text
data/interim/merged_dataset.csv
```

is the raw integrated dataset before cleaning and feature engineering.



## Step 2 — Data Cleaning, Quality Assessment, and Feature Engineering

Open and run:

```text
notebooks/02_Dataset Cleaning and Preprocessing.ipynb
```

This notebook performs:

- Data loading
- Dataset profiling
- Missing-value analysis
- Temporal consistency checks
- Duplicate timestamp checks
- Invalid-value detection
- IQR outlier analysis
- Missing-value interpolation
- Column filtering
- Numeric conversion
- Temporal feature generation
- Wind-direction cyclical encoding
- Data visualization
- PM2.5 correlation analysis

Input dataset:

```text
data/interim/merged_dataset.csv
```

Final output:

```text
data/processed/final_dataset.csv
```

Final dataset characteristics:

- 220 rows
- 41 columns
- No missing values
- No duplicate timestamps
- Ready for modeling and environmental analysis



# Standalone Scripts

The `src/` directory contains reusable standalone scripts that can also be executed independently.



## Webcam Image Download

```bash
python src/webcam_download.py
```

Downloads webcam images and saves them with timestamp-based filenames.



## Interactive ROI Viewer

```text
src/roi_viewer.py
```

Provides an interactive ROI selection interface inside Jupyter Notebook.



## Image Feature Extraction

```text
src/image_features.py
```

Extracts RGB, saturation, blue/red ratio, and contrast features from selected ROIs.



## PM2.5 Data Download

```bash
python src/eea_pm25_download.py
```

Downloads and filters hourly PM2.5 observations from the EEA API.



## ERA5 Meteorological Data Download

```bash
python src/era5_download.py
```

Downloads ERA5 single-level and pressure-level meteorological variables from CDS.



## ARPA Weather Data Integration

```bash
python src/merge_arpa_data.py
```

Merges multiple ARPA Lombardia weather station CSV files.



## Multi-Source Dataset Integration

```bash
python src/merge_all_data.py
```

Integrates webcam features, PM2.5 observations, ERA5 data, and ARPA weather station data using UTC hourly timestamps.



# Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Pillow (PIL)
- Xarray
- CDS API
- Requests
- Jupyter Notebook



# Dataset Applications

The generated dataset can support:

- PM2.5 prediction models
- Air quality monitoring
- Environmental analysis
- Urban climate studies
- Computer vision research
- Machine learning workflows
- Air pollution forecasting



# Future Improvements

Possible future extensions include:

- Deep learning PM2.5 prediction
- Real-time webcam processing
- Satellite remote sensing integration
- Additional meteorological variables
- Multi-city support
- Automated visualization dashboards



# Authors

- Tuo Qingxuan— Politecnico di Milano
- Zhang Zihao — Politecnico di Milano

GeoInformatics Project



# License

This project is intended for academic and research purposes only.
