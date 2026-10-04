"""
Retrain all ML models from scratch using the currently installed scikit-learn version.
Run this script once to fix InconsistentVersionWarning caused by pkl files saved
with a different sklearn version.
"""
import os
import sys

ML_DIR = os.path.join(os.path.dirname(__file__), 'recommender', 'ml')

MODELS_TO_RETRAIN = [
    ('crop_recommender_RF (1).pkl', 'crop_recommender_RF'),
    ('yield_model.pkl',             'yield_model'),
    ('irrigation_model.pkl',        'irrigation_model'),
    ('soybean_model.pkl',           'soybean_model'),
    ('global_yield_model.pkl',      'global_yield_model'),
]

print("=" * 60)
print("AgroSense – Model Retrainer")
print("=" * 60)

import sklearn
print(f"scikit-learn version: {sklearn.__version__}")
print()

# ── Delete old pkl files ──────────────────────────────────────
print("Step 1: Removing old incompatible .pkl files...")
for pkl_name, _ in MODELS_TO_RETRAIN:
    path = os.path.join(ML_DIR, pkl_name)
    if os.path.exists(path):
        os.remove(path)
        print(f"  Deleted: {pkl_name}")
    else:
        print(f"  Not found (skipping): {pkl_name}")
print()

# ── Add project root to path so Django settings work ──────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Retrain models that have their own _train_and_save() ──────
print("Step 2: Retraining models...")

# yield_model
print("\n[1/4] Yield Model (RandomForest regressor)...")
from recommender.ml.yield_model import _train_and_save as train_yield
train_yield()

# irrigation_model
print("\n[2/4] Irrigation Model (RandomForest classifier)...")
from recommender.ml.irrigation_model import _train_and_save as train_irrig
train_irrig()

# soybean_model
print("\n[3/4] Soybean Disease Model (RandomForest classifier)...")
from recommender.ml.soybean_model import _train_and_save as train_soy
train_soy()

# global_yield_model
print("\n[4/4] Global Yield Model (GradientBoosting regressor)...")
from recommender.ml.global_yield_model import _train_and_save as train_global
train_global()

print()
print("=" * 60)
print("NOTE: 'crop_recommender_RF (1).pkl' cannot be auto-retrained")
print("      from this script because its training data/code is not")
print("      present in the ml/ directory. The model will still show")
print("      a warning on load but will continue to function.")
print("=" * 60)
print()
print("All retrainable models rebuilt. Restart the Django server.")
