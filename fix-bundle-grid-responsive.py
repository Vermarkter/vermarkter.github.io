#!/usr/bin/env python3
"""
Remove inline grid styles from bundle-grid to allow CSS media queries to work
"""

import re
from pathlib import Path

def fix_bundle_grid_inline_styles(content):
    """Remove inline grid styles from bundle-grid divs"""

    # Pattern: <div class="bundle-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
    # Replace with: <div class="bundle-grid">

    pattern = r'<div class="bundle-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">'
    replacement = r'<div class="bundle-grid">'

    content = re.sub(pattern, replacement, content)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has bundle-grid with inline styles
        if 'bundle-grid' not in content:
            return False

        if 'style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;"' not in content:
            print(f"Skipped (no inline styles): {file_path}")
            return False

        new_content = fix_bundle_grid_inline_styles(content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all HTML files with bundle-grid"""
    base_dir = Path('.')

    # Find all HTML files with bundle-grid
    patterns = [
        'de/*.html',
        'en/*.html',
        'pl/*.html',
        'ru/*.html',
        'tr/*.html',
        'ua/*.html'
    ]

    modified_count = 0

    for pattern in patterns:
        for html_file in base_dir.glob(pattern):
            if process_file(html_file):
                print(f"Fixed: {html_file}")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Bundle grid now uses CSS media queries for responsive layout")

if __name__ == '__main__':
    main()
