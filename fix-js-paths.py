#!/usr/bin/env python3
"""
Fix JS paths: ../JS/ -> ../js/ (case sensitivity fix)
"""

import re
from pathlib import Path

def fix_js_paths(content):
    """Replace uppercase JS with lowercase js in script tags"""

    # Pattern 1: ../JS/ -> ../js/
    content = re.sub(
        r'src="(\.\./)?JS/',
        r'src="\1js/',
        content
    )

    # Pattern 2: /JS/ -> /js/
    content = re.sub(
        r'src="/JS/',
        r'src="/js/',
        content
    )

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Check if file has uppercase JS paths
        if 'JS/calculator.js' not in original and 'JS/main.js' not in original:
            return False

        new_content = fix_js_paths(original)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"ERROR: {file_path}: {e}")
        return False

def main():
    """Fix JS paths in all HTML files"""
    base_dir = Path('.')
    modified_count = 0

    # Find all HTML files
    html_files = list(base_dir.glob('**/*.html'))

    print("="*60)
    print("FIXING JS PATHS: ../JS/ -> ../js/")
    print("="*60)

    for file_path in html_files:
        if '.git' in str(file_path):
            continue

        if process_file(file_path):
            print(f"FIXED: {file_path}")
            modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Changed: ../JS/calculator.js -> ../js/calculator.js")
    print(f"Changed: ../JS/main.js -> ../js/main.js")
    print(f"Changed: ../JS/chatbot.js -> ../js/chatbot.js")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
