# AI Urban Traffic Intelligence

AI-powered urban traffic prediction and analytics platform built with React, Flask, and XGBoost. The application analyzes historical traffic patterns to predict future traffic volume at urban junctions and provides congestion classification, risk scoring, traffic recommendations, and interactive analytics.

## Live Demo

Frontend: https://traffic-intelligence5632.vercel.app/

Backend API: https://traffic-intelligence-qtsr.onrender.com

Health Check: https://traffic-intelligence-qtsr.onrender.com/api/health

GitHub: https://github.com/saravana5632/Traffic-intelligence

## Features

- AI-based traffic volume prediction
- Junction-level traffic prediction
- Historical traffic analysis
- Peak-hour detection
- Congestion classification
- Traffic risk scoring
- AI-generated recommendations
- Hourly traffic analysis
- Junction comparison
- Interactive analytics dashboard
- REST API
- React frontend
- Flask backend
- XGBoost machine learning model
- Cloud deployment using Vercel and Render

## Project Structure

    Traffic-intelligence/
    │
    ├── backend/
    │   └── app.py
    │
    ├── data/
    │   ├── traffic.csv
    │   └── processed/
    │       └── traffic_processed.csv
    │
    ├── frontend/
    │   ├── src/
    │   │   ├── App.jsx
    │   │   ├── AnalyticsDashboard.jsx
    │   │   ├── App.css
    │   │   └── ...
    │   ├── package.json
    │   └── ...
    │
    ├── ml/
    │   ├── preprocess.py
    │   └── train.py
    │
    ├── models/
    │   └── traffic_model.pkl
    │
    ├── requirements.txt
    ├── pyproject.toml
    └── README.md

## System Architecture

    User
      │
      ▼
    React Frontend
      │
      │ HTTPS / REST API
      ▼
    Flask Backend
      │
      ├── Historical Traffic Data
      ├── XGBoost Model
      └── Analytics Engine
      │
      ▼
    Traffic Prediction
      │
      ├── Predicted Vehicles
      ├── Historical Average
      ├── Congestion Level
      ├── Risk Score
      ├── Peak Period
      └── Recommendation

## Machine Learning

The project uses an XGBoost regression model to predict future traffic volume.

### Model Configuration

    Algorithm: XGBRegressor
    Objective: reg:squarederror
    Estimators: 500
    Maximum Depth: 8
    Learning Rate: 0.05
    Subsample: 0.8
    Column Sampling: 0.8
    Random State: 42

The model is trained using a chronological 80/20 train-test split without shuffling in order to preserve the temporal sequence of traffic observations.

### Evaluation Metrics

The model is evaluated using:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score

The trained model is serialized using Joblib and stored at:

    models/traffic_model.pkl

## Feature Engineering

The model uses temporal and historical traffic features.

### Time Features

    Junction
    hour
    day_of_week
    day
    month
    year

### Calendar Features

    is_weekend
    is_peak_hour

### Lag Features

    lag_1
    lag_2
    lag_3
    lag_24

### Rolling Features

    rolling_mean_3
    rolling_mean_6
    rolling_mean_24

These features allow the model to learn traffic behaviour from both time-based patterns and recent historical observations.

## Traffic Prediction Pipeline

    User selects Junction and DateTime
                  │
                  ▼
           React Frontend
                  │
                  ▼
           POST /api/predict
                  │
                  ▼
            Flask Backend
                  │
                  ▼
       Historical Junction Data
                  │
                  ▼
         Feature Engineering
                  │
                  ▼
             XGBoost Model
                  │
                  ▼
        Predicted Traffic Volume
                  │
          ┌───────┴───────┐
          ▼               ▼
    Congestion Level   Risk Score
          │
          ▼
    AI Recommendation
          │
          ▼
    React Dashboard

## Congestion Classification

The system compares the predicted traffic volume against the historical traffic baseline.

| Traffic Level | Condition |
|---|---|
| LOW | Less than 80% of historical average |
| MODERATE | 80% to less than 110% |
| HIGH | 110% to less than 140% |
| CRITICAL | 140% or higher |

