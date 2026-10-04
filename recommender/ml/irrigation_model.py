"""
Irrigation Predictor (Binary Classification)
Dataset: crop_yield.csv — 1,000,000 rows
Features: Region (cat), Soil_Type (cat), Crop (cat), Rainfall_mm (num),
          Temperature_Celsius (num), Weather_Condition (cat), Days_to_Harvest (num)
Target: Irrigation_Used (True/False → 1/0)
"""
import os
import csv
import pickle
import random
from functools import lru_cache

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'irrigation_model.pkl')
DATA_PATH  = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (24)', 'crop_yield.csv'
)

IRRIG_CROPS    = ['Barley', 'Cotton', 'Maize', 'Rice', 'Soybean', 'Wheat']
IRRIG_SOILS    = ['Chalky', 'Clay', 'Loam', 'Peaty', 'Sandy', 'Silt']
IRRIG_REGIONS  = ['East', 'North', 'South', 'West']
IRRIG_WEATHERS = ['Cloudy', 'Rainy', 'Sunny']


def _encode_bool(v):
    return 1 if str(v).strip().lower() in ('true', '1', 'yes') else 0


def _train_and_save():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import numpy as np

    print("Loading crop yield dataset (sampling 200K rows for speed)...")

    SAMPLE = 200_000
    with open(DATA_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        pool = list(reader)

    random.seed(42)
    sample = random.sample(pool, min(SAMPLE, len(pool)))

    le_region  = LabelEncoder().fit(IRRIG_REGIONS)
    le_soil    = LabelEncoder().fit(IRRIG_SOILS)
    le_crop    = LabelEncoder().fit(IRRIG_CROPS)
    le_weather = LabelEncoder().fit(IRRIG_WEATHERS)

    X, y = [], []
    yield_by_crop_irr = {}  # {crop: {0: [yields], 1: [yields]}}

    for row in pool:          # use full dataset for yield impact stats
        try:
            crop_raw  = row['Crop'].strip()
            irr       = _encode_bool(row['Irrigation_Used'])
            yld       = float(row['Yield_tons_per_hectare'])
        except (ValueError, KeyError):
            continue
        yield_by_crop_irr.setdefault(crop_raw, {0: [], 1: []})[irr].append(yld)

    for row in sample:
        try:
            region  = le_region.transform([row['Region'].strip()])[0]
            soil    = le_soil.transform([row['Soil_Type'].strip()])[0]
            crop    = le_crop.transform([row['Crop'].strip()])[0]
            weather = le_weather.transform([row['Weather_Condition'].strip()])[0]
            rain    = float(row['Rainfall_mm'])
            temp    = float(row['Temperature_Celsius'])
            days    = float(row['Days_to_Harvest'])
            irr     = _encode_bool(row['Irrigation_Used'])
        except (ValueError, KeyError):
            continue
        X.append([region, soil, crop, rain, temp, weather, days])
        y.append(irr)

    print(f"  Loaded {len(X)} samples. Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_leaf=5,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X, y)

    preds = model.predict(X[:5000])
    acc   = accuracy_score(y[:5000], preds)
    print(f"  Accuracy = {acc:.4f}")

    # Compute yield impact per crop
    yield_impact = {}
    for crop_name, by_irr in yield_by_crop_irr.items():
        irr_yields   = by_irr.get(1, [])
        noirr_yields = by_irr.get(0, [])
        if not irr_yields or not noirr_yields:
            continue
        avg_irr   = sum(irr_yields)   / len(irr_yields)
        avg_noirr = sum(noirr_yields) / len(noirr_yields)
        lift_pct  = ((avg_irr - avg_noirr) / avg_noirr * 100) if avg_noirr else 0.0
        yield_impact[crop_name] = {
            'irrigated':     round(avg_irr, 3),
            'not_irrigated': round(avg_noirr, 3),
            'lift_pct':      round(lift_pct, 2),
        }

    bundle = {
        'model':        model,
        'le_region':    le_region,
        'le_soil':      le_soil,
        'le_crop':      le_crop,
        'le_weather':   le_weather,
        'yield_impact': yield_impact,
        'crops':        IRRIG_CROPS,
        'soils':        IRRIG_SOILS,
        'regions':      IRRIG_REGIONS,
        'weathers':     IRRIG_WEATHERS,
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"  Saved to {MODEL_PATH}")
    return bundle


@lru_cache(maxsize=1)
def load_irrigation_bundle():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def predict_irrigation(region, soil, crop, rainfall, temp, weather, days):
    """
    Returns irrigation recommendation dict.

    Parameters
    ----------
    region   : str  e.g. 'North'
    soil     : str  e.g. 'Clay'
    crop     : str  e.g. 'Wheat'
    rainfall : float  mm
    temp     : float  Celsius
    weather  : str  e.g. 'Sunny'
    days     : float  Days to Harvest

    Returns
    -------
    {
        should_irrigate: bool,
        confidence: float,       # 0-1
        reason: str,
        yield_with: float,       # avg t/ha when irrigated
        yield_without: float,    # avg t/ha when not irrigated
        yield_lift_pct: float,   # % gain from irrigation
    }
    """
    bundle     = load_irrigation_bundle()
    model      = bundle['model']
    le_region  = bundle['le_region']
    le_soil    = bundle['le_soil']
    le_crop    = bundle['le_crop']
    le_weather = bundle['le_weather']
    yield_impact = bundle.get('yield_impact', {})

    def safe_encode(le, val, fallback=0):
        try:
            return le.transform([str(val).strip()])[0]
        except ValueError:
            return fallback

    features = [[
        safe_encode(le_region,  region),
        safe_encode(le_soil,    soil),
        safe_encode(le_crop,    crop),
        float(rainfall),
        float(temp),
        safe_encode(le_weather, weather),
        float(days),
    ]]

    proba          = model.predict_proba(features)[0]
    irr_class_idx  = list(model.classes_).index(1) if 1 in model.classes_ else 1
    confidence     = float(proba[irr_class_idx])
    should_irrigate = confidence >= 0.5

    # Build human-readable reason
    reasons = []
    if float(rainfall) < 300:
        reasons.append(f"low rainfall ({rainfall:.0f} mm)")
    if float(temp) > 30:
        reasons.append(f"high temperature ({temp:.1f}°C)")
    if str(weather).strip().lower() == 'sunny':
        reasons.append("sunny weather increases evapotranspiration")
    if str(soil).strip().lower() in ('sandy', 'chalky'):
        reasons.append(f"{soil} soil has poor water retention")
    if float(days) > 100:
        reasons.append(f"long growing period ({days:.0f} days)")

    if should_irrigate:
        reason = ("Irrigation recommended: " + "; ".join(reasons)) if reasons \
                 else "Model predicts irrigation will improve yield."
    else:
        reason = ("Irrigation likely unnecessary: sufficient rainfall or moisture-retaining soil."
                  if not reasons else
                  "Model predicts natural conditions are adequate despite some risk factors.")

    # Yield impact lookup
    crop_impact = yield_impact.get(crop, {})
    yield_with    = crop_impact.get('irrigated',     0.0)
    yield_without = crop_impact.get('not_irrigated', 0.0)
    yield_lift    = crop_impact.get('lift_pct',      0.0)

    return {
        'should_irrigate':  should_irrigate,
        'confidence':       round(confidence, 4),
        'reason':           reason,
        'yield_with':       round(yield_with, 3),
        'yield_without':    round(yield_without, 3),
        'yield_lift_pct':   round(yield_lift, 2),
    }


def get_irrigation_options():
    b = load_irrigation_bundle()
    return {
        'crops':    b['crops'],
        'soils':    b['soils'],
        'regions':  b['regions'],
        'weathers': b['weathers'],
    }
