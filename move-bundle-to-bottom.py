#!/usr/bin/env python3
"""
Move Smart Start Bundle to the bottom (after Pricing, before Contact/FAQ)
"""

import re
from pathlib import Path

def move_bundle_to_bottom(content):
    """Move Bundle section to correct position"""

    # Step 1: Extract Bundle section
    bundle_pattern = r'(    <!-- SMART START BUNDLE -->.*?    </section>\s*\n)'
    bundle_match = re.search(bundle_pattern, content, re.DOTALL)

    if not bundle_match:
        return content, False

    bundle_section = bundle_match.group(1)

    # Step 2: Remove Bundle from current position
    content = re.sub(bundle_pattern, '', content, count=1, flags=re.DOTALL)

    # Step 3: Insert Bundle before Contact Form
    # Try multiple patterns for contact section
    insert_patterns = [
        r'(    <!-- CONTACT FORM -->)',
        r'(    <section id="contact")',
        r'(    <section id="kontakt")'
    ]

    inserted = False
    for insert_pattern in insert_patterns:
        if re.search(insert_pattern, content):
            replacement = bundle_section + r'\n\1'
            content = re.sub(insert_pattern, replacement, content, count=1)
            inserted = True
            break

    if not inserted:
        print(f"  Warning: Could not find Contact Form insertion point")
        return content, False

    return content, True

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip if no Bundle section
        if '<!-- SMART START BUNDLE -->' not in original:
            return False

        new_content, modified = move_bundle_to_bottom(original)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Move Bundle to bottom on all service pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    # Service pages to update
    service_pages = [
        'google-ads.html',
        'meta-ads.html',
        'tiktok-ads.html',
        'seo.html',
        'crm-integration.html',
        'website-development.html'
    ]

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        for service_page in service_pages:
            file_path = lang_path / service_page
            if file_path.exists():
                if process_file(file_path):
                    print(f"[OK] Moved Bundle to bottom: {file_path}")
                    modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print("Bundle moved to bottom (before Contact Form)")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
