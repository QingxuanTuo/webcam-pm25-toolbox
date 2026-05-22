# Webcam-Based PM2.5 Dataset Generation and Multi-Source Environmental Data Fusion

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
Image Feature Extraction
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

This notebook performs dataset profiling, data quality assessment, cleaning, validation, and feature engineering to generate the final machine-learning-ready dataset.

Input dataset:

```text
data/interim/merged_dataset.csv
```

Main processing steps include:

- Dataset structure analysis
- Missing-value analysis
- Temporal coverage checking
- Duplicate timestamp detection
- Invalid physical-value detection
- IQR-based outlier analysis
- Missing-value interpolation
- Datetime conversion
- Chronological sorting
- Duplicate removal
- Numeric type conversion
- Feature engineering
- Dataset validation
- Correlation analysis and visualization

Generated features include:

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

The final dataset is fully cleaned, temporally aligned, and ready for:

- PM2.5 prediction
- Environmental analysis
- Machine learning workflows
- Urban air-quality studies
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
git clone https://github.com/QingxuanTuo/webcam-pm25-toolbox
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

---

# Authors

- Tuo Qingxuan — Politecnico di Milano
- Zhang Zihao — Politecnico di Milano

GeoInformatics Project

---

# License

This project is intended for academic and research purposes only.
