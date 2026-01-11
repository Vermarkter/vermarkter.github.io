#!/usr/bin/env python3
"""
Fix Telegram links issue:
1. Remove Telegram links from pricing cards - replace with #contact
2. Make entire Bundle card clickable (wrap in <a href="#contact">)
"""

import re
from pathlib import Path

def fix_pricing_telegram_links(content):
    """Replace Telegram links in pricing card wrappers with #contact"""

    # Pattern: Find pricing card wrappers with Telegram links
    # <a href="https://t.me/vermarkters_bot" target="_blank" class="pricing-card-link">

    # Replace Telegram link with #contact in pricing-card-link anchors
    pattern = r'<a href="https://t\.me/vermarkters_bot"([^>]*class="pricing-card-link"[^>]*)>'
    replacement = r'<a href="#contact"\1>'

    new_content = re.sub(pattern, replacement, content)

    return new_content

def fix_bundle_telegram_link(content):
    """Replace Telegram link in Bundle with #contact and make entire card clickable"""

    # Step 1: Find the Bundle section
    # Try pattern 1: bundle-card class
    bundle_pattern = r'(<!-- SMART START BUNDLE.*?<section[^>]*>.*?<div class="container"[^>]*>\s*)(<div[^>]*class="[^"]*bundle-card[^"]*"[^>]*>)(.*?)(</div>\s*</div>\s*</section>)'
    bundle_match = re.search(bundle_pattern, content, re.DOTALL)

    if not bundle_match:
        # Try pattern 2: inline style with gradient background (service pages)
        bundle_pattern = r'(<!-- SMART START BUNDLE[^>]*?-->.*?<section[^>]*>.*?<div class="container"[^>]*>\s*)(<div style="background: linear-gradient[^>]*?>)(.*?)(</div>\s*</div>\s*</section>)'
        bundle_match = re.search(bundle_pattern, content, re.DOTALL)

    if not bundle_match:
        return content

    before_bundle_card = bundle_match.group(1)
    bundle_card_opening = bundle_match.group(2)
    bundle_card_content = bundle_match.group(3)
    bundle_closing = bundle_match.group(4)

    # Step 2: Replace Telegram link inside bundle with #contact
    bundle_card_content = re.sub(
        r'<a href="https://t\.me/vermarkters_bot"([^>]*)>',
        r'<a href="#contact"\1>',
        bundle_card_content
    )

    # Step 3: Make entire Bundle card clickable by wrapping in <a>
    clickable_wrapper_start = '<a href="#contact" style="display: block; text-decoration: none; color: inherit; cursor: pointer; transition: transform 0.2s ease;" onmouseover="this.style.transform=\'scale(1.01)\'" onmouseout="this.style.transform=\'scale(1)\'">\n' + bundle_card_opening
    clickable_wrapper_end = '</div>\n</a>'

    # Reconstruct Bundle section
    new_bundle = (
        before_bundle_card +
        clickable_wrapper_start +
        bundle_card_content +
        clickable_wrapper_end +
        '\n</div>\n</section>'
    )

    # Replace in content
    new_content = content[:bundle_match.start()] + new_bundle + content[bundle_match.end():]

    return new_content

def fix_pricing_buttons(content):
    """Change pricing card buttons from spans to actual #contact links"""

    # Pattern: Find <span class="btn ... pricing-btn"> inside pricing cards
    # Replace with <a href="#contact" class="btn ...">

    pattern = r'<span class="btn ([^"]*pricing-btn[^"]*)"([^>]*)>([^<]+)</span>'
    replacement = r'<a href="#contact" class="btn \1"\2>\3</a>'

    new_content = re.sub(pattern, replacement, content)

    return new_content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content = original

        # Fix 1: Remove Telegram wrappers from pricing cards
        new_content = fix_pricing_telegram_links(new_content)

        # Fix 2: Change pricing button spans to links
        new_content = fix_pricing_buttons(new_content)

        # Fix 3: Fix Bundle Telegram link and make card clickable
        new_content = fix_bundle_telegram_link(new_content)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"  ERROR processing {file_path}: {e}")
        return False

def main():
    """Fix Telegram links on all pages"""
    base_dir = Path('.')
    modified_count = 0

    # Process index.html files (main pages with pricing + bundle)
    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    print("=== FIXING INDEX PAGES (Pricing + Bundle) ===")
    for lang in lang_dirs:
        file_path = base_dir / lang / 'index.html'
        if file_path.exists():
            print(f"Processing {lang}/index.html...")
            if process_file(file_path):
                print(f"  FIXED: {file_path}")
                modified_count += 1
            else:
                print(f"  No changes needed")

    # Process service pages (only Bundle)
    service_pages = [
        'google-ads.html',
        'meta-ads.html',
        'tiktok-ads.html',
        'seo.html',
        'crm-integration.html',
        'website-development.html'
    ]

    print("\n=== FIXING SERVICE PAGES (Bundle only) ===")
    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        for service_page in service_pages:
            file_path = lang_path / service_page
            if file_path.exists():
                print(f"Processing {lang}/{service_page}...")
                if process_file(file_path):
                    print(f"  FIXED: {file_path}")
                    modified_count += 1
                else:
                    print(f"  No changes needed")

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Fixed:")
    print(f"  - Pricing cards: removed Telegram wrappers, buttons -> #contact")
    print(f"  - Bundle: entire card clickable, leads to #contact form")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
