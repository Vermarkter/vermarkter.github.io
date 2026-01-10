#!/usr/bin/env python3
"""
Add closing </div> for nav-actions in index.html files
"""

import re
from pathlib import Path

def add_closing_div(content):
    """Add closing div for nav-actions"""

    # Pattern: Find the structure where we need to add closing div
    # </ul> (lang-dropdown)
    # </div> (lang-switcher)
    # </div> (controls)
    # [ADD HERE: </div> for nav-actions]
    # <button class="mobile-toggle"

    pattern = r'(</ul>\s*</div>\s*</div>)(\s*<button class="mobile-toggle")'

    # Check if already has 3 closing divs (meaning nav-actions is already closed)
    if re.search(r'</ul>\s*</div>\s*</div>\s*</div>\s*<button class="mobile-toggle"', content):
        return content, False

    replacement = r'\1\n                </div>\2'
    new_content = re.sub(pattern, replacement, content)

    return new_content, (new_content != content)

def process_file(file_path):
    """Process a single index.html file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if not index.html
        if file_path.name != 'index.html':
            return False

        # Skip if already has nav-actions closed
        if 'class="nav-actions"' not in original:
            return False

        new_content, modified = add_closing_div(original)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add closing nav-actions div on all index.html pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        index_file = lang_path / 'index.html'
        if index_file.exists():
            if process_file(index_file):
                print(f"[OK] Fixed: {index_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Added closing div for nav-actions")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
