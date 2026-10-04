"""
Crop Yield Predictor (Regression)
Dataset: crop_yield.csv — 1,000,000 rows
Features: Region, Soil_Type, Crop, Rainfall_mm, Temperature_Celsius,
          Fertilizer_Used, Irrigation_Used, Weather_Condition, Days_to_Harvest
Target: Yield_tons_per_hectare
"""
import os
import csv
import pickle
import random
from functools import lru_cache

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'yield_model.pkl')
DATA_PATH  = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (24)', 'crop_yield.csv'
)

YIELD_CROPS    = ['Barley', 'Cotton', 'Maize', 'Rice', 'Soybean', 'Wheat']
YIELD_SOILS    = ['Chalky', 'Clay', 'Loam', 'Peaty', 'Sandy', 'Silt']
YIELD_REGIONS  = ['East', 'North', 'South', 'West']
YIELD_WEATHERS = ['Cloudy', 'Rainy', 'Sunny']


def _train_and_save():
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import r2_score, mean_absolute_error
    import numpy as np

    print("Loading crop yield dataset (sampling 300K rows for speed)...")

    # Sample 300K rows from 1M for reasonable training time
    SAMPLE = 300_000
    rows = []
    with open(DATA_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        pool = list(reader)

    random.seed(42)
    sample = random.sample(pool, min(SAMPLE, len(pool)))

    le_region  = LabelEncoder().fit(YIELD_REGIONS)
    le_soil    = LabelEncoder().fit(YIELD_SOILS)
    le_crop    = LabelEncoder().fit(YIELD_CROPS)
    le_weather = LabelEncoder().fit(YIELD_WEATHERS)

    def encode_bool(v):
        return 1 if str(v).strip().lower() in ('true', '1', 'yes') else 0

    X, y = [], []
    for row in sample:
        try:
            region  = le_region.transform([row['Region'].strip()])[0]
            soil    = le_soil.transform([row['Soil_Type'].strip()])[0]
            crop    = le_crop.transform([row['Crop'].strip()])[0]
            weather = le_weather.transform([row['Weather_Condition'].strip()])[0]
            fert    = encode_bool(row['Fertilizer_Used'])
            irr     = encode_bool(row['Irrigation_Used'])
            rain    = float(row['Rainfall_mm'])
            temp    = float(row['Temperature_Celsius'])
            days    = float(row['Days_to_Harvest'])
            yld     = float(row['Yield_tons_per_hectare'])
        except (ValueError, KeyError):
            continue
        X.append([region, soil, crop, rain, temp, fert, irr, weather, days])
        y.append(yld)

    print(f"  Loaded {len(X)} samples. Training RandomForest regressor...")
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_leaf=5,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X, y)
    import numpy as np
    preds = model.predict(X[:5000])
    r2  = r2_score(y[:5000], preds)
    mae = mean_absolute_error(y[:5000], preds)
    print(f"  R² = {r2:.4f}  MAE = {mae:.4f} t/ha")

    bundle = {
        'model':      model,
        'le_region':  le_region,
        'le_soil':    le_soil,
        'le_crop':    le_crop,
        'le_weather': le_weather,
        'crops':    YIELD_CROPS,
        'soils':    YIELD_SOILS,
        'regions':  YIELD_REGIONS,
        'weathers': YIELD_WEATHERS,
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"  Saved to {MODEL_PATH}")
    return bundle


@lru_cache(maxsize=1)
def load_yield_bundle():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def predict_yield(region, soil_type, crop, rainfall, temperature,
                  fertilizer_used, irrigation_used, weather, days_to_harvest):
    """
    Returns predicted yield in tons/ha (float) with confidence interval.
    """
    bundle    = load_yield_bundle()
    model     = bundle['model']
    le_region = bundle['le_region']
    le_soil   = bundle['le_soil']
    le_crop   = bundle['le_crop']
    le_weather= bundle['le_weather']

    def safe_encode(le, val, fallback=0):
        try:
            return le.transform([str(val).strip()])[0]
        except ValueError:
            return fallback

    features = [[
        safe_encode(le_region,  region),
        safe_encode(le_soil,    soil_type),
        safe_encode(le_crop,    crop),
        float(rainfall),
        float(temperature),
        1 if fertilizer_used else 0,
        1 if irrigation_used else 0,
        safe_encode(le_weather, weather),
        float(days_to_harvest),
    ]]

    # Tree-based prediction + std across estimators
    pred = model.predict(features)[0]
    tree_preds = [t.predict(features)[0] for t in model.estimators_]
    import statistics
    std = statistics.stdev(tree_preds)

    return {
        'yield': round(pred, 2),
        'low':   round(max(0, pred - std), 2),
        'high':  round(pred + std, 2),
        'std':   round(std, 3),
    }


def get_yield_options():
    b = load_yield_bundle()
    return {
        'crops':    b['crops'],
        'soils':    b['soils'],
        'regions':  b['regions'],
        'weathers': b['weathers'],
    }
