#!/usr/bin/env python3
"""
Update Bundle on all service pages to match index.html format
Add container wrapper and max-width: 1100px
"""

import re
from pathlib import Path

# Translations (same as in other scripts)
TRANSLATIONS = {
    'de': {
        'subtitle': 'Landing Page + Google Ads + CRM-Integration',
        'save': 'Sie sparen €498 (45%)',
        'button': 'Bundle jetzt sichern',
        'contains': 'Das Bundle enthält:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM-Integration (Basic)'
    },
    'en': {
        'subtitle': 'Landing Page + Google Ads + CRM Integration',
        'save': 'You save €498 (45%)',
        'button': 'Get Bundle Now',
        'contains': 'The bundle includes:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM Integration (Basic)'
    },
    'pl': {
        'subtitle': 'Landing Page + Google Ads + Integracja CRM',
        'save': 'Oszczędzasz €498 (45%)',
        'button': 'Zabezpiecz Bundle',
        'contains': 'Pakiet zawiera:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'Integracja CRM (Basic)'
    },
    'ru': {
        'subtitle': 'Landing Page + Google Ads + CRM интеграция',
        'save': 'Вы экономите €498 (45%)',
        'button': 'Получить Bundle',
        'contains': 'Пакет включает:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM интеграция (Basic)'
    },
    'tr': {
        'subtitle': 'Landing Page + Google Ads + CRM Entegrasyonu',
        'save': '€498 tasarruf ediyorsunuz (45%)',
        'button': 'Bundle\'ı Şimdi Alın',
        'contains': 'Paket içeriği:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM Entegrasyonu (Basic)'
    },
    'ua': {
        'subtitle': 'Landing Page + Google Ads + CRM інтеграція',
        'save': 'Ви економите €498 (45%)',
        'button': 'Отримати Bundle',
        'contains': 'Пакет включає:',
        'item1': 'Landing Page (Express)',
        'item2': 'Google Ads Setup (Pro)',
        'item3': 'CRM інтеграція (Basic)'
    }
}

def generate_new_bundle(lang):
    """Generate Bundle HTML in index.html format (with container and max-width)"""
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
                <div class="bundle-flex-container" style="display: flex; flex-wrap: wrap; gap: 50px; align-items: flex-start; justify-content: space-between;">

                    <!-- LEFT COLUMN (Price & CTA) -->
                    <div class="bundle-left" style="flex: 1 1 400px; min-width: 300px;">
                        <h3 style="font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, #3B82F6, #2563EB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
                            🚀 Smart Start Bundle
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
                    <div class="bundle-right" style="flex: 1 1 400px; min-width: 300px; background: rgba(255,255,255,0.03); padding: 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1);">
                        <h4 style="margin-bottom: 20px; font-size: 1.2rem; color: white; font-weight: 700;">{t['contains']}</h4>
                        <ul style="display: flex; flex-direction: column; gap: 15px; list-style: none; padding: 0; margin: 0;">
                            <li style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;">
                                <span style="display: flex; align-items: center; gap: 10px; color: #F8FAFC;">
                                    🎨 <span>{t['item1']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.9rem;">Wert: €199</span>
                            </li>
                            <li style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;">
                                <span style="display: flex; align-items: center; gap: 10px; color: #F8FAFC;">
                                    📊 <span>{t['item2']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.9rem;">Wert: €399</span>
                            </li>
                            <li style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="display: flex; align-items: center; gap: 10px; color: #F8FAFC;">
                                    🔗 <span>{t['item3']}</span>
                                </span>
                                <span style="color: #94A3B8; font-size: 0.9rem;">Wert: €499</span>
                            </li>
                        </ul>
                    </div>

                </div>
            </div>
        </div>
    </section>
'''

def replace_bundle(content, lang):
    """Replace old Bundle with new format from index.html"""

    # Pattern: Find entire Bundle section from <!-- SMART START BUNDLE --> to </section> or next section start
    # Old format might be:
    # - <div class="service-card bundle-card" ...
    # - <div class="bundle-grid">...
    # - Various inline styles

    # More robust: Find from <!-- SMART START BUNDLE --> to the next <!-- comment or <section

    pattern = r'<!-- SMART START BUNDLE.*?(?=<!-- [A-Z]|<section id=|$)'

    new_bundle = generate_new_bundle(lang)

    content = re.sub(pattern, new_bundle, content, flags=re.DOTALL)

    return content

def process_file(file_path, lang):
    """Process a single HTML file (skip index.html)"""
    try:
        # Skip index.html files
        if file_path.name == 'index.html':
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no Bundle
        if 'SMART START BUNDLE' not in original:
            return False

        # Check if Bundle already has the new format (max-width INSIDE Bundle section)
        # Extract Bundle section and check for max-width there
        bundle_pattern = r'<!-- SMART START BUNDLE.*?(?=<!-- [A-Z]|<section id=|$)'
        bundle_match = re.search(bundle_pattern, original, re.DOTALL)

        if bundle_match:
            bundle_section = bundle_match.group(0)
            # Check if THIS bundle section already has max-width: 1100px
            if 'max-width: 1100px' in bundle_section:
                print(f"Skipped (already updated): {file_path}")
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
    """Update Bundle on all service pages (not index.html)"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang_dir in lang_dirs:
        lang_path = base_dir / lang_dir
        if not lang_path.exists():
            continue

        # Find all HTML files except index.html
        html_files = [f for f in lang_path.glob('*.html') if f.name != 'index.html']

        for html_file in html_files:
            if process_file(html_file, lang_dir):
                print(f"[OK] Updated: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Bundle now has container + max-width: 1100px")
    print(f"Matches index.html format")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
