import re
import json
import csv
from pathlib import Path
from datetime import datetime

import numpy as np
from PIL import Image
from matplotlib.colors import rgb_to_hsv
from zoneinfo import ZoneInfo


IMG_EXTS = {".jpg", ".jpeg", ".JPG", ".JPEG"}
NAME_RE = re.compile(r"^(?P<date>\d{8})-(?P<hour>\d{4})$")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_rgb_array(p: Path) -> np.ndarray:
    img = Image.open(p).convert("RGB")
    return np.array(img)


def crop_roi(arr: np.ndarray, top: int, left: int, height: int, width: int) -> np.ndarray:
    return arr[top:top + height, left:left + width, :]


def mean_rgb(arr: np.ndarray):
    if arr.size == 0:
        return (np.nan, np.nan, np.nan)

    r = arr[:, :, 0].mean()
    g = arr[:, :, 1].mean()
    b = arr[:, :, 2].mean()

    return (float(r), float(g), float(b))


def mean_saturation(arr: np.ndarray):
    if arr.size == 0:
        return np.nan

    arr_norm = arr / 255.0
    hsv = rgb_to_hsv(arr_norm)
    saturation = hsv[:, :, 1]

    return float(saturation.mean())


def blue_red_ratio(arr: np.ndarray):
    if arr.size == 0:
        return np.nan

    r_mean = arr[:, :, 0].mean()
    b_mean = arr[:, :, 2].mean()

    eps = 1e-6
    return float(b_mean / (r_mean + eps))


def image_contrast(arr: np.ndarray):
    if arr.size == 0:
        return np.nan

    gray = arr.mean(axis=2)
    return float(gray.std())


def extract_roi_features(image_path: Path, roi: dict):
    arr = load_rgb_array(image_path)

    top = roi["top"]
    left = roi["left"]
    height = roi["height"]
    width = roi["width"]

    h, w, c = arr.shape

    if (
        c != 3
        or h < top + height
        or w < left + width
    ):
        raise ValueError("Image too small for ROI cropping")

    roi_arr = crop_roi(arr, top, left, height, width)

    r_roi, g_roi, b_roi = mean_rgb(roi_arr)
    s_mean = mean_saturation(roi_arr)
    br_ratio = blue_red_ratio(roi_arr)
    contrast = image_contrast(roi_arr)

    return {
        "R_roi": r_roi,
        "G_roi": g_roi,
        "B_roi": b_roi,
        "S_mean": s_mean,
        "B_R_ratio": br_ratio,
        "contrast": contrast,
    }


def extract_image_features(image_dir, output_csv, roi):
    image_dir = Path(image_dir)
    output_csv = Path(output_csv)

    rows = []
    skipped_files = []

    for p in sorted(image_dir.rglob("*")):
        if not (p.is_file() and p.suffix in IMG_EXTS):
            continue

        stem = p.stem

        if not NAME_RE.match(stem):
            skipped_files.append((str(p), "Invalid filename format"))
            continue

        try:
            dt_local = datetime.strptime(
                stem,
                "%Y%m%d-%H%M"
            ).replace(
                tzinfo=ZoneInfo("Europe/Rome")
            )

            dt_utc = dt_local.astimezone(ZoneInfo("UTC"))
        except ValueError:
            skipped_files.append((str(p), "Datetime parsing failed"))
            continue

        datetime_csv = dt_utc.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            features = extract_roi_features(p, roi)
        except Exception as e:
            skipped_files.append((str(p), str(e)))
            continue

        rows.append({
            "datetime": datetime_csv,
            **features,
            "image_path": str(p.relative_to(PROJECT_ROOT))
        })

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "datetime",
        "R_roi",
        "G_roi",
        "B_roi",
        "S_mean",
        "B_R_ratio",
        "contrast",
        "image_path"
    ]

    with output_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return rows, skipped_files
if __name__ == "__main__":
    
    IMAGE_DIR = PROJECT_ROOT / "data" / "raw" / "images"

    OUTPUT_CSV = (
        PROJECT_ROOT
        / "data"
        / "interim"
        / "image_features.csv"
    )

    import json

    ROI_JSON = PROJECT_ROOT / "config" / "roi.json"

    with open(ROI_JSON, "r") as f:
        ROI = json.load(f)
    rows, skipped_files = extract_image_features(
        image_dir=IMAGE_DIR,
        output_csv=OUTPUT_CSV,
        roi=ROI
    )

    print(f"Done. Wrote {len(rows)} rows.")
    print(f"Saved to: {OUTPUT_CSV}")
    print(f"Skipped files: {len(skipped_files)}")