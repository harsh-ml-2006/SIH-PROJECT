import pandas as pd
import numpy as np
import os

np.random.seed(42)
n = 1500

# --------------------------------------------------
# KIIT / BHUBANESWAR SPECIFIC DATASET
# Location  : Patia, North Bhubaneswar, Odisha
# Rivers    : Kuakhai, Daya
# Avg Rain  : 1487 mm/year  (monsoon: June-Oct)
# IMD Heavy : >64mm/day  Very Heavy: >115mm/day
# --------------------------------------------------

# Feature 1: Rainfall (mm/day)
rainfall = np.concatenate([
    np.random.uniform(0,   60, int(n * 0.35)),   # dry/light
    np.random.uniform(60,  120, int(n * 0.30)),  # heavy
    np.random.uniform(120, 250, int(n * 0.35)),  # very heavy/extreme
])
np.random.shuffle(rainfall)
rainfall = np.round(rainfall[:n], 1)

# Feature 2: Water Level (m)
water_level = (rainfall / 55.0) + np.random.normal(0, 0.35, n)
water_level = np.clip(water_level, 0.1, 5.0)
water_level = np.round(water_level, 1)

# Feature 3: Elevation  (1=Low  2=Medium  3=High)
# KIIT area is mostly flat, 50% low-lying
elevation = np.random.choice([1, 2, 3], n, p=[0.50, 0.35, 0.15])

# Feature 4: Drainage quality  (1=Poor  2=Moderate  3=Good)
# North Bhubaneswar has poor drainage in many areas
drainage = np.random.choice([1, 2, 3], n, p=[0.45, 0.35, 0.20])

# Feature 5: Humidity (%)
humidity = np.clip(40 + (rainfall / 250) * 55 + np.random.normal(0, 5, n), 40, 100)
humidity = np.round(humidity, 1)

# Feature 6: Soil Type  (1=Clay  2=Loam  3=Sandy)
# Clay = poor water absorption = more runoff = more flood risk
soil_type = np.random.choice([1, 2, 3], n, p=[0.40, 0.40, 0.20])

# Feature 7: Population Density  (1=Low  2=Medium  3=High)
population_density = np.random.choice([1, 2, 3], n, p=[0.25, 0.45, 0.30])

# Feature 8: Distance to River (km)  -- Kuakhai/Daya rivers
# Exponential: most areas are close to a river
distance_to_river = np.random.exponential(scale=3.0, size=n)
distance_to_river = np.clip(distance_to_river, 0.1, 15.0)
distance_to_river = np.round(distance_to_river, 1)

# Feature 9: Historical Flood Frequency  (0-5 floods in last 5 years)
historical_flood_freq = np.random.choice([0, 1, 2, 3, 4, 5], n,
    p=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05])

# Feature 10: Drainage Capacity (m3/hr)
# 1=Poor(~300)  2=Moderate(~600)  3=Good(~900)
base_cap = np.random.choice([300, 600, 900], n, p=[0.40, 0.35, 0.25])
drainage_capacity = np.clip(base_cap + np.random.normal(0, 50, n), 100, 1000)
drainage_capacity = np.round(drainage_capacity, 0).astype(int)

# --------------------------------------------------
# FLOOD LABEL (weighted risk score)
# --------------------------------------------------
flood_score = (
    (rainfall         -   0)  / 250  * 0.30 +
    (water_level      - 0.1)  / 4.9  * 0.25 +
    (4 - elevation)           / 3.0  * 0.15 +
    (4 - drainage)            / 3.0  * 0.10 +
    (humidity         -  40)  / 60.0 * 0.05 +
    (4 - soil_type)           / 3.0  * 0.05 +
    np.clip(1 - distance_to_river / 15, 0, 1) * 0.05 +
    historical_flood_freq     / 5.0  * 0.03 +
    (1000 - drainage_capacity)/ 900  * 0.02
)

noise      = np.random.normal(0, 0.06, n)
flood_prob = np.clip(flood_score + noise, 0, 1)
flood      = (flood_prob > 0.50).astype(int)

# --------------------------------------------------
# SAVE
# --------------------------------------------------
df = pd.DataFrame({
    'rainfall'            : rainfall,
    'water_level'         : water_level,
    'elevation'           : elevation,
    'drainage'            : drainage,
    'humidity'            : humidity,
    'soil_type'           : soil_type,
    'population_density'  : population_density,
    'distance_to_river'   : distance_to_river,
    'historical_flood_freq': historical_flood_freq,
    'drainage_capacity'   : drainage_capacity,
    'flood'               : flood
})

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = os.path.join(BASE_DIR, 'DATA', 'flood_data.csv')
df.to_csv(SAVE_PATH, index=False)

print('Dataset  : KIIT / Bhubaneswar, Odisha')
print('Rows     :', len(df))
print('Features :', len(df.columns) - 1)
print('Flood    :', flood.sum(), '(' + str(round(flood.mean()*100, 1)) + '%)')
print('No-flood :', (1-flood).sum(), '(' + str(round((1-flood.mean())*100, 1)) + '%)')
print('Saved    :', SAVE_PATH)