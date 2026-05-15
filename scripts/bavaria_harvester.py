#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bavaria_harvester.py — Beauty lead collector for Bavaria cities.

Collects leads from Google Maps Places API, detects platform/pain tags,
and upserts into Supabase beauty_leads with status='new' (no messages generated).

Usage:
  python scripts/bavaria_harvester.py --city Nürnberg --limit 150
  python scripts/bavaria_harvester.py --city Augsburg --limit 100
  python scripts/bavaria_harvester.py --all
  python scripts/bavaria_harvester.py --city Nürnberg --limit 150 --dry-run
  python scripts/bavaria_harvester.py --report  (summary of existing Bavaria leads)
"""

import sys, io, os, re, json, time, argparse, configparser, urllib.request, urllib.parse, ssl
import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

GMAPS_KEY = _cfg.get('GOOGLE', 'maps_api_key', fallback='')
SB_URL    = (_cfg.get('SUPABASE', 'url', fallback='') or '').strip()
SB_KEY    = (_cfg.get('SUPABASE', 'service_role_key', fallback='') or
             _cfg.get('SUPABASE', 'anon_key', fallback='')).strip()

if not GMAPS_KEY:
    print('[ERROR] GOOGLE maps_api_key not configured', file=sys.stderr); sys.exit(1)
if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE url/service_role_key not configured', file=sys.stderr); sys.exit(1)

# ── Detect which columns exist in beauty_leads ────────────────────────────────

def _detect_columns() -> set:
    try:
        h = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
        url = f'{SB_URL}/rest/v1/?apikey={SB_KEY}'
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=10) as r:
            schema = json.loads(r.read())
        bl   = schema.get('definitions', {}).get('beauty_leads', {})
        cols = set(bl.get('properties', {}).keys())
        return cols if cols else {'id', 'name', 'city', 'phone', 'email', 'website',
                                  'district', 'maps_url', 'status', 'is_mobile',
                                  'custom_message', 'notes'}
    except Exception:
        return set()

_DB_COLUMNS = _detect_columns()
_EXTRA_COLS = {'country', 'reviews_count', 'category', 'platform', 'pain_tags'}

_SB_HEAD = {
    'apikey':        SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type':  'application/json',
    'Prefer':        'return=representation',
}

HTTP_CTX = ssl.create_default_context()
HTTP_CTX.check_hostname = False
HTTP_CTX.verify_mode    = ssl.CERT_NONE

# ── Bavaria city config ───────────────────────────────────────────────────────

BAVARIA_CITIES = {
    'Nürnberg':   {'limit': 150, 'search_name': 'Nürnberg'},
    'Augsburg':   {'limit': 100, 'search_name': 'Augsburg'},
    'Regensburg': {'limit': 80,  'search_name': 'Regensburg'},
    'Ingolstadt': {'limit': 80,  'search_name': 'Ingolstadt'},
    'Würzburg':   {'limit': 80,  'search_name': 'Würzburg'},
}

SEARCH_CATEGORIES = [
    'Friseur',
    'Barbershop',
    'Nagelstudio',
    'Kosmetikstudio',
    'Beauty Salon',
    'Lash Studio',
    'Brow Studio',
    'Permanent Make-up',
    'Aesthetic Hautpflege',
    'Hydrafacial',
]

# category → canonical tag
CATEGORY_TAG_MAP = {
    'Friseur':               'friseur',
    'Barbershop':            'barbershop',
    'Nagelstudio':           'nail_studio',
    'Kosmetikstudio':        'kosmetik',
    'Beauty Salon':          'beauty_salon',
    'Lash Studio':           'lash_studio',
    'Brow Studio':           'brow_studio',
    'Permanent Make-up':     'pmu',
    'Aesthetic Hautpflege':  'aesthetic',
    'Hydrafacial':           'hydrafacial',
}

# ── Platform detection ────────────────────────────────────────────────────────

_PLATFORM_RX = {
    'treatwell': re.compile(r'treatwell', re.I),
    'planity':   re.compile(r'planity', re.I),
    'fresha':    re.compile(r'fresha', re.I),
    'booksy':    re.compile(r'booksy', re.I),
    'salonkee':  re.compile(r'salonkee', re.I),
}

_INSTAGRAM_RX = re.compile(r'instagram\.com', re.I)

def detect_platform(website: str) -> str:
    """Return platform tag or empty string."""
    if not website:
        return ''
    w = website.lower()
    for name, rx in _PLATFORM_RX.items():
        if rx.search(w):
            return name
    if _INSTAGRAM_RX.search(w):
        return 'instagram'
    return ''

# ── Pain tag logic ────────────────────────────────────────────────────────────

_PREMIUM_LOC_RX = re.compile(
    r'\b(altstadt|innenstadt|zentrum|city.?center|marktplatz|hauptmarkt|königstr|karolinenstr|maximilianstr|maxstr|maximilian)\b',
    re.I
)
_INTL_RX = re.compile(r'\b(expat|international|english|arabic|multilingual|mehrsprachig)\b', re.I)
_MEDICAL_RX = re.compile(r'\b(botox|filler|laser|hydrafacial|aesthetic|ästhetik|mesother|prp|skin.?care)\b', re.I)
_ACADEMY_RX = re.compile(r'\b(academy|akademie|ausbildung|schulung|training|workshop|kurs)\b', re.I)
_LUXURY_RX  = re.compile(r'\b(luxury|luxus|premium|exklusiv|exclusive|high.?end|vip)\b', re.I)
_BARBERSHOP_PREMIUM_RX = re.compile(r'\b(barbershop|barber|rasur|bartpflege)\b', re.I)

def compute_pain_tags(name: str, website: str, address: str, platform: str,
                      rating: float, reviews: int, phone: str,
                      category: str) -> list:
    tags = []
    site = (website or '').lower()
    addr = (address or '').lower()
    nm   = (name or '').lower()
    blob = f'{nm} {site} {addr}'

    # platform tags
    if platform == 'treatwell':   tags.append('treatwell')
    elif platform == 'planity':   tags.append('planity')
    elif platform == 'fresha':    tags.append('fresha')
    elif platform == 'instagram': tags.append('instagram_only')
    elif not website:             tags.append('no_website')

    if not website:
        tags.append('no_online_booking')
    elif platform in ('treatwell', 'planity', 'fresha', 'booksy', 'salonkee'):
        pass  # has booking but via 3rd party — already tagged
    else:
        # has own site; do a light check — we can't actually visit it here
        tags.append('weak_website')  # default; enricher can upgrade later

    if _PREMIUM_LOC_RX.search(addr):
        tags.append('premium_location')
    if _INTL_RX.search(blob):
        tags.append('international_audience')
    if _MEDICAL_RX.search(blob) or category in ('Hydrafacial', 'Aesthetic Hautpflege'):
        tags.append('medical_beauty')
    if _ACADEMY_RX.search(blob):
        tags.append('academy')
    if _LUXURY_RX.search(blob):
        tags.append('luxury_service')
    if _BARBERSHOP_PREMIUM_RX.search(nm) and (rating or 0) >= 4.5:
        tags.append('barbershop_premium')

    # deduplicate preserving order
    seen = set()
    return [t for t in tags if not (t in seen or seen.add(t))]

# ── Mobile phone detection ────────────────────────────────────────────────────

_MOBILE_RX = re.compile(r'^\+49\s*1[5-7]\d', re.I)  # +49 15x / 16x / 17x

def is_mobile_phone(phone: str) -> bool:
    if not phone:
        return False
    return bool(_MOBILE_RX.match(phone.strip()))

# ── Email scraper ─────────────────────────────────────────────────────────────

_EMAIL_RX  = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_BAD_EMAIL = re.compile(r"\.(png|jpg|jpeg|gif|webp|svg|css|js|woff|ttf)$", re.I)
_JUNK_DOMAINS = re.compile(r'(sentry|wixpress|example|test\.com|schema\.org)', re.I)

def scrape_email(website: str) -> str | None:
    if not website:
        return None
    base = website.rstrip('/')
    pages = [base, base + '/impressum', base + '/kontakt', base + '/imprint', base + '/contact']
    for url in pages[:4]:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6, context=HTTP_CTX) as r:
                html = r.read().decode('utf-8', errors='ignore')
        except Exception:
            continue
        found = []
        for m in re.finditer(r'mailto:([^"\'\s>]+)', html, re.I):
            e = m.group(1).split('?')[0].strip().lower()
            if e and not _BAD_EMAIL.search(e) and not _JUNK_DOMAINS.search(e):
                found.append(e)
        for m in _EMAIL_RX.finditer(html):
            e = m.group(0).lower()
            if e and not _BAD_EMAIL.search(e) and not _JUNK_DOMAINS.search(e):
                found.append(e)
        if found:
            for pref in ('info@', 'kontakt@', 'hallo@', 'mail@', 'office@', 'salon@'):
                for e in found:
                    if e.startswith(pref):
                        return e
            return found[0]
    return None

# ── Google Maps API ───────────────────────────────────────────────────────────

_GMAPS_DETAIL_FIELDS = (
    'name,formatted_address,formatted_phone_number,international_phone_number,'
    'website,rating,user_ratings_total,types,url,business_status'
)

def _gmaps_get(endpoint: str, params: dict) -> dict:
    params = dict(params)
    params['key'] = GMAPS_KEY
    url = 'https://maps.googleapis.com/maps/api/' + endpoint + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15, context=HTTP_CTX) as r:
        return json.loads(r.read().decode('utf-8'))

def maps_text_search(query: str) -> list:
    results = []
    params  = {'query': query, 'language': 'de', 'region': 'de'}
    for _ in range(3):
        data = _gmaps_get('place/textsearch/json', params)
        results.extend(data.get('results', []))
        token = data.get('next_page_token')
        if not token:
            break
        time.sleep(2.2)
        params = {'pagetoken': token}
    return results

def place_details(place_id: str) -> dict:
    data = _gmaps_get('place/details/json', {
        'place_id': place_id,
        'fields':   _GMAPS_DETAIL_FIELDS,
        'language': 'de',
    })
    return data.get('result', {})

def canon_maps_url(place_id: str) -> str:
    return f'https://www.google.com/maps/place/?q=place_id:{place_id}'

# ── Supabase helpers ──────────────────────────────────────────────────────────

def _sb_req(method: str, path: str, payload=None, extra_headers: dict = None) -> tuple[int, any]:
    url  = SB_URL + path
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None
    h    = dict(_SB_HEAD)
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode('utf-8')
            return r.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')

def sb_get(path: str) -> list:
    code, data = _sb_req('GET', path)
    if code != 200:
        return []
    return data or []

def find_existing_id(maps_url: str, name: str, city: str) -> int | None:
    enc_url = urllib.parse.quote(maps_url, safe='')
    rows = sb_get(f'/rest/v1/beauty_leads?select=id&maps_url=eq.{enc_url}')
    if rows:
        return rows[0]['id']
    enc_name = urllib.parse.quote(name, safe='')
    enc_city = urllib.parse.quote(city, safe='')
    rows = sb_get(f'/rest/v1/beauty_leads?select=id&name=eq.{enc_name}&city=eq.{enc_city}')
    return rows[0]['id'] if rows else None

def _filter_record(record: dict) -> dict:
    """Remove keys that don't exist in the DB schema to avoid 400 errors."""
    if not _DB_COLUMNS:
        return record  # schema fetch failed — send all and hope for the best
    missing = _EXTRA_COLS - _DB_COLUMNS
    if missing:
        return {k: v for k, v in record.items() if k not in missing}
    return record

