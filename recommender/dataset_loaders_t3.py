"""
Dataset loaders for Tier-3 features.
All heavy data is loaded lazily and cached in memory (lru_cache).
No pandas — pure csv + stdlib only.
"""
import os
import csv
import re
from functools import lru_cache

BASE_DS = os.path.join(os.path.dirname(__file__), '..', 'datasets')


# ─────────────────────────────────────────────────────────────────────────────
# 1. FAO CONTINENTAL DATA  (archive 34)
# ─────────────────────────────────────────────────────────────────────────────

_FAO_FILES = {
    'Africa':   'Production_Crops_E_Africa.csv',
    'Asia':     'Production_Crops_E_Asia.csv',
    'Americas': 'Production_Crops_E_Americas.csv',
    'Europe':   'Production_Crops_E_Europe.csv',
    'Oceania':  'Production_Crops_E_Oceania.csv',
}
_FAO_DIR = os.path.join(BASE_DS, 'archive (34)')
_FAO_ELEMENTS = {'Yield', 'Production', 'Area harvested'}
_YEAR_RE = re.compile(r'^Y(\d{4})$')


def _fao_year_cols(fieldnames):
    """Return list of (col_name, year_int) for data columns like Y1961, Y1962..."""
    result = []
    for col in fieldnames:
        m = _YEAR_RE.match(col)
        if m:
            result.append((col, int(m.group(1))))
    return result


@lru_cache(maxsize=1)
def load_fao_data():
    """
    Load all 5 FAO continental CSV files and return aggregated structure.

    Returns
    -------
    {
      'by_item_country': {item: {country: {element: {year: value}}}},
      'items':     [sorted unique crop names],
      'countries': [sorted unique country names],
      'years':     list(range(1961, 2020)),
      'by_continent': {continent: {item: {year: {production: sum,
                                                  yield: avg,
                                                  area: sum}}}},
    }
    """
    by_item_country = {}   # item -> country -> element -> year -> value
    by_continent    = {}   # continent -> item -> year -> {production, yield_sum, yield_n, area}
    all_items       = set()
    all_countries   = set()

    for continent, filename in _FAO_FILES.items():
        path = os.path.join(_FAO_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, newline='', encoding='latin-1') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            year_cols  = _fao_year_cols(fieldnames)

            for row in reader:
                element = (row.get('Element') or '').strip()
                if element not in _FAO_ELEMENTS:
                    continue

                item    = (row.get('Item')  or '').strip()
                country = (row.get('Area')  or '').strip()
                if not item or not country:
                    continue

                all_items.add(item)
                all_countries.add(country)

                # Populate by_item_country
                ic = by_item_country.setdefault(item, {})
                co = ic.setdefault(country, {})
                el = co.setdefault(element, {})

                # Populate by_continent
                bc  = by_continent.setdefault(continent, {})
                bci = bc.setdefault(item, {})

                for col, year in year_cols:
                    raw = (row.get(col) or '').strip()
                    if not raw:
                        continue
                    try:
                        val = float(raw)
                    except ValueError:
                        continue
                    el[year] = val

                    # Aggregate into continent bucket
                    bcy = bci.setdefault(year, {
                        'production': 0.0,
                        'yield_sum':  0.0,
                        'yield_n':    0,
                        'area':       0.0,
                    })
                    if element == 'Production':
                        bcy['production'] += val
                    elif element == 'Yield':
                        bcy['yield_sum']  += val
                        bcy['yield_n']    += 1
                    elif element == 'Area harvested':
                        bcy['area']       += val

    # Compact continent: replace yield_sum/n with avg
    for continent, items_d in by_continent.items():
        for item, years_d in items_d.items():
            for year, agg in years_d.items():
                n   = agg.pop('yield_n', 0)
                ys  = agg.pop('yield_sum', 0.0)
                agg['yield'] = round(ys / n, 4) if n else 0.0

    return {
        'by_item_country': by_item_country,
        'items':           sorted(all_items),
        'countries':       sorted(all_countries),
        'years':           list(range(1961, 2020)),
        'by_continent':    by_continent,
    }


