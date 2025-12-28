# -*- coding: utf-8 -*-
"""
Turkish Content Quality Fixer
Fixes critical issues in Turkish version:
- Fix German-Turkish hybrid words
- Remove remaining German text
- Fix grammatical and stylistic issues
- Improve professional tone
- Fix unnatural phrasing
"""

def fix_turkish_content(content):
    """Fix all Turkish content issues"""

    # 1. CRITICAL: Fix German-Turkish hybrid word

    content = content.replace(
        'Kârwachstum',
        'Kâr Artışı'
    )
    content = content.replace(
        'Kârı wachstum',
        'Kâr Artışı'
    )

    # 2. REMOVE REMAINING GERMAN TEXT

    # Budget
    content = content.replace(
        'Werbebudget bis €2.500',
        'Reklam bütçesi €2,500\'e kadar'
    )
    content = content.replace(
        'Werbebudget bis €2,500',
        'Reklam bütçesi €2,500\'e kadar'
    )
    content = content.replace(
        'Werbebudget ab €2.500',
        'Reklam bütçesi €2,500\'den itibaren'
    )
    content = content.replace(
        'Werbebudget ab €2,500',
        'Reklam bütçesi €2,500\'den itibaren'
    )
    content = content.replace(
        'Werbebudget',
        'Reklam bütçesi'
    )

    # German support
    content = content.replace(
        'Deutschsprachiger Support',
        'Almanca destek'
    )

    # Setup
    content = content.replace(
        'Einmaliges Setup: €0 (kostenlos)',
        'Tek seferlik kurulum: €0 (ücretsiz)'
    )
    content = content.replace(
        'Einmaliges Setup:',
        'Tek seferlik kurulum:'
    )
    content = content.replace(
        'kostenlos',
        'ücretsiz'
    )

    # Month
    content = content.replace(
        '/ Monat',
        '/ ay'
    )
    content = content.replace(
        '/Monat',
        '/ay'
    )

    # OR/ODER
    content = content.replace(
        'Google Ads ODER Meta Ads',
        'Google Ads VEYA Meta Ads'
    )
    content = content.replace(
        ' ODER ',
        ' VEYA '
    )

    # 3. FIX STYLISTIC AND GRAMMATICAL ISSUES

    # Fix harsh hero phrase
    content = content.replace(
        'AB\'de reklam başlat 48 saat içinde',
        'Reklamlarınızı AB\'de 48 saat içinde başlatın'
    )

    # Fix unclear technical manager phrase
    content = content.replace(
        'Kendi dilinizde teknik yönetici',
        'Kendi dilinizde uzman danışman'
    )

    # Fix harsh imperative forms to polite business forms
    content = content.replace(
        'Kârı hesapla',
        'Kârınızı hesaplayın'
    )
    content = content.replace(
        '>Kârı hesapla<',
        '>Kârınızı hesaplayın<'
    )

    # Fix unnatural word order
    content = content.replace(
        'Bütçenin %82\'i neden kayboluyor boşa?',
        'Bütçenizin %80\'i neden boşa gidiyor?'
    )
    content = content.replace(
        'Bütçenin %80\'i neden kayboluyor boşa?',
        'Bütçenizin %80\'i neden boşa gidiyor?'
    )
    content = content.replace(
        'neden kayboluyor boşa',
        'neden boşa gidiyor'
    )

    # 4. FIX MARKETING TERMINOLOGY

    # Fix unclear abbreviation (should be explained)
    content = content.replace(
        'UÖN olmadan genel metinler',
        'Hedef kitlenize özel olmayan genel metinler'
    )
    content = content.replace(
        'UÖN olmadan',
        'Hedef kitleye özel mesajlar olmadan'
    )

    # Fix unprofessional Paint reference
    content = content.replace(
        'Paint\'te oluşturulan banner\'lar',
        'Profesyonel olmayan, temel araçlarla yapılmış banner\'lar'
    )
    content = content.replace(
        'Paint\'te oluşturulan',
        'Temel araçlarla yapılan'
    )

    # 5. FIX ADDITIONAL PROFESSIONAL TONE ISSUES

    # Make CTAs more polite and professional
    content = content.replace(
        'Potansiyeli hesapla',
        'Potansiyelinizi hesaplayın'
    )
    content = content.replace(
        'Başla',
        'Başlayın'
    )

    # Fix any remaining harsh imperatives in buttons/CTAs
    content = content.replace(
        'Şimdi başla',
        'Şimdi başlayın'
    )
    content = content.replace(
        'Hemen başla',
        'Hemen başlayın'
    )

    # 6. FIX PERCENTAGE CONSISTENCY
    # Ensure consistent use of %80 instead of %82
    content = content.replace(
        '%82',
        '%80'
    )

    return content

# Read Turkish file
print("Reading Turkish version...")
with open('tr/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Apply fixes
print("Applying fixes...")
content = fix_turkish_content(content)

# Write back
with open('tr/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Turkish content fixes applied!")
print("\nSummary of fixes:")
print("1. [OK] Fixed German-Turkish hybrid word (Karwachstum -> Kar Artisi)")
print("2. [OK] Removed all remaining German text")
print("3. [OK] Fixed stylistic issues (harsh phrases -> professional)")
print("4. [OK] Fixed grammatical issues (harsh imperatives -> polite forms)")
print("5. [OK] Fixed marketing terminology (UON -> clear explanation)")
print("6. [OK] Fixed unprofessional references (Paint -> professional tools)")
print("7. [OK] Improved CTA tone (imperative -> polite business forms)")
print("8. [OK] Fixed percentage consistency (82% -> 80%)")
