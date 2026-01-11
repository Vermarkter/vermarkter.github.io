#!/usr/bin/env python3
"""
Add Calculator and FAQ sections to service pages (google-ads, meta-ads, tiktok-ads)
- Calculator: INSERT BEFORE Pricing section
- FAQ: INSERT AFTER Bundle section
"""

import re
from pathlib import Path

# Calculator section HTML (extracted from de/index.html)
CALCULATOR_HTML = '''
    <!-- CALCULATOR SECTION -->
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

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8;">Ihre Nische:</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">-- Eigene Werte --</option>
                                <option value="ecommerce">E-Commerce (Produkte)</option>
                                <option value="services">Dienstleistungen (Beauty, Reparatur)</option>
                                <option value="realestate" selected>Immobilien</option>
                                <option value="b2b">B2B / Großhandel</option>
                                <option value="infobiz">Infoprodukte</option>
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

# FAQ section HTML
FAQ_HTML = '''
    <!-- FAQ SECTION -->
    <section id="faq" class="services-section" style="padding: 6rem 0; background: rgba(0,0,0,0.2);">
        <div class="container">
            <div class="section-header" style="text-align: center; margin-bottom: 5rem;">
                <h2 class="section-title" style="font-size: clamp(2rem, 4vw, 3rem); font-weight: 800; margin-bottom: 1rem;">
                    Häufig gestellte Fragen
                </h2>
                <p class="section-subtitle" style="font-size: 1.2rem; color: var(--text-secondary); max-width: 700px; margin: 0 auto;">
                    Alles, was Sie über unsere Dienstleistungen wissen müssen
                </p>
            </div>

            <div class="faq-container" style="max-width: 800px; margin: 0 auto;">
                <div class="faq-item" style="background: var(--glass-bg); backdrop-filter: var(--glass-blur); border: 1px solid var(--glass-border); border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">Wie schnell kann ich mit Ergebnissen rechnen?</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Erste Ergebnisse sehen Sie in der Regel innerhalb von 48-72 Stunden nach dem Kampagnenstart. Optimale Performance erreichen Kampagnen nach 2-4 Wochen Optimierung.
                    </p>
                </div>

                <div class="faq-item" style="background: var(--glass-bg); backdrop-filter: var(--glass-blur); border: 1px solid var(--glass-border); border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">Welches Mindestbudget wird benötigt?</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Wir empfehlen ein monatliches Werbebudget ab €1.000. Je höher das Budget, desto schneller können wir optimieren und bessere Ergebnisse erzielen. Unser STARTER-Paket eignet sich für Budgets bis €2.500/Monat.
                    </p>
                </div>

                <div class="faq-item" style="background: var(--glass-bg); backdrop-filter: var(--glass-blur); border: 1px solid var(--glass-border); border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;">
                    <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">Gibt es eine Vertragsbindung?</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Ja, wir haben eine Mindestlaufzeit von 3 Monaten. Das ist nötig, um Kampagnen professionell zu optimieren. Danach können Sie monatlich kündigen. Keine versteckten Kosten.
                    </p>
                </div>

                <div class="faq-item" style="background: var(--glass-bg); backdrop-filter: var(--glass-blur); border: 1px solid var(--glass-border); border-radius: 16px; padding: 2rem;">
                    <h3 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-primary);">Was passiert, wenn die Kampagne nicht funktioniert?</h3>
                    <p style="color: var(--text-secondary); line-height: 1.7;">
                        Wir analysieren kontinuierlich die Performance und passen die Strategie an. Falls nach 30 Tagen keine zufriedenstellenden Ergebnisse vorliegen, besprechen wir gemeinsam die nächsten Schritte. Transparenz und ehrliche Kommunikation sind uns wichtig.
                    </p>
                </div>
            </div>
        </div>
    </section>

'''

def add_calculator(content):
    """Add Calculator section BEFORE Pricing section"""

    # Check if calculator already exists
    if 'id="calculator-section"' in content:
        print("    Calculator already exists")
        return content, False

    # Find Pricing section
    pricing_pattern = r'(\s*)<!-- PRICING SECTION -->'
    pricing_match = re.search(pricing_pattern, content)

    if not pricing_match:
        print("    ERROR: Pricing section not found")
        return content, False

    # Insert Calculator before Pricing
    insert_pos = pricing_match.start()
    new_content = content[:insert_pos] + CALCULATOR_HTML + '\n' + content[insert_pos:]

    print("    Calculator added before Pricing")
    return new_content, True

def add_faq(content):
    """Add FAQ section AFTER Bundle section"""

    # Check if FAQ already exists
    if 'id="faq"' in content:
        print("    FAQ already exists")
        return content, False

    # Find Bundle section end
    # Pattern: Find </section> after SMART START BUNDLE
    bundle_pattern = r'(<!-- SMART START BUNDLE.*?</section>)'
    bundle_match = re.search(bundle_pattern, content, re.DOTALL)

    if not bundle_match:
        print("    ERROR: Bundle section not found")
        return content, False

    # Insert FAQ after Bundle
    insert_pos = bundle_match.end()
    new_content = content[:insert_pos] + '\n' + FAQ_HTML + '\n' + content[insert_pos:]

    print("    FAQ added after Bundle")
    return new_content, True

def process_file(file_path):
    """Process a single service page"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        modified = False

        # Add Calculator
        content, calc_added = add_calculator(content)
        if calc_added:
            modified = True

        # Add FAQ
        content, faq_added = add_faq(content)
        if faq_added:
            modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False

def main():
    """Add Calculator and FAQ to service pages"""
    base_dir = Path('.')
    modified_count = 0

    # Service pages to update
    service_pages = ['google-ads.html', 'meta-ads.html', 'tiktok-ads.html']
    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        print(f"\n=== {lang.upper()} ===")
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        for service_page in service_pages:
            file_path = lang_path / service_page
            if file_path.exists():
                print(f"Processing {service_page}...")
                if process_file(file_path):
                    print(f"  SUCCESS: {file_path}")
                    modified_count += 1
                else:
                    print(f"  No changes needed")

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Added: Calculator (before Pricing) + FAQ (after Bundle)")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
