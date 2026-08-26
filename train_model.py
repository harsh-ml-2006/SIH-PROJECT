import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# ==========================================
# LOAD DATA
# ==========================================

data = pd.read_csv("../data/flood_data.csv")


# ==========================================
# INPUT FEATURES
# ==========================================

X = data[
    [
        "rainfall",
        "water_level",
        "elevation",
        "drainage"
    ]
]


# ==========================================
# TARGET
# ==========================================

y = data["flood"]


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==========================================
# RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


# ==========================================
# TRAIN
# ==========================================

model.fit(X_train, y_train)


# ==========================================
# TEST MODEL
# ==========================================

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("--------------------------------")
print("Flood Prediction Model")
print("--------------------------------")

print(
    f"Model Accuracy: {accuracy * 100:.2f}%"
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    "flood_model.pkl"
)


print("Model saved successfully!")