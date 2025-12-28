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
    'Warum verschwinden 80% des Budgets': 'Dlaczego 80% budżetu znika',
    'im Nichts': 'na nic',
    '% der Kampagnen scheitern': '% kampanii kończy się niepowodzeniem',
    'fehlende Transparenz': 'brak przejrzystości',
    'Budget verbrannt ohne ROI': 'budżet spalony bez zwrotu',
    'Falsche Keywords': 'Błędne słowa kluczowe',
    'Sie zahlen für Klicks von Nutzern, die nie kaufen werden. 70% des Traffics sind "informationelle" Suchanfragen ohne Kaufabsicht.': 'Płacisz za kliknięcia użytkowników, którzy nigdy nie kupią. 70% ruchu to zapytania informacyjne bez intencji zakupowej.',
    'Breiter Match-Type – Sie zahlen für alles Mögliche': 'Szeroki typ dopasowania – płacisz za wszystko',
    'Keine negativen Keywords – Budget läuft aus': 'Brak negatywnych słów kluczowych – budżet się wypala',
    'Werbung für Konkurrenten statt Zielgruppe': 'Reklama dla konkurentów zamiast grupy docelowej',
    'Fehlendes End-to-End Tracking': 'Brak śledzenia end-to-end',
    'Ohne korrektes Tracking wissen Sie nicht, welche Anzeige/Keywords Verkäufe bringen. Sie steuern blind.': 'Bez poprawnego śledzenia nie wiesz, które reklamy/słowa przynoszą sprzedaż. Sterujesz na ślepo.',
    'Google Analytics falsch konfiguriert': 'Google Analytics źle skonfigurowany',
    'Conversions werden nicht an Ads übermittelt': 'Konwersje nie są przekazywane do Ads',
    'Keine Attribution – Customer Journey unklar': 'Brak atrybucji – ścieżka klienta niejasna',
    'Schwache Creatives': 'Słabe kreacje',
    'Niedrige CTR = hoher CPC. Schlechte Texte und Banner senken den Quality Score und Sie zahlen für jeden Klick mehr.': 'Niski CTR = wysoki CPC. Słabe teksty i banery obniżają Quality Score i płacisz więcej za każde kliknięcie.',
    'Generische Texte ohne USP – niemand klickt': 'Ogólne teksty bez USP – nikt nie klika',
    'Banner in Paint erstellt – sieht aus wie Spam': 'Banery zrobione w Paint – wyglądają jak spam',
    'Keine A/B-Tests – Sie bleiben beim ersten Entwurf': 'Brak testów A/B – zostajesz z pierwszym projektem',

    # Method Section
    'Unser Ansatz': 'Nasza metoda',
    'Unsere Methodik: 3-Stufen-System': 'Nasza metodyka: System 3-stopniowy',
    'So arbeiten wir': 'Tak pracujemy',
    'Audit & Strategie': 'Audyt i strategia',
    'Kampagnen-Setup': 'Konfiguracja kampanii',
    'Optimierung & Skalierung': 'Optymalizacja i skalowanie',
    'SCHRITT 1': 'KROK 1',
    'SCHRITT 2': 'KROK 2',
    'SCHRITT 3': 'KROK 3',
    'Tiefgehende Analyse': 'Dogłębna analiza',
    'Wir finden, wo Ihr Budget verschwindet. Analyse von Wettbewerbern, Semantik und technischen Fehlern.': 'Znajdujemy, gdzie znika Twój budżet. Analiza konkurencji, semantyki i błędów technicznych.',
    'Nischenanalyse': 'Analiza niszy',
    'Suche nach "Gold"-Keywords': 'Szukanie "złotych" słów kluczowych',
    'Technisches Audit': 'Audyt techniczny',
    'Wettbewerber-Mapping': 'Mapowanie konkurencji',
    'Kampagnen Launch': 'Uruchomienie kampanii',
    'Wir erstellen Kampagnen mit +8% CTR und Conversion-Tracking ab Tag 1. Keine Experimente.': 'Tworzymy kampanie z +8% CTR i śledzeniem konwersji od 1 dnia. Żadnych eksperymentów.',
    'Strukturierung nach Intent': 'Strukturyzacja według intencji',
    'Conversion-Setup (GA4 + Ads)': 'Konfiguracja konwersji (GA4 + Ads)',
    'Creatives (Texte + Banner)': 'Kreacje (teksty + banery)',
    'Erster Traffic in 48h': 'Pierwszy ruch w 48h',
    'Wöchentliche Optimierung': 'Cotygodniowa optymalizacja',
    'Wir analysieren jeden €, pausieren teure Keywords und skalieren profitable Kampagnen.': 'Analizujemy każde €, zatrzymujemy drogie słowa kluczowe i skalujemy opłacalne kampanie.',
    'Wöchentliche Reports': 'Cotygodniowe raporty',
    'Search Terms Analyse': 'Analiza fraz wyszukiwania',
    'Bid-Anpassungen': 'Dostosowania stawek',
    'Creative-Tests (A/B)': 'Testy kreacji (A/B)',
    'Bereit zu wachsen?': 'Gotowy do wzrostu?',
    'Lassen Sie uns Ihr Business skalieren': 'Pozwól nam skalować Twój biznes',
    'Wir bauen Kampagnen nach SKAG-Prinzip. Klares Conversion-Tracking.': 'Budujemy kampanie według zasady SKAG. Przejrzyste śledzenie konwersji.',
    'Transparente Cennik ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Przejrzysty cennik bez ukrytych kosztów. Wybierz idealny pakiet dla swojej firmy.',
    'Berechnen Sie die Rentabilität Ihrer Werbekampagne': 'Oblicz rentowność swojej kampanii reklamowej',
    'Wählen Sie Ihre Branche:': 'Wybierz swoją branżę:',
    'Die drei häufigsten Gründe für gescheiterte Werbekampagnen': 'Trzy najczęstsze przyczyny nieudanych kampanii reklamowych',
    'Struktur und Launch': 'Struktura i uruchomienie',
    'Von der Strategie bis zur Umsetzung – alles aus einer Hand': 'Od strategii do realizacji – wszystko z jednego źródła',
    'Heißer Traffic aus der Suche. Performance Max für E-Commerce. Shopping Ads für Produkte. Launch w 48 godzin.': 'Gorący ruch z wyszukiwania. Performance Max dla e-commerce. Shopping Ads dla produktów. Uruchomienie w 48 godzin.',
    'Shopping Ads (für Online-Shops)': 'Shopping Ads (dla sklepów internetowych)',
    'Lead-Generierung und Verkäufe über Facebook und Instagram. Lookalike Audiences, Remarketing, Messenger Ads.': 'Generowanie leadów i sprzedaż przez Facebook i Instagram. Lookalike Audiences, Remarketing, Messenger Ads.',
    'Viraler Content und junge Zielgruppe. In-Feed Ads, Spark Ads, Shopping Ads. Günstiger Traffic für E-Commerce.': 'Wirusowa treść i młoda publiczność. In-Feed Ads, Spark Ads, Shopping Ads. Tani ruch dla e-commerce.',
    'Organischer Traffic aus Google. Lokales SEO für die EU. Content-Marketing und Linkbuilding. Langfristige Ergebnisse.': 'Organiczny ruch z Google. Lokalne SEO dla UE. Content marketing i budowanie linków. Długoterminowe rezultaty.',
    'Telegram Bot für Leads (sofortige Benachrichtigungen)': 'Bot Telegram dla leadów (natychmiastowe powiadomienia)',
    'Cennik <span class="text-gradient">und Pakete</span>': 'Cennik <span class="text-gradient">i pakiety</span>',
    'Perfekt für den Einstieg': 'Idealny na start',
    'Erstellung von Anzeigen-Creatives': 'Tworzenie kreacji reklamowych',
    'Rechtliche Unterstützung für EU': 'Wsparcie prawne dla UE',
    'Dies ist ein echtes Mediaplanungs-Tool.': 'To prawdziwe narzędzie do planowania mediów.',
    'Dieselben Formeln, die große Agenturen verwenden. Transparent, ehrlich, ohne versteckte Kosten.': 'Te same formuły, których używają duże agencje. Przejrzyste, uczciwe, bez ukrytych kosztów.',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen: €1.000-1.500/Monat. Nutzen Sie unseren ROI-Kalkulator oben für eine genaue Prognose.': 'Zależy to od Twojej niszy i celów. Minimalny budżet na skuteczne kampanie: €1.000-1.500/mies. Skorzystaj z naszego kalkulatora ROI powyżej dla dokładnej prognozy.',
    'Kontaktieren Sie uns für ein technisches Audit oder eine Erstberatung': 'Skontaktuj się z nami w sprawie audytu technicznego lub wstępnej konsultacji',
    'Beschreiben Sie Ihr Projekt...': 'Opisz swój projekt...',
    'Vielen Dank! Wir melden uns in Kürze bei Ihnen.': 'Dziękujemy! Wkrótce się z Tobą skontaktujemy.',
    'Oder kontaktieren Sie uns direkt:': 'Lub skontaktuj się z nami bezpośrednio:',
    'Marketing-Agentur für kleine Unternehmen in der Europäischen Union.': 'Agencja marketingowa dla małych firm w Unii Europejskiej.',

    # Services Details
    'CRM Integration': 'Integracja CRM',
    'Alle Leads automatisch in Telegram/Google Sheets. Email/SMS Auto-Funnels. Volle Kontrolle über Ihren Sales Funnel.': 'Wszystkie leady automatycznie w Telegram/Google Sheets. Email/SMS Auto-Funnels. Pełna kontrola nad Twoim lejkiem sprzedażowym.',
    'Email Marketing (Mailchimp, SendGrid)': 'Email Marketing (Mailchimp, SendGrid)',
    'Zapier/Make.com Integrationen': 'Integracje Zapier/Make.com',
    'Web Analytics': 'Analityka webowa',
    'GA4, GTM, Hotjar, Microsoft Clarity. Vollständiges Verständnis des Nutzerverhaltens. Dashboards in Looker Studio.': 'GA4, GTM, Hotjar, Microsoft Clarity. Pełne zrozumienie zachowań użytkowników. Dashboardy w Looker Studio.',
    'GA4 Setup (Enhanced Ecommerce)': 'Konfiguracja GA4 (Enhanced Ecommerce)',
    'Heatmaps & Session Recordings (Hotjar)': 'Mapy ciepła i nagrania sesji (Hotjar)',
    'Custom Dashboards (Looker Studio)': 'Niestandardowe dashboardy (Looker Studio)',
    'Optimierung': 'Optymalizacja',
    'Tägliche Gebotsanpassungen. Budget-Skalierung nur bei positivem ROAS.': 'Codzienne dostosowania stawek. Skalowanie budżetu tylko przy dodatnim ROAS.',
    'A/B-Testing': 'Testy A/B',
    'Reporting': 'Raportowanie',
    'Analytics-Setup': 'Konfiguracja analityki',
    'Anzeigenerstellung': 'Tworzenie reklam',
    'Kampagnen-Launch': 'Uruchomienie kampanii',

    # Navigation menu
    'Leistungen': 'Usługi',
    'Cases': 'Projekty',
    'Über uns': 'O nas',
    'Portfolio': 'Portfolio',
    'Blog': 'Blog',

    # Pricing details
    'Starter': 'Starter',
    'Wachstum': 'Wzrost',
    'Business': 'Biznes',
    'Pro Monat': 'Miesięcznie',
    'Was ist enthalten': 'Co zawiera',
    'Was ist enthalten:': 'Co zawiera:',
    'Strategie-Call': 'Rozmowa strategiczna',
    'Keyword-Recherche': 'Badanie słów kluczowych',
    'Campaign Setup': 'Konfiguracja kampanii',
    'Wöchentliches Reporting': 'Cotygodniowe raportowanie',
    'Monatliche Optimierung': 'Miesięczna optymalizacja',
    'Tägliche Optimierung': 'Codzienna optymalizacja',
    'Dedicated Account Manager': 'Dedykowany opiekun konta',
    'Zugang zu': 'Dostęp do',
    'Jetzt starten': 'Rozpocznij teraz',
    'Kontakt aufnehmen': 'Skontaktuj się',

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
    'Erste Ergebnisse sehen Sie in der Regel innerhalb von 48-72 Stunden nach dem Launch. Optimale Performance erreichen Kampagnen nach 2-4 Wochen Optimierung.': 'Pierwsze wyniki zazwyczaj widać w ciągu 48-72 godzin po uruchomieniu. Optymalna wydajność kampanii osiągana jest po 2-4 tygodniach optymalizacji.',
    'Benötige ich eine eigene Website?': 'Czy potrzebuję własnej strony internetowej?',
    'Nicht unbedingt. Wir können für Sie eine konversionsstarke Landing Page erstellen oder Sie können unsere vorgefertigten Templates verwenden.': 'Niekoniecznie. Możemy stworzyć dla Ciebie landing page o wysokiej konwersji lub możesz użyć naszych gotowych szablonów.',
    'Gibt es eine Mindestvertragslaufzeit?': 'Czy jest minimalny okres umowy?',
    'Ja, die Mindestvertragslaufzeit beträgt 3 Monate. Dies gibt uns genügend Zeit, um Ihre Kampagnen zu optimieren und echte Ergebnisse zu liefern. Danach keine Bindung.': 'Tak, minimalny okres umowy to 3 miesiące. Daje nam to wystarczająco czasu na optymalizację kampanii i dostarczenie prawdziwych wyników. Potem brak zobowiązań.',
    'In welchen Ländern arbeiten Sie?': 'W jakich krajach pracujecie?',
    'Wir sind auf den EU-Markt spezialisiert: Deutschland, Polen, Tschechien, Österreich und andere EU-Länder. Wir kennen die lokalen Besonderheiten jedes Marktes.': 'Specjalizujemy się w rynku UE: Niemcy, Polska, Czechy, Austria i inne kraje UE. Znamy lokalne specyfiki każdego rynku.',
    'Welches Budget sollte ich für Werbung einplanen?': 'Jaki budżet powinienem zaplanować na reklamę?',
    'Das Mindestbudget für Google Ads liegt bei €500/Monat. Für Meta Ads empfehlen wir mindestens €300/Monat. Kleinere Budgets bringen keine statistisch relevanten Daten.': 'Minimalny budżet na Google Ads to €500/mies. Na Meta Ads zalecamy minimum €300/mies. Mniejsze budżety nie dają statystycznie istotnych danych.',

    # CTA Section
    'Bereit zu starten': 'Gotowy do startu',
    'Sprechen Sie mit einem Experten': 'Porozmawiaj z ekspertem',
    'Ihr Name': 'Twoje imię',
    'Name': 'Imię',
    'Ihre E-Mail': 'Twój email',
    'Email': 'Email',
    'Telefon (optional)': 'Telefon (opcjonalnie)',
    'Ihre Nachricht': 'Twoja wiadomość',
    'Nachricht': 'Wiadomość',
    'Nachricht senden': 'Wyślij wiadomość',
    'Anfrage senden': 'Wyślij zapytanie',

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
