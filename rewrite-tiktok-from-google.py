#!/usr/bin/env python3
"""
REWRITE de/tiktok-ads.html from de/google-ads.html template
Replace ALL Google content with TikTok content
"""

import re
from pathlib import Path

def rewrite_tiktok_page():
    """Copy google-ads.html and replace all Google content with TikTok"""

    # Read Google Ads template
    with open('de/google-ads.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # ===== META TAGS =====
    content = content.replace(
        'Google Ads Agentur für kleine Unternehmen in Europa. Search Ads, Shopping Ads, Performance Max. Start in 48 Stunden. Transparente Ergebnisse.',
        'TikTok Ads Agentur für kleine Unternehmen in Europa. In-Feed Ads, Spark Ads, Shopping Ads. Start in 48 Stunden. Transparente Ergebnisse.'
    )
    content = content.replace(
        'Google Ads Agentur, Google Ads Deutschland, Search Ads, Shopping Ads, Performance Max, PPC Marketing',
        'TikTok Ads Agentur, TikTok Marketing Deutschland, In-Feed Ads, Spark Ads, Video Ads, Gen Z Marketing'
    )
    content = content.replace('https://vermarkter.eu/de/google-ads', 'https://vermarkter.eu/de/tiktok-ads')
    content = content.replace('Google Ads Agentur — Vermarkter', 'TikTok Ads Agentur — Vermarkter')
    content = content.replace('og-image-google-ads-de.jpg', 'og-image-tiktok-ads-de.jpg')
    content = content.replace(
        'Google Ads für kleine Unternehmen in Europa. Search, Shopping, Performance Max. Start in 48 Stunden.',
        'TikTok Ads für kleine Unternehmen in Europa. Virale Kampagnen, Gen Z Marketing. Start in 48 Stunden.'
    )
    content = content.replace('Google Ads für kleine Unternehmen in Europa', 'TikTok Ads für kleine Unternehmen in Europa')

    # ===== TITLE =====
    content = content.replace('<title>Google Ads Agentur — Vermarkter</title>', '<title>TikTok Ads Agentur — Vermarkter</title>')

    # ===== NAVIGATION =====
    # Language switcher links
    content = content.replace('../de/google-ads.html', '../de/tiktok-ads.html')
    content = content.replace('../en/google-ads.html', '../en/tiktok-ads.html')
    content = content.replace('../pl/google-ads.html', '../pl/tiktok-ads.html')
    content = content.replace('../ru/google-ads.html', '../ru/tiktok-ads.html')
    content = content.replace('../tr/google-ads.html', '../tr/tiktok-ads.html')
    content = content.replace('../ua/google-ads.html', '../ua/tiktok-ads.html')

    # ===== HERO SECTION =====
    content = content.replace(
        '<span style="color: #4285F4; font-weight: 600; font-size: 0.95rem;">🔍 Google Ads Agentur</span>',
        '<span style="color: #FF0050; font-weight: 600; font-size: 0.95rem;">📱 TikTok Ads Agentur</span>'
    )
    content = content.replace(
        'background: rgba(66, 133, 244, 0.1); border: 1px solid rgba(66, 133, 244, 0.3);',
        'background: rgba(255, 0, 80, 0.1); border: 1px solid rgba(255, 0, 80, 0.3);'
    )
    content = content.replace(
        'Qualifizierte Leads aus der <span class="text-gradient">Google Suche</span>',
        'TikTok Ads, die <span class="text-gradient">viral gehen</span>'
    )
    content = content.replace(
        'Search Ads, Shopping Ads, Performance Max.<br>',
        'Erreichen Sie die Gen Z und Millennials.<br>'
    )
    content = content.replace(
        '<strong style="color: var(--text-primary);">Start in 48 Stunden. Erste Leads in 7 Tagen. <span style="color: var(--brand);">Keine Provision</span> auf Werbeausgaben.</strong>',
        '<strong style="color: var(--text-primary);">Günstiger Traffic, hohe Engagement-Raten. <span style="color: var(--brand);">Start in 48 Stunden.</span></strong>'
    )

    # Hero stats
    content = content.replace(
        '<div class="stat-value text-gradient" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">420%</div>\n                        <div class="stat-label" style="color: var(--text-secondary); font-size: 0.95rem;">durchschn. ROAS</div>',
        '<div class="stat-value text-gradient" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">15%</div>\n                        <div class="stat-label" style="color: var(--text-secondary); font-size: 0.95rem;">Engagement Rate</div>'
    )
    content = content.replace(
        '<div class="stat-value text-gradient" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">48h</div>\n                        <div class="stat-label" style="color: var(--text-secondary); font-size: 0.95rem;">bis Start</div>',
        '<div class="stat-value text-gradient" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">3-5x</div>\n                        <div class="stat-label" style="color: var(--text-secondary); font-size: 0.95rem;">Günstigerer CPM</div>'
    )
    content = content.replace(
        '<div class="stat-value text-gradient" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">100+</div>\n                        <div class="stat-label" style="color: var(--text-secondary); font-size: 0.95rem;">erfolgreiche Projekte</div>',
        '<div class="stat-value text-gradient" style="font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem;">∞</div>\n                        <div class="stat-label" style="color: var(--text-secondary); font-size: 0.95rem;">Viraler Effekt</div>'
    )

    # ===== KAMPAGNENTYPEN SECTION =====
    content = content.replace(
        'Google Ads <span class="text-gradient">Kampagnentypen</span>',
        'TikTok Ads <span class="text-gradient">Kampagnentypen</span>'
    )
    content = content.replace(
        'Wir wählen den optimalen Kampagnentyp für Ihr Business',
        'Wir wählen den optimalen Kampagnentyp für Ihr Business'
    )

    # Campaign Type 1
    content = re.sub(
        r'(<h3 class="service-title"[^>]*>)[^<]+(Search Ads[^<]*)(</h3>)',
        r'\1In-Feed Anzeigen\3',
        content
    )
    content = re.sub(
        r'(service-title"[^>]*>Search Ads.*?</h3>\s*<p class="service-description"[^>]*>)[^<]+(</p>)',
        r'\1Native Video Ads im For You Feed. Nahtlos integriert zwischen organischen TikToks für maximale Reichweite.\2',
        content,
        flags=re.DOTALL
    )

    # Campaign Type 2
    content = re.sub(
        r'(<h3 class="service-title"[^>]*>)Shopping[^<]+(</h3>)',
        r'\1Spark Ads\2',
        content
    )
    content = re.sub(
        r'(service-title"[^>]*>Spark Ads.*?</h3>\s*<p class="service-description"[^>]*>)[^<]+(</p>)',
        r'\1Boosten Sie organische Posts als Ads. Nutzen Sie vorhandenes Engagement und authentische Interaktionen.\2',
        content,
        flags=re.DOTALL
    )

    # Campaign Type 3
    content = re.sub(
        r'(<h3 class="service-title"[^>]*>)Performance[^<]+(</h3>)',
        r'\1Video Shopping Ads\2',
        content
    )
    content = re.sub(
        r'(service-title"[^>]*>Video Shopping Ads.*?</h3>\s*<p class="service-description"[^>]*>)[^<]+(</p>)',
        r'\1Direktverkauf aus dem Feed. Produktkatalog-Integration für nahtloses Shopping-Erlebnis direkt in der App.\2',
        content,
        flags=re.DOTALL
    )

    # ===== PAIN POINTS =====
    # Replace section title
    content = re.sub(
        r'(Warum funktionieren Ihre.*?<span class="text-gradient">)Google Ads(</span>.*?nicht\?)',
        r'\1TikTok Ads\2',
        content
    )

    # Pain point 1
    content = re.sub(
        r'(<div class="pain-icon">❌</div>\s*<h3 class="pain-title">)[^<]+(</h3>\s*<p class="pain-description">)[^<]+(</p>)',
        r'\1Langweilige Ads\2Niemand schaut zu. Ihre Videos wirken wie klassische Werbung und werden übersprungen.\3',
        content,
        count=1
    )

    # Pain point 2
    content = re.sub(
        r'(<div class="pain-icon">❌</div>\s*<h3 class="pain-title">)[^<]+(</h3>\s*<p class="pain-description">)[^<]+(</p>)',
        r'\1Falsche Zielgruppe\2Streuverluste ohne Ende. Sie erreichen Menschen, die nie kaufen würden.\3',
        content,
        count=1
    )

    # Pain point 3
    content = re.sub(
        r'(<div class="pain-icon">❌</div>\s*<h3 class="pain-title">)[^<]+(</h3>\s*<p class="pain-description">)[^<]+(</p>)',
        r'\1Kein Creative-Konzept\2Schlechte Videos = Geld verbrennen. Ohne Hook und Storytelling keine Conversions.\3',
        content,
        count=1
    )

    # ===== METHOD (ZIG-ZAG) =====
    # Keep structure, replace text
    content = re.sub(
        r'(So starten wir Ihre.*?<span class="text-gradient">)Google Ads(</span>)',
        r'\1TikTok Ads\2',
        content
    )

    # Step 1
    content = re.sub(
        r'(<div class="step-number">01</div>\s*<h3 class="step-title">)[^<]+(</h3>\s*<p class="step-description">)[^<]+(</p>)',
        r'\1Creative Analyse\2Wir analysieren, welche TikToks in Ihrer Nische viral gehen. Hooks, Trends, Musikauswahl.\3',
        content,
        count=1
    )

    # Step 2
    content = re.sub(
        r'(<div class="step-number">02</div>\s*<h3 class="step-title">)[^<]+(</h3>\s*<p class="step-description">)[^<]+(</p>)',
        r'\1Video-Produktion & Setup\2Wir erstellen das Creative-Briefing. Kampagnen-Setup mit Pixel-Integration und Tracking.\3',
        content,
        count=1
    )

    # Step 3
    content = re.sub(
        r'(<div class="step-number">03</div>\s*<h3 class="step-title">)[^<]+(</h3>\s*<p class="step-description">)[^<]+(</p>)',
        r'\1Skalierung\2Winning Creatives werden geduppt. Budget-Erhöhung nur bei funktionierenden Ads.\3',
        content,
        count=1
    )

    # ===== PRICING =====
    # Add "Inklusive Creative-Briefing" to descriptions
    content = re.sub(
        r'(Setup-Gebühr.*?<li>Keyword-Recherche & Strategie</li>)',
        r'\1\n                                <li>Inklusive Creative-Briefing</li>',
        content,
        count=2
    )

    # ===== FAQ =====
    # FAQ Question 1
    content = re.sub(
        r'(<button class="faq-question">)[^<]+(</button>\s*<div class="faq-answer" style="display: none;">)[^<]+(</div>)',
        r'\1Brauche ich eigene Videos?\2Ja, aber wir helfen beim Skript. Wir liefern Creative-Briefings mit Hooks, Struktur und Beispielen. Sie produzieren oder beauftragen einen Creator.\3',
        content,
        count=1,
        flags=re.DOTALL
    )

    # FAQ Question 2
    content = re.sub(
        r'(<button class="faq-question">)[^<]+(</button>\s*<div class="faq-answer" style="display: none;">)[^<]+(</div>)',
        r'\1Ist TikTok nur für Kinder?\2Nein, die Kaufkraft ist dort hoch. 50% der Nutzer sind über 30 Jahre alt. Besonders stark: Mode, Beauty, Home & Living, Dienstleistungen.\3',
        content,
        count=1,
        flags=re.DOTALL
    )

    # Write to new file
    with open('de/tiktok-ads.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("OK TikTok page rewritten based on working Google Ads template.")
    print("File: de/tiktok-ads.html")
    print("CSS path: ../styles.css")
    print("JS path: ../js/*.js")

if __name__ == '__main__':
    rewrite_tiktok_page()