def get_fao_crop_timeseries(item, countries=None, element='Yield'):
    """
    Returns {country: {year: value}} for the given item/element.
    If countries is None, returns all countries.
    Years are integers.
    """
    data   = load_fao_data()
    ic     = data['by_item_country'].get(item, {})
    result = {}
    for country, elements in ic.items():
        if countries is not None and country not in countries:
            continue
        el_data = elements.get(element, {})
        if el_data:
            result[country] = {int(yr): val for yr, val in el_data.items()}
    return result


def get_fao_continent_timeseries(item, element='Production'):
    """
    Returns {continent: {year: value}} aggregated across countries.
    """
    data   = load_fao_data()
    bc     = data['by_continent']
    result = {}
    key_map = {
        'Production':     'production',
        'Yield':          'yield',
        'Area harvested': 'area',
    }
    agg_key = key_map.get(element, 'production')
    for continent, items_d in bc.items():
        item_d = items_d.get(item, {})
        if item_d:
            result[continent] = {int(yr): agg.get(agg_key, 0.0)
                                 for yr, agg in item_d.items()}
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 2. CROP NUTRIENT DATA + ROTATION SUGGESTIONS  (archive 35)
# ─────────────────────────────────────────────────────────────────────────────

_CROPS_CSV = os.path.join(BASE_DS, 'archive (35)', 'crops.csv')

# Map recommender crop labels to crops.csv Crop column (case-insensitive lookup)
_RECOMMENDER_TO_CROPS_CSV = {
    'rice':        'Rice',
    'maize':       'Corn, Grain',
    'wheat':       'Wheat, Winter',
    'barley':      'Barley',
    'cotton':      'Cotton',
    'soybean':     'Soybean',
    'chickpea':    'Chickpea',
    'lentil':      'Lentil',
    'groundnut':   'Peanut',
    'sugarcane':   'Sugarcane',
    'mungbean':    'Cowpea',
    'blackgram':   'Cowpea',
    'pigeonpeas':  'Pigeon Pea',
    'mothbeans':   'Cowpea',
    'kidneybeans': 'Snap Bean',
    'jute':        'Sunflower',
    'mustard':     'Canola',
    'coffee':      'Alfalfa',
    'apple':       'Apple',
    'banana':      'Banana',
    'grapes':      'Grape',
    'mango':       'Mango',
    'orange':      'Orange',
    'papaya':      'Papaya',
    'pomegranate': 'Pomegranate',
    'watermelon':  'Watermelon',
    'coconut':     'Coconut',
}

