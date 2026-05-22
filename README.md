# Python Toolbox for Collection and Preprocessing of Webcam Imagery and PM2.5 Data

This project constructs a webcam-based PM2.5 environmental dataset by integrating:

- Webcam image features
- PM2.5 air quality observations
- ERA5 meteorological reanalysis data
- ARPA Lombardia ground meteorological observations

The project provides a reproducible workflow for multi-source environmental data collection, preprocessing, integration, and dataset generation for air quality analysis and machine learning applications.

---

# Overall Workflow

```text
Webcam Image Collection
        ↓
ROI Selection
        ↓
ROI-Based Image Feature Extraction
        ↓
PM2.5 Download
        ↓
ERA5 Meteorological Data Download
        ↓
ARPA Meteorological Data Merge
        ↓
Multi-source Dataset Integration
        ↓
Dataset Cleaning & Feature Engineering
        ↓
Final Dataset Generation
```

---

# Main Notebooks

## 01_Webcam-Based PM2.5 Dataset Pipeline.ipynb

This notebook implements the complete workflow for constructing the integrated environmental dataset.

Main workflow:

- Webcam image loading
- ROI selection
- ROI-based image feature extraction
- PM2.5 data download
- ERA5 meteorological data download and processing
- ARPA meteorological data merging
- Multi-source dataset integration

Main output:

```text
data/interim/merged_dataset.csv
```

---

## 02_Dataset Cleaning and Preprocessing.ipynb

This notebook performs:

- Data profiling
- Missing-value analysis
- Duplicate timestamp checking
- Outlier analysis
- Data cleaning
- Feature engineering
- Dataset validation

Main output:

```text
data/processed/final_dataset.csv
```

Final dataset characteristics:

```text
Rows: 220
Columns: 41
Missing values: 0
Duplicate timestamps: 0
```

---

# Webcam Image Collection

Webcam images are automatically collected from:

```text
https://www.meteogiuliacci.it/meteo-webcam/webcam-milano
```

using:

```text
src/webcam_download.py
```

The collection workflow is automated using GitHub Actions.

Pipeline overview:

```text
GitHub Actions
        ↓
Execute webcam_download.py
        ↓
Download Milan webcam images
        ↓
Save images locally
        ↓
Upload images to Google Drive
```

Downloaded images are later used for ROI-based image feature extraction.

---

# ROI-Based Image Feature Extraction

Webcam image features are extracted using:

```text
src/image_features.py
```

The script extracts visual features from a predefined Region of Interest (ROI) selected from Milan webcam images.

The ROI is configured using:

```text
config/roi.json
```

and selected interactively inside:

```text
01_Webcam-Based PM2.5 Dataset Pipeline.ipynb
```

---

## Extracted Features

The extracted image features include:

```text
R_roi
G_roi
B_roi
S_mean
B_R_ratio
contrast
```

Feature descriptions:

| Feature | Description |
|---|---|
| R_roi | Mean red-channel intensity |
| G_roi | Mean green-channel intensity |
| B_roi | Mean blue-channel intensity |
| S_mean | Mean saturation in HSV space |
| B_R_ratio | Blue-to-red ratio |
| contrast | Standard deviation of grayscale intensity |

---

## Processing Workflow

The feature extraction workflow includes:

```text
Load webcam image
        ↓
Crop ROI region
        ↓
Convert RGB image
        ↓
Compute RGB mean values
        ↓
Compute saturation
        ↓
Compute blue/red ratio
        ↓
Compute image contrast
        ↓
Parse timestamp from filename
        ↓
Convert Europe/Rome time to UTC
        ↓
Export feature table
```

---

## Timestamp Processing

Image timestamps are automatically parsed from filenames using the format:

```text
YYYYMMDD-HHMM.jpg
```

Example:

```text
20260301-0400.jpg
```

The script converts timestamps from:

```text
Europe/Rome
```

to:

```text
UTC
```

to ensure temporal consistency with PM2.5, ERA5, and ARPA datasets.

---

## Output Dataset

Output file:

```text
data/interim/image_features.csv
```

Generated fields:

```text
datetime
R_roi
G_roi
B_roi
S_mean
B_R_ratio
contrast
image_path
```

Project result:

```text
Rows: 220
Skipped files: 0
```

---

# PM2.5 Data Download

Hourly PM2.5 observations are downloaded from the European Environment Agency (EEA) using:

```text
src/eea_pm25_download.py
```

Selected monitoring station:

```text
IT/SPO.IT0477A_6001_BETA
```

