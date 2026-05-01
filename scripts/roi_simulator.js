/**
 * roi_simulator.js — Treatwell vs Vermarkter 3-Year Cost Chart
 * Usage: import or include, then call initROIChart(canvasId, options)
 *
 * Dependencies: Chart.js (must be loaded before this script)
 */

const ROI_DEFAULTS = {
  monthlyRevenue: 8000,       // € salon monthly revenue
  treatwellCommission: 0.26,  // 26% Treatwell commission on bookings via platform
  treatwellBookingShare: 0.35,// 35% of bookings come via Treatwell
  treatwellMonthlyFee: 39,    // € monthly subscription fee
  vermarkterSetup: 1000,      // € one-time setup
  vermarkterMonthly: 0,       // € no monthly fee
  years: 3,
};

/**
 * Calculate cumulative costs month-by-month for both models.
 * Returns { labels, treatwell, vermarkter, savings }
 */
function calcROIData(opts = {}) {
  const o = Object.assign({}, ROI_DEFAULTS, opts);
  const months = o.years * 12;
  const labels = [];
  const treatwell = [];
  const vermarkter = [];
  const savings = [];

  // Treatwell: monthly fee + commission on bookings routed through platform
  const twMonthly = o.treatwellMonthlyFee
    + (o.monthlyRevenue * o.treatwellBookingShare * o.treatwellCommission);

  let twCum = 0;
  let vmCum = o.vermarkterSetup; // one-time upfront

  for (let m = 1; m <= months; m++) {
    twCum += twMonthly;
    vmCum += o.vermarkterMonthly;

    const yr = Math.floor((m - 1) / 12) + 1;
    const mo = ((m - 1) % 12) + 1;
    labels.push('Y' + yr + 'M' + String(mo).padStart(2, '0'));
    treatwell.push(Math.round(twCum));
    vermarkter.push(Math.round(vmCum));
    savings.push(Math.round(twCum - vmCum));
  }

  return { labels, treatwell, vermarkter, savings };
}

/**
 * Render the comparison chart into a <canvas> element.
 * @param {string} canvasId  - id of the canvas element
 * @param {object} opts      - override ROI_DEFAULTS fields
 * @returns Chart instance
 */
function initROIChart(canvasId, opts = {}) {
  const data = calcROIData(opts);
  const ctx = document.getElementById(canvasId).getContext('2d');

  // Highlight breakeven point (month where vermarkter < treatwell)
  const breakevenMonth = data.savings.findIndex(s => s > 0);

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: 'Treatwell (Kosten kumulativ €)',
          data: data.treatwell,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239,68,68,0.08)',
          borderWidth: 2.5,
          pointRadius: 0,
          tension: 0.3,
          fill: true,
        },
        {
          label: 'Vermarkter (Kosten kumulativ €)',
          data: data.vermarkter,
          borderColor: '#25D366',
          backgroundColor: 'rgba(37,211,102,0.07)',
          borderWidth: 2.5,
          pointRadius: 0,
          tension: 0.3,
          fill: true,
        },
        {
          label: 'Ersparnisse €',
          data: data.savings,
          borderColor: '#8b5cf6',
          backgroundColor: 'rgba(139,92,246,0.07)',
          borderWidth: 1.5,
          borderDash: [6, 3],
          pointRadius: 0,
          tension: 0.3,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          labels: { color: '#f1f5f9', font: { size: 13 } },
        },
        tooltip: {
          callbacks: {
            label: ctx => ctx.dataset.label + ': €' + ctx.parsed.y.toLocaleString('de-DE'),
          },
        },
        annotation: breakevenMonth >= 0 ? {
          annotations: {
            breakeven: {
              type: 'line',
              xMin: breakevenMonth,
              xMax: breakevenMonth,
              borderColor: 'rgba(245,158,11,0.7)',
              borderWidth: 2,
              borderDash: [5, 4],
              label: {
                display: true,
                content: 'Break-even',
                color: '#fbbf24',
                font: { size: 11, weight: 'bold' },
                position: 'start',
              },
            },
          },
        } : {},
      },
      scales: {
        x: {
          ticks: {
            color: 'rgba(255,255,255,0.4)',
            maxTicksLimit: 12,
            font: { size: 11 },
          },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
        y: {
          ticks: {
            color: 'rgba(255,255,255,0.4)',
            callback: v => '€' + v.toLocaleString('de-DE'),
            font: { size: 11 },
          },
          grid: { color: 'rgba(255,255,255,0.05)' },
        },
      },
    },
  });
}

/**
 * Generate a summary stats object for display alongside the chart.
 * @param {object} opts - same as calcROIData opts
 */
function getROISummary(opts = {}) {
  const o = Object.assign({}, ROI_DEFAULTS, opts);
  const data = calcROIData(o);
  const finalSaving = data.savings[data.savings.length - 1];
  const breakevenMonth = data.savings.findIndex(s => s > 0) + 1;
  const twMonthly = o.treatwellMonthlyFee
    + (o.monthlyRevenue * o.treatwellBookingShare * o.treatwellCommission);

  return {
    totalTreatwell3yr: data.treatwell[data.treatwell.length - 1],
    totalVermarkter3yr: data.vermarkter[data.vermarkter.length - 1],
    totalSaving3yr: finalSaving,
    breakevenMonth: breakevenMonth > 0 ? breakevenMonth : null,
    treatwellMonthlyLoss: Math.round(twMonthly),
    roiPercent: Math.round((finalSaving / o.vermarkterSetup) * 100),
  };
}

// Export for module environments
if (typeof module !== 'undefined') {
  module.exports = { calcROIData, initROIChart, getROISummary, ROI_DEFAULTS };
}
