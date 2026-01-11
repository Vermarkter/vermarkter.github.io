/**
 * VERMARKTER - Media Planning Calculator V2
 * Platform × Niche Matrix with Real EU Market Coefficients
 * For Ukrainian Business Owners in Europe
 */

class MediaCalculator {
  constructor() {
    // Platform selector
    this.platformSelector = document.getElementById('platformSelector');

    // Niche selector
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

    // Platform base multipliers (affect CPC)
    this.platformMultipliers = {
      google: { cpc: 1.0, name: 'Google Ads' },   // Baseline
      meta: { cpc: 0.7, name: 'Meta Ads' },       // 30% cheaper CPC
      tiktok: { cpc: 0.5, name: 'TikTok Ads' }    // 50% cheaper CPC
    };

    // Niche presets: BASE values + coefficients
    // Coefficients multiply the base CPC from platform
    this.niches = {
      custom: {
        name: 'Власні значення',
        cpcMultiplier: 1.0,
        crMultiplier: 1.0,
        baseCPC: 2.5,
        baseCR: 2.0,
        aov: 500,
        margin: 30
      },
      ecommerce: {
        name: 'E-Commerce / Товарка',
        cpcMultiplier: 0.8,   // Low CPC
        crMultiplier: 1.2,    // Good conversion
        baseCPC: 0.8,
        baseCR: 3.0,
        aov: 70,
        margin: 40
      },
      beauty: {
        name: 'Beauty: Салони краси, Косметологія',
        cpcMultiplier: 0.7,   // Very low CPC
        crMultiplier: 1.5,    // High conversion
        baseCPC: 0.6,
        baseCR: 5.0,
        aov: 60,
        margin: 70
      },
      construction: {
        name: 'Ремонт та Будівництво',
        cpcMultiplier: 1.8,   // High CPC
        crMultiplier: 0.6,    // Low conversion
        baseCPC: 2.5,
        baseCR: 1.2,
        aov: 2000,
        margin: 35
      },
      auto: {
        name: 'Автобізнес / СТО / Детейлінг',
        cpcMultiplier: 1.0,   // Medium CPC
        crMultiplier: 1.0,    // Medium conversion
        baseCPC: 1.5,
        baseCR: 2.5,
        aov: 300,
        margin: 50
      },
      realestate: {
        name: 'Нерухомість',
        cpcMultiplier: 3.0,   // Very high CPC
        crMultiplier: 0.3,    // Very low conversion
        baseCPC: 4.0,
        baseCR: 0.8,
        aov: 10000,
        margin: 15
      },
      expert: {
        name: 'Послуги експертів / B2B',
        cpcMultiplier: 2.0,   // High CPC
        crMultiplier: 0.8,    // Below average conversion
        baseCPC: 3.0,
        baseCR: 2.0,
        aov: 1200,
        margin: 60
      }
    };

    this.init();
  }

  init() {
    // Check if calculator elements exist
    if (!this.inputs.budgetSlider) {
      console.warn('Calculator elements not found on this page');
      return;
    }

    // Platform selector
    if (this.platformSelector) {
      this.platformSelector.addEventListener('change', () => this.applyPreset());
    }

    // Niche selector
    if (this.nicheSelector) {
      this.nicheSelector.addEventListener('change', () => this.applyPreset());
    }

    // Sync sliders with number inputs
    this.syncInput('budget', this.inputs.budgetSlider, this.inputs.budgetInput, this.valueDisplays.budget);
    this.syncInput('cpc', this.inputs.cpcSlider, this.inputs.cpcInput, this.valueDisplays.cpc);
    this.syncInput('cr', this.inputs.crSlider, this.inputs.crInput, this.valueDisplays.cr);
    this.syncInput('aov', this.inputs.aovSlider, this.inputs.aovInput, this.valueDisplays.aov);
    this.syncInput('margin', this.inputs.marginSlider, this.inputs.marginInput, this.valueDisplays.margin);

    // Initial calculation
    setTimeout(() => {
      console.log('Running initial calculation...');
      this.calculate();
    }, 100);
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

  applyPreset() {
    const platform = this.platformSelector?.value || 'google';
    const niche = this.nicheSelector?.value || 'custom';

    console.log('Applying preset:', { platform, niche });

    if (niche === 'custom') {
      console.log('Custom selected - no preset applied');
      return;
    }

    const nicheData = this.niches[niche];
    const platformData = this.platformMultipliers[platform];

    if (!nicheData || !platformData) {
      console.warn('No preset found for:', { platform, niche });
      return;
    }

    // Calculate final CPC: base CPC × platform multiplier × niche multiplier
    const finalCPC = (nicheData.baseCPC * platformData.cpc * nicheData.cpcMultiplier).toFixed(2);

    // Calculate final CR: base CR × niche multiplier
    const finalCR = (nicheData.baseCR * nicheData.crMultiplier).toFixed(1);

    console.log('Calculated values:', {
      baseCPC: nicheData.baseCPC,
      platformMult: platformData.cpc,
      nicheMult: nicheData.cpcMultiplier,
      finalCPC,
      finalCR
    });

    // Apply CPC
    if (this.inputs.cpcSlider && this.inputs.cpcInput) {
      this.inputs.cpcSlider.value = finalCPC;
      this.inputs.cpcInput.value = finalCPC;
      if (this.valueDisplays.cpc) this.valueDisplays.cpc.textContent = finalCPC;
    }

    // Apply CR
    if (this.inputs.crSlider && this.inputs.crInput) {
      this.inputs.crSlider.value = finalCR;
      this.inputs.crInput.value = finalCR;
      if (this.valueDisplays.cr) this.valueDisplays.cr.textContent = finalCR;
    }

    // Apply AOV
    if (this.inputs.aovSlider && this.inputs.aovInput) {
      this.inputs.aovSlider.value = nicheData.aov;
      this.inputs.aovInput.value = nicheData.aov;
      if (this.valueDisplays.aov) this.valueDisplays.aov.textContent = nicheData.aov;
    }

    // Apply Margin
    if (this.inputs.marginSlider && this.inputs.marginInput) {
      this.inputs.marginSlider.value = nicheData.margin;
      this.inputs.marginInput.value = nicheData.margin;
      if (this.valueDisplays.margin) this.valueDisplays.margin.textContent = nicheData.margin;
    }

    console.log('Preset applied, recalculating...');
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
    console.log('Calculator values:', v);

    // Validation
    if (v.budget <= 0 || v.cpc <= 0) {
      console.warn('Invalid values:', v);
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

    console.log('Calculated results:', { clicks, leads, cpa, revenue, grossProfit, netProfit, roas });

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
    if (!this.outputs.clicks) {
      console.error('Output elements not found');
      return;
    }

    console.log('Displaying results:', results);

    // Update values with proper formatting
    this.outputs.clicks.textContent = Math.round(results.clicks).toLocaleString('uk-UA');
    this.outputs.leads.textContent = Math.round(results.leads).toLocaleString('uk-UA');
    this.outputs.cpa.textContent = '€' + Math.round(results.cpa).toLocaleString('uk-UA');
    this.outputs.roas.textContent = Math.round(results.roas) + '%';
    this.outputs.profit.textContent = '€' + Math.round(results.profit).toLocaleString('uk-UA');

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
