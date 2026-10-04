"""
Fertilizer Recommendation ML Model
Trained on data_core.csv (8,000 rows)
Features: Temperature, Humidity, Moisture, Soil Type, Crop Type → Fertilizer Name
"""
import os
import pickle
import numpy as np
from functools import lru_cache

MODEL_PATH  = os.path.join(os.path.dirname(__file__), 'fertilizer_model.pkl')
DATA_PATH   = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (29)', 'data_core.csv'
)

# Fertilizer info: dosage, timing, notes
FERTILIZER_INFO = {
    'Urea': {
        'nutrient': 'Nitrogen (N)',
        'npk': '46-0-0',
        'dosage': '50–100 kg/ha',
        'timing': 'Split: 50% at sowing, 50% at tillering',
        'notes': 'Most common nitrogen source. Apply when soil moisture is adequate.',
        'icon': 'fa-bottle-droplet',
        'color': '#16a34a',
    },
    'DAP': {
        'nutrient': 'Phosphorus (P) + Nitrogen (N)',
        'npk': '18-46-0',
        'dosage': '50–125 kg/ha',
        'timing': 'Basal application before sowing',
        'notes': 'Excellent starter fertilizer. Best for phosphorus-deficient soils.',
        'icon': 'fa-flask',
        'color': '#2563eb',
    },
    '14-35-14': {
        'nutrient': 'N + P + K (balanced)',
        'npk': '14-35-14',
        'dosage': '75–150 kg/ha',
        'timing': 'Basal or early-stage application',
        'notes': 'High-phosphorus complex fertilizer. Good for oilseeds and cotton.',
        'icon': 'fa-atom',
        'color': '#7c3aed',
    },
    '17-17-17': {
        'nutrient': 'N + P + K (equal)',
        'npk': '17-17-17',
        'dosage': '75–150 kg/ha',
        'timing': 'Basal or split application',
        'notes': 'Balanced NPK. Suitable when all three nutrients are needed equally.',
        'icon': 'fa-scale-balanced',
        'color': '#d97706',
    },
    '20-20': {
        'nutrient': 'N + P (equal)',
        'npk': '20-20-0',
        'dosage': '75–100 kg/ha',
        'timing': 'Basal application',
        'notes': 'Used for crops needing equal N and P without extra Potassium.',
        'icon': 'fa-droplet',
        'color': '#0891b2',
    },
    '28-28': {
        'nutrient': 'N + P (high)',
        'npk': '28-28-0',
        'dosage': '50–100 kg/ha',
        'timing': 'Basal or split',
        'notes': 'High NPK ratio. Good for crops with intensive N and P requirements.',
        'icon': 'fa-star',
        'color': '#dc2626',
    },
    '10-26-26': {
        'nutrient': 'P + K (high)',
        'npk': '10-26-26',
        'dosage': '75–150 kg/ha',
        'timing': 'Basal application',
        'notes': 'Excellent for fruiting/podding stage. High P and K for root crops and legumes.',
        'icon': 'fa-leaf',
        'color': '#059669',
    },
}


def _train_and_save():
    """Train the fertilizer RF model and save to disk. Called once on first use."""
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder

    path = os.path.normpath(DATA_PATH)
    df = pd.read_csv(path)

    # Rename typo column
    if 'Temparature' in df.columns:
        df.rename(columns={'Temparature': 'Temperature'}, inplace=True)

    le_soil = LabelEncoder()
    le_crop = LabelEncoder()
    le_fert = LabelEncoder()

    df['Soil_enc'] = le_soil.fit_transform(df['Soil Type'])
    df['Crop_enc'] = le_crop.fit_transform(df['Crop Type'])
    df['Fert_enc'] = le_fert.fit_transform(df['Fertilizer Name'])

    X = df[['Temperature', 'Humidity', 'Moisture', 'Soil_enc', 'Crop_enc']].values
    y = df['Fert_enc'].values

    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    clf.fit(X, y)

    bundle = {
        'model':      clf,
        'le_soil':    le_soil,
        'le_crop':    le_crop,
        'le_fert':    le_fert,
        'soil_types': list(le_soil.classes_),
        'crop_types': list(le_crop.classes_),
        'fertilizers': list(le_fert.classes_),
    }

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)

    return bundle


@lru_cache(maxsize=1)
def load_fertilizer_bundle():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def predict_fertilizer(temperature, humidity, moisture, soil_type, crop_type):
    """
    Returns (top_fertilizer: str, recommendations: list[dict])
    Each recommendation: {fertilizer, probability, info}
    """
    bundle   = load_fertilizer_bundle()
    model    = bundle['model']
    le_soil  = bundle['le_soil']
    le_crop  = bundle['le_crop']
    le_fert  = bundle['le_fert']

    # Encode inputs, fallback to 0 if unseen
    try:
        soil_enc = le_soil.transform([soil_type])[0]
    except ValueError:
        soil_enc = 0

    try:
        crop_enc = le_crop.transform([crop_type])[0]
    except ValueError:
        crop_enc = 0

    features = np.array([[float(temperature), float(humidity),
                          float(moisture), soil_enc, crop_enc]])

    pred_enc = model.predict(features)[0]
    top_fert = le_fert.inverse_transform([pred_enc])[0]

    proba       = model.predict_proba(features)[0]
    top_indices = np.argsort(proba)[::-1][:3]

    recommendations = []
    for i in top_indices:
        if proba[i] > 0.03:
            fert_name = le_fert.classes_[i]
            recommendations.append({
                'fertilizer':  fert_name,
                'probability': round(float(proba[i]) * 100, 1),
                'info':        FERTILIZER_INFO.get(fert_name, {}),
            })

    return top_fert, recommendations


def get_soil_types():
    return load_fertilizer_bundle()['soil_types']


def get_crop_types():
    return load_fertilizer_bundle()['crop_types']