def upsert_lead(record: dict, dry: bool = False) -> tuple[str, int | None]:
    existing = find_existing_id(record['maps_url'], record['name'], record['city'])
    safe_rec = _filter_record(record)

    if existing:
        patch = {k: v for k, v in safe_rec.items()
                 if v is not None and k not in ('status', 'custom_message')}
        if dry:
            return 'would_update', existing
        code, _ = _sb_req('PATCH', f'/rest/v1/beauty_leads?id=eq.{existing}',
                          patch, {'Prefer': 'return=minimal'})
        return ('updated' if code in (200, 204) else f'patch_err_{code}'), existing

    if dry:
        return 'would_insert', None
    code, resp = _sb_req('POST', '/rest/v1/beauty_leads', [safe_rec])
    if code in (200, 201) and isinstance(resp, list) and resp:
        return 'inserted', resp[0].get('id')
    return f'insert_err_{code}', None

# ── City / district extractor ─────────────────────────────────────────────────

def parse_city_district(formatted_address: str, city_override: str) -> tuple[str, str]:
    """Returns (city, district). district = sub-locality or street."""
    parts  = [p.strip() for p in formatted_address.split(',')]
    city   = city_override
    district = ''
    # Find the street part (first part before PLZ token)
    for p in parts:
        if re.search(r'\d{5}', p):
            break
        if not district:
            district = p
    # Try to extract Stadtteil from address
    for p in parts:
        m = re.search(r'\d{5}\s+(.+)', p)
        if m:
            extracted = m.group(1).strip()
            # If it's just the city itself, try next part
            if extracted.lower() != city_override.lower():
                district = extracted
    return city, district

