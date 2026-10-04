"""
Soybean Disease Classifier
Dataset: dataset_42_soybean.csv — 683 rows, 35 categorical features → disease class
"""
import os
import csv
import pickle
from functools import lru_cache

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'soybean_model.pkl')
DATA_PATH  = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (32)', 'dataset_42_soybean.csv'
)

# Human-readable disease info
DISEASE_INFO = {
    'diaporthe-stem-canker': {
        'display': 'Diaporthe Stem Canker',
        'severity': 'High',
        'color': '#dc2626',
        'description': 'Causes dark, sunken cankers on stems. Can kill plants at any growth stage.',
        'management': 'Use resistant varieties, crop rotation, and avoid planting in infected fields.',
        'icon': 'fa-virus',
    },
    'charcoal-rot': {
        'display': 'Charcoal Rot',
        'severity': 'High',
        'color': '#7c3aed',
        'description': 'Causes premature plant death and shredded pith turning grey-black.',
        'management': 'Optimize soil moisture, reduce plant stress, rotate with non-host crops.',
        'icon': 'fa-skull-crossbones',
    },
    'rhizoctonia-root-rot': {
        'display': 'Rhizoctonia Root Rot',
        'severity': 'Medium',
        'color': '#d97706',
        'description': 'Pre- and post-emergence damping-off; reddish-brown discoloration of hypocotyl.',
        'management': 'Seed treatment with fungicides, avoid cool-wet soils at planting.',
        'icon': 'fa-bacterium',
    },
    'phytophthora-rot': {
        'display': 'Phytophthora Root Rot',
        'severity': 'High',
        'color': '#dc2626',
        'description': 'Water-soaked lesions on stem, brown discoloration of root and lower stem.',
        'management': 'Use resistant varieties with Rps genes, improve drainage.',
        'icon': 'fa-water',
    },
    'brown-stem-rot': {
        'display': 'Brown Stem Rot',
        'severity': 'Medium',
        'color': '#92400e',
        'description': 'Internal browning of pith; interveinal yellowing of leaves.',
        'management': 'Crop rotation (2–3 years), resistant varieties, delayed planting.',
        'icon': 'fa-leaf',
    },
    'powdery-mildew': {
        'display': 'Powdery Mildew',
        'severity': 'Low',
        'color': '#059669',
        'description': 'White-grey powdery spots on upper leaf surface.',
        'management': 'Fungicide applications, resistant cultivars, reduce leaf wetness.',
        'icon': 'fa-snowflake',
    },
    'downy-mildew': {
        'display': 'Downy Mildew',
        'severity': 'Low',
        'color': '#0891b2',
        'description': 'Pale green spots on upper leaf surface, grey-purple sporulation beneath.',
        'management': 'Metalaxyl seed treatments, resistant varieties.',
        'icon': 'fa-cloud-rain',
    },
    'brown-spot': {
        'display': 'Brown Spot (Septoria)',
        'severity': 'Medium',
        'color': '#d97706',
        'description': 'Angular brown spots on leaves; early defoliation.',
        'management': 'Fungicide at R1-R3 stage, crop rotation.',
        'icon': 'fa-circle-dot',
    },
    'bacterial-blight': {
        'display': 'Bacterial Blight',
        'severity': 'Medium',
        'color': '#dc2626',
        'description': 'Angular water-soaked spots turning brown with yellow halos.',
        'management': 'Copper-based bactericides, certified clean seed.',
        'icon': 'fa-biohazard',
    },
    'bacterial-pustule': {
        'display': 'Bacterial Pustule',
        'severity': 'Low',
        'color': '#16a34a',
        'description': 'Small yellow-green spots with raised pustule on lower surface.',
        'management': 'Resistant varieties, copper sprays.',
        'icon': 'fa-circle',
    },
    'purple-seed-stain': {
        'display': 'Purple Seed Stain',
        'severity': 'Low',
        'color': '#7c3aed',
        'description': 'Pink to purple discoloration on seed coat.',
        'management': 'Fungicide seed treatment, harvest at correct moisture.',
        'icon': 'fa-eye-dropper',
    },
    'anthracnose': {
        'display': 'Anthracnose',
        'severity': 'Medium',
        'color': '#dc2626',
        'description': 'Dark sunken lesions on stems, pods and seeds. Pod and stem blight.',
        'management': 'Fungicide applications R1-R3, certified disease-free seed.',
        'icon': 'fa-virus-slash',
    },
    'phyllosticta-leaf-spot': {
        'display': 'Phyllosticta Leaf Spot',
        'severity': 'Low',
        'color': '#059669',
        'description': 'Circular tan spots with darker borders on leaves.',
        'management': 'Fungicide at first symptom, clean field debris.',
        'icon': 'fa-circle-half-stroke',
    },
    'alternarialeaf-spot': {
        'display': 'Alternaria Leaf Spot',
        'severity': 'Low',
        'color': '#d97706',
        'description': 'Dark brown irregular spots, sometimes with concentric rings.',
        'management': 'Avoid late-season stress, fungicide if severe.',
        'icon': 'fa-bullseye',
    },
    'frog-eye-leaf-spot': {
        'display': 'Frog Eye Leaf Spot',
        'severity': 'Medium',
        'color': '#d97706',
        'description': 'Circular spots with grey centres and dark brown margins.',
        'management': 'Fungicide R1-R3, resistant varieties, no-till.',
        'icon': 'fa-eye',
    },
    'diaporthe-pod-&-stem-blight': {
        'display': 'Diaporthe Pod & Stem Blight',
        'severity': 'High',
        'color': '#dc2626',
        'description': 'Brown lesions on pods and stems; infected seeds.',
        'management': 'Harvest promptly, fungicide, clean seed.',
        'icon': 'fa-seedling',
    },
    'cyst-nematode': {
        'display': 'Soybean Cyst Nematode',
        'severity': 'High',
        'color': '#7c3aed',
        'description': 'Stunted plants, yellow foliage, small white/yellow cysts on roots.',
        'management': 'SCN-resistant varieties, crop rotation, nematicide seed treatments.',
        'icon': 'fa-worm',
    },
    '2-4-d-injury': {
        'display': '2,4-D Herbicide Injury',
        'severity': 'Variable',
        'color': '#0891b2',
        'description': 'Cupped, strapped, or strap-leaved plants. Twisted stems.',
        'management': 'Avoid drift from neighbouring fields; use shielded sprayer.',
        'icon': 'fa-flask',
    },
    'herbicide-injury': {
        'display': 'Herbicide Injury',
        'severity': 'Variable',
        'color': '#0891b2',
        'description': 'Symptoms vary by herbicide: chlorosis, necrosis, or stunting.',
        'management': 'Identify herbicide involved, adjust application timing/rate.',
        'icon': 'fa-triangle-exclamation',
    },
}

