from pathlib import Path

import joblib
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "traffic.csv"

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "traffic_model.pkl"
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# CHECK FILES
# ============================================================

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Traffic dataset not found:\n{DATA_PATH}"
    )


if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Traffic model not found:\n{MODEL_PATH}\n\n"
        "Run these commands first:\n"
        "python ml\\preprocess.py\n"
        "python ml\\train.py"
    )


# ============================================================
# LOAD ML MODEL
# ============================================================

saved_model = joblib.load(MODEL_PATH)

model = saved_model["model"]

FEATURES = saved_model["features"]


# ============================================================
# LOAD TRAFFIC DATA
# ============================================================

traffic_df = pd.read_csv(DATA_PATH)


traffic_df["DateTime"] = pd.to_datetime(
    traffic_df["DateTime"],
    format="%d-%m-%Y %H:%M",
    errors="coerce"
)


traffic_df = traffic_df.dropna(
    subset=["DateTime"]
)


traffic_df = traffic_df.sort_values(
    [
        "Junction",
        "DateTime"
    ]
).reset_index(drop=True)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def create_features(df):
    """
    Generate the same features used during model training.
    """

    data = df.copy()

    # --------------------------------------------------------
    # TIME FEATURES
    # --------------------------------------------------------

    data["hour"] = (
        data["DateTime"].dt.hour
    )

    data["day_of_week"] = (
        data["DateTime"].dt.dayofweek
    )

    data["day"] = (
        data["DateTime"].dt.day
    )

    data["month"] = (
        data["DateTime"].dt.month
    )

    data["year"] = (
        data["DateTime"].dt.year
    )


    # --------------------------------------------------------
    # WEEKEND
    # --------------------------------------------------------

    data["is_weekend"] = (
        data["day_of_week"] >= 5
    ).astype(int)


    # --------------------------------------------------------
    # PEAK HOUR
    # --------------------------------------------------------

    morning_peak = (
        data["hour"].between(7, 10)
    )

    evening_peak = (
        data["hour"].between(16, 20)
    )

    data["is_peak_hour"] = (
        morning_peak |
        evening_peak
    ).astype(int)


    # --------------------------------------------------------
    # LAG FEATURES
    # --------------------------------------------------------

    grouped = (
        data.groupby("Junction")["Vehicles"]
    )

    data["lag_1"] = (
        grouped.shift(1)
    )

    data["lag_2"] = (
        grouped.shift(2)
    )

    data["lag_3"] = (
        grouped.shift(3)
    )

    data["lag_24"] = (
        grouped.shift(24)
    )


    # --------------------------------------------------------
    # ROLLING FEATURES
    # --------------------------------------------------------

    data["rolling_mean_3"] = (
        data.groupby("Junction")["Vehicles"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(3)
            .mean()
        )
    )

    data["rolling_mean_6"] = (
        data.groupby("Junction")["Vehicles"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(6)
            .mean()
        )
    )

    data["rolling_mean_24"] = (
        data.groupby("Junction")["Vehicles"]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(24)
            .mean()
        )
    )


    return data


# Create features once when Flask starts
traffic_features = create_features(
    traffic_df
)


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "system":
            "AI Urban Traffic Intelligence",

        "status":
            "running",

        "model":
            "XGBoost",

        "prediction":
            "Next-hour traffic volume"
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status":
            "healthy",

        "model_loaded":
            True,

        "dataset_loaded":
            True
    })


# ============================================================
# GET JUNCTIONS
# ============================================================

@app.route(
    "/api/junctions",
    methods=["GET"]
)
def get_junctions():

    junctions = sorted(
        traffic_df["Junction"]
        .dropna()
        .unique()
        .tolist()
    )

    return jsonify({
        "success": True,
        "junctions": junctions
    })


# ============================================================
# TRAFFIC CLASSIFICATION
# ============================================================

def calculate_traffic_level(
    predicted_vehicles,
    historical_average
):

    if historical_average <= 0:

        return (
            "UNKNOWN",
            0
        )


    ratio = (
        predicted_vehicles /
        historical_average
    )


    if ratio < 0.80:

        level = "LOW"

    elif ratio < 1.10:

        level = "MODERATE"

    elif ratio < 1.40:

        level = "HIGH"

    else:

        level = "CRITICAL"


    risk_score = min(
        ratio * 70,
        100
    )


    return (
        level,
        round(
            risk_score,
            2
        )
    )


# ============================================================
# RECOMMENDATION
# ============================================================

def generate_recommendation(
    level,
    is_peak_hour
):

    if level == "LOW":

        return (
            "Traffic conditions are "
            "within the expected range."
        )


    if level == "MODERATE":

        return (
            "Monitor traffic conditions "
            "during this period."
        )


    if level == "HIGH":

        if is_peak_hour:

            return (
                "High traffic demand is "
                "expected during the peak "
                "period. Consider traffic-flow "
                "management measures."
            )

        return (
            "High traffic demand is "
            "expected outside the normal "
            "peak period. Investigate "
            "this junction for unusual "
            "traffic conditions."
        )


    return (
        "Critical traffic demand is "
        "expected. Traffic-management "
        "attention may be required."
    )


