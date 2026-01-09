#!/usr/bin/env python3
"""
Remove section + container wrapper from Bundle and add inline max-width
Match google-ads.html structure exactly
"""

import re
from pathlib import Path

def remove_bundle_wrapper(content):
    """Remove section + container wrapper, add inline styles"""

    # Pattern 1: Remove opening section + container before bundle
    pattern_start = r'(</section>\s*\n\s*\n)\s*<!-- SMART START BUNDLE -->\s*\n\s*<section[^>]*>\s*\n\s*<div class="container">\s*\n\s*<div class="service-card bundle-card"'
    replacement_start = r'\1    <!-- SMART START BUNDLE -->\n    <div class="service-card bundle-card"'

    content = re.sub(pattern_start, replacement_start, content)

    # Pattern 2: Add inline styles to bundle-card (margin and max-width)
    pattern_styles = r'(<div class="service-card bundle-card" style="[^"]*)(position: relative;)'
    replacement_styles = r'\1margin: 3rem auto; max-width: 1400px; \2'

    content = re.sub(pattern_styles, replacement_styles, content)

    # Pattern 3: Remove closing container + section after bundle
    pattern_end = r'(                    </div>\s*\n)\s*</div>\s*\n\s*</div>\s*\n\s*</section>\s*\n\s*\n\s*(<!-- FAQ SECTION -->)'
    replacement_end = r'\1    </div>\n\n    \2'

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

        new_content = remove_bundle_wrapper(content)

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
    lang_dirs = ['en', 'pl', 'ru', 'tr', 'ua']  # Skip DE as done manually

    modified_count = 0

    for lang_dir in lang_dirs:
        index_file = base_dir / lang_dir / 'index.html'
        if index_file.exists():
            if process_file(index_file):
                print(f"Fixed: {index_file}")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Bundle now matches google-ads.html structure (no container wrapper)")

if __name__ == '__main__':
    main()
