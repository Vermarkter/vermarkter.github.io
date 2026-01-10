#!/usr/bin/env python3
"""
Properly fix header structure and add Telegram/WhatsApp buttons
"""

import re
from pathlib import Path

WHATSAPP_NUMBER = '4915510300538'
TELEGRAM_BOT = 'vermarkters_bot'

def fix_index_header(content, lang):
    """Fix header structure on index.html files"""

    # Check if already has nav-actions
    if 'class="nav-actions"' in content:
        return content

    # Pattern: Find the wrongly placed buttons and controls div
    # Remove wrongly placed buttons
    pattern_wrong_buttons = r'\s*<!-- Contact Buttons -->\s*<a href="https://t\.me/[^"]*"[^>]*>Telegram</a>\s*<a href="https://wa\.me/[^"]*"[^>]*>WhatsApp</a>\s*'
    content = re.sub(pattern_wrong_buttons, '\n', content)

    # Find controls div and wrap it with nav-actions, adding buttons
    pattern_controls = r'(\s*)(<div class="controls" style="display:flex; gap:15px; align-items:center;">)'

    nav_actions_html = f'''
                <!-- Language + CTA -->
                <div class="nav-actions">
                    <a href="https://t.me/{TELEGRAM_BOT}" target="_blank" class="btn btn-primary">Telegram</a>
                    <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" class="btn btn-secondary" style="margin-left: 10px;">WhatsApp</a>
                    '''

    # Replace controls div start
    replacement = r'\1' + nav_actions_html + r'\2'
    content = re.sub(pattern_controls, replacement, content)

    # Find end of controls div (after lang-switcher) and add closing div for nav-actions
    # Pattern: Find </div> that closes lang-switcher, then </div> that closes controls
    # After that, add </div> for nav-actions
    pattern_close = r'(</ul>\s*</div>\s*</div>)(\s*<button class="mobile-toggle")'
    replacement_close = r'\1\n                </div>\2'
    content = re.sub(pattern_close, replacement_close, content)

    return content

def process_file(file_path, lang):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Only fix index.html files (they have different structure)
        if file_path.name != 'index.html':
            return False

        new_content = fix_index_header(original, lang)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix header structure on all index.html pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        index_file = lang_path / 'index.html'
        if index_file.exists():
            if process_file(index_file, lang):
                print(f"[OK] Fixed: {index_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Fixed header structure with proper nav-actions")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
