# -*- coding: utf-8 -*-
import re

with open('en/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace lang="de" BEFORE protecting HTML tags
content = content.replace('lang="de"', 'lang="en"')

# Protect HTML tags from translation by replacing them with placeholders
html_tags = {}
tag_counter = 0

def protect_tag(match):
    global tag_counter
    placeholder = f"___HTML_TAG_{tag_counter}___"
    html_tags[placeholder] = match.group(0)
    tag_counter += 1
    return placeholder

# Protect all HTML tags (opening, closing, and self-closing)
content = re.sub(r'<[^>]+>', protect_tag, content)

translations = {

    # Meta tags - critical for SEO
    'Performance-Marketing für kleine Unternehmen in Europa. Google Ads, Meta Ads, TikTok. Transparente Ergebnisse, professionelle Betreuung.': 'Performance Marketing for Small Businesses in Europe. Google Ads, Meta Ads, TikTok. Transparent Results, Professional Support.',
    'Performance-Marketing für kleine Unternehmen in Europa. Google Ads, Meta Ads, TikTok. Transparente Ergebnisse, professioneller Support.': 'Performance Marketing for Small Businesses in Europe. Google Ads, Meta Ads, TikTok. Transparent Results, Professional Support.',
    'Europa Marketing, Google Ads Deutschland, Meta Ads, Performance Marketing, ROI Rechner': 'Europe Marketing, Google Ads Germany, Meta Ads, Performance Marketing, ROI Calculator',
    'Marketing Deutschland, Google Ads Europa, Meta Ads, Performance Marketing, ROI Rechner': 'Marketing Germany, Google Ads Europe, Meta Ads, Performance Marketing, ROI Calculator',
    'Vermarkter Agency': 'Vermarkter Agency',
    'Vermarkter — Skalieren Sie Ihr Geschäft in Europa': 'Vermarkter — Scale Your Business in Europe',
    'Performance-Marketing für Unternehmen. Transparente Ergebnisse, professioneller Support.': 'Performance Marketing for Businesses. Transparent Results, Professional Support.',
    'Performance-Marketing für Unternehmen': 'Performance Marketing for Businesses',

    # OG Tags
    'Deutschlands führende Performance-Marketing-Agentur': 'Germany\'s Leading Performance Marketing Agency',
    'Professionelle Performance-Marketing-Lösungen für kleine Unternehmen. Steigern Sie Umsatz, Leads und ROI mit Google Ads, Meta Ads und TikTok Ads.': 'Professional Performance Marketing Solutions for Small Businesses. Increase Sales, Leads and ROI with Google Ads, Meta Ads and TikTok Ads.',

    # Page title
    '<title>Performance Marketing Agentur | ROI-fokussiert | Google & Meta Ads</title>': '<title>Performance Marketing Agency | ROI-focused | Google & Meta Ads</title>',

    # Hero section - CRITICAL - must be BEFORE navigation
    'Werbestart in der EU in 48 Stunden': 'Launch Ads in EU in 48 Hours',
    'Erste Leads in 7 Tagen. Technischer Manager in Ihrer Sprache. Wöchentliche Reports.': 'First Leads in 7 Days. Technical Manager in Your Language. Weekly Reports.',

    # Navigation
    'Transparente Preise ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Transparent Prices without Hidden Costs. Choose the Perfect Package for Your Business.',
    'Preise & Pakete': 'Pricing & Packages',
    'Leistungen': 'Services',
    'Cases': 'Cases',
    'Rechner': 'Calculator',
    'Bewertungen': 'Reviews',
    'Preise': 'Pricing',
    'Methode': 'Method',
    'Kontakt': 'Contact',
    'Kostenlos beraten': 'Free Consultation',

    # Hero section
    'Werbestart in der EU <span class="text-gradient">in 48 Stunden</span>': 'Launch Ads in EU <span class="text-gradient">in 48 Hours</span>',
    'Google Ads & Meta Ads für Ihr Business in Europa.': 'Google Ads & Meta Ads for Your Business in Europe.',
    'Performance-Marketing,': 'Performance Marketing,',
    'das sich <span class="highlight">rechnet</span>': 'that <span class="highlight">pays off</span>',
    'Für kleine Unternehmen in Europa, die wachsen wollen – ohne Risiko, nur Ergebnisse.': 'For Small Businesses in Europe Who Want to Grow – No Risk, Only Results.',
    'Jetzt Potenzial berechnen': 'Calculate Potential Now',
    'Wie wir arbeiten': 'How We Work',

    # Stats section
    '% Kunden kehren zurück': '% Clients Return',
    'Durchschnittlicher ROAS': 'Average ROAS',
    'Zufriedene Kunden': 'Satisfied Clients',
    'Verwaltetes Werbebudget/Monat': 'Managed Ad Budget/Month',

    # Problem section
    'Warum verschwenden 80% des Budgets': 'Why 80% of Budget is Wasted',
    'Warum verschwinden 80% des Budgets': 'Why 80% of Budget Disappears',
    'im Nichts': 'Into Nothing',
    '% der Kampagnen scheitern': '% of Campaigns Fail',
    'fehlende Transparenz': 'lack of transparency',
    'Budget verbrannt ohne ROI': 'budget burned without ROI',
    'Die drei häufigsten Gründe für gescheiterte Werbekampagnen': 'The Three Most Common Reasons for Failed Ad Campaigns',
    'Falsche Keywords': 'Wrong Keywords',
    'Sie zahlen für Klicks von Nutzern, die nie kaufen werden. 70% des Traffics sind "informationelle" Suchanfragen ohne Kaufabsicht.': 'You pay for clicks from users who will never buy. 70% of traffic is "informational" searches without purchase intent.',
    'Breiter Match-Type – Sie zahlen für alles Mögliche': 'Broad Match Type – You Pay for Everything',
    'Keine negativen Keywords – Budget läuft aus': 'No Negative Keywords – Budget Leaks',
    'Werbung für Konkurrenten statt Zielgruppe': 'Ads for Competitors Instead of Target Audience',
    'Fehlendes End-to-End Tracking': 'Missing End-to-End Tracking',
    'Ohne korrektes Tracking wissen Sie nicht, welche Anzeige/Keywords Verkäufe bringen. Sie steuern blind.': 'Without proper tracking, you don\'t know which ads/keywords bring sales. You\'re flying blind.',
    'Google Analytics falsch konfiguriert': 'Google Analytics Misconfigured',
    'Conversions werden nicht an Ads übermittelt': 'Conversions Not Sent to Ads',
    'Keine Attribution – Customer Journey unklar': 'No Attribution – Customer Journey Unclear',
    'Schwache Creatives': 'Weak Creatives',
    'Niedrige CTR = hoher CPC. Schlechte Texte und Banner senken den Quality Score und Sie zahlen für jeden Klick mehr.': 'Low CTR = High CPC. Poor texts and banners lower Quality Score and you pay more per click.',
    'Generische Texte ohne USP – niemand klickt': 'Generic Texts Without USP – Nobody Clicks',
    'Banner in Paint erstellt – sieht aus wie Spam': 'Banners Made in Paint – Looks Like Spam',
    'Keine A/B-Tests – Sie bleiben beim ersten Entwurf': 'No A/B Tests – You Stick with First Draft',

    'Kennst du das?': 'Sound Familiar?',
    '<strong>Werbung kostet,</strong> bringt aber keine Kunden?': '<strong>Ads cost money,</strong> but bring no customers?',
    'Du probierst Facebook Ads, Google Ads – das Geld ist weg, aber die Anfragen bleiben aus.': 'You try Facebook Ads, Google Ads – the money is gone, but inquiries don\'t come.',
    '<strong>Keine Zeit</strong> für Kampagnen-Management?': '<strong>No time</strong> for campaign management?',
    'Du willst dich auf dein Business konzentrieren, nicht stundenlang in Werbe-Dashboards sitzen.': 'You want to focus on your business, not sit for hours in ad dashboards.',
    '<strong>Du weißt nicht,</strong> ob deine Werbung funktioniert?': '<strong>You don\'t know</strong> if your ads work?',
    'Keine klaren Zahlen, keine Transparenz – nur vage Versprechen von „Reichweite" und „Impressionen".': 'No clear numbers, no transparency – just vague promises of "reach" and "impressions".',

    # Solution intro
    'Wir machen Performance-Marketing': 'We Make Performance Marketing',
    '<span class="highlight">transparent & messbar</span>': '<span class="highlight">Transparent & Measurable</span>',

    # Method section (3 steps)
    'Unser Ansatz': 'Our Approach',
    'Unsere Methodik: 3-Stufen-System': 'Our Methodology: 3-Step System',
    'So arbeiten wir': 'How We Work',
    'So funktioniert\'s': 'How It Works',
    'Unsere <span class="highlight">3-Schritte-Methode</span>': 'Our <span class="highlight">3-Step Method</span>',
    'SCHRITT 1': 'STEP 1',
    'SCHRITT 2': 'STEP 2',
    'SCHRITT 3': 'STEP 3',

    'Analyse & Strategie': 'Analysis & Strategy',
    'Audit & Strategie': 'Audit & Strategy',
    'Tiefgehende Analyse': 'In-Depth Analysis',
    'Wir analysieren dein Business, deine Zielgruppe und deine Ziele. Daraus entwickeln wir eine maßgeschneiderte Strategie – ohne Standardlösungen.': 'We analyze your business, your target audience and your goals. From this we develop a tailored strategy – no standard solutions.',
    'Wir finden, wo Ihr Budget verschwindet. Analyse von Wettbewerbern, Semantik und technischen Fehlern.': 'We find where your budget disappears. Analysis of competitors, semantics and technical errors.',
    'Nischenanalyse': 'Niche Analysis',
    'Suche nach "Gold"-Keywords': 'Search for "Gold" Keywords',
    'Technisches Audit': 'Technical Audit',
    'Wettbewerber-Mapping': 'Competitor Mapping',

    'Setup & Launch': 'Setup & Launch',
    'Kampagnen-Setup': 'Campaign Setup',
    'Kampagnen Launch': 'Campaign Launch',
    'Kampagnen-Launch': 'Campaign Launch',
    'Struktur und Launch': 'Structure and Launch',
    'Wir erstellen professionelle Kampagnen auf Google Ads, Meta (Facebook/Instagram) oder TikTok – perfekt abgestimmt auf deine Ziele.': 'We create professional campaigns on Google Ads, Meta (Facebook/Instagram) or TikTok – perfectly tailored to your goals.',
    'Wir erstellen Kampagnen mit +8% CTR und Conversion-Tracking ab Tag 1. Keine Experimente.': 'We create campaigns with +8% CTR and conversion tracking from day 1. No experiments.',
    'Strukturierung nach Intent': 'Structuring by Intent',
    'Conversion-Setup (GA4 + Ads)': 'Conversion Setup (GA4 + Ads)',
    'Creatives (Texte + Banner)': 'Creatives (Texts + Banners)',
    'Erster Traffic in 48h': 'First Traffic in 48h',

    'Optimierung & Reporting': 'Optimization & Reporting',
    'Optimierung & Skalierung': 'Optimization & Scaling',
    'Wöchentliche Optimierung': 'Weekly Optimization',
    'Du bekommst wöchentlich klare Zahlen: Kosten, Leads, Umsatz, ROI. Wir optimieren laufend – damit deine Werbung immer besser wird.': 'You get clear numbers weekly: costs, leads, revenue, ROI. We continuously optimize – so your advertising gets better and better.',
    'Wir analysieren jeden €, pausieren teure Keywords und skalieren profitable Kampagnen.': 'We analyze every €, pause expensive keywords and scale profitable campaigns.',
    'Wöchentliche Reports': 'Weekly Reports',
    'Search Terms Analyse': 'Search Terms Analysis',
    'Bid-Anpassungen': 'Bid Adjustments',
    'Creative-Tests (A/B)': 'Creative Tests (A/B)',
    'Bereit zu wachsen?': 'Ready to Grow?',
    'Lassen Sie uns Ihr Business skalieren': 'Let Us Scale Your Business',
    'Wir bauen Kampagnen nach SKAG-Prinzip. Klares Conversion-Tracking.': 'We build campaigns based on SKAG principle. Clear conversion tracking.',

    # Services section
    'Full Stack Marketing Services': 'Full Stack Marketing Services',
    'Von der Strategie bis zur Umsetzung – alles aus einer Hand': 'From Strategy to Implementation – Everything from One Source',

    # Google Ads service details
    'Heißer Traffic aus der Suche. Performance Max für E-Commerce. Shopping Ads für Produkte. Launch in 48 Stunden.': 'Hot Traffic from Search. Performance Max for E-Commerce. Shopping Ads for Products. Launch in 48 Hours.',
    'Search Ads (hohe Kaufabsicht)': 'Search Ads (High Purchase Intent)',
    'Performance Max (KI-Optimierung)': 'Performance Max (AI Optimization)',
    'Shopping Ads (für Online-Shops)': 'Shopping Ads (for Online Stores)',
    'hohe Kaufabsicht': 'high purchase intent',
    'KI-Optimierung': 'AI optimization',
    'für Online-Shops': 'for online stores',
    'Unsere Leistungen': 'Our Services',

    'Google Ads Management': 'Google Ads Management',
    'Such-, Display- und Shopping-Kampagnen, die Kunden bringen – nicht nur Klicks.': 'Search, Display and Shopping campaigns that bring customers – not just clicks.',

    'Meta Ads (Facebook & Instagram)': 'Meta Ads (Facebook & Instagram)',
    'Zielgruppengerechte Anzeigen, die Aufmerksamkeit erzeugen und konvertieren.': 'Target audience-specific ads that generate attention and convert.',
    'Lead-Generierung und Verkäufe über Facebook und Instagram. Lookalike Audiences, Remarketing, Messenger Ads.': 'Lead generation and sales via Facebook and Instagram. Lookalike Audiences, Remarketing, Messenger Ads.',

    'TikTok Ads': 'TikTok Ads',
    'Kreative Video-Ads für junge Zielgruppen – authentisch, viral, wirksam.': 'Creative video ads for young audiences – authentic, viral, effective.',
    'Viraler Content und junge Zielgruppe. In-Feed Ads, Spark Ads, Shopping Ads. Günstiger Traffic für E-Commerce.': 'Viral content and young audience. In-Feed Ads, Spark Ads, Shopping Ads. Affordable traffic for e-commerce.',
    'Spark Ads (organische Posts als Werbung)': 'Spark Ads (organic posts as ads)',

    'SEO & Content Marketing': 'SEO & Content Marketing',
    'Organischer Traffic aus Google. Lokales SEO für die EU. Content-Marketing und Linkbuilding. Langfristige Ergebnisse.': 'Organic traffic from Google. Local SEO for EU. Content marketing and link building. Long-term results.',

    'ROI-Tracking & Reporting': 'ROI Tracking & Reporting',
    'Volle Transparenz: Du siehst genau, was deine Werbung bringt – in Euro und Cent.': 'Full transparency: You see exactly what your advertising brings – in euros and cents.',

    'CRM Integration': 'CRM Integration',
    'Alle Leads automatisch in Telegram/Google Sheets. Email/SMS Auto-Funnels. Volle Kontrolle über Ihren Sales Funnel.': 'All leads automatically in Telegram/Google Sheets. Email/SMS auto-funnels. Full control over your sales funnel.',
    'Email Marketing (Mailchimp, SendGrid)': 'Email Marketing (Mailchimp, SendGrid)',
    'Zapier/Make.com Integrationen': 'Zapier/Make.com Integrations',
    'Telegram Bot für Leads (sofortige Benachrichtigungen)': 'Telegram Bot for Leads (instant notifications)',

    'Web Analytics': 'Web Analytics',
    'Analityka webowa': 'Web Analytics',
    'GA4, GTM, Hotjar, Microsoft Clarity. Vollständiges Verständnis des Nutzerverhaltens. Dashboards in Looker Studio.': 'GA4, GTM, Hotjar, Microsoft Clarity. Complete understanding of user behavior. Dashboards in Looker Studio.',
    'GA4 Setup (Enhanced Ecommerce)': 'GA4 Setup (Enhanced Ecommerce)',
    'Heatmaps & Session Recordings (Hotjar)': 'Heatmaps & Session Recordings (Hotjar)',
    'Custom Dashboards (Looker Studio)': 'Custom Dashboards (Looker Studio)',

    'Optimierung': 'Optimization',
    'Tägliche Gebotsanpassungen. Budget-Skalierung nur bei positivem ROAS.': 'Daily bid adjustments. Budget scaling only with positive ROAS.',
    'Reporting': 'Reporting',
    'Analytics-Setup': 'Analytics Setup',
    'Anzeigenerstellung': 'Ad Creation',

    # Pricing section
    'Für kleine Unternehmen in der EU': 'For Small Businesses in the EU',
    'Über 100 erfolgreiche Projekte für kleine Unternehmen in der EU': 'Over 100 Successful Projects for Small Businesses in the EU',
    'Flexibel, transparent, <span class="highlight">fair</span>': 'Flexible, Transparent, <span class="highlight">Fair</span>',

    # Starter package
    'Starter': 'Starter',
    'Perfekt für den Einstieg': 'Perfect for Getting Started',
    'ab': 'from',
    '€/Monat': '€/month',
    '1 Werbekanal (z.B. Google Ads)': '1 Ad Channel (e.g. Google Ads)',
    'Basis-Setup & Kampagnen': 'Basic Setup & Campaigns',
    'Monatliches Reporting': 'Monthly Reporting',
    'E-Mail-Support': 'Email Support',
    'Jetzt starten': 'Start Now',

    # Professional package
    'Einmaliges Setup: €200': 'One-time Setup: €200',
    'Professional': 'Professional',
    'Für wachsende Unternehmen': 'For Growing Businesses',
    'Beliebteste Option': 'Most Popular Option',
    'Bis zu 2 Werbekanäle': 'Up to 2 Ad Channels',
    'Erweiterte Kampagnen-Optimierung': 'Advanced Campaign Optimization',
    'Wöchentliches Reporting': 'Weekly Reporting',
    'Telefon- & E-Mail-Support': 'Phone & Email Support',
    'A/B-Testing': 'A/B Testing',

    # Enterprise package
    'Für schnell wachsende Unternehmen': 'For Fast-Growing Businesses',
    'Einmaliges Setup: <strong style="color: var(--brand);">€0 (kostenlos)</strong>': 'One-time Setup: <strong style="color: var(--brand);">€0 (free)</strong>',
    'Enterprise': 'Enterprise',
    'Maximale Performance': 'Maximum Performance',
    'Auf Anfrage': 'On Request',
    'Alle Werbekanäle': 'All Ad Channels',
    'Dedizierter Account Manager': 'Dedicated Account Manager',
    'Tägliches Monitoring': 'Daily Monitoring',
    'Priority-Support': 'Priority Support',
    'Custom-Strategie': 'Custom Strategy',
    'Beratung anfragen': 'Request Consultation',

    # Testimonials section
    'Das sagen unsere Kunden': 'What Our Clients Say',

    # Testimonial 1
    'Endlich Werbung, die funktioniert! Seit 3 Monaten arbeiten wir zusammen – unsere Anfragen haben sich verdoppelt, und ich weiß genau, woher sie kommen.': 'Finally advertising that works! We\'ve been working together for 3 months – our inquiries have doubled, and I know exactly where they come from.',
    'Michael S.': 'Michael S.',
    'Handwerksbetrieb, München': 'Craft Business, Munich',

    # Testimonial 2
    'Ich hatte vorher selbst Google Ads probiert – Katastrophe. Jetzt läuft alles professionell, und ich bekomme wöchentlich klare Zahlen. Kann ich nur empfehlen!': 'I tried Google Ads myself before – disaster. Now everything runs professionally, and I get clear numbers weekly. Highly recommend!',
    'Anna K.': 'Anna K.',
    'Online-Shop für Naturkosmetik': 'Natural Cosmetics Online Shop',

    # Testimonial 3
    'Transparenz, Professionalität und Ergebnisse – genau das, was ich gesucht habe. Unser ROI liegt konstant über 400%.': 'Transparency, professionalism and results – exactly what I was looking for. Our ROI is consistently above 400%.',
    'Thomas B.': 'Thomas B.',
    'B2B-Dienstleister, Berlin': 'B2B Service Provider, Berlin',

    # Additional content
    'Kundenbewertungen': 'Client Reviews',
    '"Vermarkter hat uns geholfen, unseren Online-Shop in Deutschland in 6 Tagen zu starten. Die ersten Verkäufe kamen schon nach einer Woche! ROAS 380%."': '"Vermarkter helped us launch our online shop in Germany in 6 days. First sales came after just one week! ROAS 380%."',
    '"Die Meta Ads-Kampagnen brachten uns +180% Lead-Wachstum in 2 Monaten. Empfehle allen, die Transparenz und Ergebnisse suchen!"': '"Meta Ads campaigns brought us +180% lead growth in 2 months. Recommend to everyone seeking transparency and results!"',
    '"Google-Werbung in 2 Tagen gestartet. Nach einer Woche bekamen wir die ersten 15 Anfragen. CRM-Integration mit Telegram - einfach Bombe!"': '"Google Ads launched in 2 days. After one week we got the first 15 inquiries. CRM integration with Telegram - simply awesome!"',
    '"Die SEO-Strategie funktioniert! In 4 Monaten sind wir in den Top 3 für alle Keywords. Organischer Traffic ist um 300% gestiegen."': '"The SEO strategy works! In 4 months we\'re in the top 3 for all keywords. Organic traffic increased by 300%."',
    '"Das Vermarkter-Team kennt sich aus. Transparente Reports, klare KPIs, immer auf Deutsch erreichbar. Arbeiten seit 8 Monaten zusammen."': '"The Vermarkter team knows their stuff. Transparent reports, clear KPIs, always reachable. Working together for 8 months."',
    'Wir sind auf den EU-Markt spezialisiert: Deutschland, Polen, Tschechien, Österreich und andere EU-Länder. Wir kennen die lokalen Besonderheiten jedes Marktes.': 'We specialize in the EU market: Germany, Poland, Czech Republic, Austria and other EU countries. We know the local specifics of each market.',

    # FAQ section
    'Häufige Fragen': 'Frequently Asked Questions',
    'Häufig gestellte Fragen': 'Frequently Asked Questions',
    'Alles, was Sie über unsere Dienstleistungen wissen müssen': 'Everything You Need to Know About Our Services',

    # FAQ 1
    'Für wen ist Performance-Marketing geeignet?': 'Who is Performance Marketing Suitable For?',
    'Performance-Marketing eignet sich für kleine und mittlere Unternehmen, die online wachsen wollen – egal ob E-Commerce, Dienstleistungen, B2B oder lokale Geschäfte.': 'Performance marketing is suitable for small and medium-sized businesses that want to grow online – whether e-commerce, services, B2B or local businesses.',

    # FAQ 2
    'Wie schnell sehe ich Ergebnisse?': 'How Quickly Will I See Results?',
    'Wie schnell kann ich mit Ergebnissen rechnen': 'How quickly can I expect results',
    'Die ersten Daten kommen schon in den ersten Tagen. Messbare Ergebnisse (Leads, Verkäufe) siehst du in der Regel nach 2-4 Wochen – abhängig von deiner Branche und deinem Budget.': 'The first data comes in the first days. Measurable results (leads, sales) you usually see after 2-4 weeks – depending on your industry and budget.',
    'Erste Ergebnisse sehen Sie in der Regel innerhalb von 48-72 Stunden nach dem Launch. Optimale Performance erreichen Kampagnen nach 2-4 Wochen Optimierung.': 'First results are usually visible within 48-72 hours after launch. Optimal performance is reached after 2-4 weeks of optimization.',

    # FAQ 3
    'Brauche ich ein großes Werbebudget?': 'Do I Need a Large Advertising Budget?',
    'Nein. Wir arbeiten auch mit kleinen Budgets ab 500 €/Monat. Wichtig ist, dass das Budget zur Branche und den Zielen passt.': 'No. We also work with small budgets from €500/month. What matters is that the budget fits the industry and goals.',
    'Welches Budget sollte ich für Werbung einplanen?': 'What Budget Should I Plan for Advertising?',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen: €1.000-1.500/Monat. Nutzen Sie unseren ROI-Rechner oben für eine genaue Prognose.': 'It depends on your niche and goals. Minimum budget for effective campaigns: €1,000-1,500/month. Use our ROI calculator above for an accurate forecast.',
    'Das hängt von Ihrer Nische und Ihren Zielen ab. Mindestbudget für effektive Kampagnen: €1.000-1.500/Monat. Nutzen Sie unseren ROI-Kalkulator oben für eine genaue Prognose.': 'It depends on your niche and goals. Minimum budget for effective campaigns: €1,000-1,500/month. Use our ROI calculator above for an accurate forecast.',
    'Das Mindestbudget für Google Ads liegt bei €500/Monat. Für Meta Ads empfehlen wir mindestens €300/Monat. Kleinere Budgets bringen keine statistisch relevanten Daten.': 'The minimum budget for Google Ads is €500/month. For Meta Ads we recommend at least €300/month. Smaller budgets don\'t provide statistically relevant data.',

    # FAQ 4
    'Was unterscheidet euch von anderen Agenturen?': 'What Sets You Apart from Other Agencies?',
    'Volle Transparenz, klare Zahlen und keine langfristigen Verträge. Du zahlst nur, solange du zufrieden bist. Keine versteckten Kosten, keine leeren Versprechen.': 'Full transparency, clear numbers and no long-term contracts. You only pay as long as you\'re satisfied. No hidden costs, no empty promises.',

    # FAQ 5
    'Kann ich jederzeit kündigen?': 'Can I Cancel Anytime?',
    'Ja. Unsere Verträge sind monatlich kündbar. Kein Risiko, keine Bindung.': 'Yes. Our contracts can be canceled monthly. No risk, no commitment.',
    'Benötige ich eine eigene Website?': 'Do I Need My Own Website?',
    'Nicht unbedingt. Wir können für Sie eine konversionsstarke Landing Page erstellen oder Sie können unsere vorgefertigten Templates verwenden.': 'Not necessarily. We can create a high-converting landing page for you or you can use our pre-made templates.',
    'Gibt es eine Mindestvertragslaufzeit?': 'Is There a Minimum Contract Term?',
    'Ja, die Mindestvertragslaufzeit beträgt 3 Monate. Dies gibt uns genügend Zeit, um Ihre Kampagnen zu optimieren und echte Ergebnisse zu liefern. Danach keine Bindung.': 'Yes, the minimum contract term is 3 months. This gives us enough time to optimize your campaigns and deliver real results. After that, no commitment.',
    'In welchen Ländern arbeiten Sie?': 'In Which Countries Do You Work?',

    # Pricing section
    'Preise und Pakete': 'Pricing and Packages',
    'und Pakete': 'and Packages',
    'Transparente Preise ohne versteckte Kosten. Wählen Sie das perfekte Paket für Ihr Unternehmen.': 'Transparent prices without hidden costs. Choose the perfect package for your business.',
    '* Preise exkl. MwSt. Mindestvertrag 3 Monate, danach keine Bindung.': '* Prices excl. VAT. Minimum contract 3 months, after that no commitment.',

    # Calculator section
    'ROI Rechner': 'ROI Calculator',
    'Berechnen Sie die Rentabilität Ihrer Werbekampagne': 'Calculate the Profitability of Your Ad Campaign',
    'Dies ist ein echtes Mediaplanungs-Tool.': 'This is a real media planning tool.',
    'Dieselben Formeln, die große Agenturen verwenden. Transparent, ehrlich, ohne versteckte Kosten.': 'The same formulas that big agencies use. Transparent, honest, without hidden costs.',
    'Wählen Sie Ihre Branche:': 'Select Your Industry:',
    'Eigene Eingabe': 'Custom Input',
    'E-commerce (Produkte)': 'E-commerce (Products)',
    'Dienstleistungen (Handwerk, Beauty)': 'Services (Crafts, Beauty)',
    'Immobilien': 'Real Estate',
    'B2B / Großhandel': 'B2B / Wholesale',
    'Infobusiness / Kurse': 'Infobusiness / Courses',
    'Monatliches Budget (€)': 'Monthly Budget (€)',
    'Cost per Click (€)': 'Cost per Click (€)',
    'Conversion Rate (%)': 'Conversion Rate (%)',
    'Durchschnittlicher Bestellwert (€)': 'Average Order Value (€)',
    'Gewinnmarge (%)': 'Profit Margin (%)',

    # Calculator results
    'Klicks': 'Clicks',
    'Leads': 'Leads',
    'Gewinn': 'Profit',
    '💰 Gewinn berechnen': '💰 Calculate Profit',
    'Strategie für diese Zahlen erhalten': 'Get Strategy for These Numbers',
    'Das Ergebnis ist eine Prognose, kein Versprechen.<br>': 'The result is a forecast, not a promise.<br>',
    'Marketing beginnt mit ehrlichen Zahlen.': 'Marketing starts with honest numbers.',
    'Gewinnwachstum': 'Profit Growth',

    # CTA section
    'Bereit zu starten': 'Ready to Start',
    'Bereit zu starten?': 'Ready to Start?',
    'Bereit zu wachsen': 'Ready to Grow',
    'Bereit für messbares Wachstum?': 'Ready for Measurable Growth?',
    'Lass uns in einem kostenlosen Erstgespräch herausfinden, wie viel Potenzial in deinem Business steckt.': 'Let\'s find out in a free initial consultation how much potential your business has.',
    'Kontaktieren Sie uns für ein technisches Audit oder eine Erstberatung': 'Contact us for a technical audit or initial consultation',
    'Sprechen Sie mit einem Experten': 'Talk to an Expert',
    'Jetzt kostenlos beraten lassen': 'Get Free Consultation Now',
    'Keine Verpflichtungen • 100% transparent': 'No Obligations • 100% Transparent',

    # Contact form
    'Kontaktiere uns': 'Contact Us',
    'Ihr Name': 'Your Name',
    'Name': 'Name',
    'Dein Name': 'Your Name',
    'Ihre E-Mail': 'Your Email',
    'Email': 'Email',
    'Deine Email-Adresse': 'Your Email Address',
    'Telefon (optional)': 'Phone (optional)',
    'Deine Telefonnummer': 'Your Phone Number',
    'Ihre Nachricht': 'Your Message',
    'Nachricht': 'Message',
    'Beschreiben Sie Ihr Projekt...': 'Describe your project...',
    'Beschreibe dein Projekt...': 'Describe your project...',
    'Nachricht senden': 'Send Message',
    'Anfrage senden': 'Send Request',
    'Vielen Dank! Wir melden uns in Kürze bei Ihnen.': 'Thank you! We will contact you shortly.',
    'Oder kontaktieren Sie uns direkt:': 'Or contact us directly:',

    # Footer
    'Marketing-Agentur für kleine Unternehmen in der Europäischen Union.': 'Marketing Agency for Small Businesses in the European Union.',
    'Über uns': 'About Us',
    'Performance-Marketing-Agentur für kleine und mittlere Unternehmen in Europa. Spezialisiert auf Google Ads, Meta Ads und TikTok Ads.': 'Performance Marketing Agency for Small and Medium-Sized Businesses in Europe. Specialized in Google Ads, Meta Ads and TikTok Ads.',

    'Schnelllinks': 'Quick Links',
    'Services': 'Services',
    'Portfolio': 'Portfolio',
    'Blog': 'Blog',
    'Pricing': 'Pricing',
    'Methodik': 'Methodology',

    'Folgen Sie uns': 'Follow Us',
    'Legal': 'Legal',
    'Rechtliches': 'Legal',
    'Impressum': 'Imprint',
    'Datenschutz': 'Privacy',
    'AGB': 'Terms',

    'Alle Rechte vorbehalten': 'All Rights Reserved',
    '© 2025 Performance Marketing Agentur. Alle Rechte vorbehalten.': '© 2025 Performance Marketing Agency. All Rights Reserved.',

    # Pricing additional
    'Pro Monat': 'Per Month',
    'Was ist enthalten': 'What\'s Included',
    'Was ist enthalten:': 'What\'s Included:',
    'Strategie-Call': 'Strategy Call',
    'Keyword-Recherche': 'Keyword Research',
    'Campaign Setup': 'Campaign Setup',
    'Monatliche Optimierung': 'Monthly Optimization',
    'Tägliche Optimierung': 'Daily Optimization',
    'Dedicated Account Manager': 'Dedicated Account Manager',
    'Zugang zu': 'Access to',
    'Kontakt aufnehmen': 'Get in Touch',
    'Perfekt für den Einstieg': 'Perfect for Getting Started',
    'Wachstum': 'Growth',
}

# Apply translations (sorted by key length, longest first to avoid partial replacements)
for de, en in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
    content = content.replace(de, en)

# Restore HTML tags
for placeholder, tag in html_tags.items():
    content = content.replace(placeholder, tag)

# Fix language switcher - replace German flag with English flag
# Replace the button with German flag
german_flag_button = '''<button class="lang-button">
                            <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="4" fill="#000"/>
                                <rect y="4" width="16" height="4" fill="#D00"/>
                                <rect y="8" width="16" height="4" fill="#FFCE00"/>
                            </svg>
                            DE ▼
                        </button>'''

english_flag_button = '''<button class="lang-button">
                            <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                <rect width="16" height="12" fill="#012169"/>
                                <path d="M0,0 L16,12 M16,0 L0,12" stroke="#fff" stroke-width="2.4"/>
                                <path d="M0,0 L16,12 M16,0 L0,12" stroke="#C8102E" stroke-width="1.6"/>
                                <path d="M8,0 V12 M0,6 H16" stroke="#fff" stroke-width="4"/>
                                <path d="M8,0 V12 M0,6 H16" stroke="#C8102E" stroke-width="2.4"/>
                            </svg>
                            EN ▼
                        </button>'''

content = content.replace(german_flag_button, english_flag_button)

# Add German language to dropdown (remove English from dropdown if exists)
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

# Remove English from dropdown if it exists
en_dropdown_item = '''<li><a href="../en/" style="display:block; padding:5px 10px;">
                                <svg width="16" height="12" style="vertical-align:middle; margin-right:4px;">
                                    <rect width="16" height="12" fill="#012169"/>
                                    <path d="M0,0 L16,12 M16,0 L0,12" stroke="#fff" stroke-width="2.4"/>
                                    <path d="M0,0 L16,12 M16,0 L0,12" stroke="#C8102E" stroke-width="1.6"/>
                                    <path d="M8,0 V12 M0,6 H16" stroke="#fff" stroke-width="4"/>
                                    <path d="M8,0 V12 M0,6 H16" stroke="#C8102E" stroke-width="2.4"/>
                                </svg>
                                EN
                            </a></li>'''

content = content.replace(en_dropdown_item, '')

# Fix remaining German text that wasn't translated due to HTML protection
content = content.replace('Werbestart in der EU', 'Launch Ads in EU')
content = content.replace('in 48 Stunden', 'in 48 Hours')
content = content.replace('Full Stack', 'Full Stack')
content = content.replace('Marketing Services', 'Marketing Services')
content = content.replace('Erste Leads in 7 Tagen', 'First Leads in 7 Days')
content = content.replace('Technischer Manager in Ihrer Sprache', 'Technical Manager in Your Language')
content = content.replace('Wöchentliche Reports', 'Weekly Reports')

# Fix contact form placeholders
content = content.replace('placeholder="Ihr Name"', 'placeholder="Your Name"')
content = content.replace('placeholder="ihre.email@beispiel.de"', 'placeholder="your.email@example.com"')
content = content.replace('placeholder="+49 123 456 7890"', 'placeholder="+44 123 456 7890"')
content = content.replace('placeholder="Beschreiben Sie Ihr Projekt..."', 'placeholder="Describe your project..."')

# Fix remaining German phrases that were missed
content = content.replace('📊 Unsere Cases', '📊 Our Cases')
content = content.replace('Das Ergebnis ist eine Prognose, kein Versprechen.<br>', 'The result is a forecast, not a promise.<br>')
content = content.replace('Das Ergebnis ist eine Prognose, kein Versprechen.', 'The result is a forecast, not a promise.')
content = content.replace('Marketing beginnt mit ehrlichen Zahlen.', 'Marketing starts with honest numbers.')
content = content.replace('* Preise exkl. MwSt. Mindestvertrag 3 Monate, danach keine Bindung.', '* Prices excl. VAT. Minimum contract 3 months, then no commitment.')

# Write back
with open('en/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("English translation completed!")
print("Note: Calculator IDs will be fixed with sed post-processing")
