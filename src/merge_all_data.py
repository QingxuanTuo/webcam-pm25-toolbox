import pandas as pd
from functools import reduce

# 1. Read the three datasets
arpa = pd.read_csv("arpa_merged.csv")
image_features = pd.read_csv("image_feature_roi.csv")
era5_pm25 = pd.read_csv("pm25_era5_merged.csv")

# 2. Remove extra spaces from column names
arpa.columns = arpa.columns.str.strip()
image_features.columns = image_features.columns.str.strip()
era5_pm25.columns = era5_pm25.columns.str.strip()

# 3. Rename ARPA time column to "time"
arpa = arpa.rename(columns={"Data-Ora": "time"})

# 4. Combine date and hour columns into a single datetime column
image_features["time"] = pd.to_datetime(
    image_features["date"].astype(str) + " " + image_features["hour"].astype(str)
)

# 5. Convert time columns to datetime format
arpa["time"] = pd.to_datetime(arpa["time"])
era5_pm25["time"] = pd.to_datetime(era5_pm25["time"])

# 6. Remove original date and hour columns from image features dataset
image_features = image_features.drop(columns=["date", "hour"])

# 7. Keep only timestamps existing in all three datasets
merged_all = reduce(
    lambda left, right: pd.merge(left, right, on="time", how="inner"),
    [image_features, era5_pm25, arpa]
)

# 8. Sort the merged dataset by time
merged_all = merged_all.sort_values("time")

# 9. Define the final column order
column_order = [
    "time",
    "R_roi",
    "G_roi",
    "B_roi",
    "S_mean",
    "B_R_ratio",
    "contrast",
    "image_path",
    "PM25",
    "Unit",
    "T2M",
    "U10",
    "V10",
    "SP",
    "TP",
    "BLH",
    "GP_500",
    "GP_850",
    "T_500",
    "T_850",
    "U_500",
    "U_850",
    "V_500",
    "V_850",
    "precipitation_cumulative",
    "temperature_mean",
    "wind_direction_mean",
    "relative_humidity_mean",
    "global_radiation_mean",
    "wind_speed_mean",
    "wind_gust_max"
]

# 10. Reorder columns according to the specified order
merged_all = merged_all[column_order]

# 11. Save the final merged dataset
merged_all.to_csv("final_merged_all.csv", index=False)

# 12. Print preview and total number of rows
print(merged_all.head())
print("Final rows:", len(merged_all))