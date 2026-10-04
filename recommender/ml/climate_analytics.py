"""
Feature 18: Climate Impact on Yield Forecasting
Dataset: archive (33)/yield_df.csv — 28,242 rows
Columns: Area, Item, Year, hg/ha_yield, average_rain_fall_mm_per_year, pesticides_tonnes, avg_temp
Approach: Pure-Python linear regression for trend + extrapolation to 2030/2050.
"""
import os
import csv
from functools import lru_cache

_DATA_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'datasets',
    'archive (33)', 'yield_df.csv'
)


@lru_cache(maxsize=1)
def load_climate_yield_data():
    """Load yield_df.csv; return structured dict cached in memory."""
    if not os.path.exists(_DATA_PATH):
        return {'error': 'Dataset not found', 'rows': [], 'countries': [], 'crops': []}

    rows = []
    with open(_DATA_PATH, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    'country':  row['Area'].strip(),
                    'crop':     row['Item'].strip(),
                    'year':     int(float(row['Year'])),
                    'yield_hg': float(row['hg/ha_yield']),
                    'rainfall': float(row['average_rain_fall_mm_per_year']) if row.get('average_rain_fall_mm_per_year') else None,
                    'temp':     float(row['avg_temp']) if row.get('avg_temp') else None,
                })
            except (ValueError, KeyError, TypeError):
                continue

    countries = sorted(set(r['country'] for r in rows))
    crops     = sorted(set(r['crop']    for r in rows))
    return {'rows': rows, 'countries': countries, 'crops': crops}


def _linreg(xs, ys):
    """Ordinary least-squares linear regression. Returns (slope, intercept, r²)."""
    n = len(xs)
    if n < 2:
        return 0.0, (ys[0] if ys else 0.0), 0.0
    sx  = sum(xs);  sy  = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sxx = sum(x * x for x in xs)
    denom = n * sxx - sx * sx
    if denom == 0:
        return 0.0, sy / n, 0.0
    slope     = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    y_mean = sy / n
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    y_pred = [slope * x + intercept for x in xs]
    ss_res = sum((y - yp) ** 2 for y, yp in zip(ys, y_pred))
    r2 = max(0.0, 1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
    return slope, intercept, r2


def _pearson(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n;  my = sum(ys) / n
    num  = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dxsq = sum((x - mx) ** 2 for x in xs)
    dysq = sum((y - my) ** 2 for y in ys)
    denom = (dxsq * dysq) ** 0.5
    return num / denom if denom > 1e-10 else 0.0


def get_climate_forecast(country, crop):
    """
    Return climate-yield forecast for a country+crop pair.
    Returns (result_dict, error_str).  One of them will be None.
    """
    data = load_climate_yield_data()
    if 'error' in data:
        return None, data['error']

    rows = [r for r in data['rows'] if r['country'] == country and r['crop'] == crop]
    if len(rows) < 3:
        return None, f'Insufficient data for {crop} in {country} (need ≥ 3 data points).'

    rows.sort(key=lambda r: r['year'])
    years  = [r['year']     for r in rows]
    yields = [r['yield_hg'] for r in rows]
    temp_pairs = [(r['year'], r['temp']) for r in rows if r['temp'] is not None]

    # --- Yield trend ---
    y_slope, y_intercept, y_r2 = _linreg(years, yields)
    last_year = max(years)
    baseline  = y_slope * last_year + y_intercept

    forecast_2030 = max(0.0, y_slope * 2030 + y_intercept)
    forecast_2050 = max(0.0, y_slope * 2050 + y_intercept)

    pct_2030 = round((forecast_2030 - baseline) / baseline * 100, 1) if baseline else 0.0
    pct_2050 = round((forecast_2050 - baseline) / baseline * 100, 1) if baseline else 0.0

    # --- Temperature trend ---
    temp_result = {}
    if len(temp_pairs) >= 3:
        t_yrs  = [p[0] for p in temp_pairs]
        t_vals = [p[1] for p in temp_pairs]
        t_slope, t_intercept, _ = _linreg(t_yrs, t_vals)
        cur_temp   = t_slope * last_year + t_intercept
        temp_2030  = t_slope * 2030     + t_intercept
        temp_2050  = t_slope * 2050     + t_intercept
        corr       = _pearson(t_vals, [r['yield_hg'] for r in rows if r['temp'] is not None])
        temp_result = {
            'slope':       round(t_slope * 10, 3),   # °C per decade
            'current':     round(cur_temp, 1),
            'proj_2030':   round(temp_2030, 1),
            'proj_2050':   round(temp_2050, 1),
            'delta_2050':  round(temp_2050 - cur_temp, 1),
            'corr':        round(corr, 3),
            'corr_label':  (
                'strong positive' if corr > 0.5 else
                'moderate positive' if corr > 0.2 else
                'strong negative' if corr < -0.5 else
                'moderate negative' if corr < -0.2 else
                'weak'
            ),
        }

    # --- Historical data for chart ---
    hist = [
        {
            'year':  r['year'],
            'yield': round(r['yield_hg'], 0),
            'temp':  round(r['temp'], 2) if r['temp'] is not None else None,
            'trend': round(y_slope * r['year'] + y_intercept, 0),
        }
        for r in rows
    ]

    # Append forecast points
    hist_chart = hist + [
        {'year': 2030, 'yield': None, 'temp': temp_result.get('proj_2030'), 'trend': round(forecast_2030, 0)},
        {'year': 2050, 'yield': None, 'temp': temp_result.get('proj_2050'), 'trend': round(forecast_2050, 0)},
    ]

    return {
        'country':        country,
        'crop':           crop,
        'years_range':    f'{min(years)}–{max(years)}',
        'data_points':    len(rows),
        # Trend
        'y_slope':        round(y_slope, 1),
        'y_r2':           round(y_r2, 3),
        'trend_dir':      'improving' if y_slope > 50 else ('declining' if y_slope < -50 else 'stable'),
        # Forecast
        'baseline_hg':    round(baseline, 0),
        'baseline_t':     round(baseline / 10000, 2),
        'forecast_2030_hg': round(forecast_2030, 0),
        'forecast_2030_t':  round(forecast_2030 / 10000, 2),
        'forecast_2050_hg': round(forecast_2050, 0),
        'forecast_2050_t':  round(forecast_2050 / 10000, 2),
        'pct_change_2030':  pct_2030,
        'pct_change_2050':  pct_2050,
        # Temperature
        'temp':           temp_result,
        # Chart
        'chart_data':     hist_chart,
    }, None


def get_options():
    """Return available countries and crops for the form dropdowns."""
    data = load_climate_yield_data()
    return data.get('countries', []), data.get('crops', [])
