# risk_classifier.py
# -------------------------------------------------------
# Risk Classification and Impact Estimation Module
# KIIT University, Bhubaneswar, Odisha
# -------------------------------------------------------


# Risk thresholds (probability in %)
RISK_THRESHOLDS = {
    'CRITICAL' : 75,
    'HIGH'     : 50,
    'MODERATE' : 25,
    'LOW'      : 0,
}

# Population per sq km per density category (Bhubaneswar)
POPULATION_PER_KM2 = {
    1: 500,
    2: 2000,
    3: 5000,
}

# Approx affected area per risk level (km2)
AFFECTED_AREA_KM2 = {
    'CRITICAL' : 5.0,
    'HIGH'     : 3.0,
    'MODERATE' : 1.5,
    'LOW'      : 0.5,
}


def classify_risk(probability):
    """
    Classify flood risk based on predicted probability.

    Args:
        probability (float): Flood probability 0-100

    Returns:
        dict: risk level, color, action, css_class
    """
    if probability >= RISK_THRESHOLDS['CRITICAL']:
        return {
            'level'     : 'CRITICAL',
            'color'     : '#e74c3c',
            'css_class' : 'critical',
            'action'    : 'Immediate evacuation required. Activate OSDMA emergency protocol.',
        }
    elif probability >= RISK_THRESHOLDS['HIGH']:
        return {
            'level'     : 'HIGH',
            'color'     : '#e67e22',
            'css_class' : 'high',
            'action'    : 'Prepare emergency resources. Alert residents in low-lying areas.',
        }
    elif probability >= RISK_THRESHOLDS['MODERATE']:
        return {
            'level'     : 'MODERATE',
            'color'     : '#f1c40f',
            'css_class' : 'moderate',
            'action'    : 'Monitor water levels. Keep drainage channels clear.',
        }
    else:
        return {
            'level'     : 'LOW',
            'color'     : '#2ecc71',
            'css_class' : 'low',
            'action'    : 'Normal operations. Continue routine monitoring.',
        }


def estimate_impact(risk_level, population_density=2):
    """
    Estimate disaster impact based on risk level and area density.

    Args:
        risk_level (str)          : 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'
        population_density (int)  : 1=Low, 2=Medium, 3=High

    Returns:
        dict: affected population, area, infrastructure risk, resources
    """
    area_km2     = AFFECTED_AREA_KM2.get(risk_level, 0.5)
    pop_per_km2  = POPULATION_PER_KM2.get(population_density, 2000)
    affected_pop = int(area_km2 * pop_per_km2)

    infrastructure_risk = {
        'CRITICAL' : 'Roads flooded, hospitals may be inaccessible, power outages likely',
        'HIGH'     : 'Low-lying roads waterlogged, reduced hospital access',
        'MODERATE' : 'Minor road disruptions, monitor drainage',
        'LOW'      : 'No significant infrastructure impact expected',
    }

    resources_needed = {
        'CRITICAL' : [
            'NDRF teams', 'Rescue boats', 'Emergency shelters (18+ sites)',
            'Medical teams', 'Helicopters', 'Food and water supply'
        ],
        'HIGH'     : [
            'Rescue teams', 'Emergency shelters (8 sites)',
            'Medical standby', 'Pumping equipment'
        ],
        'MODERATE' : [
            'Monitoring teams', 'Emergency shelters (3 sites)', 'Pumping equipment'
        ],
        'LOW'      : ['Routine monitoring'],
    }

    return {
        'risk_level'          : risk_level,
        'affected_area_km2'   : area_km2,
        'estimated_affected'  : affected_pop,
        'infrastructure'      : infrastructure_risk.get(risk_level, ''),
        'resources_needed'    : resources_needed.get(risk_level, []),
    }


def full_assessment(probability, population_density=2):
    """
    Full flood risk assessment.

    Args:
        probability (float)      : Flood probability 0-100
        population_density (int) : 1=Low, 2=Medium, 3=High

    Returns:
        dict: complete assessment result
    """
    risk_info   = classify_risk(probability)
    impact_info = estimate_impact(risk_info['level'], population_density)

    return {
        'probability' : round(probability, 2),
        'risk'        : risk_info,
        'impact'      : impact_info,
    }


# --------------------------------------------------
# QUICK TEST
# --------------------------------------------------
if __name__ == '__main__':
    print('Risk Classifier -- KIIT Flood Prediction')
    print('-' * 50)

    test_cases = [
        (10, 1, 'Dry day, low density'),
        (30, 2, 'Light rain, medium density'),
        (60, 2, 'Heavy rain, medium density'),
        (85, 3, 'Extreme rain, high density (KIIT area)'),
    ]

    for prob, density, label in test_cases:
        result = full_assessment(prob, population_density=density)
        print('Scenario         :', label)
        print('Probability      :', prob, '%')
        print('Risk Level       :', result['risk']['level'])
        print('Action           :', result['risk']['action'])
        print('Affected People  :', result['impact']['estimated_affected'])
        print('Resources Needed :', result['impact']['resources_needed'])
        print()