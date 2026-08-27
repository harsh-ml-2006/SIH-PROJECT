# Disaster Management Digital Twin

**AI-Powered Flood Risk Prediction & Emergency Decision Support System**

Built for **KIIT University, Bhubaneswar, Odisha** -- a flood-prone region near the Kuakhai River.

---

## What Is This?

A **Digital Twin** is a virtual copy of a real-world area that is continuously updated with real data.

This system combines **AI/ML flood prediction**, **GIS mapping**, and **risk simulation** to help authorities:

- Predict flood probability based on rainfall, water level, elevation, drainage, and more
- Visualize risk zones on an interactive map
- Simulate "What-If" scenarios (e.g., "What if rainfall increases by 30%?")
- Estimate affected population and recommend emergency actions

---

## Project Structure

```
SIH-PROJECT/
|
|-- BACKEND/
|   |-- app.py                  # Flask API server
|
|-- DATA/
|   |-- flood_data.csv          # Training dataset (1500 rows, 10 features)
|
|-- FRONTED/
|   |-- index.html              # Dashboard UI
|   |-- style.css               # Dark theme CSS
|   |-- app.js                  # Map + simulation logic
|
|-- ML/
|   |-- train_model.py          # Full ML pipeline (7 models, tuning, charts)
|   |-- generate_dataset.py     # KIIT-specific synthetic dataset generator
|   |-- risk_classifier.py      # Risk classification + impact estimation
|   |-- flood_model.pkl         # Trained model (best: SVM)
|   |-- scaler.pkl              # StandardScaler for input normalization
|   |-- model_metadata.json     # Model info, metrics, features list
|   |-- reports/
|       |-- model_comparison.png    # 7-model F1 score comparison
|       |-- confusion_matrix.png    # Confusion matrix heatmap
|       |-- roc_curve.png           # ROC curve (AUC = 0.96)
|
|-- requirements.txt
|-- .gitignore
|-- idea.docx                   # Full project concept document
```

---

## ML Pipeline

### Dataset
- **1500 rows**, **10 features** -- KIIT/Bhubaneswar specific
- Features: `rainfall`, `water_level`, `elevation`, `drainage`, `humidity`, `soil_type`, `population_density`, `distance_to_river`, `historical_flood_freq`, `drainage_capacity`
- 3 engineered features: `rainfall_water_index`, `flood_risk_index`, `proximity_risk`

### Models Compared (5-Fold Cross Validation)

| Model               | F1 Score |
|---------------------|----------|
| SVM                 | 0.8995   |
| Logistic Regression | 0.8961   |
| Gradient Boosting   | 0.8886   |
| Random Forest       | 0.8882   |
| XGBoost             | 0.8745   |
| Neural Network      | 0.8719   |
| KNN                 | 0.8703   |

### Best Model: SVM (after Hyperparameter Tuning)

| Metric    | Score  |
|-----------|--------|
| Accuracy  | 88.3%  |
| Precision | 88.8%  |
| Recall    | 87.0%  |
| F1-Score  | 87.9%  |
| ROC-AUC   | 95.98% |

### Risk Classification

| Probability | Risk Level | Action                                      |
|-------------|------------|---------------------------------------------|
| 75%+        | CRITICAL   | Immediate evacuation, activate OSDMA        |
| 50-74%      | HIGH       | Prepare emergency resources, alert residents |
| 25-49%      | MODERATE   | Monitor water levels, clear drainage         |
| 0-24%       | LOW        | Normal operations, routine monitoring        |

---

## How to Run

### 1. Clone the repo

```bash
git clone https://github.com/harsh-ml-2006/SIH-PROJECT.git
cd SIH-PROJECT
```

### 2. Create virtual environment and install packages

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

### 3. Train the ML model

```bash
cd ML
python train_model.py
```

This will:
- Compare 7 models
- Tune top 3 via RandomizedSearchCV
- Save best model, scaler, metadata, and charts

### 4. Start the backend server

```bash
cd BACKEND
python app.py
```

Server runs at `http://127.0.0.1:5000`

### 5. Open the frontend

Open `FRONTED/index.html` in your browser.

---

## API Endpoints

| Method | Endpoint   | Description              |
|--------|------------|--------------------------|
| GET    | `/`        | Health check             |
| POST   | `/predict` | Flood prediction         |

### POST /predict -- Example

**Request:**
```json
{
    "rainfall": 200,
    "water_level": 4.5,
    "elevation": 1,
    "drainage": 1
}
```

**Response:**
```json
{
    "flood": 1,
    "probability": 95.5,
    "risk": "CRITICAL"
}
```

---

## Tech Stack

| Layer      | Technologies                                        |
|------------|-----------------------------------------------------|
| ML/AI      | Python, Scikit-learn, XGBoost, Pandas, NumPy         |
| Backend    | Flask, Flask-CORS, Joblib                            |
| Frontend   | HTML, CSS, JavaScript                                |
| Mapping    | Leaflet.js, OpenStreetMap                            |
| Charts     | Matplotlib, Seaborn                                  |

---

## Team

| Member   | Role                     |
|----------|--------------------------|
| Member 1 | Frontend + UI            |
| Member 2 | Map + GIS                |
| Member 3 | ML/AI                    |
| Member 4 | Backend                  |
| Member 5 | Data + Simulation        |
| Member 6 | Emergency Decision Support|

---

## License

This project is built for **Smart India Hackathon (SIH)** and is for educational/demonstration purposes.