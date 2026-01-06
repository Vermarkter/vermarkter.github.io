# -*- coding: utf-8 -*-
"""
Complete Polish translation from German CRM page
"""

# Read German version
with open('de/crm-integration.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Translation dictionary with EXACT matches
translations = {
    'lang="de"': 'lang="pl"',
    '/de/crm-integration': '/pl/crm-integration',
    'og-image-crm-de.jpg': 'og-image-crm-pl.jpg',
    'CRM-Integration — Vermarkter': 'Integracja CRM — Vermarkter',

    # Meta descriptions
    'CRM-Integration für Marketing & Sales. HubSpot, Pipedrive, Zoho. Lead-Tracking, Offline Conversions, Telegram-Benachrichtigungen. Keine verlorenen Leads mehr.': 'Integracja CRM dla marketingu i sprzedaży. HubSpot, Pipedrive, Zoho. Tracking leadów, offline conversions, powiadomienia Telegram. Koniec z utraconymi leadami.',
    'Verbinden Sie Ihre Marketing-Kampagnen mit dem Vertrieb. Lead-Tracking, Automatisierung, echtes ROAS.': 'Połącz swoje kampanie marketingowe ze sprzedażą. Tracking leadów, automatyzacja, prawdziwy ROAS.',
    'Verbinden Sie Marketing und Sales': 'Połącz marketing i sprzedaż',

    # Navigation - Change German flag to Polish
    '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#000"/>
                                <rect y="4" width="16" height="4" fill="#D00"/>
                                <rect y="8" width="16" height="4" fill="#FFCE00"/>
                            </svg>
                            DE ▼''': '''<svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="6" fill="#fff"/>
                                <rect y="6" width="16" height="6" fill="#D4213D"/>
                            </svg>
                            PL ▼''',

    # Navigation links
    '<a href="index.html#services">Leistungen</a>': '<a href="index.html#services">Usługi</a>',
    '<a href="#probleme">Probleme</a>': '<a href="#problemy">Problemy</a>',
    '<a href="#loesung">Lösung</a>': '<a href="#rozwiazanie">Rozwiązanie</a>',
    '<a href="#preise">Preise</a>': '<a href="#cennik">Cennik</a>',
    '<a href="#contact">Kontakt</a>': '<a href="#kontakt">Kontakt</a>',

    # Hero section
    '🔗 CRM-Integration': '🔗 Integracja CRM',
    'Marketing <span class="text-gradient">+ Vertrieb</span><br>\n                    in einem System': 'Marketing <span class="text-gradient">+ Sprzedaż</span><br>\n                    w jednym systemie',
    '<strong style="color: var(--text-primary);">Keine verlorenen Leads mehr.</strong> Verbinden Sie Google Ads, Meta Ads und TikTok mit HubSpot, Pipedrive oder Zoho CRM.<br>\n                    Automatische Benachrichtigungen, Sales-Tracking, echtes ROAS.': '<strong style="color: var(--text-primary);">Koniec z utraconymi leadami.</strong> Połącz Google Ads, Meta Ads i TikTok z HubSpot, Pipedrive lub Zoho CRM.<br>\n                    Automatyczne powiadomienia, tracking sprzedaży, prawdziwy ROAS.',
    'Setup ab €499': 'Konfiguracja od €499',
    'Demo buchen': 'Umów demo',
    'Unterstützte CRM-Systeme:': 'Obsługiwane systemy CRM:',

    # SVG labels
    '<text x="70" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Website</text>': '<text x="70" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Strona</text>',
    '<text x="410" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Manager</text>': '<text x="410" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Menedżer</text>',
    '<text x="580" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Verkauf</text>': '<text x="580" y="105" text-anchor="middle" fill="var(--text-secondary)" font-size="12">Sprzedaż</text>',

    # Pain points section
    'id="probleme"': 'id="problemy"',
    '⚠️ <span class="text-gradient">Kennen Sie das?</span>': '⚠️ <span class="text-gradient">Znasz to?</span>',
    'Die häufigsten Probleme ohne CRM-Integration': 'Najczęstsze problemy bez integracji CRM',

    'Leads in Excel-Tabellen': 'Leady w arkuszach Excel',
    'Ihre Leads landen in unübersichtlichen Tabellen. Manager müssen manuell sortieren, priorisieren und nachfassen. <strong style="color: #EF4444;">Zeitverlust + verpasste Chancen.</strong>': 'Twoje leady trafiają do nieczytelnych tabel. Menedżerowie muszą ręcznie sortować, priorytetyzować i śledzić. <strong style="color: #EF4444;">Strata czasu + utracone szanse.</strong>',

    'Manager reagieren zu spät': 'Menedżerowie reagują za późno',
    'Lead kommt rein → Manager sieht ihn erst Stunden später → Lead kauft bei der Konkurrenz. <strong style="color: #EF4444;">Ohne sofortige Benachrichtigung verlieren Sie 50% der Leads.</strong>': 'Lead przychodzi → Menedżer widzi go dopiero po godzinach → Lead kupuje u konkurencji. <strong style="color: #EF4444;">Bez natychmiastowych powiadomień tracisz 50% leadów.</strong>',

    'Welche Werbung funktioniert?': 'Która reklama działa?',
    'Google Ads zeigt Klicks, aber keine Verkäufe. Sie wissen nicht, welche Kampagnen echte Kunden bringen. <strong style="color: #EF4444;">Ohne Offline Conversions verbrennen Sie Budget.</strong>': 'Google Ads pokazuje kliknięcia, ale nie sprzedaż. Nie wiesz, które kampanie przynoszą prawdziwych klientów. <strong style="color: #EF4444;">Bez offline conversions marnujesz budżet.</strong>',

    # Solution section
    'id="loesung"': 'id="rozwiazanie"',
    '✅ Unsere <span class="text-gradient">Lösung</span>': '✅ Nasze <span class="text-gradient">Rozwiązanie</span>',
    'Was wir für Sie einrichten': 'Co dla Ciebie skonfigurujemy',

    'Automatisierung': 'Automatyzacja',
    'Lead kommt von der Website → landet sofort im CRM → Manager bekommt Telegram-Nachricht → Anruf innerhalb 5 Minuten.': 'Lead ze strony → trafia natychmiast do CRM → Menedżer dostaje wiadomość na Telegram → Telefon w ciągu 5 minut.',
    'Formulare → CRM (Zapier/Make)': 'Formularze → CRM (Zapier/Make)',
    'Telegram-Benachrichtigungen': 'Powiadomienia Telegram',
    'Auto-Tagging nach Quelle': 'Auto-tagowanie według źródła',

    'End-to-End Analytics': 'Analityka End-to-End',
    'Wir senden Verkaufsdaten zurück an Google Ads und Meta. Die Algorithmen lernen, welche Klicks echte Kunden werden. <strong>Besseres ROAS automatisch.</strong>': 'Wysyłamy dane sprzedażowe z powrotem do Google Ads i Meta. Algorytmy uczą się, które kliknięcia stają się prawdziwymi klientami. <strong>Lepszy ROAS automatycznie.</strong>',
    'Offline Conversions (Google)': 'Offline Conversions (Google)',
    'CAPI für Meta Ads': 'CAPI dla Meta Ads',
    'Echtes ROAS pro Kampagne': 'Prawdziwy ROAS na kampanię',

    'Sales-Pipelines': 'Pipeline sprzedażowy',
    'Strukturierte Verkaufsprozesse: Neuer Lead → Kontaktiert → Angebot → Verhandlung → Gewonnen. Kein Lead geht verloren.': 'Uporządkowane procesy sprzedaży: Nowy lead → Kontakt → Oferta → Negocjacje → Wygrana. Żaden lead się nie zgubi.',
    'Custom Funnel-Stufen': 'Niestandardowe etapy lejka',
    'Automatische Follow-ups': 'Automatyczne follow-upy',
    'Lead-Scoring': 'Scoring leadów',

    # Pricing section
    'id="preise"': 'id="cennik"',
    'Preise <span class="text-gradient">CRM-Integration</span>': 'Cennik <span class="text-gradient">Integracji CRM</span>',
    'Einmalige Setup-Gebühr. Keine monatlichen Kosten für unsere Arbeit.': 'Jednorazowa opłata za konfigurację. Brak miesięcznych kosztów za naszą pracę.',

    'BASIC SETUP': 'BASIC SETUP',
    'Für Starter': 'Dla startujących',
    'CRM-Einrichtung (HubSpot/Pipedrive/Zoho)': 'Konfiguracja CRM (HubSpot/Pipedrive/Zoho)',
    'Website-Formulare → CRM': 'Formularze ze strony → CRM',
    'Basis-Funnel (3 Stufen)': 'Podstawowy lejek (3 etapy)',
    '1 Stunde Schulung': '1 godzina szkolenia',
    'Jetzt starten': 'Rozpocznij teraz',

    '🔥 EMPFOHLEN': '🔥 POLECANE',
    'ADVANCED': 'ADVANCED',
    'Für wachsende Unternehmen': 'Dla rozwijających się firm',
    '<strong>Alles aus BASIC +</strong>': '<strong>Wszystko z BASIC +</strong>',
    'Offline Conversions (Google Ads)': 'Offline Conversions (Google Ads)',
    'Meta CAPI Integration': 'Integracja Meta CAPI',
    'Zapier/Make Automatisierungen (5 Flows)': 'Automatyzacje Zapier/Make.com (5 przepływów)',
    'Custom Sales-Pipeline': 'Niestandardowy pipeline sprzedażowy',
    'E-Mail-Sequenzen (Follow-ups)': 'Sekwencje emailowe (Follow-upy)',
    '<strong>2 Stunden Schulung + 30 Tage Support</strong>': '<strong>2 godziny szkolenia + 30 dni wsparcia</strong>',

    'CUSTOM': 'INDYWIDUALNY',
    'Für Unternehmen': 'Dla firm',
    'Preis auf Anfrage': 'Cena na zapytanie',
    '<strong>Alles aus ADVANCED +</strong>': '<strong>Wszystko z ADVANCED +</strong>',
    'Custom API-Integrationen': 'Niestandardowe integracje API',
    'Unbegrenzte Automatisierungen': 'Nieograniczone automatyzacje',
    'Dedizierter Account Manager': 'Dedykowany account manager',
    'SLA + Priority Support': 'SLA + Wsparcie priorytetowe',
    '<strong>Individuelle Schulung & Onboarding</strong>': '<strong>Indywidualne szkolenie i wdrożenie</strong>',
    'Kontaktieren Sie uns': 'Skontaktuj się z nami',

    '* Preise zzgl. MwSt. CRM-Lizenzkosten (HubSpot, Pipedrive, etc.) sind NICHT enthalten. Wir helfen Ihnen bei der Auswahl des passenden Plans.': '* Ceny netto (bez VAT). Koszty licencji CRM (HubSpot, Pipedrive, itp.) NIE są wliczone. Pomożemy Ci wybrać odpowiedni plan.',

    # FAQ section
    'Häufig gestellte <span class="text-gradient">Fragen</span>': 'Najczęściej zadawane <span class="text-gradient">Pytania</span>',

    '💰 Welches CRM soll ich wählen?': '💰 Które CRM wybrać?',
    '<strong>HubSpot:</strong> Am besten für Marketing + Sales zusammen. Kostenlose Version verfügbar, später ab €50/Monat.<br><br>\n                        <strong>Pipedrive:</strong> Einfaches Sales-CRM. €14/Monat pro User. Perfekt für kleine Teams.<br><br>\n                        <strong>Zoho CRM:</strong> Günstigste Option. Ab €14/Monat. Gut für Startups.<br><br>\n                        <strong>GoHighLevel:</strong> All-in-One für Agenturen. Ab €97/Monat.<br><br>\n                        Wir beraten Sie kostenlos, welches System zu Ihrem Budget und Prozess passt.': '<strong>HubSpot:</strong> Najlepszy dla marketingu + sprzedaży razem. Wersja darmowa dostępna, płatna od €50/mies.<br><br>\n                        <strong>Pipedrive:</strong> Prosty CRM sprzedażowy. €14/mies na użytkownika. Idealny dla małych zespołów.<br><br>\n                        <strong>Zoho CRM:</strong> Najtańsza opcja. Od €14/mies. Dobry dla startupów.<br><br>\n                        <strong>GoHighLevel:</strong> All-in-one dla agencji. Od €97/mies.<br><br>\n                        Doradzamy bezpłatnie, który system pasuje do Twojego budżetu i procesów.',

    '⏱️ Wie lange dauert die Einrichtung?': '⏱️ Jak długo trwa konfiguracja?',
    '<strong>Basic Setup:</strong> 3-5 Werktage<br>\n                        <strong>Advanced Setup:</strong> 7-10 Werktage<br><br>\n                        Nach dem Kick-off-Call starten wir sofort. Sie bekommen wöchentliche Updates und können jederzeit Fragen stellen.': '<strong>Basic Setup:</strong> 3-5 dni roboczych<br>\n                        <strong>Advanced Setup:</strong> 7-10 dni roboczych<br><br>\n                        Po rozmowie kick-off startujemy od razu. Dostajesz cotygodniowe aktualizacje i możesz zadawać pytania w każdej chwili.',

    '🔧 Brauche ich technische Kenntnisse?': '🔧 Czy potrzebuję wiedzy technicznej?',
    '<strong>Nein.</strong> Wir richten alles für Sie ein. Sie bekommen eine Schulung, wie Sie das CRM nutzen, Leads bearbeiten und Reports ansehen. Nach dem Setup arbeitet alles automatisch.': '<strong>Nie.</strong> Wszystko skonfigurujemy dla Ciebie. Dostaniesz szkolenie, jak korzystać z CRM, obsługiwać leady i przeglądać raporty. Po konfiguracji wszystko działa automatycznie.',

    '📊 Was sind Offline Conversions?': '📊 Czym są Offline Conversions?',
    'Google Ads sieht normalerweise nur Klicks und Formular-Absendungen. Aber der echte Verkauf passiert offline (Anruf, Meeting, Rechnung). <strong>Offline Conversions</strong> senden diese Daten zurück an Google. Resultat: Google weiß, welche Klicks zu echten Kunden führen, und optimiert Ihre Kampagnen automatisch auf Umsatz statt nur Leads. <strong>ROAS steigt um durchschnittlich 30-50%.</strong>': 'Google Ads normalnie widzi tylko kliknięcia i wysłane formularze. Ale prawdziwa sprzedaż dzieje się offline (telefon, spotkanie, faktura). <strong>Offline Conversions</strong> wysyłają te dane z powrotem do Google. Rezultat: Google wie, które kliknięcia prowadzą do prawdziwych klientów i automatycznie optymalizuje Twoje kampanie pod sprzedaż zamiast tylko leadów. <strong>ROAS rośnie średnio o 30-50%.</strong>',

    '💬 Wie funktionieren Telegram-Benachrichtigungen?': '💬 Jak działają powiadomienia Telegram?',
    'Sobald ein Lead von Ihrer Website kommt, bekommt Ihr Sales-Manager eine Nachricht in Telegram (oder Slack/WhatsApp). Die Nachricht enthält: Name, E-Mail, Telefon, Quelle (Google Ads/Meta/etc.). Manager kann sofort reagieren. <strong>Durchschnittliche Reaktionszeit: unter 5 Minuten.</strong>': 'Gdy tylko lead przychodzi z Twojej strony, Twój menedżer sprzedaży dostaje wiadomość na Telegram (lub Slack/WhatsApp). Wiadomość zawiera: Imię, Email, Telefon, Źródło (Google Ads/Meta/itp.). Menedżer może zareagować natychmiast. <strong>Średni czas reakcji: poniżej 5 minut.</strong>',

    '🔄 Bietet ihr auch laufende Betreuung?': '🔄 Czy oferujecie bieżące wsparcie?',
    'Das Setup ist einmalig. Danach arbeitet alles automatisch. Falls Sie später weitere Automatisierungen, zusätzliche Integrationen oder Optimierungen brauchen, können Sie uns jederzeit beauftragen. Stundensatz: €99/Stunde.': 'Konfiguracja jest jednorazowa. Potem wszystko działa automatycznie. Jeśli później potrzebujesz dodatkowych automatyzacji, integracji lub optymalizacji, możesz nas zatrudnić w każdej chwili. Stawka godzinowa: €99/godz.',

    # Contact section
    'id="contact"': 'id="kontakt"',
    'Bereit, Ihr CRM <span class="text-gradient">zu verbinden?</span>': 'Gotowy połączyć swój <span class="text-gradient">CRM?</span>',
    'Kostenlose Beratung — wir helfen Ihnen, das richtige CRM zu wählen': 'Bezpłatna konsultacja — pomożemy Ci wybrać właściwy CRM',

    'Name *': 'Imię *',
    'Ihr Name': 'Twoje imię',
    'E-Mail *': 'Email *',
    'ihre.email@firma.de': 'twoj.email@firma.pl',
    'Telefon': 'Telefon',
    '+49 123 456 7890': '+48 123 456 789',
    'Website': 'Strona internetowa',
    'https://ihre-website.de': 'https://twoja-strona.pl',
    'Ihre Nachricht *': 'Twoja wiadomość *',
    'Welches CRM nutzen Sie aktuell? Wie viele Leads bekommen Sie pro Monat?': 'Którego CRM obecnie używasz? Ile leadów dostajesz miesięcznie?',
    'Kostenlose Beratung anfragen': 'Zamów bezpłatną konsultację',
    'Antwort innerhalb von 24 Stunden. Keine Verpflichtungen.': 'Odpowiedź w ciągu 24 godzin. Bez zobowiązań.',

    # Footer
    'Ihre Marketing-Agentur für DACH und Osteuropa.': 'Twoja agencja marketingowa dla rynków DACH i Europy Wschodniej.',
    'Leistungen': 'Usługi',
    'CRM-Integration': 'Integracja CRM',
    '&copy; 2025 Vermarkter. Alle Rechte vorbehalten.': '&copy; 2025 Vermarkter. Wszelkie prawa zastrzeżone.',
    'Datenschutz': 'Polityka prywatności',
    'Impressum': 'Informacje prawne',

    # Chatbot
    'Hallo! 👋 Haben Sie Fragen zur CRM-Integration?': 'Cześć! 👋 Masz pytania dotyczące integracji CRM?',
    'Schreiben Sie Ihre Frage...': 'Napisz swoje pytanie...',
}

# Apply translations
for de, pl in translations.items():
    content = content.replace(de, pl)

# Write Polish version
with open('pl/crm-integration.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Polish CRM page created successfully!")
print("Translated phrases:", len(translations))
