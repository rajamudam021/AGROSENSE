/**
 * AgroSense - Smart AI Farming Advisor
 * main.js - Complete client-side JavaScript
 */

'use strict';

/* ============================================================
   0. NAVBAR SCROLL EFFECT
   ============================================================ */
(function initNavbarScroll() {
  const nav = document.querySelector('.navbar-agro');
  if (!nav) return;

  function handleScroll() {
    if (window.scrollY > 60) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll(); // run once on load
})();


/* ============================================================
   2. RANGE SLIDER SYNC (ph and humidity)
   ============================================================ */
(function initSliders() {
  function syncPair(sliderId, inputId) {
    const slider = document.getElementById(sliderId);
    const input  = document.getElementById(inputId);
    if (!slider || !input) return;

    slider.addEventListener('input', function () { input.value = this.value; });
    input.addEventListener('input', function () {
      const val = parseFloat(this.value);
      if (!isNaN(val) && val >= parseFloat(slider.min) && val <= parseFloat(slider.max)) {
        slider.value = val;
      }
    });
  }

  syncPair('ph_slider',       'ph');
  syncPair('humidity_slider', 'humidity');
})();


/* ============================================================
   3. WEATHER API FETCH (AJAX)
   ============================================================ */
(function initWeather() {
  const btn    = document.getElementById('getWeatherBtn');
  const cityIn = document.getElementById('city');
  if (!btn || !cityIn) return;

  btn.addEventListener('click', function () {
    const city = cityIn.value.trim();
    if (!city) {
      showAlert('Please enter a city name first.', 'warning');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Fetching...';

    fetch('/api/weather/?city=' + encodeURIComponent(city))
      .then(function (r) { return r.json(); })
      .then(function (data) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-cloud-sun me-1"></i>Get Weather';

        if (data.error && !data.demo) {
          showAlert('Weather error: ' + data.error, 'danger');
          return;
        }

        if (data.demo) {
          showAlert('Weather API key not configured. Please add your OpenWeatherMap key in settings.py.', 'info');
          return;
        }

        // Auto-fill fields
        if (data.temperature !== undefined) setFieldValue('temperature', data.temperature);
        if (data.humidity    !== undefined) setFieldValue('humidity',    data.humidity);
        if (data.rainfall    !== undefined) setFieldValue('rainfall',    data.rainfall);

        showAlert(
          'Weather data loaded for ' + (data.city || city) + ': ' +
          (data.description || '') + '. Fields auto-filled.',
          'success'
        );
      })
      .catch(function (err) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-cloud-sun me-1"></i>Get Weather';
        showAlert('Could not fetch weather: ' + err.message, 'danger');
      });
  });

  function setFieldValue(id, val) {
    const el = document.getElementById(id);
    if (el) {
      el.value = val;
      // Sync sliders
      const slider = document.getElementById(id + '_slider');
      if (slider) slider.value = val;
    }
  }
})();


/* ============================================================
   4. VOICE INPUT (Web Speech API)
   ============================================================ */
