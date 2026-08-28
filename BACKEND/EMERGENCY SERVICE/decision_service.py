"""
Emergency Decision Support Service (Member 6 Responsibility).
Computes dynamic affected population, multi-criteria evacuation priority ranking,
Haversine nearest shelter/hospital matching, road inundation routing checks,
emergency resource allocation, and Common Alerting Protocol (CAP) alerts.

All synthetic decision assets and telemetry are explicitly flagged as simulated.
"""

import math
from datetime import datetime
from services.gis_service import load_shelters, load_hospitals, load_simulated_roads
from config import KIIT_COORDINATES


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's radius in km

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def find_nearest_shelter(user_lat, user_lng):
    """
    Finds the closest emergency shelter with available capacity.
    """
    shelter_data = load_shelters()
    shelters = shelter_data.get("shelters", [])

    if not shelters:
        return {
            "name": "KIIT Indoor Stadium Cyclone Shelter (Default)",
            "lat": 20.3520,
            "lng": 85.8180,
            "distance_km": 0.5,
            "capacity": 3000,
            "remaining_capacity": 2580,
            "status": "OPEN",
            "is_simulated": True,
        }

    scored_shelters = []
    for s in shelters:
        dist = haversine_distance(user_lat, user_lng, s["lat"], s["lng"])
        rem_cap = max(0, s["capacity"] - s["current_occupancy"])
        scored_shelters.append({
            "id": s["id"],
            "name": s["name"],
            "type": s.get("type", "Emergency Shelter"),
            "lat": s["lat"],
            "lng": s["lng"],
            "distance_km": dist,
            "total_capacity": s["capacity"],
            "current_occupancy": s["current_occupancy"],
            "remaining_capacity": rem_cap,
            "facilities": s.get("facilities", []),
            "contact": s.get("contact", "+91-674-2725113"),
            "status": s.get("status", "OPEN"),
            "is_simulated": True,
        })

    # Sort by distance
    scored_shelters.sort(key=lambda x: x["distance_km"])
    return scored_shelters[0] if scored_shelters else None, scored_shelters


def find_nearest_hospital(user_lat, user_lng):
    """
    Finds the closest hospital with available emergency beds and trauma unit.
    """
    hosp_data = load_hospitals()
    hospitals = hosp_data.get("hospitals", [])

    if not hospitals:
        return {
            "name": "KIMS Hospital",
            "lat": 20.3568,
            "lng": 85.8150,
            "distance_km": 0.6,
            "available_emergency_beds": 145,
            "icu_beds_available": 32,
            "trauma_center": True,
            "helpline": "+91-674-2725472",
            "status": "OPERATIONAL",
            "is_simulated": True,
        }

    scored_hospitals = []
    for h in hospitals:
        dist = haversine_distance(user_lat, user_lng, h["lat"], h["lng"])
        scored_hospitals.append({
            "id": h["id"],
            "name": h["name"],
            "type": h.get("type", "Hospital"),
            "lat": h["lat"],
            "lng": h["lng"],
            "distance_km": dist,
            "total_beds": h["total_beds"],
            "available_emergency_beds": h["available_emergency_beds"],
            "icu_beds_available": h["icu_beds_available"],
            "trauma_center": h.get("trauma_center", True),
            "blood_bank": h.get("blood_bank", True),
            "ambulance_count": h.get("ambulance_count", 5),
            "helpline": h.get("helpline", "+91-674-2725472"),
            "status": h.get("status", "OPERATIONAL"),
            "is_simulated": True,
        })

    scored_hospitals.sort(key=lambda x: x["distance_km"])
    return scored_hospitals[0] if scored_hospitals else None, scored_hospitals


def calculate_evacuation_priority(probability, risk_level, elevation=1, population_density=2):
    """
    Calculates evacuation urgency rank based on probability, elevation, and density.
    Priority Score = (Probability * Density) / Elevation
    """
    priority_score = round((probability * population_density) / max(elevation, 1), 2)

    if risk_level == "CRITICAL" or probability >= 75:
        rank = 1
        urgency = "IMMEDIATE"
        action_directive = "Mandatory Evacuation -- Deploy NDRF teams, activate all emergency shelters."
        timeframe = "Within 1-2 Hours"
    elif risk_level == "HIGH" or probability >= 50:
        rank = 2
        urgency = "HIGH"
        action_directive = "High-Alert Evacuation -- Move vulnerable residents, elderly, and children to shelters."
        timeframe = "Within 4 Hours"
    elif risk_level == "MODERATE" or probability >= 25:
        rank = 3
        urgency = "ADVISORY"
        action_directive = "Advisory Alert -- Clear ground-floor assets, prepare emergency go-bags."
        timeframe = "Within 12 Hours"
    else:
        rank = 4
        urgency = "ROUTINE"
        action_directive = "Normal Operations -- Routine monitoring of municipal drainage channels."
        timeframe = "Standby"

    return {
        "priority_rank": rank,
        "urgency_level": urgency,
        "priority_score": priority_score,
        "action_directive": action_directive,
        "target_timeframe": timeframe,
        "is_simulated": True,
    }


