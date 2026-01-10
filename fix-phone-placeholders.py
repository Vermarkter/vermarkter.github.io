#!/usr/bin/env python3
"""
Fix phone number placeholders in all contact forms
Replace with simple, example international numbers
"""

import re
from pathlib import Path

# Phone placeholders by language
PHONE_PLACEHOLDERS = {
    'de': '+49 123 456 789',
    'en': '+49 123 456 789',  # International example
    'pl': '+48 123 456 789',
    'ru': '+7 123 456 789',
    'tr': '+90 123 456 789',
    'ua': '+380 12 345 6789'
}

def fix_phone_placeholder(content, lang):
    """Replace phone placeholder with simple example number"""

    placeholder = PHONE_PLACEHOLDERS.get(lang, '+49 123 456 789')

    # Pattern: Find all phone input placeholders
    pattern = r'(type="tel"[^>]*placeholder=")[^"]+(")'

    replacement = rf'\1{placeholder}\2'
    new_content = re.sub(pattern, replacement, content)

    return new_content, (new_content != content)

def process_file(file_path, lang):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content, modified = fix_phone_placeholder(original, lang)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix phone placeholders in all HTML files"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        html_files = list(lang_path.glob('*.html'))

        for html_file in html_files:
            # Skip backup files
            if '.backup' in html_file.name or '.old' in html_file.name:
                continue

            if process_file(html_file, lang):
                print(f"[OK] Fixed phone placeholder: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Phone placeholders updated to simple example numbers")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
