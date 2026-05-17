import pandas as pd
from functools import reduce

# 1. 读取三个表
arpa = pd.read_csv("arpa_merged.csv")
image_features = pd.read_csv("image_feature_roi.csv")
era5_pm25 = pd.read_csv("pm25_era5_merged.csv")

# 2. 清理列名
arpa.columns = arpa.columns.str.strip()
image_features.columns = image_features.columns.str.strip()
era5_pm25.columns = era5_pm25.columns.str.strip()

# 3. 统一 ARPA 时间列名
arpa = arpa.rename(columns={"Data-Ora": "time"})

# 4. 图片表：date + hour 合成 time
image_features["time"] = pd.to_datetime(
    image_features["date"].astype(str) + " " + image_features["hour"].astype(str)
)

# 5. 其他两个表转换时间格式
arpa["time"] = pd.to_datetime(arpa["time"])
era5_pm25["time"] = pd.to_datetime(era5_pm25["time"])

# 6. 删除图片表中原始 date/hour，避免重复
image_features = image_features.drop(columns=["date", "hour"])

# 7. 只保留三个表共同存在的时间
merged_all = reduce(
    lambda left, right: pd.merge(left, right, on="time", how="inner"),
    [arpa, era5_pm25, image_features]
)

# 8. 按时间排序
merged_all = merged_all.sort_values("time")

# 9. 保存结果
merged_all.to_csv("final_merged_all.csv", index=False)

print(merged_all.head())
print("Final rows:", len(merged_all))