#!/usr/bin/env python3
"""
Update contact information across all HTML files
- Telegram: @vermarkters_bot
- WhatsApp: +4915510300538
- Email: maps.werbung@gmail.com
"""

import re
from pathlib import Path

# Contact updates
CONTACTS = {
    # Telegram bot links
    r'https://t\.me/vermarkter_eu': 'https://t.me/vermarkters_bot',
    r't\.me/vermarkter_eu': 't.me/vermarkters_bot',
    r'@vermarkter_eu': '@vermarkters_bot',

    # WhatsApp number
    r'wa\.me/491234567890': 'wa.me/4915510300538',
    r'\+49\s?123\s?456\s?78\s?90': '+49 155 103 005 38',

    # Email
    r'info@vermarkter\.eu': 'maps.werbung@gmail.com',
}

def update_contacts(content):
    """Replace old contact info with new"""
    original = content

    for old_pattern, new_value in CONTACTS.items():
        content = re.sub(old_pattern, new_value, content)

    return content, content != original

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content, modified = update_contacts(content)

        if modified:
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

    print(f"Found {len(html_files)} HTML files")

    for html_file in html_files:
        if process_file(html_file):
            print(f"Updated: {html_file}")
            modified_count += 1

    print(f"\nModified {modified_count} files")
    print(f"✅ Telegram: @vermarkters_bot")
    print(f"✅ WhatsApp: +49 155 103 005 38")
    print(f"✅ Email: maps.werbung@gmail.com")

if __name__ == '__main__':
    main()
