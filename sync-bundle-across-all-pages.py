#!/usr/bin/env python3
"""
Sync Smart Start Bundle across all service pages
- Remove duplicate Bundles
- Place Bundle after pricing section
- Use new design from de/google-ads.html
"""

import re
from pathlib import Path

# Bundle HTML template (from de/google-ads.html)
BUNDLE_TEMPLATE = '''
    <!-- SMART START BUNDLE -->
    <section class="bundle-section" style="padding: 5rem 0; background: var(--bg-primary);">
        <div class="container" style="max-width: 1100px; margin: 0 auto;">
            <div class="bundle-card" style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 2px solid #3B82F6; border-radius: 24px; padding: 3rem; position: relative; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">

                <!-- Badge -->
                <div style="position: absolute; top: 30px; right: -35px; transform: rotate(45deg); background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; padding: 8px 50px; font-weight: 900; font-size: 0.75rem; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4); z-index: 10;">
                    BESTSELLER
                </div>

                <!-- Bundle Grid (2 columns on desktop, 1 on mobile) -->
                <div class="bundle-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 3rem; align-items: start;">

                    <!-- LEFT COLUMN: Pricing & CTA -->
                    <div style="text-align: center;">
                        <h2 style="font-size: 2rem; margin-bottom: 0.75rem; font-weight: 900;">
                            🚀 <span class="text-gradient">{bundle_title}</span>
                        </h2>
                        <p style="font-size: 1rem; opacity: 0.9; margin-bottom: 1.5rem;">{bundle_subtitle}</p>

                        <div style="margin-bottom: 1.5rem;">
                            <p style="font-size: 1.2rem; opacity: 0.6; text-decoration: line-through; margin-bottom: 0.25rem;">€1,097</p>
                            <p style="font-size: 3rem; font-weight: 900; margin: 0;">
                                <span class="text-gradient">€599</span>
                            </p>
                            <p style="color: #10B981; font-weight: 700; font-size: 1rem; margin-top: 0.5rem;">{savings_text}</p>
                        </div>

                        <a href="https://t.me/vermarkters_bot" target="_blank" class="btn btn-primary" style="display: inline-block; padding: 1rem 2.5rem; font-size: 1.1rem; font-weight: 700; background: linear-gradient(135deg, #3B82F6, #2563EB); box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);">
                            🎁 {cta_button}
                        </a>
                        <a href="https://wa.me/4915510300538" target="_blank" style="display: flex; align-items: center; justify-content: center; gap: 0.75rem; font-size: 1.15rem; color: #25D366; text-decoration: none; font-weight: 600; margin-top: 1rem;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                            </svg>
                            WhatsApp
                        </a>
                    </div>

                    <!-- RIGHT COLUMN: Bundle Contents -->
                    <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 1.75rem;">
                        <h3 style="font-size: 1.15rem; margin-bottom: 1.25rem; font-weight: 700; text-align: center;">{bundle_contains}</h3>
                        <div style="display: grid; gap: 1rem;">
                            <div style="display: flex; align-items: start; gap: 0.75rem;">
                                <span style="font-size: 1.3rem; flex-shrink: 0;">🎨</span>
                                <div style="text-align: left;">
                                    <strong style="font-size: 0.95rem;">{item1_title}</strong>
                                    <p style="opacity: 0.75; margin: 0.15rem 0 0; font-size: 0.85rem;">{value_label}: €199</p>
                                </div>
                            </div>
                            <div style="display: flex; align-items: start; gap: 0.75rem;">
                                <span style="font-size: 1.3rem; flex-shrink: 0;">📊</span>
                                <div style="text-align: left;">
                                    <strong style="font-size: 0.95rem;">{item2_title}</strong>
                                    <p style="opacity: 0.75; margin: 0.15rem 0 0; font-size: 0.85rem;">{value_label}: €399</p>
                                </div>
                            </div>
                            <div style="display: flex; align-items: start; gap: 0.75rem;">
                                <span style="font-size: 1.3rem; flex-shrink: 0;">🔗</span>
                                <div style="text-align: left;">
                                    <strong style="font-size: 0.95rem;">{item3_title}</strong>
                                    <p style="opacity: 0.75; margin: 0.15rem 0 0; font-size: 0.85rem;">{value_label}: €499</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Mobile Responsive -->
                <style>
                    @media (max-width: 768px) {
                        .bundle-grid {
                            grid-template-columns: 1fr !important;
                            gap: 2rem !important;
                        }
                    }
                </style>
            </div>
        </div>
    </section>
'''

