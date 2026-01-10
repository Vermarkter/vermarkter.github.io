#!/usr/bin/env python3
"""
Add calculator section to all language pages (EN, PL, RU, TR)
Calculator already exists on DE and UA
"""

import re
from pathlib import Path

# Translations for calculator
TRANSLATIONS = {
    'en': {
        'title': 'Smart Media Plan 📊',
        'subtitle': 'Calculate the profitability of your advertising campaign',
        'trust_line1': '💡 <strong>This is a real media planning tool.</strong><br>',
        'trust_line2': 'We use the same formulas as major agencies. Transparent, honest, no hidden costs.',
        'warning': '⚠️ The result is a forecast, not a promise. Marketing starts with honest numbers.',
        'niche_label': 'Your Niche:',
        'niche_custom': '-- Custom Values --',
        'niche_ecommerce': 'E-Commerce (Products)',
        'niche_services': 'Services (Beauty, Repair)',
        'niche_realestate': 'Real Estate',
        'niche_b2b': 'B2B / Wholesale',
        'niche_infobiz': 'Info Products',
        'budget': 'Advertising Budget',
        'cpc': 'Click Price (CPC)',
        'cr': 'Conversion Rate (%)',
        'aov': 'Avg Order Value (€)',
        'margin': 'Margin (%)',
        'result_clicks': 'Traffic (Clicks)',
        'result_leads': 'Leads (Inquiries)',
        'result_cpa': 'CPA (Cost per Lead)',
        'result_roas': 'ROAS (Return on Ad Spend)',
        'result_profit': 'Net Profit'
    },
    'pl': {
        'title': 'Smart Mediaplan 📊',
        'subtitle': 'Oblicz rentowność swojej kampanii reklamowej',
        'trust_line1': '💡 <strong>To prawdziwe narzędzie do planowania mediów.</strong><br>',
        'trust_line2': 'Używamy tych samych formuł co duże agencje. Przejrzyście, uczciwie, bez ukrytych kosztów.',
        'warning': '⚠️ Wynik to prognoza, a nie obietnica. Marketing zaczyna się od uczciwych liczb.',
        'niche_label': 'Twoja nisza:',
        'niche_custom': '-- Własne wartości --',
        'niche_ecommerce': 'E-Commerce (Produkty)',
        'niche_services': 'Usługi (Beauty, Naprawa)',
        'niche_realestate': 'Nieruchomości',
        'niche_b2b': 'B2B / Hurt',
        'niche_infobiz': 'Infoprodukty',
        'budget': 'Budżet reklamowy',
        'cpc': 'Cena kliknięcia (CPC)',
        'cr': 'Współczynnik konwersji (%)',
        'aov': 'Śr. wartość zamówienia (€)',
        'margin': 'Marża (%)',
        'result_clicks': 'Ruch (Kliknięcia)',
        'result_leads': 'Leady (Zapytania)',
        'result_cpa': 'CPA (Koszt za Lead)',
        'result_roas': 'ROAS (Zwrot z wydatków)',
        'result_profit': 'Zysk netto'
    },
    'ru': {
        'title': 'Smart Медиаплан 📊',
        'subtitle': 'Рассчитайте рентабельность вашей рекламной кампании',
        'trust_line1': '💡 <strong>Это реальный инструмент медиапланирования.</strong><br>',
        'trust_line2': 'Мы используем те же формулы, что и крупные агентства. Прозрачно, честно, без скрытых расходов.',
        'warning': '⚠️ Результат — это прогноз, а не обещание. Маркетинг начинается с честных цифр.',
        'niche_label': 'Ваша ниша:',
        'niche_custom': '-- Свои значения --',
        'niche_ecommerce': 'E-Commerce (Товары)',
        'niche_services': 'Услуги (Красота, Ремонт)',
        'niche_realestate': 'Недвижимость',
        'niche_b2b': 'B2B / Опт',
        'niche_infobiz': 'Инфопродукты',
        'budget': 'Рекламный бюджет',
        'cpc': 'Цена клика (CPC)',
        'cr': 'Конверсия (%)',
        'aov': 'Средний чек (€)',
        'margin': 'Маржа (%)',
        'result_clicks': 'Трафик (Клики)',
        'result_leads': 'Лиды (Заявки)',
        'result_cpa': 'CPA (Цена за лид)',
        'result_roas': 'ROAS (Возврат инвестиций)',
        'result_profit': 'Чистая прибыль'
    },
    'tr': {
        'title': 'Smart Medya Planı 📊',
        'subtitle': 'Reklam kampanyanızın karlılığını hesaplayın',
        'trust_line1': '💡 <strong>Bu gerçek bir medya planlama aracıdır.</strong><br>',
        'trust_line2': 'Büyük ajanslarla aynı formülleri kullanıyoruz. Şeffaf, dürüst, gizli maliyet yok.',
        'warning': '⚠️ Sonuç bir tahmindir, söz değil. Pazarlama dürüst rakamlarla başlar.',
        'niche_label': 'Nişiniz:',
        'niche_custom': '-- Özel Değerler --',
        'niche_ecommerce': 'E-Ticaret (Ürünler)',
        'niche_services': 'Hizmetler (Güzellik, Tamir)',
        'niche_realestate': 'Gayrimenkul',
        'niche_b2b': 'B2B / Toptan',
        'niche_infobiz': 'Bilgi Ürünleri',
        'budget': 'Reklam bütçesi',
        'cpc': 'Tıklama fiyatı (CPC)',
        'cr': 'Dönüşüm oranı (%)',
        'aov': 'Ort. sipariş değeri (€)',
        'margin': 'Marj (%)',
        'result_clicks': 'Trafik (Tıklamalar)',
        'result_leads': 'Potansiyel Müşteriler',
        'result_cpa': 'CPA (Lead başına maliyet)',
        'result_roas': 'ROAS (Yatırım getirisi)',
        'result_profit': 'Net kâr'
    }
}

