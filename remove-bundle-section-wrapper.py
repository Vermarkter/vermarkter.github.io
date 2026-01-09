#!/usr/bin/env python3
"""
Remove section wrapper from Smart Start Bundle on index.html files
Make structure same as service pages
"""

import re
from pathlib import Path

def remove_bundle_section_wrapper(content):
    """Remove the section + container wrapper from bundle"""

    # Pattern 1: Remove opening section + container
    pattern_start = r'        <!-- SMART START BUNDLE SECTION -->\s*\n\s*<section class="bundle-section"[^>]*>\s*\n\s*<div class="container">\s*\n\s*'
    replacement_start = '    <!-- SMART START BUNDLE -->\n                '

    content = re.sub(pattern_start, replacement_start, content)

    # Pattern 2: Remove closing container + section (before FAQ section)
    pattern_end = r'\s*</div>\s*\n\s*</section>\s*\n\s*\n\s*(<!-- FAQ SECTION -->)'
    replacement_end = r'\n\n    \1'

    content = re.sub(pattern_end, replacement_end, content)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has bundle-section
        if 'bundle-section' not in content:
            print(f"Skipped (no bundle-section): {file_path}")
            return False

        new_content = remove_bundle_section_wrapper(content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all index.html files"""
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
    print(f"Bundle now has same structure as service pages")

if __name__ == '__main__':
    main()
