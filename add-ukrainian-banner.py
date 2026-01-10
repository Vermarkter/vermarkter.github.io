#!/usr/bin/env python3
"""
Add Ukrainian support banner to all UA service pages
"""

import re
from pathlib import Path

UKRAINIAN_BANNER = '''    <!-- UKRAINIAN SUPPORT BANNER -->
    <div style="background: linear-gradient(90deg, #0057B7 0%, #FFD700 100%); color: #000; text-align: center; padding: 8px; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">
        🇺🇦 Створено для підтримки українців, які будують бізнес у Європі
    </div>

'''

def add_ukrainian_banner(content):
    """Add Ukrainian banner after header, before main content"""

    # Check if banner already exists
    if '🇺🇦 Створено для підтримки українців' in content:
        return content, False

    # Pattern: Find </header> and add banner after it
    # Match </header> followed by optional whitespace and then <!-- HERO or <section
    pattern = r'(</header>)\s*\n(\s*)(<!-- HERO|<section)'

    replacement = r'\1\n\n' + UKRAINIAN_BANNER + r'\2\3'
    new_content = re.sub(pattern, replacement, content)

    return new_content, (new_content != content)

def update_hero_badge(content):
    """Update hero badge to Ukrainian-specific text"""

    # Pattern: Find hero badge and replace with Ukrainian version
    # Look for badges like "🔍 Google Ads агентство" or similar
    badge_pattern = r'<div style="display: inline-block; background: rgba\([^)]+\); border: 1px solid rgba\([^)]+\); border-radius: 50px; padding: [^>]+>\s*<span[^>]*>[^<]+</span>\s*</div>'

    ukrainian_badge = '''<div style="display: inline-block; background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 50px; padding: 0.5rem 1.5rem; margin-bottom: 2rem;">
                    <span style="color: #3B82F6; font-weight: 600; font-size: 0.95rem;">⚡ Для підприємців із України в ЄС</span>
                </div>'''

    # Replace first badge in hero section
    def replace_first_badge(match):
        # Check if we're in hero section (look back for "hero" class)
        return ukrainian_badge

    new_content = re.sub(badge_pattern, replace_first_badge, content, count=1)

    return new_content, (new_content != content)

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Skip index.html (already has banner)
        if file_path.name == 'index.html':
            return False

        # Skip non-service pages
        if file_path.name in ['contact.html', 'privacy.html', 'imprint.html']:
            return False

        new_content = original
        modified = False

        # 1. Add banner after header
        new_content, banner_added = add_ukrainian_banner(new_content)
        modified = modified or banner_added

        # 2. Update hero badge
        new_content, badge_updated = update_hero_badge(new_content)
        modified = modified or badge_updated

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add Ukrainian banner to all UA service pages"""
    base_dir = Path('.')
    modified_count = 0

    ua_dir = base_dir / 'ua'
    if not ua_dir.exists():
        print("UA directory not found!")
        return

    html_files = list(ua_dir.glob('*.html'))

    for html_file in html_files:
        if process_file(html_file):
            print(f"[OK] Added Ukrainian banner: {html_file}")
            modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Added Ukrainian support banner")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
