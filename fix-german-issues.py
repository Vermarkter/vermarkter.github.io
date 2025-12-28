# -*- coding: utf-8 -*-
"""
German Content Quality Fixer
Fixes critical issues in German version:
- Incorrect/English terminology
- Grammatical errors
- Informal expressions
- Anglicisms replacement
- Stylistic improvements
"""

def fix_german_content(content):
    """Fix all German content issues"""

    # 1. CRITICAL TERMINOLOGY ERRORS

    # Fix non-existent German word "Dedizierter"
    content = content.replace(
        'Dedizierter Account Manager',
        'Persönlicher Account Manager'
    )
    content = content.replace(
        'Dedizierter',
        'Persönlicher'
    )

    # Fix English term "Full-Funnel"
    content = content.replace(
        'Full-Funnel Strategie',
        'Strategie für den gesamten Verkaufsprozess'
    )
    content = content.replace(
        'Full-Funnel',
        'Gesamter Verkaufsprozess'
    )

    # Fix English term "Strategy-Calls"
    content = content.replace(
        'Strategy-Calls',
        'Strategiegespräche'
    )
    content = content.replace(
        'Wöchentliche Strategy-Calls',
        'Wöchentliche Strategiegespräche'
    )

    # Fix "Kombo" (English "combo")
    content = content.replace(
        'Kombo',
        'Kombination Google Ads + Meta Ads'
    )

    # Fix "Creative Production"
    content = content.replace(
        'Creative Production',
        'Kreativproduktion (Dreharbeiten + Schnitt)'
    )
    content = content.replace(
        'Creative-Production',
        'Kreativproduktion (Dreharbeiten + Schnitt)'
    )

    # 2. TECHNICAL TERMS - Replace English with German

    content = content.replace(
        'Cost per Click (€)',
        'Kosten pro Klick (€)'
    )
    content = content.replace(
        'Cost per Click',
        'Kosten pro Klick'
    )

    content = content.replace(
        'Conversion Rate (%)',
        'Konversionsrate (%)'
    )
    content = content.replace(
        'Conversion Rate',
        'Konversionsrate'
    )

    content = content.replace(
        'End-to-End Tracking',
        'Durchgängiges Tracking der Customer Journey'
    )

    # 3. GRAMMATICAL ERRORS

    # Fix subject-verb agreement (Budget is singular)
    content = content.replace(
        'Warum verschwinden 80% des Budgets im Nichts?',
        'Warum verschwindet 80% des Budgets im Nichts?'
    )
    content = content.replace(
        'verschwinden 80% des Budgets',
        'verschwindet 80% des Budgets'
    )

    # 4. INFORMAL EXPRESSIONS - Make professional

    content = content.replace(
        'Banner in Paint erstellt – sieht aus wie Spam',
        'Banner aus einfachen Grafiktools – wirken unseriös'
    )
    content = content.replace(
        'sieht aus wie Spam',
        'wirkt unseriös'
    )

    content = content.replace(
        'Budget läuft aus',
        'Budget wird ineffizient genutzt'
    )

    # 5. WRITING ERRORS - Add missing hyphens

    content = content.replace(
        'ROI Rechner',
        'ROI-Rechner'
    )

    content = content.replace(
        'GA4 Setup',
        'GA4-Einrichtung'
    )

    # 6. REPLACE ANGLICISMS with German equivalents

    anglicisms = {
        # Package names and features
        'Launch': 'Kampagnenstart',
        'Reporting': 'Berichterstattung',
        'Setup': 'Einrichtung',

        # Be careful with context - only replace standalone words
        '>Growth<': '>Wachstum<',
        'Growth</h3>': 'Wachstum</h3>',

        # Replace "Creative" with proper German term
        'Creative': 'Anzeigengestaltung',
        'Creatives': 'Anzeigengestaltung',
    }

    for en, de in sorted(anglicisms.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(en, de)

    # 7. IMPROVE READABILITY - Fix compound words

    content = content.replace(
        '48h-Launch-Garantie',
        '48-Stunden-Startgarantie'
    )
    content = content.replace(
        '48h-Launch',
        '48-Stunden-Start'
    )

    # 8. FIX SPECIFIC CALCULATOR LABELS (context-aware)

    # Only fix in calculator section, not in HTML attributes
    content = content.replace(
        '<label for="cpc" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">Cost per Click (€)</label>',
        '<label for="cpc" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">Kosten pro Klick (€)</label>'
    )

    content = content.replace(
        '<label for="conversionRate" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">Conversion Rate (%)</label>',
        '<label for="conversionRate" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">Konversionsrate (%)</label>'
    )

    # 9. FIX UVP TEXT - improve terminology

    content = content.replace(
        'Einzige Agentur in der EU mit 48h-Launch-Garantie und 90% Erfolgsquote',
        'Einzige Agentur in der EU mit 48-Stunden-Startgarantie und 90% Erfolgsquote'
    )

    return content

# Read German file
print("Reading German version...")
with open('de/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Apply fixes
print("Applying fixes...")
content = fix_german_content(content)

# Write back
with open('de/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] German content fixes applied!")
print("\nSummary of fixes:")
print("1. [OK] Fixed critical terminology errors (Dedizierter → Persönlicher)")
print("2. [OK] Replaced English terms with German (Full-Funnel, Strategy-Calls, Kombo)")
print("3. [OK] Fixed technical terms (Cost per Click → Kosten pro Klick)")
print("4. [OK] Fixed grammatical errors (verschwinden → verschwindet)")
print("5. [OK] Replaced informal expressions with professional tone")
print("6. [OK] Fixed writing errors (added missing hyphens)")
print("7. [OK] Replaced anglicisms (Launch → Kampagnenstart, Creative → Anzeigengestaltung)")
print("8. [OK] Improved compound words (48h-Launch → 48-Stunden-Start)")
