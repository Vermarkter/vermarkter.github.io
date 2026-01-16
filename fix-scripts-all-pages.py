#!/usr/bin/env python3
"""
Fix script tags on all service pages
Replace old script.js with proper JS files
"""

import os
import re

# Files to fix
files_to_fix = [
    # DE
    "de/google-ads.html",
    "de/meta-ads.html",
    "de/tiktok-ads.html",
    "de/seo.html",
    # EN
    "en/google-ads.html",
    "en/meta-ads.html",
    "en/tiktok-ads.html",
    "en/seo.html",
    "en/website-development.html",
    # PL
    "pl/google-ads.html",
    "pl/meta-ads.html",
    "pl/tiktok-ads.html",
    "pl/seo.html",
    # RU
    "ru/google-ads.html",
    "ru/meta-ads.html",
    "ru/tiktok-ads.html",
    "ru/seo.html",
    "ru/website-development.html",
    # TR
    "tr/google-ads.html",
    "tr/meta-ads.html",
    "tr/tiktok-ads.html",
    "tr/seo.html",
    "tr/website-development.html",
    # UA (already fixed but check)
    "ua/seo.html",
]

# Old pattern to replace
OLD_SCRIPT = r'<script src="\.\./script\.js\?v=[^"]*"></script>'

# New scripts
NEW_SCRIPTS = """<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script src="../js/telegram-service.js"></script>
    <script src="../js/calculator.js"></script>
    <script src="../js/chatbot.js"></script>
    <script src="../js/main.js"></script>"""

def fix_file(filepath):
    """Fix scripts in a single file"""
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filepath} - not found")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if old script exists
    if not re.search(OLD_SCRIPT, content):
        # Check if already has calculator.js
        if 'calculator.js' in content:
            print(f"  [OK] {filepath} - already fixed")
            return False
        print(f"  [SKIP] {filepath} - no old script found")
        return False

    # Replace old script with new scripts
    new_content = re.sub(OLD_SCRIPT, NEW_SCRIPTS, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  [FIXED] {filepath}")
    return True

def main():
    print("=" * 50)
    print("Fixing script tags on service pages")
    print("=" * 50)

    fixed_count = 0

    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1

    print("=" * 50)
    print(f"Fixed {fixed_count} files")
    print("=" * 50)

if __name__ == "__main__":
    main()
