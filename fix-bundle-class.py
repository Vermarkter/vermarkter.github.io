#!/usr/bin/env python3
"""
Remove service-card class from Bundle to fix grid layout
"""

import re
from pathlib import Path

def fix_bundle_class(content):
    """Replace 'service-card bundle-card' with just 'bundle-card'"""

    # Pattern: class="service-card bundle-card"
    content = re.sub(
        r'class="service-card bundle-card"',
        'class="bundle-card"',
        content
    )

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Check if file has the problematic class
        if 'service-card bundle-card' not in original:
            return False

        new_content = fix_bundle_class(original)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix Bundle class in all index.html files"""
    base_dir = Path('.')
    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    modified_count = 0

    for lang_dir in lang_dirs:
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file):
                print(f"Fixed: {index_file}")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Bundle now displays as 2-column grid (fixed flex-column issue)")

if __name__ == '__main__':
    main()
