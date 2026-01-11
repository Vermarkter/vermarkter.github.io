#!/usr/bin/env python3
"""
Fix navigation menu: "Kontakt/Contact" should link to contact.html, not #contact
CTA buttons stay as #contact (form on same page)
"""

import re
from pathlib import Path

def fix_navigation_contact_link(content):
    """Fix only navigation menu contact link, not CTA buttons"""

    # Pattern: Find contact link in navigation menu (inside <nav> tags)
    # Look for <nav ... > ... <a href="#contact">Kontakt/Contact</a> ... </nav>

    # Pattern 1: In nav menu - German
    pattern1 = r'(<nav[^>]*>.*?)<a href="#contact"([^>]*)>(Kontakt)</a>(.*?</nav>)'
    if re.search(pattern1, content, re.DOTALL):
        content = re.sub(pattern1, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # Pattern 2: In nav menu - English
    pattern2 = r'(<nav[^>]*>.*?)<a href="#contact"([^>]*)>(Contact)</a>(.*?</nav>)'
    if re.search(pattern2, content, re.DOTALL):
        content = re.sub(pattern2, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # Pattern 3: In nav menu - Polish
    pattern3 = r'(<nav[^>]*>.*?)<a href="#contact"([^>]*)>(Kontakt)</a>(.*?</nav>)'
    if re.search(pattern3, content, re.DOTALL):
        content = re.sub(pattern3, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # Pattern 4: In nav menu - Russian
    pattern4 = r'(<nav[^>]*>.*?)<a href="#contact"([^>]*)>(Контакты|Контакт)</a>(.*?</nav>)'
    if re.search(pattern4, content, re.DOTALL):
        content = re.sub(pattern4, r'\1<a href="contact.html"\2>\2</a>\4', content, flags=re.DOTALL)

    # Pattern 5: In nav menu - Turkish
    pattern5 = r'(<nav[^>]*>.*?)<a href="#contact"([^>]*)>(İletişim)</a>(.*?</nav>)'
    if re.search(pattern5, content, re.DOTALL):
        content = re.sub(pattern5, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # Pattern 6: In nav menu - Ukrainian
    pattern6 = r'(<nav[^>]*>.*?)<a href="#contact"([^>]*)>(Контакти)</a>(.*?</nav>)'
    if re.search(pattern6, content, re.DOTALL):
        content = re.sub(pattern6, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # FOOTER PATTERNS - same languages
    # Footer pattern - German
    footer1 = r'(<footer[^>]*>.*?)<a href="#contact"([^>]*)>(Kontakt)</a>(.*?</footer>)'
    if re.search(footer1, content, re.DOTALL):
        content = re.sub(footer1, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # Footer pattern - English
    footer2 = r'(<footer[^>]*>.*?)<a href="#contact"([^>]*)>(Contact)</a>(.*?</footer>)'
    if re.search(footer2, content, re.DOTALL):
        content = re.sub(footer2, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    # Footer pattern - Polish/Russian/Turkish/Ukrainian
    footer3 = r'(<footer[^>]*>.*?)<a href="#contact"([^>]*)>(Kontakt|Контакты|Контакт|İletişim|Контакти)</a>(.*?</footer>)'
    if re.search(footer3, content, re.DOTALL):
        content = re.sub(footer3, r'\1<a href="contact.html"\2>\3</a>\4', content, flags=re.DOTALL)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content = fix_navigation_contact_link(original)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix navigation contact links on all service pages"""
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
                    print(f"[OK] Fixed nav contact link: {file_path}")
                    modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print("Navigation: Kontakt/Contact -> contact.html")
    print("CTA buttons: unchanged (#contact)")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
