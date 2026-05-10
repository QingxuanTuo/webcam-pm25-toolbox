import pandas as pd
from functools import reduce

files = [
    "table1.csv",
    "table2.csv",
    "table3.csv",
    "table4.csv",
    "table5.csv",
    "table6.csv",
    "table7.csv"
]

def get_variable_name(sensor_id, value_col):
    value_col = value_col.strip()

    if sensor_id == 5908:
        return "precipitation_cumulative"
    elif sensor_id == 5909:
        return "temperature_mean"
    elif sensor_id == 6044:
        return "wind_direction_mean"
    elif sensor_id == 6179:
        return "relative_humidity_mean"
    elif sensor_id == 6458:
        return "global_radiation_mean"
    elif sensor_id == 19242 and value_col == "Medio":
        return "wind_speed_mean"
    elif sensor_id == 19242 and value_col == "Massimo":
        return "wind_gust_max"
    else:
        return f"unknown_{sensor_id}_{value_col}"

dfs = []

for file in files:
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()

    sensor_id = int(df["Id Sensore"].iloc[0])

    value_col = [c for c in df.columns if c not in ["Id Sensore", "Data-Ora"]][0]

    new_col = get_variable_name(sensor_id, value_col)

    df = df[["Data-Ora", value_col]].rename(columns={value_col: new_col})

    dfs.append(df)

merged = reduce(
    lambda left, right: pd.merge(left, right, on="Data-Ora", how="outer"),
    dfs
)

merged["Data-Ora"] = pd.to_datetime(merged["Data-Ora"])
merged = merged.sort_values("Data-Ora")

merged.replace(-999, pd.NA, inplace=True)

merged.to_csv("arpa_merged.csv", index=False)

print(merged.head())
print(merged.columns)