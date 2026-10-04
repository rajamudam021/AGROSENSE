"""
Global Crop Yield Predictor (Regression)
Dataset: yield_df.csv — 28,242 rows
Features: Area (country), Item (crop), Year, avg_rain_fall_mm_per_year,
          pesticides_tonnes, avg_temp
Target: hg/ha_yield
"""
import os
import csv
import pickle
from functools import lru_cache

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'global_yield_model.pkl')
DATA_PATH  = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (33)', 'yield_df.csv'
)


def _train_and_save():
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import r2_score, mean_absolute_error

    print("Loading global yield dataset...")
    rows = []
    with open(DATA_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"  {len(rows)} rows loaded.")

    all_areas = sorted(set(r['Area'].strip() for r in rows if r.get('Area')))
    all_items = sorted(set(r['Item'].strip() for r in rows if r.get('Item')))

    le_area = LabelEncoder().fit(all_areas)
    le_item = LabelEncoder().fit(all_items)

    X, y = [], []
    for row in rows:
        try:
            area   = le_area.transform([row['Area'].strip()])[0]
            item   = le_item.transform([row['Item'].strip()])[0]
            year   = float(row['Year'])
            rain   = float(row['average_rain_fall_mm_per_year'])
            pest   = float(row['pesticides_tonnes'])
            temp   = float(row['avg_temp'])
            yld    = float(row['hg/ha_yield'])
        except (ValueError, KeyError, TypeError):
            continue
        X.append([area, item, year, rain, pest, temp])
        y.append(yld)

    print(f"  {len(X)} clean samples. Training GradientBoosting regressor...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
    )
    model.fit(X, y)
    preds = model.predict(X)
    r2  = r2_score(y, preds)
    mae = mean_absolute_error(y, preds)
    print(f"  R² = {r2:.4f}  MAE = {mae:.1f} hg/ha")

    bundle = {
        'model':    model,
        'le_area':  le_area,
        'le_item':  le_item,
        'areas':    all_areas,
        'items':    all_items,
        'year_min': int(min(float(r['Year']) for r in rows if r.get('Year') and r['Year'])),
        'year_max': int(max(float(r['Year']) for r in rows if r.get('Year') and r['Year'])),
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"  Saved to {MODEL_PATH}")
    return bundle


@lru_cache(maxsize=1)
def load_global_yield_bundle():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def predict_global_yield(area, item, year, rainfall, pesticides, temperature):
    """Returns predicted yield in hg/ha."""
    bundle   = load_global_yield_bundle()
    model    = bundle['model']
    le_area  = bundle['le_area']
    le_item  = bundle['le_item']

    def safe_enc(le, val, fallback=0):
        try:
            return le.transform([str(val).strip()])[0]
        except ValueError:
            return fallback

    features = [[
        safe_enc(le_area, area),
        safe_enc(le_item, item),
        float(year),
        float(rainfall),
        float(pesticides),
        float(temperature),
    ]]

    pred = model.predict(features)[0]

    # Feature importances for explanation
    fi  = model.feature_importances_
    names = ['Country', 'Crop', 'Year', 'Rainfall', 'Pesticides', 'Temperature']
    factors = sorted(zip(names, fi), key=lambda x: x[1], reverse=True)

    return {
        'yield_hg_ha':   round(pred, 0),
        'yield_kg_ha':   round(pred / 10, 1),
        'yield_t_ha':    round(pred / 10000, 2),
        'key_factors':   factors[:3],
    }


def get_global_yield_options():
    b = load_global_yield_bundle()
    return {
        'areas':    b['areas'],
        'items':    b['items'],
        'year_min': b['year_min'],
        'year_max': b['year_max'],
    }


def get_country_benchmarks(item, year=None):
    """Get all countries' actual yields for a crop (for comparison chart)."""
    data = load_global_yield_bundle()
    rows = []
    with open(DATA_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Item', '').strip() == item:
                if year is None or str(row.get('Year', '')).strip() == str(year):
                    try:
                        rows.append({
                            'country': row['Area'].strip(),
                            'yield':   round(float(row['hg/ha_yield']) / 10, 1),
                            'year':    int(float(row['Year'])),
                        })
                    except (ValueError, TypeError):
                        pass
    # Average per country across years
    by_country = {}
    for r in rows:
        c = r['country']
        if c not in by_country:
            by_country[c] = []
        by_country[c].append(r['yield'])
    return sorted(
        [{'country': k, 'avg_yield': round(sum(v)/len(v), 1)} for k, v in by_country.items()],
        key=lambda x: x['avg_yield'], reverse=True
    )[:20]
