import csv
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from matplotlib.colors import rgb_to_hsv
from PIL import Image


IMG_EXTS = {".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"}
NAME_RE = re.compile(r"^(?P<date>\d{8})-(?P<hour>\d{4})$")


def load_rgb_array(image_path):
    img = Image.open(image_path).convert("RGB")
    return np.array(img)


def crop_roi(arr, top, left, height, width):
    return arr[top:top + height, left:left + width, :]


def mean_rgb(arr):
    if arr.size == 0:
        return np.nan, np.nan, np.nan

    r = arr[:, :, 0].mean()
    g = arr[:, :, 1].mean()
    b = arr[:, :, 2].mean()

    return float(r), float(g), float(b)


def mean_saturation(arr):
    if arr.size == 0:
        return np.nan

    arr_norm = arr / 255.0
    hsv = rgb_to_hsv(arr_norm)
    saturation = hsv[:, :, 1]

    return float(saturation.mean())


def blue_red_ratio(arr):
    if arr.size == 0:
        return np.nan

    r_mean = arr[:, :, 0].mean()
    b_mean = arr[:, :, 2].mean()

    eps = 1e-6

    return float(b_mean / (r_mean + eps))


def image_contrast(arr):
    if arr.size == 0:
        return np.nan

    gray = arr.mean(axis=2)

    return float(gray.std())


def extract_roi_features(image_path, roi):
    image_path = Path(image_path)
    arr = load_rgb_array(image_path)

    top = int(roi["top"])
    left = int(roi["left"])
    height = int(roi["height"])
    width = int(roi["width"])

    h, w, c = arr.shape

    if c != 3 or h < top + height or w < left + width:
        raise ValueError(
            f"Image too small for ROI cropping: {image_path.name}, image shape={arr.shape}, roi={roi}"
        )

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


def extract_image_features(
    image_dir,
    output_csv,
    roi,
    project_root=None,
    image_timezone="Europe/Rome",
    output_timezone="UTC",
):
    image_dir = Path(image_dir)
    output_csv = Path(output_csv)

    if project_root is not None:
        project_root = Path(project_root)

    rows = []
    skipped_files = []

    for image_path in sorted(image_dir.rglob("*")):
        if not (image_path.is_file() and image_path.suffix in IMG_EXTS):
            continue

        stem = image_path.stem

        if not NAME_RE.match(stem):
            skipped_files.append((str(image_path), "Invalid filename format"))
            continue

        try:
            dt_local = datetime.strptime(stem, "%Y%m%d-%H%M").replace(
                tzinfo=ZoneInfo(image_timezone)
            )
            dt_output = dt_local.astimezone(ZoneInfo(output_timezone))
        except ValueError:
            skipped_files.append((str(image_path), "Datetime parsing failed"))
            continue

        datetime_csv = dt_output.strftime("%Y-%m-%d %H:%M:%S")

        try:
            features = extract_roi_features(image_path, roi)
        except Exception as error:
            skipped_files.append((str(image_path), str(error)))
            continue

        if project_root is not None:
            try:
                image_path_value = str(image_path.relative_to(project_root))
            except ValueError:
                image_path_value = str(image_path)
        else:
            image_path_value = str(image_path)

        rows.append(
            {
                "datetime": datetime_csv,
                **features,
                "image_path": image_path_value,
            }
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "datetime",
        "R_roi",
        "G_roi",
        "B_roi",
        "S_mean",
        "B_R_ratio",
        "contrast",
        "image_path",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    #print(f"Saved image features: {output_csv}")
    #print(f"Rows written: {len(rows)}")
    #print(f"Skipped files: {len(skipped_files)}")

    return rows, skipped_files