# Feature definitions (35 categorical features)
FEATURE_COLS = [
    'date', 'plant-stand', 'precip', 'temp', 'hail', 'crop-hist',
    'area-damaged', 'severity', 'seed-tmt', 'germination', 'plant-growth',
    'leaves', 'leafspots-halo', 'leafspots-marg', 'leafspot-size',
    'leaf-shread', 'leaf-malf', 'leaf-mild', 'stem', 'lodging',
    'stem-cankers', 'canker-lesion', 'fruiting-bodies', 'external-decay',
    'mycelium', 'int-discolor', 'sclerotia', 'fruit-pods', 'fruit-spots',
    'seed', 'mold-growth', 'seed-discolor', 'seed-size', 'shriveling', 'roots',
]


def _train_and_save():
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import numpy as np

    print("Loading soybean disease dataset...")
    rows = []
    with open(DATA_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): v.strip() for k, v in row.items()})
    print(f"  {len(rows)} rows, {len(FEATURE_COLS)} features, {len(DISEASE_INFO)} classes")

    # Collect unique values per feature
    feature_values = {}
    for col in FEATURE_COLS:
        vals = sorted(set(r.get(col, '').strip() for r in rows if r.get(col, '').strip()))
        feature_values[col] = vals

    # Encode features
    encoders = {}
    for col in FEATURE_COLS:
        le = LabelEncoder()
        le.fit(feature_values[col] + ['unknown'])
        encoders[col] = le

    le_class = LabelEncoder()
    le_class.fit(list(DISEASE_INFO.keys()) + [r.get('class', '').strip() for r in rows])

    X, y = [], []
    for row in rows:
        feat = []
        for col in FEATURE_COLS:
            val = row.get(col, 'unknown').strip() or 'unknown'
            try:
                feat.append(encoders[col].transform([val])[0])
            except ValueError:
                feat.append(0)
        try:
            cls = le_class.transform([row.get('class', '').strip()])[0]
        except ValueError:
            continue
        X.append(feat)
        y.append(cls)

    print(f"  Training on {len(X)} samples...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=1,
        n_jobs=-1,
        random_state=42,
        class_weight='balanced',
    )
    model.fit(X, y)
    preds = model.predict(X)
    acc   = accuracy_score(y, preds)
    print(f"  Train accuracy: {acc*100:.1f}%")

    bundle = {
        'model':          model,
        'encoders':       encoders,
        'le_class':       le_class,
        'feature_cols':   FEATURE_COLS,
        'feature_values': feature_values,
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"  Saved to {MODEL_PATH}")
    return bundle


@lru_cache(maxsize=1)
def load_soybean_bundle():
    if not os.path.exists(MODEL_PATH):
        return _train_and_save()
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def get_feature_options():
    b = load_soybean_bundle()
    return {
        'feature_cols':   b['feature_cols'],
        'feature_values': b['feature_values'],
    }


def predict_soybean_disease(input_dict):
    """
    input_dict: {feature_name: value, ...}
    Returns: {disease, display_name, confidence, top3, info}
    """
    bundle   = load_soybean_bundle()
    model    = bundle['model']
    encoders = bundle['encoders']
    le_class = bundle['le_class']

    feat = []
    for col in FEATURE_COLS:
        val = str(input_dict.get(col, 'unknown')).strip() or 'unknown'
        try:
            feat.append(encoders[col].transform([val])[0])
        except ValueError:
            feat.append(0)

    proba   = model.predict_proba([feat])[0]
    top_idx = proba.argsort()[::-1][:3]

    top3 = []
    for i in top_idx:
        if proba[i] > 0.01:
            cls_name = le_class.classes_[i]
            info     = DISEASE_INFO.get(cls_name, {'display': cls_name.replace('-', ' ').title()})
            top3.append({
                'disease':    cls_name,
                'display':    info.get('display', cls_name),
                'confidence': round(float(proba[i]) * 100, 1),
                'info':       info,
            })

    top = top3[0] if top3 else {}
    return {
        'top_disease':  top.get('disease', 'Unknown'),
        'top_display':  top.get('display', 'Unknown'),
        'confidence':   top.get('confidence', 0),
        'top3':         top3,
        'info':         top.get('info', {}),
    }
