import json
import urllib.request
import urllib.parse
import urllib.error

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Avg, Count

from .models import UserProfile, Prediction
from .ml.loader import predict_top3, load_bundle
from .data import (
    CROP_DATA,
    MARKET_PRICES,
    KHARIF_CROPS,
    RABI_CROPS,
    ZAID_CROPS,
    PERENNIAL_CROPS,
    calculate_soil_health,
    get_current_season,
    get_fertilizer_recommendation,
    estimate_yield_profit,
)


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

def home(request):
    season = get_current_season()
    return render(request, 'home.html', {'season': season})


# ---------------------------------------------------------------------------
# AUTH VIEWS
# ---------------------------------------------------------------------------

def signup_view(request):
    if request.method == 'POST':
        name     = request.POST.get('name', '').strip()
        phone    = request.POST.get('phone', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not name or not email or not phone or not password:
            messages.error(request, 'Please fill all required fields.')
            return redirect('signup')

        if len(password) < 6:
            messages.error(request, 'Password should be at least 6 characters.')
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, 'Account already exists with this email.')
            return redirect('signup')

        user = User.objects.create_user(username=email, password=password)

        if ' ' in name:
            first, last = name.split(' ', 1)
        else:
            first, last = name, ''

        user.first_name = first
        user.last_name  = last
        user.email      = email
        user.save()

        UserProfile.objects.create(user=user, phone=phone)

        login(request, user)
        messages.success(request, 'Account created successfully. Welcome to AgroSense!')
        return redirect('predict')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)

        if not user:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

        login(request, user)
        messages.success(request, 'Logged in successfully!')
        return redirect('predict')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')


# ---------------------------------------------------------------------------
# PREDICT VIEW
# ---------------------------------------------------------------------------

@login_required(login_url='login')
def predict_view(request):
    feature_order = load_bundle()['feature_cols']
    result = None
    last_data = None

    if request.method == 'POST':
        try:
            N           = float(request.POST.get('N', 0))
            P           = float(request.POST.get('P', 0))
            K           = float(request.POST.get('K', 0))
            temperature = float(request.POST.get('temperature', 25))
            humidity    = float(request.POST.get('humidity', 50))
            ph          = float(request.POST.get('ph', 6.5))
            rainfall    = float(request.POST.get('rainfall', 100))
            city        = request.POST.get('city', '').strip()
            land_size   = request.POST.get('land_size', '').strip()
            land_size   = float(land_size) if land_size else 1.0
        except (ValueError, TypeError):
            messages.error(request, 'Invalid input values. Please enter valid numbers.')
            return redirect('predict')

        last_data = {
            'N': N, 'P': P, 'K': K,
            'temperature': temperature, 'humidity': humidity,
            'ph': ph, 'rainfall': rainfall,
            'city': city, 'land_size': land_size,
        }

        # --- ML prediction ---
        feature_dict = {
            'N': N, 'P': P, 'K': K,
            'temperature': temperature,
            'humidity': humidity,
            'ph': ph,
            'rainfall': rainfall,
        }

        try:
            top3 = predict_top3(feature_dict)
        except Exception as e:
            messages.error(request, f'Prediction error: {e}')
            return render(request, 'predict.html', {'feature_order': feature_order, 'last_data': last_data})

        top_crop   = top3[0]['crop'] if top3 else 'Unknown'
        top2_crop  = top3[1]['crop'] if len(top3) > 1 else ''
        top3_crop  = top3[2]['crop'] if len(top3) > 2 else ''

        # --- Soil health ---
        soil_health = calculate_soil_health(N, P, K, ph)

        # --- Crop data lookup ---
        crop_key = top_crop.lower().replace(' ', '')
        # Try exact match first, then strip spaces
        crop_info = CROP_DATA.get(top_crop.lower(), CROP_DATA.get(crop_key, {}))

        fertilizer_recs = get_fertilizer_recommendation(top_crop, N, P, K)
        irrigation_info = crop_info.get('irrigation', {
            'frequency': 'As required',
            'notes': 'Monitor crop water requirements based on weather.',
        })
        rotation_info   = crop_info.get('rotation', [])
        timeline        = crop_info.get('timeline', [])
        season_info     = get_current_season()

        # --- Yield / profit estimation ---
        profit_estimate = estimate_yield_profit(top_crop, land_size)

        # --- Save to DB ---
        try:
            pred_obj = Prediction.objects.create(
                user            = request.user,
                N               = N,
                P               = P,
                K               = K,
                temperature     = temperature,
                humidity        = humidity,
                ph              = ph,
                rainfall        = rainfall,
                predicted_label = top_crop,
                city            = city,
                confidence_scores = json.dumps(top3),
                soil_health_score = soil_health['score'],
                land_size       = land_size,
                top2_crop       = top2_crop,
                top3_crop       = top3_crop,
            )
        except Exception as e:
            messages.warning(request, f'Prediction made but could not be saved: {e}')
            pred_obj = None

        # --- Variety recommendations ---
        try:
            varieties = get_varieties_for_crop(top_crop)
        except Exception:
            varieties = []

        result = {
            'top3'           : top3,
            'top_crop'       : top_crop,
            'soil_health'    : soil_health,
            'fertilizer_recs': fertilizer_recs,
            'irrigation'     : irrigation_info,
            'rotation'       : rotation_info,
            'timeline'       : timeline,
            'season_info'    : season_info,
            'profit'         : profit_estimate,
            'city'           : city,
            'pred_id'        : pred_obj.pk if pred_obj else None,
            'crop_season'    : crop_info.get('season', 'N/A'),
            'tips'           : crop_info.get('tips', []),
            'varieties'      : varieties,
        }

        messages.success(request, f'Recommendation complete! Top crop: {top_crop}')

    return render(request, 'predict.html', {
        'feature_order': feature_order,
        'result'       : result,
        'last_data'    : last_data,
    })


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@login_required(login_url='login')
def dashboard_view(request):
    if request.user.is_staff:
        predictions = Prediction.objects.all()
    else:
        predictions = Prediction.objects.filter(user=request.user)

    total_predictions = predictions.count()
    recent_5          = predictions.select_related('user')[:5]

    # Combined aggregate — single DB query instead of four
    agg = predictions.aggregate(
        avg_n    = Avg('N'),
        avg_p    = Avg('P'),
        avg_k    = Avg('K'),
        avg_soil = Avg('soil_health_score'),
    )
    avg_n    = agg['avg_n']    or 0
    avg_p    = agg['avg_p']    or 0
    avg_k    = agg['avg_k']    or 0
    avg_soil = agg['avg_soil'] or 0

    # Best crop (most predicted)
    crop_counts = predictions.values('predicted_label').annotate(cnt=Count('predicted_label')).order_by('-cnt')
    best_crop   = crop_counts[0]['predicted_label'] if crop_counts else 'N/A'

    # Days active
    if predictions.exists():
        first  = predictions.last()
        import datetime
        days_active = (datetime.datetime.now(tz=first.created_at.tzinfo) - first.created_at).days + 1
    else:
        days_active = 0

    # Chart data: crop distribution doughnut
    crop_dist_labels = [c['predicted_label'] for c in crop_counts[:8]]
    crop_dist_data   = [c['cnt'] for c in crop_counts[:8]]

    # Chart data: soil health over time (last 10)
    soil_timeline_qs = predictions.order_by('created_at')[:10]
    soil_dates  = [p.created_at.strftime('%b %d') for p in soil_timeline_qs]
    soil_scores = [p.soil_health_score or 0 for p in soil_timeline_qs]

    # Latest prediction top3 chart
    latest_pred = predictions.first()
    latest_top3_labels = []
    latest_top3_data   = []
    if latest_pred:
        for item in latest_pred.get_confidence_scores():
            latest_top3_labels.append(item.get('crop', ''))
            latest_top3_data.append(item.get('probability', 0))

    chart_data = json.dumps({
        'npk'            : {'N': round(avg_n, 1), 'P': round(avg_p, 1), 'K': round(avg_k, 1)},
        'crop_dist'      : {'labels': crop_dist_labels, 'data': crop_dist_data},
        'soil_timeline'  : {'labels': soil_dates, 'data': soil_scores},
        'latest_top3'    : {'labels': latest_top3_labels, 'data': latest_top3_data},
    })

    return render(request, 'dashboard.html', {
        'total_predictions': total_predictions,
        'best_crop'        : best_crop,
        'avg_soil'         : round(avg_soil, 1),
        'days_active'      : days_active,
        'recent_5'         : recent_5,
        'chart_data'       : chart_data,
    })


