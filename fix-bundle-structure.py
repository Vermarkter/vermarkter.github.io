#!/usr/bin/env python3
"""
Wrap Smart Start Bundle in proper section structure on index.html files
"""

import re
from pathlib import Path

def fix_bundle_structure(content):
    """Wrap bundle in section + container"""

    # Find the pattern: </section>\n\n    <!-- SMART START BUNDLE -->
    # and the bundle div without section wrapper

    # Pattern 1: Opening - after closing section, before bundle
    pattern_start = r'(</section>\s*\n\s*\n)\s*<!-- SMART START BUNDLE -->\s*\n\s*<div class="service-card bundle-card"'

    replacement_start = r'\1        <!-- SMART START BUNDLE SECTION -->\n        <section class="bundle-section" style="padding: 4rem 0; background: rgba(0,0,0,0.1);">\n            <div class="container">\n                <div class="service-card bundle-card"'

    content = re.sub(pattern_start, replacement_start, content)

    # Pattern 2: Closing - after bundle div, before FAQ section
    pattern_end = r'(                    </div>\s*\n\s*</div>\s*\n)\s*\n\s*(<!-- FAQ SECTION -->)'

    replacement_end = r'\1            </div>\n        </section>\n\n        \2'

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

        # Check if already has bundle-section
        if 'bundle-section' in content:
            print(f"Skipped (already fixed): {file_path}")
            return False

        new_content = fix_bundle_structure(content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all index.html files in language directories"""
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
    print(f"Bundle now wrapped in proper section structure")

if __name__ == '__main__':
    main()
