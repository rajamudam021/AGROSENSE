"""
Pesticide Usage vs Yield Correlation Analysis
Datasets: pesticides.csv + yield_df.csv + rainfall.csv + temp.csv
No ML model needed — pure statistical analysis with correlation metrics.
"""
import os
import csv
import json
from functools import lru_cache

DS = os.path.join(os.path.dirname(__file__), '..', '..', 'datasets', 'archive (23)')

PEST_PATH    = os.path.join(DS, 'pesticides.csv')
YIELD_PATH   = os.path.join(DS, 'yield_df.csv')    # alternate: archive 33
RAIN_PATH    = os.path.join(DS, 'rainfall.csv')
TEMP_PATH    = os.path.join(DS, 'temp.csv')

# Fall back to archive 33 yield file
YIELD_PATH2  = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (33)', 'yield_df.csv'
)


def _pearson(x_list, y_list):
    """Simple Pearson correlation coefficient."""
    n = len(x_list)
    if n < 3:
        return None
    mx = sum(x_list) / n
    my = sum(y_list) / n
    num = sum((x - mx) * (y - my) for x, y in zip(x_list, y_list))
    dx  = sum((x - mx) ** 2 for x in x_list) ** 0.5
    dy  = sum((y - my) ** 2 for y in y_list) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return round(num / (dx * dy), 4)


@lru_cache(maxsize=1)
def load_pesticide_analysis():
    """
    Merges pesticides + yield_df on (country, year).
    Returns:
    {
      'overall_corr': float,
      'by_crop': {crop: {corr, n, pest_avg, yield_avg, scatter: [{pest, yield, country, year}]}},
      'by_country': {country: {corr, n, pest_avg, yield_avg}},
      'top_positive': [(crop, corr), ...],   # pest helps yield
      'top_negative': [(crop, corr), ...],   # pest hurts yield
      'scatter_all':  [{pest, yield, crop, country, year}, ...],
      'crops': [...],
      'countries': [...],
    }
    """
    # 1. Load pesticides → {(country, year): tonnes}
    pest = {}
    try:
        with open(PEST_PATH, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                country = row.get('Area', '').strip()
                year_s  = row.get('Year', '').strip()
                val_s   = row.get('Value', '').strip()
                try:
                    pest[(country, int(float(year_s)))] = float(val_s)
                except (ValueError, TypeError):
                    pass
    except FileNotFoundError:
        pass

    # 2. Load yield data
    yield_path = YIELD_PATH2 if os.path.exists(YIELD_PATH2) else YIELD_PATH
    yield_rows = []
    try:
        with open(yield_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    country = row.get('Area', '').strip()
                    crop    = row.get('Item', '').strip()
                    year    = int(float(row.get('Year', 0)))
                    yld     = float(row.get('hg/ha_yield', 0)) / 10  # → kg/ha
                    rain    = float(row.get('average_rain_fall_mm_per_year', 0) or 0)
                    temp    = float(row.get('avg_temp', 0) or 0)
                    p_tonnes = pest.get((country, year), None)
                    if p_tonnes is not None and yld > 0:
                        yield_rows.append({
                            'country': country,
                            'crop':    crop,
                            'year':    year,
                            'yield':   yld,
                            'pest':    p_tonnes,
                            'rain':    rain,
                            'temp':    temp,
                        })
                except (ValueError, TypeError):
                    pass
    except FileNotFoundError:
        return {}

    if not yield_rows:
        return {}

    # 3. Overall correlation
    all_x = [r['pest'] for r in yield_rows]
    all_y = [r['yield'] for r in yield_rows]
    overall_corr = _pearson(all_x, all_y)

    # 4. By crop
    by_crop_data = {}
    for row in yield_rows:
        by_crop_data.setdefault(row['crop'], []).append(row)

    by_crop = {}
    for crop, rows in by_crop_data.items():
        px = [r['pest']  for r in rows]
        py = [r['yield'] for r in rows]
        corr = _pearson(px, py)
        # Keep up to 80 scatter points per crop
        scatter = [{'pest': r['pest'], 'yield': r['yield'],
                    'country': r['country'], 'year': r['year']}
                   for r in rows[:80]]
        by_crop[crop] = {
            'corr':      corr,
            'n':         len(rows),
            'pest_avg':  round(sum(px) / len(px), 1),
            'yield_avg': round(sum(py) / len(py), 1),
            'scatter':   scatter,
        }

    # 5. By country
    by_country_data = {}
    for row in yield_rows:
        by_country_data.setdefault(row['country'], []).append(row)

    by_country = {}
    for country, rows in by_country_data.items():
        if len(rows) < 5:
            continue
        px = [r['pest']  for r in rows]
        py = [r['yield'] for r in rows]
        corr = _pearson(px, py)
        by_country[country] = {
            'corr':      corr,
            'n':         len(rows),
            'pest_avg':  round(sum(px) / len(px), 1),
            'yield_avg': round(sum(py) / len(py), 1),
        }

    # 6. Sorted by correlation
    crop_corrs = [(c, d['corr']) for c, d in by_crop.items() if d['corr'] is not None]
    top_positive = sorted(crop_corrs, key=lambda x: x[1], reverse=True)[:8]
    top_negative = sorted(crop_corrs, key=lambda x: x[1])[:8]

    # 7. Global scatter (limit to 2000 points for chart performance)
    import random
    random.seed(42)
    scatter_sample = random.sample(yield_rows, min(2000, len(yield_rows)))
    scatter_all = [{
        'pest':    r['pest'],
        'yield':   r['yield'],
        'crop':    r['crop'],
        'country': r['country'],
        'year':    r['year'],
    } for r in scatter_sample]

    return {
        'overall_corr':  overall_corr,
        'by_crop':       by_crop,
        'by_country':    by_country,
        'top_positive':  top_positive,
        'top_negative':  top_negative,
        'scatter_all':   scatter_all,
        'crops':         sorted(by_crop.keys()),
        'countries':     sorted(by_country.keys()),
        'total_records': len(yield_rows),
    }


def get_crop_scatter(crop):
    """Return scatter data for a specific crop."""
    data = load_pesticide_analysis()
    if not data:
        return []
    cd = data.get('by_crop', {}).get(crop, {})
    return cd.get('scatter', [])


def get_country_comparison(crop):
    """Countries ranked by avg pesticide use vs avg yield for a crop."""
    data = load_pesticide_analysis()
    if not data:
        return []
    by_crop = data.get('by_crop', {}).get(crop, {})
    return by_crop
