from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "traffic.csv"

PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = (
    PROCESSED_DIR /
    "traffic_processed.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)

print(
    f"Original rows: {len(df)}"
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

df = df.drop_duplicates()


# ============================================================
# DATETIME CONVERSION
# ============================================================

df["DateTime"] = pd.to_datetime(
    df["DateTime"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)


# ============================================================
# CHECK INVALID DATES
# ============================================================

invalid_dates = df["DateTime"].isna().sum()

if invalid_dates > 0:

    raise ValueError(
        f"Invalid DateTime values found: "
        f"{invalid_dates}"
    )


# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    [
        "Junction",
        "DateTime"
    ]
).reset_index(drop=True)


# ============================================================
# TIME FEATURES
# ============================================================

df["hour"] = (
    df["DateTime"].dt.hour
)

df["day_of_week"] = (
    df["DateTime"].dt.dayofweek
)

df["day"] = (
    df["DateTime"].dt.day
)

df["month"] = (
    df["DateTime"].dt.month
)

df["year"] = (
    df["DateTime"].dt.year
)


# ============================================================
# WEEKEND
# ============================================================

df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)


# ============================================================
# PEAK HOUR
# ============================================================

morning_peak = (
    df["hour"].between(
        7,
        10
    )
)

evening_peak = (
    df["hour"].between(
        16,
        20
    )
)

df["is_peak_hour"] = (
    morning_peak |
    evening_peak
).astype(int)


# ============================================================
# LAG FEATURES
# ============================================================

grouped = (
    df.groupby("Junction")["Vehicles"]
)


df["lag_1"] = (
    grouped.shift(1)
)


df["lag_2"] = (
    grouped.shift(2)
)


df["lag_3"] = (
    grouped.shift(3)
)


df["lag_24"] = (
    grouped.shift(24)
)


# ============================================================
# ROLLING AVERAGES
# ============================================================

df["rolling_mean_3"] = (
    df.groupby("Junction")["Vehicles"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(3)
        .mean()
    )
)


df["rolling_mean_6"] = (
    df.groupby("Junction")["Vehicles"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(6)
        .mean()
    )
)


df["rolling_mean_24"] = (
    df.groupby("Junction")["Vehicles"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(24)
        .mean()
    )
)


# ============================================================
# TARGET
# ============================================================

# Target = vehicle count of the next hour

df["target"] = (
    df.groupby("Junction")["Vehicles"]
    .shift(-1)
)


# ============================================================
# REMOVE NaN
# ============================================================

before = len(df)

df = df.dropna().reset_index(drop=True)

after = len(df)


print(
    f"Removed {before - after} rows "
    f"because of lag/target requirements."
)


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# RESULT
# ============================================================

print("\n========================================")
print("      PREPROCESSING COMPLETED")
print("========================================")

print(
    f"Processed rows: {len(df)}"
)

print(
    f"Processed columns: {len(df.columns)}"
)

print(
    f"Saved to:\n{OUTPUT_PATH}"
)

print("\nColumns:")
print(df.columns.tolist())