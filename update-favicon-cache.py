#!/usr/bin/env python3
"""
Add cache busting version to favicon links
"""

import re
from pathlib import Path
import time

# Current timestamp for cache busting
VERSION = str(int(time.time()))

def update_favicon_links(content):
    """Add version parameter to favicon links"""

    # Pattern 1: <link rel="icon" ... href="../favicon.svg">
    content = re.sub(
        r'(<link\s+rel="icon"[^>]*href=")([^"]*favicon\.svg)(")',
        rf'\1\2?v={VERSION}\3',
        content
    )

    # Pattern 2: <link rel="apple-touch-icon" ... href="../favicon.svg">
    content = re.sub(
        r'(<link\s+rel="apple-touch-icon"[^>]*href=")([^"]*favicon\.svg)(")',
        rf'\1\2?v={VERSION}\3',
        content
    )

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Check if favicon links exist
        if 'favicon.svg' not in original:
            return False

        # Update
        new_content = update_favicon_links(original)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Process all HTML files"""
    base_dir = Path('.')
    modified_count = 0

    # Find all HTML files
    html_files = list(base_dir.glob('**/*.html'))

    print(f"Processing {len(html_files)} HTML files...")
    print(f"Cache version: {VERSION}")

    for html_file in html_files:
        if process_file(html_file):
            print(f"Updated: {html_file}")
            modified_count += 1

    print(f"\nModified {modified_count} files")

if __name__ == '__main__':
    main()
