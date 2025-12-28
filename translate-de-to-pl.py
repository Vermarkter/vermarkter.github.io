# -*- coding: utf-8 -*-
import re

# Read DE version (which is currently in pl/index.html)
with open('pl/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Dictionary of German → Polish translations
translations = {
    # Navigation
    'Services': 'Usługi',
    'Preise': 'Cennik',
    'Rechner': 'Kalkulator',
    'Bewertungen': 'Opinie',
    'Kontakt': 'Kontakt',

    # Hero Section
    'Für kleine Unternehmen in der EU': 'Dla małych firm w UE',
    'Werbestart in der EU': 'Start reklamy w UE',
    'in 48 Stunden': 'w 48 godzin',
    'Google Ads & Meta Ads für Ihr Business in Europa': 'Google Ads i Meta Ads dla Twojego biznesu w Europie',
    'Erste Leads in 7 Tagen': 'Pierwsze leady w 7 dni',
    'Technischer Manager in Ihrer Sprache': 'Menedżer techniczny w Twoim języku',
    'Wöchentliche Reports': 'Cotygodniowe raporty',
    'Gewinn berechnen': 'Oblicz zysk',
    'Unsere Cases': 'Nasze projekty',

    # Stats
    '% durchschn. ROAS': '% średni ROAS',
    '% Kunden kehren zurück': '% klientów wraca',
    'Tage bis Launch': 'dni do startu',

    # Problem Section
    'Warum verschwenden 80% des Budgets': 'Dlaczego 80% budżetu marnuje się',
    'im Nichts': 'na nic',
    '% der Kampagnen scheitern': '% kampanii kończy się niepowodzeniem',
    'fehlende Transparenz': 'brak przejrzystości',
    'Budget verbrannt ohne ROI': 'budżet spalony bez zwrotu',

    # Method Section
    'Unser Ansatz': 'Nasza metoda',
    'So arbeiten wir': 'Tak pracujemy',
    'Audit & Strategie': 'Audyt i strategia',
    'Kampagnen-Setup': 'Konfiguracja kampanii',
    'Optimierung & Skalierung': 'Optymalizacja i skalowanie',

    # Calculator Section
    'ROI-Rechner': 'Kalkulator ROI',
    'Berechnen Sie Ihren potenziellen Gewinn': 'Oblicz swój potencjalny zysk',
    'Monatliches Budget': 'Miesięczny budżet',
    'Kosten pro Klick': 'Koszt za kliknięcie',
    'Cost per Click': 'Koszt za kliknięcie',
    'Conversion Rate': 'Wskaźnik konwersji',
    'Durchschnittlicher Bestellwert': 'Średnia wartość zamówienia',
    'Gewinnmarge': 'Marża zysku',
    'Klicks pro Monat': 'Kliknięć miesięcznie',
    'Leads pro Monat': 'Leadów miesięcznie',
    'Kosten pro Lead': 'Koszt za lead',
    'ROAS': 'ROAS',
    'Profit': 'Zysk',
    'Gewinn': 'Zysk',
    'Strategie für diese Zahlen erhalten': 'Otrzymaj strategię dla tych liczb',

    # Testimonials
    'Kundenbewertungen': 'Opinie klientów',
    'Über 100 erfolgreiche Projekte für kleine Unternehmen in der EU': 'Ponad 100 udanych projektów dla małych firm w UE',

    # FAQ
    'Häufig gestellte Fragen': 'Często zadawane pytania',
    'Alles, was Sie über unsere Dienstleistungen wissen müssen': 'Wszystko, co musisz wiedzieć o naszych usługach',
    'Wie schnell kann ich mit Ergebnissen rechnen': 'Jak szybko mogę spodziewać się wyników',

    # CTA Section
    'Bereit zu starten': 'Gotowy do startu',
    'Sprechen Sie mit einem Experten': 'Porozmawiaj z ekspertem',
    'Ihr Name': 'Twoje imię',
    'Ihre E-Mail': 'Twój email',
    'Ihre Nachricht': 'Twoja wiadomość',
    'Nachricht senden': 'Wyślij wiadomość',

    # Footer
    'Folgen Sie uns': 'Śledź nas',
    'Rechtliches': 'Informacje prawne',
    'Datenschutz': 'Polityka prywatności',
    'Impressum': 'Nota prawna',

    # Testimonials content
    'Vermarkter hat uns geholfen, unseren Online-Shop in Deutschland in 6 Tagen zu starten. Die ersten Verkäufe kamen schon nach einer Woche! ROAS 380%.': 'Vermarkter pomógł nam uruchomić sklep internetowy w Niemczech w 6 dni. Pierwsze sprzedaże nadeszły już po tygodniu! ROAS 380%.',
    'Professionelles Team! Google Ads hat sich im ersten Monat amortisiert. ROAS 420%. Sehr zufrieden, endlich kompetente Marketer gefunden.': 'Profesjonalny zespół! Google Ads zwrócił się w pierwszym miesiącu. ROAS 420%. Bardzo zadowolony, wreszcie znalazłem kompetentnych marketerów.',
    'Die Meta Ads-Kampagnen brachten uns +180% Lead-Wachstum in 2 Monaten. Empfehle allen, die Transparenz und Ergebnisse suchen!': 'Kampanie Meta Ads przyniosły nam +180% wzrost leadów w 2 miesiące. Polecam wszystkim szukającym przejrzystości i wyników!',
    'Die SEO-Strategie funktioniert! In 4 Monaten sind wir in den Top 3 für alle Keywords. Organischer Traffic ist um 300% gestiegen.': 'Strategia SEO działa! W 4 miesiące jesteśmy w TOP 3 dla wszystkich słów kluczowych. Organiczny ruch wzrósł o 300%.',
    'Google-Werbung in 2 Tagen gestartet. Nach einer Woche bekamen wir die ersten 15 Anfragen. CRM-Integration mit Telegram - einfach Bombe!': 'Reklama Google uruchomiona w 2 dni. Po tygodniu otrzymaliśmy pierwsze 15 zapytań. Integracja CRM z Telegramem - po prostu bomba!',
    'Das Vermarkter-Team kennt sich aus. Transparente Reports, klare KPIs, immer auf Deutsch erreichbar. Arbeiten seit 8 Monaten zusammen.': 'Zespół Vermarkter zna się na rzeczy. Przejrzyste raporty, jasne KPI, zawsze dostępni po polsku. Współpracujemy od 8 miesięcy.',
    'München': 'Monachium',
    'Berlin': 'Berlin',
    'Warschau': 'Warszawa',
    'Düsseldorf': 'Düsseldorf',
    'Bau': 'Budowa',
    'Kosmetik': 'Kosmetyka',
}

# Apply translations
for de, pl in translations.items():
    content = content.replace(de, pl)

# Write result
with open('pl/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Translation completed!")