(function initVoiceInput() {
  const btn = document.getElementById('voiceInputBtn');
  if (!btn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    btn.title = 'Voice input not supported in this browser';
    btn.style.opacity = '0.5';
    btn.addEventListener('click', function () {
      showAlert('Voice input is not supported in your browser. Try Chrome or Edge.', 'warning');
    });
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';
  recognition.continuous = false;
  recognition.interimResults = false;

  const indicator = document.getElementById('voiceIndicator');

  btn.addEventListener('click', function () {
    recognition.start();
    btn.classList.add('btn-danger');
    btn.innerHTML = '<i class="fa-solid fa-microphone-slash me-1"></i>Listening...';
    if (indicator) indicator.style.display = 'block';
  });

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript.toLowerCase();
    parseVoiceInput(transcript);
    btn.classList.remove('btn-danger');
    btn.innerHTML = '<i class="fa-solid fa-microphone me-1"></i>Voice Input';
    if (indicator) indicator.style.display = 'none';
    showAlert('Voice input received: "' + transcript + '"', 'info');
  };

  recognition.onerror = function (event) {
    btn.classList.remove('btn-danger');
    btn.innerHTML = '<i class="fa-solid fa-microphone me-1"></i>Voice Input';
    if (indicator) indicator.style.display = 'none';
    showAlert('Voice recognition error: ' + event.error, 'danger');
  };

  recognition.onend = function () {
    btn.classList.remove('btn-danger');
    btn.innerHTML = '<i class="fa-solid fa-microphone me-1"></i>Voice Input';
    if (indicator) indicator.style.display = 'none';
  };

  /**
   * Parse voice command like:
   * "N 50 P 30 K 40 temperature 25 humidity 70 ph 6.5 rainfall 100"
   */
  function parseVoiceInput(text) {
    const patterns = {
      N:           /\bnitrogen\s+(\d+\.?\d*)|(?:^|\s)n\s+(\d+\.?\d*)/,
      P:           /\bphosphorus\s+(\d+\.?\d*)|(?:^|\s)p\s+(\d+\.?\d*)/,
      K:           /\bpotassium\s+(\d+\.?\d*)|(?:^|\s)k\s+(\d+\.?\d*)/,
      temperature: /\btemperature\s+(\d+\.?\d*)/,
      humidity:    /\bhumidity\s+(\d+\.?\d*)/,
      ph:          /\bph\s+(\d+\.?\d*)/,
      rainfall:    /\brainfall\s+(\d+\.?\d*)/,
    };

    for (const [field, pattern] of Object.entries(patterns)) {
      const match = text.match(pattern);
      if (match) {
        const val = match[1] || match[2];
        const el  = document.getElementById(field);
        if (el && val) {
          el.value = parseFloat(val);
          const slider = document.getElementById(field + '_slider');
          if (slider) slider.value = parseFloat(val);
        }
      }
    }
  }
})();


/* ============================================================
   5. FORM VALIDATION
   ============================================================ */
(function initFormValidation() {
  const form = document.getElementById('predictForm');
  if (!form) return;

  const rules = {
    N:           { min: 0,   max: 200, label: 'Nitrogen (N)' },
    P:           { min: 0,   max: 200, label: 'Phosphorus (P)' },
    K:           { min: 0,   max: 200, label: 'Potassium (K)' },
    temperature: { min: -10, max: 55,  label: 'Temperature' },
    humidity:    { min: 0,   max: 100, label: 'Humidity' },
    ph:          { min: 0,   max: 14,  label: 'pH' },
    rainfall:    { min: 0,   max: 4000, label: 'Rainfall' },
  };

  form.addEventListener('submit', function (e) {
    let valid = true;

    for (const [id, rule] of Object.entries(rules)) {
      const el  = document.getElementById(id);
      const msg = document.getElementById(id + '_error');
      if (!el) continue;

      clearError(el, msg);
      const val = parseFloat(el.value);

      if (isNaN(val)) {
        showFieldError(el, msg, rule.label + ' must be a number.');
        valid = false;
      } else if (val < rule.min || val > rule.max) {
        showFieldError(el, msg, rule.label + ' must be between ' + rule.min + ' and ' + rule.max + '.');
        valid = false;
      }
    }

    if (!valid) {
      e.preventDefault();
      showAlert('Please correct the highlighted errors before submitting.', 'danger');
    }
  });

  function showFieldError(el, msgEl, text) {
    el.classList.add('is-invalid');
    if (msgEl) { msgEl.textContent = text; msgEl.style.display = 'block'; }
  }

  function clearError(el, msgEl) {
    el.classList.remove('is-invalid');
    if (msgEl) { msgEl.style.display = 'none'; }
  }
})();


/* ============================================================
   6. CROP FILTER (Tips & Market Prices pages)
   ============================================================ */