# ── Main harvester ────────────────────────────────────────────────────────────

def harvest_city(city: str, limit: int, dry: bool = False) -> dict:
    print(f'\n{"="*64}')
    print(f'  City: {city}  |  Limit: {limit}  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'{"="*64}')

    seen_place_ids: set = set()
    inserted = updated = errors = 0
    stats = {
        'city':         city,
        'total':        0,
        'with_email':   0,
        'mobile_phone': 0,
        'no_website':   0,
        'instagram_only': 0,
        'treatwell':    0,
        'planity_fresha': 0,
        'premium_leads': [],  # list of dicts for top-20 report
    }

    for category in SEARCH_CATEGORIES:
        if limit and inserted >= limit:
            break

        query = f'{category} in {city}'
        print(f'\n  [{category}] "{query}" ...', end=' ', flush=True)
        try:
            results = maps_text_search(query)
        except Exception as e:
            print(f'FAIL: {e}')
            continue
        print(f'{len(results)} results')

        for r in results:
            if limit and inserted >= limit:
                break

            pid = r.get('place_id')
            if not pid or pid in seen_place_ids:
                continue
            seen_place_ids.add(pid)

            # Skip permanently closed
            if r.get('business_status') == 'CLOSED_PERMANENTLY':
                continue

            try:
                d = place_details(pid)
            except Exception as e:
                print(f'    [details FAIL] {r.get("name", "?")} — {e}')
                errors += 1
                continue
            time.sleep(0.3)

            if d.get('business_status') == 'CLOSED_PERMANENTLY':
                continue

            name    = (d.get('name') or r.get('name') or '').strip()
            addr    = (d.get('formatted_address') or r.get('formatted_address') or '').strip()
            phone   = d.get('international_phone_number') or d.get('formatted_phone_number')
            website = d.get('website')
            rating  = d.get('rating')
            reviews = d.get('user_ratings_total')
            maps_url = canon_maps_url(pid)

            if not name:
                continue

            _, district = parse_city_district(addr, city)
            platform = detect_platform(website)

            # Email scraping (only if own website, not a booking platform link)
            email = None
            if website and platform not in ('treatwell', 'planity', 'fresha', 'booksy', 'salonkee', 'instagram'):
                try:
                    email = scrape_email(website)
                except Exception:
                    email = None
                time.sleep(0.15)

            is_mobile = is_mobile_phone(phone)
            pain_tags = compute_pain_tags(name, website, addr, platform, rating, reviews, phone, category)

            record = {
                'name':          name,
                'city':          city,
                'country':       'Germany',
                'district':      district or addr,
                'phone':         phone,
                'email':         email,
                'website':       website,
                'maps_url':      maps_url,
                # 'rating' column does not exist in beauty_leads — kept only in-memory for scoring
                'reviews_count': reviews,
                'category':      CATEGORY_TAG_MAP.get(category, category.lower().replace(' ', '_')),
                'is_mobile':     is_mobile,
                'platform':      platform or None,
                'pain_tags':     pain_tags,
                'status':        'new',
                'custom_message': None,
            }

            action, lead_id = upsert_lead(record, dry=dry)

            # Stats
            stats['total'] += 1
            if email:           stats['with_email'] += 1
            if is_mobile:       stats['mobile_phone'] += 1
            if 'no_website' in pain_tags:     stats['no_website'] += 1
            if 'instagram_only' in pain_tags: stats['instagram_only'] += 1
            if 'treatwell' in pain_tags:      stats['treatwell'] += 1
            if 'planity' in pain_tags or 'fresha' in pain_tags:
                stats['planity_fresha'] += 1

            # Premium lead scoring for Sniper
            score = 0
            if rating and rating >= 4.5:  score += 2
            if reviews and reviews >= 50: score += 2
            if email:                     score += 3
            if 'premium_location' in pain_tags: score += 3
            if 'medical_beauty' in pain_tags:   score += 2
            if 'barbershop_premium' in pain_tags: score += 2
            if 'luxury_service' in pain_tags:   score += 2
            if 'no_website' in pain_tags:       score += 1  # easy pain to sell on
            if is_mobile:                       score += 1

            stats['premium_leads'].append({
                'id':       lead_id,
                'name':     name,
                'city':     city,
                'category': CATEGORY_TAG_MAP.get(category, category),
                'rating':   rating,
                'reviews':  reviews,
                'phone':    phone,
                'email':    email,
                'platform': platform or '—',
                'pain_tags': ', '.join(pain_tags[:4]),
                'score':    score,
                '_action':  action,
            })

            tag = {'inserted': 'INS', 'updated': 'UPD',
                   'would_insert': 'DRY-INS', 'would_update': 'DRY-UPD'}.get(action, 'ERR')

            if 'insert' in action or 'would_insert' in action:
                inserted += 1
            elif 'update' in action or 'would_update' in action:
                updated += 1
            else:
                errors += 1

            print(f'    [{tag}] {name[:40]:<40} '
                  f'⭐{rating or "?"} '
                  f'📞{"mob" if is_mobile else ("fix" if phone else "—")} '
                  f'✉ {"y" if email else "—"} '
                  f'🌐{"y" if website else "—"} '
                  f'[{", ".join(pain_tags[:3])}]')

    print(f'\n  {city}: inserted={inserted} updated={updated} errors={errors} '
          f'seen={len(seen_place_ids)}')

    # Sort premium leads by score desc, keep top 20
    stats['premium_leads'].sort(key=lambda x: x['score'], reverse=True)
    stats['premium_leads'] = stats['premium_leads'][:20]
    stats['inserted'] = inserted
    stats['updated']  = updated
    stats['errors']   = errors
    return stats

# ── Report printer ────────────────────────────────────────────────────────────

def print_report(all_stats: list[dict]) -> None:
    print('\n' + '='*70)
    print('  BAVARIA HARVEST — REPORT')
    print('='*70)
    print(f'  {"City":<14} {"Total":>6} {"Email":>6} {"Mobile":>7} {"NoSite":>7} {"IG":>4} {"TW":>4} {"PL/FR":>6}')
    print('  ' + '-'*60)
    totals = dict(total=0, with_email=0, mobile_phone=0, no_website=0,
                  instagram_only=0, treatwell=0, planity_fresha=0)
    for s in all_stats:
        print(f'  {s["city"]:<14} {s["total"]:>6} {s["with_email"]:>6} '
              f'{s["mobile_phone"]:>7} {s["no_website"]:>7} '
              f'{s["instagram_only"]:>4} {s["treatwell"]:>4} {s["planity_fresha"]:>6}')
        for k in totals:
            totals[k] += s.get(k, 0)
    print('  ' + '-'*60)
    print(f'  {"TOTAL":<14} {totals["total"]:>6} {totals["with_email"]:>6} '
          f'{totals["mobile_phone"]:>7} {totals["no_website"]:>7} '
          f'{totals["instagram_only"]:>4} {totals["treatwell"]:>4} '
          f'{totals["planity_fresha"]:>6}')

    print('\n' + '='*70)
    print('  TOP 20 PREMIUM LEADS FOR SNIPER')
    print('='*70)

    all_premium = []
    for s in all_stats:
        all_premium.extend(s.get('premium_leads', []))
    all_premium.sort(key=lambda x: x['score'], reverse=True)

    print(f'  {"#":>3}  {"Name":<36} {"City":<12} {"Cat":<12} '
          f'{"⭐":>4} {"Rev":>5} {"Email":>5} {"Tags"}')
    print('  ' + '-'*100)
    for i, p in enumerate(all_premium[:20], 1):
        print(f'  {i:>3}. {(p["name"] or "")[:35]:<36} {p["city"]:<12} '
              f'{str(p["category"])[:11]:<12} '
              f'{str(p["rating"] or "?"):>4} {str(p["reviews"] or "?"):>5} '
              f'{"y" if p["email"] else "—":>5}  {p["pain_tags"][:45]}')
    print()

# ── Standalone report from Supabase ──────────────────────────────────────────

def print_db_report() -> None:
    """Pull existing Bavaria leads from Supabase and print summary."""
    import urllib.parse as up
    cities = list(BAVARIA_CITIES.keys())
    print('\nFetching Bavaria leads from Supabase...')
    all_leads = []
    for city in cities:
        enc = up.quote(city, safe='')
        rows = sb_get(
            f'/rest/v1/beauty_leads?city=eq.{enc}'
            f'&select=id,name,city,email,phone,is_mobile,platform,pain_tags,rating,reviews_count,category,status'
            f'&limit=2000'
        )
        all_leads.extend(rows)
        print(f'  {city}: {len(rows)} rows')

    if not all_leads:
        print('No Bavaria leads found in DB.')
        return

    by_city: dict[str, list] = {}
    for lead in all_leads:
        c = lead.get('city', 'Unknown')
        by_city.setdefault(c, []).append(lead)

    stats_list = []
    for city, leads in by_city.items():
        pain_flat = []
        for l in leads:
            pt = l.get('pain_tags') or []
            if isinstance(pt, list):
                pain_flat.extend(pt)
        stats = {
            'city':          city,
            'total':         len(leads),
            'with_email':    sum(1 for l in leads if l.get('email')),
            'mobile_phone':  sum(1 for l in leads if l.get('is_mobile')),
            'no_website':    pain_flat.count('no_website'),
            'instagram_only': pain_flat.count('instagram_only'),
            'treatwell':     pain_flat.count('treatwell'),
            'planity_fresha': pain_flat.count('planity') + pain_flat.count('fresha'),
            'premium_leads': [],
        }
        # Build premium list
        for l in leads:
            pt  = l.get('pain_tags') or []
            if isinstance(pt, str):
                pt = pt.strip('{}').replace('"', '').split(',')
            score = 0
            rv = l.get('reviews_count') or 0
            if rv >= 100: score += 3
            elif rv >= 50: score += 2
            elif rv >= 20: score += 1
            if l.get('email'):                             score += 3
            if 'premium_location' in pt:                   score += 3
            if 'medical_beauty' in pt:                     score += 2
            if 'barbershop_premium' in pt:                 score += 2
            if 'luxury_service' in pt:                     score += 2
            if 'no_website' in pt:                         score += 1
            if l.get('is_mobile'):                         score += 1
            stats['premium_leads'].append({
                'id':       l.get('id'),
                'name':     l.get('name', ''),
                'city':     city,
                'category': l.get('category', ''),
                'rating':   None,
                'reviews':  l.get('reviews_count'),
                'email':    l.get('email'),
                'pain_tags': ', '.join(pt[:4]) if isinstance(pt, list) else '',
                'score':    score,
            })
        stats['premium_leads'].sort(key=lambda x: x['score'], reverse=True)
        stats['premium_leads'] = stats['premium_leads'][:20]
        stats_list.append(stats)

    print_report(stats_list)

# ── Sniper pilot batch ────────────────────────────────────────────────────────

# Chain names for common booking platforms
_CHAINS = re.compile(
    r'\b(supercuts|great\s*clips|regis|fantastic\s*sam|sport\s*clips|hairhouse|'
    r'klier|essanelle|frisör\s*klier|hairworld|hairkiller|headway|toni\s*guy|'
    r'jean\s*louis\s*david|tchip|saint\s*algue)\b',
    re.I
)

def build_evidence(lead: dict) -> str:
    """
    Build a human-readable evidence string for each pain_tag on a lead.
    Returns a concise sentence per tag, joined by ' | '.
    Returns '' if no evidence can be constructed (lead should be skipped).
    """
    tags   = lead.get('pain_tags') or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.strip('{}').replace('"','').split(',') if t.strip()]

    name     = lead.get('name', '')
    website  = lead.get('website') or ''
    platform = lead.get('platform') or ''
    reviews  = lead.get('reviews_count') or 0
    district = lead.get('district') or ''
    category = lead.get('category') or ''
    phone    = lead.get('phone') or ''

    evidence_parts = []

    for tag in tags:
        if tag == 'no_website':
            evidence_parts.append(
                f'no_website: kein Website-Link auf Google Maps gefunden'
                + (f' (nur Telefon: {phone})' if phone else '')
            )
        elif tag == 'instagram_only':
            evidence_parts.append(
                f'instagram_only: Google Maps verlinkt direkt auf instagram.com statt eigene Website'
            )
        elif tag == 'treatwell':
            evidence_parts.append(
                f'treatwell: Website-URL enthält treatwell.de — kein eigenes Buchungssystem'
            )
        elif tag == 'planity':
            evidence_parts.append(
                f'planity: Website-URL enthält planity.com — Buchungen laufen über Drittanbieter'
            )
        elif tag == 'fresha':
            evidence_parts.append(
                f'fresha: Website-URL enthält fresha.com — kein eigenes Online-Buchungssystem'
            )
        elif tag == 'no_online_booking':
            if not website:
                evidence_parts.append(
                    'no_online_booking: keine Website → keine Online-Buchung möglich'
                )
            else:
                evidence_parts.append(
                    f'no_online_booking: eigene Website ({website[:50]}) ohne erkennbares Buchungs-Widget'
                )
        elif tag == 'weak_website':
            if website:
                evidence_parts.append(
                    f'weak_website: Website vorhanden ({website[:50]}) — kein Booking-Tool erkannt, '
                    f'wahrscheinlich nur Visitenkarte'
                )
        elif tag == 'premium_location':
            evidence_parts.append(
                f'premium_location: Adresse enthält Innenstadt/Altstadt-Indikator — "{district[:60]}"'
            )
        elif tag == 'medical_beauty':
            evidence_parts.append(
                f'medical_beauty: Kategorie "{category}" oder Name deutet auf ästhetische Behandlungen hin'
            )
        elif tag == 'barbershop_premium':
            rev_str = f'{reviews} Bewertungen' if reviews else 'Bewertungen vorhanden'
            evidence_parts.append(
                f'barbershop_premium: Barbershop mit {rev_str} — Premium-Positionierung wahrscheinlich'
            )
        elif tag == 'luxury_service':
            evidence_parts.append(
                f'luxury_service: Name/Website enthält "luxury/premium/exklusiv" — '
                f'Hochpreis-Positionierung erkennbar'
            )
        elif tag == 'international_audience':
            evidence_parts.append(
                f'international_audience: Name oder Beschreibung enthält mehrsprachige/internationale Signale'
            )
        elif tag == 'academy':
            evidence_parts.append(
                f'academy: Name/Website enthält "Akademie/Academy/Ausbildung" — '
                f'Schulungsangebot vorhanden, höherer Lifetime Value'
            )

    return ' | '.join(evidence_parts)


