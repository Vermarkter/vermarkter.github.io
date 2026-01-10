#!/usr/bin/env python3
"""
Update calculator description on all language pages
Based on Ukrainian version
"""

import re
from pathlib import Path

# Translations for each language
DESCRIPTIONS = {
    'de': {
        'subtitle': 'Berechnen Sie die Rentabilität Ihrer Werbekampagne',
        'line1': '💡 <strong>Dies ist ein echtes Mediaplanungs-Tool.</strong><br>',
        'line2': 'Wir verwenden dieselben Formeln wie große Agenturen. Transparent, ehrlich, ohne versteckte Kosten.',
        'warning': '⚠️ Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.'
    },
    'en': {
        'subtitle': 'Calculate the profitability of your advertising campaign',
        'line1': '💡 <strong>This is a real media planning tool.</strong><br>',
        'line2': 'We use the same formulas as major agencies. Transparent, honest, no hidden costs.',
        'warning': '⚠️ The result is a forecast, not a promise. Marketing starts with honest numbers.'
    },
    'pl': {
        'subtitle': 'Oblicz rentowność swojej kampanii reklamowej',
        'line1': '💡 <strong>To prawdziwe narzędzie do planowania mediów.</strong><br>',
        'line2': 'Używamy tych samych formuł co duże agencje. Przejrzyście, uczciwie, bez ukrytych kosztów.',
        'warning': '⚠️ Wynik to prognoza, a nie obietnica. Marketing zaczyna się od uczciwych liczb.'
    },
    'ru': {
        'subtitle': 'Рассчитайте рентабельность вашей рекламной кампании',
        'line1': '💡 <strong>Это реальный инструмент медиапланирования.</strong><br>',
        'line2': 'Мы используем те же формулы, что и крупные агентства. Прозрачно, честно, без скрытых расходов.',
        'warning': '⚠️ Результат — это прогноз, а не обещание. Маркетинг начинается с честных цифр.'
    },
    'tr': {
        'subtitle': 'Reklam kampanyanızın karlılığını hesaplayın',
        'line1': '💡 <strong>Bu gerçek bir medya planlama aracıdır.</strong><br>',
        'line2': 'Büyük ajanslarla aynı formülleri kullanıyoruz. Şeffaf, dürüst, gizli maliyet yok.',
        'warning': '⚠️ Sonuç bir tahmindir, söz değil. Pazarlama dürüst rakamlarla başlar.'
    },
    'ua': {
        'subtitle': 'Розрахуйте рентабельність вашої рекламної кампанії',
        'line1': '💡 <strong>Це реальний інструмент медіапланування.</strong><br>',
        'line2': 'Ми використовуємо ті самі формули, що й великі агенції. Прозоро, чесно, без прихованих витрат.',
        'warning': '⚠️ Результат є прогнозом, а не обіцянкою. Маркетинг починається з чесних цифр.'
    }
}

def generate_new_description(lang):
    """Generate new calculator description HTML"""
    t = DESCRIPTIONS[lang]

    return f'''                    <p class="calculator__subtitle" style="margin-bottom: 20px;">
                        {t['subtitle']}
                    </p>

                    <!-- БЛОК ДОВІРИ / TRUST BLOCK -->
                    <div style="max-width: 700px; margin: 0 auto; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); padding: 15px; border-radius: 12px;">
                        <p style="margin: 0; color: #F8FAFC; font-size: 15px; line-height: 1.6;">
                            {t['line1']}
                            {t['line2']}
                        </p>
                    </div>'''

def update_calculator_description(content, lang):
    """Replace old calculator subtitle with new description block"""

    # Pattern 1: Find old subtitle (single line, various texts)
    # Match from <p class="calculator__subtitle"> to </p> (before <div class="calculator__grid">)
    pattern = r'(<h2 class="calculator__title">.*?</h2>\s*)\n\s*<p class="calculator__subtitle">.*?</p>'

    new_desc = generate_new_description(lang)

    # Replace with new description
    content = re.sub(
        pattern,
        r'\1\n' + new_desc,
        content,
        flags=re.DOTALL
    )

    return content

def process_file(file_path, lang):
    """Process a single index.html file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no calculator found
        if 'calculator__title' not in original:
            return False

        # Skip if already has trust block
        if 'БЛОК ДОВІРИ' in original or 'TRUST BLOCK' in original:
            print(f"Skipped (already updated): {file_path}")
            return False

        new_content = update_calculator_description(original, lang)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Update calculator descriptions in all language versions"""
    base_dir = Path('.')
    lang_dirs = {
        'de': 'de',
        'en': 'en',
        'pl': 'pl',
        'ru': 'ru',
        'tr': 'tr',
        'ua': 'ua'
    }

    modified_count = 0

    for lang, lang_dir in lang_dirs.items():
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file, lang):
                print(f"[OK] Updated: {index_file} ({lang.upper()})")
                modified_count += 1

    print(f"\n{'='*50}")
    print(f"Modified {modified_count} files")
    print(f"Added trust block to calculator descriptions")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
