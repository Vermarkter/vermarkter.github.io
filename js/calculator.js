(function() {
  const platformData = {
    google: { label: 'Google Ads', cpc: 0.65, ctr: 0.035 },
    meta: { label: 'Meta Ads', cpc: 0.45, ctr: 0.022 },
    tiktok: { label: 'TikTok Ads', cpc: 0.3, ctr: 0.028 },
    linkedin: { label: 'LinkedIn Ads', cpc: 1.1, ctr: 0.018 }
  };

  const geoMultiplier = {
    germany: 1,
    poland: 0.72,
    spain: 0.82,
    france: 1.05,
    italy: 0.9,
    europe: 1.12
  };

  const goalConversion = {
    traffic: 0.015,
    leads: 0.035,
    sales: 0.024
  };

  function formatNumber(value) {
    return Number(value || 0).toLocaleString('uk-UA');
  }

  function calculateForecast({ platform, geo, goal, budget }) {
    const platformMeta = platformData[platform];
    if (!platformMeta) {
      return { effectiveCpc: 0, ctr: 0, clicks: 0, impressions: 0, leads: 0, cpa: null };
    }
    const multiplier = geoMultiplier[geo] || 1;
    const conversionRate = goalConversion[goal] || 0.02;
    const effectiveCpc = Number((platformMeta.cpc * multiplier).toFixed(2));
    const ctr = platformMeta.ctr * (goal === 'traffic' ? 1.05 : goal === 'sales' ? 0.9 : 1);
    const clicks = Math.max(0, Math.floor(budget / effectiveCpc));
    const impressions = ctr > 0 ? Math.max(0, Math.round(clicks / ctr)) : 0;
    const leads = Math.max(0, Math.round(clicks * conversionRate));
    const cpa = leads > 0 ? Number((budget / leads).toFixed(2)) : null;

    return {
      effectiveCpc,
      ctr,
      clicks,
      impressions,
      leads,
      cpa
    };
  }

  function updateCalculatorUI({ platform, geo, goal, budget }) {
    const forecast = calculateForecast({ platform, geo, goal, budget });
    const clicksEl = document.getElementById('result-clicks');
    const impressionsEl = document.getElementById('result-impressions');
    const leadsEl = document.getElementById('result-leads');
    const cpcEl = document.getElementById('result-cpc');
    const ctrEl = document.getElementById('result-ctr');
    const cpaEl = document.getElementById('result-cpa');
    const summaryEl = document.getElementById('result-summary');
    const statusEl = document.getElementById('calc-status');

    if (!clicksEl || !impressionsEl || !leadsEl || !cpcEl || !ctrEl || !cpaEl || !summaryEl) return;

    clicksEl.textContent = formatNumber(forecast.clicks);
    impressionsEl.textContent = formatNumber(forecast.impressions);
    leadsEl.textContent = formatNumber(forecast.leads);
    cpcEl.textContent = `${forecast.effectiveCpc.toFixed(2)} €`;
    ctrEl.textContent = `${(forecast.ctr * 100).toFixed(1)}%`;
    cpaEl.textContent = forecast.cpa ? `${forecast.cpa.toFixed(2)} €` : '—';

    const geoLabel = document.querySelector(`#calc-geo option[value="${geo}"]`)?.textContent || 'Європа';
    const platformLabel = platformData[platform]?.label || 'Ads';
    const goalLabel = document.querySelector(`#calc-goal option[value="${goal}"]`)?.textContent || '';

    summaryEl.textContent = `Бюджет ${budget}€ → ${platformLabel} у регіоні ${geoLabel}: до ${formatNumber(forecast.impressions)} показів, ${formatNumber(forecast.clicks)} кліків та приблизно ${formatNumber(forecast.leads)} лідів (${goalLabel}).`;
    if (statusEl) {
      statusEl.textContent = `Прогноз оновлено під бюджет ${budget}€`;
    }
  }

  function initAdsCalculator() {
    const form = document.getElementById('calculator-form');
    const platformInput = document.getElementById('calc-platform');
    const geoInput = document.getElementById('calc-geo');
    const goalInput = document.getElementById('calc-goal');
    const budgetInput = document.getElementById('budget');
    const budgetRange = document.getElementById('budget-range');

    if (!form || !platformInput || !geoInput || !goalInput || !budgetInput || !budgetRange) return;

    const syncAndUpdate = () => {
      const budgetValue = Number(budgetInput.value) || 0;
      updateCalculatorUI({
        platform: platformInput.value,
        geo: geoInput.value,
        goal: goalInput.value,
        budget: budgetValue
      });
    };

    budgetInput.addEventListener('input', () => {
      budgetRange.value = budgetInput.value;
      syncAndUpdate();
    });

    budgetRange.addEventListener('input', () => {
      budgetInput.value = budgetRange.value;
      syncAndUpdate();
    });

    [platformInput, geoInput, goalInput].forEach(el => el.addEventListener('change', syncAndUpdate));

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      syncAndUpdate();
    });

    syncAndUpdate();
  }

  document.addEventListener('DOMContentLoaded', initAdsCalculator);
})();