# ============================================================
# PREDICTION API
# ============================================================

@app.route(
    "/api/predict",
    methods=["POST"]
)
def predict():

    try:

        # ----------------------------------------------------
        # READ JSON
        # ----------------------------------------------------

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "error":
                    "JSON request body is required."
            }), 400


        # ----------------------------------------------------
        # CHECK INPUTS
        # ----------------------------------------------------

        if "Junction" not in data:

            return jsonify({
                "success": False,
                "error":
                    "Junction is required."
            }), 400


        if "DateTime" not in data:

            return jsonify({
                "success": False,
                "error":
                    "DateTime is required."
            }), 400


        junction = int(
            data["Junction"]
        )


        requested_datetime = pd.to_datetime(
            data["DateTime"],
            errors="coerce"
        )


        if pd.isna(
            requested_datetime
        ):

            return jsonify({
                "success": False,
                "error":
                    "Invalid DateTime."
            }), 400


        # ----------------------------------------------------
        # VALID JUNCTION?
        # ----------------------------------------------------

        available_junctions = (
            traffic_df["Junction"]
            .unique()
        )


        if junction not in available_junctions:

            return jsonify({
                "success": False,
                "error":
                    f"Junction {junction} does not exist."
            }), 404


        # ----------------------------------------------------
        # GET JUNCTION HISTORY
        # ----------------------------------------------------

        junction_data = (
            traffic_features[
                traffic_features["Junction"]
                == junction
            ]
            .copy()
        )


        # ----------------------------------------------------
        # RECORDS BEFORE REQUESTED TIME
        # ----------------------------------------------------

        historical_rows = (
            junction_data[
                junction_data["DateTime"]
                < requested_datetime
            ]
            .sort_values(
                "DateTime"
            )
        )


        if historical_rows.empty:

            return jsonify({
                "success": False,
                "error":
                    "Not enough historical data "
                    "for this DateTime."
            }), 400


        # Latest known traffic record
        latest = (
            historical_rows
            .iloc[-1]
        )


        # ----------------------------------------------------
        # CHECK REQUIRED FEATURES
        # ----------------------------------------------------

        required_features = [

            "lag_1",
            "lag_2",
            "lag_3",
            "lag_24",

            "rolling_mean_3",
            "rolling_mean_6",
            "rolling_mean_24"

        ]


        for feature in required_features:

            if pd.isna(
                latest[feature]
            ):

                return jsonify({
                    "success": False,
                    "error":
                        "Not enough historical "
                        "data to generate a prediction."
                }), 400


        # ----------------------------------------------------
        # DETERMINE TIME FEATURES
        # ----------------------------------------------------

        hour = (
            requested_datetime.hour
        )

        day_of_week = (
            requested_datetime.dayofweek
        )

        day = (
            requested_datetime.day
        )

        month = (
            requested_datetime.month
        )

        year = (
            requested_datetime.year
        )

        is_weekend = int(
            day_of_week >= 5
        )

        is_peak_hour = int(
            (
                7 <= hour <= 10
            )
            or
            (
                16 <= hour <= 20
            )
        )


        # ----------------------------------------------------
        # CREATE MODEL INPUT
        # ----------------------------------------------------

        input_data = pd.DataFrame([{

            "Junction":
                junction,

            "hour":
                hour,

            "day_of_week":
                day_of_week,

            "day":
                day,

            "month":
                month,

            "year":
                year,

            "is_weekend":
                is_weekend,

            "is_peak_hour":
                is_peak_hour,

            "lag_1":
                latest["lag_1"],

            "lag_2":
                latest["lag_2"],

            "lag_3":
                latest["lag_3"],

            "lag_24":
                latest["lag_24"],

            "rolling_mean_3":
                latest["rolling_mean_3"],

            "rolling_mean_6":
                latest["rolling_mean_6"],

            "rolling_mean_24":
                latest["rolling_mean_24"]

        }])


        # ----------------------------------------------------
        # CORRECT FEATURE ORDER
        # ----------------------------------------------------

        input_data = (
            input_data[FEATURES]
        )


        # ----------------------------------------------------
        # XGBOOST
        # ----------------------------------------------------

        prediction = model.predict(
            input_data
        )[0]


        prediction = float(
            prediction
        )


        # ----------------------------------------------------
        # HISTORICAL BASELINE
        # ----------------------------------------------------

        historical_average = float(
            latest["rolling_mean_24"]
        )


        # ----------------------------------------------------
        # TRAFFIC LEVEL
        # ----------------------------------------------------

        level, risk_score = (
            calculate_traffic_level(
                prediction,
                historical_average
            )
        )


        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        recommendation = (
            generate_recommendation(
                level,
                is_peak_hour
            )
        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success":
                True,

            "junction":
                junction,

            "requested_datetime":
                requested_datetime.strftime(
                    "%Y-%m-%d %H:%M"
                ),

            "predicted_vehicles":
                round(
                    prediction,
                    2
                ),

            "historical_average":
                round(
                    historical_average,
                    2
                ),

            "congestion_level":
                level,

            "risk_score":
                risk_score,

            "is_peak_hour":
                bool(
                    is_peak_hour
                ),

            "last_observation":
                latest["DateTime"].strftime(
                    "%Y-%m-%d %H:%M"
                ),

            "recommendation":
                recommendation

        })


    except ValueError as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 400


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# ANALYTICS - SUMMARY
# ============================================================

