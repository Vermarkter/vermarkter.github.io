# -*- coding: utf-8 -*-
import re

with open('ru/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Protect HTML tags from translation by replacing them with placeholders
html_tags = {}
tag_counter = 0

def protect_tag(match):
    global tag_counter
    placeholder = f"___HTML_TAG_{tag_counter}___"
    html_tags[placeholder] = match.group(0)
    tag_counter += 1
    return placeholder

# Replace lang="de" BEFORE protecting HTML tags
content = content.replace('lang="de"', 'lang="ru"')

# Protect all HTML tags (opening, closing, and self-closing)
content = re.sub(r'<[^>]+>', protect_tag, content)

translations = {

    # Meta tags - critical for SEO
    'Performance-Marketing für kleine Unternehmen in Europa. Google Ads, Meta Ads, TikTok. Transparente Ergebnisse, professionelle Betreuung.': 'Эффективный маркетинг для малого бизнеса в Европе. Google Ads, Meta Ads, TikTok. Прозрачные результаты, профессиональная поддержка.',
    'Performance-Marketing für kleine Unternehmen in Europa. Google Ads, Meta Ads, TikTok. Transparente Ergebnisse, professioneller Support.': 'Эффективный маркетинг для малого бизнеса в Европе. Google Ads, Meta Ads, TikTok. Прозрачные результаты, профессиональная поддержка.',
    'Europa Marketing, Google Ads Deutschland, Meta Ads, Performance Marketing, ROI Rechner': 'Европа Маркетинг, Google Ads Германия, Meta Ads, Эффективный маркетинг, ROI калькулятор',
    'Marketing Deutschland, Google Ads Europa, Meta Ads, Performance Marketing, ROI Rechner': 'Маркетинг Германия, Google Ads Европа, Meta Ads, Эффективный маркетинг, ROI калькулятор',
    'Vermarkter Agency': 'Агентство Vermarkter',
    'Vermarkter — Skalieren Sie Ihr Geschäft in Europa': 'Vermarkter — Развивайте ваш бизнес в Европе',
    'Performance-Marketing für Unternehmen. Transparente Ergebnisse, professioneller Support.': 'Эффективный маркетинг для компаний. Прозрачные результаты, профессиональная поддержка.',
    'Performance-Marketing für Unternehmen': 'Эффективный маркетинг для компаний',

    # OG Tags
    'Deutschlands führende Performance-Marketing-Agentur': 'Ведущее агентство эффективного маркетинга в Германии',
    'Professionelle Performance-Marketing-Lösungen für kleine Unternehmen. Steigern Sie Umsatz, Leads und ROI mit Google Ads, Meta Ads und TikTok Ads.': 'Профессиональные решения для эффективного маркетинга для малого бизнеса. Увеличьте продажи, лиды и ROI с помощью Google Ads, Meta Ads и TikTok Ads.',

    # Page title
    '<title>Performance Marketing Agentur | ROI-fokussiert | Google & Meta Ads</title>': '<title>Агентство эффективного маркетинга | Фокус на ROI | Google & Meta Ads</title>',

    # Hero section - CRITICAL - must be BEFORE navigation
    'Werbestart in der EU in 48 Stunden': 'Запуск рекламы в ЕС за 48 часов',
    'Erste Leads in 7 Tagen. Technischer Manager in Ihrer Sprache. Wöchentliche Reports.': 'Первые лиды за 7 дней. Технический менеджер на вашем языке. Еженедельные отчеты.',

    # Navigation
    'Transparente Preise ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Прозрачные цены без скрытых расходов. Выберите идеальный пакет для вашей компании.',
    'Preise & Pakete': 'Цены и пакеты',
    'Leistungen': 'Услуги',
    'Cases': 'Кейсы',
    'Rechner': 'Калькулятор',
    'Bewertungen': 'Отзывы',
    'Preise': 'Цены',
    'Methode': 'Метод',
    'Kontakt': 'Контакт',
    'Kostenlos beraten': 'Бесплатная консультация',

    # Hero section
    'Werbestart in der EU <span class="text-gradient">in 48 Stunden</span>': 'Запуск рекламы в ЕС <span class="text-gradient">за 48 часов</span>',
    'Google Ads & Meta Ads für Ihr Business in Europa.': 'Google Ads и Meta Ads для вашего бизнеса в Европе.',
    'Performance-Marketing,': 'Эффективный маркетинг,',
    'das sich <span class="highlight">rechnet</span>': 'который <span class="highlight">окупается</span>',
    'Für kleine Unternehmen in Europa, die wachsen wollen – ohne Risiko, nur Ergebnisse.': 'Для малого бизнеса в Европе, который хочет расти – без риска, только результаты.',
    'Jetzt Potenzial berechnen': 'Рассчитать потенциал',
    'Wie wir arbeiten': 'Как мы работаем',

    # Stats section
    '% Kunden kehren zurück': '% клиентов возвращаются',
    'Durchschnittlicher ROAS': 'Средний ROAS',
    'Zufriedene Kunden': 'Довольных клиентов',
    'Verwaltetes Werbebudget/Monat': 'Управляемый рекламный бюджет/месяц',

    # Problem section
    'Warum verschwenden 80% des Budgets': 'Почему 80% бюджета тратится впустую',
    'Warum verschwinden 80% des Budgets': 'Почему 80% бюджета исчезает',
    'im Nichts': 'впустую',
    '% der Kampagnen scheitern': '% кампаний терпят неудачу',
    'fehlende Transparenz': 'отсутствие прозрачности',
    'Budget verbrannt ohne ROI': 'бюджет сожжен без ROI',
    'Die drei häufigsten Gründe für gescheiterte Werbekampagnen': 'Три наиболее частые причины провала рекламных кампаний',
    'Falsche Keywords': 'Неправильные ключевые слова',
    'Sie zahlen für Klicks von Nutzern, die nie kaufen werden. 70% des Traffics sind "informationelle" Suchanfragen ohne Kaufabsicht.': 'Вы платите за клики пользователей, которые никогда не купят. 70% трафика — это "информационные" запросы без намерения покупки.',
    'Breiter Match-Type – Sie zahlen für alles Mögliche': 'Широкое соответствие – вы платите за все подряд',
    'Keine negativen Keywords – Budget läuft aus': 'Нет минус-слов – бюджет утекает',
    'Werbung für Konkurrenten statt Zielgruppe': 'Реклама для конкурентов вместо целевой аудитории',
    'Fehlendes End-to-End Tracking': 'Отсутствие сквозной аналитики',
    'Ohne korrektes Tracking wissen Sie nicht, welche Anzeige/Keywords Verkäufe bringen. Sie steuern blind.': 'Без правильной аналитики вы не знаете, какие объявления/ключевые слова приносят продажи. Вы управляете вслепую.',
    'Google Analytics falsch konfiguriert': 'Google Analytics неправильно настроен',
    'Conversions werden nicht an Ads übermittelt': 'Конверсии не передаются в Ads',
    'Keine Attribution – Customer Journey unklar': 'Нет атрибуции – путь клиента неясен',
    'Schwache Creatives': 'Слабые креативы',
    'Niedrige CTR = hoher CPC. Schlechte Texte und Banner senken den Quality Score und Sie zahlen für jeden Klick mehr.': 'Низкий CTR = высокая цена клика. Плохие тексты и баннеры снижают показатель качества, и вы платите за каждый клик больше.',
    'Generische Texte ohne USP – niemand klickt': 'Общие тексты без УТП – никто не кликает',
    'Banner in Paint erstellt – sieht aus wie Spam': 'Баннеры сделаны в Paint – выглядят как спам',
    'Keine A/B-Tests – Sie bleiben beim ersten Entwurf': 'Нет A/B-тестов – остаетесь с первым вариантом',

    'Kennst du das?': 'Знакомо?',
    '<strong>Werbung kostet,</strong> bringt aber keine Kunden?': '<strong>Реклама стоит денег,</strong> но не приносит клиентов?',
    'Du probierst Facebook Ads, Google Ads – das Geld ist weg, aber die Anfragen bleiben aus.': 'Вы пробуете Facebook Ads, Google Ads – деньги потрачены, но заявок нет.',
    '<strong>Keine Zeit</strong> für Kampagnen-Management?': '<strong>Нет времени</strong> на управление кампаниями?',
    'Du willst dich auf dein Business konzentrieren, nicht stundenlang in Werbe-Dashboards sitzen.': 'Вы хотите сосредоточиться на своем бизнесе, а не часами сидеть в рекламных панелях.',
    '<strong>Du weißt nicht,</strong> ob deine Werbung funktioniert?': '<strong>Вы не знаете,</strong> работает ли ваша реклама?',
    'Keine klaren Zahlen, keine Transparenz – nur vage Versprechen von „Reichweite" und „Impressionen".': 'Никаких четких цифр, никакой прозрачности – только расплывчатые обещания об «охвате» и «показах».',

    # Solution intro
    'Wir machen Performance-Marketing': 'Мы делаем эффективный маркетинг',
    '<span class="highlight">transparent & messbar</span>': '<span class="highlight">прозрачным и измеримым</span>',

    # Method section (3 steps)
    'Unser Ansatz': 'Наш подход',
    'Unsere Methodik: 3-Stufen-System': 'Наша методика: 3-ступенчатая система',
    'So arbeiten wir': 'Как мы работаем',
    'So funktioniert\'s': 'Как это работает',
    'Unsere <span class="highlight">3-Schritte-Methode</span>': 'Наш <span class="highlight">3-шаговый метод</span>',
    'SCHRITT 1': 'ШАГ 1',
    'SCHRITT 2': 'ШАГ 2',
    'SCHRITT 3': 'ШАГ 3',

    'Analyse & Strategie': 'Анализ и стратегия',
    'Audit & Strategie': 'Аудит и стратегия',
    'Tiefgehende Analyse': 'Глубокий анализ',
    'Wir analysieren dein Business, deine Zielgruppe und deine Ziele. Daraus entwickeln wir eine maßgeschneiderte Strategie – ohne Standardlösungen.': 'Мы анализируем ваш бизнес, вашу целевую аудиторию и ваши цели. На основе этого мы разрабатываем индивидуальную стратегию – без стандартных решений.',
    'Wir finden, wo Ihr Budget verschwindet. Analyse von Wettbewerbern, Semantik und technischen Fehlern.': 'Мы находим, куда уходит ваш бюджет. Анализ конкурентов, семантики и технических ошибок.',
    'Nischenanalyse': 'Анализ ниши',
    'Suche nach "Gold"-Keywords': 'Поиск "золотых" ключевых слов',
    'Technisches Audit': 'Технический аудит',
    'Wettbewerber-Mapping': 'Карта конкурентов',

    'Setup & Launch': 'Настройка и запуск',
    'Kampagnen-Setup': 'Настройка кампаний',
    'Kampagnen Launch': 'Запуск кампаний',
    'Kampagnen-Launch': 'Запуск кампаний',
    'Struktur und Launch': 'Структура и запуск',
    'Wir erstellen professionelle Kampagnen auf Google Ads, Meta (Facebook/Instagram) oder TikTok – perfekt abgestimmt auf deine Ziele.': 'Мы создаем профессиональные кампании в Google Ads, Meta (Facebook/Instagram) или TikTok – идеально настроенные под ваши цели.',
    'Wir erstellen Kampagnen mit +8% CTR und Conversion-Tracking ab Tag 1. Keine Experimente.': 'Мы создаем кампании с +8% CTR и отслеживанием конверсий с 1-го дня. Никаких экспериментов.',
    'Strukturierung nach Intent': 'Структурирование по намерению',
    'Conversion-Setup (GA4 + Ads)': 'Настройка конверсий (GA4 + Ads)',
    'Creatives (Texte + Banner)': 'Креативы (тексты + баннеры)',
    'Erster Traffic in 48h': 'Первый трафик за 48 часов',

    'Optimierung & Reporting': 'Оптимизация и отчетность',
    'Optimierung & Skalierung': 'Оптимизация и масштабирование',
    'Wöchentliche Optimierung': 'Еженедельная оптимизация',
    'Du bekommst wöchentlich klare Zahlen: Kosten, Leads, Umsatz, ROI. Wir optimieren laufend – damit deine Werbung immer besser wird.': 'Вы получаете еженедельно четкие цифры: затраты, лиды, доход, ROI. Мы постоянно оптимизируем – чтобы ваша реклама становилась лучше.',
    'Wir analysieren jeden €, pausieren teure Keywords und skalieren profitable Kampagnen.': 'Мы анализируем каждый €, останавливаем дорогие ключевые слова и масштабируем прибыльные кампании.',
    'Wöchentliche Reports': 'Еженедельные отчеты',
    'Search Terms Analyse': 'Анализ поисковых запросов',
    'Bid-Anpassungen': 'Корректировка ставок',
    'Creative-Tests (A/B)': 'Тесты креативов (A/B)',
    'Bereit zu wachsen?': 'Готовы к росту?',
    'Lassen Sie uns Ihr Business skalieren': 'Позвольте нам масштабировать ваш бизнес',
    'Wir bauen Kampagnen nach SKAG-Prinzip. Klares Conversion-Tracking.': 'Мы строим кампании по принципу SKAG. Четкое отслеживание конверсий.',

    # Services section
    'Full Stack Marketing Services': 'Комплексные маркетинговые услуги',
    'Von der Strategie bis zur Umsetzung – alles aus einer Hand': 'От стратегии до реализации – все из одних рук',

    # Google Ads service details
    'Heißer Traffic aus der Suche. Performance Max für E-Commerce. Shopping Ads für Produkte. Launch in 48 Stunden.': 'Горячий трафик из поиска. Performance Max для электронной коммерции. Shopping Ads для товаров. Запуск за 48 часов.',
    'Search Ads (hohe Kaufabsicht)': 'Search Ads (высокая покупательская способность)',
    'Performance Max (KI-Optimierung)': 'Performance Max (AI-оптимизация)',
    'Shopping Ads (für Online-Shops)': 'Shopping Ads (для интернет-магазинов)',
    'hohe Kaufabsicht': 'высокая покупательская способность',
    'KI-Optimierung': 'AI-оптимизация',
    'für Online-Shops': 'для интернет-магазинов',
    'Unsere Leistungen': 'Наши услуги',

    'Google Ads Management': 'Управление Google Ads',
    'Such-, Display- und Shopping-Kampagnen, die Kunden bringen – nicht nur Klicks.': 'Поисковые, медийные и торговые кампании, которые приносят клиентов – а не только клики.',
    'Heißer Traffic aus der Suche. Performance Max für E-Commerce. Shopping Ads für Produkte. Launch w 48 godzin.': 'Горячий трафик из поиска. Performance Max для e-commerce. Shopping Ads для товаров. Запуск за 48 часов.',
    'Shopping Ads (für Online-Shops)': 'Shopping Ads (для интернет-магазинов)',

    'Meta Ads (Facebook & Instagram)': 'Meta Ads (Facebook и Instagram)',
    'Zielgruppengerechte Anzeigen, die Aufmerksamkeit erzeugen und konvertieren.': 'Объявления для целевой аудитории, которые привлекают внимание и конвертируют.',
    'Lead-Generierung und Verkäufe über Facebook und Instagram. Lookalike Audiences, Remarketing, Messenger Ads.': 'Генерация лидов и продаж через Facebook и Instagram. Lookalike Audiences, Remarketing, Messenger Ads.',

    'TikTok Ads': 'TikTok Ads',
    'Kreative Video-Ads für junge Zielgruppen – authentisch, viral, wirksam.': 'Креативная видеореклама для молодой аудитории – аутентичная, вирусная, эффективная.',
    'Viraler Content und junge Zielgruppe. In-Feed Ads, Spark Ads, Shopping Ads. Günstiger Traffic für E-Commerce.': 'Вирусный контент и молодая аудитория. In-Feed Ads, Spark Ads, Shopping Ads. Недорогой трафик для e-commerce.',
    'Spark Ads (organische Posts als Werbung)': 'Spark Ads (органические посты как реклама)',

    'SEO & Content Marketing': 'SEO и контент-маркетинг',
    'Organischer Traffic aus Google. Lokales SEO für die EU. Content-Marketing und Linkbuilding. Langfristige Ergebnisse.': 'Органический трафик из Google. Локальное SEO для ЕС. Контент-маркетинг и линкбилдинг. Долгосрочные результаты.',

    'ROI-Tracking & Reporting': 'ROI-Отслеживание и отчетность',
    'Volle Transparenz: Du siehst genau, was deine Werbung bringt – in Euro und Cent.': 'Полная прозрачность: вы видите точно, что приносит ваша реклама – в евро и центах.',

    'CRM Integration': 'Интеграция CRM',
    'Alle Leads automatisch in Telegram/Google Sheets. Email/SMS Auto-Funnels. Volle Kontrolle über Ihren Sales Funnel.': 'Все лиды автоматически в Telegram/Google Sheets. Email/SMS авто-воронки. Полный контроль над вашей воронкой продаж.',
    'Email Marketing (Mailchimp, SendGrid)': 'Email-маркетинг (Mailchimp, SendGrid)',
    'Zapier/Make.com Integrationen': 'Интеграции Zapier/Make.com',
    'Telegram Bot für Leads (sofortige Benachrichtigungen)': 'Telegram-бот для лидов (мгновенные уведомления)',

    'Web Analytics': 'Веб-аналитика',
    'Analityka webowa': 'Веб-аналитика',
    'GA4, GTM, Hotjar, Microsoft Clarity. Vollständiges Verständnis des Nutzerverhaltens. Dashboards in Looker Studio.': 'GA4, GTM, Hotjar, Microsoft Clarity. Полное понимание поведения пользователей. Дашборды в Looker Studio.',
    'GA4 Setup (Enhanced Ecommerce)': 'Настройка GA4 (Enhanced Ecommerce)',
    'Heatmaps & Session Recordings (Hotjar)': 'Тепловые карты и записи сессий (Hotjar)',
    'Custom Dashboards (Looker Studio)': 'Пользовательские дашборды (Looker Studio)',

    'Optimierung': 'Оптимизация',
    'Tägliche Gebotsanpassungen. Budget-Skalierung nur bei positivem ROAS.': 'Ежедневная корректировка ставок. Масштабирование бюджета только при положительном ROAS.',
    'Reporting': 'Отчетность',
    'Analytics-Setup': 'Настройка аналитики',
    'Anzeigenerstellung': 'Создание объявлений',

    # Pricing section
    'Für kleine Unternehmen in der EU': 'Для малого бизнеса в ЕС',
    'Über 100 erfolgreiche Projekte für kleine Unternehmen in der EU': 'Более 100 успешных проектов для малого бизнеса в ЕС',
    'Flexibel, transparent, <span class="highlight">fair</span>': 'Гибко, прозрачно, <span class="highlight">честно</span>',

    # Starter package
    'Starter': 'Старт',
    'Perfekt für den Einstieg': 'Идеально для начала',
    'ab': 'от',
    '€/Monat': '€/месяц',
    '1 Werbekanal (z.B. Google Ads)': '1 рекламный канал (например, Google Ads)',
    'Basis-Setup & Kampagnen': 'Базовая настройка и кампании',
    'Monatliches Reporting': 'Ежемесячная отчетность',
    'E-Mail-Support': 'Поддержка по электронной почте',
    'Jetzt starten': 'Начать сейчас',

    # Professional package
    'Einmaliges Setup: €200': 'Первоначальная настройка: €200',
    'Professional': 'Профессионал',
    'Für wachsende Unternehmen': 'Для растущих компаний',
    'Beliebteste Option': 'Самый популярный вариант',
    'Bis zu 2 Werbekanäle': 'До 2 рекламных каналов',
    'Erweiterte Kampagnen-Optimierung': 'Расширенная оптимизация кампаний',
    'Wöchentliches Reporting': 'Еженедельная отчетность',
    'Telefon- & E-Mail-Support': 'Поддержка по телефону и электронной почте',
    'A/B-Testing': 'A/B-тестирование',

    # Enterprise package
    'Für schnell wachsende Unternehmen': 'Для быстрорастущих компаний',
    'Einmaliges Setup: <strong style="color: var(--brand);">€0 (kostenlos)</strong>': 'Первоначальная настройка: <strong style="color: var(--brand);">€0 (бесплатно)</strong>',
    'Enterprise': 'Корпоративный',
    'Maximale Performance': 'Максимальная эффективность',
    'Auf Anfrage': 'По запросу',
    'Alle Werbekanäle': 'Все рекламные каналы',
    'Dedizierter Account Manager': 'Выделенный менеджер аккаунта',
    'Tägliches Monitoring': 'Ежедневный мониторинг',
    'Priority-Support': 'Приоритетная поддержка',
    'Custom-Strategie': 'Индивидуальная стратегия',
    'Beratung anfragen': 'Запросить консультацию',

    # Calculator section
    'Potenzial-Rechner': 'Калькулятор потенциала',
    'ROI-Rechner': 'ROI-калькулятор',
    'ROI-Kalkulator': 'ROI-калькулятор',
    'Berechne, wie viel <span class="highlight">mehr Umsatz</span> du mit Performance-Marketing erzielen kannst': 'Рассчитайте, насколько <span class="highlight">больше дохода</span> вы можете получить с помощью эффективного маркетинга',
    'Berechnen Sie die Rentabilität Ihrer Werbekampagne': 'Рассчитайте рентабельность вашей рекламной кампании',
    'Berechnen Sie Ihren potenziellen Gewinn': 'Рассчитайте свою потенциальную прибыль',
    'Dies ist ein echtes Mediaplanungs-Tool.': 'Это настоящий инструмент медиапланирования.',
    'Dieselben Formeln, die große Agenturen verwenden. Transparent, ehrlich, ohne versteckte Kosten.': 'Те же формулы, которые используют крупные агентства. Прозрачно, честно, без скрытых расходов.',

    # Calculator form
    'Wählen Sie Ihre Branche:': 'Выберите вашу отрасль:',
    'Deine Branche': 'Ваша отрасль',
    'Wähle deine Branche': 'Выберите вашу отрасль',
    'Eigene Eingabe': 'Свой вариант',
    'E-Commerce (Produkte)': 'Электронная коммерция (товары)',
    'Dienstleistungen (Handwerk, Beauty)': 'Услуги (ремесло, красота)',
    'Immobilien': 'Недвижимость',
    'B2B / Großhandel': 'B2B / Оптовая торговля',
    'Gesundheit & Medizin': 'Здоровье и медицина',

    'Durchschnittlicher Auftragswert': 'Средняя стоимость заказа',
    'z.B. 500 für einen Handwerker-Auftrag': 'например, 500 для заказа у ремесленника',

    'Monatliches Werbebudget': 'Ежемесячный рекламный бюджет',
    'Wie viel möchtest du monatlich in Werbung investieren?': 'Сколько вы хотите ежемесячно инвестировать в рекламу?',

    'Potenzial berechnen': 'Рассчитать потенциал',

    # Calculator results
    'Dein monatliches Potenzial:': 'Ваш ежемесячный потенциал:',
    'Potenzielle Leads': 'Потенциальные лиды',
    'Potenzielle Klicks': 'Потенциальные клики',
    'Geschätzte Kosten pro Lead': 'Ориентировочная стоимость лида',
    'Erwarteter Umsatz': 'Ожидаемый доход',
    'Geschätzter Gewinn': 'Ориентировочная прибыль',
    'ROAS (Return on Ad Spend)': 'ROAS (возврат на рекламные расходы)',

    # Disclaimer
    '*Basierend auf Branchen-Durchschnittswerten. Tatsächliche Ergebnisse können variieren.': '*На основе средних показателей по отрасли. Фактические результаты могут отличаться.',

    # Testimonials section
    'Das sagen unsere Kunden': 'Что говорят наши клиенты',

    # Testimonial 1
    'Endlich Werbung, die funktioniert! Seit 3 Monaten arbeiten wir zusammen – unsere Anfragen haben sich verdoppelt, und ich weiß genau, woher sie kommen.': 'Наконец-то реклама, которая работает! Мы работаем вместе уже 3 месяца – наши заявки удвоились, и я точно знаю, откуда они приходят.',
    'Michael S.': 'Михаэль З.',
    'Handwerksbetrieb, München': 'Ремесленное предприятие, Мюнхен',

    # Testimonial 2
    'Ich hatte vorher selbst Google Ads probiert – Katastrophe. Jetzt läuft alles professionell, und ich bekomme wöchentlich klare Zahlen. Kann ich nur empfehlen!': 'Раньше я сам пробовал Google Ads – катастрофа. Теперь все работает профессионально, и я получаю четкие цифры каждую неделю. Могу только рекомендовать!',
    'Anna K.': 'Анна К.',
    'Online-Shop für Naturkosmetik': 'Интернет-магазин натуральной косметики',

    # Testimonial 3
    'Transparenz, Professionalität und Ergebnisse – genau das, was ich gesucht habe. Unser ROI liegt konstant über 400%.': 'Прозрачность, профессионализм и результаты – именно то, что я искал. Наш ROI стабильно выше 400%.',
    'Thomas B.': 'Томас Б.',
    'B2B-Dienstleister, Berlin': 'B2B-поставщик услуг, Берлин',

    # Additional content
    'Kundenbewertungen': 'Отзывы клиентов',
    '"Vermarkter hat uns geholfen, unseren Online-Shop in Deutschland in 6 Tagen zu starten. Die ersten Verkäufe kamen schon nach einer Woche! ROAS 380%."': '"Vermarkter помог нам запустить интернет-магазин в Германии за 6 дней. Первые продажи пришли уже через неделю! ROAS 380%."',
    '"Die Meta Ads-Kampagnen brachten uns +180% Lead-Wachstum in 2 Monaten. Empfehle allen, die Transparenz und Ergebnisse suchen!"': '"Кампании Meta Ads принесли нам +180% рост лидов за 2 месяца. Рекомендую всем, кто ищет прозрачность и результаты!"',
    '"Google-Werbung in 2 Tagen gestartet. Nach einer Woche bekamen wir die ersten 15 Anfragen. CRM-Integration mit Telegram - einfach Bombe!"': '"Реклама Google запущена за 2 дня. Через неделю получили первые 15 заявок. Интеграция CRM с Telegram - просто бомба!"',
    '"Die SEO-Strategie funktioniert! In 4 Monaten sind wir in den Top 3 für alle Keywords. Organischer Traffic ist um 300% gestiegen."': '"SEO-стратегия работает! За 4 месяца мы в топ-3 по всем ключевым словам. Органический трафик вырос на 300%."',
    '"Das Vermarkter-Team kennt sich aus. Transparente Reports, klare KPIs, immer auf Deutsch erreichbar. Arbeiten seit 8 Monaten zusammen."': '"Команда Vermarkter знает свое дело. Прозрачные отчеты, четкие KPI, всегда на связи. Работаем вместе уже 8 месяцев."',
    'Wir sind auf den EU-Markt spezialisiert: Deutschland, Polen, Tschechien, Österreich und andere EU-Länder. Wir kennen die lokalen Besonderheiten jedes Marktes.': 'Мы специализируемся на рынке ЕС: Германия, Польша, Чехия, Австрия и другие страны ЕС. Мы знаем локальные особенности каждого рынка.',

    # FAQ section
    'Häufige Fragen': 'Частые вопросы',
    'Häufig gestellte Fragen': 'Часто задаваемые вопросы',
    'Alles, was Sie über unsere Dienstleistungen wissen müssen': 'Все, что вам нужно знать о наших услугах',

    # FAQ 1
    'Für wen ist Performance-Marketing geeignet?': 'Для кого подходит эффективный маркетинг?',
    'Performance-Marketing eignet sich für kleine und mittlere Unternehmen, die online wachsen wollen – egal ob E-Commerce, Dienstleistungen, B2B oder lokale Geschäfte.': 'Эффективный маркетинг подходит для малого и среднего бизнеса, который хочет расти онлайн – независимо от того, это электронная коммерция, услуги, B2B или местный бизнес.',

    # FAQ 2
    'Wie schnell sehe ich Ergebnisse?': 'Как быстро я увижу результаты?',
    'Wie schnell kann ich mit Ergebnissen rechnen': 'Как быстро я могу ожидать результаты',
    'Die ersten Daten kommen schon in den ersten Tagen. Messbare Ergebnisse (Leads, Verkäufe) siehst du in der Regel nach 2-4 Wochen – abhängig von deiner Branche und deinem Budget.': 'Первые данные появляются уже в первые дни. Измеримые результаты (лиды, продажи) вы увидите обычно через 2-4 недели – в зависимости от вашей отрасли и бюджета.',
    'Erste Ergebnisse sehen Sie in der Regel innerhalb von 48-72 Stunden nach dem Launch. Optimale Performance erreichen Kampagnen nach 2-4 Wochen Optimierung.': 'Первые результаты обычно видны в течение 48-72 часов после запуска. Оптимальной производительности кампании достигают после 2-4 недель оптимизации.',

    # FAQ 3
    'Brauche ich ein großes Werbebudget?': 'Нужен ли большой рекламный бюджет?',
    'Nein. Wir arbeiten auch mit kleinen Budgets ab 500 €/Monat. Wichtig ist, dass das Budget zur Branche und den Zielen passt.': 'Нет. Мы работаем и с небольшими бюджетами от 500 €/месяц. Важно, чтобы бюджет соответствовал отрасли и целям.',
    'Welches Budget sollte ich für Werbung einplanen?': 'Какой бюджет нужно планировать на рекламу?',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen: €1.000-1.500/Monat. Nutzen Sie unseren ROI-Rechner oben für eine genaue Prognose.': 'Это зависит от вашей ниши и целей. Минимальный бюджет для эффективных кампаний: €1.000-1.500/месяц. Используйте наш ROI-калькулятор выше для точного прогноза.',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen: €1.000-1.500/Monat. Nutzen Sie unseren ROI-Kalkulator oben für eine genaue Prognose.': 'Это зависит от вашей ниши и целей. Минимальный бюджет для эффективных кампаний: €1.000-1.500/месяц. Используйте наш ROI-калькулятор выше для точного прогноза.',
    'Das Mindestbudget für Google Ads liegt bei €500/Monat. Für Meta Ads empfehlen wir mindestens €300/Monat. Kleinere Budgets bringen keine statistisch relevanten Daten.': 'Минимальный бюджет для Google Ads составляет €500/месяц. Для Meta Ads мы рекомендуем минимум €300/месяц. Меньшие бюджеты не дают статистически значимых данных.',

    # FAQ 4
    'Was unterscheidet euch von anderen Agenturen?': 'Чем вы отличаетесь от других агентств?',
    'Volle Transparenz, klare Zahlen und keine langfristigen Verträge. Du zahlst nur, solange du zufrieden bist. Keine versteckten Kosten, keine leeren Versprechen.': 'Полная прозрачность, четкие цифры и никаких долгосрочных контрактов. Вы платите только пока довольны. Никаких скрытых расходов, никаких пустых обещаний.',

    # FAQ 5
    'Kann ich jederzeit kündigen?': 'Могу ли я отказаться в любое время?',
    'Ja. Unsere Verträge sind monatlich kündbar. Kein Risiko, keine Bindung.': 'Да. Наши контракты можно расторгнуть ежемесячно. Никакого риска, никаких обязательств.',
    'Benötige ich eine eigene Website?': 'Нужен ли мне собственный сайт?',
    'Nicht unbedingt. Wir können für Sie eine konversionsstarke Landing Page erstellen oder Sie können unsere vorgefertigten Templates verwenden.': 'Необязательно. Мы можем создать для вас лендинг с высокой конверсией или вы можете использовать наши готовые шаблоны.',
    'Gibt es eine Mindestvertragslaufzeit?': 'Есть ли минимальный срок контракта?',
    'Ja, die Mindestvertragslaufzeit beträgt 3 Monate. Dies gibt uns genügend Zeit, um Ihre Kampagnen zu optimieren und echte Ergebnisse zu liefern. Danach keine Bindung.': 'Да, минимальный срок контракта составляет 3 месяца. Это дает нам достаточно времени для оптимизации ваших кампаний и достижения реальных результатов. После этого никаких обязательств.',
    'In welchen Ländern arbeiten Sie?': 'В каких странах вы работаете?',

    # Pricing section
    'Preise und Pakete': 'Цены и пакеты',
    'und Pakete': 'и пакеты',
    'Transparente Preise ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Прозрачные цены без скрытых расходов. Выберите идеальный пакет для вашего бизнеса.',
    '* Preise exkl. MwSt. Mindestvertrag 3 Monate, danach keine Bindung.': '* Цены без НДС. Минимальный контракт 3 месяца, после этого никаких обязательств.',

    # Calculator section
    'ROI Rechner': 'ROI калькулятор',
    'Berechnen Sie die Rentabilität Ihrer Werbekampagne': 'Рассчитайте рентабельность вашей рекламной кампании',
    'Dies ist ein echtes Mediaplanungs-Tool.': 'Это настоящий инструмент медиапланирования.',
    'Dieselben Formeln, die große Agenturen verwenden. Transparent, ehrlich, ohne versteckte Kosten.': 'Те же формулы, которые используют крупные агентства. Прозрачно, честно, без скрытых расходов.',
    'Wählen Sie Ihre Branche:': 'Выберите вашу отрасль:',
    'Eigene Eingabe': 'Свой вариант',
    'E-commerce (Produkte)': 'Электронная коммерция (товары)',
    'Dienstleistungen (Handwerk, Beauty)': 'Услуги (ремесла, красота)',
    'Immobilien': 'Недвижимость',
    'B2B / Großhandel': 'B2B / Оптовая торговля',
    'Infobusiness / Kurse': 'Инфобизнес / Курсы',
    'Monatliches Budget (€)': 'Месячный бюджет (€)',
    'Cost per Click (€)': 'Цена за клик (€)',
    'Conversion Rate (%)': 'Конверсия (%)',
    'Durchschnittlicher Bestellwert (€)': 'Средний чек (€)',
    'Gewinnmarge (%)': 'Маржа прибыли (%)',

    # Calculator results
    'Klicks': 'Клики',
    'Leads': 'Лиды',
    'Gewinn': 'Прибыль',
    '💰 Gewinn berechnen': '💰 Рассчитать прибыль',
    'Strategie für diese Zahlen erhalten': 'Получить стратегию для этих цифр',
    'Das Ergebnis ist eine Prognose, kein Versprechen.<br>': 'Результат является прогнозом, а не обещанием.<br>',
    'Marketing beginnt mit ehrlichen Zahlen.': 'Маркетинг начинается с честных цифр.',
    'Gewinnwachstum': 'Рост прибыли',

    # CTA section
    'Bereit zu starten': 'Готовы начать',
    'Bereit zu starten?': 'Готовы начать?',
    'Bereit zu wachsen': 'Готовы расти',
    'Bereit für messbares Wachstum?': 'Готовы к измеримому росту?',
    'Lass uns in einem kostenlosen Erstgespräch herausfinden, wie viel Potenzial in deinem Business steckt.': 'Давайте на бесплатной первой консультации узнаем, какой потенциал есть в вашем бизнесе.',
    'Kontaktieren Sie uns für ein technisches Audit oder eine Erstberatung': 'Свяжитесь с нами для технического аудита или первичной консультации',
    'Sprechen Sie mit einem Experten': 'Поговорите с экспертом',
    'Jetzt kostenlos beraten lassen': 'Получить бесплатную консультацию',
    'Keine Verpflichtungen • 100% transparent': 'Без обязательств • 100% прозрачно',

    # Contact form
    'Kontaktiere uns': 'Свяжитесь с нами',
    'Ihr Name': 'Ваше имя',
    'Name': 'Имя',
    'Dein Name': 'Ваше имя',
    'Ihre E-Mail': 'Ваш email',
    'Email': 'Email',
    'Deine Email-Adresse': 'Ваш email адрес',
    'Telefon (optional)': 'Телефон (необязательно)',
    'Deine Telefonnummer': 'Ваш номер телефона',
    'Ihre Nachricht': 'Ваше сообщение',
    'Nachricht': 'Сообщение',
    'Beschreiben Sie Ihr Projekt...': 'Опишите ваш проект...',
    'Beschreibe dein Projekt...': 'Опишите ваш проект...',
    'Nachricht senden': 'Отправить сообщение',
    'Anfrage senden': 'Отправить запрос',
    'Vielen Dank! Wir melden uns in Kürze bei Ihnen.': 'Спасибо! Мы свяжемся с вами в ближайшее время.',
    'Oder kontaktieren Sie uns direkt:': 'Или свяжитесь с нами напрямую:',

    # Footer
    'Marketing-Agentur für kleine Unternehmen in der Europäischen Union.': 'Маркетинговое агентство для малого бизнеса в Европейском Союзе.',
    'Über uns': 'О нас',
    'Performance-Marketing-Agentur für kleine und mittlere Unternehmen in Europa. Spezialisiert auf Google Ads, Meta Ads und TikTok Ads.': 'Агентство эффективного маркетинга для малого и среднего бизнеса в Европе. Специализируемся на Google Ads, Meta Ads и TikTok Ads.',

    'Schnelllinks': 'Быстрые ссылки',
    'Services': 'Услуги',
    'Portfolio': 'Портфолио',
    'Blog': 'Блог',
    'Pricing': 'Цены',
    'Methodik': 'Методика',

    'Folgen Sie uns': 'Следите за нами',
    'Legal': 'Юридическая информация',
    'Rechtliches': 'Юридическая информация',
    'Impressum': 'Выходные данные',
    'Datenschutz': 'Конфиденциальность',
    'AGB': 'Условия использования',

    'Alle Rechte vorbehalten': 'Все права защищены',
    '© 2025 Performance Marketing Agentur. Alle Rechte vorbehalten.': '© 2025 Агентство эффективного маркетинга. Все права защищены.',

    # Pricing additional
    'Pro Monat': 'В месяц',
    'Was ist enthalten': 'Что входит',
    'Was ist enthalten:': 'Что входит:',
    'Strategie-Call': 'Стратегический звонок',
    'Keyword-Recherche': 'Исследование ключевых слов',
    'Campaign Setup': 'Настройка кампании',
    'Monatliche Optimierung': 'Ежемесячная оптимизация',
    'Tägliche Optimierung': 'Ежедневная оптимизация',
    'Dedicated Account Manager': 'Выделенный менеджер аккаунта',
    'Zugang zu': 'Доступ к',
    'Kontakt aufnehmen': 'Связаться',
    'Perfekt für den Einstieg': 'Идеально для начала',
    'Wachstum': 'Рост',
}

# Apply translations (sorted by key length, longest first to avoid partial replacements)
for de, ru in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
    content = content.replace(de, ru)

# Restore HTML tags
for placeholder, tag in html_tags.items():
    content = content.replace(placeholder, tag)

# Fix language switcher - replace German flag with Russian flag
# Replace the button with German flag
german_flag_button = '''<button class="lang-button">
                            <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#000"/>
                                <rect y="4" width="16" height="4" fill="#D00"/>
                                <rect y="8" width="16" height="4" fill="#FFCE00"/>
                            </svg>
                            DE ▼
                        </button>'''

russian_flag_button = '''<button class="lang-button">
                            <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#fff"/>
                                <rect y="4" width="16" height="4" fill="#0039A6"/>
                                <rect y="8" width="16" height="4" fill="#D52B1E"/>
                            </svg>
                            RU ▼
                        </button>'''

content = content.replace(german_flag_button, russian_flag_button)

# Add German language to dropdown (remove Russian from dropdown if exists)
# Find the dropdown and add DE after UA
ua_dropdown = '''<li><a href="../ua/" style="display:block; padding:5px 10px;">
                                <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                    <rect width="16" height="6" fill="#0057B7"/>
                                    <rect y="6" width="16" height="6" fill="#FFD700"/>
                                </svg>
                                UA
                            </a></li>'''

ua_de_dropdown = '''<li><a href="../ua/" style="display:block; padding:5px 10px;">
                                <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                    <rect width="16" height="6" fill="#0057B7"/>
                                    <rect y="6" width="16" height="6" fill="#FFD700"/>
                                </svg>
                                UA
                            </a></li>
                            <li><a href="../de/" style="display:block; padding:5px 10px;">
                                <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                    <rect width="16" height="4" fill="#000"/>
                                    <rect y="4" width="16" height="4" fill="#D00"/>
                                    <rect y="8" width="16" height="4" fill="#FFCE00"/>
                                </svg>
                                DE
                            </a></li>'''

content = content.replace(ua_dropdown, ua_de_dropdown)

# Remove Russian from dropdown if it exists
ru_dropdown_item = '''<li><a href="../ru/" style="display:block; padding:5px 10px;">
                                <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                    <rect width="16" height="4" fill="#fff"/>
                                    <rect y="4" width="16" height="4" fill="#0039A6"/>
                                    <rect y="8" width="16" height="4" fill="#D52B1E"/>
                                </svg>
                                RU
                            </a></li>'''

content = content.replace(ru_dropdown_item, '')

# Fix remaining German text that wasn't translated due to HTML protection
content = content.replace('Werbestart in der EU', 'Запуск рекламы в ЕС')
content = content.replace('in 48 Stunden', 'за 48 часов')
content = content.replace('Full Stack', 'Полный стек')
content = content.replace('Marketing Services', 'Маркетинговые услуги')
content = content.replace('Marketing Услуги', 'Маркетинговые услуги')  # Fix partial translation
content = content.replace('Erste Leads in 7 Tagen', 'Первые лиды за 7 дней')
content = content.replace('Erste Лиды in 7 Tagen', 'Первые лиды за 7 дней')  # Fix partial
content = content.replace('Technischer Manager in Ihrer Sprache', 'Технический менеджер на вашем языке')
content = content.replace('Wöchentliche Reports', 'Еженедельные отчеты')
content = content.replace('Еженедельные отчеты.', 'Еженедельные отчеты.')  # Ensure period is kept

# Fix contact form placeholders
content = content.replace('placeholder="Ihr Name"', 'placeholder="Ваше имя"')
content = content.replace('placeholder="ihre.email@beispiel.de"', 'placeholder="ваш.email@пример.ru"')
content = content.replace('placeholder="+49 123 456 7890"', 'placeholder="+7 123 456 7890"')
content = content.replace('placeholder="Beschreiben Sie Ihr Projekt..."', 'placeholder="Опишите ваш проект..."')

# Write back
with open('ru/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Russian translation completed!")
print("Note: Calculator IDs will be fixed with sed post-processing")
