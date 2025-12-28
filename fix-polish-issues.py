# -*- coding: utf-8 -*-
"""
Polish Content Quality Fixer
Fixes critical issues in Polish version:
- German terms mixed with Polish
- Grammatical errors
- Unprofessional formulations
- Contact data localization
"""

def fix_polish_content(content):
    """Fix all Polish content issues"""

    # 1. Critical: Fix UVP grammatical error
    content = content.replace(
        '90% skutecznością kampanii',
        '90% skuteczności kampanii'
    )

    # 2. Fix methodology terminology
    content = content.replace(
        'System 3-stopniowy',
        'System trzyetapowy'
    )
    content = content.replace(
        '3-stopniowy',
        'trzyetapowy'
    )

    # 3. Critical: Fix German word mixed with Polish
    content = content.replace(
        'Zyskwachstum',
        'Wzrost zysków'
    )
    content = content.replace(
        'Zysk i wachstum',
        'Wzrost zysków'
    )

    # 4. Replace German terms with Polish equivalents
    german_to_polish = {
        # Pricing section
        'Einmaliges Setup': 'Jednorazowa konfiguracja',
        'Monatliches Raportowanie': 'Miesięczne raportowanie',
        'Monatliches Reporting': 'Miesięczne raportowanie',
        'Wöchentliches Reporting': 'Tygodniowe raportowanie',
        'Deutschsprachiger Support': 'Wsparcie w języku niemieckim',
        'Für schnell wachsende Unternehmen': 'Dla szybko rozwijających się firm',
        'Priorisierter Support': 'Priorytetowe wsparcie',
        'Wöchentliche Strategy-Calls': 'Tygodniowe rozmowy strategiczne',
        'Dedizierter Account Manager': 'Dedykowany menedżer konta',
        'Individuell': 'Indywidualny',
        'Technisches SEO Audit': 'Audyt techniczny SEO',
        'Content-Strategie': 'Strategia contentu',
        'Direktverkäufe': 'Sprzedaż bezpośrednia',

        # Replace anglicisms and improve terminology
        'Kombo': 'Pakiet łączony',
        'Full-Funnel Strategie': 'Strategia pełnego lejka',
        'Full-Funnel': 'Pełny lejek',

        # Other German terms
        'Für alle': 'Dla wszystkich',
        'Einmaliges': 'Jednorazowa',
        'Monatliches': 'Miesięczne',
        'Wöchentliche': 'Tygodniowe',
        'Tägliche': 'Dzienne',
    }

    for de, pl in sorted(german_to_polish.items(), key=lambda x: len(x[0]), reverse=True):
        content = content.replace(de, pl)

    # 5. Fix unprofessional formulations
    content = content.replace(
        'budżet się wypala',
        'budżet jest marnowany'
    )
    content = content.replace(
        'Brak negatywnych słów kluczowych – budżet się wypala',
        'Brak negatywnych słów kluczowych – budżet jest marnowany'
    )
    content = content.replace(
        'Szeroki typ dopasowania – płacisz za wszystko',
        'Szeroki zakres dopasowania – płacisz za niecelowe kliknięcia'
    )
    content = content.replace(
        'Reklama dla konkurentów zamiast grupy docelowej',
        'Reklama trafia do konkurencji zamiast do Twoich klientów'
    )

    # 6. Fix contact form placeholders - German to Polish
    content = content.replace(
        'ihre.email@beispiel.de',
        'twoj.email@przyklad.pl'
    )
    content = content.replace(
        'placeholder="ihre.email@beispiel.de"',
        'placeholder="twoj.email@przyklad.pl"'
    )
    content = content.replace(
        '+49 123 456 7890',
        '+48 123 456 789'
    )
    content = content.replace(
        'placeholder="+49 123 456 7890"',
        'placeholder="+48 123 456 789"'
    )

    # 7. Fix footer - German terms
    content = content.replace(
        'Wszystkie prawa vorbehalten',
        'Wszystkie prawa zastrzeżone'
    )
    content = content.replace(
        'vorbehalten',
        'zastrzeżone'
    )
    content = content.replace(
        'Büros:',
        'Biura:'
    )
    content = content.replace(
        'Büros',
        'Biura'
    )

    # 8. Fix calculator terminology
    content = content.replace(
        '>Klicks<',
        '>Kliknięcia<'
    )
    # Be more specific with replacements to avoid breaking HTML
    content = content.replace(
        'id="resultClicks"',
        'id="resultClicks"'  # Keep ID the same for JS
    )
    # Fix the label text only
    content = content.replace(
        '<div class="calculator__result-label" style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Klicks</div>',
        '<div class="calculator__result-label" style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem;">Kliknięcia</div>'
    )

    # 9. Improve form labels for B2B context
    content = content.replace(
        '<label for="name" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">Imię *</label>',
        '<label for="name" style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">Imię i nazwisko *</label>'
    )
    content = content.replace(
        'placeholder="Twoje imię"',
        'placeholder="Jan Kowalski"'
    )
    content = content.replace(
        'placeholder="Imię"',
        'placeholder="Jan Kowalski"'
    )

    return content

# Read Polish file
print("Reading Polish version...")
with open('pl/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Apply fixes
print("Applying fixes...")
content = fix_polish_content(content)

# Write back
with open('pl/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Polish content fixes applied!")
print("\nSummary of fixes:")
print("1. [OK] Fixed UVP grammatical error (skutecznością → skuteczności)")
print("2. [OK] Fixed methodology terminology (3-stopniowy → trzyetapowy)")
print("3. [OK] Removed German-Polish hybrid word (Zyskwachstum → Wzrost zysków)")
print("4. [OK] Replaced 20+ German terms with Polish equivalents")
print("5. [OK] Fixed unprofessional formulations")
print("6. [OK] Localized contact data (DE phone/email → PL)")
print("7. [OK] Fixed footer German terms")
print("8. [OK] Fixed calculator labels (Klicks → Kliknięcia)")
print("9. [OK] Improved form labels for B2B context")
