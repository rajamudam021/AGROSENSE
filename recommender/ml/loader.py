import os
import pickle
from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def load_bundle():
    pkl_path = os.path.join(settings.BASE_DIR, 'recommender', 'ml', 'crop_recommender_RF (1).pkl')
    with open(pkl_path, 'rb') as f:
        bundle = pickle.load(f)
    assert "model" in bundle and "feature_cols" in bundle, "Invalid model bundle structure"
    return bundle


def predict_one(feature_dict):
    bundle = load_bundle()
    model = bundle['model']
    order = bundle['feature_cols']
    X = [[float(feature_dict[c]) for c in order]]
    return model.predict(X)


def predict_top3(feature_dict):
    """Returns top 3 crop predictions with probability scores."""
    bundle = load_bundle()
    model = bundle['model']
    order = bundle['feature_cols']
    X = [[float(feature_dict[c]) for c in order]]
    try:
        probas = model.predict_proba(X)[0]
        classes = model.classes_
        top3_idx = probas.argsort()[-3:][::-1]
        return [
            {'crop': str(classes[i]), 'probability': round(float(probas[i]) * 100, 1)}
            for i in top3_idx
        ]
    except AttributeError:
        pred = model.predict(X)[0]
        return [{'crop': str(pred), 'probability': 100.0}]
