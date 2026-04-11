from __future__ import annotations

import zipfile
from pathlib import Path

import cdsapi
import numpy as np
import pandas as pd
import xarray as xr

# =========================
# Basic settings
# =========================
LAT = 45.46
LON = 9.19
START_DATE = "2026-03-01"
END_DATE = "2026-03-02"

OUT_DIR = Path("era5_work")
OUT_DIR.mkdir(exist_ok=True)

# downloaded zip files
SINGLE_ZIP = OUT_DIR / "single_levels.zip"
PRESSURE_ZIP = OUT_DIR / "pressure_levels.zip"

# extracted folders
SINGLE_EXTRACT = OUT_DIR / "single_extracted"
PRESSURE_EXTRACT = OUT_DIR / "pressure_extracted"

# final output
FINAL_CSV = OUT_DIR / "era5_all_merged.csv"

# =========================
# Variables
# =========================
# single-level: 

SINGLE_VARS = [
    "2m_temperature",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "surface_pressure",
    "total_precipitation",
    "boundary_layer_height",
]

# pressure-level: 500 and 850 hPa
PRESSURE_VARS = [
    "geopotential",
    "temperature",
    "u_component_of_wind",
    "v_component_of_wind",
]

PRESSURE_LEVELS = ["500", "850"]


# =========================
# Helper functions
# =========================
def ensure_clean_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def unzip_file(zip_path: Path, extract_dir: Path) -> list[Path]:
    ensure_clean_dir(extract_dir)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
        names = zf.namelist()
    return [extract_dir / n for n in names]


def first_existing(paths: list[Path], suffixes: tuple[str, ...]) -> Path:
    for p in paths:
        if p.suffix.lower() in suffixes:
            return p
    raise FileNotFoundError(f"No file found with suffix in {suffixes}")


def build_date_parts(start_date: str, end_date: str) -> tuple[list[str], list[str], list[str], list[str]]:
    dt_index = pd.date_range(start=start_date, end=end_date + " 23:00:00", freq="h")
    years = sorted({f"{d.year:04d}" for d in dt_index})
    months = sorted({f"{d.month:02d}" for d in dt_index})
    days = sorted({f"{d.day:02d}" for d in dt_index})
    times = [f"{h:02d}:00" for h in range(24)]
    return years, months, days, times


def calc_rh(t_kelvin: pd.Series, td_kelvin: pd.Series) -> pd.Series:
    t_c = t_kelvin - 273.15
    td_c = td_kelvin - 273.15
    rh = 100.0 * np.exp(
        (17.625 * td_c) / (243.04 + td_c)
        - (17.625 * t_c) / (243.04 + t_c)
    )
    return rh.clip(lower=0, upper=100)


