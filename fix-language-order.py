#!/usr/bin/env python3
"""
Fix language order in all HTML files to alphabetical: DE, EN, PL, RU, TR, UA
"""

import os
import re
from pathlib import Path

# Language order patterns (UA first -> DE first)
LANG_PATTERNS = [
    ('ua', 'Ukrainian', '#0057B7", "#FFD700'),
    ('en', 'English', '#012169'),
    ('pl', 'Polish', '#fff", "#DC143C'),
    ('ru', 'Russian', '#fff", "#0039A6", "#D52B1E'),
    ('tr', 'Turkish', '#E30A17", "#fff')
]

def fix_lang_dropdown_order(content):
    """Reorder languages in lang-dropdown from UA-first to DE-first (alphabetical)"""

    # Find the lang-dropdown section
    dropdown_pattern = r'(<ul class="lang-dropdown">)(.*?)(</ul>)'

    match = re.search(dropdown_pattern, content, re.DOTALL)
    if not match:
        return content

    start_tag = match.group(1)
    dropdown_content = match.group(2)
    end_tag = match.group(3)

    # Extract individual language items
    lang_items = {}

    # Pattern to match each <li><a> block
    li_pattern = r'<li><a href="\.\./(ua|de|en|pl|ru|tr)/">(.*?)</a></li>'

    for li_match in re.finditer(li_pattern, dropdown_content, re.DOTALL):
        lang_code = li_match.group(1)
        full_content = li_match.group(0)
        lang_items[lang_code] = full_content

    # Check if we have all items
    if len(lang_items) < 5:  # Should have at least 5 (all except current page's language)
        return content

    # Rebuild in correct order: DE, EN, PL, RU, TR, UA
    correct_order = ['de', 'en', 'pl', 'ru', 'tr', 'ua']
    new_dropdown_content = '\n'

    for lang_code in correct_order:
        if lang_code in lang_items:
            new_dropdown_content += '                            ' + lang_items[lang_code] + '\n'

    new_dropdown_content += '                        '

    # Replace in original content
    new_content = content.replace(
        start_tag + dropdown_content + end_tag,
        start_tag + new_dropdown_content + end_tag
    )

    return new_content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if file has lang-dropdown
        if 'lang-dropdown' not in content:
            return False

        new_content = fix_lang_dropdown_order(content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all HTML files in language directories"""
    base_dir = Path('.')
    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    modified_count = 0

    for lang_dir in lang_dirs:
        dir_path = base_dir / lang_dir
        if not dir_path.exists():
            continue

        for html_file in dir_path.glob('*.html'):
            if process_file(html_file):
                print(f"Fixed: {html_file}")
                modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"Language order is now: DE, EN, PL, RU, TR, UA (alphabetical)")

if __name__ == '__main__':
    main()