## Risk Score

A traffic risk score from 0 to 100 is calculated using the relationship between predicted traffic and the historical traffic baseline.

A higher predicted traffic ratio represents a higher traffic risk.

## Peak-Hour Detection

The system identifies peak traffic periods based on predefined traffic patterns.

Morning Peak: 07:00 – 10:00

Evening Peak: 16:00 – 20:00

The peak-period information is included in the prediction result and is also used when generating traffic recommendations.

## Traffic Recommendations

The system generates recommendations according to the predicted traffic level and peak-hour status.

Examples:

- Traffic conditions are within the expected range.
- Monitor traffic conditions during this period.
- High traffic demand is expected during the peak period. Consider traffic-flow management measures.
- Critical traffic demand is expected. Traffic-management attention may be required.

## Backend API

Base URL:

https://traffic-intelligence-qtsr.onrender.com

### Root Endpoint

    GET /

Returns basic information about the AI traffic intelligence system.

Example response:

    {
      "system": "AI Urban Traffic Intelligence",
      "status": "running",
      "model": "XGBoost",
      "prediction": "Next-hour traffic volume"
    }

### Health Check

    GET /api/health

Example response:

    {
      "status": "healthy",
      "model_loaded": true,
      "dataset_loaded": true
    }

### Get Junctions

    GET /api/junctions

Example response:

    {
      "success": true,
      "junctions": [1, 2, 3, 4]
    }

### Traffic Prediction

    POST /api/predict

Example request:

    {
      "Junction": 1,
      "DateTime": "2017-06-30T10:00"
    }

Example response:

    {
      "success": true,
      "junction": 1,
      "requested_datetime": "2017-06-30 10:00",
      "predicted_vehicles": 123.45,
      "historical_average": 110.25,
      "congestion_level": "HIGH",
      "risk_score": 78.42,
      "is_peak_hour": true,
      "last_observation": "2017-06-30 09:00",
      "recommendation": "High traffic demand is expected during the peak period."
    }

## Analytics API

The backend provides the following analytics endpoints:

    GET /api/analytics/summary
    GET /api/analytics/junctions
    GET /api/analytics/hourly
    GET /api/analytics/peak

These endpoints provide overall traffic statistics, junction-level statistics, hourly traffic patterns, and peak-hour analysis.

## Frontend

The frontend is built using React, Vite, Recharts, JavaScript, and CSS.

### Prediction Dashboard

Users can select a junction and prediction date/time. The frontend sends the request to the Flask backend and displays:

- Predicted Vehicles
- Historical Average
- Congestion Level
- Risk Score
- Peak Period
- Last Historical Observation
- AI Recommendation

### Analytics Dashboard

The analytics dashboard provides:

- Total observations
- Average vehicles
- Maximum vehicles
- Minimum vehicles
- Monitored junctions
- Peak traffic hour
- Lowest traffic hour
- Traffic range
- Hourly traffic pattern
- Junction comparison
- Junction intelligence table

## Technology Stack

| Category | Technology |
|---|---|
| Frontend | React |
| Build Tool | Vite |
| Visualization | Recharts |
| Backend | Flask |
| API | REST |
| Machine Learning | XGBoost |
| Data Processing | Pandas |
| Numerical Computing | NumPy |
| Machine Learning Utilities | Scikit-learn |
| Model Serialization | Joblib |
| CORS | Flask-CORS |
| Production Server | Gunicorn |
| Frontend Hosting | Vercel |
| Backend Hosting | Render |

## Requirements

### Backend

    pandas
    numpy
    scikit-learn
    xgboost
    joblib
    flask
    flask-cors
    gunicorn

### Frontend

    react
    react-dom
    recharts
    vite

## Local Installation

### Clone the Repository

    git clone https://github.com/saravana5632/Traffic-intelligence.git
    cd Traffic-intelligence

### Backend Setup

Create a virtual environment.

Windows:

    python -m venv venv
    venv\Scripts\activate

Linux/macOS:

    python3 -m venv venv
    source venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Run the Flask backend:

    python backend/app.py