def evaluate_emergency_routes(user_lat, user_lng, risk_level):
    """
    Evaluates passable vs blocked roads and provides a safe waypoint path
    to the nearest shelter/hospital.
    """
    road_data = load_simulated_roads(risk_level)
    features = road_data.get("features", [])

    blocked_roads = []
    clear_roads = []

    for f in features:
        props = f.get("properties", {})
        if props.get("current_status") == "BLOCKED":
            blocked_roads.append({
                "road_id": props.get("id"),
                "name": props.get("name"),
                "inundation_depth_cm": props.get("inundation_depth_cm", 35),
                "reason": "Waterlogged / Inundated above safe vehicular clearance",
                "coordinates": f.get("geometry", {}).get("coordinates", []),
            })
        else:
            clear_roads.append({
                "road_id": props.get("id"),
                "name": props.get("name"),
                "status": props.get("current_status"),
                "coordinates": f.get("geometry", {}).get("coordinates", []),
            })

    # Recommended safe evacuation waypoints avoiding low-lying canal roads
    safe_corridor = [
        [user_lat, user_lng],
        [20.3545, 85.8210],  # Patia High Ground Point
        [20.3560, 85.8175],  # KIIT Campus 5 Elevated Corridor
        [20.3568, 85.8150],  # KIMS Hospital / Primary Shelter Hub
    ]

    return {
        "blocked_roads_count": len(blocked_roads),
        "blocked_roads": blocked_roads,
        "clear_roads": clear_roads,
        "safe_evacuation_corridor": safe_corridor,
        "is_simulated": True,
        "routing_disclaimer": "Simulated evacuation corridor based on elevated terrain waypoints.",
    }


def optimize_resource_allocation(risk_level, probability, affected_population):
    """
    Computes emergency resource dispatch orders based on risk severity.
    """
    if risk_level == "CRITICAL":
        boats = max(6, int(affected_population / 4000))
        ndrf_teams = max(4, int(affected_population / 6000))
        ambulances = 12
        pumps = 8
        food_kits = affected_population
    elif risk_level == "HIGH":
        boats = 2
        ndrf_teams = 2
        ambulances = 6
        pumps = 4
        food_kits = int(affected_population * 0.8)
    elif risk_level == "MODERATE":
        boats = 0
        ndrf_teams = 1
        ambulances = 2
        pumps = 2
        food_kits = 1000
    else:
        boats = 0
        ndrf_teams = 0
        ambulances = 1
        pumps = 1
        food_kits = 0

    dispatches = [
        {
            "resource_type": "NDRF Disaster Response Team",
            "quantity": ndrf_teams,
            "unit": "Platoons (30 personnel each)",
            "staging_area": "OSDMA Regional Hub / KIIT Campus 6",
            "status": "DISPATCHED" if ndrf_teams > 0 else "STANDBY",
        },
        {
            "resource_type": "Inflatable Motorized Rescue Boats",
            "quantity": boats,
            "unit": "Boats",
            "staging_area": "Kuakhai Embankment & Patia Canal Post",
            "status": "DEPLOYED" if boats > 0 else "STANDBY",
        },
        {
            "resource_type": "Advanced Life Support Ambulances",
            "quantity": ambulances,
            "unit": "Vehicles",
            "staging_area": "KIMS Hospital Triage Center",
            "status": "ACTIVE",
        },
        {
            "resource_type": "High-Discharge De-Watering Pumps (1000 m3/hr)",
            "quantity": pumps,
            "unit": "Pumping Units",
            "staging_area": "Patia Low-Lying Drainage Outfalls",
            "status": "OPERATIONAL",
        },
        {
            "resource_type": "Emergency Relief Kits (Food & Clean Water)",
            "quantity": food_kits,
            "unit": "Family Ration Packs",
            "staging_area": "KIIT Indoor Stadium Cyclone Shelter",
            "status": "STOCKED" if food_kits > 0 else "STANDBY",
        },
    ]

    return {
        "risk_level": risk_level,
        "dispatches": dispatches,
        "is_simulated": True,
    }


