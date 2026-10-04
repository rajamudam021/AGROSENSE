"""
Dataset loaders for Tier-1 features.
All heavy data is loaded lazily and cached in memory (lru_cache).
"""
import os
import csv
from functools import lru_cache

BASE_DS = os.path.join(os.path.dirname(__file__), '..', 'datasets')


# ─────────────────────────────────────────────
# 1. CROP VARIETY DATA (archive 28, datafile 3)
# ─────────────────────────────────────────────
VARIETY_PATH = os.path.join(BASE_DS, 'archive (28)', 'datafile (3).csv')

# Map recommender crop labels → variety dataset crop names
_CROP_MAP = {
    'rice':        'Paddy',
    'maize':       'Maize',
    'chickpea':    'Chickpea ',
    'pigeonpeas':  'Cluster Bean',
    'mungbean':    'Mungbean',
    'blackgram':   'Urdbean',
    'lentil':      'Lentil',
    'cotton':      'Cotton',
    'jute':        'Jute',
    'mothbeans':   'Mungbean',   # closest match
    'kidneybeans': 'Fieldpea',   # closest match
    'groundnut':   'Groundnut',
    'wheat':       'Wheat',
    'barley':      'Barley',
    'sugarcane':   'Sugarcane',
    'maize':       'Maize',
    'sesame':      'Sesame',
    'mustard':     'Indian Mustard',
}


