"""
What-If Scenario Simulation Service.
Simulates disaster progression when rainfall increases, drainage conditions degrade,
or water levels surge. Feeds simulated conditions through the ML model and Decision Support engine.
"""

from services.ml_service import predict_flood
from services.decision_service import generate_full_decision_support
from config import (
    DEFAULT_ELEVATION,
    DEFAULT_DRAINAGE,
    DEFAULT_HUMIDITY,
    DEFAULT_SOIL_TYPE,
    DEFAULT_POPULATION_DENSITY,
    DEFAULT_DISTANCE_TO_RIVER,
    KIIT_COORDINATES,
)


def run_simulation(scenario_input):
    """
    Executes a What-If disaster scenario.

    Args:
        scenario_input (dict):
            - base_rainfall (float): Baseline rainfall in mm (default: 80.0)
            - rainfall_increase_percent (float): Slider percentage increase 0-50% (default: 0.0)
            - drainage_quality (int): 1=Poor, 2=Moderate, 3=Good (default: 1)
            - water_level_override (float, optional): Custom water level in meters

    Returns:
        dict: Complete simulation assessment including baseline vs simulated delta,
              multi-zone risk progression, and emergency recommendations.
    """
    base_rainfall = float(scenario_input.get("base_rainfall", 80.0))
    rain_increase_pct = float(scenario_input.get("rainfall_increase_percent", 0.0))
    drainage = int(scenario_input.get("drainage_quality", DEFAULT_DRAINAGE))
    elevation = int(scenario_input.get("elevation", DEFAULT_ELEVATION))
    pop_density = int(scenario_input.get("population_density", DEFAULT_POPULATION_DENSITY))

    # Calculate new simulated rainfall
    simulated_rainfall = round(base_rainfall * (1.0 + rain_increase_pct / 100.0), 2)

    # Estimate correlated water level rise if not explicitly provided
    if scenario_input.get("water_level_override") is not None:
        simulated_water_level = float(scenario_input["water_level_override"])
    else:
        base_water_level = 1.8
        simulated_water_level = round(base_water_level * (1.0 + (rain_increase_pct * 1.15) / 100.0), 2)

    # 1. Evaluate baseline scenario
    baseline_ml = predict_flood({
        "rainfall": base_rainfall,
        "water_level": 1.8,
        "elevation": elevation,
        "drainage": drainage,
        "population_density": pop_density,
    })

    # 2. Evaluate simulated scenario with AI model
    simulated_ml = predict_flood({
        "rainfall": simulated_rainfall,
        "water_level": simulated_water_level,
        "elevation": elevation,
        "drainage": drainage,
        "population_density": pop_density,
    })

    # 3. Multi-Zone Risk Progression Simulation (for the 4 KIIT Geographic Zones)
    # Zone 1: KIIT Campus (Higher ground, good drainage)
    z1 = predict_flood({"rainfall": simulated_rainfall, "water_level": max(0.5, simulated_water_level * 0.6), "elevation": 3, "drainage": 3, "distance_to_river": 6.7})
    # Zone 2: Patia-Chandrasekharpur (Moderate ground)
    z2 = predict_flood({"rainfall": simulated_rainfall, "water_level": simulated_water_level * 0.85, "elevation": 2, "drainage": 2, "distance_to_river": 5.0})
    # Zone 3: Patia Low-Lying Residential (Low elevation, poor drainage)
    z3 = predict_flood({"rainfall": simulated_rainfall, "water_level": simulated_water_level * 1.1, "elevation": 1, "drainage": 1, "distance_to_river": 3.2})
    # Zone 4: Kuakhai River Basin (Critical flood plain)
    z4 = predict_flood({"rainfall": simulated_rainfall, "water_level": simulated_water_level * 1.35, "elevation": 1, "drainage": 1, "distance_to_river": 0.5})

    zone_progression = [
        {"zone_id": "ZONE_01", "name": "KIIT University Campus (Elevated)", "risk": z1["risk"], "probability": z1["probability"]},
        {"zone_id": "ZONE_02", "name": "Patia-Chandrasekharpur Urban Ward", "risk": z2["risk"], "probability": z2["probability"]},
        {"zone_id": "ZONE_03", "name": "Patia Low-Lying Canal Area", "risk": z3["risk"], "probability": z3["probability"]},
        {"zone_id": "ZONE_04", "name": "Kuakhai River Flood Plain", "risk": z4["risk"], "probability": z4["probability"]},
    ]

    # 4. Generate Emergency Decision Support for simulated state
    decision_support = generate_full_decision_support(
        user_lat=KIIT_COORDINATES["lat"],
        user_lng=KIIT_COORDINATES["lng"],
        risk_level=simulated_ml["risk"],
        probability=simulated_ml["probability"],
        elevation=elevation,
        population_density=pop_density,
    )

    # 5. Compute deltas
    prob_delta = round(simulated_ml["probability"] - baseline_ml["probability"], 2)
    pop_delta = decision_support["assessment"]["estimated_affected_population"] - baseline_ml["impact"].get("estimated_affected", 3000)

    return {
        "status": "success",
        "scenario_parameters": {
            "base_rainfall_mm": base_rainfall,
            "rainfall_increase_percent": rain_increase_pct,
            "simulated_rainfall_mm": simulated_rainfall,
            "simulated_water_level_m": simulated_water_level,
            "drainage_quality": drainage,
        },
        "baseline_state": {
            "probability": baseline_ml["probability"],
            "risk_level": baseline_ml["risk"],
        },
        "simulated_state": {
            "flood_predicted": simulated_ml["flood"],
            "probability": simulated_ml["probability"],
            "risk_level": simulated_ml["risk"],
            "risk_color": simulated_ml["risk_details"].get("color", "#f1c40f"),
            "action": simulated_ml["risk_details"].get("action", ""),
            "affected_population": decision_support["assessment"]["estimated_affected_population"],
            "affected_area_km2": decision_support["assessment"]["estimated_affected_area_km2"],
        },
        "delta": {
            "probability_change_pct": f"{'+' if prob_delta >= 0 else ''}{prob_delta}%",
            "additional_affected_population": max(0, pop_delta),
        },
        "zone_breakdown": zone_progression,
        "emergency_decision_support": decision_support,
        "is_simulated": True,
        "disclaimer": "What-If simulation model for disaster preparedness. All scenario projections are simulated.",
    }
