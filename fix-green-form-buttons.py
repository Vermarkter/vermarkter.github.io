#!/usr/bin/env python3
"""
Change green form buttons to blue gradient
"""

import re
from pathlib import Path

def fix_green_button(content):
    """Replace green gradient with blue gradient in form buttons"""

    # Pattern: Find green gradient buttons (with or without !important)
    # Green: #10B981, #059669
    # Blue: #3B82F6, #2563EB

    modified = False

    # Pattern 1: With !important
    pattern1 = r'background: linear-gradient\(135deg, #10B981, #059669\) !important;'
    if re.search(pattern1, content):
        content = re.sub(pattern1, 'background: linear-gradient(135deg, #3B82F6, #2563EB) !important;', content)
        modified = True

    # Pattern 2: Without !important
    pattern2 = r'background: linear-gradient\(135deg, #10B981, #059669\);'
    if re.search(pattern2, content):
        content = re.sub(pattern2, 'background: linear-gradient(135deg, #3B82F6, #2563EB);', content)
        modified = True

    # Pattern 3: Fix box-shadow
    pattern3 = r'box-shadow: 0 8px (24|30)px rgba\(16, 185, 129, 0\.4\)'
    if re.search(pattern3, content):
        content = re.sub(pattern3, r'box-shadow: 0 8px \1px rgba(59, 130, 246, 0.4)', content)
        modified = True

    return content, modified

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content, modified = fix_green_button(original)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix green buttons across all pages"""
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

            if process_file(html_file):
                print(f"[OK] Fixed green button: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print("Green form buttons -> Blue gradient")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
