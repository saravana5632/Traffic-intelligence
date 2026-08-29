from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "traffic.csv"


# ============================================================
# CHECK FILE
# ============================================================

if not DATA_PATH.exists():

    raise FileNotFoundError(
        f"Dataset not found:\n{DATA_PATH}"
    )


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)


# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n========================================")
print("           DATASET INSPECTION")
print("========================================")

print("\nFile:")
print(DATA_PATH)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nData Types:")
print(df.dtypes)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nFirst 5 Rows:")
print(df.head())

print("\nLast 5 Rows:")
print(df.tail())

print("\nJunctions:")
print(df["Junction"].unique())

print("\nVehicle Statistics:")
print(df["Vehicles"].describe())

print("\nDateTime range:")

print(
    df["DateTime"].iloc[0],
    "to",
    df["DateTime"].iloc[-1]
)