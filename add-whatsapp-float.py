#!/usr/bin/env python3
"""
Add floating WhatsApp button to all HTML pages
"""

import re
from pathlib import Path

WHATSAPP_NUMBER = '4915510300538'

# Translations for button text
BUTTON_TEXT = {
    'de': 'Chat starten',
    'en': 'Start Chat',
    'pl': 'Rozpocznij czat',
    'ru': 'Начать чат',
    'tr': 'Sohbet Başlat',
    'ua': 'Почати чат'
}

def generate_whatsapp_float(lang):
    """Generate floating WhatsApp button HTML"""

    text = BUTTON_TEXT.get(lang, BUTTON_TEXT['en'])

    return f'''    <!-- FLOATING WHATSAPP BUTTON -->
    <div class="whatsapp-float">
        <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" class="whatsapp-button" aria-label="WhatsApp">
            <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
            </svg>
            <span class="whatsapp-button-text">{text}</span>
        </a>
    </div>

'''

def add_whatsapp_float(content, lang):
    """Add WhatsApp float button before closing body tag"""

    # Check if button already exists
    if 'class="whatsapp-float"' in content:
        return content, False

    # Pattern: Find </body> and add button before it
    pattern = r'(\s*)(</body>)'

    whatsapp_html = generate_whatsapp_float(lang)
    replacement = whatsapp_html + r'\1\2'

    new_content = re.sub(pattern, replacement, content)

    return new_content, (new_content != content)

def process_file(file_path, lang):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content, modified = add_whatsapp_float(original, lang)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add floating WhatsApp button to all HTML pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        html_files = list(lang_path.glob('*.html'))

        for html_file in html_files:
            if process_file(html_file, lang):
                print(f"[OK] Added WhatsApp float: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Added floating WhatsApp button")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
