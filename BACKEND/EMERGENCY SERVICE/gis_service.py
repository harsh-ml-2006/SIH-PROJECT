"""
GIS Service for Disaster Management Digital Twin.
Loads existing GeoJSON risk zones and locations, and overlays simulated road network
and auxiliary shelters with explicit simulation labeling.
"""

import os
import json
import re

from config import (
    RISK_ZONES_GEOJSON_PATH,
    GIS_LOCATIONS_JS_PATH,
    SIMULATED_ROADS_PATH,
    SIMULATED_SHELTERS_PATH,
    SIMULATED_HOSPITALS_PATH,
)


def load_risk_zones():
    """
    Loads original risk zones GeoJSON.
    """
    if os.path.exists(RISK_ZONES_GEOJSON_PATH):
        with open(RISK_ZONES_GEOJSON_PATH, "r") as f:
            return json.load(f)
    return {"type": "FeatureCollection", "features": []}


def load_gis_locations():
    """
    Reads existing locations.js file and parses the object.
    """
    if not os.path.exists(GIS_LOCATIONS_JS_PATH):
        return []

    try:
        with open(GIS_LOCATIONS_JS_PATH, "r") as f:
            content = f.read()

        # Extract JS object using regex or manual matching
        locations = []
        pattern = r'(\w+):\s*\{([^}]+)\}'
        matches = re.findall(pattern, content)

        for key, body in matches:
            loc = {"key": key}
            for line in body.strip().split("\n"):
                line = line.strip().rstrip(",")
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k in ("lat", "lng"):
                        try:
                            loc[k] = float(v)
                        except ValueError:
                            loc[k] = 0.0
                    else:
                        loc[k] = v
            if "lat" in loc and "lng" in loc:
                locations.append(loc)

        return locations
    except Exception:
        # Fallback if parsing fails
        return [
            {"name": "KIMS Hospital", "type": "Hospital", "lat": 20.3568, "lng": 85.8150, "description": "Emergency medical support"},
            {"name": "Emergency Shelter", "type": "Shelter", "lat": 20.3350, "lng": 85.8250, "description": "Evacuation shelter"},
            {"name": "OSDMA", "type": "Disaster Management", "lat": 20.2726, "lng": 85.8390, "description": "Disaster control HQ"},
            {"name": "Kuakhai River", "type": "River", "lat": 20.2870, "lng": 85.8750, "description": "River / flood-prone belt"},
        ]


def load_simulated_roads(risk_level="LOW", water_level_cm=0):
    """
    Loads simulated road network and dynamically updates road passability
    based on the current disaster risk level and sensor water levels.
    """
    if not os.path.exists(SIMULATED_ROADS_PATH):
        return {"type": "FeatureCollection", "features": []}

    with open(SIMULATED_ROADS_PATH, "r") as f:
        road_data = json.load(f)

    # Dynamic status update based on risk state
    for feature in road_data.get("features", []):
        props = feature.get("properties", {})
        road_id = props.get("id")

        if risk_level == "CRITICAL":
            if road_id in ("ROAD_02", "ROAD_04"):
                props["current_status"] = "BLOCKED"
                props["inundation_depth_cm"] = 45
                props["passable_for_evacuation"] = False
            elif road_id == "ROAD_01":
                props["current_status"] = "VULNERABLE"
                props["inundation_depth_cm"] = 20
                props["passable_for_evacuation"] = True
            else:
                props["current_status"] = "CLEAR"
                props["inundation_depth_cm"] = 0
                props["passable_for_evacuation"] = True
        elif risk_level == "HIGH":
            if road_id == "ROAD_04":
                props["current_status"] = "BLOCKED"
                props["inundation_depth_cm"] = 30
                props["passable_for_evacuation"] = False
            elif road_id == "ROAD_02":
                props["current_status"] = "VULNERABLE"
                props["inundation_depth_cm"] = 18
                props["passable_for_evacuation"] = True
            else:
                props["current_status"] = "CLEAR"
                props["inundation_depth_cm"] = 0
                props["passable_for_evacuation"] = True
        else:
            props["current_status"] = "CLEAR"
            props["inundation_depth_cm"] = 0
            props["passable_for_evacuation"] = True

    return road_data


def load_shelters():
    """
    Loads simulated emergency shelters.
    """
    if os.path.exists(SIMULATED_SHELTERS_PATH):
        with open(SIMULATED_SHELTERS_PATH, "r") as f:
            return json.load(f)
    return {"shelters": []}


def load_hospitals():
    """
    Loads simulated emergency hospitals.
    """
    if os.path.exists(SIMULATED_HOSPITALS_PATH):
        with open(SIMULATED_HOSPITALS_PATH, "r") as f:
            return json.load(f)
    return {"hospitals": []}


def get_all_gis_data(risk_level="LOW", water_level_cm=0):
    """
    Returns aggregated GIS payload for frontend and decision support systems.
    """
    return {
        "status": "success",
        "risk_zones": load_risk_zones(),
        "primary_locations": load_gis_locations(),
        "simulated_roads": load_simulated_roads(risk_level, water_level_cm),
        "shelters": load_shelters(),
        "hospitals": load_hospitals(),
        "simulation_disclaimer": "Auxiliary road vectors, expanded shelter, and hospital metrics are simulated for demonstration & decision planning.",
    }
