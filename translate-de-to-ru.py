# -*- coding: utf-8 -*-
import re

with open('ru/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

translations = {
    # HTML lang attribute
    'lang="de"': 'lang="ru"',

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

    # Navigation
    'Transparente Preise ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Прозрачные цены без скрытых расходов. Выберите идеальный пакет для вашей компании.',
    'Preise & Pakete': 'Цены и пакеты',
    'Leistungen': 'Услуги',
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
    'So funktioniert\'s': 'Как это работает',
    'Unsere <span class="highlight">3-Schritte-Methode</span>': 'Наш <span class="highlight">3-шаговый метод</span>',

    'Analyse & Strategie': 'Анализ и стратегия',
    'Wir analysieren dein Business, deine Zielgruppe und deine Ziele. Daraus entwickeln wir eine maßgeschneiderte Strategie – ohne Standardlösungen.': 'Мы анализируем ваш бизнес, вашу целевую аудиторию и ваши цели. На основе этого мы разрабатываем индивидуальную стратегию – без стандартных решений.',

    'Setup & Launch': 'Настройка и запуск',
    'Wir erstellen professionelle Kampagnen auf Google Ads, Meta (Facebook/Instagram) oder TikTok – perfekt abgestimmt auf deine Ziele.': 'Мы создаем профессиональные кампании в Google Ads, Meta (Facebook/Instagram) или TikTok – идеально настроенные под ваши цели.',

    'Optimierung & Reporting': 'Оптимизация и отчетность',
    'Du bekommst wöchentlich klare Zahlen: Kosten, Leads, Umsatz, ROI. Wir optimieren laufend – damit deine Werbung immer besser wird.': 'Вы получаете еженедельно четкие цифры: затраты, лиды, доход, ROI. Мы постоянно оптимизируем – чтобы ваша реклама становилась лучше.',

    # Services section
    'Unsere Leistungen': 'Наши услуги',

    'Google Ads Management': 'Управление Google Ads',
    'Such-, Display- und Shopping-Kampagnen, die Kunden bringen – nicht nur Klicks.': 'Поисковые, медийные и торговые кампании, которые приносят клиентов – а не только клики.',

    'Meta Ads (Facebook & Instagram)': 'Meta Ads (Facebook и Instagram)',
    'Zielgruppengerechte Anzeigen, die Aufmerksamkeit erzeugen und konvertieren.': 'Объявления для целевой аудитории, которые привлекают внимание и конвертируют.',

    'TikTok Ads': 'TikTok Ads',
    'Kreative Video-Ads für junge Zielgruppen – authentisch, viral, wirksam.': 'Креативная видеореклама для молодой аудитории – аутентичная, вирусная, эффективная.',

    'ROI-Tracking & Reporting': 'ROI-Отслеживание и отчетность',
    'Volle Transparenz: Du siehst genau, was deine Werbung bringt – in Euro und Cent.': 'Полная прозрачность: вы видите точно, что приносит ваша реклама – в евро и центах.',

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
    'Berechne, wie viel <span class="highlight">mehr Umsatz</span> du mit Performance-Marketing erzielen kannst': 'Рассчитайте, насколько <span class="highlight">больше дохода</span> вы можете получить с помощью эффективного маркетинга',

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
    '"Vermarkter hat uns geholfen, unseren Online-Shop in Deutschland in 6 Tagen zu starten. Die ersten Verkäufe kamen schon nach einer Woche! ROAS 380%."': '"Vermarkter помог нам запустить интернет-магазин в Германии за 6 дней. Первые продажи пришли уже через неделю! ROAS 380%."',
    'Wir sind auf den EU-Markt spezialisiert: Deutschland, Polen, Tschechien, Österreich und andere EU-Länder. Wir kennen die lokalen Besonderheiten jedes Marktes.': 'Мы специализируемся на рынке ЕС: Германия, Польша, Чехия, Австрия и другие страны ЕС. Мы знаем локальные особенности каждого рынка.',

    # FAQ section
    'Häufige Fragen': 'Частые вопросы',

    # FAQ 1
    'Für wen ist Performance-Marketing geeignet?': 'Для кого подходит эффективный маркетинг?',
    'Performance-Marketing eignet sich für kleine und mittlere Unternehmen, die online wachsen wollen – egal ob E-Commerce, Dienstleistungen, B2B oder lokale Geschäfte.': 'Эффективный маркетинг подходит для малого и среднего бизнеса, который хочет расти онлайн – независимо от того, это электронная коммерция, услуги, B2B или местный бизнес.',

    # FAQ 2
    'Wie schnell sehe ich Ergebnisse?': 'Как быстро я увижу результаты?',
    'Die ersten Daten kommen schon in den ersten Tagen. Messbare Ergebnisse (Leads, Verkäufe) siehst du in der Regel nach 2-4 Wochen – abhängig von deiner Branche und deinem Budget.': 'Первые данные появляются уже в первые дни. Измеримые результаты (лиды, продажи) вы увидите обычно через 2-4 недели – в зависимости от вашей отрасли и бюджета.',

    # FAQ 3
    'Brauche ich ein großes Werbebudget?': 'Нужен ли большой рекламный бюджет?',
    'Nein. Wir arbeiten auch mit kleinen Budgets ab 500 €/Monat. Wichtig ist, dass das Budget zur Branche und den Zielen passt.': 'Нет. Мы работаем и с небольшими бюджетами от 500 €/месяц. Важно, чтобы бюджет соответствовал отрасли и целям.',

    # FAQ 4
    'Was unterscheidet euch von anderen Agenturen?': 'Чем вы отличаетесь от других агентств?',
    'Volle Transparenz, klare Zahlen und keine langfristigen Verträge. Du zahlst nur, solange du zufrieden bist. Keine versteckten Kosten, keine leeren Versprechen.': 'Полная прозрачность, четкие цифры и никаких долгосрочных контрактов. Вы платите только пока довольны. Никаких скрытых расходов, никаких пустых обещаний.',

    # FAQ 5
    'Kann ich jederzeit kündigen?': 'Могу ли я отказаться в любое время?',
    'Ja. Unsere Verträge sind monatlich kündbar. Kein Risiko, keine Bindung.': 'Да. Наши контракты можно расторгнуть ежемесячно. Никакого риска, никаких обязательств.',

    # CTA section
    'Bereit für messbares Wachstum?': 'Готовы к измеримому росту?',
    'Lass uns in einem kostenlosen Erstgespräch herausfinden, wie viel Potenzial in deinem Business steckt.': 'Давайте на бесплатной первой консультации узнаем, какой потенциал есть в вашем бизнесе.',
    'Jetzt kostenlos beraten lassen': 'Получить бесплатную консультацию',
    'Keine Verpflichtungen • 100% transparent': 'Без обязательств • 100% прозрачно',

    # Contact form
    'Kontaktiere uns': 'Свяжитесь с нами',
    'Name': 'Имя',
    'Dein Name': 'Ваше имя',
    'Email': 'Email',
    'Deine Email-Adresse': 'Ваш email адрес',
    'Telefon (optional)': 'Телефон (необязательно)',
    'Deine Telefonnummer': 'Ваш номер телефона',
    'Nachricht': 'Сообщение',
    'Beschreibe dein Projekt...': 'Опишите ваш проект...',
    'Anfrage senden': 'Отправить запрос',

    # Footer
    'Marketing-Agentur für kleine Unternehmen in der Europäischen Union.': 'Маркетинговое агентство для малого бизнеса в Европейском Союзе.',
    'Über uns': 'О нас',
    'Performance-Marketing-Agentur für kleine und mittlere Unternehmen in Europa. Spezialisiert auf Google Ads, Meta Ads und TikTok Ads.': 'Агентство эффективного маркетинга для малого и среднего бизнеса в Европе. Специализируемся на Google Ads, Meta Ads и TikTok Ads.',

    'Schnelllinks': 'Быстрые ссылки',
    'Services': 'Услуги',
    'Pricing': 'Цены',
    'Methodik': 'Методика',

    'Legal': 'Юридическая информация',
    'Impressum': 'Выходные данные',
    'Datenschutz': 'Конфиденциальность',
    'AGB': 'Условия использования',

    '© 2025 Performance Marketing Agentur. Alle Rechte vorbehalten.': '© 2025 Агентство эффективного маркетинга. Все права защищены.',
}

# Apply translations
for de, ru in translations.items():
    content = content.replace(de, ru)

# Write back
with open('ru/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Russian translation completed!")
print("Note: Calculator IDs will be fixed with sed post-processing")
