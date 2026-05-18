from __future__ import annotations

import zipfile
from pathlib import Path

import cdsapi
import numpy as np
import pandas as pd
import xarray as xr


def build_date_parts(start_date, end_date):
    dt_index = pd.date_range(
        start=start_date,
        end=end_date + " 23:00:00",
        freq="h",
    )

    years = sorted({f"{d.year:04d}" for d in dt_index})
    months = sorted({f"{d.month:02d}" for d in dt_index})
    days = sorted({f"{d.day:02d}" for d in dt_index})
    times = [f"{h:02d}:00" for h in range(24)]

    return years, months, days, times


def unzip_file(zip_path, extract_dir):
    extract_dir = Path(extract_dir)
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)
        names = zf.namelist()

    return [extract_dir / name for name in names]


def first_existing(paths, suffixes):
    for path in paths:
        if path.suffix.lower() in suffixes:
            return path

    raise FileNotFoundError(f"No file found with suffixes: {suffixes}")


def process_single_csv(csv_path):
    df = pd.read_csv(csv_path)

    #print("Single raw columns:", df.columns.tolist())

    if "valid_time" not in df.columns:
        raise KeyError(
            f"'valid_time' not found in single-level CSV columns: {df.columns.tolist()}"
        )

    df["time"] = pd.to_datetime(df["valid_time"]).dt.tz_localize(None)

    rename_map = {
        "2m_temperature": "T2M",
        "2m_dewpoint_temperature": "D2M",
        "10m_u_component_of_wind": "U10",
        "10m_v_component_of_wind": "V10",
        "surface_pressure": "SP",
        "total_precipitation": "TP",
        "boundary_layer_height": "BLH",
        "total_cloud_cover": "TCC",
        "cloud_base_height": "CBH",
        "t2m": "T2M",
        "d2m": "D2M",
        "u10": "U10",
        "v10": "V10",
        "sp": "SP",
        "tp": "TP",
        "blh": "BLH",
        "tcc": "TCC",
        "cbh": "CBH",
    }

    df = df.rename(columns=rename_map)

    if {"T2M", "D2M"}.issubset(df.columns):
        t_c = df["T2M"] - 273.15
        td_c = df["D2M"] - 273.15

        df["RH"] = 100.0 * np.exp(
            (17.625 * td_c) / (243.04 + td_c)
            - (17.625 * t_c) / (243.04 + t_c)
        )

        df["RH"] = df["RH"].clip(lower=0, upper=100)

    if {"U10", "V10"}.issubset(df.columns):
        df["WS10"] = np.sqrt(df["U10"] ** 2 + df["V10"] ** 2)

    drop_cols = [
        c for c in ["valid_time", "latitude", "longitude"]
        if c in df.columns
    ]

    df = df.drop(columns=drop_cols)

    keep_cols = [
        "time",
        "T2M",
        "D2M",
        "RH",
        "U10",
        "V10",
        "SP",
        "TP",
        "BLH",
        "TCC",
        "CBH",
        "WS10",
    ]

    keep_cols = [c for c in keep_cols if c in df.columns]

    out = df[keep_cols].sort_values("time").reset_index(drop=True)

    #print("Single processed columns:", out.columns.tolist())
    
    #print("Single processed shape:", out.shape)

    return out


