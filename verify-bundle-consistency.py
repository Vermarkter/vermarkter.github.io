#!/usr/bin/env python3
"""
Verify all Bundle sections have max-width: 1100px
"""

import re
from pathlib import Path

def main():
    base_dir = Path('.')
    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    total_files = 0
    correct_files = 0
    missing_files = []

    for lang_dir in lang_dirs:
        lang_path = base_dir / lang_dir
        if not lang_path.exists():
            continue

        html_files = list(lang_path.glob('*.html'))

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Skip if no Bundle
                if 'SMART START BUNDLE' not in content:
                    continue

                total_files += 1

                # Extract Bundle section
                pattern = r'<!-- SMART START BUNDLE.*?(?=<!-- [A-Z]|<section id=|$)'
                bundle_match = re.search(pattern, content, re.DOTALL)

                if bundle_match:
                    bundle_section = bundle_match.group(0)
                    if 'max-width: 1100px' in bundle_section:
                        correct_files += 1
                    else:
                        missing_files.append(str(html_file))

            except Exception as e:
                print(f"Error reading {html_file}: {e}")

    print(f"{'='*60}")
    print(f"Bundle Consistency Check")
    print(f"{'='*60}")
    print(f"Total files with Bundle: {total_files}")
    print(f"Files with max-width: 1100px: {correct_files}")
    print(f"Match: {'YES ✓' if correct_files == total_files else 'NO ✗'}")

    if missing_files:
        print(f"\nMissing max-width in:")
        for f in missing_files:
            print(f"  - {f}")
    else:
        print(f"\n✓ All {total_files} files have consistent Bundle format!")

if __name__ == '__main__':
    main()
