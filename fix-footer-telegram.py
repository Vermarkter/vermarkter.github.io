#!/usr/bin/env python3
"""
Fix wrong Telegram bot name in footer and add WhatsApp if missing
"""

import re
from pathlib import Path

CORRECT_BOT = 'vermarkters_bot'
WHATSAPP_NUMBER = '4915510300538'

def fix_footer_telegram(content):
    """Fix wrong Telegram bot names in footer"""

    # Fix various wrong bot names
    wrong_bots = [
        'Asystentmijbot',
        'Asystentmjbot',
        'vermarkter'  # without s_bot
    ]

    for wrong_bot in wrong_bots:
        # Fix URLs
        content = re.sub(
            rf't\.me/{wrong_bot}(?![s_])',  # Don't match vermarkters_bot
            f't.me/{CORRECT_BOT}',
            content,
            flags=re.IGNORECASE
        )

        # Fix @ mentions
        content = re.sub(
            rf'@{wrong_bot}(?![s_])',
            f'@{CORRECT_BOT}',
            content,
            flags=re.IGNORECASE
        )

    return content

def add_whatsapp_to_footer(content):
    """Add WhatsApp link to footer if missing"""

    # Check if footer already has WhatsApp
    if 'Footer bereits mit WhatsApp' in content or (
        'wa.me' in content and
        content.rfind('wa.me') > content.rfind('</footer>') - 1000 if '</footer>' in content else False
    ):
        return content

    # Pattern: Find footer Telegram link and add WhatsApp after it
    # Look for Telegram in footer section (after "Kontakt" or similar heading)
    pattern = r'(<a href="https://t\.me/vermarkters_bot"[^>]*>.*?Telegram.*?</a>)'

    def add_whatsapp(match):
        telegram_link = match.group(1)

        # Check if next element already has WhatsApp
        end_pos = match.end()
        next_100_chars = content[end_pos:end_pos+100] if end_pos < len(content) else ''
        if 'wa.me' in next_100_chars:
            return telegram_link

        whatsapp_link = f'''
                    <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" style="display: block; color: var(--text-secondary); margin-bottom: 0.75rem; text-decoration: none;">WhatsApp</a>'''

        return telegram_link + whatsapp_link

    content = re.sub(pattern, add_whatsapp, content)

    return content

def process_file(file_path):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content = original

        # Fix wrong Telegram bot names
        new_content = fix_footer_telegram(new_content)

        # Add WhatsApp to footer
        new_content = add_whatsapp_to_footer(new_content)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix footer Telegram and add WhatsApp on all pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        html_files = list(lang_path.glob('*.html'))

        for html_file in html_files:
            if process_file(html_file):
                print(f"[OK] Fixed: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Fixed footer Telegram and added WhatsApp")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
