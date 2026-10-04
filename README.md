# AgroSense — Smart AI Farming Advisor

A full-stack Django web application that combines machine learning, statistical analysis, and agricultural datasets to deliver **20 tools across four tiers** — from crop recommendation to climate-impact forecasting and portfolio optimization.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Live Features](#live-features)
  - [Core Platform](#core-platform)
  - [Tier-1 — Advisory Tools](#tier-1--advisory-tools)
  - [Tier-2 — AI / ML Models](#tier-2--ai--ml-models)
  - [Tier-3 — Research & Analytics](#tier-3--research--analytics)
  - [Tier-4 — AI Forecasting & Optimization](#tier-4--ai-forecasting--optimization)
- [Tech Stack](#tech-stack)
- [ML Models](#ml-models)
- [Datasets](#datasets)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [URL Reference](#url-reference)
- [Screenshots](#screenshots)
- [Notes](#notes)

---

## Project Overview

AgroSense is built on Django 4.2 with a single `recommender` app. It uses:

- **RandomForest / GradientBoosting** models (scikit-learn) for tabular prediction
- **MobileNetV2 CNN** (TensorFlow/Keras) for image-based rice disease detection
- **Pure Python / stdlib** for statistical analysis (Pearson correlation, CSV parsing)
- **Chart.js** for interactive frontend charts
- **Bootstrap 5** with a custom warm earthy agricultural theme
- **`lru_cache`** for lazy-loading and in-memory caching of large datasets

---

## Live Features

### Core Platform

| Feature | URL | Description |
|---|---|---|
| Home / Landing | `/` | Hero page with feature cards |
| Crop Recommender | `/predict/` | RF model predicts best crop from N, P, K, temp, humidity, pH, rainfall — with top-3 results and confidence bars |
| Dashboard | `/dashboard/` | Personal stats, prediction history charts |
| Prediction History | `/history/` | Paginated log of all past predictions |
| Market Prices | `/market-prices/` | Live indicative commodity prices |
| Farming Tips | `/farming-tips/` | Season-wise agronomic tips |
| Crop Calendar | `/crop-calendar/` | Kharif / Rabi / Zaid sowing calendars |
| User Profile | `/profile/` | Account settings and stats |
| Auth | `/signup/` `/login/` `/logout/` | Full authentication flow |
| Weather API | `/api/weather/` | JSON endpoint for live weather |
| Prediction Report | `/report/<id>/` | Shareable PDF-style report per prediction |

---

### Tier-1 — Advisory Tools

Six data-driven advisory tools using Indian agricultural datasets.

| # | Feature | URL | Data Source |
|---|---|---|---|
| 1 | **Fertilizer Advisor** | `/fertilizer/` | Trained RF classifier on soil + crop → NPK recommendation |
| 2 | **Cost Calculator** | `/cost-calculator/` | Input area, crop, inputs → estimated cost & profit |
| 3 | **District Benchmark** | `/district-benchmark/` | APY dataset — compare your district's yield vs state avg |
| 4 | **India Trends** | `/trends/` | National crop production & yield trends 1997–2015 |
| 5 | **Tamil Nadu Analytics** | `/tn-analytics/` | TN-specific district-level production breakdown |
| 6 | **Variety Recommender** | Embedded in `/predict/` | Curated variety suggestions per crop (season, zone) |

---

### Tier-2 — AI / ML Models

Five trained machine learning models with interactive inference UIs.

| # | Feature | URL | Model | Accuracy |
|---|---|---|---|---|
| 7 | **Yield Predictor** | `/yield-predictor/` | RandomForestRegressor | R² = 0.94, MAE = 0.34 t/ha |
| 8 | **Global Yield Predictor** | `/global-yield/` | GradientBoostingRegressor | R² = 0.97 |
| 9 | **Rice Disease Detector** | `/disease-detect/` | MobileNetV2 CNN (transfer learning) | 92.5% val accuracy |
| 10 | **Soybean Disease Classifier** | `/soybean-disease/` | RandomForestClassifier | 99.9% train accuracy |
| 11 | **Pesticide vs Yield Analysis** | `/pesticide-analysis/` | Pearson correlation analysis | r = 0.06 overall |

**Yield Predictor** (`/yield-predictor/`)
- Trained on 300K random sample of 1M-row `crop_yield.csv`
- Features: Region, Soil Type, Crop, Rainfall (mm), Temperature (°C), Fertilizer Used, Irrigation Used, Weather Condition, Days to Harvest
- Output: Predicted yield (t/ha) with ±confidence interval from per-tree std

**Global Yield Predictor** (`/global-yield/`)
- Trained on 28,242 rows from `yield_df.csv` (FAO + World Bank merged dataset)
- Features: Country, Crop, Year, Rainfall (mm/yr), Pesticides (tonnes), Avg Temperature
- Output: Yield in hg/ha, kg/ha, t/ha + country benchmark chart (top 20)

**Rice Disease Detector** (`/disease-detect/`)
- Upload any rice leaf photo → CNN classifies into 4 diseases
- Classes: Bacterial Blight, Rice Blast, Brown Spot, False Smut
- Architecture: MobileNetV2 (ImageNet weights) → custom head → fine-tune top 20 layers
- Training: 160 images / 40 validation images (200 total from archive 31)
- Fallback: HOG + colour histogram → SVM (if TensorFlow unavailable)

**Soybean Disease Classifier** (`/soybean-disease/`)
- 35-feature symptom questionnaire (leaf colour, spots, stem, roots, etc.)
- 19 possible disease classes from UCI soybean dataset (683 rows)
- Shows: top diagnosis, confidence %, differential diagnosis bar chart, disease reference grid

**Pesticide vs Yield Correlation** (`/pesticide-analysis/`)
- Merges FAO pesticide data (`pesticides.csv`) with global yield data (`yield_df.csv`)
- Pearson r computed per-crop and per-country (pure Python, no pandas)
- Interactive scatter chart with crop filter; country correlation table

---

### Tier-3 — Research & Analytics

Six ambitious multi-dataset analytics pages.

| # | Feature | URL | Data |
|---|---|---|---|
| 12 | **Global Agriculture Comparison** | `/global-agriculture/` | FAO 5 continental CSVs, 1961–2019, 200+ crops |
| 13 | **Smart Irrigation Advisor** | `/irrigation-advisor/` | RF binary classifier on 1M-row crop_yield.csv |
| 14 | **Crop Rotation Planner** | `/rotation-planner/` | IPNI/FAO NPK removal data + curated agronomic DB |
| 15 | **Soil Nutrient Tracker** | `/soil-tracker/` | Session-based N/P/K balance calculator |
| 16 | **US vs India Corn Comparison** | `/corn-comparison/` | USDA NASS + India Crops_data.csv |
| 17 | **Food Security Index** | `/food-security/` | APY.csv × Census 2011 population, 37 states |

**Global Agriculture Comparison** (`/global-agriculture/`)
- Select any of 200+ FAO crops and compare Production / Yield / Area Harvested across 5 continents from 1961 to 2019
- Multi-line Chart.js chart + top-20 country ranking table

**Smart Irrigation Advisor** (`/irrigation-advisor/`)
- Binary RF classifier (78.6% accuracy, 200K training rows)
- Inputs: Crop, Region, Soil Type, Weather, Rainfall, Temperature, Days to Harvest
- Output: Irrigate / Don't Irrigate recommendation with confidence %, reason text, and yield-lift % (irrigated vs non-irrigated average from full 1M row dataset)

**Crop Rotation Planner** (`/rotation-planner/`)
- Select current crop → get top-6 next-crop suggestions ranked by agronomic benefit
- Uses scientifically-sourced NPK removal rates (kg/tonne produce) from IPNI/FAO for 29 crops
- Curated `_ROTATION_AFTER` lookup with agronomic reasoning per crop pair
- NPK reference table for all 29 crops; legume N-fixing indicator

**Soil Nutrient Tracker** (`/soil-tracker/`)
- Session-based tool — add crop seasons with yield achieved and fertilizer applied (N, P, K kg/ha)
- Auto-computes nutrient removal (NPK × yield_t) and balance (applied − removed)
- Cumulative balance chart across all seasons; colour-coded surplus/deficit indicators

**US vs India Corn Comparison** (`/corn-comparison/`)
- US: USDA NASS corn grain yield (bu/acre → kg/ha, 1 bu/acre = 62.77 kg/ha), state-level
- India: Crops_data.csv district-level maize yield averaged to state level (kg/ha)
- National trend line chart + top-15 state rankings for both countries
- Yield gap analysis: US vs India % difference

**Food Security Index** (`/food-security/`)
- APY dataset (345K rows): aggregated annual average production per state (tonnes/yr)
- Per-capita kg/yr = (avg annual production × 1000) ÷ Census 2011 population
- 37 Indian states ranked by per-capita agricultural output
- Surplus score = state per-capita ÷ national average (1.0 = average)
- Bar chart of all states + year-wise national production trend

---

### Tier-4 — AI Forecasting & Optimization

Three new advanced tools using time-series analysis, anomaly detection, and optimization algorithms — all implemented with pure-Python statistics (no extra dependencies beyond scikit-learn).

| # | Feature | URL | Data | Approach |
|---|---|---|---|---|
| 18 | **Climate Impact on Yield Forecasting** | `/climate-forecast/` | `yield_df.csv` (28K rows) + temp/rainfall | OLS linear regression + extrapolation to 2030/2050 |
| 19 | **Crop Production Anomaly Detection** | `/anomaly-detection/` | `APY.csv` (345K rows) | Z-score per district-crop group; flags crashes & spikes |
| 20 | **Multi-crop Portfolio Optimizer** | `/portfolio-optimizer/` | ICAR `datafile (1).csv` + MSP prices | Greedy profit-maximization with diversification constraint |

**Climate Impact on Yield Forecasting** (`/climate-forecast/`)
- Covers 101 countries, 10 global crops, data spanning 1961–2013
- Fits OLS trend line on Year→Yield and Year→Temperature separately
- Extrapolates to **2030** and **2050** with % change vs current baseline
- Computes Pearson r between temperature and yield (positive/negative climate signal)
- Interactive Chart.js line chart: historical yield + trend line + forecast stars
- Example: *India Rice* → 3.51 t/ha now → 4.22 t/ha by 2030 → 5.05 t/ha by 2050 (+1.1 °C warming projected)

**Crop Production Anomaly Detection** (`/anomaly-detection/`)
- Indexes 345,657 district-crop-year records from the APY dataset
- Z-score computed per (State, District, Crop) group (requires ≥ 3 years of data)
- Threshold configurable: 1.5 / 2.0 / 2.5 / 3.0 (standard = 2.0, ~5% tail)
- Direction labels: **Crash** (Z < 0) or **Spike** (Z > 0) with % deviation from group mean
- Bar chart of top-20 anomalies coloured red/green; full sortable table
- Example: *DEORIA district, Uttar Pradesh, Rice 2015* → Z = −3.5, −61% yield crash

**Multi-crop Portfolio Optimizer** (`/portfolio-optimizer/`)
- Loads ICAR cultivation cost data (cost/ha, yield q/ha for 10 crops from 49 state-level rows)
- Combines with MSP / market prices to compute revenue, profit/ha, and ROI per crop
- User inputs: farm size (acres), budget (₹), risk tolerance (Low / Balanced / Aggressive), max crops
- Greedy allocation: rank by profit/ha, respect budget, enforce ≤ 60% single-crop diversification rule
- Outputs: donut chart of land allocation, per-crop breakdown (area, cost, revenue, profit), overall ROI
- Example: *5 acres, ₹50,000 budget (Balanced)* → 31% Sugarcane → expected profit ₹1.29L (257% ROI)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 4.2.11 |
| ML / Stats | scikit-learn 1.8, TensorFlow 2.x (optional), NumPy |
| Data | Pure Python `csv` module, `functools.lru_cache` (no pandas at runtime) |
| Frontend | Bootstrap 5.3, Chart.js 4.4, Font Awesome 6 |
| Database | SQLite (development) |
| Auth | Django built-in `django.contrib.auth` |
| Deployment ready | `manage.py`, `wsgi.py`, environment variables via `settings.py` |

---

## ML Models

| Model File | Size | Algorithm | Trained On | Excluded from Git |
|---|---|---|---|---|
| `crop_recommender_RF.pkl` | 3.6 MB | RandomForest (100 trees) | 2,200 rows, 7 features | No |
| `fertilizer_model.pkl` | 168 MB | RandomForest | Fertilizer dataset | **Yes** (>100MB) |
| `yield_model.pkl` | 167 MB | RandomForest (200 trees) | 300K rows, 9 features | **Yes** (>100MB) |
| `global_yield_model.pkl` | 940 KB | GradientBoosting (200 est.) | 28,242 rows, 6 features | No |
| `soybean_model.pkl` | 9.1 MB | RandomForest, balanced | 683 rows, 35 features, 19 classes | No |
| `irrigation_model.pkl` | 40 MB | RandomForest (100 trees) | 200K rows, 7 features | No |
| `rice_disease_model.pkl` | 4 KB | SVM (fallback sklearn) | HOG features from 200 images | No |
| `rice_disease_tf.keras` | ~9 MB | MobileNetV2 + fine-tuning | 200 images, 4 classes | No |

> **Note:** `fertilizer_model.pkl` and `yield_model.pkl` are excluded from this repo (exceed GitHub's 100MB file limit). They are automatically retrained and saved on first server startup if missing.

---

## Datasets

| Archive | File(s) | Rows | Used For |
|---|---|---|---|
| archive (22) | `Crop_recommendation.csv` | 2,200 | Crop recommender (N, P, K, temp, humidity, pH, rainfall → crop) |
| archive (24) | `crop_yield.csv` | 1,000,000 | Yield Predictor + Irrigation Advisor ML training |
| archive (30) | `APY.csv` | 345,658 | India Trends, District Benchmark, TN Analytics, Food Security |
| archive (31) | `Rice_Diseases/` (200 images) | 200 imgs | Rice Disease Detector (CNN training) |
| archive (32) | `corn yield.csv` | ~50K | US corn yield by state (USDA NASS) |
| archive (32) | `dataset_42_soybean.csv` | 683 | Soybean Disease Classifier (35 features, 19 classes) |
| archive (33) | `yield_df.csv` | 28,242 | Global Yield Predictor, Pesticide Analysis, **Climate Forecast** |
| archive (23) | `pesticides.csv` | ~10K | Pesticide vs Yield Correlation |
| archive (38) | `APY.csv` | 345,657 | **Anomaly Detection** (district-crop Z-score) |
| archive (37) | `datafile (1).csv` | 49 | **Portfolio Optimizer** (ICAR cost & yield data) |
| archive (34) | `Production_Crops_E_*.csv` (5 files) | ~38K | FAO continental data (Africa, Asia, Americas, Europe, Oceania) |
| archive (35) | `crops.csv` | 736 | US crop NPK reference (Rotation Planner supplementary) |
| archive (40) | `Crops_data.csv` | ~100K | India district-level maize yield (US vs India comparison) |
| archive (21) | `Tamilnadu agriculture yield data.csv` | — | Tamil Nadu Analytics |
| archive (27) | `India Agriculture Crop Production.csv` | — | Additional India production data |

---

## Project Structure

```
crop_site/
├── manage.py
├── README.md
├── .gitignore
├── crop_site/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── datasets/
│   ├── archive (22)/   — Crop recommendation CSV
│   ├── archive (24)/   — 1M-row crop yield CSV
│   ├── archive (30)/   — APY India production
│   ├── archive (31)/   — Rice disease images (200)
│   ├── archive (32)/   — US corn yield + soybean disease
│   ├── archive (33)/   — Global yield (FAO+WorldBank)
│   ├── archive (34)/   — FAO 5 continental CSVs
│   ├── archive (40)/   — India crops data
│   └── ...
└── recommender/
    ├── models.py           — UserProfile, Prediction
    ├── views.py            — All 33 view functions
    ├── urls.py             — 33 URL routes
    ├── data.py             — Static data (crop info, market prices)
    ├── dataset_loaders.py  — Tier-1 dataset loaders (lru_cache)
    ├── dataset_loaders_t3.py — Tier-3 loaders (FAO, corn, food security, rotation)
    ├── templatetags/
    │   └── dict_extras.py  — Custom template filter: {{ dict|get_item:key }}
    ├── ml/
    │   ├── loader.py               — Crop recommender RF model
    │   ├── fertilizer_loader.py    — Fertilizer advisor model
    │   ├── yield_model.py          — Yield Predictor (RF, 1M rows)
    │   ├── global_yield_model.py   — Global Yield (GBM, 28K rows)
    │   ├── rice_disease_model.py   — Rice Disease CNN (MobileNetV2)
    │   ├── soybean_model.py        — Soybean Disease RF (683 rows)
    │   ├── pesticide_analysis.py   — Pearson correlation analysis
    │   ├── irrigation_model.py     — Irrigation RF classifier (1M rows)
    │   ├── climate_analytics.py    — Climate forecast (OLS trend + extrapolation)
    │   ├── anomaly_detector.py     — Yield anomaly detection (Z-score, APY dataset)
    │   └── portfolio_optimizer.py  — Multi-crop portfolio optimizer (greedy LP)
    └── templates/
        ├── base.html               — Navbar, theme, layout
        ├── home.html               — Landing page
        ├── predict.html            — Crop recommender + variety cards
        ├── dashboard.html
        ├── fertilizer.html         — Tier-1
        ├── cost_calculator.html    — Tier-1
        ├── district_benchmark.html — Tier-1
        ├── trends_dashboard.html   — Tier-1
        ├── tn_analytics.html       — Tier-1
        ├── yield_predictor.html    — Tier-2
        ├── global_yield.html       — Tier-2
        ├── rice_disease.html       — Tier-2
        ├── soybean_disease.html    — Tier-2
        ├── pesticide_analysis.html — Tier-2
        ├── global_agriculture.html — Tier-3
        ├── irrigation_advisor.html — Tier-3
        ├── rotation_planner.html   — Tier-3
        ├── soil_tracker.html       — Tier-3
        ├── corn_comparison.html    — Tier-3
        ├── food_security.html      — Tier-3
        ├── climate_forecast.html   — Tier-4
        ├── anomaly_detection.html  — Tier-4
        └── portfolio_optimizer.html — Tier-4
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- pip
- (Optional) TensorFlow 2.x for CNN rice disease model

### 1. Clone the repository

```bash
git clone https://github.com/rajamudam021/AGROSENSE.git
cd Crop-Prediction/crop_site
```

### 2. Create a virtual environment

```bash
python -m venv env
source env/bin/activate        # Linux / macOS
env\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install django==4.2.11 scikit-learn numpy pillow
# Optional: for CNN rice disease model
pip install tensorflow
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for /admin)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 7. First-run model training

On first access to **Yield Predictor** (`/yield-predictor/`) and **Fertilizer Advisor** (`/fertilizer/`), the app will automatically train and save the large RF models from the datasets. This takes ~2–5 minutes each and only happens once. All other models are pre-trained and included in the repository.

---

## URL Reference

```
/                          Home
/predict/                  Crop Recommender
/dashboard/                Dashboard
/history/                  Prediction History
/market-prices/            Market Prices
/farming-tips/             Farming Tips
/crop-calendar/            Crop Calendar
/profile/                  User Profile
/report/<id>/              Prediction Report

# Tier-1 — Advisory Tools
/fertilizer/               Fertilizer Advisor
/cost-calculator/          Input Cost Calculator
/district-benchmark/       District Yield Benchmark
/trends/                   India Crop Trends
/tn-analytics/             Tamil Nadu Analytics

# Tier-2 — AI / ML Models
/yield-predictor/          Yield Predictor (RF)
/global-yield/             Global Yield Predictor (GBM)
/disease-detect/           Rice Disease Detector (CNN)
/soybean-disease/          Soybean Disease Classifier
/pesticide-analysis/       Pesticide vs Yield Correlation

# Tier-3 — Research & Analytics
/global-agriculture/       FAO Global Agriculture Comparison
/irrigation-advisor/       Smart Irrigation Advisor
/rotation-planner/         Crop Rotation Planner
/soil-tracker/             Soil Nutrient Depletion Tracker
/corn-comparison/          US vs India Corn Yield
/food-security/            India Food Security Index

# Tier-4 — AI Forecasting & Optimization
/climate-forecast/         Climate Impact on Yield Forecasting (2030/2050)
/anomaly-detection/        Crop Production Anomaly Detection (Z-score)
/portfolio-optimizer/      Multi-crop Portfolio Optimizer

# API
/api/weather/              Live weather JSON
/api/districts/            Districts AJAX endpoint
```

---

## Notes

- **No pandas at runtime** — all dataset loading uses Python's built-in `csv` module for minimal memory overhead and no dependency conflicts.
- **Lazy loading** — every heavy dataset is wrapped in `@lru_cache(maxsize=1)`. Data loads once on first request and stays in memory for the server lifetime.
- **Large models** — `fertilizer_model.pkl` (168 MB) and `yield_model.pkl` (167 MB) exceed GitHub's 100 MB file size limit. They are listed in `.gitignore` and will auto-retrain on first use.
- **TensorFlow optional** — the rice disease page gracefully falls back to an sklearn SVM using HOG + colour histogram features if TensorFlow is not installed.
- **SQLite** — the project uses SQLite for development. For production, switch to PostgreSQL in `settings.py`.
- **Session-based tracker** — the Soil Nutrient Tracker stores history in Django sessions (no database writes). Data resets when the session expires.

---

## Author

**Raja**
[GitHub: rajamudam021](https://github.com/rajamudam021)