(function initCropFilter() {
  // Filter buttons (data-filter attribute)
  document.querySelectorAll('[data-filter-btn]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const filterVal = this.getAttribute('data-filter-btn');

      // Toggle active state
      document.querySelectorAll('[data-filter-btn]').forEach(function (b) {
        b.classList.remove('active', 'btn-success');
        b.classList.add('btn-outline-success');
      });
      this.classList.add('active', 'btn-success');
      this.classList.remove('btn-outline-success');

      // Show/hide items
      document.querySelectorAll('[data-filter-item]').forEach(function (item) {
        if (filterVal === 'all' || item.getAttribute('data-filter-item') === filterVal) {
          item.style.display = '';
          item.style.animation = 'fadeInUp 0.3s ease';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  // Search bar
  const searchInput = document.getElementById('cropSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      const query = this.value.toLowerCase();
      document.querySelectorAll('[data-searchable]').forEach(function (item) {
        const text = item.getAttribute('data-searchable').toLowerCase();
        item.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }
})();


/* ============================================================
   7. LANGUAGE SWITCHER
   ============================================================ */
(function initLanguageSwitcher() {
  const sel = document.getElementById('languageSelect');
  if (!sel) return;

  // Restore saved language
  const saved = localStorage.getItem('agroLang') || 'en';
  sel.value = saved;

  sel.addEventListener('change', function () {
    const lang = this.value;
    localStorage.setItem('agroLang', lang);
    if (lang !== 'en') {
      showAlert(
        'Full ' + (lang === 'hi' ? 'Hindi' : 'Telugu') + ' language support is coming soon! Currently displaying in English.',
        'info'
      );
      sel.value = 'en';
      localStorage.setItem('agroLang', 'en');
    }
  });
})();


/* ============================================================
   8. SMOOTH SCROLL FOR ANCHOR LINKS
   ============================================================ */
document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});


/* ============================================================
   9. FADE-IN ON SCROLL (Intersection Observer)
   ============================================================ */
(function initScrollAnimations() {
  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.fade-in-scroll').forEach(function (el) {
    observer.observe(el);
  });
})();


/* ============================================================
   10. ANIMATED COUNTERS (Stats Section)
   ============================================================ */
(function initCounters() {
  const counters = document.querySelectorAll('[data-counter]');
  if (!counters.length) return;

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      const el     = entry.target;
      const target = parseInt(el.getAttribute('data-counter'), 10);
      const suffix = el.getAttribute('data-counter-suffix') || '';
      const duration = 1500;
      const start    = performance.now();

      function step(now) {
        const elapsed  = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased    = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
        el.textContent = Math.floor(eased * target) + suffix;
        if (progress < 1) requestAnimationFrame(step);
      }

      requestAnimationFrame(step);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });

  counters.forEach(function (c) { observer.observe(c); });
})();


/* ============================================================
   11. CSV EXPORT (History Page)
   ============================================================ */
