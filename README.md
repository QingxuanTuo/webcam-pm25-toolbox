# air-quality-thesis pipeline（自动数据采集 pipeline）

## 流程概览

GitHub server<br>
↓<br>
每天 UTC 02:00（≈ 米兰 03:00）<br>
↓<br>
运行 webcam_download.py<br>
↓<br>
抓取 Milan webcam<br>
↓<br>
保存到 images/<br>
↓<br>
rclone 上传到 Google Drive

## 建议每周检查一次

### A. GitHub Actions 是否成功

进入 **GitHub → Actions**

如果最近的运行结果都是 **Success**，说明系统正常。

### B. Google Drive 数据是否增加

打开 Google Drive 对应文件夹。

每天应该会新增 **一个文件夹**（或新增对应日期的数据）。

### C. 图片数量是否正常

如果某天只有几张图片，可能是网站某些小时没有更新。  
属于正常波动，但需要留意是否持续发生。

## 什么时候开始真正做分析

建议等到至少 **1–2 个月的数据量** 再开始分析。

## 后续分析步骤

1. 图像特征提取  
2. 与 PM2.5 station 数据匹配  
3. 加入 ERA5 气象变量  
4. 训练 ML / DL 模型



# EEA PM2.5 Downloader – Milan Monitoring Station

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
