#!/usr/bin/env python3
"""
Fix all favicon issues:
1. Replace favicon.ico → favicon.svg
2. Add cache busting version
3. Remove duplicate inline SVG data URIs
4. Add missing favicon links
"""

import re
from pathlib import Path
import time

# Current timestamp for cache busting
VERSION = str(int(time.time()))

def replace_ico_with_svg(content):
    """Replace favicon.ico references with favicon.svg"""

    # Pattern 1: ../favicon.ico → ../favicon.svg?v=VERSION
    content = re.sub(
        r'href="(\.\./)?favicon\.ico"',
        rf'href="\1favicon.svg?v={VERSION}"',
        content
    )

    # Pattern 2: /favicon.ico → /favicon.svg?v=VERSION (absolute paths)
    content = re.sub(
        r'href="/favicon\.ico"',
        rf'href="/favicon.svg?v={VERSION}"',
        content
    )

    # Pattern 3: favicon.ico (no path) → favicon.svg?v=VERSION
    content = re.sub(
        r'href="favicon\.ico"',
        rf'href="favicon.svg?v={VERSION}"',
        content
    )

    return content

def remove_duplicate_inline_svg(content):
    """Remove duplicate inline SVG data URI favicon links"""

    # Find and remove lines like: <link rel="icon" href="data:image/svg+xml,...">
    content = re.sub(
        r'\s*<link\s+rel="icon"\s+href="data:image/svg\+xml[^"]*">\s*\n',
        '',
        content
    )

    return content

def add_cache_busting_to_svg(content):
    """Add version parameter to existing favicon.svg links (without ?v=)"""

    # Only add version if it doesn't already have one
    # Pattern: href="../favicon.svg" (without ?v=)
    content = re.sub(
        r'href="([^"]*favicon\.svg)"(?!\?v=)',
        rf'href="\1?v={VERSION}"',
        content
    )

    return content

def has_favicon_links(content):
    """Check if file has any favicon links"""
    return bool(re.search(r'<link[^>]*rel="icon"', content))

def add_missing_favicon(content, file_path):
    """Add favicon links to files that don't have them"""

    # Skip if already has favicon
    if has_favicon_links(content):
        return content

    # Determine correct path based on file location
    path_parts = Path(file_path).parts
    if len(path_parts) > 1:  # File is in subdirectory
        favicon_path = '../favicon.svg?v=' + VERSION
    else:  # File is at root
        favicon_path = 'favicon.svg?v=' + VERSION

    # Create favicon links
    favicon_html = f'''    <link rel="icon" type="image/svg+xml" href="{favicon_path}">
    <link rel="apple-touch-icon" sizes="180x180" href="{favicon_path}">
'''

    # Try to insert after <title> or <meta charset>
    # Pattern 1: After </title>
    if '</title>' in content:
        content = re.sub(
            r'(</title>\s*\n)',
            r'\1' + favicon_html,
            content,
            count=1
        )
    # Pattern 2: After <meta charset>
    elif '<meta charset' in content:
        content = re.sub(
            r'(<meta charset[^>]*>\s*\n)',
            r'\1' + favicon_html,
            content,
            count=1
        )
    # Pattern 3: After <head>
    elif '<head>' in content:
        content = re.sub(
            r'(<head>\s*\n)',
            r'\1' + favicon_html,
            content,
            count=1
        )

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content = original

        # Step 1: Replace .ico with .svg
        new_content = replace_ico_with_svg(new_content)

        # Step 2: Remove duplicate inline SVG data URIs
        new_content = remove_duplicate_inline_svg(new_content)

        # Step 3: Add cache busting to existing .svg links
        new_content = add_cache_busting_to_svg(new_content)

        # Step 4: Add missing favicon links
        new_content = add_missing_favicon(new_content, file_path)

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
    print(f"Cache version: {VERSION}\n")

    for html_file in html_files:
        if process_file(html_file):
            print(f"Updated: {html_file}")
            modified_count += 1

    print(f"\n========================================")
    print(f"Modified {modified_count} files")
    print(f"All favicon.ico links replaced with favicon.svg")
    print(f"Cache busting version: ?v={VERSION}")
    print(f"========================================")

if __name__ == '__main__':
    main()
