#!/usr/bin/env python3
"""
Fix Telegram links and add WhatsApp buttons on all pages
1. Fix wrong @vermarkter -> @vermarkters_bot
2. Add Telegram + WhatsApp buttons to header
3. Add WhatsApp buttons next to Telegram in pricing and contact sections
"""

import re
from pathlib import Path

WHATSAPP_NUMBER = '4915510300538'
TELEGRAM_BOT = 'vermarkters_bot'

def fix_telegram_links(content):
    """Fix wrong Telegram links"""
    # Fix @vermarkter to @vermarkters_bot
    content = re.sub(r't\.me/vermarkter(?!s_bot)', f't.me/{TELEGRAM_BOT}', content)
    return content

def add_header_buttons(content, lang):
    """Add Telegram and WhatsApp buttons to header"""

    # Translations for buttons
    buttons_text = {
        'de': {'telegram': 'Telegram', 'whatsapp': 'WhatsApp'},
        'en': {'telegram': 'Telegram', 'whatsapp': 'WhatsApp'},
        'pl': {'telegram': 'Telegram', 'whatsapp': 'WhatsApp'},
        'ru': {'telegram': 'Telegram', 'whatsapp': 'WhatsApp'},
        'tr': {'telegram': 'Telegram', 'whatsapp': 'WhatsApp'},
        'ua': {'telegram': 'Telegram', 'whatsapp': 'WhatsApp'}
    }

    t = buttons_text.get(lang, buttons_text['en'])

    # Check if header already has Telegram button
    if 'btn btn-primary">Telegram<' in content or 'btn btn-primary">تلگرام<' in content:
        # Header already has buttons, skip
        return content

    # Find the controls div with theme toggle and language switcher
    # Add buttons BEFORE the controls div
    pattern = r'(<div class="controls" style="display:flex; gap:15px; align-items:center;">)'

    buttons_html = f'''                    <!-- Contact Buttons -->
                    <a href="https://t.me/{TELEGRAM_BOT}" target="_blank" class="btn btn-primary" style="padding: 8px 16px;">{t['telegram']}</a>
                    <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" class="btn btn-secondary" style="padding: 8px 16px; margin-left: 5px;">{t['whatsapp']}</a>

                    '''

    replacement = buttons_html + r'\1'
    content = re.sub(pattern, replacement, content)

    return content

def add_whatsapp_to_pricing(content):
    """Add WhatsApp button next to Telegram in pricing cards"""

    # Pattern: Find Telegram link in pricing cards and add WhatsApp after it
    # <a href="https://t.me/vermarkters_bot" ... class="pricing-card-link">
    #     Telegram Icon + Text
    # </a>

    pattern = r'(<a href="https://t\.me/vermarkters_bot"[^>]*class="pricing-card-link">[^<]*(?:<[^>]*>[^<]*)*</a>)'

    def add_whatsapp(match):
        telegram_link = match.group(1)
        # Add WhatsApp link after Telegram
        whatsapp_link = f'''
                    <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" class="pricing-card-link" style="margin-top: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="margin-right: 8px;">
                            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                        </svg>
                        WhatsApp
                    </a>'''
        return telegram_link + whatsapp_link

    content = re.sub(pattern, add_whatsapp, content)

    return content

def add_whatsapp_to_contact(content):
    """Add WhatsApp button in contact section"""

    # Find contact section with Telegram link
    # Pattern: Look for Telegram link in contact section and add WhatsApp after
    pattern = r'(<a href="https://t\.me/vermarkters_bot"[^>]*>(?:[^<]|<(?!\/a>))*<\/a>)(\s*)((?:<\/div>|<a))'

    def add_whatsapp(match):
        telegram_link = match.group(1)
        whitespace = match.group(2)
        next_element = match.group(3)

        # Check if WhatsApp already exists nearby
        if 'wa.me' in content[max(0, match.start()-500):match.end()+500]:
            return match.group(0)

        whatsapp_link = f'''
                        <a href="https://wa.me/{WHATSAPP_NUMBER}" target="_blank" style="display: flex; align-items: center; gap: 0.75rem; font-size: 1.15rem; color: #25D366; text-decoration: none; font-weight: 600; margin-top: 1rem;">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                            </svg>
                            WhatsApp
                        </a>'''

        return telegram_link + whatsapp_link + whitespace + next_element

    content = re.sub(pattern, add_whatsapp, content)

    return content

def process_file(file_path, lang):
    """Process a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        new_content = original

        # 1. Fix Telegram links
        new_content = fix_telegram_links(new_content)

        # 2. Add header buttons
        new_content = add_header_buttons(new_content, lang)

        # 3. Add WhatsApp to pricing cards
        new_content = add_whatsapp_to_pricing(new_content)

        # 4. Add WhatsApp to contact section
        new_content = add_whatsapp_to_contact(new_content)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix Telegram and add WhatsApp on all pages"""
    base_dir = Path('.')
    modified_count = 0

    lang_dirs = ['de', 'en', 'pl', 'ru', 'tr', 'ua']

    for lang in lang_dirs:
        lang_path = base_dir / lang
        if not lang_path.exists():
            continue

        # Process all HTML files in language directory
        html_files = list(lang_path.glob('*.html'))

        for html_file in html_files:
            if process_file(html_file, lang):
                print(f"[OK] Fixed: {html_file}")
                modified_count += 1

    print(f"\n{'='*60}")
    print(f"Modified {modified_count} files")
    print(f"Fixed Telegram links and added WhatsApp buttons")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
