from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    BASE_DIR /
    "data" /
    "processed" /
    "traffic_processed.csv"
)

MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


MODEL_PATH = (
    MODEL_DIR /
    "traffic_model.pkl"
)


# ============================================================
# LOAD PROCESSED DATA
# ============================================================

print("Loading processed data...")

df = pd.read_csv(
    DATA_PATH
)


print(
    f"Rows: {len(df)}"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [

    "Junction",

    "hour",

    "day_of_week",

    "day",

    "month",

    "year",

    "is_weekend",

    "is_peak_hour",

    "lag_1",

    "lag_2",

    "lag_3",

    "lag_24",

    "rolling_mean_3",

    "rolling_mean_6",

    "rolling_mean_24"

]


TARGET = "target"


# ============================================================
# INPUT / OUTPUT
# ============================================================

X = df[FEATURES]

y = df[TARGET]


# ============================================================
# TEMPORAL SPLIT
# ============================================================

# DO NOT SHUFFLE.
#
# First 80% = training
# Last 20% = testing

split_index = int(
    len(df) * 0.80
)


X_train = X.iloc[
    :split_index
]

X_test = X.iloc[
    split_index:
]


y_train = y.iloc[
    :split_index
]

y_test = y.iloc[
    split_index:
]


print("\n========================================")
print("             DATA SPLIT")
print("========================================")

print(
    f"Training rows: {len(X_train)}"
)

print(
    f"Testing rows : {len(X_test)}"
)


# ============================================================
# XGBOOST MODEL
# ============================================================

print("\nCreating XGBoost model...")


model = XGBRegressor(

    n_estimators=500,

    max_depth=8,

    learning_rate=0.05,

    subsample=0.8,

    colsample_bytree=0.8,

    objective="reg:squarederror",

    random_state=42,

    n_jobs=-1
)


# ============================================================
# TRAIN
# ============================================================

print(
    "Training model..."
)


model.fit(
    X_train,
    y_train
)


print(
    "Training completed."
)


# ============================================================
# PREDICT
# ============================================================

predictions = model.predict(
    X_test
)


# ============================================================
# METRICS
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)


rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5


r2 = r2_score(
    y_test,
    predictions
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n========================================")
print("           MODEL PERFORMANCE")
print("========================================")

print(
    f"MAE  : {mae:.4f}"
)

print(
    f"RMSE : {rmse:.4f}"
)

print(
    f"R²   : {r2:.4f}"
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({

    "feature":
        FEATURES,

    "importance":
        model.feature_importances_

})


importance = (
    importance
    .sort_values(
        "importance",
        ascending=False
    )
)


print("\n========================================")
print("          FEATURE IMPORTANCE")
print("========================================")

print(
    importance.to_string(
        index=False
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(

    {
        "model": model,

        "features": FEATURES,

        "mae": mae,

        "rmse": rmse,

        "r2": r2

    },

    MODEL_PATH
)


print("\n========================================")
print("          MODEL SAVED")
print("========================================")

print(
    MODEL_PATH
)