@lru_cache(maxsize=1)
def load_variety_data():
    """Returns {crop_name_lower: [{variety, season, zone}, ...]}"""
    data = {}
    if not os.path.exists(VARIETY_PATH):
        return data
    with open(VARIETY_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            crop = (row.get('Crop') or '').strip()
            variety = (row.get('Variety') or '').strip()
            season = (row.get('Season/ duration in days') or '').strip()
            zone = (row.get('Recommended Zone') or '').strip()
            if crop and variety:
                key = crop.lower().strip()
                data.setdefault(key, []).append({
                    'variety': variety,
                    'season':  season,
                    'zone':    zone,
                })
    return data


def get_varieties_for_crop(crop_label):
    """
    Given a recommender crop label (e.g. 'rice'), return list of recommended varieties.
    """
    variety_data = load_variety_data()
    crop_label   = (crop_label or '').lower().strip()

    # Try direct match first
    if crop_label in variety_data:
        return variety_data[crop_label]

    # Try mapped name
    mapped = _CROP_MAP.get(crop_label, '').lower()
    if mapped in variety_data:
        return variety_data[mapped]

    # Fuzzy: check if crop_label appears in any key
    for key, variants in variety_data.items():
        if crop_label in key or key in crop_label:
            return variants

    return []


# ─────────────────────────────────────────────
# 2. CULTIVATION COST DATA (archive 28, datafile 1)
# ─────────────────────────────────────────────
COST_PATH = os.path.join(BASE_DS, 'archive (28)', 'datafile (1).csv')

_COST_CROP_MAP = {
    'rice':      'PADDY',
    'wheat':     'WHEAT',
    'maize':     'MAIZE',
    'chickpea':  'GRAM',
    'groundnut': 'GROUNDNUT',
    'cotton':    'COTTON',
    'sugarcane': 'SUGARCANE',
    'pigeonpeas':'ARHAR',
    'mungbean':  'MOONG',
    'mustard':   'RAPESEED AND MUSTARD',
}


@lru_cache(maxsize=1)
def load_cost_data():
    """Returns {crop_upper: {state: {cost_a2fl, cost_c2, cost_per_q, yield_q_per_ha}}}"""
    data = {}
    if not os.path.exists(COST_PATH):
        return data
    with open(COST_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            crop  = (row.get('Crop') or '').strip().upper()
            state = (row.get('State') or '').strip().title()

            def clean(v):
                try:
                    return round(float((v or '0').replace(',', '').strip()), 2)
                except (ValueError, AttributeError):
                    return 0.0

            cols  = list(row.keys())
            c_a2  = clean(row.get(cols[2], '0'))
            c_c2  = clean(row.get(cols[3], '0'))
            c_pq  = clean(row.get(cols[4], '0'))
            yld   = clean(row.get(cols[5], '0'))

            data.setdefault(crop, {})[state] = {
                'cost_a2fl':       c_a2,
                'cost_c2':         c_c2,
                'cost_per_quintal':c_pq,
                'yield_q_per_ha':  yld,
            }
    return data


def get_cost_for_crop(crop_label, state=None):
    """
    Returns list of {state, cost_a2fl, cost_c2, cost_per_quintal, yield_q_per_ha}
    Optionally filtered by state name.
    """
    cost_data = load_cost_data()
    crop_label = (crop_label or '').lower().strip()
    crop_key   = _COST_CROP_MAP.get(crop_label, crop_label.upper())

    rows = cost_data.get(crop_key, {})
    if not rows:
        # Try partial match
        for k, v in cost_data.items():
            if crop_label in k.lower() or k.lower() in crop_label:
                rows = v
                break

    result = [{'state': s, **vals} for s, vals in rows.items()]

    if state:
        result = [r for r in result if state.lower() in r['state'].lower()]

    return sorted(result, key=lambda x: x['state'])


def get_all_cost_crops():
    return sorted(load_cost_data().keys())


def get_all_cost_states():
    states = set()
    for crop_states in load_cost_data().values():
        states.update(crop_states.keys())
    return sorted(states)


# ─────────────────────────────────────────────
# 3. APY DATA — District Yield Benchmarking + India Trends
# ─────────────────────────────────────────────
APY_PATH = os.path.join(BASE_DS, 'archive (30)', 'APY.csv')


@lru_cache(maxsize=1)
def load_apy_data():
    """
    Returns a dict:
    {
      'by_district': {state: {district: {crop: {avg_yield, max_yield, avg_area, years, count}}}},
      'by_state_crop_year': {state: {crop: {year: production}}},
      'national_by_crop_year': {crop: {year: production}},
      'states': [sorted list],
      'crops':  [sorted list],
    }
    """
    if not os.path.exists(APY_PATH):
        return {}

    # Read CSV manually for speed (avoid pandas overhead at runtime)
    by_district     = {}
    by_state        = {}
    national        = {}
    all_states      = set()
    all_crops       = set()

    with open(APY_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows   = list(reader)

    for row in rows:
        state    = (row.get('State')    or '').strip()
        district = (row.get('District ') or row.get('District') or '').strip()
        crop     = (row.get('Crop')     or '').strip()
        year_raw = (row.get('Crop_Year') or '').strip()
        yield_raw= (row.get('Yield')    or '').strip()
        prod_raw = (row.get('Production') or '').strip()
        area_raw = (row.get('Area ')    or row.get('Area') or '').strip()

        if not (state and district and crop):
            continue

        all_states.add(state)
        all_crops.add(crop)

        try:
            year = int(float(year_raw))
        except (ValueError, TypeError):
            year = None

        try:
            yld = float(yield_raw)
        except (ValueError, TypeError):
            yld = None

        try:
            prod = float(prod_raw)
        except (ValueError, TypeError):
            prod = None

        try:
            area = float(area_raw)
        except (ValueError, TypeError):
            area = None

        # --- by_district aggregation ---
        by_district.setdefault(state, {}).setdefault(district, {}).setdefault(crop, {
            'yields': [], 'areas': [], 'prods': [], 'years': []
        })
        entry = by_district[state][district][crop]
        if yld  is not None: entry['yields'].append(yld)
        if area is not None: entry['areas'].append(area)
        if prod is not None: entry['prods'].append(prod)
        if year is not None: entry['years'].append(year)

        # --- by_state for trends ---
        if year:
            by_state.setdefault(state, {}).setdefault(crop, {})
            cur = by_state[state][crop].get(year, {'prod': 0, 'area': 0, 'n': 0})
            by_state[state][crop][year] = {
                'prod': cur['prod'] + (prod or 0),
                'area': cur['area'] + (area or 0),
                'n':    cur['n'] + 1,
            }
            # national
            national.setdefault(crop, {})
            ncur = national[crop].get(year, {'prod': 0, 'area': 0, 'n': 0})
            national[crop][year] = {
                'prod': ncur['prod'] + (prod or 0),
                'area': ncur['area'] + (area or 0),
                'n':    ncur['n'] + 1,
            }

    # Compact district data: replace raw lists with aggregates
    for state, districts in by_district.items():
        for district, crops in districts.items():
            for crop, d in crops.items():
                yl = d['yields']
                al = d['areas']
                pl = d['prods']
                yrs= d['years']
                by_district[state][district][crop] = {
                    'avg_yield':  round(sum(yl)/len(yl), 2) if yl else None,
                    'max_yield':  round(max(yl), 2) if yl else None,
                    'avg_area':   round(sum(al)/len(al), 0) if al else None,
                    'avg_prod':   round(sum(pl)/len(pl), 0) if pl else None,
                    'years':      f"{min(yrs)}–{max(yrs)}" if yrs else 'N/A',
                    'data_points': len(d['yields']) if d['yields'] else len(d['years']),
                }

    return {
        'by_district':           by_district,
        'by_state_crop_year':    by_state,
        'national_by_crop_year': national,
        'states':                sorted(all_states),
        'crops':                 sorted(all_crops),
    }


def get_district_benchmark(state, district, crop):
    """Return benchmark data for a given state/district/crop."""
    data     = load_apy_data()
    bd       = data.get('by_district', {})
    state_d  = bd.get(state, {})

    # fuzzy district match
    dist_d = state_d.get(district, {})
    if not dist_d:
        for k, v in state_d.items():
            if district.lower() in k.lower() or k.lower() in district.lower():
                dist_d = v
                break

    # fuzzy crop match
    crop_d = dist_d.get(crop, {})
    if not crop_d:
        for k, v in dist_d.items():
            if crop.lower() in k.lower() or k.lower() in crop.lower():
                crop_d = v
                break

    return crop_d


def get_national_trends(crop, top_n_years=20):
    """Return national production trend for a crop (most recent top_n_years)."""
    data          = load_apy_data()
    nat           = data.get('national_by_crop_year', {})
    by_state_raw  = data.get('by_state_crop_year', {})

    # fuzzy crop match
    matched_key = crop
    crop_data   = nat.get(crop, {})
    if not crop_data:
        for k, v in nat.items():
            if crop.lower() in k.lower() or k.lower() in crop.lower():
                crop_data   = v
                matched_key = k
                break

    years = sorted(crop_data.keys(), reverse=True)[:top_n_years]
    years = sorted(years)

    # Per-year yield (prod / area)
    def safe_yield(y):
        a = crop_data[y]['area']
        p = crop_data[y]['prod']
        return round(p / a, 2) if a else 0

    # State-level averages for this crop
    by_state = {}
    for state, crops_dict in by_state_raw.items():
        cd = crops_dict.get(matched_key, {})
        if not cd:
            for k, v in crops_dict.items():
                if matched_key.lower() in k.lower():
                    cd = v
                    break
        if cd:
            total_prod  = sum(v['prod'] for v in cd.values())
            total_area  = sum(v['area'] for v in cd.values())
            n           = len(cd)
            by_state[state] = {
                'production': round(total_prod / n / 1000, 1) if n else 0,
                'yield':      round(total_prod / total_area, 2) if total_area else 0,
            }

    return {
        'years':      years,
        'production': [round(crop_data[y]['prod'] / 1000, 1) for y in years],
        'area':       [round(crop_data[y]['area'] / 1000, 1) for y in years],
        'yield':      [safe_yield(y) for y in years],
        'by_state':   by_state,
    }


def get_apy_states():
    return load_apy_data().get('states', [])


def get_apy_crops():
    return load_apy_data().get('crops', [])


def get_districts_for_state(state):
    bd = load_apy_data().get('by_district', {})
    return sorted(bd.get(state, {}).keys())


# ─────────────────────────────────────────────
# 4. TAMIL NADU DATA
# ─────────────────────────────────────────────
TN_PATH = os.path.join(BASE_DS, 'archive (21)', 'Tamilnadu agriculture yield data.csv')


@lru_cache(maxsize=1)
def load_tn_data():
    """
    Returns:
    {
      'by_district': {district: {crop: {avg_prod, avg_area, years, seasons}}},
      'by_crop':     {crop: {district: avg_prod}},
      'by_year':     {year: {total_production}},
      'top_crops_by_district': {district: [(crop, avg_prod), ...]},
      'districts': [...],
      'crops':     [...],
      'years':     [...],
    }
    """
    if not os.path.exists(TN_PATH):
        return {}

    raw = {}     # district -> crop -> {prods, areas, years}
    by_year = {}

    with open(TN_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            district = (row.get('District_Name') or '').strip()
            crop     = (row.get('Crop')          or '').strip()
            year_raw = (row.get('Crop_Year')     or '').strip()
            prod_raw = (row.get('Production')    or '').strip()
            area_raw = (row.get('Area')          or '').strip()
            season   = (row.get('Season')        or '').strip()

            if not (district and crop):
                continue

            try:
                year = int(float(year_raw))
            except (ValueError, TypeError):
                year = None

            try:
                prod = float(prod_raw)
            except (ValueError, TypeError):
                prod = None

            try:
                area = float(area_raw)
            except (ValueError, TypeError):
                area = None

            raw.setdefault(district, {}).setdefault(crop, {
                'prods': [], 'areas': [], 'years': [], 'seasons': set()
            })
            e = raw[district][crop]
            if prod is not None: e['prods'].append(prod)
            if area is not None: e['areas'].append(area)
            if year is not None: e['years'].append(year)
            if season:            e['seasons'].add(season)

            if year:
                by_year.setdefault(year, {'prod': 0, 'n': 0})
                by_year[year]['prod'] += prod or 0
                by_year[year]['n']    += 1

    # Aggregate
    by_district = {}
    by_crop     = {}
    all_districts = set()
    all_crops     = set()

    for district, crops in raw.items():
        all_districts.add(district)
        by_district[district] = {}
        for crop, d in crops.items():
            all_crops.add(crop)
            avg_p = round(sum(d['prods'])/len(d['prods']), 1) if d['prods'] else None
            avg_a = round(sum(d['areas'])/len(d['areas']), 1) if d['areas'] else None
            by_district[district][crop] = {
                'avg_prod': avg_p,
                'avg_area': avg_a,
                'years':    f"{min(d['years'])}–{max(d['years'])}" if d['years'] else 'N/A',
                'seasons':  ', '.join(sorted(d['seasons'])),
            }
            by_crop.setdefault(crop, {})[district] = avg_p

    # Top crops per district (by avg production)
    top_crops = {}
    for district, crops in by_district.items():
        ranked = sorted(
            [(c, v['avg_prod']) for c, v in crops.items() if v['avg_prod']],
            key=lambda x: x[1], reverse=True
        )[:5]
        top_crops[district] = ranked

    # Year trend
    year_trend = {
        'labels': [str(y) for y in sorted(by_year.keys())],
        'production': [round(by_year[y]['prod'] / 1000, 1) for y in sorted(by_year.keys())],
    }

    # Top producing districts (sum of avg_prod across all crops)
    district_totals = {}
    for district, crops in by_district.items():
        total = sum(v['avg_prod'] for v in crops.values() if v['avg_prod'])
        district_totals[district] = round(total, 0)

    top_districts = sorted(district_totals.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        'by_district':    by_district,
        'by_crop':        by_crop,
        'year_trend':     year_trend,
        'top_crops':      top_crops,
        'top_districts':  top_districts,
        'districts':      sorted(all_districts),
        'crops':          sorted(all_crops),
        'years':          sorted(by_year.keys()),
    }
