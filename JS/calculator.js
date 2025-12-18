/**
 * VERMARKTER - Media Planning Calculator
 * Real formulas, no simplification
 * Follows masterplan.md specifications exactly
 */

class MediaCalculator {
  constructor() {
    this.inputs = {
      platform: document.getElementById('platform'),
      budget: document.getElementById('budget'),
      cpc: document.getElementById('cpc'),
      ctr: document.getElementById('ctr'),
      cr: document.getElementById('cr'),
      aov: document.getElementById('aov')
    };

    this.outputs = {
      clicks: document.getElementById('result-clicks'),
      conversions: document.getElementById('result-conversions'),
      revenue: document.getElementById('result-revenue'),
      profit: document.getElementById('result-profit'),
      roas: document.getElementById('result-roas')
    };

    this.init();
  }

  init() {
    // Attach event listeners to all inputs
    Object.values(this.inputs).forEach(input => {
      input.addEventListener('input', () => this.calculate());
    });

    // Initial calculation
    this.calculate();
  }

  getValues() {
    return {
      platform: this.inputs.platform.value,
      budget: parseFloat(this.inputs.budget.value) || 0,
      cpc: parseFloat(this.inputs.cpc.value) || 0,
      ctr: parseFloat(this.inputs.ctr.value) || 0,
      cr: parseFloat(this.inputs.cr.value) || 0,
      aov: parseFloat(this.inputs.aov.value) || 0
    };
  }

  calculate() {
    const v = this.getValues();

    // Validation
    if (v.budget <= 0) {
      this.showError('Bitte geben Sie ein Budget ein');
      return;
    }

    if (v.cpc <= 0) {
      this.showError('CPC muss größer als 0 sein');
      return;
    }

    // ===== FORMULA 1: Clicks =====
    const clicks = Math.floor(v.budget / v.cpc);

    // ===== FORMULA 2: Conversions =====
    const conversions = Math.floor(clicks * (v.cr / 100));

    // ===== FORMULA 3: Revenue =====
    const revenue = conversions * v.aov;

    // ===== FORMULA 4: Profit =====
    const profit = revenue - v.budget;

    // ===== FORMULA 5: ROAS =====
    const roas = v.budget > 0 ? revenue / v.budget : 0;

    // Validation: High CR warning
    if (v.cr > 20) {
      this.showWarning('Das ist eine sehr hohe CR. Bitte überprüfen Sie die Realitätsnähe.');
    }

    // Display results
    this.displayResults({
      clicks,
      conversions,
      revenue,
      profit,
      roas
    });
  }

  displayResults(results) {
    // Animate numbers slowly (calm, not casino-style)
    this.animateValue(this.outputs.clicks, results.clicks, '');
    this.animateValue(this.outputs.conversions, results.conversions, '');
    this.animateValue(this.outputs.revenue, results.revenue, '€');
    this.animateValue(this.outputs.profit, results.profit, '€', results.profit < 0);
    this.animateValue(this.outputs.roas, results.roas, 'x', results.roas < 1);

    // Color profit based on value
    if (results.profit < 0) {
      this.outputs.profit.classList.add('text-error');
      this.outputs.profit.classList.remove('text-success');
    } else {
      this.outputs.profit.classList.add('text-success');
      this.outputs.profit.classList.remove('text-error');
    }

    // Color ROAS based on value
    if (results.roas < 1) {
      this.outputs.roas.classList.add('text-warning');
      this.outputs.roas.classList.remove('text-success');
    } else if (results.roas >= 3) {
      this.outputs.roas.classList.add('text-success');
      this.outputs.roas.classList.remove('text-warning');
    } else {
      this.outputs.roas.classList.remove('text-success', 'text-warning');
    }
  }

  animateValue(element, targetValue, suffix = '', isNegative = false) {
    const duration = 300; // Slow, calm animation
    const startValue = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function (easeOutQuad)
      const easeProgress = progress * (2 - progress);
      const currentValue = startValue + (targetValue - startValue) * easeProgress;

      // Format number
      let formatted;
      if (suffix === 'x') {
        formatted = currentValue.toFixed(2);
      } else if (suffix === '€') {
        formatted = Math.round(currentValue).toLocaleString('de-DE');
      } else {
        formatted = Math.round(currentValue).toLocaleString('de-DE');
      }

      element.textContent = (isNegative && currentValue < 0 ? '' : '') + formatted + suffix;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  showError(message) {
    Object.values(this.outputs).forEach(output => {
      output.textContent = '—';
    });
    console.warn('Calculator:', message);
  }

  showWarning(message) {
    console.warn('Calculator warning:', message);
    // Could add visual warning indicator here
  }
}

// Initialize calculator when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new MediaCalculator();
  });
} else {
  new MediaCalculator();
}
