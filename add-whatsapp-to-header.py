#!/usr/bin/env python3
"""
Add WhatsApp button next to Telegram in header navigation
"""

import re
from pathlib import Path

def add_whatsapp_button(content):
    """Add WhatsApp button after Telegram in header"""

    # Pattern: Find Telegram button in header (nav-actions section)
    # <a href="https://t.me/vermarkters_bot" ... class="btn btn-primary">Telegram</a>
    # Add WhatsApp button after it

    pattern = r'(<a href="https://t\.me/vermarkters_bot"[^>]*class="btn btn-primary">Telegram</a>)'

    whatsapp_btn = r'\1\n                    <a href="https://wa.me/4915510300538" target="_blank" class="btn btn-secondary" style="margin-left: 10px;">WhatsApp</a>'

    content = re.sub(pattern, whatsapp_btn, content)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no Telegram button in header
        if 't.me/vermarkters_bot' not in original or 'btn btn-primary">Telegram<' not in original:
            return False

        # Skip if already has WhatsApp in header (near Telegram)
        if 'wa.me/4915510300538' in original and 'btn btn-secondary">WhatsApp<' in original:
            telegram_pos = original.find('btn btn-primary">Telegram<')
            whatsapp_pos = original.find('btn btn-secondary">WhatsApp<')
            # Check if WhatsApp is within 200 chars of Telegram (in header)
            if abs(telegram_pos - whatsapp_pos) < 200:
                print(f"Skipped (already has WhatsApp): {file_path}")
                return False

        new_content = add_whatsapp_button(original)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add WhatsApp to header on all pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang_dir in lang_dirs:
        lang_path = base_dir / lang_dir
        if not lang_path.exists():
            continue

        html_files = list(lang_path.glob('*.html'))

        for html_file in html_files:
            if process_file(html_file):
                print(f"[OK] Added WhatsApp: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"WhatsApp button added next to Telegram in header")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
