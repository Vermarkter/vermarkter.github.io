# -*- coding: utf-8 -*-
"""
Google Ads page translation script
Translates de/google-ads.html to all language versions
"""

import re
import os

def protect_html(content):
    """Protect HTML tags from translation"""
    html_tags = {}
    tag_counter = [0]

    def protect_tag(match):
        placeholder = f"___HTML_TAG_{tag_counter[0]}___"
        html_tags[placeholder] = match.group(0)
        tag_counter[0] += 1
        return placeholder

    content = re.sub(r'<[^>]+>', protect_tag, content)
    return content, html_tags

def restore_html(content, html_tags):
    """Restore protected HTML tags"""
    for placeholder, tag in html_tags.items():
        content = content.replace(placeholder, tag)
    return content

def translate_to_ukrainian(content, html_tags):
    """Translate Google Ads page to Ukrainian"""

    # Change language attribute
    content = content.replace('lang="de"', 'lang="uk"')

    translations = {
        # Meta tags
        'Google Ads Agentur für kleine Unternehmen in Europa. Search Ads, Shopping Ads, Performance Max. Launch in 48 Stunden. Transparente Ergebnisse.': 'Google Ads агентство для малого бізнесу в Європі. Search Ads, Shopping Ads, Performance Max. Запуск за 48 годин. Прозорі результати.',
        'Google Ads Agentur, Google Ads Deutschland, Search Ads, Shopping Ads, Performance Max, PPC Marketing': 'Google Ads агентство, Google Ads Україна, Search Ads, Shopping Ads, Performance Max, PPC маркетинг',
        'Google Ads Agentur — Vermarkter': 'Google Ads агентство — Vermarkter',
        'Google Ads für kleine Unternehmen in Europa. Search, Shopping, Performance Max. Launch in 48 Stunden.': 'Google Ads для малого бізнесу в Європі. Search, Shopping, Performance Max. Запуск за 48 годин.',
        'Google Ads für kleine Unternehmen in Europa': 'Google Ads для малого бізнесу в Європі',

        # Navigation
        'Leistungen': 'Послуги',
        'Kampagnentypen': 'Типи кампаній',
        'Prozess': 'Процес',
        'Ergebnisse': 'Результати',
        'Kontakt': 'Контакти',

        # Hero section
        '🔍 Google Ads Agentur': '🔍 Google Ads агентство',
        'Qualifizierte Leads aus der': 'Кваліфіковані ліди з',
        'Google Suche': 'пошуку Google',
        'Search Ads, Shopping Ads, Performance Max.': 'Search Ads, Shopping Ads, Performance Max.',
        'Launch in 48 Stunden. Erste Leads in 7 Tagen. Manager in Ihrer Sprache.': 'Запуск за 48 годин. Перші ліди за 7 днів. Менеджер вашою мовою.',
        '🚀 Kostenlose Beratung': '🚀 Безкоштовна консультація',
        '💰 ROI berechnen': '💰 Розрахувати ROI',
        'durchschn. ROAS': 'середній ROAS',
        'bis Launch': 'до запуску',
        'erfolgreiche Projekte': 'успішних проектів',

        # Campaign types section
        'Google Ads': 'Google Ads',
        'Kampagnentypen': 'Типи кампаній',
        'Wir wählen den optimalen Kampagnentyp für Ihr Business': 'Ми обираємо оптимальний тип кампанії для вашого бізнесу',

        # Search Ads
        'Search Ads': 'Search Ads',
        'Textanzeigen in der Google Suche. Nutzer mit hoher Kaufabsicht, die aktiv nach Ihren Produkten/Dienstleistungen suchen.': 'Текстові оголошення в пошуку Google. Користувачі з високою купівельною готовністю, які активно шукають ваші продукти/послуги.',
        'Hohe Kaufabsicht': 'Висока купівельна готовність',
        'Pay-per-Click Modell': 'Модель pay-per-click',
        'Schnelle Ergebnisse': 'Швидкі результати',

        # Shopping Ads
        'Shopping Ads': 'Shopping Ads',
        'Produktanzeigen mit Bild, Preis und Name. Ideal für E-Commerce und Online-Shops mit physischen Produkten.': 'Товарні оголошення з фото, ціною та назвою. Ідеально для e-commerce та інтернет-магазинів з фізичними товарами.',
        'Visuelle Produktanzeigen': 'Візуальні товарні оголошення',
        'Google Merchant Center': 'Google Merchant Center',
        'Hohe Conversion-Rate': 'Висока конверсія',

        # Performance Max
        'Performance Max': 'Performance Max',
        'KI-gesteuerte Kampagnen über alle Google-Netzwerke. Automatische Optimierung für maximale Performance.': 'AI-кампанії по всіх мережах Google. Автоматична оптимізація для максимальної ефективності.',
        'KI-Optimierung': 'AI-оптимізація',
        'Alle Google-Netzwerke': 'Всі мережі Google',
        'Automatische Skalierung': 'Автоматичне масштабування',

        # Display Ads
        'Display Ads': 'Display Ads',
        'Banner-Werbung im Google Display-Netzwerk. Reichweite über 2 Millionen Websites. Ideal für Branding und Remarketing.': 'Банерна реклама в контекстно-медійній мережі Google. Охоплення понад 2 млн сайтів. Ідеально для брендингу та ремаркетингу.',
        'Riesige Reichweite': 'Величезне охоплення',
        'Visuelle Anzeigen': 'Візуальні оголошення',
        'Remarketing-Kampagnen': 'Ремаркетинг кампанії',

        # Process section
        'Wie wir': 'Як ми',
        'arbeiten': 'працюємо',
        'Von der Strategie bis zur Skalierung — Schritt für Schritt': 'Від стратегії до масштабування — крок за кроком',

        'Analyse': 'Аналіз',
        'Wir analysieren Ihr Business, Zielgruppe und Wettbewerb. Keyword-Recherche und Marktanalyse.': 'Аналізуємо ваш бізнес, цільову аудиторію та конкурентів. Дослідження ключових слів та аналіз ринку.',

        'Setup': 'Налаштування',
        'Kampagnen-Struktur, Anzeigentexte, Landing Pages. Conversion-Tracking und Analytics-Integration.': 'Структура кампаній, тексти оголошень, посадкові сторінки. Відстеження конверсій та інтеграція з Analytics.',

        'Launch': 'Запуск',
        'Kampagnen-Start in 48 Stunden. Erste Optimierungen nach 3 Tagen. Erste Leads in 7 Tagen.': 'Запуск кампаній за 48 годин. Перші оптимізації через 3 дні. Перші ліди за 7 днів.',

        'Optimierung': 'Оптимізація',
        'Tägliche Überwachung, wöchentliche Optimierung. A/B-Tests, Gebotsanpassungen, negative Keywords.': 'Щоденний моніторинг, щотижнева оптимізація. A/B-тести, коригування ставок, мінус-слова.',

        # Results section
        '📊 Unsere': '📊 Наші',
        'Ergebnisse': 'результати',
        'Echte Zahlen von unseren Kunden': 'Реальні цифри наших клієнтів',

        'E-Commerce': 'E-Commerce',
        'Online-Shop für Haushaltswaren': 'Інтернет-магазин товарів для дому',
        'Shopping Ads + Performance Max für einen deutschen E-Commerce Shop.': 'Shopping Ads + Performance Max для німецького інтернет-магазину.',
        'Umsatz/Monat': 'дохід/місяць',
        '"Nach 2 Monaten haben wir unsere Verkäufe verdoppelt. Das Team ist top!"': '"За 2 місяці ми подвоїли продажі. Команда топова!"',

        'B2B Services': 'B2B послуги',
        'IT-Dienstleistungen Berlin': 'IT-послуги Берлін',
        'Search Ads für Managed IT Services in Deutschland.': 'Search Ads для керованих IT-послуг у Німеччині.',
        'Leads/Monat': 'лідів/місяць',
        '"Qualität der Leads ist hervorragend. ROAS 420%. Sehr zufrieden!"': '"Якість лідів чудова. ROAS 420%. Дуже задоволені!"',

        'Local Business': 'Локальний бізнес',
        'Zahnarztpraxis München': 'Стоматологія Мюнхен',
        'Local Search Ads für eine private Zahnarztpraxis.': 'Локальні Search Ads для приватної стоматології.',
        'Termine/Monat': 'записів/місяць',
        '"Kalender voll gebucht dank Google Ads. Endlich verlässliche Ergebnisse!"': '"Календар заповнений завдяки Google Ads. Нарешті надійні результати!"',

        # FAQ section
        'Häufig gestellte': 'Часті',
        'Fragen': 'питання',

        '💰 Was kostet Google Ads Management?': '💰 Скільки коштує управління Google Ads?',
        'Unsere Gebühr beträgt 15-20% vom Werbebudget, mindestens €490/Monat. Für Budgets ab €2.500/Monat empfehlen wir unser BOOST-Paket (€990/Monat) mit Google + Meta Ads Kombo.': 'Наша комісія становить 15-20% від рекламного бюджету, мінімум €490/міс. Для бюджетів від €2.500/міс рекомендуємо пакет BOOST (€990/міс) з комбо Google + Meta Ads.',

        '⏱️ Wie schnell sehe ich Ergebnisse?': '⏱️ Як швидко я побачу результати?',
        'Launch in 48 Stunden, erste Optimierungen nach 3 Tagen, erste Leads in 7 Tagen. Stabile Performance nach 4-6 Wochen.': 'Запуск за 48 годин, перші оптимізації через 3 дні, перші ліди за 7 днів. Стабільна ефективність через 4-6 тижнів.',

        '🎯 Für welche Branchen ist Google Ads geeignet?': '🎯 Для яких галузей підходить Google Ads?',
        'Google Ads funktioniert für fast alle Branchen: E-Commerce, B2B-Dienstleistungen, lokale Geschäfte, SaaS, Bildung, Gesundheit und mehr. Wir passen die Strategie an Ihre Branche an.': 'Google Ads працює для майже всіх галузей: e-commerce, B2B-послуги, локальний бізнес, SaaS, освіта, здоров\'я та інше. Ми адаптуємо стратегію під вашу галузь.',

        '📊 Welche Reports bekomme ich?': '📊 Які звіти я отримаю?',
        'Wöchentliche Performance-Reports mit allen wichtigen Metriken: Klicks, Conversions, CPA, ROAS. Plus monatliche Strategie-Calls mit Ihrem Account Manager.': 'Щотижневі звіти про ефективність з усіма важливими метриками: кліки, конверсії, CPA, ROAS. Плюс щомісячні стратегічні дзвінки з вашим менеджером.',

        '🔒 Wie lange ist die Vertragsbindung?': '🔒 Яка мінімальна тривалість контракту?',
        'Mindestvertrag 3 Monate (Setup + Optimierungsphase). Danach monatlich kündbar. Keine versteckten Gebühren.': 'Мінімальний контракт 3 місяці (налаштування + фаза оптимізації). Потім можна розірвати щомісяця. Без прихованих комісій.',

        '🌍 In welchen Ländern schaltet ihr Ads?': '🌍 В яких країнах ви запускаєте рекламу?',
        'Wir arbeiten mit Kunden in ganz Europa: Deutschland, Österreich, Schweiz, Polen, Tschechien, Ukraine und mehr. Support in Deutsch, Englisch, Polnisch, Russisch, Ukrainisch und Türkisch.': 'Працюємо з клієнтами по всій Європі: Німеччина, Австрія, Швейцарія, Польща, Чехія, Україна та інші. Підтримка німецькою, англійською, польською, російською, українською та турецькою.',

        # Contact section
        'Bereit für mehr': 'Готові до більшої',
        'Leads?': 'кількості лідів?',
        'Kostenlose Strategie-Beratung in 24 Stunden': 'Безкоштовна стратегічна консультація за 24 години',

        'Name *': 'Ім\'я *',
        'Ihr Name': 'Ваше ім\'я',
        'E-Mail *': 'E-Mail *',
        'ihre.email@beispiel.de': 'ваш.email@приклад.ua',
        'Telefon': 'Телефон',
        '+49 123 456 7890': '+380 44 123 4567',
        'Monatliches Werbebudget': 'Місячний рекламний бюджет',
        'Bitte wählen': 'Будь ласка, оберіть',
        'Unter €1.000': 'До €1.000',
        'Über €10.000': 'Понад €10.000',
        'Nachricht *': 'Повідомлення *',
        'Beschreiben Sie Ihr Projekt...': 'Опишіть ваш проект...',
        '🚀 Kostenlose Beratung anfordern': '🚀 Замовити безкоштовну консультацію',
        'Antwort innerhalb von 24 Stunden garantiert': 'Відповідь протягом 24 годин гарантована',

        '✓ Nachricht erfolgreich gesendet!': '✓ Повідомлення успішно надіслано!',
        'Wir melden uns innerhalb von 24 Stunden bei Ihnen.': 'Ми зв\'яжемося з вами протягом 24 годин.',
        '✗ Fehler beim Senden': '✗ Помилка надсилання',
        'Bitte versuchen Sie es später erneut oder kontaktieren Sie uns direkt per E-Mail.': 'Будь ласка, спробуйте пізніше або зв\'яжіться з нами напряму електронною поштою.',

        # Footer
        'Google Ads Agentur für kleine Unternehmen in Europa. Transparente Ergebnisse, professioneller Support.': 'Google Ads агентство для малого бізнесу в Європі. Прозорі результати, професійна підтримка.',
        'Unternehmen': 'Компанія',
        'Bewertungen': 'Відгуки',
        'Datenschutz': 'Конфіденційність',
        'ROI Rechner': 'ROI калькулятор',
        '© 2025 Vermarkter. Alle Rechte vorbehalten.': '© 2025 Vermarkter. Всі права захищені.',

        # Chatbot
        'Vermarkter Assistent': 'Vermarkter асистент',
        'Wir antworten in Sekunden': 'Відповідаємо за секунди',
        'Hallo! 👋 Ich bin Ihr Vermarkter Assistent. Wie kann ich Ihnen bei Google Ads helfen?': 'Привіт! 👋 Я ваш Vermarkter асистент. Як я можу допомогти вам з Google Ads?',
        'Schreiben Sie Ihre Frage...': 'Напишіть ваше питання...',
        'Senden': 'Надіслати',
    }

    # Apply translations
    for de, ua in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(de, ua)

    # Fix language switcher paths
    content = content.replace('href="../ua/google-ads.html"', 'href="google-ads.html"')

    return content

# Read German version
print("Reading German version...")
with open('de/google-ads.html', 'r', encoding='utf-8') as f:
    de_content = f.read()

# Generate Ukrainian version
print("Generating Ukrainian version...")
ua_content, html_tags = protect_html(de_content)
ua_content = translate_to_ukrainian(ua_content, html_tags)
ua_content = restore_html(ua_content, html_tags)

# Ensure ua directory exists
os.makedirs('ua', exist_ok=True)

# Write Ukrainian version
with open('ua/google-ads.html', 'w', encoding='utf-8') as f:
    f.write(ua_content)

print("Ukrainian version created: ua/google-ads.html")
print("\nTranslation completed!")
print("Note: English, Polish, Russian, and Turkish versions will need similar translation scripts.")
