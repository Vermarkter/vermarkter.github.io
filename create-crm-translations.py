#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick script to create CRM Integration page translations
Based on German template
"""

import re

# Read German template
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    de_content = f.read()

# Translation dictionaries
translations = {
    'pl': {
        # Meta & Title
        'lang="de"': 'lang="pl"',
        'CRM-Integration für Marketing & Sales': 'Integracja CRM dla Marketingu i Sprzedaży',
        'HubSpot, Pipedrive, Zoho': 'HubSpot, Pipedrive, Zoho',
        'Lead-Tracking, Offline Conversions, Telegram-Benachrichtigungen': 'Śledzenie leadów, Offline Conversions, Powiadomienia Telegram',
        'Keine verlorenen Leads mehr': 'Koniec ze straconymi leadami',
        'Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb': 'Połącz swoje kampanie marketingowe ze sprzedażą',
        'Lead-Tracking, Automatisierung, echtes ROAS': 'Śledzenie leadów, Automatyzacja, prawdziwy ROAS',
        'og-image-crm-de.jpg': 'og-image-crm-pl.jpg',
        '/de/crm-integration': '/pl/crm-integration',
        'Verbinden Sie Marketing und Sales': 'Połącz Marketing i Sprzedaż',

        # Navigation
        'Leistungen': 'Usługi',
        'Probleme': 'Problemy',
        'Lösung': 'Rozwiązanie',
        'Preise': 'Ceny',
        'Kontakt': 'Kontakt',

        # Hero
        'Marketing <span class="text-gradient">+ Vertrieb</span><br>\n                    in einem System': 'Marketing <span class="text-gradient">+ Sprzedaż</span><br>\n                    w jednym systemie',
        'Keine verlorenen Leads mehr.': 'Koniec ze straconymi leadami.',
        'Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.<br>\n                    Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': 'Połącz Google Ads, Meta Ads i TikTok z HubSpot, Pipedrive lub Zoho CRM.<br>\n                    Automatyczne powiadomienia, tracking sprzedaży, prawdziwy ROAS.',
        'Setup ab €499': 'Setup od €499',
        'Demo buchen': 'Zamów demo',
        'Website': 'Strona',
        'CRM': 'CRM',
        'Manager': 'Manager',
        'Verkauf': 'Sprzedaż',
        'Unterstützte CRM-Systeme:': 'Wspierane systemy CRM:',

        # Pain Points
        '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Znasz to?</span>',
        'Die häufigsten Probleme ohne CRM-Integration': 'Najczęstsze problemy bez integracji CRM',
        'Leads in Excel-Tabellen': 'Leady w tabelach Excel',
        'Ihre Leads landen in unübersichtlichen Tabellen': 'Twoje leady lądują w nieuporządkowanych tabelach',
        'Manager müssen manuell sortieren, priorisieren und nachfassen': 'Managerowie muszą ręcznie sortować, ustalać priorytety i kontaktować się',
        'Zeitverlust + verpasste Chancen': 'Strata czasu + utracone szanse',
        'Manager reagieren zu spät': 'Managerowie reagują za późno',
        'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz': 'Lead wpływa → Manager widzi go dopiero po godzinach → Lead kupuje u konkurencji',
        'Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads': 'Bez natychmiastowych powiadomień tracisz 50% leadów',
        'Welche Werbung funktioniert?': 'Która reklama działa?',
        'Google Ads zeigt Klicks, aber keine Verkäufe': 'Google Ads pokazuje kliknięcia, ale nie sprzedaż',
        'Sie wissen nicht, welche Kampagnen echte Kunden bringen': 'Nie wiesz, które kampanie przynoszą prawdziwych klientów',
        'Ohne Offline Conversions verbrennen Sie Budget': 'Bez Offline Conversions marnujesz budżet',

        # Solution
        '✅ Unsere <span class="text-gradient">Lösung</span>': '✅ Nasze <span class="text-gradient">Rozwiązanie</span>',
        'Was wir für Sie einrichten': 'Co dla Ciebie skonfigurujemy',
        'Automatisierung': 'Automatyzacja',
        'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten': 'Lead ze strony → trafia od razu do CRM → Manager dostaje wiadomość na Telegram → Kontakt w ciągu 5 minut',
        'Formulare → CRM (Zapier/Make)': 'Formularze → CRM (Zapier/Make)',
        'Telegram-Benachrichtigungen': 'Powiadomienia Telegram',
        'Auto-Tagging nach Quelle': 'Auto-tagowanie według źródła',
        'End-to-End Analytics': 'Analityka End-to-End',
        'Wir senden Verkaufsdaten zurück an Google Ads und Meta': 'Wysyłamy dane o sprzedaży z powrotem do Google Ads i Meta',
        'Die Algorithmen lernen, welche Klicks echte Kunden werden': 'Algorytmy uczą się, które kliknięcia stają się prawdziwymi klientami',
        'Besseres ROAS automatisch': 'Lepszy ROAS automatycznie',
        'Offline Conversions (Google)': 'Offline Conversions (Google)',
        'CAPI für Meta Ads': 'CAPI dla Meta Ads',
        'Echtes ROAS pro Kampagne': 'Prawdziwy ROAS per kampania',
        'Sales-Pipelines': 'Ścieżki sprzedaży',
        'Strukturierte Verkaufsprozesse': 'Ustrukturyzowane procesy sprzedaży',
        'Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen': 'Nowy lead → Kontakt → Oferta → Negocjacje → Wygrana',
        'Kein Lead geht verloren': 'Żaden lead nie zostaje utracony',
        'Custom Funnel-Stufen': 'Niestandardowe etapy lejka',
        'Automatische Follow-ups': 'Automatyczne follow-upy',
        'Lead-Scoring': 'Lead-Scoring',

        # Pricing
        'Preise <span class="text-gradient">CRM-Integration</span>': 'Ceny <span class="text-gradient">Integracji CRM</span>',
        'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Jednorazowa opłata za setup. Brak miesięcznych kosztów za naszą pracę.',
        'BASIC SETUP': 'BASIC SETUP',
        'Für Starter': 'Dla początkujących',
        'einmalig': 'jednorazowo',
        'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'Konfiguracja CRM (HubSpot/Pipedrive/Zoho)',
        'Website-Formulare → CRM': 'Formularze ze strony → CRM',
        'Basis-Funnel (3 Stufen)': 'Podstawowy lejek (3 etapy)',
        '1 Stunde Schulung': '1 godzina szkolenia',
        'Jetzt starten': 'Zacznij teraz',
        '🔥 EMPFOHLEN': '🔥 POLECANE',
        'ADVANCED': 'ADVANCED',
        'Für wachsende Unternehmen': 'Dla rozwijających się firm',
        'Alles aus BASIC +': 'Wszystko z BASIC +',
        'Zapier/Make Automatisierungen (5 Flows)': 'Automatyzacje Zapier/Make (5 przepływów)',
        'Custom Sales-Pipeline': 'Niestandardowa ścieżka sprzedaży',
        'E-Mail-Sequenzen (Follow-ups)': 'Sekwencje e-mail (Follow-upy)',
        '2 Stunden Schulung + 30 Tage Support': '2 godziny szkolenia + 30 dni wsparcia',
        '* Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten': '* Ceny netto. Koszty licencji CRM (HubSpot, Pipedrive, etc.) NIE są wliczone',
        'Wir helfen Ihnen bei der Auswahl des passenden Plans': 'Pomożemy Ci wybrać odpowiedni plan',

        # FAQ
        'Häufig gestellte <span class="text-gradient">Fragen</span>': 'Często zadawane <span class="text-gradient">pytania</span>',
        '💰 Welches CRM soll ich wählen?': '💰 Który CRM wybrać?',
        'Am besten für Marketing + Sales zusammen': 'Najlepszy dla Marketing + Sprzedaż razem',
        'Kostenlose Version verfügbar, später ab €50/Monat': 'Dostępna darmowa wersja, później od €50/mies',
        'Einfaches Sales-CRM': 'Prosty CRM sprzedażowy',
        'Perfekt für kleine Teams': 'Idealny dla małych zespołów',
        'Günstigste Option': 'Najtańsza opcja',
        'Gut für Startups': 'Dobry dla startupów',
        'All-in-One für Agenturen': 'All-in-One dla agencji',
        'Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt': 'Doradzimy Ci bezpłatnie, który system pasuje do Twojego budżetu i procesu',
        '⏱️ Wie lange dauert die Einrichtung?': '⏱️ Jak długo trwa konfiguracja?',
        'Nach dem Kick-off-Call starten wir sofort': 'Po kick-off call zaczynamy natychmiast',
        'Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen': 'Dostajesz tygodniowe aktualizacje i możesz zadawać pytania w każdej chwili',
        '🔧 Brauche ich technische Kenntnisse?': '🔧 Czy potrzebuję wiedzy technicznej?',
        'Wir richten alles für Sie ein': 'Skonfigurujemy wszystko dla Ciebie',
        'Sie bekommen eine Schulung, wie Sie das CRM nutzen': 'Otrzymasz szkolenie, jak korzystać z CRM',
        'Nach dem Setup arbeitet alles automatisch': 'Po konfiguracji wszystko działa automatycznie',

        # Contact
        'Bereit, Ihr CRM <span class="text-gradient">zu verbinden?</span>': 'Gotowy, aby <span class="text-gradient">połączyć swój CRM?</span>',
        'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Bezpłatna konsultacja — pomożemy Ci wybrać odpowiedni CRM',
        'Name *': 'Imię *',
        'Ihr Name': 'Twoje imię',
        'E-Mail *': 'E-mail *',
        'ihre.email@firma.de': 'twoj.email@firma.pl',
        'Telefon': 'Telefon',
        '+49 123 456 7890': '+48 123 456 789',
        'https://ihre-website.de': 'https://twoja-strona.pl',
        'Ihre Nachricht *': 'Twoja wiadomość *',
        'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Jakiego CRM obecnie używasz? Ile leadów dostajesz miesięcznie?',
        'Kostenlose Beratung anfragen': 'Zapytaj o bezpłatną konsultację',
        'Antwort innerhalb von 24 Stunden. Keine Verpflichtungen.': 'Odpowiedź w ciągu 24 godzin. Żadnych zobowiązań.',

        # Footer
        'Ihre Marketing-Agentur für DACH und Osteuropa': 'Twoja Agencja Marketingowa dla DACH i Europy Wschodniej',
        'Alle Rechte vorbehalten': 'Wszystkie prawa zastrzeżone',
        'Datenschutz': 'Prywatność',
        'Impressum': 'Nota prawna',
        'Schreiben Sie Ihre Frage...': 'Napisz swoje pytanie...',
        'Haben Sie Fragen zur CRM-Integration?': 'Masz pytania o integrację CRM?',
    },
    'ru': {
        # Meta & Title
        'lang="de"': 'lang="ru"',
        'CRM-Integration für Marketing & Sales': 'Интеграция CRM для Маркетинга и Продаж',
        'Lead-Tracking, Offline Conversions, Telegram-Benachrichtigungen': 'Отслеживание лидов, Offline Conversions, Telegram-уведомления',
        'Keine verlorenen Leads mehr': 'Больше никаких потерянных лидов',
        'og-image-crm-de.jpg': 'og-image-crm-ru.jpg',
        '/de/crm-integration': '/ru/crm-integration',

        # Navigation (same as PL but in Russian)
        'Leistungen': 'Услуги',
        'Probleme': 'Проблемы',
        'Lösung': 'Решение',
        'Preise': 'Цены',
        'Kontakt': 'Контакт',

        # Hero
        'Marketing <span class="text-gradient">+ Vertrieb</span><br>\n                    in einem System': 'Маркетинг <span class="text-gradient">+ Продажи</span><br>\n                    в одной системе',
        'Keine verlorenen Leads mehr.': 'Больше никаких потерянных лидов.',
        'Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.<br>\n                    Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': 'Подключите Google Ads, Meta Ads и TikTok к HubSpot, Pipedrive или Zoho CRM.<br>\n                    Автоматические уведомления, отслеживание продаж, реальный ROAS.',
        'Setup ab €499': 'Настройка от €499',
        'Demo buchen': 'Заказать демо',

        'Website': 'Сайт',
        'CRM': 'CRM',
        'Manager': 'Менеджер',
        'Verkauf': 'Продажа',
        'Unterstützte CRM-Systeme:': 'Поддерживаемые CRM-системы:',

        # Pain Points
        '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Знакомо?</span>',
        'Die häufigsten Probleme ohne CRM-Integration': 'Самые частые проблемы без интеграции CRM',
        'Leads in Excel-Tabellen': 'Лиды в Excel-таблицах',
        'Ihre Leads landen in unübersichtlichen Tabellen': 'Ваши лиды попадают в неразборчивые таблицы',
        'Manager müssen manuell sortieren, priorisieren und nachfassen': 'Менеджеры должны вручную сортировать, расставлять приоритеты и связываться',
        'Zeitverlust + verpasste Chancen': 'Потеря времени + упущенные возможности',
        'Manager reagieren zu spät': 'Менеджеры реагируют слишком поздно',
        'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz': 'Лид поступает → Менеджер видит его через часы → Лид покупает у конкурентов',
        'Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads': 'Без мгновенных уведомлений вы теряете 50% лидов',
        'Welche Werbung funktioniert?': 'Какая реклама работает?',
        'Google Ads zeigt Klicks, aber keine Verkäufe': 'Google Ads показывает клики, но не продажи',
        'Sie wissen nicht, welche Kampagnen echte Kunden bringen': 'Вы не знаете, какие кампании приносят реальных клиентов',
        'Ohne Offline Conversions verbrennen Sie Budget': 'Без Offline Conversions вы сжигаете бюджет',

        # Solution
        '✅ Unsere <span class="text-gradient">Lösung</span>': '✅ Наше <span class="text-gradient">Решение</span>',
        'Was wir für Sie einrichten': 'Что мы настроим для вас',
        'Automatisierung': 'Автоматизация',
        'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten': 'Лид с сайта → сразу попадает в CRM → Менеджер получает сообщение в Telegram → Звонок в течение 5 минут',
        'Formulare → CRM (Zapier/Make)': 'Формы → CRM (Zapier/Make)',
        'Telegram-Benachrichtigungen': 'Telegram-уведомления',
        'Auto-Tagging nach Quelle': 'Авто-тегирование по источнику',
        'End-to-End Analytics': 'End-to-End Аналитика',
        'Wir senden Verkaufsdaten zurück an Google Ads und Meta': 'Мы отправляем данные о продажах обратно в Google Ads и Meta',
        'Die Algorithmen lernen, welche Klicks echte Kunden werden': 'Алгоритмы учатся, какие клики становятся реальными клиентами',
        'Besseres ROAS automatisch': 'Лучший ROAS автоматически',
        'Offline Conversions (Google)': 'Offline Conversions (Google)',
        'CAPI für Meta Ads': 'CAPI для Meta Ads',
        'Echtes ROAS pro Kampagne': 'Реальный ROAS по кампании',
        'Sales-Pipelines': 'Воронки продаж',
        'Strukturierte Verkaufsprozesse': 'Структурированные процессы продаж',
        'Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen': 'Новый лид → Контакт → Предложение → Переговоры → Выиграно',
        'Kein Lead geht verloren': 'Ни один лид не теряется',
        'Custom Funnel-Stufen': 'Пользовательские этапы воронки',
        'Automatische Follow-ups': 'Автоматические follow-up',
        'Lead-Scoring': 'Lead-Scoring',

        # Pricing
        'Preise <span class="text-gradient">CRM-Integration</span>': 'Цены <span class="text-gradient">Интеграция CRM</span>',
        'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Единоразовая плата за настройку. Никаких ежемесячных затрат за нашу работу.',
        'BASIC SETUP': 'BASIC SETUP',
        'Für Starter': 'Для начинающих',
        'einmalig': 'единоразово',
        'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'Настройка CRM (HubSpot/Pipedrive/Zoho)',
        'Website-Formulare → CRM': 'Формы с сайта → CRM',
        'Basis-Funnel (3 Stufen)': 'Базовая воронка (3 этапа)',
        '1 Stunde Schulung': '1 час обучения',
        'Jetzt starten': 'Начать сейчас',
        '🔥 EMPFOHLEN': '🔥 РЕКОМЕНДУЕМ',
        'ADVANCED': 'ADVANCED',
        'Für wachsende Unternehmen': 'Для растущих компаний',
        'Alles aus BASIC +': 'Всё из BASIC +',
        'Zapier/Make Automatisierungen (5 Flows)': 'Автоматизации Zapier/Make (5 потоков)',
        'Custom Sales-Pipeline': 'Пользовательская воронка продаж',
        'E-Mail-Sequenzen (Follow-ups)': 'E-mail последовательности (Follow-up)',
        '2 Stunden Schulung + 30 Tage Support': '2 часа обучения + 30 дней поддержки',
        '* Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten': '* Цены без НДС. Затраты на лицензии CRM (HubSpot, Pipedrive, etc.) НЕ включены',
        'Wir helfen Ihnen bei der Auswahl des passenden Plans': 'Мы поможем вам выбрать подходящий план',

        # FAQ
        'Häufig gestellte <span class="text-gradient">Fragen</span>': 'Часто задаваемые <span class="text-gradient">вопросы</span>',
        '💰 Welches CRM soll ich wählen?': '💰 Какой CRM выбрать?',
        'Am besten für Marketing + Sales zusammen': 'Лучший для Marketing + Продажи вместе',
        'Kostenlose Version verfügbar, später ab €50/Monat': 'Доступна бесплатная версия, потом от €50/мес',
        'Einfaches Sales-CRM': 'Простая CRM для продаж',
        'Perfekt für kleine Teams': 'Идеально для небольших команд',
        'Günstigste Option': 'Самый дешевый вариант',
        'Gut für Startups': 'Хорошо для стартапов',
        'All-in-One für Agenturen': 'All-in-One для агентств',
        'Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt': 'Мы бесплатно проконсультируем, какая система подходит вашему бюджету и процессу',
        '⏱️ Wie lange dauert die Einrichtung?': '⏱️ Сколько времени занимает настройка?',
        'Nach dem Kick-off-Call starten wir sofort': 'После kick-off звонка мы начинаем сразу',
        'Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen': 'Вы получаете еженедельные обновления и можете задавать вопросы в любое время',
        '🔧 Brauche ich technische Kenntnisse?': '🔧 Нужны ли технические знания?',
        'Wir richten alles für Sie ein': 'Мы настроим всё для вас',
        'Sie bekommen eine Schulung, wie Sie das CRM nutzen': 'Вы получите обучение, как пользоваться CRM',
        'Nach dem Setup arbeitet alles automatisch': 'После настройки всё работает автоматически',

        # Contact
        'Bereit, Ihr CRM <span class="text-gradient">zu verbinden?</span>': 'Готовы <span class="text-gradient">подключить свой CRM?</span>',
        'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Бесплатная консультация — мы поможем выбрать правильный CRM',
        'Name *': 'Имя *',
        'Ihr Name': 'Ваше имя',
        'E-Mail *': 'E-mail *',
        'ihre.email@firma.de': 'vash.email@gmail.com',
        'Telefon': 'Телефон',
        '+49 123 456 7890': '+XX 123 456 789',
        'https://ihre-website.de': 'https://vash-site.com',
        'Ihre Nachricht *': 'Ваше сообщение *',
        'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Какую CRM вы используете сейчас? Сколько лидов получаете в месяц?',
        'Kostenlose Beratung anfragen': 'Запросить бесплатную консультацию',
        'Antwort innerhalb von 24 Stunden. Keine Verpflichtungen.': 'Ответ в течение 24 часов. Никаких обязательств.',

        # Footer
        'Ihre Marketing-Agentur für DACH und Osteuropa': 'Ваше Маркетинговое Агентство для DACH и Восточной Европы',
        'Alle Rechte vorbehalten': 'Все права защищены',
        'Datenschutz': 'Конфиденциальность',
        'Impressum': 'Выходные данные',
        'Schreiben Sie Ihre Frage...': 'Напишите ваш вопрос...',
        'Haben Sie Fragen zur CRM-Integration?': 'Есть вопросы по интеграции CRM?',
    }
}

# Create Polish version
pl_content = de_content
for de_text, pl_text in translations['pl'].items():
    pl_content = pl_content.replace(de_text, pl_text)

with open('pl/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(pl_content)

print("Polish CRM page created")

# Create Russian version
ru_content = de_content
for de_text, ru_text in translations['ru'].items():
    ru_content = ru_content.replace(de_text, ru_text)

with open('ru/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(ru_content)

print("Russian CRM page created")
print("Done")
