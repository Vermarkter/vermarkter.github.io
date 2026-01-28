#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Batch update contact form fields across all language folders"""

import os
import re
import sys

# Force UTF-8 output
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

REPLACEMENTS = {
    'pl': {
        'email_placeholder': [
            (r'placeholder="twoj\.email@przyklad\.pl"', 'placeholder="twoj.email@firma.pl"'),
        ],
        'textarea_rows': [
            (r'rows="5" placeholder', 'required rows="4" placeholder'),
        ],
    },
}

def process_file(filepath, lang):
    """Process a single file with replacements"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Apply replacements
        if lang in REPLACEMENTS:
            for category, patterns in REPLACEMENTS[lang].items():
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)

        # Only write if changed
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    base_dir = r"c:\Users\andri\OneDrive\Projects\агенство-новий"
    langs = ['pl']

    for lang in langs:
        lang_dir = os.path.join(base_dir, lang)
        if not os.path.exists(lang_dir):
            continue

        print(f"\n=== Processing {lang.upper()} files ===")
        for filename in os.listdir(lang_dir):
            if filename.endswith('.html'):
                filepath = os.path.join(lang_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        if 'contact' in f.read():
                            if process_file(filepath, lang):
                                print(f"[OK] Updated: {filename}")
                except:
                    pass

if __name__ == "__main__":
    main()