Output dataset:

```text
data/interim/PM25_MI_hourly.csv
```

---

# ERA5 Meteorological Data

ERA5 meteorological data are downloaded and processed using:

```text
src/era5_download.py
```

The workflow downloads:

- ERA5 single-level variables
- ERA5 pressure-level variables

Main variables include:

- T2M
- D2M
- RH
- U10
- V10
- SP
- TP
- BLH
- TCC
- CBH
- WS10
- GP_500
- GP_850
- T_500
- T_850
- U_500
- U_850
- V_500
- V_850

Output dataset:

```text
data/interim/era5_all_merged.csv
```

---

# ERA5 CDS API Configuration

ERA5 download requires a Copernicus Climate Data Store account.

Register at:

```text
https://cds.climate.copernicus.eu/
```

Create the `.cdsapirc` file in your home directory.

Windows:

```text
C:\Users\YOUR_USERNAME\.cdsapirc
```

Linux/macOS:

```text
~/.cdsapirc
```

Example configuration:

```text
url: https://cds.climate.copernicus.eu/api
key: YOUR_UID:YOUR_API_KEY
```

---

# ARPA Meteorological Data

Ground meteorological observations are obtained from ARPA Lombardia:

```text
https://www.arpalombardia.it/temi-ambientali/meteo-e-clima/form-richiesta-dati
```

Selected station:

```text
Milano - v. Juvara
```

ARPA CSV tables are merged using:

```text
src/merge_arpa_data.py
```

Merged variables include:

```text
temperature_mean
wind_direction_mean
relative_humidity_mean
wind_speed_mean
wind_gust_max
```

Output dataset:

```text
data/interim/arpa_merged.csv
```

---

# Multi-source Dataset Integration

All datasets are merged by UTC hourly timestamp using:

```text
src/merge_all_data.py
```

Integrated datasets:

```text
image_features.csv
PM25_MI_hourly.csv
era5_all_merged.csv
arpa_merged.csv
```

Output dataset:

```text
data/interim/merged_dataset.csv
```

The merged dataset contains:

- Webcam ROI image features
- PM2.5 observations
- ERA5 meteorological variables
- ARPA ground meteorological variables

---

# Dataset Cleaning and Feature Engineering

The integrated dataset is further processed using:

```text
02_Dataset Cleaning and Preprocessing.ipynb
```

Input dataset:

```text
data/interim/merged_dataset.csv
```

Final output:

```text
data/processed/final_dataset.csv
```

---

## Data Profiling

The notebook analyzes:

- Dataset structure
- Missing values
- Temporal coverage
- Timestamp continuity
- Numerical distributions
- Correlation structure

Visualization includes:

- Missing-value matrix
- Histograms
- Correlation heatmaps
- Boxplots
- PM2.5 time-series plots

---

## Data Quality Assessment

The workflow checks:

- Missing values
- Duplicate rows
- Duplicate timestamps
- Invalid physical values
- Outliers using the IQR method
- Temporal consistency

Examples of validation rules include:

- PM2.5 ≥ 0
- Relative humidity between 0–100
- Total cloud cover between 0–1
- Wind speed ≥ 0

---

## Data Cleaning

Cleaning operations include:

- Datetime conversion
- Chronological sorting
- Linear interpolation of missing values
- Wind-direction filling
- Invalid-value filtering
- Duplicate removal
- Numeric type conversion
- Removal of non-modeling columns

Removed columns:

```text
image_path
Unit
```

---

## Feature Engineering

Additional temporal and cyclical features are generated, including:

```text
hour
day
weekday
month
hour_sin
hour_cos
is_daytime
wind_dir_sin
wind_dir_cos
```

These features improve the representation of:

- Daily atmospheric cycles
- Illumination conditions
- Wind-direction periodicity

---

## Final Dataset Characteristics

```text
Rows: 220
Columns: 41
Missing values: 0
Duplicate timestamps: 0
```

The final dataset is ready for:

- PM2.5 prediction
- Environmental analysis
- Machine learning workflows
- Urban air-quality studies

---

# Output Datasets

Main generated datasets:

```text
data/interim/image_features.csv
data/interim/PM25_MI_hourly.csv
data/interim/era5_all_merged.csv
data/interim/arpa_merged.csv
data/interim/merged_dataset.csv
data/processed/final_dataset.csv
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/QingxuanTuo/webcam-pm25-toolbox.git
cd webcam-pm25-toolbox
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate environment:

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

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
