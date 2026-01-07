# -*- coding: utf-8 -*-
"""
Complete Russian translation from German CRM page
"""

# Read German version
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Translation dictionary with EXACT matches
translations = {
    'lang="de"': 'lang="ru"',
    '/de/crm-integration': '/ru/crm-integration',
    'og-image-crm-de.jpg': 'og-image-crm-ru.jpg',
    'CRM-Integration — Vermarkter': 'Интеграция CRM — Vermarkter',

    # Meta descriptions
    'CRM-Integration für Marketing & Sales. HubSpot, Pipedrive, Zoho. Lead-Tracking, Offline Conversions, Telegram-Benachrichtigungen. Keine verlorenen Leads mehr.': 'Интеграция CRM для маркетинга и продаж. HubSpot, Pipedrive, Zoho. Отслеживание лидов, офлайн-конверсии, уведомления в Telegram. Больше никаких потерянных лидов.',
    'Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb. Lead-Tracking, Automatisierung, echtes ROAS.': 'Соедините маркетинговые кампании с продажами. Отслеживание лидов, автоматизация, реальный ROAS.',
    'Verbinden Sie Marketing und Sales': 'Соедините маркетинг и продажи',

    # Navigation - Change German flag to Russian
    '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#000"/>
                                <rect y="4" width="16" height="4" fill="#D00"/>
                                <rect y="8" width="16" height="4" fill="#FFCE00"/>
                            </svg>
                            DE ▼''': '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#fff"/>
                                <rect y="4" width="16" height="4" fill="#0039A6"/>
                                <rect y="8" width="16" height="4" fill="#D52B1E"/>
                            </svg>
                            RU ▼''',

    # Navigation links
    '<a href="index.html#services">Leistungen</a>': '<a href="index.html#services">Услуги</a>',
    '<a href="#probleme">Probleme</a>': '<a href="#problemy">Проблемы</a>',
    '<a href="#loesung">Lösung</a>': '<a href="#reshenie">Решение</a>',
    '<a href="#preise">Preise</a>': '<a href="#ceny">Цены</a>',
    '<a href="#contact">Kontakt</a>': '<a href="#kontakt">Контакт</a>',

    # Hero section
    '🔗 CRM-Integration': '🔗 Интеграция CRM',
    'Marketing <span class="text-gradient">+ Vertrieb</span><br>\n                    in einem System': 'Маркетинг <span class="text-gradient">+ Продажи</span><br>\n                    в одной системе',
    '<strong style="color: var(--text-primary);">Keine verlorenen Leads mehr.</strong> Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.<br>\n                    Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': '<strong style="color: var(--text-primary);">Больше никаких потерянных лидов.</strong> Подключите Google Ads, Meta Ads и TikTok к HubSpot, Pipedrive или Zoho CRM.<br>\n                    Автоматические уведомления, отслеживание продаж, реальный ROAS.',
    'Setup ab €499': 'Настройка от €499',
    'Demo buchen': 'Заказать демо',
    'Unterstützte CRM-Systeme:': 'Поддерживаемые CRM-системы:',

    # SVG labels
    '<text x="70" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Website</text>': '<text x="70" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Сайт</text>',
    '<text x="410" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Manager</text>': '<text x="410" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Менеджер</text>',
    '<text x="580" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Verkauf</text>': '<text x="580" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Продажа</text>',

    # Pain points section
    'id="probleme"': 'id="problemy"',
    '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Знакомо?</span>',
    'Die häufigsten Probleme ohne CRM-Integration': 'Самые частые проблемы без интеграции CRM',

    'Leads in Excel-Tabellen': 'Лиды в Excel-таблицах',
    'Ihre Leads landen in unübersichtlichen Tabellen. Manager müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Ваши лиды попадают в нечитаемые таблицы. Менеджеры вынуждены вручную сортировать, расставлять приоритеты и следить. <strong style="color: #EF4444;">Потеря времени + упущенные возможности.</strong>',

    'Manager reagieren zu spät': 'Менеджеры реагируют слишком поздно',
    'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Лид пришёл → Менеджер видит его только через часы → Лид покупает у конкурентов. <strong style="color: #EF4444;">Без мгновенных уведомлений вы теряете 50% лидов.</strong>',

    'Welche Werbung funktioniert?': 'Какая реклама работает?',
    'Google Ads zeigt Klicks, aber keine Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. <strong style="color: #EF4444;">Ohne Offline Conversions verbrennen Sie Budget.</strong>': 'Google Ads показывает клики, но не продажи. Вы не знаете, какие кампании приносят реальных клиентов. <strong style="color: #EF4444;">Без офлайн-конверсий вы сжигаете бюджет.</strong>',

    # Solution section
    'id="loesung"': 'id="reshenie"',
    '✅ Unsere <span class="text-gradient">Lösung</span>': '✅ Наше <span class="text-gradient">Решение</span>',
    'Was wir für Sie einrichten': 'Что мы настроим для вас',

    'Automatisierung': 'Автоматизация',
    'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Лид с сайта → сразу попадает в CRM → Менеджер получает сообщение в Telegram → Звонок в течение 5 минут.',
    'Formulare → CRM (Zapier/Make)': 'Формы → CRM (Zapier/Make)',
    'Telegram-Benachrichtigungen': 'Уведомления в Telegram',
    'Auto-Tagging nach Quelle': 'Авто-тегирование по источнику',

    'End-to-End Analytics': 'Сквозная аналитика',
    'Wir senden Verkaufsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Мы отправляем данные о продажах обратно в Google Ads и Meta. Алгоритмы учатся, какие клики становятся реальными клиентами. <strong>Лучший ROAS автоматически.</strong>',
    'Offline Conversions (Google)': 'Офлайн-конверсии (Google)',
    'CAPI für Meta Ads': 'CAPI для Meta Ads',
    'Echtes ROAS pro Kampagne': 'Реальный ROAS по кампаниям',

    'Sales-Pipelines': 'Воронки продаж',
    'Strukturierte Verkaufsprozesse: Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen. Kein Lead geht verloren.': 'Структурированные процессы продаж: Новый лид → Контакт → Предложение → Переговоры → Сделка. Ни один лид не теряется.',
    'Custom Funnel-Stufen': 'Кастомные этапы воронки',
    'Automatische Follow-ups': 'Автоматические follow-up',
    'Lead-Scoring': 'Скоринг лидов',

    # Pricing section
    'id="preise"': 'id="ceny"',
    'Preise <span class="text-gradient">CRM-Integration</span>': 'Цены <span class="text-gradient">Интеграция CRM</span>',
    'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Разовая оплата за настройку. Без ежемесячных платежей за нашу работу.',

    'BASIC SETUP': 'BASIC SETUP',
    'Für Starter': 'Для начинающих',
    'einmalig': 'разово',
    'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'Настройка CRM (HubSpot/Pipedrive/Zoho)',
    'Website-Formulare → CRM': 'Формы с сайта → CRM',
    'Basis-Funnel (3 Stufen)': 'Базовая воронка (3 этапа)',
    '1 Stunde Schulung': '1 час обучения',
    'Jetzt starten': 'Начать сейчас',

    '🔥 EMPFOHLEN': '🔥 РЕКОМЕНДУЕМ',
    'ADVANCED': 'ADVANCED',
    'Für wachsende Unternehmen': 'Для растущих компаний',
    '<strong>Alles aus BASIC +</strong>': '<strong>Всё из BASIC +</strong>',
    'Offline Conversions (Google Ads)': 'Офлайн-конверсии (Google Ads)',
    'Meta CAPI Integration': 'Интеграция Meta CAPI',
    'Zapier/Make Automatisierungen (5 Flows)': 'Автоматизации Zapier/Make.com (5 потоков)',
    'Custom Sales-Pipeline': 'Кастомная воронка продаж',
    'E-Mail-Sequenzen (Follow-ups)': 'Email-последовательности (Follow-up)',
    '<strong>2 Stunden Schulung + 30 Tage Support</strong>': '<strong>2 часа обучения + 30 дней поддержки</strong>',

    'CUSTOM': 'ИНДИВИДУАЛЬНЫЙ',
    'Für Unternehmen': 'Для компаний',
    'Preis auf Anfrage': 'Цена по запросу',
    '<strong>Alles aus ADVANCED +</strong>': '<strong>Всё из ADVANCED +</strong>',
    'Custom API-Integrationen': 'Кастомные API-интеграции',
    'Unbegrenzte Automatisierungen': 'Безлимитные автоматизации',
    'Dedizierter Account Manager': 'Выделенный account manager',
    'SLA + Priority Support': 'SLA + Приоритетная поддержка',
    '<strong>Individuelle Schulung & Onboarding</strong>': '<strong>Индивидуальное обучение и онбординг</strong>',
    'Kontaktieren Sie uns': 'Связаться с нами',

    '* Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': '* Цены без НДС. Стоимость лицензий CRM (HubSpot, Pipedrive и т.д.) НЕ включена. Поможем выбрать подходящий тариф.',

    # FAQ section
    'Häufig gestellte <span class="text-gradient">Fragen</span>': 'Частые <span class="text-gradient">Вопросы</span>',

    '💰 Welches CRM soll ich wählen?': '💰 Какую CRM выбрать?',
    '<strong>HubSpot:</strong> Am besten für Marketing + Sales zusammen. Kostenlose Version verfügbar, später ab €50/Monat.<br><br>\n                        <strong>Pipedrive:</strong> Einfaches Sales-CRM. €14/Monat pro User. Perfekt für kleine Teams.<br><br>\n                        <strong>Zoho CRM:</strong> Günstigste Option. Ab €14/Monat. Gut für Startups.<br><br>\n                        <strong>GoHighLevel:</strong> All-in-One für Agenturen. Ab €97/Monat.<br><br>\n                        Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': '<strong>HubSpot:</strong> Лучше всего для маркетинга + продаж вместе. Бесплатная версия доступна, платная от €50/мес.<br><br>\n                        <strong>Pipedrive:</strong> Простая CRM для продаж. €14/мес на пользователя. Отлично для малых команд.<br><br>\n                        <strong>Zoho CRM:</strong> Самый доступный вариант. От €14/мес. Хорош для стартапов.<br><br>\n                        <strong>GoHighLevel:</strong> Всё-в-одном для агентств. От €97/мес.<br><br>\n                        Бесплатно консультируем, какая система подойдёт под ваш бюджет и процессы.',

    '⏱️ Wie lange dauert die Einrichtung?': '⏱️ Сколько времени занимает настройка?',
    '<strong>Basic Setup:</strong> 3-5 Werktage<br>\n                        <strong>Advanced Setup:</strong> 7-10 Werktage<br><br>\n                        Nach dem Kick-off-Call starten wir sofort. Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen.': '<strong>Basic Setup:</strong> 3-5 рабочих дней<br>\n                        <strong>Advanced Setup:</strong> 7-10 рабочих дней<br><br>\n                        После стартового звонка начинаем сразу. Вы получаете еженедельные отчёты и можете задавать вопросы в любое время.',

    '🔧 Brauche ich technische Kenntnisse?': '🔧 Нужны ли технические знания?',
    '<strong>Nein.</strong> Wir richten alles für Sie ein. Sie bekommen eine Schulung, wie Sie das CRM nutzen, Leads bearbeiten und Reports ansehen. Nach dem Setup arbeitet alles automatisch.': '<strong>Нет.</strong> Мы настроим всё под ключ. Вы получите обучение, как пользоваться CRM, работать с лидами и смотреть отчёты. После настройки всё работает автоматически.',

    '📊 Was sind Offline Conversions?': '📊 Что такое офлайн-конверсии?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Verkauf passiert offline (Anruf, Meeting, Rechnung). <strong>Offline Conversions</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads обычно видит только клики и отправку форм. Но реальная продажа происходит офлайн (звонок, встреча, счёт). <strong>Офлайн-конверсии</strong> отправляют эти данные обратно в Google. Результат: Google знает, какие клики приводят к реальным клиентам, и автоматически оптимизирует кампании на продажи, а не просто на лиды. <strong>ROAS растёт в среднем на 30-50%.</strong>',

    '💬 Wie funktionieren Telegram-Benachrichtigungen?': '💬 Как работают уведомления в Telegram?',
    'Sobald ein Lead von Ihrer Website kommt, bekommt Ihr Sales-Manager eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Telefon, Quelle (Google Ads/Meta/etc.). Manager kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Как только лид приходит с вашего сайта, ваш менеджер по продажам получает сообщение в Telegram (или Slack/WhatsApp). Сообщение содержит: Имя, Email, Телефон, Источник (Google Ads/Meta/и т.д.). Менеджер может среагировать мгновенно. <strong>Среднее время реакции: менее 5 минут.</strong>',

    '🔄 Bietet ihr auch laufende Betreuung?': '🔄 Предоставляете ли вы текущую поддержку?',
    'Das Setup ist einmalig. Danach arbeitet alles automatisch. Falls Sie später weitere Automatisierungen, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Настройка разовая. После этого всё работает автоматически. Если позже понадобятся дополнительные автоматизации, интеграции или оптимизации, можете нанять нас в любой момент. Ставка: €99/час.',

    # Contact section
    'id="contact"': 'id="kontakt"',
    'Bereit, Ihr CRM <span class="text-gradient">zu verbinden?</span>': 'Готовы подключить <span class="text-gradient">CRM?</span>',
    'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Бесплатная консультация — поможем выбрать правильную CRM',

    'Name *': 'Имя *',
    'Ihr Name': 'Ваше имя',
    'E-Mail *': 'Email *',
    'ihre.email@firma.de': 'vash.email@company.ru',
    'Telefon': 'Телефон',
    '+49 123 456 7890': '+7 123 456 7890',
    'Website': 'Сайт',
    'https://ihre-website.de': 'https://vash-sait.ru',
    'Ihre Nachricht *': 'Ваше сообщение *',
    'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Какую CRM используете сейчас? Сколько лидов получаете в месяц?',
    'Kostenlose Beratung anfragen': 'Заказать бесплатную консультацию',
    'Antwort innerhalb von 24 Stunden. Keine Verpflichtungen.': 'Ответ в течение 24 часов. Без обязательств.',

    # Footer
    'Ihre Marketing-Agentur für DACH und Osteuropa.': 'Ваше маркетинговое агентство для рынков DACH и Восточной Европы.',
    'Leistungen': 'Услуги',
    'CRM-Integration': 'Интеграция CRM',
    '&copy; 2025 Vermarkter. Alle Rechte vorbehalten.': '&copy; 2025 Vermarkter. Все права защищены.',
    'Datenschutz': 'Конфиденциальность',
    'Impressum': 'Правовая информация',

    # Chatbot
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Привет! 👋 Есть вопросы по интеграции CRM?',
    'Schreiben Sie Ihre Frage...': 'Напишите ваш вопрос...',
}

# Apply translations
for de, ru in translations.items():
    content = content.replace(de, ru)

# Write Russian version
with open('ru/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Russian CRM page created successfully!")
print("Translated phrases:", len(translations))
