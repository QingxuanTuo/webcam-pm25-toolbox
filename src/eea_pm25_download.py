# %% [markdown]
# # EEA PM2.5 Data Download and Preprocessing
# 
# This notebook downloads hourly PM2.5 data from the European Environment Agency (EEA) Air Quality Download Service for Milan, Italy. The workflow is designed to produce a clean and station-specific CSV file that can be used in the subsequent image-based PM2.5 analysis and machine learning experiments.
# 
# The main steps are:
# 1. import the required libraries;
# 2. define the download parameters;
# 3. request and download the parquet files from the EEA service;
# 4. merge all downloaded files into one dataset;
# 5. filter the data by the selected monitoring station;
# 6. filter the data by the required time range;
# 7. remove timezone information for consistent formatting;
# 8. export the final CSV file for later modelling.

# %% [markdown]
# 

# %%
import requests
import pandas as pd
import time
import csv
from pathlib import Path

# %% [markdown]
# 
# ## Parameter Configuration
# 
# This section defines all parameters required for the download and preprocessing procedure. The selected country is Italy, the selected city is *Milano (greater city)*, and the pollutant of interest is PM2.5. The dataset used is the up-to-date E2a dataset with hourly aggregation.
# 
# In addition, the target monitoring station is specified using its sampling point prefix. This is necessary because the Milan download contains multiple monitoring stations, while only one station is retained for the present study.
# 
# The start and end times can be modified depending on the period of interest.

# %%
countries = ["IT"]
cities = ["Milano (greater city)"]
pollutants = ["PM2.5"]
dataset = 1
aggregation = "hour"

api_start = "2026-03-01T00:00:00Z"
api_end   = "2026-03-12T23:59:59Z"

station_prefix = "IT/SPO.IT0477A_6001_BETA"

download_dir = Path("data/raw/pm25/downloads_milano")
csv_out = Path("data/raw/pm25/PM25_MI_hourly.csv")

download_dir.mkdir(parents=True, exist_ok=True)
csv_out.parent.mkdir(parents=True, exist_ok=True)

API_BASE = "https://eeadmz1-downloads-api-appservice.azurewebsites.net/"
URLS_ENDPOINT = "ParquetFile/urls"

# %% [markdown]
# 
# ## Helper Functions for File Retrieval
# 
# This section defines the utility functions used in the download process. First, the returned text from the EEA API is parsed in order to extract valid parquet file URLs. Then, each file is downloaded and saved locally.
# 
# These helper functions separate the low-level retrieval logic from the main workflow, making the notebook easier to read and reuse.

# %%
def extract_urls(text):
    urls = []
    for raw in text.splitlines():
        line = raw.strip().strip('"')
        if line.startswith("http://") or line.startswith("https://"):
            urls.append(line)
    return urls


def download_file(url, out_path):
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

# %% [markdown]
# 
# ## Download of Hourly PM2.5 Data from the EEA Service
# 
# In this step, a request body is created and sent to the EEA download API. The response contains a list of parquet file URLs corresponding to the selected city, pollutant, dataset type, and time range.
# 
# All returned parquet files are then downloaded into a local directory. Since multiple monitoring stations may be included in the city-level request, all files are temporarily retained and filtered in a later step.

# %%
body = {
    "countries": countries,
    "cities": cities,
    "pollutants": pollutants,
    "dataset": dataset,
    "dateTimeStart": api_start,
    "dateTimeEnd": api_end,
    "aggregationType": aggregation,
    "source": "Jupyter notebook",
}

print("Request:", body)

response = requests.post(API_BASE + URLS_ENDPOINT, json=body, timeout=180)
response.raise_for_status()

urls = extract_urls(response.text)
print("Found parquet files:", len(urls))

downloaded_files = []

for i, url in enumerate(urls, start=1):
    file_name = url.split("/")[-1]
    out_path = download_dir / file_name
    print(f"[{i}/{len(urls)}] Downloading {file_name}")
    download_file(url, out_path)
    downloaded_files.append(out_path)
    time.sleep(0.2)

# %% [markdown]
# 
# ## Merging the Downloaded Parquet Files
# 
# The downloaded parquet files are stored separately because different monitoring stations are returned as different files. To simplify the preprocessing stage, all parquet files are read and merged into a single dataframe.
# 
# An additional column indicating the source file is added for traceability. This can be useful for checking which observations originally came from which station-specific parquet file.

# %%
parquet_files = list(download_dir.glob("*.parquet"))

dfs = []
for file in parquet_files:
    print("Reading", file.name)
    df = pd.read_parquet(file)
    df["source_file"] = file.name
    dfs.append(df)

merged = pd.concat(dfs, ignore_index=True)

print("Merged shape:", merged.shape)
print("Columns:", merged.columns.tolist())

# %% [markdown]
# 
# ## Station Filtering and Time Filtering
# 
# Although the request is restricted to Milan, the downloaded data still contains several monitoring stations. Therefore, an additional filtering step is required in order to keep only the target station used in this study.
# 
# The selected station is identified by the prefix:
# 
# `IT/SPO.IT0477A_6001_BETA`
# 
# After the station filtering step, the observations are further filtered according to the selected time interval. The `Start` and `End` fields are converted to datetime format, and timezone information is removed after filtering so that the exported CSV uses a cleaner and more convenient timestamp format.

# %%
# ===== Station filtering =====
filtered = merged[
    merged["Samplingpoint"].astype(str).str.startswith(station_prefix, na=False)
].copy()

print("After station filter:", filtered.shape)

# ===== Time processing =====
filtered["Start"] = pd.to_datetime(filtered["Start"], utc=True)
filtered["End"] = pd.to_datetime(filtered["End"], utc=True)

start_ts = pd.to_datetime(api_start, utc=True)
end_ts = pd.to_datetime(api_end, utc=True)

filtered = filtered[
    (filtered["Start"] >= start_ts) &
    (filtered["Start"] <= end_ts)
].copy()

# Remove timezone information
filtered["Start"] = filtered["Start"].dt.tz_localize(None)
filtered["End"] = filtered["End"].dt.tz_localize(None)

filtered = filtered.sort_values("Start").reset_index(drop=True)

print("After time filter:", filtered.shape)

# %% [markdown]
# 
# ## Selection of Relevant Columns and CSV Export
# 
# The final dataset does not require every field returned by the raw parquet files. Therefore, only the columns relevant for the PM2.5 analysis are retained.
# 
# The cleaned dataframe is then exported as a CSV file. This CSV serves as the input air-quality dataset for the next stages of the research, including time alignment with webcam images, feature extraction, and predictive modelling.

# %%
target_columns = [
    "Samplingpoint",
    "Pollutant",
    "Start",
    "End",
    "Value",
    "Unit",
    "AggType",
    "Validity",
    "Verification",
    "ResultTime",
    "DataCapture",
    "FkObservationLog",
]

existing = [c for c in target_columns if c in filtered.columns]

final_df = filtered[existing].copy()

final_df.to_csv(csv_out, index=False)

print("Saved CSV:", csv_out)
print("Final shape:", final_df.shape)

final_df.head()

# Optional cleanup of downloaded parquet files
for file in parquet_files:
    file.unlink()

print("Temporary parquet files removed.")

# %% [markdown]
# ## Summary
# 
# This notebook provides a reproducible workflow for downloading and preprocessing hourly PM2.5 data from the EEA platform for the selected Milan monitoring station. The exported CSV file is the final output of this stage and will be used in the following steps of the project.
# 
# At this point, the data has been:
# - restricted to the selected city;
# - filtered to the target monitoring station;
# - limited to the desired time interval;
# - cleaned into a consistent CSV format for later analysis.


