"""
Data service for accessing sensor telemetry and historical weather datasets.
Reads existing CSV files in DATA/ without modifying them.
"""

import os
import pandas as pd
from config import SENSOR_DATA_PATH, WEATHER_DATA_PATH


def get_latest_sensor_data():
    """
    Retrieve the most recent water level sensor readings per sensor location.
    Returns:
        dict: Sensor telemetry, latest timestamp, and status.
    """
    if not os.path.exists(SENSOR_DATA_PATH):
        return {
            "status": "error",
            "message": "Sensor data file not found",
            "sensors": [],
            "average_water_level_m": 0.0,
        }

    try:
        df = pd.read_csv(SENSOR_DATA_PATH)
        if df.empty:
            return {
                "status": "warning",
                "message": "Sensor dataset is empty",
                "sensors": [],
                "average_water_level_m": 0.0,
            }

        # Sort by timestamp descending
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df_sorted = df.sort_values(by="Timestamp", ascending=False)

        # Get latest reading for each unique Sensor_ID
        latest_per_sensor = df_sorted.drop_duplicates(subset=["Sensor_ID"]).to_dict(orient="records")

        # Format output
        sensor_list = []
        total_level_cm = 0.0

        for record in latest_per_sensor:
            level_cm = float(record.get("Water_Level_cm", 0.0))
            total_level_cm += level_cm

            # Determine alert status
            if level_cm >= 30:
                status = "CRITICAL"
            elif level_cm >= 15:
                status = "WARNING"
            elif level_cm >= 5:
                status = "ELEVATED"
            else:
                status = "NORMAL"

            sensor_list.append({
                "sensor_id": record.get("Sensor_ID"),
                "location": record.get("Location"),
                "timestamp": str(record.get("Timestamp")),
                "water_level_cm": level_cm,
                "temperature_c": float(record.get("Temperature_C", 28.0)),
                "status": status,
            })

        avg_water_level_m = round((total_level_cm / max(len(sensor_list), 1)) / 100.0, 3)

        return {
            "status": "success",
            "count": len(sensor_list),
            "latest_timestamp": sensor_list[0]["timestamp"] if sensor_list else None,
            "average_water_level_m": avg_water_level_m,
            "sensors": sensor_list,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading sensor data: {str(e)}",
            "sensors": [],
            "average_water_level_m": 0.0,
        }


def get_weather_history(limit=30):
    """
    Retrieve historical weather data preview from NASA POWER dataset.
    """
    if not os.path.exists(WEATHER_DATA_PATH):
        return {
            "status": "error",
            "message": "Weather dataset not found",
            "records": [],
        }

    try:
        df = pd.read_csv(WEATHER_DATA_PATH)
        # Take the most recent rows
        recent_df = df.tail(limit)

        records = []
        for _, row in recent_df.iterrows():
            date_str = f"{int(row['YEAR'])}-{int(row['MO']):02d}-{int(row['DY']):02d}"
            records.append({
                "date": date_str,
                "precipitation_mm": float(row.get("PRECTOTCORR", 0.0)),
                "temperature_c": float(row.get("T2M", 25.0)),
                "wind_speed_ms": float(row.get("WS10M", 2.0)),
            })

        return {
            "status": "success",
            "total_rows": len(df),
            "returned_rows": len(records),
            "records": records,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading weather data: {str(e)}",
            "records": [],
        }
