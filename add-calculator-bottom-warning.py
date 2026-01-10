#!/usr/bin/env python3
"""
Add warning text UNDER the calculator (after results, before closing tags)
UA already has it, need to add to DE, EN, PL, RU, TR
"""

import re
from pathlib import Path

# Warning texts for each language
WARNINGS = {
    'de': '⚠️ Das Ergebnis ist eine Prognose, kein Versprechen. Marketing beginnt mit ehrlichen Zahlen.',
    'en': '⚠️ The result is a forecast, not a promise. Marketing starts with honest numbers.',
    'pl': '⚠️ Wynik to prognoza, a nie obietnica. Marketing zaczyna się od uczciwych liczb.',
    'ru': '⚠️ Результат — это прогноз, а не обещание. Маркетинг начинается с честных цифр.',
    'tr': '⚠️ Sonuç bir tahmindir, söz değil. Pazarlama dürüst rakamlarla başlar.',
    'ua': '⚠️ Результат є прогнозом, а не обіцянкою. Маркетинг починається з чесних цифр.'
}

def add_bottom_warning(content, lang):
    """Add warning paragraph at the bottom of calculator section"""

    warning_text = WARNINGS[lang]

    # HTML for warning paragraph
    warning_html = f'''
                <p class="text-center" style="margin-top: 30px; color: #94A3B8; font-size: 14px;">
                    {warning_text}
                </p>'''

    # Find calculator section specifically using id="resultProfit"
    # Then insert warning after the closing </div> tags of calculator__grid
    # But before the closing </div> of calculator container

    # Pattern: Look for resultProfit (last result card), then find the closing structure
    # </div> (result-card close)
    # </div> (results close)
    # </div> (grid close) <- INSERT AFTER THIS
    # </div> (calculator close)

    # More specific: find the closing div structure after resultProfit
    pattern = r'(<div class="calculator__result-value" id="resultProfit">€0</div>\s*</div>\s*</div>\s*</div>\s*)(</div>\s*</div>\s*</section>)'

    replacement = r'\1' + warning_html + r'\n            \2'

    content = re.sub(pattern, replacement, content)

    return content

def process_file(file_path, lang):
    """Process a single index.html file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no calculator section
        if 'id="calculator-section"' not in original:
            print(f"Skipped (no calculator): {file_path}")
            return False

        # Skip if already has bottom warning (check for margin-top: 30px pattern)
        if 'margin-top: 30px; color: #94A3B8' in original:
            print(f"Skipped (already has bottom warning): {file_path}")
            return False

        new_content = add_bottom_warning(original, lang)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add bottom warning to calculator on all languages (skip UA - already has it)"""
    base_dir = Path('.')

    # All languages including UA (but UA will be skipped by check)
    lang_map = {
        'de': 'de',
        'en': 'en',
        'pl': 'pl',
        'ru': 'ru',
        'tr': 'tr',
        'ua': 'ua'
    }

    modified_count = 0

    for lang, lang_dir in lang_map.items():
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file, lang):
                print(f"[OK] Added bottom warning: {index_file} ({lang.upper()})")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Added warning text UNDER calculator")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