(function initCsvExport() {
  const btn = document.getElementById('exportCsvBtn');
  if (!btn) return;

  btn.addEventListener('click', function () {
    const table = document.getElementById('historyTable');
    if (!table) return;

    const rows   = table.querySelectorAll('tr');
    const lines  = [];

    rows.forEach(function (row) {
      const cells = row.querySelectorAll('th, td');
      const cols  = [];
      cells.forEach(function (cell) {
        // Escape quotes and wrap in quotes
        const text = cell.innerText.replace(/"/g, '""').replace(/\n/g, ' ');
        cols.push('"' + text + '"');
      });
      lines.push(cols.join(','));
    });

    const csvContent = '\uFEFF' + lines.join('\r\n'); // BOM for Excel
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href     = url;
    link.download = 'agrosense_history_' + new Date().toISOString().slice(0, 10) + '.csv';
    link.click();
    URL.revokeObjectURL(url);
  });
})();


/* ============================================================
   12. HELPER: Show bootstrap-style alert toast
   ============================================================ */
function showAlert(message, type) {
  type = type || 'info';
  const container = document.getElementById('alertContainer');
  if (!container) {
    // Fallback: use SweetAlert2 if available
    if (window.Swal) {
      Swal.fire({ text: message, icon: type === 'danger' ? 'error' : type, timer: 3500, showConfirmButton: false });
    }
    return;
  }

  const alertDiv = document.createElement('div');
  alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show shadow-sm';
  alertDiv.role = 'alert';
  alertDiv.innerHTML =
    message +
    '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
  container.appendChild(alertDiv);

  setTimeout(function () {
    alertDiv.classList.remove('show');
    setTimeout(function () { alertDiv.remove(); }, 300);
  }, 4000);
}


/* ============================================================
   13. LEAFLET MAP INIT (Predict page - if city given)
   ============================================================ */
(function initMap() {
  const mapEl = document.getElementById('prediction-map');
  if (!mapEl || typeof L === 'undefined') return;

  const lat  = parseFloat(mapEl.getAttribute('data-lat')  || '20.5937');
  const lng  = parseFloat(mapEl.getAttribute('data-lng')  || '78.9629');
  const city = mapEl.getAttribute('data-city') || 'India';

  const map = L.map('prediction-map').setView([lat, lng], 6);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(map);

  L.marker([lat, lng])
    .addTo(map)
    .bindPopup('<b>' + city + '</b><br>Predicted Location')
    .openPopup();
})();


/* ============================================================
   14. DASHBOARD CHARTS (Chart.js)
   ============================================================ */
(function initDashboardCharts() {
  const chartDataEl = document.getElementById('chartData');
  if (!chartDataEl || typeof Chart === 'undefined') return;

  let chartData;
  try {
    chartData = JSON.parse(chartDataEl.textContent);
  } catch (e) { return; }

  const gridColor   = 'rgba(0,0,0,0.07)';
  const labelColor  = '#4a5568';
  const green       = '#38a169';

  Chart.defaults.color = labelColor;
  Chart.defaults.borderColor = gridColor;

  // 1. NPK Bar Chart
  const npkCanvas = document.getElementById('npkChart');
  if (npkCanvas && chartData.npk) {
    new Chart(npkCanvas, {
      type: 'bar',
      data: {
        labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
        datasets: [{
          label: 'Average kg/ha',
          data: [chartData.npk.N, chartData.npk.P, chartData.npk.K],
          backgroundColor: ['#38a169aa', '#4299e1aa', '#d69e2eaa'],
          borderColor:     ['#38a169',   '#4299e1',   '#d69e2e'],
          borderWidth: 2,
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: gridColor } },
          x: { grid: { display: false } },
        },
      },
    });
  }

  // 2. Crop Distribution Doughnut
  const cropCanvas = document.getElementById('cropChart');
  if (cropCanvas && chartData.crop_dist) {
    const palette = ['#38a169','#4299e1','#d69e2e','#e53e3e','#805ad5','#ed8936','#0bc5ea','#9c4221'];
    new Chart(cropCanvas, {
      type: 'doughnut',
      data: {
        labels: chartData.crop_dist.labels,
        datasets: [{
          data: chartData.crop_dist.data,
          backgroundColor: palette.slice(0, chartData.crop_dist.labels.length),
          borderWidth: 2,
          borderColor: '#fff',
        }],
      },
      options: {
        responsive: true,
        cutout: '65%',
        plugins: {
          legend: { position: 'bottom', labels: { padding: 12, boxWidth: 12 } },
        },
      },
    });
  }

  // 3. Soil Health Line Chart
  const soilCanvas = document.getElementById('soilChart');
  if (soilCanvas && chartData.soil_timeline) {
    new Chart(soilCanvas, {
      type: 'line',
      data: {
        labels: chartData.soil_timeline.labels,
        datasets: [{
          label: 'Soil Health Score',
          data: chartData.soil_timeline.data,
          borderColor: green,
          backgroundColor: 'rgba(56,161,105,0.12)',
          borderWidth: 2,
          pointBackgroundColor: green,
          pointRadius: 4,
          tension: 0.4,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { min: 0, max: 100, grid: { color: gridColor } },
          x: { grid: { display: false } },
        },
      },
    });
  }

  // 4. Latest Top-3 Bar Chart
  const top3Canvas = document.getElementById('top3Chart');
  if (top3Canvas && chartData.latest_top3) {
    new Chart(top3Canvas, {
      type: 'bar',
      data: {
        labels: chartData.latest_top3.labels,
        datasets: [{
          label: 'Probability %',
          data: chartData.latest_top3.data,
          backgroundColor: ['#38a169aa', '#4299e1aa', '#d69e2eaa'],
          borderColor:     ['#38a169',   '#4299e1',   '#d69e2e'],
          borderWidth: 2,
          borderRadius: 6,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, max: 100, grid: { color: gridColor } },
          y: { grid: { display: false } },
        },
      },
    });
  }
})();


/* ============================================================
   15. MARKET PRICES CHART (Chart.js horizontal bar)
   ============================================================ */
(function initMarketChart() {
  const canvas = document.getElementById('marketChart');
  if (!canvas || typeof Chart === 'undefined') return;

  const labels = JSON.parse(canvas.getAttribute('data-labels') || '[]');
  const prices = JSON.parse(canvas.getAttribute('data-prices') || '[]');

  if (!labels.length) return;

  const gridColor = 'rgba(0,0,0,0.07)';

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Price (INR/quintal)',
        data: prices,
        backgroundColor: 'rgba(56,161,105,0.7)',
        borderColor: '#38a169',
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, grid: { color: gridColor } },
        y: { grid: { display: false } },
      },
    },
  });
})();
