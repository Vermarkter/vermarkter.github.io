# -*- coding: utf-8 -*-

# Read current Ukrainian CRM page
with open('ua/crm-integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all remaining German/mixed content
fixes = {
    # Section subtitles with mixed content
    'Die häufigsten Проблеми ohne CRM-інтеграція': 'Найпоширеніші проблеми без CRM-інтеграції',

    # Problem descriptions
    'Ihre Leads landen in unübersichtlichen Tabellen. Менеджер müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Ваші ліди потрапляють у незручні таблиці. Менеджери повинні вручну сортувати, розставляти пріоритети та нагадувати. <strong style="color: #EF4444;">Втрата часу + упущені можливості.</strong>',

    'Менеджер reagieren zu spät': 'Менеджери реагують занадто пізно',
    'Lead kommt rein → Менеджер sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Лід надходить → Менеджер бачить його тільки через години → Лід купує у конкурентів. <strong style="color: #EF4444;">Без миттєвого сповіщення ви втрачаєте 50% лідів.</strong>',

    # Solution section header
    'Unsere <span class="text-gradient">Рішення</span>': 'Наше <span class="text-gradient">Рішення</span>',

    # Solution descriptions
    'Lead kommt von der Сайт → landet sofort im CRM → Менеджер bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Лід надходить з сайту → відразу потрапляє в CRM → Менеджер отримує Telegram-повідомлення → Дзвінок протягом 5 хвилин.',

    'Wir senden Продажsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Ми відправляємо дані про продажі назад у Google Ads і Meta. Алгоритми вчаться, які кліки перетворюються на реальних клієнтів. <strong>Кращий ROAS автоматично.</strong>',

    'Strukturierte Продажsprozesse: Neuer Lead → Контактiert → Angebot → Verhandlung → Gewonnen. Kein Lead geht verloren.': 'Структуровані процеси продажу: Новий лід → Контакт → Пропозиція → Переговори → Угода. Жоден лід не втрачається.',

    # Pricing features
    'Сайт-Formulare → CRM': 'Форми з сайту → CRM',
    'Zapier/Make Автоматизаціяen (5 Flows)': 'Zapier/Make автоматизації (5 потоків)',
    'Alles aus РОЗШИРЕНИЙ +': 'Все з РОЗШИРЕНОГО +',
    'Unbegrenzte Автоматизаціяen': 'Безлімітні автоматизації',
    'Dedizierter Account Менеджер': 'Виділений менеджер проекту',
    'Kontaktieren Sie uns': 'Зв\'язатися з нами',

    # Pricing disclaimer
    'Ціни zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': 'Ціни без ПДВ. Вартість ліцензій CRM (HubSpot, Pipedrive тощо) НЕ включена. Ми допоможемо вам обрати відповідний план.',

    # FAQ answers
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Продаж passiert offline (Anruf, Meeting, Rechnung). <strong>Offline Conversions</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads зазвичай бачить тільки кліки та відправлення форм. Але реальний продаж відбувається офлайн (дзвінок, зустріч, рахунок). <strong>Офлайн-конверсії</strong> відправляють ці дані назад у Google. Результат: Google знає, які кліки призводять до реальних клієнтів, і оптимізує ваші кампанії автоматично на продажі, а не тільки на ліди. <strong>ROAS зростає в середньому на 30-50%.</strong>',

    'Wie funktionieren Telegram-сповіщення?': 'Як працюють Telegram-сповіщення?',
    'Sobald ein Lead von Ihrer Сайт kommt, bekommt Ihr Sales-Менеджер eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Телефон, Quelle (Google Ads/Meta/etc.). Менеджер kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Як тільки лід надходить з вашого сайту, ваш менеджер продажів отримує повідомлення в Telegram (або Slack/WhatsApp). Повідомлення містить: Ім\'я, Email, Телефон, Джерело (Google Ads/Meta/тощо). Менеджер може одразу відреагувати. <strong>Середній час реакції: до 5 хвилин.</strong>',

    'Das Setup ist одноразово. Danach arbeitet alles automatisch. Falls Sie später weitere Автоматизаціяen, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Налаштування одноразове. Після цього все працює автоматично. Якщо пізніше вам знадобляться додаткові автоматизації, інтеграції або оптимізації, ви можете замовити їх окремо. Вартість: €99/год.',

    # Chatbot
    'Hallo! 👋 Haben Sie Fragen zur CRM-інтеграція?': 'Привіт! 👋 Є питання щодо CRM-інтеграції?',
}

# Apply fixes
for old, new in fixes.items():
    content = content.replace(old, new)

# Write fixed content
with open('ua/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Ukrainian CRM page - removed all German text!")
