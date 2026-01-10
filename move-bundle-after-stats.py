#!/usr/bin/env python3
"""
Move Bundle section to appear right after stats cards
(after 420% ROAS, 92%, 7 days stats)
"""

import re
from pathlib import Path

def move_bundle_after_stats(content):
    """Extract Bundle and insert it after stats section"""

    # Pattern 1: Extract Bundle section
    bundle_pattern = r'    <!-- SMART START BUNDLE.*?</section>\n'
    bundle_match = re.search(bundle_pattern, content, re.DOTALL)

    if not bundle_match:
        return content, False

    bundle_section = bundle_match.group(0)

    # Pattern 2: Find stats section closing (after the stats grid)
    # Look for: </div> (stats close) + </div> (container) + </section> (hero section)
    # Then insert Bundle BEFORE the next section

    # More specific: Find closing of hero/stats section, which has stats-grid
    # After stats cards there's: </section> followed by next section (PROBLEM or other)

    # Find: end of stats section (containing "durchschn. ROAS" or similar stats)
    stats_pattern = r'(                </div>\n            </div>\n        </section>\n)\n(        <!-- PROBLEM|        <!-- SERVICES|        <section)'

    # Check if Bundle is already right after stats
    if re.search(stats_pattern + r'\n    <!-- SMART START BUNDLE', content):
        return content, False  # Already in correct position

    # Remove Bundle from current position
    content_no_bundle = re.sub(bundle_pattern, '', content, flags=re.DOTALL)

    # Insert Bundle after stats section
    def insert_bundle(match):
        return match.group(1) + '\n' + bundle_section + match.group(2)

    new_content = re.sub(stats_pattern, insert_bundle, content_no_bundle)

    return new_content, (new_content != content)

def process_file(file_path):
    """Process a single index.html file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no Bundle
        if 'SMART START BUNDLE' not in original:
            return False

        # Skip if not index.html (only move on main pages)
        if not file_path.name == 'index.html':
            return False

        new_content, modified = move_bundle_after_stats(original)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Move Bundle after stats on all index.html pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang_dir in lang_dirs:
        lang_path = base_dir / lang_dir
        if not lang_path.exists():
            continue

        index_file = lang_path / 'index.html'
        if index_file.exists():
            if process_file(index_file):
                print(f"[OK] Moved Bundle: {index_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Bundle now appears right after stats (420%, 92%, 7)")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