def process_pressure_netcdf(nc_path):
    ds = xr.open_dataset(nc_path)

    df = ds.to_dataframe().reset_index()

    required = {"valid_time", "pressure_level"}

    if not required.issubset(df.columns):
        raise KeyError(
            f"Pressure data missing required columns. Found: {df.columns.tolist()}"
        )

    df["time"] = pd.to_datetime(df["valid_time"]).dt.tz_localize(None)

    df["pressure_level"] = (
        df["pressure_level"]
        .astype(int)
        .astype(str)
    )

    value_cols = [c for c in ["z", "t", "u", "v"] if c in df.columns]

    if len(value_cols) == 0:
        raise ValueError(
            f"No pressure-level variables found. Available columns: {df.columns.tolist()}"
        )

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
            print(f"Warning: {raw_var} not found in pressure data.")
            continue

        temp = (
            df_agg[["time", "pressure_level", raw_var]]
            .pivot(index="time", columns="pressure_level", values=raw_var)
            .rename(columns=lambda level: f"{short_var}_{level}")
            .reset_index()
        )

        wide_parts.append(temp)

    if len(wide_parts) == 0:
        raise ValueError("No pressure-level variables available after processing.")

    out = wide_parts[0]

    for part in wide_parts[1:]:
        out = out.merge(part, on="time", how="outer")

    out = out.sort_values("time").reset_index(drop=True)

    #print("Pressure processed columns:", out.columns.tolist())
    #print("Pressure processed shape:", out.shape)

    return out


def download_era5_data(
    lat,
    lon,
    start_date,
    end_date,
    work_dir,
    output_file,
    single_vars=None,
    pressure_vars=None,
    pressure_levels=None,
    pressure_area=None,
):
    work_dir = Path(work_dir)
    output_file = Path(output_file)

    work_dir.mkdir(parents=True, exist_ok=True)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    single_zip = work_dir / "single_levels.zip"
    pressure_zip = work_dir / "pressure_levels.zip"

    single_extract = work_dir / "single_extracted"
    pressure_extract = work_dir / "pressure_extracted"

    if single_vars is None:
        single_vars = [
            "2m_temperature",
            "2m_dewpoint_temperature",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "surface_pressure",
            "total_precipitation",
            "boundary_layer_height",
            "total_cloud_cover",
            "cloud_base_height",
        ]

    if pressure_vars is None:
        pressure_vars = [
            "geopotential",
            "temperature",
            "u_component_of_wind",
            "v_component_of_wind",
        ]

    if pressure_levels is None:
        pressure_levels = ["500", "850"]

    if pressure_area is None:
        pressure_area = [45.50, 9.00, 45.25, 9.25]

    client = cdsapi.Client()

    single_request = {
        "variable": single_vars,
        "location": {
            "latitude": lat,
            "longitude": lon,
        },
        "date": [f"{start_date}/{end_date}"],
        "data_format": "csv",
    }

    #print("Downloading ERA5 single-level data...")

    client.retrieve(
        "reanalysis-era5-single-levels-timeseries",
        single_request,
        str(single_zip),
    )

    years, months, days, times = build_date_parts(start_date, end_date)

    pressure_request = {
        "product_type": ["reanalysis"],
        "variable": pressure_vars,
        "pressure_level": pressure_levels,
        "year": years,
        "month": months,
        "day": days,
        "time": times,
        "area": pressure_area,
        "data_format": "netcdf",
        "download_format": "zip",
    }

    #print("Downloading ERA5 pressure-level data...")

    client.retrieve(
        "reanalysis-era5-pressure-levels",
        pressure_request,
        str(pressure_zip),
    )

    single_files = unzip_file(single_zip, single_extract)
    pressure_files = unzip_file(pressure_zip, pressure_extract)

    single_csv = first_existing(single_files, (".csv",))
    pressure_nc = first_existing(pressure_files, (".nc", ".netcdf"))

    #print("Single extracted file:", single_csv)
    #print("Pressure extracted file:", pressure_nc)

    single_df = process_single_csv(single_csv)
    pressure_df = process_pressure_netcdf(pressure_nc)

    final_df = pd.merge(
        single_df,
        pressure_df,
        on="time",
        how="inner",
    )

    final_df = final_df.sort_values("time").reset_index(drop=True)

    final_df["time"] = final_df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    final_df.to_csv(output_file, index=False)

    #print(f"Saved merged CSV: {output_file}")
    #print("Shape:", final_df.shape)
    #print(final_df.head())

    return final_df