"""
Feature 20: Multi-crop Portfolio Optimizer
Datasets:
  - archive (37)/datafile (1).csv — Crop cost & yield data (49 rows)
  - MARKET_PRICES from data.py for revenue calculation
Approach: Greedy profit-maximization with diversification constraint.
"""
import os
import csv
from functools import lru_cache

_COST_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (37)', 'datafile (1).csv'
)

# Market prices (₹/quintal) for crops in the cost dataset.
# Crops in the CSV use uppercase ICAR names; mapped to MSP/market rates.
_PRICE_MAP = {
    'ARHAR':      7200,   # Pigeonpeas
    'BAJRA':      2500,   # Pearl millet
    'BARLEY':     1635,
    'COTTON':     6620,
    'GRAM':       5400,   # Chickpea
    'GROUNDNUT':  5800,
    'JOWAR':      3180,   # Sorghum
    'JUTE':       4300,
    'LINSEED':    6600,
    'MAIZE':      1870,
    'MOONG':      7500,   # Mungbean
    'MUSTARD':    5600,
    'NIGER':      7000,
    'PADDY':      2183,   # Rice MSP
    'RAGI':       3846,
    'RAPESEED':   5600,
    'RICE':       2183,
    'SAFFLOWER':  5800,
    'SESAMUM':    8635,
    'SOYBEAN':    4600,
    'SUGARCANE':   360,   # ₹/quintal (state-advised)
    'SUNFLOWER':  6400,
    'WHEAT':      2275,
    'URAD':       7000,   # Blackgram
}

# Risk profile: 1=low risk (stable demand), 2=medium, 3=high risk
_RISK_MAP = {
    'PADDY': 1, 'RICE': 1, 'WHEAT': 1, 'MAIZE': 1, 'BAJRA': 1, 'JOWAR': 1,
    'GRAM': 1, 'ARHAR': 2, 'MOONG': 2, 'URAD': 2,
    'GROUNDNUT': 2, 'SOYBEAN': 2, 'MUSTARD': 2, 'RAPESEED': 2,
    'COTTON': 3, 'SUGARCANE': 1, 'JUTE': 2,
    'SUNFLOWER': 2, 'SAFFLOWER': 3, 'SESAMUM': 3, 'NIGER': 3,
    'RAGI': 1, 'BARLEY': 1, 'LINSEED': 2,
}

# Category labels
_CATEGORY = {
    'PADDY': 'Cereal', 'RICE': 'Cereal', 'WHEAT': 'Cereal',
    'MAIZE': 'Cereal', 'BAJRA': 'Cereal', 'JOWAR': 'Cereal',
    'RAGI': 'Cereal', 'BARLEY': 'Cereal',
    'GRAM': 'Pulse', 'ARHAR': 'Pulse', 'MOONG': 'Pulse',
    'URAD': 'Pulse', 'LINSEED': 'Oilseed',
    'GROUNDNUT': 'Oilseed', 'SOYBEAN': 'Oilseed', 'MUSTARD': 'Oilseed',
    'RAPESEED': 'Oilseed', 'SUNFLOWER': 'Oilseed', 'SAFFLOWER': 'Oilseed',
    'SESAMUM': 'Oilseed', 'NIGER': 'Oilseed',
    'COTTON': 'Cash Crop', 'SUGARCANE': 'Cash Crop', 'JUTE': 'Cash Crop',
}


