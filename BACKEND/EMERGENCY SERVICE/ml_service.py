"""
Machine Learning service for Flood Prediction.
Centralizes 13-feature input vector construction, derived feature engineering,
StandardScaler transformation, and SVM model inference with risk classification.
Preserves existing ML model and scaler without modification.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

from config import (
    MODEL_PATH,
    SCALER_PATH,
    METADATA_PATH,
    ML_DIR,
    DEFAULT_ELEVATION,
    DEFAULT_DRAINAGE,
    DEFAULT_HUMIDITY,
    DEFAULT_SOIL_TYPE,
    DEFAULT_POPULATION_DENSITY,
    DEFAULT_DISTANCE_TO_RIVER,
    DEFAULT_HISTORICAL_FLOOD_FREQ,
    DEFAULT_DRAINAGE_CAPACITY,
)

# Import existing risk_classifier without modifying it
if ML_DIR not in sys.path:
    sys.path.insert(0, ML_DIR)

try:
    import risk_classifier
except ImportError:
    risk_classifier = None

# Exact 13 features required by the trained model in exact sequence
FEATURE_NAMES = [
    "rainfall",
    "water_level",
    "elevation",
    "drainage",
    "humidity",
    "soil_type",
    "population_density",
    "distance_to_river",
    "historical_flood_freq",
    "drainage_capacity",
    "rainfall_water_index",
    "flood_risk_index",
    "proximity_risk",
]

# Global cache for loaded model and scaler
_model = None
_scaler = None
_metadata = None


def load_ml_assets():
    """
    Loads model, scaler, and metadata once.
    """
    global _model, _scaler, _metadata

    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")
        _model = joblib.load(MODEL_PATH)

    if _scaler is None:
        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
        _scaler = joblib.load(SCALER_PATH)

    if _metadata is None and os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r") as f:
            _metadata = json.load(f)

    return _model, _scaler, _metadata


def construct_features(raw_input):
    """
    Validates, fills regional defaults, and engineers the 3 derived features
    to produce the exact 13-feature vector for the model.

    Args:
        raw_input (dict): Raw dictionary containing any subset of input features.

    Returns:
        pd.DataFrame: DataFrame containing exactly 13 columns in correct order.
    """
    # Extract base features with regional defaults
    rainfall = float(raw_input.get("rainfall", 80.0))
    water_level = float(raw_input.get("water_level", 1.8))
    elevation = int(raw_input.get("elevation", DEFAULT_ELEVATION))
    drainage = int(raw_input.get("drainage", DEFAULT_DRAINAGE))
    humidity = float(raw_input.get("humidity", DEFAULT_HUMIDITY))
    soil_type = int(raw_input.get("soil_type", DEFAULT_SOIL_TYPE))
    population_density = int(raw_input.get("population_density", DEFAULT_POPULATION_DENSITY))
    distance_to_river = float(raw_input.get("distance_to_river", DEFAULT_DISTANCE_TO_RIVER))
    historical_flood_freq = int(raw_input.get("historical_flood_freq", DEFAULT_HISTORICAL_FLOOD_FREQ))
    drainage_capacity = float(raw_input.get("drainage_capacity", DEFAULT_DRAINAGE_CAPACITY))

    # Basic boundary safety
    rainfall = max(0.0, min(rainfall, 500.0))
    water_level = max(0.0, min(water_level, 10.0))
    elevation = max(1, min(elevation, 3))
    drainage = max(1, min(drainage, 3))
    humidity = max(10.0, min(humidity, 100.0))
    soil_type = max(1, min(soil_type, 3))
    population_density = max(1, min(population_density, 3))
    distance_to_river = max(0.1, min(distance_to_river, 30.0))
    historical_flood_freq = max(0, min(historical_flood_freq, 10))
    drainage_capacity = max(50.0, min(drainage_capacity, 2000.0))

    # Engineer 3 derived features exactly as done during training (train_model.py)
    rainfall_water_index = rainfall * water_level
    flood_risk_index = (4 - elevation) * (4 - drainage) * rainfall / 1000.0
    proximity_risk = 1.0 / (distance_to_river + 0.1)

    feature_dict = {
        "rainfall": rainfall,
        "water_level": water_level,
        "elevation": elevation,
        "drainage": drainage,
        "humidity": humidity,
        "soil_type": soil_type,
        "population_density": population_density,
        "distance_to_river": distance_to_river,
        "historical_flood_freq": historical_flood_freq,
        "drainage_capacity": drainage_capacity,
        "rainfall_water_index": rainfall_water_index,
        "flood_risk_index": flood_risk_index,
        "proximity_risk": proximity_risk,
    }

    df = pd.DataFrame([feature_dict])[FEATURE_NAMES]
    return df, population_density


def predict_flood(raw_input):
    """
    Executes end-to-end flood prediction:
    1. Feature extraction & engineering (13 features)
    2. StandardScaler transformation
    3. SVM inference
    4. Risk classification & impact estimation via risk_classifier.py

    Args:
        raw_input (dict): Input parameters.

    Returns:
        dict: Standardized flood prediction and impact assessment.
    """
    model, scaler, _ = load_ml_assets()

    # Construct 13 features
    features_df, pop_density = construct_features(raw_input)

    # Scale inputs using fitted scaler
    features_scaled = scaler.transform(features_df)

    # Model inference
    prediction = int(model.predict(features_scaled)[0])
    probabilities = model.predict_proba(features_scaled)[0]
    probability_pct = round(float(probabilities[1]) * 100.0, 2)

    # Use existing risk_classifier module for classification & impact
    if risk_classifier:
        assessment = risk_classifier.full_assessment(probability_pct, population_density=pop_density)
        risk_info = assessment.get("risk", {})
        impact_info = assessment.get("impact", {})
    else:
        # Fallback in case risk_classifier is unreachable
        if probability_pct >= 75:
            level, color, action = "CRITICAL", "#e74c3c", "Immediate evacuation required. Activate OSDMA emergency protocol."
        elif probability_pct >= 50:
            level, color, action = "HIGH", "#e67e22", "Prepare emergency resources. Alert residents in low-lying areas."
        elif probability_pct >= 25:
            level, color, action = "MODERATE", "#f1c40f", "Monitor water levels. Keep drainage channels clear."
        else:
            level, color, action = "LOW", "#2ecc71", "Normal operations. Continue routine monitoring."

        risk_info = {"level": level, "color": color, "action": action}
        impact_info = {
            "risk_level": level,
            "affected_area_km2": 5.0 if level == "CRITICAL" else 3.0 if level == "HIGH" else 1.5 if level == "MODERATE" else 0.5,
            "estimated_affected": 25000 if level == "CRITICAL" else 12500 if level == "HIGH" else 3000 if level == "MODERATE" else 500,
            "infrastructure": "Disaster protocol active" if level in ("CRITICAL", "HIGH") else "Normal",
            "resources_needed": ["NDRF", "Boats", "Medical"] if level == "CRITICAL" else ["Routine"],
        }

    return {
        "flood": prediction,
        "probability": probability_pct,
        "risk": risk_info.get("level", "LOW"),
        "risk_details": risk_info,
        "impact": impact_info,
        "features_used": {
            "rainfall": float(features_df["rainfall"].iloc[0]),
            "water_level": float(features_df["water_level"].iloc[0]),
            "elevation": int(features_df["elevation"].iloc[0]),
            "drainage": int(features_df["drainage"].iloc[0]),
            "population_density": int(features_df["population_density"].iloc[0]),
            "distance_to_river": float(features_df["distance_to_river"].iloc[0]),
        },
    }