# Translations
TRANSLATIONS = {
    'de': {
        'bundle_title': 'Smart Start Bundle',
        'bundle_subtitle': 'Landing Page + Google Ads + CRM-Integration',
        'savings_text': 'Sie sparen €498 (45%)',
        'cta_button': 'Bundle jetzt sichern',
        'bundle_contains': 'Das Bundle enthält:',
        'item1_title': 'Landing Page (Express)',
        'item2_title': 'Google Ads Setup (Pro)',
        'item3_title': 'CRM-Integration (Basic)',
        'value_label': 'Wert'
    },
    'en': {
        'bundle_title': 'Smart Start Bundle',
        'bundle_subtitle': 'Landing Page + Google Ads + CRM Integration',
        'savings_text': 'You save €498 (45%)',
        'cta_button': 'Get Bundle Now',
        'bundle_contains': 'The bundle includes:',
        'item1_title': 'Landing Page (Express)',
        'item2_title': 'Google Ads Setup (Pro)',
        'item3_title': 'CRM Integration (Basic)',
        'value_label': 'Value'
    },
    'pl': {
        'bundle_title': 'Smart Start Bundle',
        'bundle_subtitle': 'Landing Page + Google Ads + Integracja CRM',
        'savings_text': 'Oszczędzasz €498 (45%)',
        'cta_button': 'Zamów Teraz',
        'bundle_contains': 'Pakiet zawiera:',
        'item1_title': 'Landing Page (Express)',
        'item2_title': 'Google Ads Setup (Pro)',
        'item3_title': 'Integracja CRM (Basic)',
        'value_label': 'Wartość'
    },
    'ru': {
        'bundle_title': 'Smart Start Bundle',
        'bundle_subtitle': 'Landing Page + Google Ads + CRM-интеграция',
        'savings_text': 'Вы экономите €498 (45%)',
        'cta_button': 'Получить Bundle',
        'bundle_contains': 'Пакет включает:',
        'item1_title': 'Landing Page (Express)',
        'item2_title': 'Google Ads Setup (Pro)',
        'item3_title': 'CRM-интеграция (Basic)',
        'value_label': 'Стоимость'
    },
    'tr': {
        'bundle_title': 'Smart Start Bundle',
        'bundle_subtitle': 'Landing Page + Google Ads + CRM Entegrasyonu',
        'savings_text': '€498 tasarruf ediyorsunuz (45%)',
        'cta_button': 'Bundle\'ı Şimdi Alın',
        'bundle_contains': 'Paket içeriği:',
        'item1_title': 'Landing Page (Express)',
        'item2_title': 'Google Ads Setup (Pro)',
        'item3_title': 'CRM Entegrasyonu (Basic)',
        'value_label': 'Değer'
    },
    'ua': {
        'bundle_title': 'Smart Start Bundle',
        'bundle_subtitle': 'Landing Page + Google Ads + CRM-інтеграція',
        'savings_text': 'Ви економите €498 (45%)',
        'cta_button': 'Отримати Bundle',
        'bundle_contains': 'Пакет включає:',
        'item1_title': 'Landing Page (Express)',
        'item2_title': 'Google Ads Setup (Pro)',
        'item3_title': 'CRM-інтеграція (Basic)',
        'value_label': 'Вартість'
    }
}

def remove_all_bundles(content):
    """Remove ALL existing Bundle sections"""

    # Pattern 1: New card layout Bundle (multiple variations)
    patterns = [
        r'<!-- SMART START BUNDLE.*?</section>\s*\n',
        r'<section class="bundle-section".*?</section>\s*\n',
        r'<!-- Bundle Grid.*?</div>\s*</div>\s*\n'
    ]

    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)

    return content

def insert_bundle_after_pricing(content, lang):
    """Insert Bundle after pricing section"""

    t = TRANSLATIONS.get(lang, TRANSLATIONS['de'])

    # Replace placeholders manually (avoiding .format() conflicts with CSS)
    bundle_html = BUNDLE_TEMPLATE
    for key, value in t.items():
        bundle_html = bundle_html.replace(f'{{{key}}}', value)

    # Find pricing section closing
    # Pattern: </section> after "Preise" or "Pricing" or "Prices"
    pattern = r'(</section>\s*\n)(    <!-- [A-Z]|    <section id="contact")'

    # Check if we can find pricing section
    if not re.search(pattern, content):
        # Fallback: Insert before contact form
        pattern = r'(    <!-- CONTACT FORM -->)'
        replacement = bundle_html + r'\n\1'
    else:
        replacement = r'\1' + bundle_html + r'\n\2'

    content = re.sub(pattern, replacement, content, count=1)

    return content

def process_file(file_path, lang):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no pricing section (probably not a service page)
        if 'Preise' not in original and 'Pricing' not in original and 'Prices' not in original:
            return False

        # Remove all existing Bundles
        new_content = remove_all_bundles(original)

        # Insert new Bundle after pricing
        new_content = insert_bundle_after_pricing(new_content, lang)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Sync Bundle across all service pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    # Service pages to update
    service_pages = [
        'google-ads.html',
        'meta-ads.html',
        'tiktok-ads.html',
        'seo.html',
        'crm-integration.html',
        'website-development.html'
    ]

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        for service_page in service_pages:
            file_path = lang_path / service_page
            if file_path.exists():
                if process_file(file_path, lang):
                    print(f"[OK] Updated Bundle: {file_path}")
                    modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Bundle synced across all service pages")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
