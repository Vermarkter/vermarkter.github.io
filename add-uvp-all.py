# -*- coding: utf-8 -*-
"""Add UVP to remaining language versions"""

uvp_additions = {
    'en/index.html': {
        'search': '<strong style="color: var(--text-primary);">First leads in 7 days. Technical manager in your language. Weekly reports.</strong>\n                </p>',
        'replace': '<strong style="color: var(--text-primary);">First leads in 7 days. Technical manager in your language. Weekly reports.</strong>\n                </p>\n                <p style="font-size: 1.1rem; margin-top: 1rem; color: var(--brand); font-weight: 600;">🎯 Only EU agency with 48h launch guarantee and 90% campaign success rate</p>'
    },
    'pl/index.html': {
        'search': '<strong style="color: var(--text-primary);">Pierwsze leady w 7 dni. Menedżer techniczny w Twoim języku. Cotygodniowe raporty.</strong>\n                </p>',
        'replace': '<strong style="color: var(--text-primary);">Pierwsze leady w 7 dni. Menedżer techniczny w Twoim języku. Cotygodniowe raporty.</strong>\n                </p>\n                <p style="font-size: 1.1rem; margin-top: 1rem; color: var(--brand); font-weight: 600;">🎯 Jedyna agencja w UE z gwarancją 48-godzinnego uruchomienia i 90% skutecznością kampanii</p>'
    },
    'ru/index.html': {
        'search': '<strong style="color: var(--text-primary);">Первые лиды за 7 дней. Технический менеджер на вашем языке. Еженедельные отчеты.</strong>\n                </p>',
        'replace': '<strong style="color: var(--text-primary);">Первые лиды за 7 дней. Технический менеджер на вашем языке. Еженедельные отчеты.</strong>\n                </p>\n                <p style="font-size: 1.1rem; margin-top: 1rem; color: var(--brand); font-weight: 600;">🎯 Единственное агентство в ЕС с гарантией запуска за 48 часов и 90% успешностью кампаний</p>'
    },
    'tr/index.html': {
        'search': '<strong style="color: var(--text-primary);">İlk potansiyel müşteriler 7 günde. Dilinizde teknik yönetici. Haftalık raporlar.</strong>\n                </p>',
        'replace': '<strong style="color: var(--text-primary);">İlk potansiyel müşteriler 7 günde. Dilinizde teknik yönetici. Haftalık raporlar.</strong>\n                </p>\n                <p style="font-size: 1.1rem; margin-top: 1rem; color: var(--brand); font-weight: 600;">🎯 AB\'de 48 saatlik başlatma garantisi ve %90 kampanya başarı oranı ile tek ajans</p>'
    }
}

for file_path, replacement in uvp_additions.items():
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if replacement['search'] in content:
        content = content.replace(replacement['search'], replacement['replace'])

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Added UVP to {file_path}")
    else:
        print(f"[SKIP] Pattern not found in {file_path}")

print("\n[SUCCESS] UVP additions completed!")
