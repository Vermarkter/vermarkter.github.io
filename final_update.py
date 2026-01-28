# -*- coding: utf-8 -*-
import os
import re

BASE = r"c:\Users\andri\OneDrive\Projects\агенство-новий"

# TR files - update email placeholders and rows
tr_files = ['tr/google-ads.html', 'tr/meta-ads.html', 'tr/tiktok-ads.html', 'tr/seo.html', 'tr/crm-integration.html', 'tr/website-development.html']
for filepath in tr_files:
    full_path = os.path.join(BASE, filepath)
    if not os.path.exists(full_path):
        continue

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'contact' not in content:
            continue

        # Update email placeholders
        content = re.sub(r'placeholder="[^"]*@[^"]*"', 'placeholder="adiniz@sirket.com"', content)
        # Update textarea rows
        content = re.sub(r'rows="5"', 'rows="4"', content)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"OK: {filepath}")
    except Exception as e:
        print(f"ERR: {filepath} - {e}")

# RU files - update email placeholders and rows
ru_files = ['ru/google-ads.html', 'ru/meta-ads.html', 'ru/tiktok-ads.html', 'ru/seo.html', 'ru/website-development.html']
for filepath in ru_files:
    full_path = os.path.join(BASE, filepath)
    if not os.path.exists(full_path):
        continue

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'contact' not in content:
            continue

        # Update email placeholders
        content = re.sub(r'placeholder="[^"]*@[^"]*"', 'placeholder="vash.email@gmail.com"', content)
        # Update textarea rows
        content = re.sub(r'rows="5"', 'rows="4"', content)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"OK: {filepath}")
    except Exception as e:
        print(f"ERR: {filepath} - {e}")

print("\nDone!")