# ---------------------------------------------------------------------------
# HISTORY
# ---------------------------------------------------------------------------

@login_required(login_url='login')
def history_view(request):
    if request.user.is_staff:
        predictions = Prediction.objects.select_related('user').all()
    else:
        predictions = Prediction.objects.filter(user=request.user)

    paginator = Paginator(predictions, 10)
    page_number = request.GET.get('page', 1)
    page_obj    = paginator.get_page(page_number)

    return render(request, 'history.html', {'page_obj': page_obj})


# ---------------------------------------------------------------------------
# MARKET PRICES
# ---------------------------------------------------------------------------

def market_prices_view(request):
    return render(request, 'market_prices.html', {
        'market_prices': MARKET_PRICES,
    })


# ---------------------------------------------------------------------------
# FARMING TIPS
# ---------------------------------------------------------------------------

def farming_tips_view(request):
    crop_filter = request.GET.get('crop', '').lower()
    if crop_filter and crop_filter in CROP_DATA:
        filtered = {crop_filter: CROP_DATA[crop_filter]}
    else:
        filtered = CROP_DATA

    return render(request, 'farming_tips.html', {
        'crop_data'   : filtered,
        'all_crops'   : sorted(CROP_DATA.keys()),
        'crop_filter' : crop_filter,
    })


# ---------------------------------------------------------------------------
# CROP CALENDAR
# ---------------------------------------------------------------------------

def crop_calendar_view(request):
    crop_filter = request.GET.get('crop', '').lower()
    if crop_filter and crop_filter in CROP_DATA:
        filtered = {crop_filter: CROP_DATA[crop_filter]}
    else:
        filtered = CROP_DATA

    season = get_current_season()

    return render(request, 'crop_calendar.html', {
        'crop_data'  : filtered,
        'all_crops'  : sorted(CROP_DATA.keys()),
        'crop_filter': crop_filter,
        'season'     : season,
        'months'     : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    })


# ---------------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------------

