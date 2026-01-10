#!/usr/bin/env python3
"""
Add WhatsApp to contact section (after Telegram with chat icon)
"""

import re
from pathlib import Path

WHATSAPP_NUMBER = '4915510300538'

def add_whatsapp_to_contact_section(content):
    """Add WhatsApp after Telegram in contact section"""

    # Pattern: Find Telegram link with chat icon 💬 in paragraph
    # Then add WhatsApp after it
    pattern = r'(<p style="font-size: 1\.125rem; color: var\(--text-secondary\);">\s*💬 <a href="https://t\.me/vermarkters_bot"[^>]*>@vermarkters_bot</a>\s*</p>)\s*(</div>)'

    # Check if WhatsApp already exists nearby
    if re.search(r'💬.*?vermarkters_bot.*?📱.*?WhatsApp', content, re.DOTALL):
        return content, False

    whatsapp_html = f'''
                    <p style="font-size: 1.125rem; color: var(--text-secondary);">
                        📱 <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" style="color: var(--brand);">WhatsApp</a>
                    </p>
                    '''

    replacement = r'\1' + whatsapp_html + r'\2'
    new_content = re.sub(pattern, replacement, content)

    return new_content, (new_content != content)

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content, modified = add_whatsapp_to_contact_section(original)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add WhatsApp to contact section on all index.html pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        # Only process index.html
        index_file = lang_path / 'index.html'
        if index_file.exists():
            if process_file(index_file):
                print(f"[OK] Added WhatsApp: {index_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Added WhatsApp to contact section")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
