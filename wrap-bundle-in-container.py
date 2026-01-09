#!/usr/bin/env python3
"""
Wrap Smart Start Bundle in section + container on all index.html files
This ensures proper max-width and centering
"""

import re
from pathlib import Path

def wrap_bundle_in_container(content):
    """Wrap bundle in section + container if not already wrapped"""

    # Check if already wrapped in section (look for section tag RIGHT AFTER comment)
    if re.search(r'<!-- SMART START BUNDLE -->\s*\n\s*<section', content):
        print("Already wrapped")
        return content

    # Pattern 1: Add section + container before bundle
    pattern_start = r'(</section>\s*\n\s*\n)\s*<!-- SMART START BUNDLE -->\s*\n\s*<div class="service-card bundle-card"'
    replacement_start = r'\1    <!-- SMART START BUNDLE -->\n        <section style="padding: 3rem 0;">\n            <div class="container">\n                <div class="service-card bundle-card"'

    content = re.sub(pattern_start, replacement_start, content)

    # Pattern 2: Close container + section after bundle (before FAQ)
    pattern_end = r'(                    </div>\s*\n\s*</div>\s*\n)\s*\n\s*(<!-- FAQ SECTION -->)'
    replacement_end = r'\1            </div>\n        </section>\n\n    \2'

    content = re.sub(pattern_end, replacement_end, content)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has Smart Start Bundle
        if 'SMART START BUNDLE' not in content:
            return False

        new_content = wrap_bundle_in_container(content)

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
    lang_dirs = ['en', 'pl', 'ru', 'tr', 'ua']  # Skip 'de' as we already did it manually

    modified_count = 0

    for lang_dir in lang_dirs:
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file):
                print(f"Fixed: {index_file}")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Bundle now wrapped in section + container for proper width")

if __name__ == '__main__':
    main()
