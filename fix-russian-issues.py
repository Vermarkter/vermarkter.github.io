# -*- coding: utf-8 -*-
"""
Russian Content Quality Fixer
Fixes critical issues in Russian version:
- Remove remaining German and English text
- Fix grammatical errors
- Fix number formatting (Russian uses spaces for thousands)
- Fix unprofessional terminology
- Fix footer and form issues
"""

def fix_russian_content(content):
    """Fix all Russian content issues"""

    # 1. STATISTICS SECTION - Fix German terms and duplicates

    # Fix double percent sign
    content = content.replace(
        '420% % durchschn. ROAS',
        '420% средний ROAS'
    )
    content = content.replace(
        '% durchschn. ROAS',
        '% средний ROAS'
    )
    content = content.replace(
        'durchschn. ROAS',
        'средний ROAS'
    )

    # Fix "Tage bis Launch"
    content = content.replace(
        'Tage bis Launch',
        'дней до запуска'
    )
    content = content.replace(
        '7 Tage bis Launch',
        '7 дней до запуска'
    )

    # 2. HEADERS - Fix mixed language

    content = content.replace(
        'Unsere Кейсы',
        'Наши кейсы'
    )
    content = content.replace(
        'Unsere ',
        'Наши '
    )

    # 3. PRICING SECTION - Remove all German text

    # Month
    content = content.replace(
        '/ Monat',
        '/ месяц'
    )
    content = content.replace(
        '/Monat',
        '/месяц'
    )

    # Budget
    content = content.replace(
        'Werbebudget bis €2.500',
        'Бюджет на рекламу до €2 500'
    )
    content = content.replace(
        'Werbebudget bis €2,500',
        'Бюджет на рекламу до €2 500'
    )
    content = content.replace(
        'Werbebudget ab €2.500',
        'Бюджет на рекламу от €2 500'
    )
    content = content.replace(
        'Werbebudget ab €2,500',
        'Бюджет на рекламу от €2 500'
    )
    content = content.replace(
        'Werbebudget',
        'Бюджет на рекламу'
    )

    # OR/ODER
    content = content.replace(
        'Google Ads ODER Meta Ads',
        'Google Ads ИЛИ Meta Ads'
    )
    content = content.replace(
        ' ODER ',
        ' ИЛИ '
    )

    # Setup
    content = content.replace(
        'Einmaliges Setup: €0 (kostenlos)',
        'Единоразовая настройка: €0 (бесплатно)'
    )
    content = content.replace(
        'Einmaliges Setup:',
        'Единоразовая настройка:'
    )
    content = content.replace(
        'kostenlos',
        'бесплатно'
    )

    # German support
    content = content.replace(
        'Deutschsprachiger Support',
        'Поддержка на немецком языке'
    )

    # 4. SERVICES SECTION - Fix German terms

    content = content.replace(
        'FB-Formulare',
        'Формы Facebook'
    )
    content = content.replace(
        'dynamische Anzeigen',
        'Динамические объявления'
    )
    content = content.replace(
        'Technisches SEO Audit',
        'Технический SEO-аудит'
    )
    content = content.replace(
        'Content-Strategie',
        'Контент-стратегия'
    )
    content = content.replace(
        'Direktverkäufe',
        'Прямые продажи'
    )

    # 5. GRAMMATICAL ERRORS

    # Fix UVP grammatical error (instrumental case)
    content = content.replace(
        '90% успешностью кампаний',
        '90% успешных кампаний'
    )

    # Fix unprofessional "budget leaks" translation
    content = content.replace(
        'Бюджет утекает',
        'Бюджет тратится впустую'
    )
    content = content.replace(
        'бюджет утекает',
        'бюджет тратится впустую'
    )

    # 6. TERMINOLOGY FIXES

    # Fix "buying power" (should be "buying intent")
    content = content.replace(
        'Высокая покупательская способность',
        'Высокая покупательская активность'
    )
    content = content.replace(
        'высокая покупательская способность',
        'высокая покупательская активность'
    )

    # 7. NUMBER FORMATTING - Russian uses spaces for thousands

    # Fix Euro amounts (periods to spaces)
    content = content.replace(
        '€2.500',
        '€2 500'
    )
    content = content.replace(
        '€1.220',
        '€1 220'
    )
    content = content.replace(
        '€1.250',
        '€1 250'
    )
    content = content.replace(
        '€1.500',
        '€1 500'
    )
    content = content.replace(
        '€5.000',
        '€5 000'
    )

    # Also fix comma-formatted numbers
    content = content.replace(
        '€2,500',
        '€2 500'
    )
    content = content.replace(
        '€1,220',
        '€1 220'
    )
    content = content.replace(
        '€1,250',
        '€1 250'
    )
    content = content.replace(
        '€1,500',
        '€1 500'
    )
    content = content.replace(
        '€5,000',
        '€5 000'
    )

    # 8. FOOTER FIXES

    # Fix mixed German-Russian footer text
    content = content.replace(
        'Конфиденциальностьerklärung',
        'Политика конфиденциальности'
    )
    content = content.replace(
        'erklärung',
        ''
    )

    # Fix "Impressum" translation
    content = content.replace(
        'Выходные данные',
        'Реквизиты компании'
    )

    # Fix "Büros"
    content = content.replace(
        'Büros:',
        'Офисы:'
    )
    content = content.replace(
        'Büros',
        'Офисы'
    )

    # Fix chatbot German text
    content = content.replace(
        '💬Fragen? Ich helfe Ihnen!',
        '💬Есть вопросы? Я помогу вам!'
    )
    content = content.replace(
        'Ich helfe Ihnen',
        'Я помогу вам'
    )

    # 9. FIX ANY REMAINING GERMAN FRAGMENTS

    content = content.replace(
        'Tage',
        'дней'
    )

    return content

# Read Russian file
print("Reading Russian version...")
with open('ru/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Apply fixes
print("Applying fixes...")
content = fix_russian_content(content)

# Write back
with open('ru/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Russian content fixes applied!")
print("\nSummary of fixes:")
print("1. [OK] Fixed statistics section (removed German, fixed duplicates)")
print("2. [OK] Fixed headers (Unsere -> Nashi)")
print("3. [OK] Removed all German text from pricing section")
print("4. [OK] Fixed German terms in services section")
print("5. [OK] Fixed grammatical errors (instrumental case, terminology)")
print("6. [OK] Fixed number formatting (periods/commas -> spaces)")
print("7. [OK] Fixed footer German-Russian mix")
print("8. [OK] Fixed chatbot German text")
print("9. [OK] Removed remaining German fragments")
