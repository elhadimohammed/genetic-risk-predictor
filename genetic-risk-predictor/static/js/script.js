/* =========================================================
   script.js — Genetic Risk Predictor
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  initNavHighlight();
  initCheckboxToggles();
  initBMICalc();
  initFormValidation();
  initGaugeChart();
  initCounters();
  initFlashDismiss();
  initTableRowLinks();
});

/* ── Active nav highlight ─────────────────────────────────── */
function initNavHighlight() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === path ||
        (path.startsWith('/result') && a.getAttribute('href') === '/predict')) {
      a.classList.add('active');
    }
  });
}

/* ── Checkbox card toggle ─────────────────────────────────── */
function initCheckboxToggles() {
  document.querySelectorAll('.toggle-item').forEach(item => {
    const cb = item.querySelector('input[type="checkbox"]');
    if (!cb) return;
    const sync = () => item.classList.toggle('checked', cb.checked);
    sync();
    cb.addEventListener('change', sync);
    item.addEventListener('click', e => {
      if (e.target !== cb) { cb.checked = !cb.checked; sync(); }
    });
  });
}

/* ── Live BMI calculator ──────────────────────────────────── */
function initBMICalc() {
  const bmiInput = document.getElementById('bmi');
  const badge    = document.getElementById('bmi-badge');
  if (!bmiInput || !badge) return;

  const classify = v => {
    if (v < 18.5) return { label:'Underweight', cls:'#60a5fa' };
    if (v < 25)   return { label:'Normal',      cls:'#22c55e' };
    if (v < 30)   return { label:'Overweight',  cls:'#f59e0b' };
    return              { label:'Obese',         cls:'#ef4444' };
  };

  const update = () => {
    const v = parseFloat(bmiInput.value);
    if (isNaN(v) || v < 10 || v > 70) { badge.style.display = 'none'; return; }
    const { label, cls } = classify(v);
    badge.textContent = `BMI ${v.toFixed(1)} — ${label}`;
    badge.style.background = cls + '25';
    badge.style.color = cls;
    badge.style.display = 'inline-flex';
  };

  bmiInput.addEventListener('input', update);
  update();
}

/* ── Client-side form validation ──────────────────────────── */
function initFormValidation() {
  const form = document.getElementById('predict-form');
  if (!form) return;

  form.addEventListener('submit', e => {
    const errors = [];
    const require = (id, label, min, max) => {
      const el = document.getElementById(id);
      if (!el) return;
      const v = parseFloat(el.value);
      if (el.value.trim() === '') { errors.push(`${label} is required.`); markInvalid(el); }
      else if (min !== undefined && v < min) { errors.push(`${label} must be ≥ ${min}.`); markInvalid(el); }
      else if (max !== undefined && v > max) { errors.push(`${label} must be ≤ ${max}.`); markInvalid(el); }
      else markValid(el);
    };
    require('patient_name',      'Patient name');
    require('age',               'Age',               1,  120);
    require('bmi',               'BMI',               10, 70);
    require('blood_pressure',    'Blood pressure',    40, 300);
    require('cholesterol',       'Cholesterol',       50, 500);
    require('glucose',           'Glucose',           40, 600);
    require('physical_activity', 'Physical activity', 0,  168);

    if (errors.length) {
      e.preventDefault();
      showClientErrors(errors);
      form.querySelector('.alert-error')?.scrollIntoView({ behavior:'smooth', block:'center' });
    }
  });

  // Clear error on input
  form.querySelectorAll('.form-control').forEach(el => {
    el.addEventListener('input', () => {
      el.classList.remove('input-error');
      el.classList.add('input-ok');
    });
  });
}

function markInvalid(el) {
  el.classList.add('input-error');
  el.classList.remove('input-ok');
  el.style.borderColor = 'var(--risk-high)';
}
function markValid(el) {
  el.classList.remove('input-error');
  el.classList.add('input-ok');
  el.style.borderColor = '';
}
function showClientErrors(errors) {
  let box = document.getElementById('client-errors');
  if (!box) {
    box = document.createElement('div');
    box.id = 'client-errors';
    box.className = 'alert alert-error';
    const form = document.getElementById('predict-form');
    form.prepend(box);
  }
  box.innerHTML = `<span>⚠️</span><div><strong>Please fix the following:</strong><ul>${
    errors.map(e => `<li>${e}</li>`).join('')
  }</ul></div>`;
}

/* ── Risk gauge chart (Chart.js doughnut) ─────────────────── */
function initGaugeChart() {
  const canvas = document.getElementById('risk-gauge');
  if (!canvas) return;

  const pct   = parseFloat(canvas.dataset.probability || '0');
  const level = canvas.dataset.level || 'Low';

  const colorMap = { Low: '#22c55e', Medium: '#f59e0b', High: '#ef4444' };
  const color = colorMap[level] || '#22c55e';
  const remaining = 1 - pct;

  if (typeof Chart === 'undefined') return;

  new Chart(canvas, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [pct, remaining],
        backgroundColor: [color, 'rgba(255,255,255,0.06)'],
        borderWidth: 0,
        borderRadius: 6,
      }]
    },
    options: {
      cutout: '76%',
      rotation: -90,
      circumference: 180,
      animation: { animateRotate: true, duration: 1200, easing: 'easeInOutQuart' },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
    }
  });
}

/* ── Animated stat counters ───────────────────────────────── */
function initCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    const isInt  = Number.isInteger(target);
    const duration = 1400;
    const start    = performance.now();

    const tick = now => {
      const t = Math.min((now - start) / duration, 1);
      const ease = t < .5 ? 2*t*t : -1+(4-2*t)*t;
      const cur  = target * ease;
      el.textContent = isInt ? Math.round(cur).toLocaleString() : cur.toFixed(1);
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = isInt ? target.toLocaleString() : target.toFixed(1);
    };

    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) { requestAnimationFrame(tick); obs.disconnect(); }
    }, { threshold: 0.5 });
    obs.observe(el);
  });
}

/* ── Flash message auto-dismiss ───────────────────────────── */
function initFlashDismiss() {
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity .5s, transform .5s';
      el.style.opacity    = '0';
      el.style.transform  = 'translateX(40px)';
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });
}

/* ── History table row → view result ─────────────────────── */
function initTableRowLinks() {
  document.querySelectorAll('tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => {
      window.location.href = row.dataset.href;
    });
  });
}

/* ── Probability bar animate on scroll ───────────────────── */
document.querySelectorAll('.prob-bar').forEach(bar => {
  const w = bar.dataset.width || '0';
  bar.style.width = '0';
  const obs = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) {
      setTimeout(() => { bar.style.width = w + '%'; }, 100);
      obs.disconnect();
    }
  });
  obs.observe(bar);
});