@lru_cache(maxsize=1)
def load_cost_data():
    """Load datafile (1).csv and compute per-crop economics."""
    if not os.path.exists(_COST_PATH):
        return {'error': 'Cost dataset not found', 'crops': []}

    # Aggregate by crop (average across states)
    agg = {}   # crop -> {cost_sum, yield_sum, count}
    with open(_COST_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        # Strip all column names (they may have backtick instead of ₹ or trailing spaces)
        col_map = {}
        for k in (reader.fieldnames or []):
            clean = k.strip()
            col_map[k] = clean
        for row in reader:
            row_s = {col_map.get(k, k.strip()): (v.strip() if isinstance(v, str) else v)
                     for k, v in row.items()}
            crop = row_s.get('Crop', '').strip().upper()
            if not crop:
                continue
            try:
                # Column names use backtick instead of ₹ sign
                cost_c2  = None
                yld_qpha = None
                for k, v in row_s.items():
                    kl = k.lower()
                    if 'c2' in kl and 'cultivation' in kl and v:
                        try: cost_c2 = float(v.replace(',', ''))
                        except ValueError: pass
                    elif 'a2' in kl and 'cultivation' in kl and cost_c2 is None and v:
                        try: cost_c2 = float(v.replace(',', ''))
                        except ValueError: pass
                    elif 'quintal' in kl and 'hectare' in kl.replace('/', '') and v:
                        try: yld_qpha = float(v.replace(',', ''))
                        except ValueError: pass
                if cost_c2 is None or yld_qpha is None:
                    continue
            except (ValueError, TypeError):
                continue
            if crop not in agg:
                agg[crop] = {'cost': 0.0, 'yield': 0.0, 'n': 0}
            agg[crop]['cost']  += cost_c2
            agg[crop]['yield'] += yld_qpha
            agg[crop]['n']     += 1

    crops = []
    for crop, vals in agg.items():
        n     = vals['n']
        cost  = vals['cost']  / n   # ₹/ha
        yld   = vals['yield'] / n   # quintal/ha
        price = _PRICE_MAP.get(crop, 3000)  # ₹/quintal
        rev   = yld * price
        profit = rev - cost
        roi    = round(profit / cost * 100, 1) if cost > 0 else 0

        crops.append({
            'crop':       crop,
            'cost_ha':    round(cost, 0),      # ₹/ha cultivation
            'yield_qha':  round(yld, 2),        # quintal/ha
            'price_q':    price,                # ₹/quintal
            'revenue_ha': round(rev, 0),        # ₹/ha
            'profit_ha':  round(profit, 0),     # ₹/ha
            'roi':        roi,                  # %
            'risk':       _RISK_MAP.get(crop, 2),
            'category':   _CATEGORY.get(crop, 'Other'),
        })

    crops.sort(key=lambda c: c['profit_ha'], reverse=True)
    return {'crops': crops}


_ACRES_TO_HA = 0.404686


def optimize_portfolio(farm_acres, budget_inr, risk_pref='medium', max_crops=4):
    """
    Find the optimal crop mix for given constraints.

    Parameters
    ----------
    farm_acres  : float — total farm size in acres
    budget_inr  : float — total cultivation budget (₹)
    risk_pref   : 'low' | 'medium' | 'high'
    max_crops   : int   — maximum number of different crops to grow

    Returns
    -------
    (result_dict, error_str)
    """
    data = load_cost_data()
    if 'error' in data:
        return None, data['error']

    farm_ha = farm_acres * _ACRES_TO_HA

    # Risk filter
    max_risk = {'low': 1, 'medium': 2, 'high': 3}.get(risk_pref, 2)
    eligible = [c for c in data['crops'] if c['risk'] <= max_risk and c['profit_ha'] > 0]

    if not eligible:
        return None, 'No profitable crops match your risk preference.'

    # ── Greedy allocation with diversification ────────────────────────────
    # Rule: no single crop > 60% of farm area
    max_single_ha = farm_ha * 0.60
    remaining_ha  = farm_ha
    remaining_bud = budget_inr
    portfolio     = []

    for crop in eligible:
        if len(portfolio) >= max_crops:
            break
        if remaining_ha <= 0.01 or remaining_bud <= 0:
            break

        # Max area affordable by budget
        affordable_ha = remaining_bud / crop['cost_ha'] if crop['cost_ha'] > 0 else remaining_ha
        alloc_ha = min(remaining_ha, max_single_ha, affordable_ha)
        if alloc_ha < 0.05:   # less than 0.05 ha → skip
            continue

        cost_alloc   = alloc_ha * crop['cost_ha']
        rev_alloc    = alloc_ha * crop['revenue_ha']
        profit_alloc = alloc_ha * crop['profit_ha']

        portfolio.append({
            'crop':        crop['crop'],
            'category':    crop['category'],
            'alloc_ha':    round(alloc_ha, 3),
            'alloc_acres': round(alloc_ha / _ACRES_TO_HA, 2),
            'alloc_pct':   round(alloc_ha / farm_ha * 100, 1),
            'cost':        round(cost_alloc, 0),
            'revenue':     round(rev_alloc, 0),
            'profit':      round(profit_alloc, 0),
            'roi':         crop['roi'],
            'risk':        crop['risk'],
            'price_q':     crop['price_q'],
            'yield_qha':   crop['yield_qha'],
            'expected_yield_q': round(alloc_ha * crop['yield_qha'], 1),
        })
        remaining_ha  -= alloc_ha
        remaining_bud -= cost_alloc

    if not portfolio:
        return None, 'Budget too small to cultivate any crop with selected risk level.'

    total_cost   = sum(p['cost']   for p in portfolio)
    total_rev    = sum(p['revenue'] for p in portfolio)
    total_profit = sum(p['profit'] for p in portfolio)
    used_ha      = sum(p['alloc_ha'] for p in portfolio)
    overall_roi  = round(total_profit / total_cost * 100, 1) if total_cost else 0

    # Break-even area
    break_even_ha = total_cost / (total_rev / used_ha) if (used_ha > 0 and total_rev > 0) else None

    # Risk label
    risk_label = {'low': 'Conservative', 'medium': 'Balanced', 'high': 'Aggressive'}.get(risk_pref, 'Balanced')

    return {
        'portfolio':     portfolio,
        'farm_ha':       round(farm_ha, 3),
        'farm_acres':    farm_acres,
        'used_ha':       round(used_ha, 3),
        'used_acres':    round(used_ha / _ACRES_TO_HA, 2),
        'total_cost':    round(total_cost, 0),
        'total_revenue': round(total_rev, 0),
        'total_profit':  round(total_profit, 0),
        'overall_roi':   overall_roi,
        'risk_pref':     risk_pref,
        'risk_label':    risk_label,
        'break_even_ha': round(break_even_ha, 2) if break_even_ha else None,
        'budget_used_pct': round(total_cost / budget_inr * 100, 1) if budget_inr else 0,
        'all_crops':     data['crops'],   # for "all options" table
    }, None


def get_all_crops():
    """Return all crop economics for the reference table."""
    data = load_cost_data()
    return data.get('crops', [])
