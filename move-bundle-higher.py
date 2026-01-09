#!/usr/bin/env python3
"""
Move Smart Start Bundle higher on google-ads.html pages
Place it right after Hero section, before Kampagnentypen
"""

import re
from pathlib import Path

def move_bundle_higher(content):
    """Move bundle from before contact form to after hero section"""

    # Step 1: Extract the entire Bundle HTML
    bundle_pattern = r'(    <!-- SMART START BUNDLE -->.*?                </div>\s*\n\s*\n)'
    bundle_match = re.search(bundle_pattern, content, re.DOTALL)

    if not bundle_match:
        print("Bundle not found")
        return content

    bundle_html = bundle_match.group(1)

    # Step 2: Remove Bundle from current location
    content = re.sub(bundle_pattern, '', content, flags=re.DOTALL)

    # Step 3: Insert Bundle after Hero section (before KAMPAGNENTYPEN)
    insertion_pattern = r'(    </section>\s*\n\s*\n)(    <!-- KAMPAGNENTYPEN -->)'
    replacement = r'\1' + bundle_html + r'\n\2'

    content = re.sub(insertion_pattern, replacement, content)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has Smart Start Bundle
        if 'SMART START BUNDLE' not in content:
            return False

        new_content = move_bundle_higher(content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process google-ads.html files in all languages"""
    base_dir = Path('.')
    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    modified_count = 0

    for lang_dir in lang_dirs:
        google_ads_file = base_dir / lang_dir / 'google-ads.html'
        if google_ads_file.exists():
            if process_file(google_ads_file):
                print(f"Fixed: {google_ads_file}")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Bundle now appears right after Hero section")

if __name__ == '__main__':
    main()