def generate_cap_alert(risk_level, probability, nearest_shelter_name):
    """
    Generates a Common Alerting Protocol (CAP) compliant emergency alert.
    """
    now_iso = datetime.now().isoformat()

    if risk_level == "CRITICAL":
        severity = "Extreme"
        urgency = "Immediate"
        headline = "CRITICAL FLOOD WARNING: KIIT & PATIA DRAINAGE BASIN"
        instruction = f"Immediate evacuation required for low-lying areas. Move via elevated Infocity corridor to {nearest_shelter_name}. Avoid Kuakhai embankment road."
    elif risk_level == "HIGH":
        severity = "Severe"
        urgency = "Expected"
        headline = "HIGH FLOOD RISK ADVISORY: NORTH BHUBANESWAR"
        instruction = f"Prepare emergency evacuation kits. Residents in ground floors advised to relocate to {nearest_shelter_name}."
    elif risk_level == "MODERATE":
        severity = "Moderate"
        urgency = "Future"
        headline = "FLOOD WATCH & MONITORING ALERT: PATIA BASIN"
        instruction = "Water levels rising. Keep local drainage gratings clear and monitor official alerts."
    else:
        severity = "Minor"
        urgency = "Past"
        headline = "ROUTINE WEATHER & FLOOD STATUS: NORMAL"
        instruction = "Standard municipal monitoring. No immediate evacuation necessary."

    return {
        "identifier": f"CAP-ODISHA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "sender": "KIIT Disaster Twin / OSDMA Emergency Decision Cell",
        "sent": now_iso,
        "status": "Simulated Exercise",
        "msgType": "Alert",
        "scope": "Public",
        "info": {
            "category": "Met / Geo / Safety",
            "event": "Urban Flash Flood Warning",
            "urgency": urgency,
            "severity": severity,
            "certainty": "Observed / High Probability",
            "headline": headline,
            "description": f"AI Digital Twin predicted flood probability of {probability}% in KIIT & surrounding zones.",
            "instruction": instruction,
            "contact": "Toll-Free Emergency Helpline: 1070 / +91-674-2725472",
        },
        "is_simulated": True,
    }


def generate_full_decision_support(user_lat=None, user_lng=None, risk_level="LOW", probability=0.0, elevation=1, population_density=2):
    """
    Produces complete Emergency Decision Support package combining all Member 6 features.
    """
    lat = float(user_lat) if user_lat is not None else KIIT_COORDINATES["lat"]
    lng = float(user_lng) if user_lng is not None else KIIT_COORDINATES["lng"]

    # 1. Shelter & Hospital Matching
    primary_shelter, all_shelters = find_nearest_shelter(lat, lng)
    primary_hospital, all_hospitals = find_nearest_hospital(lat, lng)

    # 2. Priority Ranking
    priority_info = calculate_evacuation_priority(probability, risk_level, elevation, population_density)

    # 3. Dynamic Affected Population (from ML baseline density rules)
    area_km2 = 5.0 if risk_level == "CRITICAL" else 3.0 if risk_level == "HIGH" else 1.5 if risk_level == "MODERATE" else 0.5
    density_per_km2 = 5000 if population_density == 3 else 2000 if population_density == 2 else 500
    affected_pop = int(area_km2 * density_per_km2)

    # 4. Road Inundation & Safe Routing
    routes_info = evaluate_emergency_routes(lat, lng, risk_level)

    # 5. Emergency Resource Allocation
    resource_info = optimize_resource_allocation(risk_level, probability, affected_pop)

    # 6. CAP Alert
    cap_alert = generate_cap_alert(risk_level, probability, primary_shelter.get("name", "KIIT Shelter"))

    return {
        "status": "success",
        "location": {"lat": lat, "lng": lng, "area": "KIIT University / Patia, Bhubaneswar"},
        "assessment": {
            "risk_level": risk_level,
            "probability": round(probability, 2),
            "estimated_affected_population": affected_pop,
            "estimated_affected_area_km2": area_km2,
        },
        "evacuation_priority": priority_info,
        "nearest_shelter": primary_shelter,
        "all_shelters": all_shelters,
        "nearest_hospital": primary_hospital,
        "all_hospitals": all_hospitals,
        "road_conditions": routes_info,
        "resource_allocation": resource_info,
        "emergency_alert": cap_alert,
        "is_simulated": True,
        "disclaimer": "Emergency Decision Support outputs, shelter occupancies, hospital beds, and road statuses are simulated for demonstration purposes.",
    }
