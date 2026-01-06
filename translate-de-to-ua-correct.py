# -*- coding: utf-8 -*-
"""
Correct Ukrainian translation from German CRM page
"""

# Read German version
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Translation dictionary with EXACT matches
translations = {
    'lang="de"': 'lang="uk"',
    '/de/crm-integration': '/ua/crm-integration',
    'og-image-crm-de.jpg': 'og-image-crm-ua.jpg',
    'CRM-Integration — Vermarkter': 'Інтеграція CRM — Vermarkter',

    # Apply all replacements from fix-ua-crm-final.py
    'Kennen Sie das?': 'Чи знайоме вам це?',
    'Die häufigsten Probleme ohne CRM-Integration': 'Найпоширеніші проблеми без CRM-інтеграції',
    'Manager reagieren zu spät': 'Менеджери реагують занадто пізно',
    'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.': 'Лід заходить → Менеджер бачить його через години → Лід купує у конкурентів. Без миттєвих сповіщень ви втрачаєте 50% клієнтів.',
    'Welche Werbung funktioniert?': 'Яка реклама працює?',
    'Google Ads zeigt Klicks, aber keine Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. Ohne Offline Conversions verbrennen Sie Budget.': 'Google Ads показує кліки, а не продажі. Ви не знаєте, які кампанії приносять гроші. Без наскрізної аналітики ви спалюєте бюджет.',
    'Unsere Lösung': 'Наше рішення',
    'Was wir für Sie einrichten': 'Що ми налаштуємо для вас',
    'Auto-Tagging nach Quelle': 'Авто-тегування джерела',
    'Wir senden Verkaufsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. Besseres ROAS automatisch.': 'Ми передаємо дані про продажі назад у Google Ads та Meta. Алгоритми вчаться на реальних клієнтах. ROAS зростає автоматично.',
    'CAPI für Meta Ads': 'CAPI для Meta Ads',
    'Echtes ROAS pro Kampagne': 'Реальний ROAS по кампаніях',
    'Custom Funnel-Stufen': 'Налаштування етапів воронки',
    'Automatische Follow-ups': 'Автоматичні нагадування',
    'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Разова оплата за налаштування. Жодних щомісячних комісій.',
    'Jetzt starten': 'Почати зараз',
    '🔥 EMPFOHLEN': '🔥 РЕКОМЕНДУЄМО',
    'Für Unternehmen': 'Для корпорацій',
    'Preis auf Anfrage': 'Ціна за запитом',
    'Alles aus ADVANCED +': 'Все, що в ADVANCED +',
    'Unbegrenzte Automatisierungen': 'Безлімітні автоматизації',
    'Individuelle Schulung & Onboarding': 'Індивідуальне навчання та онбординг',
    'Kontaktieren Sie uns': "Зв'язатися з нами",
    'Am besten für Marketing + Sales zusammen. Kostenlose Version verfügbar, später ab €50/Monat.': 'Найкраще для маркетингу та продажів. Є безкоштовна версія, платна від €50/міс.',
    'Einfaches Sales-CRM. €14/Monat pro User. Perfekt für kleine Teams.': 'Проста CRM для продажів. €14/міс за користувача. Ідеально для малих команд.',
    'Günstigste Option. Ab €14/Monat. Gut für Startups.': 'Найдешевший варіант. Від €14/міс. Добре для стартапів.',
    'All-in-One für Agenturen. Ab €97/Monat.': 'Все-в-одному для агенцій. Від €97/міс.',
    'Werktage': 'робочих днів',
    'Nach dem Kick-off-Call starten wir sofort. Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen.': 'Починаємо одразу після стартового дзвінка. Ви отримуєте щотижневі звіти і можете ставити питання будь-коли.',
    'Brauche ich technische Kenntnisse?': 'Чи потрібні технічні знання?',
    'Nein. Wir richten alles für Sie ein. Sie bekommen eine Schulung, wie Sie das CRM nutzen, Leads bearbeiten und Reports ansehen. Nach dem Setup arbeitet alles automatisch.': 'Ні. Ми все налаштуємо під ключ. Ви отримаєте навчання, як користуватися CRM. Після налаштування все працює автоматично.',
    'Was sind Offline Conversions?': 'Що таке офлайн-конверсії?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Verkauf passiert offline (Anruf, Meeting, Rechnung). Offline Conversions senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. ROAS steigt um durchschnittlich 30-50%.': 'Google Ads бачить лише кліки. Але реальний продаж відбувається офлайн (дзвінок, зустріч). Офлайн-конверсії передають ці дані назад у Google, щоб реклама оптимізувалася на прибуток, а не просто на заявки. ROAS зростає на 30-50%.',
    'Wie funktioniert die Telegram-Benachrichtigung?': 'Як працюють сповіщення в Telegram?',
    'Sobald ein Lead das Formular ausfüllt, erhält Ihr Vertriebsteam eine sofortige Nachricht mit allen Kontaktdaten. Manager kann in 2 Minuten anrufen.': "Як тільки лід залишає заявку, менеджер отримує повідомлення в Telegram. Воно містить: Ім'я, Телефон, Джерело реклами. Це дозволяє реагувати миттєво (до 5 хвилин).",
    'Bietet ihr auch laufende Betreuung?': 'Чи надаєте ви подальшу підтримку?',
    'Das Setup ist einmalig. Danach arbeitet alles automatisch. Falls Sie später weitere Automatisierungen, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Налаштування разове. Далі все працює автоматично. Якщо пізніше знадобляться доробки, ви можете замовити їх окремо (€99/год).',
    'Bereit, Ihr CRM zu verbinden?': 'Готові підключити CRM?',
    'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Безкоштовна консультація — допоможемо обрати правильну CRM',
    'ihre.email@firma.de': 'vash.email@company.com',
    'Ihre Nachricht': 'Ваше повідомлення',
    'Kostenlose Beratung anfragen': 'Замовити консультацію',
    'Antwort innerhalb von 24 Stunden. Keine Verpflichtungen.': "Відповідь протягом 24 годин. Без зобов'язань.",
    'Ihre Marketing-Agentur für DACH und Osteuropa.': 'Ваша маркетингова агенція для ринків ЄС.',
    'Datenschutz': 'Політика конфіденційності',
    'Impressum': 'Юридична інформація',
    '© 2025 Vermarkter. Alle Rechte vorbehalten.': '© 2025 Vermarkter. Всі права захищені.',

    # Language switcher
    '<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">\n                                <rect width="16" height="4" fill="#000"/>\n                                <rect y="4" width="16" height="4" fill="#D00"/>\n                                <rect y="8" width="16" height="4" fill="#FFCE00"/>\n                            </svg>\n                            DE ▼': '<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">\n                                <rect width="16" height="6" fill="#0057B7"/>\n                                <rect y="6" width="16" height="6" fill="#FFD700"/>\n                            </svg>\n                            UA ▼',

    # Chatbot
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Привіт! 👋 Є питання щодо CRM-інтеграції?',
    'Schreiben Sie Ihre Frage...': 'Напишіть ваше питання...',
}

# Apply translations
for de, ua in translations.items():
    content = content.replace(de, ua)

# Write Ukrainian version
with open('ua/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Ukrainian CRM page created successfully!")
