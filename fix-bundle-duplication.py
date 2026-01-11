#!/usr/bin/env python3
"""
Fix Bundle duplication: Keep only the GOOD wide Bundle, remove broken duplicates
"""

import re
from pathlib import Path

def fix_bundle_duplication(content):
    """Remove duplicate/broken Bundle sections, keep only the good one"""

    # STEP 1: Find and keep the GOOD Bundle (with display: flex in section)
    # Pattern: <!-- SMART START BUNDLE (FIXED LAYOUT) --> ... </section>
    good_bundle_pattern = r'<!-- SMART START BUNDLE \(FIXED LAYOUT\) -->.*?</section>'
    good_bundle_match = re.search(good_bundle_pattern, content, re.DOTALL)

    if not good_bundle_match:
        print("  WARNING: No good Bundle found")
        return content, False

    good_bundle = good_bundle_match.group(0)
    good_bundle_start = good_bundle_match.start()
    good_bundle_end = good_bundle_match.end()

    # STEP 2: Find the closing </section> of the good Bundle
    # Then remove everything from there until <!-- CONTACT FORM --> or <section id="contact"

    # Pattern: Match from end of good Bundle to start of Contact section
    # This captures all the loose HTML fragments
    after_good_bundle = content[good_bundle_end:]

    # Find where Contact section starts
    contact_patterns = [
        r'\s*<!-- CONTACT FORM -->',
        r'\s*<section id="contact"'
    ]

    contact_start = None
    for pattern in contact_patterns:
        match = re.search(pattern, after_good_bundle)
        if match:
            contact_start = match.start()
            break

    if contact_start is None:
        print("  WARNING: No Contact section found after Bundle")
        return content, False

    # Extract the fragment between good Bundle and Contact
    fragment = after_good_bundle[:contact_start]

    # Check if fragment contains broken Bundle pieces
    broken_indicators = [
        'BESTSELLER',
        'bundle-grid',
        'Smart Start Bundle',
        'Landing Page (Express)',
        'Bundle jetzt sichern'
    ]

    has_broken_bundle = any(indicator in fragment for indicator in broken_indicators)

    if not has_broken_bundle:
        print("  OK: No broken Bundle fragments found")
        return content, False

    # STEP 3: Remove the broken fragment
    # Reconstruct: content before good Bundle + good Bundle + contact section onwards
    new_content = (
        content[:good_bundle_end] +
        '\n' +
        after_good_bundle[contact_start:]
    )

    return new_content, True

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content, modified = fix_bundle_duplication(original)

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"  ERROR processing {file_path}: {e}")
        return False

def main():
    """Fix Bundle duplication on all service pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']
    service_pages = [
        'google-ads.html',
        'meta-ads.html',
        'tiktok-ads.html',
        'seo.html',
        'crm-integration.html',
        'website-development.html'
    ]

    for lang in lang_dirs:
        print(f"\n=== {lang.upper()} ===")
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        for service_page in service_pages:
            file_path = lang_path / service_page
            if file_path.exists():
                print(f"Processing {service_page}...")
                if process_file(file_path):
                    print(f"  FIXED: {file_path}")
                    modified_count += 1
                else:
                    print(f"  No changes needed")

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Kept: GOOD Bundle (display: flex layout)")
    print(f"Removed: Broken Bundle fragments")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
