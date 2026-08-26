from flask import Flask, request, jsonify
from flask_cors import CORS

import joblib
import pandas as pd


# ==========================================
# CREATE FLASK APP
# ==========================================

app = Flask(__name__)

CORS(app)


# ==========================================
# LOAD ML MODEL
# ==========================================

model = joblib.load(
    "../ml/flood_model.pkl"
)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return {
        "message": "Disaster Digital Twin API is running"
    }


# ==========================================
# FLOOD PREDICTION API
# ==========================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    data = request.get_json()


    rainfall = float(
        data["rainfall"]
    )

    water_level = float(
        data["water_level"]
    )

    elevation = int(
        data["elevation"]
    )

    drainage = int(
        data["drainage"]
    )


    # ======================================
    # CREATE INPUT DATAFRAME
    # ======================================

    input_data = pd.DataFrame(
        [
            {
                "rainfall": rainfall,
                "water_level": water_level,
                "elevation": elevation,
                "drainage": drainage
            }
        ]
    )


    # ======================================
    # PREDICTION
    # ======================================

    prediction = model.predict(
        input_data
    )[0]


    probability = model.predict_proba(
        input_data
    )[0][1]


    probability = probability * 100


    # ======================================
    # RISK LEVEL
    # ======================================

    if probability >= 75:

        risk = "CRITICAL"

    elif probability >= 50:

        risk = "HIGH"

    elif probability >= 25:

        risk = "MODERATE"

    else:

        risk = "LOW"


    # ======================================
    # RESPONSE
    # ======================================

    return jsonify(
        {
            "flood": int(prediction),

            "probability": round(
                probability,
                2
            ),

            "risk": risk
        }
    )


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )