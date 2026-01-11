#!/usr/bin/env python3
"""
Replace OLD calculator with NEW compact version (with Platform Selector)
on all service pages: google-ads.html, meta-ads.html, tiktok-ads.html
"""

import re
from pathlib import Path

# NEW COMPACT CALCULATOR HTML TEMPLATES (per language)

CALCULATOR_DE = '''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">Smart Mediaplan 📊</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        Berechnen Sie die Rentabilität Ihrer Werbekampagne
                    </p>

                    <!-- БЛОК ДОВІРИ / TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            💡 <strong>Dies ist ein echtes Mediaplanungs-Tool.</strong><br>
                            Wir verwenden dieselben Formeln wie große Agenturen. Transparent, ehrlich, ohne versteckte Kosten.
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            ⚠️ Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Platform Selector -->
                        <div class="niche-select-group" style="margin-bottom: 20px;">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">📢 Werbeplattform:</label>
                            <select id="platformSelector" class="niche-select">
                                <option value="google">Google Ads</option>
                                <option value="meta">Meta Ads (Facebook/Instagram)</option>
                                <option value="tiktok">TikTok Ads</option>
                            </select>
                        </div>

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8; font-weight: 600;">🎯 Ihre Nische:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Eigene Werte --</option>
                                <option value="ecommerce">E-Commerce / Waren</option>
                                <option value="beauty">Beauty: Schönheitssalons, Kosmetologie</option>
                                <option value="construction">Reparatur und Bau</option>
                                <option value="auto" selected>Autogeschäft / Werkstatt / Detailing</option>
                                <option value="realestate">Immobilien</option>
                                <option value="expert">Expertenleistungen / B2B</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>Werbebudget</span>
                                <span class="calculator__label-value">€<span id="budgetValue">5000</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="budgetSlider" min="500" max="50000" step="100" value="5000">
                                <input type="number" class="calculator__number-input" id="budgetInput" value="5000">
                            </div>
                        </div>

                        <!-- CPC -->
                        <div class="calculator__input-group" data-input="cpc">
                            <div class="calculator__label">
                                <span>Klickpreis (CPC)</span>
                                <span class="calculator__label-value">€<span id="cpcValue">2.5</span></span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="cpcSlider" min="0.1" max="10" step="0.1" value="2.5">
                                <input type="number" class="calculator__number-input" id="cpcInput" value="2.5" step="0.1">
                            </div>
                        </div>

                        <!-- Conversion -->
                        <div class="calculator__input-group" data-input="cr">
                            <div class="calculator__label">
                                <span>Conversion Rate (%)</span>
                                <span class="calculator__label-value"><span id="crValue">1.5</span>%</span>
                            </div>
                            <div class="calculator__controls">
                                <input type="range" class="calculator__range" id="crSlider" min="0.1" max="15" step="0.1" value="1.5">
                                <input type="number" class="calculator__number-input" id="crInput" value="1.5" step="0.1">
                            </div>
                        </div>

                        <!-- Advanced (AOV + Margin) -->
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px;">
                            <div class="calculator__input-group" data-input="aov">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Ø Bestellwert (€)</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">Marge (%)</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Traffic (Klicks)</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Leads (Anfragen)</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">CPA (Kosten pro Lead)</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">ROAS (Return on Ad Spend)</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">Nettogewinn</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>

                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    ⚠️ Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.
                </p>
            </div>
        </div>
    </section>
'''

CALCULATOR_EN = CALCULATOR_DE.replace('Berechnen Sie die Rentabilität Ihrer Werbekampagne', 'Calculate the profitability of your advertising campaign')\
    .replace('Dies ist ein echtes Mediaplanungs-Tool.', 'This is a real media planning tool.')\
    .replace('Wir verwenden dieselben Formeln wie große Agenturen. Transparent, ehrlich, ohne versteckte Kosten.', 'We use the same formulas as big agencies. Transparent, honest, no hidden costs.')\
    .replace('Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.', 'The result is a forecast, not a promise. Marketing starts with honest numbers.')\
    .replace('Werbeplattform:', 'Advertising Platform:')\
    .replace('Ihre Nische:', 'Your Niche:')\
    .replace('Eigene Werte', 'Custom Values')\
    .replace('E-Commerce / Waren', 'E-Commerce / Products')\
    .replace('Beauty: Schönheitssalons, Kosmetologie', 'Beauty: Salons, Cosmetology')\
    .replace('Reparatur und Bau', 'Repair and Construction')\
    .replace('Autogeschäft / Werkstatt / Detailing', 'Auto Business / Service / Detailing')\
    .replace('Immobilien', 'Real Estate')\
    .replace('Expertenleistungen / B2B', 'Expert Services / B2B')\
    .replace('Werbebudget', 'Advertising Budget')\
    .replace('Klickpreis (CPC)', 'Cost Per Click (CPC)')\
    .replace('Conversion Rate (%)', 'Conversion Rate (%)')\
    .replace('Ø Bestellwert (€)', 'Avg. Order Value (€)')\
    .replace('Marge (%)', 'Margin (%)')\
    .replace('Traffic (Klicks)', 'Traffic (Clicks)')\
    .replace('Leads (Anfragen)', 'Leads (Requests)')\
    .replace('CPA (Kosten pro Lead)', 'CPA (Cost Per Lead)')\
    .replace('Nettogewinn', 'Net Profit')

# For other languages, keep DE version (will need manual translation later if needed)
CALCULATOR_PL = CALCULATOR_DE
CALCULATOR_RU = CALCULATOR_DE
CALCULATOR_TR = CALCULATOR_DE
CALCULATOR_UA = CALCULATOR_DE

CALCULATORS = {
    'de': CALCULATOR_DE,
    'en': CALCULATOR_EN,
    'pl': CALCULATOR_PL,
    'ru': CALCULATOR_RU,
    'tr': CALCULATOR_TR,
    'ua': CALCULATOR_UA
}

def replace_calculator(content, lang):
    """Replace OLD calculator section with NEW compact version"""

    # Pattern: Find entire calculator section from <!-- CALCULATOR SECTION --> to </section>
    pattern = r'<!-- CALCULATOR SECTION -->.*?</section>\s*\n\s*\n\s*\n'

    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("    WARNING: Calculator section not found")
        return content, False

    new_calculator = CALCULATORS.get(lang, CALCULATOR_DE)
    new_content = content[:match.start()] + new_calculator + '\n\n\n' + content[match.end():]

    return new_content, True

def process_file(file_path, lang):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content, modified = replace_calculator(original, lang)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def main():
    """Replace calculator on all service pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']
    service_pages = ['google-ads.html', 'meta-ads.html', 'tiktok-ads.html']

    print("="*60)
    print("REPLACING OLD CALCULATOR WITH NEW COMPACT VERSION")
    print("="*60)

    for lang in lang_dirs:
        print(f"\n=== {lang.upper()} ===")
        lang_path = base_dir / lang
        if not lang_path.exists():
            print(f"  SKIP: {lang}/ directory not found")
            continue

        for service_page in service_pages:
            file_path = lang_path / service_page
            if file_path.exists():
                print(f"  Processing {service_page}...")
                if process_file(file_path, lang):
                    print(f"    OK: Replaced calculator")
                    modified_count += 1
                else:
                    print(f"    SKIP: No changes")
            else:
                print(f"  SKIP: {service_page} not found")

    print(f"\n{'='*60}")
    print(f"SUMMARY: Modified {modified_count} files")
    print(f"NEW FEATURES:")
    print(f"  - Platform Selector (Google/Meta/TikTok)")
    print(f"  - 7 specific business niches (not generic)")
    print(f"  - Same compact 2-column layout as ua/index.html")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