def generate_calculator_html(lang):
    """Generate full calculator section HTML with translations"""
    t = TRANSLATIONS[lang]

    return f'''    <!-- CALCULATOR SECTION -->
    <section id="calculator-section" class="calculator-section">
        <div class="container">
            <div class="calculator">
                <div class="calculator__header">
                    <h2 class="calculator__title">{t['title']}</h2>
                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        {t['subtitle']}
                    </p>

                    <!-- TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px; margin-bottom: 10px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            {t['trust_line1']}
                            {t['trust_line2']}
                        </p>
                    </div>

                    <!-- WARNING BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 14px; line-height: 1.5;">
                            {t['warning']}
                        </p>
                    </div>
                </div>

                <div class="calculator__grid">
                    <!-- Left: Inputs -->
                    <div class="calculator__inputs">

                        <!-- Niche Selector -->
                        <div class="niche-select-group">
                            <label style="display:block; margin-bottom:10px; color:#94A3B8;">{t['niche_label']}</label>
                            <select id="nicheSelector" class="niche-select">
                                <option value="custom">{t['niche_custom']}</option>
                                <option value="ecommerce">{t['niche_ecommerce']}</option>
                                <option value="services">{t['niche_services']}</option>
                                <option value="realestate" selected>{t['niche_realestate']}</option>
                                <option value="b2b">{t['niche_b2b']}</option>
                                <option value="infobiz">{t['niche_infobiz']}</option>
                            </select>
                        </div>

                        <!-- Budget -->
                        <div class="calculator__input-group" data-input="budget">
                            <div class="calculator__label">
                                <span>{t['budget']}</span>
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
                                <span>{t['cpc']}</span>
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
                                <span>{t['cr']}</span>
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
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">{t['aov']}</label>
                                <input type="number" class="calculator__number-input" id="aovInput" value="5000" style="width:100%;">
                                <input type="range" id="aovSlider" min="10" max="10000" step="10" value="5000" style="display:none;">
                                <span id="aovValue" style="display:none;"></span>
                            </div>
                            <div class="calculator__input-group" data-input="margin">
                                <label style="font-size:12px; color:#94A3B8; display:block; margin-bottom:5px;">{t['margin']}</label>
                                <input type="number" class="calculator__number-input" id="marginInput" value="15" style="width:100%;">
                                <input type="range" id="marginSlider" min="5" max="100" step="5" value="15" style="display:none;">
                                <span id="marginValue" style="display:none;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Right: Results -->
                    <div class="calculator__results">
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">{t['result_clicks']}</div>
                            <div class="calculator__result-value" id="resultClicks">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">{t['result_leads']}</div>
                            <div class="calculator__result-value calculator__result-value--primary" id="resultLeads">0</div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">{t['result_cpa']}</div>
                            <div class="calculator__result-value" id="resultCPA">€0</div>
                        </div>
                        <div class="calculator__result-card calculator__result-card--highlight" id="roasCard">
                            <div class="calculator__result-label">{t['result_roas']}</div>
                            <div class="calculator__result-value calculator__result-value--success" id="resultROAS">0%</div>
                            <div class="calculator__roas-indicator">
                                <div class="calculator__roas-bar"><div class="calculator__roas-fill" id="roasFill"></div></div>
                                <span class="calculator__roas-text" id="roasStatus">-</span>
                            </div>
                        </div>
                        <div class="calculator__result-card">
                            <div class="calculator__result-label">{t['result_profit']}</div>
                            <div class="calculator__result-value" id="resultProfit">€0</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

'''

def insert_calculator(content, lang):
    """Insert calculator section before CONTACT SECTION"""

    calculator_html = generate_calculator_html(lang)

    # Pattern: Find "<!-- CONTACT SECTION -->"
    pattern = r'(\s*)<!-- CONTACT SECTION -->'

    replacement = r'\1' + calculator_html + r'\1<!-- CONTACT SECTION -->'

    content = re.sub(pattern, replacement, content)

    return content

def process_file(file_path, lang):
    """Process a single index.html file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if already has calculator SECTION (not just links)
        if 'id="calculator-section"' in original or 'calculator__title' in original:
            print(f"Skipped (already has calculator): {file_path}")
            return False

        # Skip if no CONTACT SECTION anchor found
        if '<!-- CONTACT SECTION -->' not in original:
            print(f"Warning: No CONTACT SECTION found in {file_path}")
            return False

        new_content = insert_calculator(original, lang)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add calculator to EN, PL, RU, TR (skip DE, UA - already have it)"""
    base_dir = Path('.')

    # Only languages that need calculator added
    lang_map = {
        'en': 'en',
        'pl': 'pl',
        'ru': 'ru',
        'tr': 'tr'
    }

    modified_count = 0

    for lang, lang_dir in lang_map.items():
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file, lang):
                print(f"[OK] Added calculator: {index_file} ({lang.upper()})")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Calculator added with trust + warning blocks")
    print(f"Languages: EN, PL, RU, TR (DE, UA already have it)")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
