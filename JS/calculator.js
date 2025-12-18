/**
 * VERMARKTER - Media Planning Calculator
 * Real formulas with margin support
 * Follows masterplan.md specifications exactly
 */

class MediaCalculator {
  constructor() {
    // Preset/Niche selector
    this.nicheSelector = document.getElementById('nicheSelector');

    // Input sliders and number inputs
    this.inputs = {
      budgetSlider: document.getElementById('budgetSlider'),
      budgetInput: document.getElementById('budgetInput'),
      cpcSlider: document.getElementById('cpcSlider'),
      cpcInput: document.getElementById('cpcInput'),
      crSlider: document.getElementById('crSlider'),
      crInput: document.getElementById('crInput'),
      aovSlider: document.getElementById('aovSlider'),
      aovInput: document.getElementById('aovInput'),
      marginSlider: document.getElementById('marginSlider'),
      marginInput: document.getElementById('marginInput')
    };

    // Value displays
    this.valueDisplays = {
      budget: document.getElementById('budgetValue'),
      cpc: document.getElementById('cpcValue'),
      cr: document.getElementById('crValue'),
      aov: document.getElementById('aovValue'),
      margin: document.getElementById('marginValue')
    };

    // Output elements
    this.outputs = {
      clicks: document.getElementById('resultClicks'),
      leads: document.getElementById('resultLeads'),
      cpa: document.getElementById('resultCPA'),
      roas: document.getElementById('resultROAS'),
      profit: document.getElementById('resultProfit')
    };

    // Niche presets
    this.presets = {
      ecommerce: { cpc: 0.8, cr: 3, aov: 150, margin: 40 },
      services: { cpc: 1.2, cr: 5, aov: 250, margin: 60 },
      realestate: { cpc: 2.5, cr: 1.5, aov: 5000, margin: 15 },
      b2b: { cpc: 3.0, cr: 2, aov: 1200, margin: 50 },
      infobiz: { cpc: 0.5, cr: 8, aov: 97, margin: 85 }
    };

    this.init();
  }

  init() {
    // Niche selector
    if (this.nicheSelector) {
      this.nicheSelector.addEventListener('change', (e) => this.applyPreset(e.target.value));
    }

    // Sync sliders with number inputs
    this.syncInput('budget', this.inputs.budgetSlider, this.inputs.budgetInput, this.valueDisplays.budget);
    this.syncInput('cpc', this.inputs.cpcSlider, this.inputs.cpcInput, this.valueDisplays.cpc);
    this.syncInput('cr', this.inputs.crSlider, this.inputs.crInput, this.valueDisplays.cr);
    this.syncInput('aov', this.inputs.aovSlider, this.inputs.aovInput, this.valueDisplays.aov);
    this.syncInput('margin', this.inputs.marginSlider, this.inputs.marginInput, this.valueDisplays.margin);

    // Initial calculation
    this.calculate();
  }

  syncInput(name, slider, numberInput, display) {
    if (!slider || !numberInput) return;

    // Slider changes
    slider.addEventListener('input', (e) => {
      const value = parseFloat(e.target.value);
      numberInput.value = value;
      if (display) display.textContent = value;
      this.calculate();
    });

    // Number input changes
    numberInput.addEventListener('input', (e) => {
      const value = parseFloat(e.target.value);
      if (!isNaN(value)) {
        slider.value = value;
        if (display) display.textContent = value;
        this.calculate();
      }
    });
  }

