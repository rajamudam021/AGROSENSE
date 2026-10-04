"""
Feature 19: Crop Production Anomaly Detection
Dataset: archive (38)/APY.csv — 345,657 rows
Columns: State, District, Crop, Crop_Year, Season, Area, Production, Yield
Approach: Z-score per (State, District, Crop) group; flag |Z| > 2 as anomalies.
"""
import os
import csv
import math
from functools import lru_cache
from collections import defaultdict

_APY_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (38)', 'APY.csv'
)


def _mean_std(vals):
    n = len(vals)
    if n == 0:
        return 0.0, 0.0
    m = sum(vals) / n
    if n == 1:
        return m, 0.0
    var = sum((v - m) ** 2 for v in vals) / (n - 1)
    return m, math.sqrt(var)


@lru_cache(maxsize=1)
def load_apy_index():
    """
    Load APY.csv and build an in-memory index.
    Returns:
      {
        'rows':       list of row dicts,
        'states':     sorted list of state names,
        'crops':      sorted list of crop names,
        'by_state':   {state: {crop: [rows]}},
      }
    """
    if not os.path.exists(_APY_PATH):
        return {'error': 'APY dataset not found', 'states': [], 'crops': []}

    rows = []
    by_state = defaultdict(lambda: defaultdict(list))

    with open(_APY_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalise column names (strip whitespace) to handle trailing spaces
        fieldnames_stripped = {k: k.strip() for k in (reader.fieldnames or [])}
        for row in reader:
            row_s = {fieldnames_stripped.get(k, k.strip()): (v.strip() if isinstance(v, str) else v)
                     for k, v in row.items()}
            try:
                state    = row_s.get('State', '')
                district = row_s.get('District', '')
                crop     = row_s.get('Crop', '')
                year     = int(float(row_s['Crop_Year']))
                yld_raw  = row_s.get('Yield', '')
                area_raw = row_s.get('Area', '')
                prod_raw = row_s.get('Production', '')
                yld  = float(yld_raw)  if yld_raw  else None
                area = float(area_raw) if area_raw else None
                prod = float(prod_raw) if prod_raw else None
                if not state or not district or not crop:
                    continue
            except (ValueError, KeyError, TypeError):
                continue

            if yld is None or yld < 0:
                continue

            r = {
                'state': state, 'district': district, 'crop': crop,
                'year': year, 'yield': yld, 'area': area, 'production': prod,
                'season': row.get('Season', '').strip(),
            }
            rows.append(r)
            by_state[state][crop].append(r)

    # Convert defaultdicts to plain dicts for pickling safety
    plain_by_state = {s: dict(c) for s, c in by_state.items()}

    return {
        'rows':     rows,
        'states':   sorted(plain_by_state.keys()),
        'crops':    sorted(set(r['crop'] for r in rows)),
        'by_state': plain_by_state,
    }


def detect_anomalies(state=None, crop=None, threshold=2.0, top_n=30):
    """
    Detect anomalous yield records.

    Parameters
    ----------
    state : str | None  — filter to a specific state (None = all India)
    crop  : str | None  — filter to a specific crop  (None = all crops)
    threshold : float   — |Z-score| cutoff (default 2.0 ≈ top ~5%)
    top_n : int         — return at most this many anomalies

    Returns
    -------
    (anomalies_list, summary_dict, error_str)
    anomalies_list: sorted by |Z| descending, each item has:
      state, district, crop, year, yield, z_score, pct_deviation,
      group_mean, group_std, direction ('crash' | 'spike')
    """
    data = load_apy_index()
    if 'error' in data:
        return [], {}, data['error']

    # ── Filter rows ──────────────────────────────────────────────
    if state and crop:
        grp_map = {(state, crop): data['by_state'].get(state, {}).get(crop, [])}
    elif state:
        grp_map = {(state, c): rows for c, rows in data['by_state'].get(state, {}).items()}
    elif crop:
        grp_map = {}
        for st, crops_dict in data['by_state'].items():
            if crop in crops_dict:
                grp_map[(st, crop)] = crops_dict[crop]
    else:
        grp_map = {}
        for st, crops_dict in data['by_state'].items():
            for c, rows in crops_dict.items():
                grp_map[(st, c)] = rows

    # ── Z-score per (state, district, crop) ─────────────────────
    # Group further by district within each state+crop
    dist_groups = defaultdict(list)
    for (st, cr), rows in grp_map.items():
        for r in rows:
            dist_groups[(st, r['district'], cr)].append(r)

    anomalies = []
    for (st, dist, cr), g_rows in dist_groups.items():
        if len(g_rows) < 3:        # need enough points for meaningful Z
            continue
        yields = [r['yield'] for r in g_rows]
        mu, sigma = _mean_std(yields)
        if sigma < 1e-6:
            continue
        for r in g_rows:
            z = (r['yield'] - mu) / sigma
            if abs(z) >= threshold:
                pct = round((r['yield'] - mu) / mu * 100, 1) if mu else 0
                anomalies.append({
                    'state':       st,
                    'district':    dist,
                    'crop':        cr,
                    'year':        r['year'],
                    'season':      r['season'],
                    'yield':       round(r['yield'], 3),
                    'group_mean':  round(mu, 3),
                    'group_std':   round(sigma, 3),
                    'z_score':     round(z, 2),
                    'abs_z':       round(abs(z), 2),
                    'pct_dev':     pct,
                    'direction':   'crash' if z < 0 else 'spike',
                    'area':        round(r['area'], 1) if r['area'] else None,
                })

    # Sort by |Z| descending
    anomalies.sort(key=lambda a: a['abs_z'], reverse=True)
    anomalies = anomalies[:top_n]

    total_rows = sum(len(v) for v in grp_map.values())
    summary = {
        'total_rows':    total_rows,
        'anomaly_count': len(anomalies),
        'crash_count':   sum(1 for a in anomalies if a['direction'] == 'crash'),
        'spike_count':   sum(1 for a in anomalies if a['direction'] == 'spike'),
        'threshold':     threshold,
    }
    return anomalies, summary, None


def get_yield_trend(state, district, crop):
    """Year-by-year yield for a specific district+crop (for sparklines)."""
    data = load_apy_index()
    rows = [
        r for r in data.get('rows', [])
        if r['state'] == state and r['district'] == district and r['crop'] == crop
    ]
    rows.sort(key=lambda r: r['year'])
    return [{'year': r['year'], 'yield': round(r['yield'], 3)} for r in rows]


def get_filter_options():
    """Return (states, crops) for dropdown population."""
    data = load_apy_index()
    return data.get('states', []), data.get('crops', [])
