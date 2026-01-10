#!/usr/bin/env python3
"""
Replace Bundle with new Flex layout (wide, 2-column, side-by-side)
"""

import re
from pathlib import Path

# Translations for each language
TRANSLATIONS = {
    'de': {
        'title': 'Smart Start Bundle',
        'subtitle': 'Landing Page + Google Ads + CRM-Integration',
        'save': 'Sie sparen €498 (45%)',
        'button': 'Bundle jetzt sichern',
        'contains': 'Das Bundle enthält:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM-Integration (Basic)',
        'value': 'Wert'
    },
    'en': {
        'title': 'Smart Start Bundle',
        'subtitle': 'Landing Page + Google Ads + CRM Integration',
        'save': 'You save €498 (45%)',
        'button': 'Get Bundle Now',
        'contains': 'The bundle includes:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM Integration (Basic)',
        'value': 'Value'
    },
    'pl': {
        'title': 'Smart Start Bundle',
        'subtitle': 'Landing Page + Google Ads + Integracja CRM',
        'save': 'Oszczędzasz €498 (45%)',
        'button': 'Zabezpiecz Bundle',
        'contains': 'Pakiet zawiera:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'Integracja CRM (Basic)',
        'value': 'Wartość'
    },
    'ru': {
        'title': 'Smart Start Bundle',
        'subtitle': 'Landing Page + Google Ads + CRM интеграция',
        'save': 'Вы экономите €498 (45%)',
        'button': 'Получить Bundle',
        'contains': 'Пакет включает:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM интеграция (Basic)',
        'value': 'Стоимость'
    },
    'tr': {
        'title': 'Smart Start Bundle',
        'subtitle': 'Landing Page + Google Ads + CRM Entegrasyonu',
        'save': '€498 tasarruf ediyorsunuz (45%)',
        'button': 'Bundle\'ı Şimdi Alın',
        'contains': 'Paket içeriği:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM Entegrasyonu (Basic)',
        'value': 'Değer'
    },
    'ua': {
        'title': 'Smart Start Bundle',
        'subtitle': 'Landing Page + Google Ads + CRM інтеграція',
        'save': 'Ви економите €498 (45%)',
        'button': 'Отримати Bundle',
        'contains': 'Пакет включає:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM інтеграція (Basic)',
        'value': 'Вартість'
    }
}

def generate_bundle_html(lang):
    """Generate Bundle HTML with translations"""
    t = TRANSLATIONS[lang]

    return f'''    <!-- SMART START BUNDLE (FIXED LAYOUT) -->
    <section class="bundle-section" style="padding: 80px 0; width: 100%; display: block;">
        <div class="container">
            <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 2px solid #3B82F6; border-radius: 24px; padding: 40px; position: relative; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5); max-width: 1100px; margin: 0 auto;">

                <!-- Badge -->
                <div style="position: absolute; top: 30px; right: -35px; transform: rotate(45deg); background: #F59E0B; color: #000; padding: 5px 40px; font-weight: 800; font-size: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 10;">
                    BESTSELLER
                </div>

                <!-- Flex Container: Forces Side-by-Side -->
                <div style="display: flex; flex-wrap: wrap; gap: 50px; align-items: center; justify-content: space-between;">

                    <!-- LEFT COLUMN (Price & CTA) -->
                    <div style="flex: 1 1 400px; min-width: 300px;">
                        <h3 style="font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, #3B82F6, #2563EB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                            🚀 {t['title']}
                        </h3>
                        <p style="color: #94A3B8; font-size: 1.2rem; margin-bottom: 25px;">
                            {t['subtitle']}
                        </p>

                        <div style="display: flex; align-items: baseline; gap: 15px; margin-bottom: 10px;">
                            <span style="text-decoration: line-through; color: #64748B; font-size: 1.4rem;">€1.097</span>
                            <span style="font-size: 3.5rem; font-weight: 900; color: #F8FAFC; line-height: 1;">€599</span>
                        </div>
                        <p style="color: #10B981; font-weight: 700; margin-bottom: 30px; font-size: 1.1rem;">
                            {t['save']}
                        </p>

                        <a href="#contact" class="btn btn-primary" style="width: 100%; text-align: center; padding: 18px; font-size: 1.2rem; display: block; background: #3B82F6; color: white; border-radius: 12px; text-decoration: none;">
                            {t['button']}
                        </a>
                    </div>

                    <!-- RIGHT COLUMN (List) -->
                    <div style="flex: 1 1 400px; min-width: 300px; background: rgba(255,255,255,0.03); padding: 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                        <h4 style="margin-bottom: 20px; font-size: 1.2rem; color: white; font-weight: 700;">{t['contains']}</h4>
                        <ul style="display: flex; flex-direction: column; gap: 15px; list-style: none; padding: 0; margin: 0;">
                            <li style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;">
                                <span style="display: flex; align-items: center; gap: 10px; color: #F8FAFC;">
                                    🎨 <span>{t['item1']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.9rem;">{t['value']}: €199</span>
                            </li>
                            <li style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;">
                                <span style="display: flex; align-items: center; gap: 10px; color: #F8FAFC;">
                                    📊 <span>{t['item2']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.9rem;">{t['value']}: €399</span>
                            </li>
                            <li style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="display: flex; align-items: center; gap: 10px; color: #F8FAFC;">
                                    🔗 <span>{t['item3']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.9rem;">{t['value']}: €499</span>
                            </li>
                        </ul>
                    </div>

                </div>
            </div>
        </div>
    </section>'''

def replace_bundle(content, lang):
    """Replace old Bundle with new Flex layout"""

    # Pattern: Find and replace entire Bundle section
    # Look for: <!-- SMART START BUNDLE --> ... </section>
    pattern = r'    <!-- SMART START BUNDLE.*?</section>'

    new_bundle = generate_bundle_html(lang)

    content = re.sub(pattern, new_bundle, content, flags=re.DOTALL)

    return content

def process_file(file_path, lang):
    """Process a single index.html file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no Bundle found
        if 'SMART START BUNDLE' not in original:
            return False

        new_content = replace_bundle(original, lang)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update Bundle in all language versions (except DE - already done)"""
    base_dir = Path('.')
    lang_dirs = ['en', 'pl', 'ru', 'tr', 'ua']  # Skip DE

    modified_count = 0

    for lang_dir in lang_dirs:
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file, lang_dir):
                print(f"Fixed: {index_file} ({lang_dir.upper()})")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Bundle now uses FLEX layout (wide, 2 columns, side-by-side)")

if __name__ == '__main__':
    main()