# Fallback NPK nutrient data (kg nutrient per tonne of grain) for recommender crops
# Sources: FAO Fertilizer Recommendations, IPNI crop nutrient removal guides
_CROP_NPK_FALLBACK = {
    'rice':        {'N': 17.5, 'P': 3.5, 'K': 20.0, 'category': 'Cereal', 'legume': False},
    'wheat':       {'N': 30.0, 'P': 5.0, 'K': 6.0,  'category': 'Cereal', 'legume': False},
    'maize':       {'N': 14.0, 'P': 2.5, 'K': 4.0,  'category': 'Cereal', 'legume': False},
    'barley':      {'N': 23.0, 'P': 4.0, 'K': 5.5,  'category': 'Cereal', 'legume': False},
    'sugarcane':   {'N': 1.0,  'P': 0.5, 'K': 1.6,  'category': 'Sugar',  'legume': False},
    'cotton':      {'N': 55.0, 'P': 9.0, 'K': 19.0, 'category': 'Fiber',  'legume': False},
    'jute':        {'N': 18.0, 'P': 4.0, 'K': 30.0, 'category': 'Fiber',  'legume': False},
    'soybean':     {'N': 80.0, 'P': 10.0,'K': 30.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'chickpea':    {'N': 60.0, 'P': 8.0, 'K': 25.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'lentil':      {'N': 55.0, 'P': 7.0, 'K': 20.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'mungbean':    {'N': 45.0, 'P': 7.0, 'K': 25.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'blackgram':   {'N': 50.0, 'P': 8.0, 'K': 22.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'pigeonpeas':  {'N': 55.0, 'P': 8.5, 'K': 24.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'kidneybeans': {'N': 45.0, 'P': 7.0, 'K': 20.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'mothbeans':   {'N': 40.0, 'P': 6.0, 'K': 18.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'groundnut':   {'N': 56.0, 'P': 6.0, 'K': 19.0, 'category': 'Legume', 'legume': True,  'fixes_n': True},
    'mustard':     {'N': 35.0, 'P': 10.0,'K': 12.0, 'category': 'Oilseed','legume': False},
    'sesame':      {'N': 42.0, 'P': 8.5, 'K': 15.0, 'category': 'Oilseed','legume': False},
    'coffee':      {'N': 30.0, 'P': 5.0, 'K': 40.0, 'category': 'Beverage','legume': False},
    'apple':       {'N': 3.0,  'P': 0.5, 'K': 5.0,  'category': 'Fruit',  'legume': False},
    'banana':      {'N': 1.5,  'P': 0.3, 'K': 5.0,  'category': 'Fruit',  'legume': False},
    'grapes':      {'N': 4.0,  'P': 0.7, 'K': 7.0,  'category': 'Fruit',  'legume': False},
    'mango':       {'N': 2.5,  'P': 0.5, 'K': 4.0,  'category': 'Fruit',  'legume': False},
    'watermelon':  {'N': 2.0,  'P': 0.5, 'K': 3.5,  'category': 'Vegetable','legume': False},
    'coconut':     {'N': 2.0,  'P': 0.5, 'K': 8.0,  'category': 'Fruit',  'legume': False},
    'papaya':      {'N': 3.5,  'P': 0.7, 'K': 6.0,  'category': 'Fruit',  'legume': False},
    'orange':      {'N': 3.5,  'P': 0.6, 'K': 5.0,  'category': 'Fruit',  'legume': False},
    'pomegranate': {'N': 3.0,  'P': 0.6, 'K': 5.5,  'category': 'Fruit',  'legume': False},
}

# Rotation knowledge: what to grow after each crop (NPK-based + agronomic)
_ROTATION_AFTER = {
    'rice':      [('wheat','Cereal break, avoids rice blast carryover'),
                  ('mungbean','Legume: fixes N depleted by rice, 90-day quick crop'),
                  ('chickpea','Legume: fixes N, low water requirement'),
                  ('mustard','Oilseed: different pest cycle, good for soil structure'),
                  ('lentil','Legume: fixes N, adds organic matter')],
    'wheat':     [('chickpea','Legume: fixes N depleted by wheat, common rotation'),
                  ('maize','Cereal rotation breaks wheat diseases'),
                  ('soybean','Legume: high N-fixing, best wheat rotation partner'),
                  ('mustard','Oilseed: different nutrient profile'),
                  ('mungbean','Short-duration legume, fits between wheat seasons')],
    'maize':     [('soybean','Soybean-corn rotation is the classic high-yield system'),
                  ('wheat','Winter wheat after maize is highly productive'),
                  ('chickpea','Legume: fixes N depleted by maize\'s heavy demand'),
                  ('groundnut','Legume+oilseed: replenishes N, breaks corn rootworm cycle'),
                  ('barley','Cereal variety: different disease spectrum')],
    'cotton':    [('wheat','Classic cotton-wheat rotation in Punjab/Haryana'),
                  ('chickpea','Legume: cotton is a heavy N user'),
                  ('soybean','N-fixer, completely different pest family'),
                  ('maize','Breaks cotton bollworm cycle'),
                  ('barley','Winter crop, good for soil rest')],
    'sugarcane': [('soybean','Legume: restores N after sugarcane\'s long crop duration'),
                  ('wheat','Ratoon sugarcane → wheat is classic in UP'),
                  ('mungbean','Quick short-season legume after cane harvest'),
                  ('maize','Breaks sugarcane pests, good biomass'),
                  ('groundnut','N-fixer, improves soil porosity')],
    'soybean':   [('wheat','Classic soybean-wheat rotation'),
                  ('maize','Soybean-corn is the world\'s best rotation'),
                  ('rice','Takes advantage of N left by soybean'),
                  ('barley','Uses residual N from soybean nodules'),
                  ('cotton','Different pest and disease spectrum')],
    'default':   [('soybean','Legume: fixes atmospheric N for next crop'),
                  ('mungbean','Short-duration legume, fits most rotations'),
                  ('wheat','Cereal with different nutrient draw'),
                  ('mustard','Oilseed: breaks pathogen cycles'),
                  ('barley','Hardy cereal, good soil cover')],
}

# Legume / N-fixing crops in crops.csv (partial name match)
_LEGUME_KEYWORDS = {
    'soybean', 'soya', 'cowpea', 'pea', 'bean', 'lentil', 'chickpea',
    'pigeon', 'alfalfa', 'clover', 'vetch', 'groundnut', 'peanut',
    'mung', 'blackgram', 'urd',
}


def _safe_float(val):
    try:
        v = str(val).strip().replace(',', '')
        if not v or v in ('#DIV/0!', 'N/A', '-', ''):
            return None
        return float(v)
    except (ValueError, TypeError):
        return None


@lru_cache(maxsize=1)
def load_crops_nutrients():
    """
    Load datasets/archive (35)/crops.csv.

    Returns
    -------
    {crop_lower: {N: float, P: float, K: float,
                  category: str, yield_unit: str, crop_name: str}}
    """
    result = {}
    if not os.path.exists(_CROPS_CSV):
        return result

    with open(_CROPS_CSV, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            crop     = (row.get('Crop') or '').strip()
            category = (row.get('CropCategory') or '').strip()
            y_unit   = (row.get('YieldUnit') or '').strip()
            n_val    = _safe_float(row.get('AvN%(dry)'))
            p_val    = _safe_float(row.get('AvP%(dry)'))
            k_val    = _safe_float(row.get('AvK%(dry)'))
            if not crop:
                continue
            result[crop.lower()] = {
                'N':         n_val,
                'P':         p_val,
                'K':         k_val,
                'category':  category,
                'yield_unit': y_unit,
                'crop_name': crop,
            }
    return result


def _is_legume(crop_lower):
    return any(kw in crop_lower for kw in _LEGUME_KEYWORDS)


def get_rotation_suggestions(crop_label, top_n=5):
    """
    Given the current crop label (recommender system label),
    return a ranked list of rotation candidates with agronomic reasoning.

    Returns
    -------
    list of {crop, reason, replenishes, N_removes, P_removes, K_removes, score}
    sorted by score descending.
    """
    crop_label_lower = (crop_label or '').lower().strip()

    # 1. Look up current crop in fallback table
    current_npk = _CROP_NPK_FALLBACK.get(crop_label_lower)
    current_is_legume = (current_npk or {}).get('legume', False)
    current_category  = (current_npk or {}).get('category', '')

    # Determine which nutrient classes were depleted
    depleted_n = (current_npk['N'] if current_npk else 0) > 10.0   # kg/tonne
    depleted_p = (current_npk['P'] if current_npk else 0) > 4.0
    depleted_k = (current_npk['K'] if current_npk else 0) > 8.0

    # 2. Get curated rotation order
    curated = _ROTATION_AFTER.get(crop_label_lower, _ROTATION_AFTER['default'])

    results = []
    seen    = set()
    # First add curated suggestions (guaranteed agronomically sound)
    for next_crop, agronomic_reason in curated:
        if next_crop == crop_label_lower or next_crop in seen:
            continue
        seen.add(next_crop)
        npk   = _CROP_NPK_FALLBACK.get(next_crop, {})
        is_leg = npk.get('legume', False) or npk.get('fixes_n', False)

        replenishes = []
        score = 10.0   # base score for curated (preferred over generic)
        if is_leg and depleted_n and not current_is_legume:
            replenishes.append('N (legume N-fixation)')
            score += 2.0
        elif is_leg:
            replenishes.append('soil health via N-fixation')
        if npk.get('category', '') != current_category and current_category:
            replenishes.append('crop diversity')
            score += 0.5

        results.append({
            'crop':        next_crop.title(),
            'reason':      agronomic_reason,
            'replenishes': ', '.join(replenishes) if replenishes else 'general soil rest',
            'N_removes':   npk.get('N', 0.0),
            'P_removes':   npk.get('P', 0.0),
            'K_removes':   npk.get('K', 0.0),
            'is_legume':   is_leg,
            'score':       round(score, 2),
        })

    # 3. Fill remaining slots from fallback table (scored)
    for next_crop, npk in _CROP_NPK_FALLBACK.items():
        if len(results) >= top_n:
            break
        if next_crop == crop_label_lower or next_crop in seen:
            continue
        seen.add(next_crop)
        is_leg = npk.get('legume', False) or npk.get('fixes_n', False)
        score  = 0.0
        replenishes = []

        if is_leg and depleted_n and not current_is_legume:
            score += 3.0
            replenishes.append('N (legume N-fixation)')
        if npk.get('category', '') != current_category and current_category:
            score += 0.5
            replenishes.append('crop diversity')
        if depleted_n and npk.get('N', 99) < 10:
            score += 1.0
            replenishes.append('N (low demand)')
        if depleted_p and npk.get('P', 99) < 4:
            score += 0.5
            replenishes.append('P (low demand)')
        if depleted_k and npk.get('K', 99) < 8:
            score += 0.3
            replenishes.append('K (low demand)')

        results.append({
            'crop':        next_crop.title(),
            'reason':      'Agronomic rotation: different nutrient demand and pest cycle',
            'replenishes': ', '.join(replenishes) if replenishes else 'general rotation benefit',
            'N_removes':   npk.get('N', 0.0),
            'P_removes':   npk.get('P', 0.0),
            'K_removes':   npk.get('K', 0.0),
            'is_legume':   is_leg,
            'score':       round(score, 2),
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_n]


# ─────────────────────────────────────────────────────────────────────────────
# 3. CORN YIELD COMPARISON — US vs INDIA  (archives 32 & 40)
# ─────────────────────────────────────────────────────────────────────────────

_CORN_US_CSV    = os.path.join(BASE_DS, 'archive (32)', 'corn yield.csv')
_CROPS_DATA_CSV = os.path.join(BASE_DS, 'archive (40)', 'Crops_data.csv')

_BU_ACRE_TO_KG_HA = 62.77   # 1 bu/acre corn ≈ 62.77 kg/ha


@lru_cache(maxsize=1)
def load_corn_comparison():
    """
    Load corn/maize yield data for US (by state) and India (by state).

    Returns
    -------
    {
      'us_by_state':       {state: {year: yield_kg_ha}},
      'india_by_state':    {state: {year: yield_kg_ha}},
      'us_national_avg':   {year: yield_kg_ha},
      'india_national_avg':{year: yield_kg_ha},
    }
    """
    us_by_state    = {}
    india_by_state = {}

    # ── US data ──────────────────────────────────────────────────────────────
    _TONS_ACRE_TO_KG_HA = 2241.7   # 1 short ton/acre ≈ 2241.7 kg/ha
    if os.path.exists(_CORN_US_CSV):
        with open(_CORN_US_CSV, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                geo   = (row.get('Geo Level') or '').strip()
                ditem = (row.get('Data Item')  or '').strip().upper()
                if geo != 'STATE':
                    continue
                # Prefer grain bu/acre; also accept silage tons/acre as fallback
                is_grain  = 'CORN, GRAIN - YIELD' in ditem and 'BU / ACRE'   in ditem
                is_silage = 'CORN, SILAGE - YIELD' in ditem and 'TONS / ACRE' in ditem
                if not is_grain and not is_silage:
                    continue
                state    = (row.get('State') or '').strip().title()
                year_raw = (row.get('Year')  or '').strip()
                val_raw  = (row.get('Value') or '').strip().replace(',', '')
                if not state or not year_raw or not val_raw or val_raw in ('', ' ', '(D)', '(Z)'):
                    continue
                try:
                    year = int(year_raw)
                    raw_val = float(val_raw)
                    val = raw_val * (_BU_ACRE_TO_KG_HA if is_grain else _TONS_ACRE_TO_KG_HA)
                except ValueError:
                    continue
                # Only store grain if we have it; silage only fills in missing years
                existing = us_by_state.setdefault(state, {})
                if is_grain or year not in existing:
                    existing[year] = round(val, 1)

    # ── India data ────────────────────────────────────────────────────────────
    if os.path.exists(_CROPS_DATA_CSV):
        with open(_CROPS_DATA_CSV, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            # Find column containing MAIZE or CORN yield
            maize_yield_col = None
            for col in fieldnames:
                cu = col.upper()
                if ('MAIZE' in cu or 'CORN' in cu) and 'YIELD' in cu:
                    maize_yield_col = col
                    break

            for row in reader:
                state    = (row.get('State Name') or '').strip().title()
                year_raw = (row.get('Year')        or '').strip()
                if not state or not year_raw:
                    continue
                try:
                    year = int(float(year_raw))
                except ValueError:
                    continue

                if maize_yield_col:
                    val_raw = (row.get(maize_yield_col) or '').strip()
                    try:
                        val = float(val_raw)   # already in kg/ha
                        if val > 0:
                            # accumulate: average across districts later
                            india_by_state.setdefault(state, {}).setdefault(year, []).append(val)
                    except ValueError:
                        pass

    # Average district-level values to state level
    india_averaged = {}
    for state, year_dict in india_by_state.items():
        india_averaged[state] = {}
        for year, vals in year_dict.items():
            india_averaged[state][year] = round(sum(vals) / len(vals), 1)

    # ── National averages ─────────────────────────────────────────────────────
    def _national_avg(by_state_d):
        agg = {}
        for state_d in by_state_d.values():
            for yr, val in state_d.items():
                agg.setdefault(yr, []).append(val)
        return {yr: round(sum(v) / len(v), 1) for yr, v in agg.items()}

    return {
        'us_by_state':        us_by_state,
        'india_by_state':     india_averaged,
        'us_national_avg':    _national_avg(us_by_state),
        'india_national_avg': _national_avg(india_averaged),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 4. FOOD SECURITY (APY — Indian production per-capita)  (archive 30)
# ─────────────────────────────────────────────────────────────────────────────

_APY_CSV = os.path.join(BASE_DS, 'archive (30)', 'APY.csv')

# 2011 India Census population by state (approximate)
_STATE_POPULATION_2011 = {
    'Andhra Pradesh':         84665533,
    'Arunachal Pradesh':       1383727,
    'Assam':                  31205576,
    'Bihar':                  104099452,
    'Chhattisgarh':           25545198,
    'Goa':                     1458545,
    'Gujarat':                60439692,
    'Haryana':                25351462,
    'Himachal Pradesh':        6864602,
    'Jammu And Kashmir':      12541302,
    'Jharkhand':              32988134,
    'Karnataka':              61095297,
    'Kerala':                 33406061,
    'Madhya Pradesh':         72626809,
    'Maharashtra':            112374333,
    'Manipur':                 2855794,
    'Meghalaya':               2966889,
    'Mizoram':                 1097206,
    'Nagaland':                1978502,
    'Odisha':                 41974218,
    'Punjab':                 27743338,
    'Rajasthan':              68548437,
    'Sikkim':                   610577,
    'Tamil Nadu':             72147030,
    'Telangana':              35003674,
    'Tripura':                 3673917,
    'Uttar Pradesh':          199812341,
    'Uttarakhand':             10086292,
    'West Bengal':            91276115,
    'Andaman And Nicobar Island':  380581,
    'Chandigarh':               1055450,
    'Dadra And Nagar Haveli':    343709,
    'Daman And Diu':             243247,
    'Delhi':                  16787941,
    'Lakshadweep':               64473,
    'Puducherry':               1247953,
}


@lru_cache(maxsize=1)
def load_food_security():
    """
    Load APY.csv and compute per-capita agricultural production by Indian state.

    Production is in tonnes (APY units are tonnes for production).
    Per-capita is computed in kg (1 tonne = 1000 kg).

    Returns
    -------
    {
      'by_state': {
          state: {
              total_prod: float,        # total tonnes across all crops/years
              per_capita_kg: float,     # kg per person (total_prod * 1000 / population)
              surplus_score: float,     # per_capita relative to national avg
              years: {year: total_prod_tonnes},
          }
      },
      'surplus_states':  [(state, per_capita_kg), ...],  # sorted desc
      'deficit_states':  [(state, per_capita_kg), ...],  # sorted asc
      'national_avg_per_capita': float,
      'year_trend': {year: national_total_tonnes},
      'states': [sorted list],
    }
    """
    if not os.path.exists(_APY_CSV):
        return {}

    # Aggregate: state -> year -> total production (tonnes)
    state_year_prod = {}    # {state: {year: prod_tonnes}}
    year_national   = {}    # {year: prod_tonnes}

    with open(_APY_CSV, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state    = (row.get('State')    or '').strip()
            year_raw = (row.get('Crop_Year') or '').strip()
            prod_raw = (row.get('Production') or '').strip()

            if not state:
                continue
            try:
                year = int(float(year_raw))
            except (ValueError, TypeError):
                continue
            try:
                prod = float(prod_raw)
                if prod < 0:
                    prod = 0.0
            except (ValueError, TypeError):
                prod = 0.0

            state_year_prod.setdefault(state, {})
            state_year_prod[state][year] = state_year_prod[state].get(year, 0.0) + prod
            year_national[year]          = year_national.get(year, 0.0) + prod

    # Build by_state summary
    by_state    = {}
    total_pop   = 0
    total_prod_all = 0.0

    for state, year_d in state_year_prod.items():
        # Use ANNUAL AVERAGE production (not cumulative sum across years)
        n_years    = max(len(year_d), 1)
        avg_annual_prod = sum(year_d.values()) / n_years   # tonnes/year average
        total_prod = avg_annual_prod

        pop = _STATE_POPULATION_2011.get(state)
        if pop is None:
            for k, v in _STATE_POPULATION_2011.items():
                if k.lower() == state.lower():
                    pop = v
                    break
        pop = pop or 1_000_000

        # kg per person per year = (avg tonnes/yr × 1000) / population
        per_cap_kg = (total_prod * 1000.0) / pop

        by_state[state] = {
            'total_prod':   round(total_prod, 2),
            'per_capita_kg': round(per_cap_kg, 2),
            'surplus_score': 0.0,          # filled after national avg computed
            'years':         {yr: round(p, 2) for yr, p in year_d.items()},
        }
        total_pop      += pop
        total_prod_all += total_prod

    # National average per-capita (weighted by population)
    if total_pop:
        nat_avg = (total_prod_all * 1000.0) / total_pop   # total_prod_all is now sum of annual avgs
    else:
        all_pcs = [v['per_capita_kg'] for v in by_state.values()]
        nat_avg = sum(all_pcs) / len(all_pcs) if all_pcs else 0.0

    # Surplus score = ratio to national avg
    for state, d in by_state.items():
        d['surplus_score'] = round(d['per_capita_kg'] / nat_avg, 4) if nat_avg else 0.0

    ranked = sorted(by_state.items(), key=lambda x: x[1]['per_capita_kg'], reverse=True)
    mid    = len(ranked) // 2

    return {
        'by_state':               by_state,
        'surplus_states':         [(s, d['per_capita_kg']) for s, d in ranked],
        'deficit_states':         [(s, d['per_capita_kg']) for s, d in reversed(ranked)],
        'national_avg_per_capita': round(nat_avg, 2),
        'year_trend':             {yr: round(p, 2) for yr, p in sorted(year_national.items())},
        'states':                 sorted(by_state.keys()),
    }