# Flags that mark a lead as a chain / empty profile / unusable
def _is_chain(name: str) -> bool:
    return bool(_CHAINS.search(name or ''))

def _is_empty_profile(lead: dict) -> bool:
    has_contact = bool(lead.get('phone') or lead.get('email'))
    has_tags    = bool(lead.get('pain_tags'))
    return not has_contact or not has_tags


def sniper_pilot_batch(city: str = '', top_n: int = 20) -> None:
    """
    Pull Bavaria leads from Supabase, filter and rank, print Sniper-ready batch.
    Optionally filtered to a single city.
    """
    import urllib.parse as up

    cities = [city] if city else list(BAVARIA_CITIES.keys())
    print(f'\nFetching leads for Sniper batch (cities: {", ".join(cities)})...')

    all_leads = []
    for c in cities:
        enc  = up.quote(c, safe='')
        rows = sb_get(
            f'/rest/v1/beauty_leads'
            f'?city=eq.{enc}'
            f'&select=id,name,city,district,category,reviews_count,'
            f'website,phone,email,platform,pain_tags,status,is_mobile,'
            f'custom_message,batch_id,email_funnel_json'
            f'&limit=2000'
        )
        all_leads.extend(rows)

    if not all_leads:
        print('No leads found. Run harvest first.')
        return

    # ── Filter ────────────────────────────────────────────────────────────────
    _JUNK_EMAIL_RX = re.compile(
        r'beispiel@|@beispiel\.'         # placeholder
        r'|&#\d+;'                       # HTML-encoded address
        r'|@ivof\.com$'                  # non-salon vendor
        r'|@ebvv\.com$'
        r'|noreply|no-reply|donotreply'
        r'|@treatwell\.|@planity\.|@booksy\.|@fresha\.|@salonkee\.',
        re.I
    )

    _ALREADY_SENT_STATUSES = {
        'wa_ready', 'email_ready', 'funnel_ready',
        'EMAIL SENT', 'email_sent', 'НАДІСЛАНО WA',
    }

    candidates = []
    skipped_chain = skipped_empty = skipped_no_evidence = 0
    skipped_already = skipped_junk_email = 0

    for lead in all_leads:
        # Skip leads already processed in a previous batch
        if lead.get('custom_message'):
            skipped_already += 1
            continue
        if lead.get('email_funnel_json'):
            skipped_already += 1
            continue
        if lead.get('batch_id'):
            skipped_already += 1
            continue
        if (lead.get('status') or '') in _ALREADY_SENT_STATUSES:
            skipped_already += 1
            continue

        # Must-have contact
        if not lead.get('phone') and not lead.get('email'):
            skipped_empty += 1
            continue

        # Strip junk/technical emails — they don't belong to the salon
        raw_email = (lead.get('email') or '').strip()
        if raw_email and _JUNK_EMAIL_RX.search(raw_email):
            lead = {**lead, 'email': None}
            skipped_junk_email += 1
            # don't skip the lead entirely — it may still have a phone
            if not lead.get('phone'):
                skipped_empty += 1
                continue

        # Skip chains
        if _is_chain(lead.get('name', '')):
            skipped_chain += 1
            continue

        # Skip empty profiles
        if _is_empty_profile(lead):
            skipped_empty += 1
            continue

        # Must have evidence
        evidence = build_evidence(lead)
        if not evidence:
            skipped_no_evidence += 1
            continue

        # Score (same weights as harvest_city)
        tags = lead.get('pain_tags') or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.strip('{}').replace('"','').split(',') if t.strip()]

        score = 0
        rv = lead.get('reviews_count') or 0
        if rv >= 100: score += 3
        elif rv >= 50: score += 2
        elif rv >= 20: score += 1
        if lead.get('email'):                    score += 3
        if 'premium_location'  in tags:          score += 3
        if 'medical_beauty'    in tags:          score += 2
        if 'barbershop_premium' in tags:         score += 2
        if 'luxury_service'    in tags:          score += 2
        if 'no_website'        in tags:          score += 1
        if lead.get('is_mobile'):                score += 1

        candidates.append({**lead, '_score': score, '_evidence': evidence, '_tags': tags})

    candidates.sort(key=lambda x: x['_score'], reverse=True)
    batch = candidates[:top_n]

    print(f'\nFiltered: {len(all_leads)} total → {len(candidates)} candidates '
          f'(skipped: already_batched={skipped_already} junk_email={skipped_junk_email} '
          f'chain={skipped_chain} empty={skipped_empty} no_evidence={skipped_no_evidence})')
    print(f'Batch size: {len(batch)}\n')

    # ── Print Sniper batch ────────────────────────────────────────────────────
    _MOBILE_DE = re.compile(r'\+49\s*1[5-7]|\b015\d|016\d|017\d')

    sep = '─' * 80
    for i, lead in enumerate(batch, 1):
        tags_str = ', '.join(lead['_tags']) if isinstance(lead['_tags'], list) else lead['_tags']

        phone = (lead.get('phone') or '').strip()
        email = (lead.get('email') or '').strip()
        has_mobile = bool(phone and _MOBILE_DE.search(phone))
        has_email  = bool(email)
        if has_mobile and has_email:
            output_needed = 'both'
        elif has_mobile:
            output_needed = 'whatsapp'
        elif has_email:
            output_needed = 'email'
        else:
            output_needed = '—'

        print(sep)
        print(f'#{i:>2}  [{lead["_score"]} pts]  ID={lead.get("id")}')
        print(f'  Name:          {lead.get("name")}')
        print(f'  City:          {lead.get("city")}')
        print(f'  Address:       {lead.get("district") or "—"}')
        print(f'  Category:      {lead.get("category") or "—"}')
        print(f'  Reviews:       {lead.get("reviews_count") or "?"} reviews on Google Maps')
        print(f'  Website:       {lead.get("website") or "—"}')
        print(f'  Phone:         {phone or "—"}')
        print(f'  Email:         {email or "—"}')
        print(f'  Platform:      {lead.get("platform") or "—"}')
        print(f'  Pain_tags:     {tags_str or "—"}')
        print(f'  Evidence:      {lead["_evidence"]}')
        print(f'  Output needed: {output_needed}')
    print(sep)
    print(f'\nTotal in batch: {len(batch)} leads ready for Sniper.')


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='Bavaria beauty lead harvester')
    ap.add_argument('--city',         default='',  help='Single city to harvest or filter')
    ap.add_argument('--limit',        type=int, default=0, help='Override limit for chosen city')
    ap.add_argument('--all',          action='store_true', help='Harvest all 5 Bavaria cities')
    ap.add_argument('--dry-run',      action='store_true', help='Simulate without writing to DB')
    ap.add_argument('--report',       action='store_true', help='Print report from existing DB data')
    ap.add_argument('--sniper-batch', action='store_true', help='Print Sniper pilot batch (top 20)')
    ap.add_argument('--top',          type=int, default=20, help='How many leads in Sniper batch')
    args = ap.parse_args()

    if args.report:
        print_db_report()
        return

    if args.sniper_batch:
        # Resolve optional city fuzzy-match
        city_filter = ''
        if args.city:
            matched = next(
                (c for c in BAVARIA_CITIES if c.lower() == args.city.lower() or
                 c.lower().replace('ü','u').replace('ö','o').replace('ä','a') == args.city.lower()),
                None
            )
            if not matched:
                print(f'[ERROR] Unknown city: {args.city}', file=sys.stderr); sys.exit(1)
            city_filter = matched
        sniper_pilot_batch(city=city_filter, top_n=args.top)
        return

    if not args.city and not args.all:
        ap.print_help()
        print('\nAvailable cities:', ', '.join(BAVARIA_CITIES.keys()))
        return

    cities_to_run = []
    if args.all:
        cities_to_run = list(BAVARIA_CITIES.items())  # [(name, cfg), ...]
    else:
        city = args.city
        # fuzzy match: allow "Nurnberg" → "Nürnberg" etc
        matched = next(
            (c for c in BAVARIA_CITIES if c.lower() == city.lower() or
             c.lower().replace('ü','u').replace('ö','o').replace('ä','a') == city.lower()),
            None
        )
        if not matched:
            print(f'[ERROR] Unknown city: {city}. Available: {", ".join(BAVARIA_CITIES)}',
                  file=sys.stderr)
            sys.exit(1)
        cities_to_run = [(matched, BAVARIA_CITIES[matched])]

    all_stats = []
    t0 = time.time()
    for city_name, cfg in cities_to_run:
        limit = args.limit or cfg['limit']
        stats = harvest_city(city_name, limit=limit, dry=args.dry_run)
        all_stats.append(stats)

    elapsed = time.time() - t0
    print(f'\nTotal time: {elapsed:.0f}s')
    print_report(all_stats)

    # Save report to file
    if not args.dry_run:
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        report_path = os.path.join(_ROOT, 'reports', f'bavaria_harvest_{ts}.txt')
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            cities_summary = ', '.join(c for c, _ in cities_to_run)
            f.write(f'Bavaria Harvest — {cities_summary}\n')
            f.write(f'Run at: {datetime.datetime.now().isoformat()}\n\n')
            for s in all_stats:
                f.write(f'{s["city"]}: total={s["total"]} email={s["with_email"]} '
                        f'mobile={s["mobile_phone"]} no_web={s["no_website"]}\n')
            f.write('\nTop 20 premium leads:\n')
            all_premium = []
            for s in all_stats:
                all_premium.extend(s.get('premium_leads', []))
            all_premium.sort(key=lambda x: x['score'], reverse=True)
            for i, p in enumerate(all_premium[:20], 1):
                f.write(f'{i:>3}. {p["name"]} ({p["city"]}) — '
                        f'⭐{p["rating"]} rev={p["reviews"]} '
                        f'email={"y" if p["email"] else "n"} '
                        f'tags={p["pain_tags"]}\n')
        print(f'\nReport saved: {report_path}')

if __name__ == '__main__':
    main()