@app.route(
    "/api/analytics/summary",
    methods=["GET"]
)
def analytics_summary():

    try:

        total_observations = int(
            len(traffic_df)
        )

        total_vehicles = int(
            traffic_df["Vehicles"].sum()
        )

        average_vehicles = float(
            traffic_df["Vehicles"].mean()
        )

        maximum_vehicles = int(
            traffic_df["Vehicles"].max()
        )

        minimum_vehicles = int(
            traffic_df["Vehicles"].min()
        )

        junction_count = int(
            traffic_df["Junction"].nunique()
        )


        return jsonify({

            "success":
                True,

            "total_observations":
                total_observations,

            "total_vehicles":
                total_vehicles,

            "average_vehicles":
                round(
                    average_vehicles,
                    2
                ),

            "maximum_vehicles":
                maximum_vehicles,

            "minimum_vehicles":
                minimum_vehicles,

            "junction_count":
                junction_count

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# ANALYTICS - JUNCTIONS
# ============================================================

@app.route(
    "/api/analytics/junctions",
    methods=["GET"]
)
def analytics_junctions():

    try:

        result = (
            traffic_df
            .groupby("Junction")
            .agg(

                average_vehicles=(
                    "Vehicles",
                    "mean"
                ),

                maximum_vehicles=(
                    "Vehicles",
                    "max"
                ),

                total_vehicles=(
                    "Vehicles",
                    "sum"
                ),

                observations=(
                    "Vehicles",
                    "count"
                )

            )
            .reset_index()
        )


        result = result.sort_values(
            "average_vehicles",
            ascending=False
        )


        records = []


        for _, row in result.iterrows():

            records.append({

                "junction":
                    int(
                        row["Junction"]
                    ),

                "average_vehicles":
                    round(
                        float(
                            row[
                                "average_vehicles"
                            ]
                        ),
                        2
                    ),

                "maximum_vehicles":
                    int(
                        row[
                            "maximum_vehicles"
                        ]
                    ),

                "total_vehicles":
                    int(
                        row[
                            "total_vehicles"
                        ]
                    ),

                "observations":
                    int(
                        row[
                            "observations"
                        ]
                    )

            })


        return jsonify({

            "success":
                True,

            "junctions":
                records

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# ANALYTICS - HOURLY
# ============================================================

@app.route(
    "/api/analytics/hourly",
    methods=["GET"]
)
def analytics_hourly():

    try:

        data = traffic_df.copy()

        data["hour"] = (
            data["DateTime"].dt.hour
        )


        hourly = (
            data
            .groupby("hour")["Vehicles"]
            .mean()
            .reset_index()
        )


        records = []


        for _, row in hourly.iterrows():

            records.append({

                "hour":
                    int(
                        row["hour"]
                    ),

                "average_vehicles":
                    round(
                        float(
                            row["Vehicles"]
                        ),
                        2
                    )

            })


        return jsonify({

            "success":
                True,

            "hourly":
                records

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# ANALYTICS - PEAK
# ============================================================

@app.route(
    "/api/analytics/peak",
    methods=["GET"]
)
def analytics_peak():

    try:

        data = traffic_df.copy()

        data["hour"] = (
            data["DateTime"].dt.hour
        )


        hourly = (
            data
            .groupby("hour")["Vehicles"]
            .mean()
            .reset_index()
        )


        peak_row = hourly.loc[
            hourly["Vehicles"].idxmax()
        ]


        lowest_row = hourly.loc[
            hourly["Vehicles"].idxmin()
        ]


        return jsonify({

            "success":
                True,

            "peak_hour":
                int(
                    peak_row["hour"]
                ),

            "peak_average_vehicles":
                round(
                    float(
                        peak_row["Vehicles"]
                    ),
                    2
                ),

            "lowest_hour":
                int(
                    lowest_row["hour"]
                ),

            "lowest_average_vehicles":
                round(
                    float(
                        lowest_row["Vehicles"]
                    ),
                    2
                )

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )