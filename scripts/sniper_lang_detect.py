#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_lang_detect.py — Language detection module for beauty lead names.

Detects Turkish (TR), Arabic (AR), or Ukrainian (UA) origin from business/owner names.
Returns a tag string: 'TR', 'AR', 'UA', or None.

Imported by sniper_batch_prepare_multilang.py and sniper_engine_multilang.py.
"""

# ── Turkish indicators ────────────────────────────────────────────────────────

TR_BUSINESS_KEYWORDS = [
    'kuafor', 'kuaför',           # "hairdresser" in Turkish
    'berber',                      # Turkish for barber — also berberium, berberlin (intentional)
    # Note: 'berber' is checked first; 'zauberberg' won't match because compound check is word-level
    'güzellik', 'guzellik',       # beauty
    'yildiz', 'yıldız',           # star
    'zengin',                      # rich / family name
    'türkisch', 'türk',
    'turkish',
    ' turk ', 'turk-', '-turk',  # standalone word only — avoids "naturkosmetik"
    'istanbul', 'anatolien', 'anadolu',
    'salon selam',
    'saç studio', 'sac studio',
]

TR_GIVEN_NAMES = [
    # Female
    'hunar',                       # Kurdish-Turkish name common in TR community
    'esra','esray',                # Esray is TR variant of Esra
    'ayse','ayşe','bahar','banu','busra','büşra','burcu',
    'canan','cigdem','çiğdem','derya','dilek','duygu',
    'eda','elif','emine','esra','figen','filiz','gamze',
    'gizem','gonca','gulcan','gülcan','gulsen','gülsen',
    'gulsum','gülsüm','guzin','güzin','hande','hatice',
    'hilal','hulya','hülya','irem','ilknur',
    'kübra','kubra','kader','latife','leyla',
    'melike','meltem','merve','meryem',
    'nazan','nilufer','nilüfer','nurgul','nurgül','nursen','nurşen','nurten','nuray',
    'olcay','ozge','özge','ozlem','özlem',
    'perihan','pinar','pınar',
    'rabiye','rukiye','reyhan',
    'selinay','selin','semra','serap','sevinc','sevinç','sibel','songul','songül',
    'sultan','suzan','sevda',
    'tugba','tuğba','tuba','tulay','tülay',
    'ummahan','yesim','yeşim','zeynep',
    # Male
    'ahmet','ali','arzu','aynur',
    'bulent','bülent',
    'eda',  # can be male too
    'erol','ercan','emre',
    'fatma',  # sometimes used for businesses
    'hasan','hüseyin','huseyin',
    'ibrahim',
    'kemal',
    'mehmet','murat','mustafa',
    'omer','ömer',
    'sabri','selin','serkan',
    'taner','tayfun',
    'yusuf',
]

# ── Arabic indicators ─────────────────────────────────────────────────────────

AR_BUSINESS_KEYWORDS = [
    'arabic', 'arabisch', 'arabische',
    'orient friseur', 'orient barber', 'orient style', 'orient hair',
    'orientalisch', 'orientalische',  # not 'orientierte' (German word for "oriented")
    'alhambra', 'marokk', 'marokkanisch',
    'halal beauty', 'halal salon',
    'noor beauty', 'nour beauty',
]

AR_GIVEN_NAMES = [
    # Female
    'aicha','aisha','amira','aya',
    'dina','dalia',
    'fatima',
    'ghada',
    'hana','hiba',
    'dina',     # Arabic name (Dina hair free, Dina Nails) — short but distinctive
    'karima',
    'layla','leilah','lama','lina',
    'malak','mariam','mona',
    'nadia','noura','nour',
    'rana','rania','reem','riham','rola','roaa',
    'salma','samira','sana','sara','sawsan','suha',
    'yasmin','yara',
    'zainab',
    # Male
    'adnan','ahmad','ahmed',
    'bassem','bilal',
    'hassan','hamza',
    'ibrahim',  # shared TR/AR — TR_KEYWORDS take priority
    'karim','kareem','khalid',
    'maher','marwan',
    'nabil',
    'omar',
    'said','samir',
    'tariq',
    'walid','wael',
    'youssef','yusuf',
    'ziad',
]

# ── Ukrainian indicators ─────────────────────────────────────────────────────

UA_GIVEN_NAMES = [
    # As specified by Director + common Ukrainian names in DE diaspora
    'oleksandr', 'oleksandra',
    'iryna',
    'kateryna', 'katerynas',
    'olena',
    'dmytro',
    'serhiy', 'serhii', 'sergiy',
    'oksana',
    'anastasiia', 'anastasia',   # anastasia alone is ambiguous (RU/UA) — kept, suffix check wins
    # Extended diaspora names frequently found in DE salons
    'nataliia', 'nataliya',
    'liudmyla', 'liudmila', 'lyudmyla',
    'halyna', 'galyna',
    'oksana',
    'tetiana', 'tetyana',
    'vasyl',
    'mykola',
    'volodymyr',
    'yuliia', 'yuliya',
    'daryna',
    'khrystyna',
    'svitlana',
]

# Surname suffixes strongly Ukrainian (not shared with Russian to same degree)
UA_SURNAME_SUFFIXES = [
    'enko',   # Shevchenko, Petrenko, Marchenko
    'chuk',   # Savchuk, Kovalchuk, Tkachuk
    'iuk',    # Hryniuk, Kovalyuk
    'ienko',  # Bondarenko variant
    'yuk',    # Kovalyuk variant
    'shyn',   # Hryshyn, Boyko-Hryshyn
    'nko',    # Shevchenko short-suffix scan (covered by 'enko' but explicit)
]

# Business keywords that strongly signal Ukrainian-owned salon
UA_BUSINESS_KEYWORDS = [
    'ukrainisch', 'ukrainische', 'ukrainian',
    'lviv', 'kyiv', 'kyjiv', 'odessa', 'kharkiv',
]

# ── Turkish special characters (fastest signal) ───────────────────────────────
_TR_CHARS = set('ğşıİĞŞ')


# Names that look TR/AR but are common German/European names — skip them
# Names that are prefixes of non-TR/AR names — exclude from compound substring check
_FP_COMPOUND_PREFIXES = {
    'sabri',    # sabri is TR, but 'sabrina' is not — compound check would false-match
}

_FALSE_POSITIVE_NAMES = {
    'sabrina',  # Italian/German, not TR (unlike 'sabri' which is TR)
    'mona',     # too generic (Mona Lisa, etc.)
    'lina',     # German name
    'sara',     # universal
}

# Business name fragments that contain TR keywords but are NOT TR salons
_FALSE_POSITIVE_COMPOUNDS = {
    'zauberberg',    # zauber+berg — not berber
    'naturkosmetik', # contains 'turk' substring — already handled via word boundary
    'naturbeauty',
}


def detect(name: str) -> str | None:
    """
    Returns 'UA', 'TR', 'AR', or None.

    Priority order: UA → TR → AR.
    Ukrainian check runs first: diaspora owners are high-value warm leads.
    """
    n = name.lower()

    # 0. False-positive compound word guard
    for fp in _FALSE_POSITIVE_COMPOUNDS:
        if fp in n:
            n = n.replace(fp, ' ')

    parts = n.replace('-', ' ').replace("'", ' ').replace('.', ' ').replace('&', ' ').split()

    # ── 1. Ukrainian detection ────────────────────────────────────────────────

    # 1a. Business keyword (fastest)
    for kw in UA_BUSINESS_KEYWORDS:
        if kw in n:
            return 'UA'

    # 1b. Surname suffix — check every word-part
    for part in parts:
        for suffix in UA_SURNAME_SUFFIXES:
            if len(part) > len(suffix) + 1 and part.endswith(suffix):
                return 'UA'

    # 1c. Given name match — exact word or clear prefix
    for part in parts:
        for fn in UA_GIVEN_NAMES:
            if len(fn) >= 5 and (part == fn or part.startswith(fn)):
                return 'UA'
        for fn in UA_GIVEN_NAMES:
            if len(fn) >= 6 and fn in n:   # compound: "IrynaBeauty"
                return 'UA'

    # ── 2. Turkish detection ──────────────────────────────────────────────────

    for kw in TR_BUSINESS_KEYWORDS:
        if kw in n:
            return 'TR'

    if any(c in name for c in _TR_CHARS):
        return 'TR'

    for fn in TR_GIVEN_NAMES:
        if len(fn) >= 5 and fn not in _FP_COMPOUND_PREFIXES and fn in n:
            return 'TR'

    for part in parts:
        if part in _FALSE_POSITIVE_NAMES:
            continue
        for fn in TR_GIVEN_NAMES:
            if len(fn) >= 4 and (part == fn or part.startswith(fn + 's') or part == fn + 'n'):
                return 'TR'
        if part in TR_GIVEN_NAMES and len(part) >= 3:
            return 'TR'

    # ── 3. Arabic detection ───────────────────────────────────────────────────

    for kw in AR_BUSINESS_KEYWORDS:
        if kw in n:
            return 'AR'

    for part in parts:
        if part in _FALSE_POSITIVE_NAMES:
            continue
        for fn in AR_GIVEN_NAMES:
            if len(fn) >= 4 and (part == fn or part.startswith(fn + 's') or part == fn + 'n'):
                return 'AR'
        if part in AR_GIVEN_NAMES and len(part) >= 4:
            return 'AR'

    return None


# ── Bilingual UA prompt builder ───────────────────────────────────────────────

def build_ua_bilingual_message(lead: dict) -> str:
    """
    Generates a bilingual DE+UA message for Ukrainian-owned beauty leads.

    Structure:
      Block 1 (DE) — professional entry, problem statement
      Block 2 (UA) — warm Ukrainian peer appeal
      Signature    — 'З повагою, Андрій | Vermarkter'

    Args:
        lead: dict with keys: name, city, notes (optional), website (optional)
    """
    name_raw  = lead.get('name', '')
    city      = lead.get('city') or lead.get('district') or 'München'
    notes     = (lead.get('notes') or '').lower()
    website   = lead.get('website') or ''

    # Extract first name — skip generic business words to find the actual person name
    _SKIP = {'friseur', 'friseure', 'salon', 'studio', 'beauty', 'barber', 'barbershop',
             'nails', 'nail', 'coiffeur', 'kosmetik', 'hair', 'haarwerk', 'by', 'und',
             'und', '&', 'gmbh', 'ug', 'kg', 'ohg'}
    words = name_raw.replace('-', ' ').split()
    first_name = 'Team'
    for w in words:
        if w.lower() not in _SKIP and len(w) > 2:
            first_name = w.title()
            break

    # Determine pain point from notes audit
    has_ssl     = 'ssl=n' in notes
    has_booking = 'booking=n' in notes or ('booking=y' not in notes)
    on_treatwell = 'treatwell' in (website or '').lower()

    if has_ssl:
        de_pain = (
            'Ihre Website wird aktuell von Google als „unsicher" eingestuft. '
            'Das schreckt ca. 70 % der Besucher ab, noch bevor sie Ihre Arbeit sehen.'
        )
        ua_observation = 'я перевірив ваш сайт — браузер показує попередження про безпеку.'
    elif on_treatwell:
        de_pain = (
            'Jede Buchung läuft über Treatwell – das bedeutet Provision für jeden Kunden, '
            'den Sie selbst aufgebaut haben.'
        )
        ua_observation = 'ви працюєте через Treatwell — це комісія з кожного клієнта, якого ви самі виростили.'
    else:
        de_pain = (
            'Viele potenzielle Neukunden finden online keine direkte Buchungsmöglichkeit '
            'und wählen dann den nächsten Salon.'
        )
        ua_observation = 'я не знайшов зручної онлайн-форми для запису на ваш сайті — клієнти йдуть до конкурентів.'

    de_block = (
        f'Guten Tag, {first_name}! '
        f'{de_pain} '
        f'Wir helfen {city}er Salons, das in 14 Tagen zu lösen – '
        f'einmalig 1 000 €, kein Abo, keine laufenden Kosten. '
        f'Darf ich Ihnen das Video-Demo dazu schicken?'
    )

    ua_block = (
        f'Привіт, {first_name}! Я теж українець, займаюся автоматизацією бізнесу в Мюнхені. '
        f'Помітив, що {ua_observation} '
        f'Якщо цікаво — можу показати, як це вирішили інші українські салони тут, у Німеччині. '
        f'Написав по-українськи, бо так простіше 🙂'
    )

    signature = 'З повагою, Андрій | Vermarkter'

    return f'{de_block}\n\n{ua_block}\n\n{signature}'


if __name__ == '__main__':
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    tests = [
        # Ukrainian — given names
        ('Friseur Oleksandr Draganov',   'UA'),
        ('Iryna Beauty Studio',          'UA'),
        ('Kateryna Nails München',       'UA'),
        ('Olena Kosmetik Berlin',        'UA'),
        ('Dmytro Barbershop',            'UA'),
        ('Oksana Friseur & Beauty',      'UA'),
        # Ukrainian — surnames with UA suffix
        ('Salon Petrenko',               'UA'),
        ('Anna Savchuk Beauty',          'UA'),
        ('Nails by Kovalchuk',           'UA'),
        ('Studio Hryniuk',               'UA'),
        # Turkish
        ('Kuaför Delfer 27',             'TR'),
        ('Gülşen Tasch AVEDA SALON',     'TR'),
        ('BENGİN STYLE - Dortmund',      'TR'),
        ('Beautify By Bahar',            'TR'),
        ('ESRAYBEAUTY',                  'TR'),
        ('Sabri Berber Coiffeur',        'TR'),
        ('Hunar Friseur',                'TR'),
        # Arabic
        ('Orient Friseur & Barber',      'AR'),
        ('Beauty By Samira Abadi',       'AR'),
        ('Dina hair free',               'AR'),
        ('Karima Kosmetik',              'AR'),
        # None
        ('Max Mustermann Salon',         None),
        ('Berliner Haarwerk GmbH',       None),
    ]

    print('── detect() tests ────────────────────────────────')
    ok = fail = 0
    for name, expected in tests:
        result = detect(name)
        sym = 'OK' if result == expected else 'FAIL'
        if sym == 'FAIL': fail += 1
        else: ok += 1
        print(f'  [{sym}] "{name}" → {result} (expected {expected})')
    print(f'\n{ok}/{ok+fail} passed')

    print('\n── build_ua_bilingual_message() sample ───────────')
    sample_lead = {
        'name': 'Friseur Oleksandr Draganov',
        'city': 'Berlin',
        'notes': 'ssl=n booking=n',
        'website': '',
    }
    print(build_ua_bilingual_message(sample_lead))