@login_required(login_url='login')
def profile_view(request):
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, phone='')

    predictions   = Prediction.objects.filter(user=user)
    total_preds   = predictions.count()
    avg_soil      = predictions.aggregate(avg=Avg('soil_health_score'))['avg'] or 0
    crop_counts   = predictions.values('predicted_label').annotate(cnt=Count('predicted_label')).order_by('-cnt')
    fav_crop      = crop_counts[0]['predicted_label'] if crop_counts else 'N/A'
    recent_acts   = predictions[:5]

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            name  = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()

            if name:
                if ' ' in name:
                    first, last = name.split(' ', 1)
                else:
                    first, last = name, ''
                user.first_name = first
                user.last_name  = last
                user.save()

            if phone:
                profile.phone = phone
                profile.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')

        elif action == 'change_password':
            old_pw  = request.POST.get('old_password', '')
            new_pw  = request.POST.get('new_password', '')
            conf_pw = request.POST.get('confirm_password', '')

            if not user.check_password(old_pw):
                messages.error(request, 'Current password is incorrect.')
                return redirect('profile')

            if new_pw != conf_pw:
                messages.error(request, 'New passwords do not match.')
                return redirect('profile')

            if len(new_pw) < 6:
                messages.error(request, 'Password must be at least 6 characters.')
                return redirect('profile')

            user.set_password(new_pw)
            user.save()
            login(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')

    return render(request, 'profile.html', {
        'profile'    : profile,
        'total_preds': total_preds,
        'avg_soil'   : round(avg_soil, 1),
        'fav_crop'   : fav_crop,
        'recent_acts': recent_acts,
    })


# ---------------------------------------------------------------------------
# WEATHER API (AJAX)
# ---------------------------------------------------------------------------

def weather_api_view(request):
    city = request.GET.get('city', '').strip()
    if not city:
        return JsonResponse({'error': 'City name is required.'}, status=400)

    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '')
    if not api_key:
        return JsonResponse({
            'error': 'Weather API key not configured. Please add OPENWEATHER_API_KEY to settings.py.',
            'demo': True,
        }, status=200)

    try:
        encoded_city = urllib.parse.quote(city)

        # Step 1: current weather — temperature & humidity
        url = (
            f'https://api.openweathermap.org/data/2.5/weather'
            f'?q={encoded_city}&appid={api_key}&units=metric'
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'AgroSense/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        temperature = data['main']['temp']
        humidity    = data['main']['humidity']
        city_name   = data.get('name', city)
        description = data['weather'][0]['description'] if data.get('weather') else ''

        # Step 2: 5-day / 3-hour forecast — sum all rain slots to get
        # 5-day total, then scale to 30-day monthly estimate.
        rainfall = 0.0
        try:
            forecast_url = (
                f'https://api.openweathermap.org/data/2.5/forecast'
                f'?q={encoded_city}&appid={api_key}&units=metric&cnt=40'
            )
            freq = urllib.request.Request(forecast_url, headers={'User-Agent': 'AgroSense/1.0'})
            with urllib.request.urlopen(freq, timeout=5) as fresp:
                fdata = json.loads(fresp.read().decode())
            # Each slot covers 3 hours; sum all rain volumes
            five_day_rain = sum(
                slot.get('rain', {}).get('3h', 0)
                for slot in fdata.get('list', [])
            )
            # Scale 5-day total → 30-day monthly estimate
            rainfall = five_day_rain * (30 / 5)
        except Exception:
            # Fallback: derive a rough estimate from current humidity
            # (high humidity ≈ wetter climate; ~1 mm per 1 % above 40 %)
            rainfall = max(0.0, (humidity - 40) * 1.5)

        return JsonResponse({
            'temperature': round(temperature, 1),
            'humidity'   : round(humidity, 1),
            'rainfall'   : round(rainfall, 1),
            'city'       : city_name,
            'description': description,
        })

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return JsonResponse({'error': f'City "{city}" not found.'}, status=404)
        return JsonResponse({'error': f'Weather API error: {e.code}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Could not fetch weather data: {str(e)}'}, status=500)


# ---------------------------------------------------------------------------
# AGROMONITORING API (AJAX) — satellite / soil data by lat,lon
# ---------------------------------------------------------------------------

def agromonitoring_api_view(request):
    try:
        lat = float(request.GET.get('lat', ''))
        lon = float(request.GET.get('lon', ''))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Valid lat and lon parameters are required.'}, status=400)

    api_key = getattr(settings, 'AGROMONITORING_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'AgroMonitoring API key not configured.'}, status=200)

    try:
        # Current weather from AgroMonitoring
        weather_url = (
            f'https://api.agromonitoring.com/agro/1.0/weather'
            f'?lat={lat}&lon={lon}&appid={api_key}'
        )
        req = urllib.request.Request(weather_url, headers={'User-Agent': 'AgroSense/1.0'})
        with urllib.request.urlopen(req, timeout=6) as resp:
            weather = json.loads(resp.read().decode())

        # UV index from AgroMonitoring
        uvi = None
        try:
            uv_url = (
                f'https://api.agromonitoring.com/agro/1.0/uvi'
                f'?lat={lat}&lon={lon}&appid={api_key}'
            )
            uv_req = urllib.request.Request(uv_url, headers={'User-Agent': 'AgroSense/1.0'})
            with urllib.request.urlopen(uv_req, timeout=5) as uv_resp:
                uv_data = json.loads(uv_resp.read().decode())
                uvi = uv_data.get('value')
        except Exception:
            pass

        result = {
            'temperature'  : round(weather['main']['temp'] - 273.15, 1),   # Kelvin → °C
            'humidity'     : weather['main']['humidity'],
            'pressure'     : weather['main']['pressure'],
            'wind_speed'   : round(weather.get('wind', {}).get('speed', 0), 1),
            'clouds'       : weather.get('clouds', {}).get('all', 0),
            'description'  : weather['weather'][0]['description'] if weather.get('weather') else '',
            'uv_index'     : uvi,
            'rainfall_1h'  : weather.get('rain', {}).get('1h', 0),
        }
        return JsonResponse(result)

    except urllib.error.HTTPError as e:
        return JsonResponse({'error': f'AgroMonitoring API error: {e.code}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Could not fetch data: {str(e)}'}, status=500)


# ---------------------------------------------------------------------------
# REPORT VIEW
# ---------------------------------------------------------------------------

@login_required(login_url='login')
def report_view(request, pk):
    if request.user.is_staff:
        pred = get_object_or_404(Prediction, pk=pk)
    else:
        pred = get_object_or_404(Prediction, pk=pk, user=request.user)

    top_crop    = pred.predicted_label
    crop_key    = top_crop.lower().replace(' ', '')
    crop_info   = CROP_DATA.get(top_crop.lower(), CROP_DATA.get(crop_key, {}))

    soil_health     = calculate_soil_health(pred.N, pred.P, pred.K, pred.ph)
    fertilizer_recs = get_fertilizer_recommendation(top_crop, pred.N, pred.P, pred.K)
    irrigation_info = crop_info.get('irrigation', {})
    rotation_info   = crop_info.get('rotation', [])
    timeline        = crop_info.get('timeline', [])
    land_size       = pred.land_size or 1.0
    profit_estimate = estimate_yield_profit(top_crop, land_size)
    season_info     = get_current_season()
    top3            = pred.get_confidence_scores()

    return render(request, 'report.html', {
        'pred'           : pred,
        'top3'           : top3,
        'soil_health'    : soil_health,
        'fertilizer_recs': fertilizer_recs,
        'irrigation'     : irrigation_info,
        'rotation'       : rotation_info,
        'timeline'       : timeline,
        'profit'         : profit_estimate,
        'season_info'    : season_info,
        'crop_season'    : crop_info.get('season', 'N/A'),
        'tips'           : crop_info.get('tips', []),
    })

# ═══════════════════════════════════════════════════════════════
# TIER-1 FEATURE VIEWS
# ═══════════════════════════════════════════════════════════════
from .ml.fertilizer_loader import (
    predict_fertilizer, get_soil_types, get_crop_types, FERTILIZER_INFO
)
from .dataset_loaders import (
    get_varieties_for_crop,
    get_cost_for_crop, get_all_cost_crops, get_all_cost_states,
    get_national_trends, get_apy_states, get_apy_crops,
    get_districts_for_state, get_district_benchmark,
    load_tn_data,
)


# ── 1. FERTILIZER ADVISOR ───────────────────────────────────────
def fertilizer_view(request):
    result = None
    error  = None

    soil_types = get_soil_types()
    crop_types = get_crop_types()

    if request.method == 'POST':
        try:
            temperature = float(request.POST.get('temperature', 0))
            humidity    = float(request.POST.get('humidity', 0))
            moisture    = float(request.POST.get('moisture', 0))
            soil_type   = request.POST.get('soil_type', '')
            crop_type   = request.POST.get('crop_type', '')

            top_fert, recommendations = predict_fertilizer(
                temperature, humidity, moisture, soil_type, crop_type
            )

            result = {
                'top_fertilizer':  top_fert,
                'recommendations': recommendations,
                'info':            FERTILIZER_INFO.get(top_fert, {}),
                'inputs': {
                    'temperature': temperature,
                    'humidity':    humidity,
                    'moisture':    moisture,
                    'soil_type':   soil_type,
                    'crop_type':   crop_type,
                },
            }
        except Exception as e:
            error = str(e)

    return render(request, 'fertilizer.html', {
        'result':     result,
        'error':      error,
        'soil_types': soil_types,
        'crop_types': crop_types,
    })


# ── 2. COST CALCULATOR ──────────────────────────────────────────
def cost_calculator_view(request):
    result = None
    all_crops  = get_all_cost_crops()
    all_states = get_all_cost_states()
    selected_crop  = request.GET.get('crop', '')
    selected_state = request.GET.get('state', '')
    land_size      = float(request.GET.get('land_size', 1.0) or 1.0)

    if selected_crop:
        rows = get_cost_for_crop(selected_crop, selected_state or None)
        if rows:
            result = []
            for r in rows:
                y     = r['yield_q_per_ha']
                ca2   = r['cost_a2fl']
                cc2   = r['cost_c2']
                total_cost   = round(cc2 * land_size, 0)
                total_yield  = round(y * land_size * 100, 0)   # quintal → kg
                # rough MSP estimate: cost_per_quintal * yield
                revenue_est  = round(r['cost_per_quintal'] * y * land_size * 1.2, 0)
                profit_est   = round(revenue_est - total_cost, 0)
                result.append({
                    **r,
                    'land_size':    land_size,
                    'total_cost':   total_cost,
                    'total_yield_q':round(y * land_size, 2),
                    'revenue_est':  revenue_est,
                    'profit_est':   profit_est,
                })

    return render(request, 'cost_calculator.html', {
        'result':        result,
        'all_crops':     all_crops,
        'all_states':    all_states,
        'selected_crop': selected_crop,
        'selected_state':selected_state,
        'land_size':     land_size,
    })


# ── 3. DISTRICT BENCHMARK ───────────────────────────────────────
def district_benchmark_view(request):
    states    = get_apy_states()
    all_crops = get_apy_crops()

    selected_state    = request.GET.get('state', '')
    selected_district = request.GET.get('district', '')
    selected_crop     = request.GET.get('crop', '')

    districts = []
    if selected_state:
        districts = get_districts_for_state(selected_state)

    benchmark = None
    if selected_state and selected_district and selected_crop:
        benchmark = get_district_benchmark(selected_state, selected_district, selected_crop)

    return render(request, 'district_benchmark.html', {
        'states':             states,
        'districts':          districts,
        'all_crops':          all_crops,
        'selected_state':     selected_state,
        'selected_district':  selected_district,
        'selected_crop':      selected_crop,
        'benchmark':          benchmark,
    })


# ── 3a. AJAX: get districts for a state ────────────────────────
def ajax_get_districts(request):
    state     = request.GET.get('state', '')
    districts = get_districts_for_state(state) if state else []
    return JsonResponse({'districts': districts})


# ── 4. INDIA PRODUCTION TRENDS ──────────────────────────────────
def trends_view(request):
    all_crops      = get_apy_crops()
    selected_crop  = request.GET.get('crop', all_crops[0] if all_crops else '')
    trend_data     = {}
    if selected_crop:
        trend_data = get_national_trends(selected_crop, top_n_years=20)

    return render(request, 'trends_dashboard.html', {
        'all_crops':     all_crops,
        'selected_crop': selected_crop,
        'trend_json':    json.dumps(trend_data),
    })


# ── 5. TAMIL NADU ANALYTICS ─────────────────────────────────────
def tn_analytics_view(request):
    data = load_tn_data()
    if not data:
        return render(request, 'tn_analytics.html', {'error': 'Data not available'})

    selected_district = request.GET.get('district', '')
    selected_crop     = request.GET.get('crop', '')

    districts    = data.get('districts', [])
    crops        = data.get('crops', [])
    top_districts= data.get('top_districts', [])
    by_district  = data.get('by_district', {})
    by_crop      = data.get('by_crop', {})

    # year_trend from loader: {'labels': [...], 'production': [...]}
    # Convert to flat {year: value} for JS
    raw_yt   = data.get('year_trend', {})
    year_trend = {}
    for y, p in zip(raw_yt.get('labels', []), raw_yt.get('production', [])):
        year_trend[y] = p

    # top_crops from loader: {district: [(crop, avg_prod), ...]}
    # Aggregate across districts → {crop: total_avg_prod}, top 20
    raw_tc = data.get('top_crops', {})
    crop_totals = {}
    for district, ranked in raw_tc.items():
        for crop, prod in ranked:
            crop_totals[crop] = crop_totals.get(crop, 0) + (prod or 0)
    top_crops = dict(sorted(crop_totals.items(), key=lambda x: x[1], reverse=True)[:20])

    # District detail: {crop: avg_prod} flat dict for template
    district_detail = None
    if selected_district:
        raw_dd = by_district.get(selected_district, {})
        district_detail = {
            crop: vals.get('avg_prod', 0)
            for crop, vals in raw_dd.items()
            if vals.get('avg_prod')
        }
        district_detail = dict(sorted(district_detail.items(), key=lambda x: x[1], reverse=True))

    # Crop detail: which districts produce most?
    crop_detail = None
    if selected_crop:
        raw = by_crop.get(selected_crop, {})
        # Get max for progress bar scaling
        crop_detail_list = sorted(
            [(d, p) for d, p in raw.items() if p],
            key=lambda x: x[1], reverse=True
        )[:10]
        max_prod = crop_detail_list[0][1] if crop_detail_list else 1
        crop_detail = [(d, p, round(p / max_prod * 100)) for d, p, *_ in
                       [(d, p) for d, p in crop_detail_list]]

    # Chart: top 10 districts total production
    top_dist_labels  = [d[0] for d in top_districts]
    top_dist_values  = [d[1] for d in top_districts]

    return render(request, 'tn_analytics.html', {
        'districts':         districts,
        'crops':             crops,
        'top_districts':     top_districts,
        'year_trend_json':   json.dumps(year_trend),
        'top_dist_json':     json.dumps({'labels': top_dist_labels, 'values': top_dist_values}),
        'selected_district': selected_district,
        'selected_crop':     selected_crop,
        'district_detail':   district_detail,
        'crop_detail':       crop_detail,
        'top_crops':         top_crops,
    })

# ═══════════════════════════════════════════════════════════════
# TIER-2 FEATURE VIEWS
# ═══════════════════════════════════════════════════════════════
from .ml.yield_model import (
    predict_yield, get_yield_options, load_yield_bundle,
)
from .ml.global_yield_model import (
    predict_global_yield, get_global_yield_options, get_country_benchmarks,
)
from .ml.soybean_model import (
    predict_soybean_disease, get_feature_options, DISEASE_INFO as SOYBEAN_DISEASE_INFO,
)
from .ml.rice_disease_model import (
    predict_rice_disease_from_pil, load_rice_disease_bundle, CLASSES as RICE_CLASSES,
)
from .ml.pesticide_analysis import load_pesticide_analysis


# ── 6. CROP YIELD PREDICTOR ─────────────────────────────────────
def yield_predictor_view(request):
    opts   = get_yield_options()
    result = None
    error  = None
    inputs = {}

    if request.method == 'POST':
        try:
            region    = request.POST.get('region', '')
            soil_type = request.POST.get('soil_type', '')
            crop      = request.POST.get('crop', '')
            rainfall  = float(request.POST.get('rainfall', 0))
            temp      = float(request.POST.get('temperature', 0))
            fert      = request.POST.get('fertilizer_used') == 'on'
            irr       = request.POST.get('irrigation_used') == 'on'
            weather   = request.POST.get('weather', '')
            days      = float(request.POST.get('days_to_harvest', 90))

            inputs = {
                'region': region, 'soil_type': soil_type, 'crop': crop,
                'rainfall': rainfall, 'temperature': temp,
                'fertilizer_used': fert, 'irrigation_used': irr,
                'weather': weather, 'days_to_harvest': days,
            }
            result = predict_yield(
                region, soil_type, crop, rainfall, temp, fert, irr, weather, days
            )
            result['inputs'] = inputs
            result['land_1ha_kg'] = round(result['yield'] * 1000, 0)
        except Exception as e:
            error = str(e)

    return render(request, 'yield_predictor.html', {
        'opts':   opts,
        'result': result,
        'error':  error,
        'inputs': inputs,
    })


# ── 7. GLOBAL YIELD PREDICTOR ───────────────────────────────────
def global_yield_view(request):
    opts   = get_global_yield_options()
    result = None
    error  = None
    benchmarks = []
    inputs = {}

    selected_item = request.GET.get('item', '')

    if request.method == 'POST':
        try:
            area        = request.POST.get('area', '')
            item        = request.POST.get('item', '')
            year        = int(request.POST.get('year', 2010))
            rainfall    = float(request.POST.get('rainfall', 1000))
            pesticides  = float(request.POST.get('pesticides', 50))
            temperature = float(request.POST.get('temperature', 20))

            inputs = {
                'area': area, 'item': item, 'year': year,
                'rainfall': rainfall, 'pesticides': pesticides,
                'temperature': temperature,
            }
            result         = predict_global_yield(area, item, year, rainfall, pesticides, temperature)
            result['inputs'] = inputs
            selected_item  = item
        except Exception as e:
            error = str(e)

    if selected_item:
        benchmarks = get_country_benchmarks(selected_item)

    return render(request, 'global_yield.html', {
        'opts':          opts,
        'result':        result,
        'error':         error,
        'inputs':        inputs,
        'benchmarks':    benchmarks,
        'benchmarks_json': json.dumps(benchmarks[:20]),
        'selected_item': selected_item,
    })


# ── 8. RICE DISEASE DETECTOR ────────────────────────────────────
def rice_disease_view(request):
    result = None
    error  = None
    bundle = load_rice_disease_bundle()
    backend = bundle.get('backend', 'sklearn')
    cv_acc  = bundle.get('cv_acc', bundle.get('val_acc', None))

    if request.method == 'POST' and request.FILES.get('leaf_image'):
        try:
            from PIL import Image
            img_file = request.FILES['leaf_image']
            pil_img  = Image.open(img_file).convert('RGB')
            result   = predict_rice_disease_from_pil(pil_img)
        except Exception as e:
            error = str(e)

    return render(request, 'rice_disease.html', {
        'result':      result,
        'error':       error,
        'backend':     backend,
        'cv_acc':      cv_acc,
        'rice_classes': RICE_CLASSES,
    })


# ── 9. SOYBEAN DISEASE CLASSIFIER ──────────────────────────────
def soybean_disease_view(request):
    opts   = get_feature_options()
    result = None
    error  = None
    submitted = {}

    # Key diagnostic features to surface (subset for UI)
    KEY_FEATURES = [
        'date', 'plant-stand', 'precip', 'temp', 'hail', 'crop-hist',
        'area-damaged', 'severity', 'seed-tmt', 'germination',
        'leaves', 'leafspots-halo', 'leafspots-marg', 'leafspot-size',
        'stem', 'lodging', 'stem-cankers', 'canker-lesion',
        'fruiting-bodies', 'external-decay', 'roots',
    ]

    if request.method == 'POST':
        submitted = {k: v for k, v in request.POST.items() if not k.startswith('csrf')}
        try:
            result = predict_soybean_disease(submitted)
        except Exception as e:
            error = str(e)

    return render(request, 'soybean_disease.html', {
        'opts':         opts,
        'key_features': KEY_FEATURES,
        'result':       result,
        'error':        error,
        'submitted':    submitted,
        'disease_info': SOYBEAN_DISEASE_INFO,
    })


# ── 10. PESTICIDE vs YIELD CORRELATION ─────────────────────────
def pesticide_analysis_view(request):
    data = load_pesticide_analysis()
    if not data:
        return render(request, 'pesticide_analysis.html', {'error': 'Data not available'})

    selected_crop = request.GET.get('crop', '')
    crop_scatter  = []
    crop_stats    = {}

    if selected_crop and selected_crop in data.get('by_crop', {}):
        crop_scatter = data['by_crop'][selected_crop].get('scatter', [])
        crop_stats   = data['by_crop'][selected_crop]

    # Top/bottom 8 crops by correlation strength
    top_pos = data.get('top_positive', [])
    top_neg = data.get('top_negative', [])

    # Country correlations (top 15 by magnitude)
    country_corrs = sorted(
        [(c, d['corr']) for c, d in data.get('by_country', {}).items()
         if d['corr'] is not None],
        key=lambda x: abs(x[1]), reverse=True
    )[:15]

    return render(request, 'pesticide_analysis.html', {
        'data':            data,
        'selected_crop':   selected_crop,
        'crop_scatter_json': json.dumps(crop_scatter),
        'crop_stats':      crop_stats,
        'top_positive':    top_pos,
        'top_negative':    top_neg,
        'country_corrs':   country_corrs,
        'scatter_all_json': json.dumps(data.get('scatter_all', [])[:500]),
        'overall_corr':    data.get('overall_corr'),
        'total_records':   data.get('total_records', 0),
        'crops':           data.get('crops', []),
    })


# ══════════════════════════════════════════════════════════════════════════════
#  TIER-3 VIEWS — Global Analytics & Advanced Tools
# ══════════════════════════════════════════════════════════════════════════════

from .dataset_loaders_t3 import (
    load_fao_data,
    get_fao_crop_timeseries,
    get_fao_continent_timeseries,
    get_rotation_suggestions,
    load_corn_comparison,
    load_food_security,
    _CROP_NPK_FALLBACK,
    _ROTATION_AFTER,
)
from .ml.irrigation_model import (
    predict_irrigation,
    get_irrigation_options,
    load_irrigation_bundle,
)


# ── T3-1. GLOBAL AGRICULTURE COMPARISON ────────────────────────────────────
def global_agriculture_view(request):
    try:
        fao = load_fao_data()
    except Exception as e:
        return render(request, 'global_agriculture.html', {'error': str(e)})

    all_items = fao['items']
    selected_item    = request.GET.get('item', 'Wheat')
    selected_element = request.GET.get('element', 'Production')

    if selected_item not in all_items:
        selected_item = all_items[0] if all_items else 'Wheat'

    element_choices = ['Production', 'Yield', 'Area harvested']
    if selected_element not in element_choices:
        selected_element = 'Production'

    # Continental timeseries
    continent_ts = get_fao_continent_timeseries(selected_item, selected_element)
    years = sorted({yr for ts in continent_ts.values() for yr in ts.keys()})

    continent_json = {}
    for continent, ts in continent_ts.items():
        continent_json[continent] = [ts.get(yr, 0) for yr in years]

    # Top countries for this crop (latest year average)
    country_ts = get_fao_crop_timeseries(selected_item, None, selected_element)
    # Compute each country's latest value
    country_avgs = []
    for country, ts in country_ts.items():
        vals = [v for v in ts.values() if v]
        if vals:
            country_avgs.append({'country': country, 'value': round(sum(vals[-5:]) / min(len(vals), 5), 2)})
    country_avgs.sort(key=lambda x: x['value'], reverse=True)
    top_countries = country_avgs[:20]

    unit_map = {
        'Production':     '1000 tonnes',
        'Yield':          'hg/ha',
        'Area harvested': '1000 ha',
    }

    return render(request, 'global_agriculture.html', {
        'all_items':       all_items[:200],   # limit for dropdown size
        'selected_item':   selected_item,
        'selected_element': selected_element,
        'element_choices': element_choices,
        'years_json':      json.dumps(years),
        'continent_json':  json.dumps(continent_json),
        'top_countries':   top_countries,
        'unit':            unit_map.get(selected_element, ''),
    })


# ── T3-2. SMART IRRIGATION ADVISOR ─────────────────────────────────────────
def irrigation_advisor_view(request):
    opts   = get_irrigation_options()
    result = None
    error  = None

    # Load yield impact table for context card
    bundle = load_irrigation_bundle()
    yield_impact = bundle.get('yield_impact', {})

    if request.method == 'POST':
        try:
            region   = request.POST.get('region',  'North')
            soil     = request.POST.get('soil',    'Loam')
            crop     = request.POST.get('crop',    'Wheat')
            rainfall = float(request.POST.get('rainfall', 500))
            temp     = float(request.POST.get('temp', 25))
            weather  = request.POST.get('weather', 'Sunny')
            days     = float(request.POST.get('days', 90))

            result = predict_irrigation(region, soil, crop, rainfall, temp, weather, days)
            result['crop']    = crop
            result['region']  = region
            result['soil']    = soil
            result['weather'] = weather
        except Exception as e:
            error = str(e)

    # Build yield impact chart data (irrigated vs not, per crop)
    yield_chart = {
        'crops':        list(yield_impact.keys()),
        'irrigated':    [round(v['irrigated'], 2)     for v in yield_impact.values()],
        'not_irrigated': [round(v['not_irrigated'], 2) for v in yield_impact.values()],
    }

    return render(request, 'irrigation_advisor.html', {
        'opts':         opts,
        'result':       result,
        'error':        error,
        'yield_chart':  yield_chart,
        'yield_impact_json': json.dumps(yield_chart),
    })


# ── T3-3. CROP ROTATION PLANNER ────────────────────────────────────────────
def rotation_planner_view(request):
    all_crops = sorted(_CROP_NPK_FALLBACK.keys())
    selected_crop = request.GET.get('crop', '')
    suggestions   = []

    if selected_crop:
        suggestions = get_rotation_suggestions(selected_crop.lower(), top_n=6)

    # Build NPK overview table for all crops
    npk_table = []
    for crop, npk in sorted(_CROP_NPK_FALLBACK.items()):
        npk_table.append({
            'crop':     crop.title(),
            'category': npk.get('category', ''),
            'N':        npk.get('N', 0),
            'P':        npk.get('P', 0),
            'K':        npk.get('K', 0),
            'legume':   npk.get('legume', False),
        })

    return render(request, 'rotation_planner.html', {
        'all_crops':     all_crops,
        'selected_crop': selected_crop,
        'suggestions':   suggestions,
        'npk_table':     npk_table,
    })


# ── T3-4. SOIL NUTRIENT TRACKER ────────────────────────────────────────────
def soil_tracker_view(request):
    """
    Session-based N/P/K balance calculator.
    User adds crop seasons; tracker accumulates depletion.
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'add')
        if action == 'reset':
            request.session['soil_history'] = []
        else:
            history = request.session.get('soil_history', [])
            crop_key  = request.POST.get('crop', 'wheat').lower()
            yield_t   = max(float(request.POST.get('yield_t', 1.0)), 0)
            n_applied = float(request.POST.get('n_applied', 0))
            p_applied = float(request.POST.get('p_applied', 0))
            k_applied = float(request.POST.get('k_applied', 0))
            season    = request.POST.get('season', 'Kharif 2024')

            npk = _CROP_NPK_FALLBACK.get(crop_key, {'N': 20, 'P': 4, 'K': 10})
            n_removed = round(npk['N'] * yield_t, 1)
            p_removed = round(npk['P'] * yield_t, 1)
            k_removed = round(npk['K'] * yield_t, 1)

            history.append({
                'season':     season,
                'crop':       crop_key.title(),
                'yield_t':    round(yield_t, 2),
                'n_applied':  n_applied,
                'p_applied':  p_applied,
                'k_applied':  k_applied,
                'n_removed':  n_removed,
                'p_removed':  p_removed,
                'k_removed':  k_removed,
                'n_balance':  round(n_applied - n_removed, 1),
                'p_balance':  round(p_applied - p_removed, 1),
                'k_balance':  round(k_applied - k_removed, 1),
            })
            request.session['soil_history'] = history
        return redirect('soil_tracker')

    history = request.session.get('soil_history', [])

    # Cumulative totals
    cum_n = sum(h['n_balance'] for h in history)
    cum_p = sum(h['p_balance'] for h in history)
    cum_k = sum(h['k_balance'] for h in history)

    # Chart: balance trend per season
    chart_data = {
        'labels': [h['season'] for h in history],
        'N':      [round(sum(x['n_balance'] for x in history[:i+1]), 1) for i in range(len(history))],
        'P':      [round(sum(x['p_balance'] for x in history[:i+1]), 1) for i in range(len(history))],
        'K':      [round(sum(x['k_balance'] for x in history[:i+1]), 1) for i in range(len(history))],
    }

    all_crops = sorted(_CROP_NPK_FALLBACK.keys())

    return render(request, 'soil_tracker.html', {
        'history':      history,
        'cum_n':        round(cum_n, 1),
        'cum_p':        round(cum_p, 1),
        'cum_k':        round(cum_k, 1),
        'chart_json':   json.dumps(chart_data),
        'all_crops':    all_crops,
        'npk_ref':      _CROP_NPK_FALLBACK,
    })


# ── T3-5. US vs INDIA CORN YIELD COMPARISON ────────────────────────────────
def corn_comparison_view(request):
    try:
        data = load_corn_comparison()
    except Exception as e:
        return render(request, 'corn_comparison.html', {'error': str(e)})

    us_nat  = data['us_national_avg']
    ind_nat = data['india_national_avg']

    all_years = sorted(set(us_nat.keys()) | set(ind_nat.keys()))

    national_chart = {
        'years':  all_years,
        'us':     [us_nat.get(yr)   for yr in all_years],
        'india':  [ind_nat.get(yr)  for yr in all_years],
    }

    # Latest year stats
    latest_yr_us  = max(us_nat.keys())  if us_nat  else None
    latest_yr_ind = max(ind_nat.keys()) if ind_nat else None

    # State rankings for latest available year
    us_states = []
    for state, yr_d in data['us_by_state'].items():
        if yr_d:
            latest = yr_d.get(latest_yr_us, None)
            if latest:
                us_states.append({'state': state, 'yield': latest})
    us_states.sort(key=lambda x: x['yield'], reverse=True)

    india_states = []
    for state, yr_d in data['india_by_state'].items():
        if yr_d:
            latest = yr_d.get(latest_yr_ind, None)
            if latest:
                india_states.append({'state': state, 'yield': latest})
    india_states.sort(key=lambda x: x['yield'], reverse=True)

    # Gap analysis
    us_latest   = us_nat.get(latest_yr_us, 0)
    ind_latest  = ind_nat.get(latest_yr_ind, 0)
    gap_pct     = round((us_latest - ind_latest) / ind_latest * 100, 1) if ind_latest else 0

    return render(request, 'corn_comparison.html', {
        'national_chart_json': json.dumps(national_chart),
        'us_states':    us_states[:15],
        'india_states': india_states[:15],
        'us_latest':    round(us_latest, 0),
        'ind_latest':   round(ind_latest, 0),
        'gap_pct':      gap_pct,
        'latest_yr_us':  latest_yr_us,
        'latest_yr_ind': latest_yr_ind,
    })


# ── T3-6. FOOD SECURITY INDEX ───────────────────────────────────────────────
def food_security_view(request):
    try:
        data = load_food_security()
    except Exception as e:
        return render(request, 'food_security.html', {'error': str(e)})

    if not data:
        return render(request, 'food_security.html', {'error': 'APY dataset not loaded'})

    by_state     = data['by_state']
    nat_avg      = data['national_avg_per_capita']
    surplus_list = data['surplus_states']     # sorted desc by per_capita_kg
    year_trend   = data['year_trend']

    # Top 10 surplus + bottom 10 deficit
    top_surplus = surplus_list[:10]
    top_deficit = list(reversed(surplus_list))[:10]

    # Bar chart: all states ranked
    ranked = sorted(by_state.items(), key=lambda x: x[1]['per_capita_kg'], reverse=True)
    bar_chart = {
        'states': [s for s, _ in ranked],
        'values': [d['per_capita_kg'] for _, d in ranked],
        'scores': [d['surplus_score'] for _, d in ranked],
    }

    # Year trend
    trend_years  = sorted(year_trend.keys())
    trend_values = [year_trend[yr] for yr in trend_years]

    selected_state = request.GET.get('state', '')
    state_detail   = by_state.get(selected_state, {})

    return render(request, 'food_security.html', {
        'nat_avg':          round(nat_avg, 1),
        'top_surplus':      top_surplus,
        'top_deficit':      top_deficit,
        'bar_chart_json':   json.dumps(bar_chart),
        'trend_json':       json.dumps({'years': trend_years, 'values': trend_values}),
        'states':           data['states'],
        'selected_state':   selected_state,
        'state_detail':     state_detail,
        'total_states':     len(by_state),
    })


# ===========================================================================
# TIER-4 FEATURES (18–20)
# ===========================================================================

# ── T4-1. CLIMATE IMPACT ON YIELD FORECASTING ──────────────────────────────
def climate_forecast_view(request):
    from .ml.climate_analytics import get_climate_forecast, get_options

    countries, crops = get_options()
    result = None
    error  = None

    selected_country = request.GET.get('country', 'India')
    selected_crop    = request.GET.get('crop', 'Rice, paddy')

    if selected_country and selected_crop:
        result, error = get_climate_forecast(selected_country, selected_crop)

    chart_json = json.dumps(result['chart_data']) if result else json.dumps(None)

    return render(request, 'climate_forecast.html', {
        'countries':        countries,
        'crops':            crops,
        'selected_country': selected_country,
        'selected_crop':    selected_crop,
        'result':           result,
        'error':            error,
        'chart_json':       chart_json,
    })


# ── T4-2. CROP PRODUCTION ANOMALY DETECTION ────────────────────────────────
def anomaly_detection_view(request):
    from .ml.anomaly_detector import detect_anomalies, get_filter_options

    states, crops = get_filter_options()
    anomalies = []
    summary   = {}
    error     = None

    selected_state = request.GET.get('state', '')
    selected_crop  = request.GET.get('crop', '')
    threshold      = float(request.GET.get('threshold', 2.0))

    # Only run detection after user selects at least one filter
    if selected_state or selected_crop:
        anomalies, summary, error = detect_anomalies(
            state=selected_state or None,
            crop=selected_crop  or None,
            threshold=threshold,
            top_n=30,
        )

    # Chart: top-20 anomalies timeline
    chart_data = {
        'labels': [f"{a['district']} {a['year']}" for a in anomalies[:20]],
        'z_scores': [a['z_score'] for a in anomalies[:20]],
        'directions': [a['direction'] for a in anomalies[:20]],
    }

    return render(request, 'anomaly_detection.html', {
        'states':         states,
        'crops':          crops,
        'selected_state': selected_state,
        'selected_crop':  selected_crop,
        'threshold':      threshold,
        'anomalies':      anomalies,
        'summary':        summary,
        'error':          error,
        'chart_json':     json.dumps(chart_data),
    })


# ── T4-3. MULTI-CROP PORTFOLIO OPTIMIZER ───────────────────────────────────
def portfolio_optimizer_view(request):
    from .ml.portfolio_optimizer import optimize_portfolio, get_all_crops

    result     = None
    error      = None
    inputs     = {}
    all_crops  = get_all_crops()

    if request.method == 'POST':
        try:
            farm_acres = float(request.POST.get('farm_acres', 5))
            budget     = float(request.POST.get('budget', 50000))
            risk_pref  = request.POST.get('risk_pref', 'medium')
            max_crops  = int(request.POST.get('max_crops', 4))

            if farm_acres <= 0 or budget <= 0:
                raise ValueError('Farm size and budget must be positive.')

            inputs = {
                'farm_acres': farm_acres,
                'budget':     budget,
                'risk_pref':  risk_pref,
                'max_crops':  max_crops,
            }
            result, error = optimize_portfolio(farm_acres, budget, risk_pref, max_crops)

        except (ValueError, TypeError) as exc:
            error = str(exc)

    # Donut chart data for result
    chart_json = 'null'
    if result and result.get('portfolio'):
        chart_json = json.dumps({
            'labels': [p['crop'] for p in result['portfolio']],
            'values': [p['alloc_pct'] for p in result['portfolio']],
            'profits': [p['profit'] for p in result['portfolio']],
        })

    return render(request, 'portfolio_optimizer.html', {
        'result':     result,
        'error':      error,
        'inputs':     inputs,
        'all_crops':  all_crops,
        'chart_json': chart_json,
    })
