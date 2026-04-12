from pathlib import Path
import pandas as pd


# =========================
# File paths
# =========================
PM25_FILE = Path("PM25_MI_hourly.csv")
ERA5_FILE = Path("era5_work/era5_all_merged.csv")
OUTPUT_FILE = Path("pm25_era5_merged.csv")


def main() -> None:
    # 1. Read files
    pm25 = pd.read_csv(PM25_FILE)
    era5 = pd.read_csv(ERA5_FILE)

    # 2. Parse time columns
    pm25["Start"] = pd.to_datetime(pm25["Start"])
    pm25["End"] = pd.to_datetime(pm25["End"])
    era5["time"] = pd.to_datetime(era5["time"])

    # 3. Keep only required PM2.5 columns
    pm25_selected = pm25[["Start", "Value", "Unit"]].copy()

    # Rename Start to time for direct merge
    pm25_selected = pm25_selected.rename(columns={"Start": "time"})

    # Optional: rename Value to PM25 for clarity
    pm25_selected = pm25_selected.rename(columns={"Value": "PM25"})

    # 4. Merge on time
    merged = pd.merge(
        era5,
        pm25_selected,
        on="time",
        how="inner"
    )

    # 5. Reorder columns: put PM2.5 near the front
    front_cols = ["time", "PM25", "Unit"]
    other_cols = [c for c in merged.columns if c not in front_cols]
    merged = merged[front_cols + other_cols]

    # 6. Format time for output
    merged["time"] = merged["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # 7. Save
    merged.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print("Shape:", merged.shape)
    print(merged.head())


if __name__ == "__main__":
    main()