def process_single_csv(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    print("Single raw columns:", df.columns.tolist())

    if "valid_time" not in df.columns:
        raise KeyError(f"'valid_time' not found in single-level csv columns: {df.columns.tolist()}")

    df["time"] = pd.to_datetime(df["valid_time"]).dt.tz_localize(None)

    # 同时兼容长名和短名
    rename_map = {
        # long names
        "2m_temperature": "T2M",
        "10m_u_component_of_wind": "U10",
        "10m_v_component_of_wind": "V10",
        "surface_pressure": "SP",
        "total_precipitation": "TP",
        "boundary_layer_height": "BLH",

        # short names
        "t2m": "T2M",
        "u10": "U10",
        "v10": "V10",
        "sp": "SP",
        "tp": "TP",
        "blh": "BLH",
    }

    df = df.rename(columns=rename_map)

    # 可选：加一个风速
    if {"U10", "V10"}.issubset(df.columns):
        df["WS10"] = np.sqrt(df["U10"] ** 2 + df["V10"] ** 2)

    drop_cols = [c for c in ["valid_time", "latitude", "longitude"] if c in df.columns]
    df = df.drop(columns=drop_cols)

    keep_cols = ["time", "T2M", "U10", "V10", "SP", "TP", "BLH"]
    keep_cols = [c for c in keep_cols if c in df.columns]

    out = df[keep_cols].sort_values("time").reset_index(drop=True)

    print("Single processed columns:", out.columns.tolist())
    print("Single processed shape:", out.shape)
    print(out.head())

    return out

def process_pressure_netcdf(nc_path: Path) -> pd.DataFrame:
    ds = xr.open_dataset(nc_path)

    print(ds)

    df = ds.to_dataframe().reset_index()

    required = {"valid_time", "pressure_level"}
    if not required.issubset(df.columns):
        raise KeyError(f"Pressure data missing required columns. Found: {df.columns.tolist()}")

    df["time"] = pd.to_datetime(df["valid_time"]).dt.tz_localize(None)

    # pressure level 
    df["pressure_level"] = df["pressure_level"].astype(int).astype(str)

    # time + pressure_level 
    value_cols = [c for c in ["z", "t", "u", "v"] if c in df.columns]
    df_agg = (
        df.groupby(["time", "pressure_level"], as_index=False)[value_cols]
        .mean()
    )

    var_map = {
        "z": "GP",
        "t": "T",
        "u": "U",
        "v": "V",
    }

    wide_parts = []

    for raw_var, short_var in var_map.items():
        if raw_var not in df_agg.columns:
            print(f"Warning: {raw_var} not found in pressure data columns.")
            continue

        temp = (
            df_agg[["time", "pressure_level", raw_var]]
            .pivot(index="time", columns="pressure_level", values=raw_var)
            .rename(columns=lambda lvl: f"{short_var}_{lvl}")
            .reset_index()
        )
        wide_parts.append(temp)

    if not wide_parts:
        raise ValueError(
            f"No pressure-level variables found after reading NetCDF. "
            f"Available columns: {df_agg.columns.tolist()}"
        )

    out = wide_parts[0]
    for part in wide_parts[1:]:
        out = out.merge(part, on="time", how="outer")

    out = out.sort_values("time").reset_index(drop=True)
    return out
# =========================
# Download
# =========================
client = cdsapi.Client()

# 1) single-level zip
single_request = {
    "variable": SINGLE_VARS,
    "location": {
        "latitude": LAT,
        "longitude": LON,
    },
    "date": [f"{START_DATE}/{END_DATE}"],
    "data_format": "csv",
}

client.retrieve(
    "reanalysis-era5-single-levels-timeseries",
    single_request,
    str(SINGLE_ZIP),
)

# 2) pressure-level zip
years, months, days, times = build_date_parts(START_DATE, END_DATE)

pressure_request = {
    "product_type": ["reanalysis"],
    "variable": PRESSURE_VARS,
    "pressure_level": PRESSURE_LEVELS,
    "year": years,
    "month": months,
    "day": days,
    "time": times,
    "area": [45.50, 9.00, 45.25, 9.25],  # North, East, South, West
    "data_format": "netcdf",
    "download_format": "zip",
}

client.retrieve(
    "reanalysis-era5-pressure-levels",
    pressure_request,
    str(PRESSURE_ZIP),
)

# =========================
# Extract
# =========================
single_files = unzip_file(SINGLE_ZIP, SINGLE_EXTRACT)
pressure_files = unzip_file(PRESSURE_ZIP, PRESSURE_EXTRACT)

single_csv = first_existing(single_files, (".csv",))
pressure_nc = first_existing(pressure_files, (".nc", ".netcdf"))

print("Single extracted file:", single_csv)
print("Pressure extracted file:", pressure_nc)

# =========================
# Process
# =========================
single_df = process_single_csv(single_csv)
pressure_df = process_pressure_netcdf(pressure_nc)

# =========================
# Merge
# =========================
final_df = pd.merge(single_df, pressure_df, on="time", how="inner")
final_df = final_df.sort_values("time").reset_index(drop=True)

final_df["time"] = final_df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
final_df.to_csv(FINAL_CSV, index=False)

print(f"Saved merged CSV: {FINAL_CSV}")
print("Shape:", final_df.shape)
print(final_df.head())