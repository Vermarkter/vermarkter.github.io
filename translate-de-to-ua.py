# -*- coding: utf-8 -*-
"""
Translate German CRM Integration page to Ukrainian
"""

# Read German version
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    de_content = f.read()

# Translation dictionary
translations = {
    'lang="de"': 'lang="uk"',

    # Meta tags
    'CRM-Integration für Marketing & Sales. HubSpot, Pipedrive, Zoho. Lead-Tracking, Offline Conversions, Telegram-Benachrichtigungen. Keine verlorenen Leads mehr.': 'Інтеграція CRM для маркетингу та продажів. HubSpot, Pipedrive, Zoho. Відстеження лідів, офлайн-конверсії, Telegram-сповіщення. Ніяких втрачених лідів.',
    '/de/crm-integration': '/ua/crm-integration',
    'og-image-crm-de.jpg': 'og-image-crm-ua.jpg',
    'CRM-Integration — Vermarkter': 'Інтеграція CRM — Vermarkter',
    'Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb. Lead-Tracking, Automatisierung, echtes ROAS.': 'З\'єднайте ваші маркетингові кампанії з продажами. Відстеження лідів, автоматизація, реальний ROAS.',
    'Verbinden Sie Marketing und Sales': 'З\'єднайте маркетинг і продажі',

    # Navigation
    'Leistungen': 'Послуги',
    'Probleme': 'Проблеми',
    'Lösung': 'Рішення',
    'Preise': 'Ціни',
    'Kontakt': 'Контакт',

    # Hero section
    'Marketing <span class="text-gradient">+ Vertrieb</span>': 'Маркетинг <span class="text-gradient">+ Продажі</span>',
    'in einem System': 'в одній системі',
    'Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.': 'З\'єднуйте Google Ads, Meta Ads та TikTok з HubSpot, Pipedrive або Zoho CRM.',
    'Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': 'Автоматичні сповіщення, відстеження продажів, реальний ROAS.',
    'Unterstützte CRM-Systeme:': 'Підтримувані CRM-системи:',
    'Keine verlorenen Leads mehr.': 'Ніяких втрачених лідів.',
    'Wir verbinden Ihre Website-Formulare direkt mit <strong>HubSpot, Pipedrive oder Zoho CRM</strong>. Telegram-Benachrichtigungen für Ihren Vertrieb. <strong>Offline Conversions</strong> zurück an Google/Meta Ads. Volle Kontrolle über Ihren Sales-Funnel.': 'Ми з\'єднуємо форми вашого сайту безпосередньо з <strong>HubSpot, Pipedrive або Zoho CRM</strong>. Telegram-сповіщення для вашого відділу продажів. <strong>Офлайн-конверсії</strong> назад у Google/Meta Ads. Повний контроль над вашою воронкою продажів.',
    'Jetzt integrieren': 'Інтегрувати зараз',
    'Setup ab €499': 'Налаштування від €499',
    'Demo buchen': 'Замовити демо',
    'Jetzt starten': 'Почати зараз',
    'Automatische Follow-ups': 'Автоматичні follow-up',
    'Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': 'Ми безкоштовно проконсультуємо, яка система підходить для вашого бюджету та процесу.',
    '💰 Welches CRM soll ich wählen?': '💰 Яку CRM обрати?',
    'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Яку CRM ви зараз використовуєте? Скільки лідів ви отримуєте на місяць?',

    # Critical missing translations from user feedback
    '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Чи знайоме вам це?</span>',
    'Die häufigsten Probleme ohne CRM-Integration': 'Найпоширеніші проблеми без інтеграції CRM',
    'Manager reagieren zu spät': 'Менеджери реагують занадто пізно',
    'Lead kommt rein': 'Лід заходить',
    'Welche Werbung funktioniert?': 'Яка реклама працює?',
    'Anruf innerhalb 5 Minuten': 'Дзвінок за 5 хвилин',
    'Besseres ROAS automatisch': 'Покращення ROAS автоматично',
    'Strukturierte Verkaufsprozesse': 'Структуровані процеси продажу',
    'Einmalige Setup-Gebühr': 'Разова плата за налаштування',
    '🔥 EMPFOHLEN': '🔥 РЕКОМЕНДУЄМО',
    'Preis auf Anfrage': 'Ціна за запитом',
    'zzgl. MwSt.': 'без ПДВ',
    'Werktage': 'робочих днів',
    'Nein. Wir richten alles für Sie ein.': 'Ні. Ми все налаштуємо за вас.',
    'Was sind Offline Conversions?': 'Що таке офлайн-конверсії?',
    'Wie funktioniert die Telegram-Benachrichtigung?': 'Як працюють сповіщення в Telegram?',
    'Bietet ihr auch laufende Betreuung?': 'Чи надаєте ви підтримку?',
    'ihre.email@firma.de': 'vash.email@company.com',
    'Kostenlose Beratung anfragen': 'Замовити безкоштовну консультацію',
    'Keine Verpflichtungen': 'Без зобов\'язань',
    'Kontaktieren Sie uns': 'Зв\'яжіться з нами',
    'Für Unternehmen': 'Для компаній',
    'Custom API-Integrationen': 'Кастомні API-інтеграції',
    'Unbegrenzte Automatisierungen': 'Безлімітні автоматизації',
    'Dedizierter Account Manager': 'Виділений менеджер',
    'SLA + Priority Support': 'SLA + Пріоритетна підтримка',
    'Individuelle Schulung & Onboarding': 'Індивідуальне навчання та онбординг',

    # Pain points section
    'Warum Leads verloren gehen': 'Чому ліди втрачаються',
    'Leads in Excel-Tabellen': 'Ліди в Excel-таблицях',
    'Ihre Leads landen in unübersichtlichen Tabellen. Manager müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Ваші ліди потрапляють у незрозумілі таблиці. Менеджери повинні вручну сортувати, визначати пріоритети та робити follow-up. <strong style="color: #EF4444;">Втрата часу + втрачені можливості.</strong>',
    'Zu späte Anrufe': 'Занадто пізні дзвінки',
    'Ein Lead kommt rein → Manager sieht es 2 Stunden später. Der Kunde hat sich bereits bei der Konkurrenz gemeldet. <strong style="color: #EF4444;">80% der Leads kaufen beim ersten Anruf.</strong>': 'Лід надходить → Менеджер бачить його через 2 години. Клієнт вже звернувся до конкурентів. <strong style="color: #EF4444;">80% лідів купують при першому дзвінку.</strong>',
    'Unbekannter ROAS': 'Невідомий ROAS',
    'Sie wissen nicht, welche Kampagne echte Verkäufe bringt. Google Ads sieht nur Klicks, nicht Zahlungen. <strong style="color: #EF4444;">Sie optimieren auf die falschen Daten.</strong>': 'Ви не знаєте, яка кампанія приносить реальні продажі. Google Ads бачить тільки кліки, а не оплати. <strong style="color: #EF4444;">Ви оптимізуєте за неправильними даними.</strong>',

    # Solution section
    'Unsere Lösung': 'Наше рішення',
    'Automatisierung': 'Автоматизація',
    'Lead von der Website → <strong>sofort ins CRM</strong> (HubSpot/Pipedrive/Zoho) → Telegram-Nachricht an den Vertrieb → Manager ruft in <strong>2 Minuten</strong> an.': 'Лід з сайту → <strong>миттєво в CRM</strong> (HubSpot/Pipedrive/Zoho) → Повідомлення в Telegram відділу продажів → Менеджер дзвонить через <strong>2 хвилини</strong>.',
    'End-to-End-Analytik': 'Наскрізна аналітика',
    'Lead klickt auf Google Ads → kauft im Laden → Wir senden <strong>Offline Conversion</strong> zurück an Google. Google lernt, <strong>welche Kampagne echtes Geld bringt</strong>.': 'Лід клікає на Google Ads → купує в магазині → Ми надсилаємо <strong>Офлайн-конверсію</strong> назад у Google. Google вчиться, <strong>яка кампанія приносить реальні гроші</strong>.',
    'Sales Pipelines': 'Воронки продажів',
    'Stufen: <strong>Neuer Lead → Anruf → Termin → Bezahlt</strong>. Automatische Follow-ups (E-Mail/SMS), wenn ein Lead stecken bleibt. Verlieren Sie nie wieder einen Deal.': 'Етапи: <strong>Новий лід → Дзвінок → Зустріч → Оплачено</strong>. Автоматичні follow-up (Email/SMS), якщо лід застряг. Ніколи більше не втрачайте угоду.',

    # System logos section
    'Systeme, mit denen wir arbeiten': 'Системи, з якими ми працюємо',

    # Pricing section
    'Für Starter': 'Для початківців',
    'einmalig': 'одноразово',
    'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'Налаштування CRM (HubSpot/Pipedrive/Zoho)',
    'Website-Formulare → CRM': 'Форми сайту → CRM',
    'Telegram-Benachrichtigungen': 'Telegram-сповіщення',
    'Basis-Funnel (3 Stufen)': 'Базова воронка (3 етапи)',
    '1 Stunde Schulung': '1 година навчання',
    'Für wachsende Unternehmen': 'Для зростаючих компаній',
    'Alles aus BASIC +': 'Все з BASIC +',
    'Offline Conversions (Google Ads)': 'Офлайн-конверсії (Google Ads)',
    'Meta CAPI Integration': 'Інтеграція Meta CAPI',
    'Zapier/Make Automatisierungen (5 Flows)': 'Автоматизації Zapier/Make (5 потоків)',
    '2 Stunden Schulung + 30 Tage Support': '2 години навчання + 30 днів підтримки',

    # FAQ section
    'Häufig gestellte Fragen': 'Часті питання',
    'Welche CRM-Systeme werden unterstützt?': 'Які CRM-системи підтримуються?',
    'Wir arbeiten hauptsächlich mit <strong>HubSpot, Pipedrive, Zoho CRM und GoHighLevel</strong>. Für Automatisierungen nutzen wir Zapier und Make.com.': 'Ми працюємо переважно з <strong>HubSpot, Pipedrive, Zoho CRM та GoHighLevel</strong>. Для автоматизацій використовуємо Zapier та Make.com.',
    'Was sind Offline Conversions?': 'Що таке офлайн-конверсії?',
    'Sie senden Daten über abgeschlossene Verkäufe zurück an Google Ads / Meta Ads. Der Algorithmus lernt, <strong>welche Kampagne echte Käufer bringt</strong>, nicht nur Klicks. ROAS steigt um 20-40%.': 'Ви надсилаєте дані про завершені продажі назад у Google Ads / Meta Ads. Алгоритм вчиться, <strong>яка кампанія приносить справжніх покупців</strong>, а не тільки кліки. ROAS зростає на 20-40%.',
    'Wie funktioniert die Telegram-Benachrichtigung?': 'Як працює Telegram-сповіщення?',
    'Sobald ein Lead das Formular ausfüllt, erhält Ihr Vertriebsteam eine <strong>sofortige Nachricht</strong> mit allen Kontaktdaten. Manager kann in 2 Minuten anrufen.': 'Як тільки лід заповнює форму, ваша команда продажів отримує <strong>миттєве повідомлення</strong> з усіма контактними даними. Менеджер може подзвонити через 2 хвилини.',
    'Brauche ich ein teures CRM?': 'Чи потрібна мені дорога CRM?',
    'Nein. <strong>HubSpot und Pipedrive haben kostenlose Pläne</strong>. Wir richten das für Sie ein. Für kleine Unternehmen reicht das völlig aus.': 'Ні. <strong>HubSpot та Pipedrive мають безкоштовні плани</strong>. Ми налаштуємо це для вас. Для малого бізнесу цього цілком достатньо.',
    'Wie lange dauert die Einrichtung?': 'Скільки часу займає налаштування?',
    '<strong>BASIC: 3-5 Werktage</strong>. ADVANCED: 7-10 Werktage (wegen Offline Conversions und Automatisierungen).': '<strong>BASIC: 3-5 робочих днів</strong>. ADVANCED: 7-10 робочих днів (через офлайн-конверсії та автоматизації).',
    'Welche Sprachen werden unterstützt?': 'Які мови підтримуються?',
    'Wir arbeiten mit Kunden in ganz Europa: <strong>Deutschland, Österreich, Schweiz, Polen, Tschechien, Ukraine und andere EU-Länder</strong>.': 'Ми працюємо з клієнтами по всій Європі: <strong>Німеччина, Австрія, Швейцарія, Польща, Чехія, Україна та інші країни ЄС</strong>.',

    # Contact form
    'Bereit für Automatisierung?': 'Готові до автоматизації?',
    'Füllen Sie das Formular aus. Wir antworten innerhalb von 24 Stunden. Kostenlose Beratung (30 Min).': 'Заповніть форму. Ми відповімо протягом 24 годин. Безкоштовна консультація (30 хв).',
    'Ihr Name': 'Ваше ім\'я',
    'Max Mustermann': 'Іван Іванов',
    'Ihre E-Mail': 'Ваш Email',
    'ihr.email@gmail.com': 'vash.email@gmail.com',
    'Telefon': 'Телефон',
    'Website': 'Веб-сайт',
    'https://ihre-website.de': 'https://vash-site.com',
    'Nachricht': 'Повідомлення',
    'Ich möchte CRM-Integration für...': 'Мені потрібна CRM-інтеграція для...',
    'Ich stimme der <a href="../privacy-policy.html" style="color: var(--brand); text-decoration: underline;">Datenschutzerklärung</a> zu.': 'Я погоджуюсь з <a href="../privacy-policy.html" style="color: var(--brand); text-decoration: underline;">Політикою конфіденційності</a>.',
    'Senden': 'Надіслати',
    'Formular wird gesendet...': 'Надсилання форми...',

    # Footer
    'Über uns': 'Про нас',
    'Marketing-Agentur für kleine Unternehmen in der Europäischen Union.': 'Маркетингова агенція для малого бізнесу в Європейському Союзі.',
    'Informationen': 'Інформація',
    'Bewertungen': 'Відгуки',
    'Rechner': 'Калькулятор',
    'Datenschutzerklärung': 'Політика конфіденційності',
    'Impressum': 'Імпресум',
    'Email': 'Email',
    'Telegram': 'Telegram',
    'Büros: Berlin, Warschau, Kyiv': 'Офіси: Берлін, Варшава, Київ',
    '© 2025 Vermarkter. Alle Rechte vorbehalten.': '© 2025 Vermarkter. Всі права захищені.',

    # Language switcher - CRITICAL FIX
    'DE ▼': 'UA ▼',

    # Footer links - CRITICAL FIX
    'https://vermarkter.eu/privacy.html': 'https://vermarkter.eu/ua/privacy.html',
    'https://vermarkter.eu/imprint.html': 'https://vermarkter.eu/ua/imprint.html',
    'Datenschutz': 'Конфіденційність',

    # Chatbot - CRITICAL FIX
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Привіт! 👋 Є питання щодо CRM-інтеграції?',
    'Schreiben Sie Ihre Frage...': 'Напишіть ваше питання...',
    'Vermarkter Bot': 'Vermarkter Бот',
    'Online': 'Онлайн',

    # Success/Error messages
    'Erfolgreich gesendet!': 'Успішно надіслано!',
    'Wir melden uns innerhalb von 24 Stunden.': 'Ми зв\'яжемося протягом 24 годин.',
    'Fehler beim Senden.': 'Помилка надсилання.',
    'Bitte versuchen Sie es später erneut oder schreiben Sie uns direkt an': 'Будь ласка, спробуйте пізніше або напишіть нам безпосередньо на',
}

# Create Ukrainian version
ua_content = de_content
for de_text, ua_text in translations.items():
    ua_content = ua_content.replace(de_text, ua_text)

# Write Ukrainian version
with open('ua/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(ua_content)

print("Ukrainian CRM page created successfully")
