# -*- coding: utf-8 -*-

# Read German CRM page
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    de_content = f.read()

# Complete German → Ukrainian translations
translations = {
    # HTML lang attribute
    'lang="de"': 'lang="uk"',

    # Meta tags
    'CRM-Integration für Marketing & Sales. HubSpot, Pipedrive, Zoho. Lead-Tracking, Offline Conversions, Telegram-Benachrichtigungen. Keine verlorenen Leads mehr.': 'CRM-інтеграція для маркетингу та продажів. HubSpot, Pipedrive, Zoho. Відстеження лідів, офлайн-конверсії, Telegram-сповіщення. Більше жодних втрачених лідів.',
    'CRM Integration, HubSpot, Pipedrive, Marketing Automation, Lead Tracking, Offline Conversions, Sales Pipeline': 'CRM інтеграція, HubSpot, Pipedrive, маркетингова автоматизація, відстеження лідів, офлайн конверсії, воронка продажів',
    'Vermarkter Agency': 'Vermarkter Агенція',
    'Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb. Lead-Tracking, Automatisierung, echtes ROAS.': 'З\'єднайте ваші маркетингові кампанії з продажами. Відстеження лідів, автоматизація, реальний ROAS.',
    'Verbinden Sie Marketing und Sales': 'З\'єднайте маркетинг та продажі',
    'CRM-Integration — Vermarkter': 'CRM-інтеграція — Vermarkter',

    # Navigation
    'Leistungen': 'Послуги',
    'Probleme': 'Проблеми',
    'Lösung': 'Рішення',
    'Preise': 'Ціни',
    'FAQ': 'Питання',
    'Kontakt': 'Контакт',

    # Language switcher
    'DE ▼': 'UA ▼',

    # Hero section
    '🔗 CRM-Integration': '🔗 CRM-інтеграція',
    'Marketing <span class="text-gradient">+ Vertrieb</span><br>\n                    in einem System': 'Маркетинг <span class="text-gradient">+ Продажі</span><br>\n                    в одній системі',
    '<strong style="color: var(--text-primary);">Keine verlorenen Leads mehr.</strong> Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.<br>\n                    Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': '<strong style="color: var(--text-primary);">Більше жодних втрачених лідів.</strong> З\'єднайте Google Ads, Meta Ads і TikTok з HubSpot, Pipedrive або Zoho CRM.<br>\n                    Автоматичні сповіщення, відстеження продажів, реальний ROAS.',
    'Setup ab €499': 'Налаштування від €499',
    'Demo buchen': 'Замовити демо',

    # Diagram labels
    'Website': 'Сайт',
    'CRM': 'CRM',
    'Manager': 'Менеджер',
    'Verkauf': 'Продаж',

    # Supported CRMs
    'Unterstützte CRM-Systeme:': 'Підтримувані CRM-системи:',

    # Pain Points section
    '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Чи знайоме вам це?</span>',
    'Die häufigsten Probleme ohne CRM-Integration': 'Найпоширеніші проблеми без CRM-інтеграції',

    # Problem 1
    'Leads in Excel-Tabellen': 'Ліди в Excel-таблицях',
    'Ihre Leads landen in unübersichtlichen Tabellen. Manager müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Ваші ліди потрапляють у незручні таблиці. Менеджери повинні вручну сортувати, розставляти пріоритети та нагадувати. <strong style="color: #EF4444;">Втрата часу + упущені можливості.</strong>',

    # Problem 2
    'Manager reagieren zu spät': 'Менеджери реагують занадто пізно',
    'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Лід надходить → Менеджер бачить його тільки через години → Лід купує у конкурентів. <strong style="color: #EF4444;">Без миттєвого сповіщення ви втрачаєте 50% лідів.</strong>',

    # Problem 3
    'Welche Werbung funktioniert?': 'Яка реклама працює?',
    'Google Ads zeigt Klicks, aber keine Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. <strong style="color: #EF4444;">Ohne Offline Conversions verbrennen Sie Budget.</strong>': 'Google Ads показує кліки, але не продажі. Ви не знаєте, які кампанії приносять реальних клієнтів. <strong style="color: #EF4444;">Без офлайн-конверсій ви спалюєте бюджет.</strong>',

    # Solution section
    '✅ Unsere <span class="text-gradient">Lösung</span>': '✅ Наше <span class="text-gradient">Рішення</span>',
    'Was wir für Sie einrichten': 'Що ми налаштуємо для вас',

    # Solution 1: Automation
    'Automatisierung': 'Автоматизація',
    'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Лід надходить з сайту → відразу потрапляє в CRM → Менеджер отримує Telegram-повідомлення → Дзвінок протягом 5 хвилин.',
    'Formulare → CRM (Zapier/Make)': 'Форми → CRM (Zapier/Make)',
    'Telegram-Benachrichtigungen': 'Telegram-сповіщення',
    'Auto-Tagging nach Quelle': 'Авто-тегування за джерелом',

    # Solution 2: Analytics
    'End-to-End Analytics': 'Наскрізна аналітика',
    'Wir senden Verkaufsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Ми відправляємо дані про продажі назад у Google Ads і Meta. Алгоритми вчаться, які кліки перетворюються на реальних клієнтів. <strong>Кращий ROAS автоматично.</strong>',
    'Offline Conversions (Google)': 'Офлайн-конверсії (Google)',
    'CAPI für Meta Ads': 'CAPI для Meta Ads',
    'Echtes ROAS pro Kampagne': 'Реальний ROAS за кампаніями',

    # Solution 3: Pipelines
    'Sales-Pipelines': 'Воронки продажів',
    'Strukturierte Verkaufsprozesse: Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen. Kein Lead geht verloren.': 'Структуровані процеси продажу: Новий лід → Контакт → Пропозиція → Переговори → Угода. Жоден лід не втрачається.',
    'Custom Funnel-Stufen': 'Індивідуальні етапи воронки',
    'Automatische Follow-ups': 'Автоматичні нагадування',
    'Lead-Scoring': 'Оцінка лідів',

    # Pricing section
    'Preise <span class="text-gradient">CRM-Integration</span>': 'Ціни <span class="text-gradient">CRM-інтеграція</span>',
    'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Разова оплата за налаштування. Жодних щомісячних витрат за нашу роботу.',

    # Pricing card 1
    'BASIC SETUP': 'БАЗОВИЙ ПАКЕТ',
    'Für Starter': 'Для початківців',
    '€499': '€499',
    'einmalig': 'одноразово',
    'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'Налаштування CRM (HubSpot/Pipedrive/Zoho)',
    'Website-Formulare → CRM': 'Форми з сайту → CRM',
    'Basis-Funnel (3 Stufen)': 'Базова воронка (3 етапи)',
    '1 Stunde Schulung': '1 година навчання',
    'Jetzt starten': 'Почати зараз',

    # Pricing card 2
    '🔥 EMPFOHLEN': '🔥 РЕКОМЕНДУЄМО',
    'ADVANCED': 'РОЗШИРЕНИЙ',
    'Für wachsende Unternehmen': 'Для зростаючих компаній',
    '€999': '€999',
    '<strong>Alles aus BASIC +</strong>': '<strong>Все з БАЗОВОГО +</strong>',
    'Offline Conversions (Google Ads)': 'Офлайн-конверсії (Google Ads)',
    'Meta CAPI Integration': 'Meta CAPI інтеграція',
    'Zapier/Make Automatisierungen (5 Flows)': 'Zapier/Make автоматизації (5 потоків)',
    'Custom Sales-Pipeline': 'Індивідуальна воронка продажів',
    'E-Mail-Sequenzen (Follow-ups)': 'Email-послідовності (нагадування)',
    '<strong>2 Stunden Schulung + 30 Tage Support</strong>': '<strong>2 години навчання + 30 днів підтримки</strong>',

    # Pricing card 3
    'CUSTOM': 'ІНДИВІДУАЛЬНИЙ',
    'Für Unternehmen': 'Для корпорацій',
    'Preis auf Anfrage': 'Ціна за запитом',
    '<strong>Alles aus ADVANCED +</strong>': '<strong>Все з РОЗШИРЕНОГО +</strong>',
    'Custom API-Integrationen': 'Індивідуальні API-інтеграції',
    'Unbegrenzte Automatisierungen': 'Безлімітні автоматизації',
    'Dedizierter Account Manager': 'Виділений менеджер проекту',
    'SLA + Priority Support': 'SLA + пріоритетна підтримка',
    '<strong>Individuelle Schulung & Onboarding</strong>': '<strong>Індивідуальне навчання та онбординг</strong>',
    'Kontaktieren Sie uns': 'Зв\'язатися з нами',

    # Pricing disclaimer
    '* Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': '* Ціни без ПДВ. Вартість ліцензій CRM (HubSpot, Pipedrive тощо) НЕ включена. Ми допоможемо вам обрати відповідний план.',

    # FAQ section
    'Häufig gestellte <span class="text-gradient">Fragen</span>': 'Часті <span class="text-gradient">Питання</span>',

    # FAQ 1
    '💰 Welches CRM soll ich wählen?': '💰 Яку CRM обрати?',
    '<strong>HubSpot:</strong> Am besten für Marketing + Sales zusammen. Kostenlose Version verfügbar, später ab €50/Monat.<br><br>\n                        <strong>Pipedrive:</strong> Einfaches Sales-CRM. €14/Monat pro User. Perfekt für kleine Teams.<br><br>\n                        <strong>Zoho CRM:</strong> Günstigste Option. Ab €14/Monat. Gut für Startups.<br><br>\n                        <strong>GoHighLevel:</strong> All-in-One für Agenturen. Ab €97/Monat.<br><br>\n                        Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': '<strong>HubSpot:</strong> Найкраще для маркетингу та продажів разом. Є безкоштовна версія, платна від €50/міс.<br><br>\n                        <strong>Pipedrive:</strong> Проста CRM для продажів. €14/міс за користувача. Ідеально для малих команд.<br><br>\n                        <strong>Zoho CRM:</strong> Найдешевший варіант. Від €14/міс. Добре для стартапів.<br><br>\n                        <strong>GoHighLevel:</strong> Все-в-одному для агенцій. Від €97/міс.<br><br>\n                        Ми безкоштовно порадимо, яка система підходить вашому бюджету та процесам.',

    # FAQ 2
    '⏱️ Wie lange dauert die Einrichtung?': '⏱️ Скільки часу займає налаштування?',
    '<strong>Basic Setup:</strong> 3-5 Werktage<br>\n                        <strong>Advanced Setup:</strong> 7-10 Werktage<br><br>\n                        Nach dem Kick-off-Call starten wir sofort. Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen.': '<strong>Базовий пакет:</strong> 3-5 робочих днів<br>\n                        <strong>Розширений пакет:</strong> 7-10 робочих днів<br><br>\n                        Після стартового дзвінка ми починаємо одразу. Ви отримуєте щотижневі звіти і можете ставити питання будь-коли.',

    # FAQ 3
    '🔧 Brauche ich technische Kenntnisse?': '🔧 Чи потрібні технічні знання?',
    '<strong>Nein.</strong> Wir richten alles für Sie ein. Sie bekommen eine Schulung, wie Sie das CRM nutzen, Leads bearbeiten und Reports ansehen. Nach dem Setup arbeitet alles automatisch.': '<strong>Ні.</strong> Ми налаштуємо все за вас. Ви отримаєте навчання, як користуватися CRM, обробляти ліди та переглядати звіти. Після налаштування все працює автоматично.',

    # FAQ 4
    '📊 Was sind Offline Conversions?': '📊 Що таке офлайн-конверсії?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Verkauf passiert offline (Anruf, Meeting, Rechnung). <strong>Offline Conversions</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads зазвичай бачить тільки кліки та відправлення форм. Але реальний продаж відбувається офлайн (дзвінок, зустріч, рахунок). <strong>Офлайн-конверсії</strong> відправляють ці дані назад у Google. Результат: Google знає, які кліки призводять до реальних клієнтів, і оптимізує ваші кампанії автоматично на продажі, а не тільки на ліди. <strong>ROAS зростає в середньому на 30-50%.</strong>',

    # FAQ 5
    '💬 Wie funktionieren Telegram-Benachrichtigungen?': '💬 Як працюють Telegram-сповіщення?',
    'Sobald ein Lead von Ihrer Website kommt, bekommt Ihr Sales-Manager eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Telefon, Quelle (Google Ads/Meta/etc.). Manager kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Як тільки лід надходить з вашого сайту, ваш менеджер продажів отримує повідомлення в Telegram (або Slack/WhatsApp). Повідомлення містить: Ім\'я, Email, Телефон, Джерело (Google Ads/Meta/тощо). Менеджер може одразу відреагувати. <strong>Середній час реакції: до 5 хвилин.</strong>',

    # FAQ 6
    '🔄 Bietet ihr auch laufende Betreuung?': '🔄 Чи надаєте ви подальшу підтримку?',
    'Das Setup ist einmalig. Danach arbeitet alles automatisch. Falls Sie später weitere Automatisierungen, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Налаштування одноразове. Після цього все працює автоматично. Якщо пізніше вам знадобляться додаткові автоматизації, інтеграції або оптимізації, ви можете замовити їх окремо. Вартість: €99/год.',

    # Contact section
    'Bereit, Ihr CRM <span class="text-gradient">zu verbinden?</span>': 'Готові підключити вашу <span class="text-gradient">CRM?</span>',
    'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Безкоштовна консультація — допоможемо обрати правильну CRM',

    # Contact form
    'Name *': 'Ім\'я *',
    'Ihr Name': 'Ваше ім\'я',
    'E-Mail *': 'Email *',
    'ihre.email@firma.de': 'vash.email@company.com',
    'Telefon': 'Телефон',
    'Website': 'Сайт',
    'https://ihre-website.de': 'https://vash-website.ua',
    'Ihre Nachricht *': 'Ваше повідомлення *',
    'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Яку CRM ви зараз використовуєте? Скільки лідів отримуєте щомісяця?',
    'Kostenlose Beratung anfragen': 'Замовити консультацію',
    'Antwort innerhalb von 24 Stunden. Keine Verpflichtungen.': 'Відповідь протягом 24 годин. Без зобов\'язань.',

    # Footer
    'Ihre Marketing-Agentur für DACH und Osteuropa.': 'Ваша маркетингова агенція для ринків ЄС.',
    'Google Ads': 'Google Ads',
    'Meta Ads': 'Meta Ads',
    'TikTok Ads': 'TikTok Ads',
    'SEO': 'SEO',
    'CRM-Integration': 'CRM-інтеграція',
    '&copy; 2025 Vermarkter. Alle Rechte vorbehalten.': '&copy; 2025 Vermarkter. Всі права захищені.',
    'Datenschutz': 'Політика конфіденційності',
    'Impressum': 'Юридична інформація',

    # Chatbot
    'Vermarkter Bot': 'Vermarkter Бот',
    'Online': 'Онлайн',
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Привіт! 👋 Є питання щодо CRM-інтеграції?',
    'Schreiben Sie Ihre Frage...': 'Напишіть ваше питання...',
}

# Apply translations
ua_content = de_content
for de_text, ua_text in translations.items():
    ua_content = ua_content.replace(de_text, ua_text)

# Write Ukrainian version
with open('ua/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(ua_content)

print("Ukrainsku CRM storinku stvoreno uspishno!")
print("Perekladeno: {} fraz".format(len(translations)))
