// ── STATE ──────────────────────────────────────
let goalSelected = 'recomp';
let stepInterval;

// ── GOAL SELECTION ─────────────────────────────
function selectGoal(el) {
  document.querySelectorAll('.goal-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  goalSelected = el.dataset.goal;
}

// ── LOADING STATE ──────────────────────────────
function showLoading() {
  document.getElementById('loading-card').style.display = 'block';
  document.getElementById('error-card').style.display = 'none';
  document.getElementById('results').classList.remove('visible');
  document.getElementById('calc-btn').disabled = true;

  const steps = ['step-1', 'step-2', 'step-3', 'step-4'];
  let current = 0;

  steps.forEach(s => document.getElementById(s).className = 'loading-step');
  document.getElementById(steps[0]).classList.add('active');

  stepInterval = setInterval(() => {
    if (current < steps.length - 1) {
      document.getElementById(steps[current]).className = 'loading-step done';
      current++;
      document.getElementById(steps[current]).classList.add('active');
    }
  }, 1800);
}

function hideLoading() {
  clearInterval(stepInterval);
  document.getElementById('loading-card').style.display = 'none';
  document.getElementById('calc-btn').disabled = false;
}

function showError(msg) {
  hideLoading();
  document.getElementById('error-msg').textContent = msg;
  document.getElementById('error-card').style.display = 'block';
}

// ── COUNTER ANIMATION ──────────────────────────
function animateCounter(el, target, isKcal = false) {
  const duration = 900;
  const start = performance.now();

  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(target * eased);
    el.textContent = isKcal ? value.toLocaleString('pt-BR') : value;
    if (progress < 1) requestAnimationFrame(step);
  }

  requestAnimationFrame(step);
}

// ── RENDER RESULTS ─────────────────────────────
function renderResults(data) {
  const colorMap = {
    'Abaixo':    '#f59e0b',
    'Peso':      '#03ddff',
    'Sobrepeso': '#f59e0b',
    'Obesidade': '#ef4444',
  };
  const imcColor = Object.entries(colorMap).find(([k]) => data.imc_label?.startsWith(k))?.[1] || '#03ddff';
  const imcPct   = data.imc < 18.5 ? 18 : data.imc < 25 ? 52 : data.imc < 30 ? 72 : 90;

  // IMC
  document.getElementById('imc-val').textContent   = data.imc;
  document.getElementById('imc-val').style.color   = imcColor;
  document.getElementById('imc-label').textContent = data.imc_label;
  document.getElementById('imc-label').style.color = imcColor;
  document.getElementById('imc-desc').textContent  = data.imc_desc;
  document.getElementById('imc-tag').style.color   = imcColor;
  document.getElementById('imc-bar').style.width      = imcPct + '%';
  document.getElementById('imc-bar').style.background = imcColor;

  // Metrics (com animação de contador)
  animateCounter(document.getElementById('r-kcal'), data.kcal, true);
  animateCounter(document.getElementById('r-prot'), data.prot);
  animateCounter(document.getElementById('r-carb'), data.carb);
  animateCounter(document.getElementById('r-gord'), data.gord);

  // Macro bar (delay pra animar depois do reveal)
  setTimeout(() => {
    document.getElementById('mb-p').style.width = data.prot_pct + '%';
    document.getElementById('mb-c').style.width = data.carb_pct + '%';
    document.getElementById('mb-g').style.width = data.gord_pct + '%';
  }, 200);

  document.getElementById('ml-p').textContent = data.prot_pct + '%';
  document.getElementById('ml-c').textContent = data.carb_pct + '%';
  document.getElementById('ml-g').textContent = data.gord_pct + '%';

  // Cardápio
  document.getElementById('meals-list').innerHTML = data.meals.map(m => `
    <div class="meal-row">
      <div class="meal-time">${m.time}</div>
      <div>
        <div class="meal-name">${m.name}</div>
        <div class="meal-items">${m.items}</div>
      </div>
      <div class="meal-kcal">~${m.kcal} kcal</div>
    </div>
  `).join('');

  // Tip & Insight
  document.getElementById('tip-box').textContent = data.tip || '';

  if (data.insight) {
    document.getElementById('insight-text').textContent = data.insight;
    document.getElementById('insight-box').style.display = 'flex';
  }

  // Exibe resultados com scroll reveal
  hideLoading();

  const results = document.getElementById('results');
  results.classList.add('visible');

  setTimeout(() => {
    results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setTimeout(() => {
      document.querySelectorAll('.reveal').forEach((el, i) => {
        setTimeout(() => el.classList.add('revealed'), i * 60);
      });
    }, 300);
  }, 80);
}

// ── MAIN FUNCTION ──────────────────────────────
async function calcular() {
  const peso   = parseFloat(document.getElementById('peso').value);
  const altura = parseFloat(document.getElementById('altura').value);
  const idade  = parseFloat(document.getElementById('idade').value);

  // Validação visual
  if (!peso || !altura || !idade) {
    ['peso', 'altura', 'idade'].forEach(id => {
      const el = document.getElementById(id);
      if (!el.value) {
        el.style.borderColor = 'rgba(239,68,68,0.7)';
        setTimeout(() => el.style.borderColor = '', 1600);
      }
    });
    return;
  }

  showLoading();

  try {
    const res = await fetch('/api/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        peso,
        altura,
        idade,
        sexo:      document.getElementById('sexo').value,
        atividade: parseFloat(document.getElementById('atividade').value),
        objetivo:  goalSelected,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erro ${res.status}`);
    }

    renderResults(await res.json());

  } catch (e) {
    showError(e.message);
  }
}