  applyPreset(niche) {
    if (niche === 'custom') return;

    const preset = this.presets[niche];
    if (!preset) return;

    // Apply preset values
    if (this.inputs.cpcSlider) {
      this.inputs.cpcSlider.value = preset.cpc;
      this.inputs.cpcInput.value = preset.cpc;
      if (this.valueDisplays.cpc) this.valueDisplays.cpc.textContent = preset.cpc;
    }

    if (this.inputs.crSlider) {
      this.inputs.crSlider.value = preset.cr;
      this.inputs.crInput.value = preset.cr;
      if (this.valueDisplays.cr) this.valueDisplays.cr.textContent = preset.cr;
    }

    if (this.inputs.aovSlider) {
      this.inputs.aovSlider.value = preset.aov;
      this.inputs.aovInput.value = preset.aov;
      if (this.valueDisplays.aov) this.valueDisplays.aov.textContent = preset.aov;
    }

    if (this.inputs.marginSlider) {
      this.inputs.marginSlider.value = preset.margin;
      this.inputs.marginInput.value = preset.margin;
      if (this.valueDisplays.margin) this.valueDisplays.margin.textContent = preset.margin;
    }

    this.calculate();
  }

  getValues() {
    return {
      budget: parseFloat(this.inputs.budgetInput?.value) || 1000,
      cpc: parseFloat(this.inputs.cpcInput?.value) || 0.8,
      cr: parseFloat(this.inputs.crInput?.value) || 3,
      aov: parseFloat(this.inputs.aovInput?.value) || 150,
      margin: parseFloat(this.inputs.marginInput?.value) || 40
    };
  }

  calculate() {
    const v = this.getValues();

    // Validation
    if (v.budget <= 0 || v.cpc <= 0) {
      this.showError();
      return;
    }

    // ===== FORMULA 1: Clicks =====
    const clicks = Math.floor(v.budget / v.cpc);

    // ===== FORMULA 2: Leads (Conversions) =====
    const leads = Math.floor(clicks * (v.cr / 100));

    // ===== FORMULA 3: CPA (Cost Per Acquisition) =====
    const cpa = leads > 0 ? v.budget / leads : 0;

    // ===== FORMULA 4: Revenue =====
    const revenue = leads * v.aov;

    // ===== FORMULA 5: Gross Profit (with margin) =====
    const grossProfit = revenue * (v.margin / 100);

    // ===== FORMULA 6: Net Profit (after ad spend) =====
    const netProfit = grossProfit - v.budget;

    // ===== FORMULA 7: ROAS =====
    const roas = v.budget > 0 ? (revenue / v.budget) * 100 : 0;

    // Display results
    this.displayResults({
      clicks,
      leads,
      cpa,
      roas,
      profit: netProfit
    });
  }

  displayResults(results) {
    if (!this.outputs.clicks) return;

    // Animate numbers
    this.animateValue(this.outputs.clicks, results.clicks, '');
    this.animateValue(this.outputs.leads, results.leads, '');
    this.animateValue(this.outputs.cpa, results.cpa, '€');
    this.animateValue(this.outputs.roas, results.roas, '%');
    this.animateValue(this.outputs.profit, results.profit, '€');

    // Color profit based on value
    if (results.profit < 0) {
      this.outputs.profit.style.color = 'var(--error, #EF4444)';
    } else if (results.profit > 0) {
      this.outputs.profit.style.color = 'var(--success, #10B981)';
    } else {
      this.outputs.profit.style.color = 'var(--text-primary)';
    }

    // Color ROAS based on value
    if (results.roas < 100) {
      this.outputs.roas.style.color = 'var(--warning, #F59E0B)';
    } else if (results.roas >= 300) {
      this.outputs.roas.style.color = 'var(--success, #10B981)';
    } else {
      this.outputs.roas.style.color = 'var(--text-primary)';
    }
  }

  animateValue(element, targetValue, suffix = '') {
    const duration = 400;
    const startValue = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function
      const easeProgress = progress * (2 - progress);
      const currentValue = startValue + (targetValue - startValue) * easeProgress;

      // Format number
      let formatted;
      if (suffix === '%') {
        formatted = Math.round(currentValue);
      } else if (suffix === '€') {
        formatted = Math.round(currentValue).toLocaleString('de-DE');
      } else {
        formatted = Math.round(currentValue).toLocaleString('de-DE');
      }

      element.textContent = formatted + suffix;

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }

  showError() {
    if (!this.outputs.clicks) return;

    Object.values(this.outputs).forEach(output => {
      output.textContent = '—';
    });
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