The backend runs locally at:

    http://127.0.0.1:5000

### Frontend Setup

Open another terminal:

    cd frontend
    npm install
    npm run dev

## Model Training

### Preprocess Data

From the project root:

    python ml/preprocess.py

### Train Model

    python ml/train.py

The trained model is generated at:

    models/traffic_model.pkl

## Deployment

The project uses separate deployments for the frontend and backend.

### Frontend — Vercel

Frontend root directory:

    frontend

Build command:

    npm run build

Production URL:

https://traffic-intelligence5632.vercel.app/

### Backend — Render

Service type:

    Web Service

Root directory:

    .

Build command:

    pip install -r requirements.txt

Start command:

    gunicorn backend.app:app

Production API:

https://traffic-intelligence-qtsr.onrender.com

## Environment Variable

For production frontend configuration:

    VITE_API_URL=https://traffic-intelligence-qtsr.onrender.com

In React:

    const API_URL = import.meta.env.VITE_API_URL;

Example request:

    fetch(`${API_URL}/api/junctions`);

Prediction request:

    fetch(`${API_URL}/api/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        Junction: 1,
        DateTime: "2017-06-30T10:00"
      })
    });

## Production Flow

    https://traffic-intelligence5632.vercel.app/
                      │
                      ▼
               React Frontend
                      │
                      │ HTTPS
                      ▼
    https://traffic-intelligence-qtsr.onrender.com
                      │
                      ▼
                Flask REST API
                      │
            ┌─────────┼─────────┐
            ▼         ▼         ▼
       Prediction  Analytics  Junctions
            │         │         │
            └─────────┼─────────┘
                      ▼
                Traffic Data
                      │
                      ▼
                   XGBoost
                      │
                      ▼
            Traffic Intelligence

## API Test

Example cURL request:

    curl -X POST https://traffic-intelligence-qtsr.onrender.com/api/predict \
      -H "Content-Type: application/json" \
      -d "{\"Junction\":1,\"DateTime\":\"2017-06-30T10:00\"}"

## Error Handling

The backend handles:

- Missing request body
- Missing junction
- Missing date/time
- Invalid date/time
- Invalid junction
- Insufficient historical data
- Missing required features
- Model and runtime errors

Example error response:

    {
      "success": false,
      "error": "Not enough historical data to generate a prediction."
    }

## Dataset

The project uses historical traffic observations for machine learning and traffic analytics.

The dataset is used for:

- Model training
- Feature engineering
- Historical traffic analysis
- Traffic baseline calculation
- Traffic prediction
- Junction comparison
- Hourly traffic analysis

## Advantages

- Predicts future traffic volume
- Provides junction-level intelligence
- Learns from historical traffic patterns
- Detects peak traffic periods
- Classifies congestion
- Calculates traffic risk
- Generates traffic recommendations
- Provides interactive analytics
- Exposes REST APIs
- Supports cloud deployment
- Separates frontend and backend services

## Future Improvements

- Real-time traffic data integration
- Live traffic maps
- Weather-aware traffic prediction
- Accident detection
- Incident detection
- Multi-junction forecasting
- Longer-term traffic forecasting
- Traffic signal optimization
- Real-time notifications
- Automated model retraining
- Model performance monitoring
- Traffic anomaly detection
- Geographic traffic visualization
- IoT traffic sensor integration

## Project Goals

1. Analyze historical urban traffic behaviour.
2. Predict future traffic volume.
3. Identify potential congestion periods.
4. Calculate traffic risk levels.
5. Generate useful traffic recommendations.
6. Visualize historical traffic intelligence.
7. Integrate machine learning with a full-stack web application.
8. Deploy the application using modern cloud platforms.

## Author

### Saravanakumar

AI Urban Traffic Intelligence

Live Application: https://traffic-intelligence5632.vercel.app/

Backend API: https://traffic-intelligence-qtsr.onrender.com

GitHub Repository: https://github.com/saravana5632/Traffic-intelligence

## License

This project is intended for educational, demonstration, and research purposes.
```
