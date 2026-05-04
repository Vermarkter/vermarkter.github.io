#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch_reviews.py — Munich Intelligence Package builder.

For each Munich 'new' lead:
  1. Fetch place_id via Google Places Text Search
  2. Fetch up to 5 reviews via Place Details
  3. Extract pain quote (booking/wait/language complaints)
  4. Find nearest competitor with higher rating (300-500m radius)

Output: data/munich_intelligence_100.json

Usage:
  python scripts/fetch_reviews.py
  python scripts/fetch_reviews.py --limit 10   # test with 10 leads
  python scripts/fetch_reviews.py --limit 100  # full run
"""

import sys, io, os, json, argparse, configparser, time, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Config ────────────────────────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL  = _cfg['SUPABASE']['url'].strip()
_svc    = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY  = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
          else _cfg['SUPABASE']['anon_key'].strip()
MAPS_KEY = _cfg['GOOGLE']['maps_api_key'].strip()

SB_HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}

# ── Pain signal keywords ──────────────────────────────────────────────────────
PAIN_KEYWORDS = [
    # Booking / appointment
    'termin', 'booking', 'buchen', 'buchung', 'reservier', 'appointment',
    'online', 'telefon', 'anruf', 'erreichbar', 'call',
    # Wait / time
    'warten', 'wartezeit', 'wait', 'lange', 'stunde', 'minuten',
    # Language
    'sprache', 'deutsch', 'language', 'verständigung', 'kommunikation',
    'verstehen', 'englisch', 'türkisch', 'arabisch',
    # Service quality complaints
    'unfreundlich', 'ignoriert', 'niemand', 'nicht reagiert', 'no response',
    'disappointed', 'enttäuscht', 'schlecht', 'horrible', 'awful',
]

PAIN_NEG_SIGNALS = [
    'warten', 'wartezeit', 'termin', 'nicht erreichbar', 'kein online',
    'keine buchung', 'lange', 'ignoriert', 'niemand', 'schlecht',
    'enttäuscht', 'unfreundlich', 'nicht reagiert',
]

def is_pain_review(text: str) -> bool:
    t = text.lower()
    # Must have at least one negative signal — pure keyword presence is not enough
    has_neg = any(neg in t for neg in [
        'nicht', 'kein', 'keine', 'no ', 'never', 'nie ', 'niemals',
        'schlecht', 'problem', 'leider', 'unfortunately', 'enttäuscht',
        'schade', 'traurig', 'worst', 'horrible', 'awful', 'terrible',
        '1 stern', '2 stern', '1 star', '2 star', 'unfreundlich',
        'nicht reagiert', 'ignoriert', 'niemand', 'unerreichbar',
    ])
    if not has_neg:
        return False
    return any(kw in t for kw in PAIN_NEG_SIGNALS + PAIN_KEYWORDS)

def extract_pain_quote(reviews: list) -> str | None:
    """Return best pain quote (≤200 chars) or None. Must be genuinely negative."""
    candidates = []
    for r in reviews:
        text   = (r.get('text') or '').strip()
        rating = r.get('rating', 5)
        if not text:
            continue
        # Only consider reviews that are low-rated AND/OR contain actual pain signal
        if rating <= 3 and is_pain_review(text):
            candidates.append((rating, text))
        elif rating <= 2:
            candidates.append((rating, text))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0])  # worst rating first
    best = candidates[0][1]
    # Truncate to 200 chars at word boundary
    if len(best) > 200:
        best = best[:197].rsplit(' ', 1)[0] + '…'
    return best

# ── Google API helpers ────────────────────────────────────────────────────────
BASE = 'https://maps.googleapis.com/maps/api'

def gmaps_get(endpoint: str, params: dict) -> dict:
    params['key'] = MAPS_KEY
    url = f"{BASE}/{endpoint}/json?" + urllib.parse.urlencode(params, safe='')
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'status': 'REQUEST_ERROR', 'error': str(e)}

def find_place_id(name: str, city: str = 'München') -> tuple[str | None, dict | None]:
    """Returns (place_id, basic_info_dict) or (None, None)."""
    query = f"{name} {city}"
    data = gmaps_get('place/findplacefromtext', {
        'input': query,
        'inputtype': 'textquery',
        'fields': 'place_id,name,rating,geometry,formatted_address',
        'locationbias': 'circle:20000@48.1351,11.5820',  # Munich center
    })
    if data.get('status') != 'OK':
        return None, None
    candidates = data.get('candidates', [])
    if not candidates:
        return None, None
    c = candidates[0]
    return c.get('place_id'), c

def get_place_details(place_id: str) -> dict:
    """Returns full place details including reviews."""
    data = gmaps_get('place/details', {
        'place_id': place_id,
        'fields': 'name,rating,user_ratings_total,reviews,geometry,formatted_address,website',
        'language': 'de',
        'reviews_sort': 'newest',
    })
    if data.get('status') != 'OK':
        return {}
    return data.get('result', {})

def find_better_competitor(lat: float, lng: float, our_rating: float) -> dict | None:
    """Find nearest salon with higher rating within 500m."""
    data = gmaps_get('place/nearbysearch', {
        'location': f'{lat},{lng}',
        'radius': 500,
        'type': 'beauty_salon|hair_care|barber',
        'rankby': 'prominence',
    })
    if data.get('status') not in ('OK', 'ZERO_RESULTS'):
        return None

    best = None
    best_dist = float('inf')

    for p in data.get('results', []):
        r = p.get('rating', 0)
        if r <= our_rating:
            continue
        # Rough distance calc (Euclidean in degrees — good enough for 500m)
        plat = p['geometry']['location']['lat']
        plng = p['geometry']['location']['lng']
        dist = ((plat - lat)**2 + (plng - lng)**2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best = {
                'name':   p.get('name', ''),
                'rating': r,
                'address': p.get('vicinity', ''),
            }
    return best

# ── Supabase fetch ─────────────────────────────────────────────────────────────
def fetch_munich_leads(limit: int) -> list:
    fields = 'id,name,city,website,maps_url,phone,notes'
    url = (f"{SB_URL}/rest/v1/beauty_leads"
           f"?select={fields}"
           f"&city=eq.M%C3%BCnchen"
           f"&status=eq.new"
           f"&order=id.asc"
           f"&limit={limit}")
    req = urllib.request.Request(url, headers=SB_HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

# ── Main ──────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Munich Intelligence Package builder')
    p.add_argument('--limit', type=int, default=100, help='Max leads to process (default: 100)')
    p.add_argument('--out',   default='data/munich_intelligence_100.json')
    p.add_argument('--delay', type=float, default=0.15,
                   help='Seconds between Google API calls (default: 0.15)')
    return p.parse_args()

def main():
    args    = parse_args()
    out_path = args.out if os.path.isabs(args.out) else os.path.join(_ROOT, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    print(f'\n{"="*64}')
    print(f'  Munich Intelligence Package  |  limit={args.limit}')
    print(f'  Output: {out_path}')
    print(f'{"="*64}\n')

    print('Fetching Munich leads from Supabase...')
    leads = fetch_munich_leads(args.limit)
    print(f'Got {len(leads)} leads.\n')

    results = []
    ok = skipped = 0

    for i, lead in enumerate(leads, 1):
        name    = lead['name']
        lead_id = lead['id']
        print(f'  [{i:3d}/{len(leads)}] ID={lead_id} — {name[:50]}')

        record = {
            'id':               lead_id,
            'name':             name,
            'website':          lead.get('website') or None,
            'maps_url':         lead.get('maps_url') or None,
            'pain_quote':       None,
            'pain_rating':      None,
            'competitor_name':  None,
            'competitor_rating': None,
            'competitor_address': None,
            'our_rating':       None,
            'place_id':         None,
            'address':          None,
            '_status':          'ok',
        }

        # Step 1 — find place_id
        place_id, basic = find_place_id(name)
        time.sleep(args.delay)

        if not place_id:
            print(f'           place_id: NOT FOUND')
            record['_status'] = 'no_place_id'
            results.append(record)
            skipped += 1
            continue

        record['place_id'] = place_id

        # Step 2 — get full details + reviews
        details = get_place_details(place_id)
        time.sleep(args.delay)

        our_rating = details.get('rating')
        record['our_rating'] = our_rating
        record['address']    = details.get('formatted_address')

        reviews = details.get('reviews', [])
        pain_q  = extract_pain_quote(reviews)
        if pain_q:
            record['pain_quote']  = pain_q
            # find the rating of the review we picked
            for rv in reviews:
                if pain_q[:40] in (rv.get('text') or ''):
                    record['pain_rating'] = rv.get('rating')
                    break

        print(f'           place_id: {place_id}  rating={our_rating}  '
              f'reviews={len(reviews)}  pain={"YES" if pain_q else "no"}')

        # Step 3 — find better competitor
        loc = details.get('geometry', {}).get('location', {})
        lat, lng = loc.get('lat'), loc.get('lng')

        if lat and lng and our_rating is not None:
            comp = find_better_competitor(lat, lng, our_rating)
            time.sleep(args.delay)
            if comp:
                record['competitor_name']    = comp['name']
                record['competitor_rating']  = comp['rating']
                record['competitor_address'] = comp['address']
                print(f'           competitor: {comp["name"]} ({comp["rating"]}★)')
            else:
                print(f'           competitor: none better found')
        else:
            print(f'           competitor: skipped (no coords or rating)')

        results.append(record)
        ok += 1

    # Save
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f'\n{"="*64}')
    print(f'  DONE')
    print(f'  Processed: {ok}   Skipped (no place_id): {skipped}')
    print(f'  Pain quotes found: {sum(1 for r in results if r["pain_quote"])}')
    print(f'  Competitors found: {sum(1 for r in results if r["competitor_name"])}')
    print(f'  Saved: {out_path}')
    print(f'{"="*64}')

    # Print first 10 records summary
    print(f'\n--- Preview: first 10 records ---\n')
    for r in results[:10]:
        print(f'  ID {r["id"]:5d} | {r["name"][:40]:<40} | {r["our_rating"] or "?"} ★')
        if r['pain_quote']:
            print(f'          PAIN: "{r["pain_quote"][:120]}"')
        if r['competitor_name']:
            print(f'          COMP: {r["competitor_name"]} ({r["competitor_rating"]}★)')
        if r['_status'] != 'ok':
            print(f'          STATUS: {r["_status"]}')
        print()


if __name__ == '__main__':
    main()
