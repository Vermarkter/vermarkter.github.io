#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_street_view.py — Fetches Google Street View facade photos for beauty leads.

For each lead with a maps_url (Google Maps link), resolves coordinates via
Places/Geocoding API, checks Street View metadata for coverage, and if
available stores the static Street View image URL in street_view_url column.
Sets null if Street View is unavailable.

Usage:
  python scripts/enrich_street_view.py
  python scripts/enrich_street_view.py --city Berlin --limit 50
  python scripts/enrich_street_view.py --ids 260,261,262 --dry-run

Requirements:
  config.ini [GOOGLE] maps_api_key
  SUPABASE_URL / SUPABASE_KEY in env or config.ini [SUPABASE]
  Street View Static API must be enabled in Google Cloud Console
  (same key as Maps — enable at: console.cloud.google.com → APIs → Street View Static API)
"""

import sys, io, os, re, json, time, argparse, configparser, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _env(key):
    return (os.environ.get(key) or '').strip()

def _cfg_get(section, key):
    try:    return _cfg.get(section, key).strip()
    except: return ''

GOOGLE_KEY = _env('GOOGLE_MAPS_API_KEY') or _cfg_get('GOOGLE', 'maps_api_key')
SB_URL     = _env('SUPABASE_URL')        or _cfg_get('SUPABASE', 'url')
SB_KEY     = _env('SUPABASE_KEY')        or _cfg_get('SUPABASE', 'service_role_key') or _cfg_get('SUPABASE', 'anon_key')

if not GOOGLE_KEY:
    print('[ERROR] GOOGLE_MAPS_API_KEY not configured.', file=sys.stderr)
    sys.exit(1)
if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE_URL / SUPABASE_KEY not configured.', file=sys.stderr)
    sys.exit(1)

# Street View Static API parameters
SV_WIDTH  = 600
SV_HEIGHT = 400
SV_FOV    = 90    # field of view degrees
SV_PITCH  = 5     # slight upward tilt for facade shots

# ── Supabase helpers ──────────────────────────────────────────────────────────

SB_HEADERS_READ = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
}
SB_HEADERS_PATCH = {
    **SB_HEADERS_READ,
    'Content-Type': 'application/json; charset=utf-8',
    'Prefer':       'return=minimal',
}


def sb_get(path: str, params: dict = None) -> list:
    url = f"{SB_URL}/rest/v1/{path}"
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=SB_HEADERS_READ)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch(lead_id: int, payload: dict) -> str:
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=SB_HEADERS_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 'OK' if r.status in (200, 204) else f'ERR {r.status}'
    except urllib.request.HTTPError as e:
        return f'ERR {e.code}: {e.read().decode("utf-8", errors="replace")[:120]}'


# ── Google helpers ────────────────────────────────────────────────────────────

def _google_get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read().decode('utf-8'))


def extract_place_id(maps_url: str) -> str | None:
    """Extract place_id from a Google Maps URL if present."""
    m = re.search(r'place_id[=:]([A-Za-z0-9_-]+)', maps_url or '')
    return m.group(1) if m else None


def extract_cid(maps_url: str) -> str | None:
    """Extract CID (numeric) from ?cid= param."""
    m = re.search(r'[?&]cid=(\d+)', maps_url or '')
    return m.group(1) if m else None


def resolve_latlng_from_place_id(place_id: str) -> tuple[float, float] | None:
    url = (
        'https://maps.googleapis.com/maps/api/place/details/json'
        f'?place_id={urllib.parse.quote(place_id)}'
        f'&fields=geometry'
        f'&key={GOOGLE_KEY}'
    )
    data = _google_get(url)
    if data.get('status') != 'OK':
        return None
    loc = data['result']['geometry']['location']
    return loc['lat'], loc['lng']


def resolve_latlng_from_address(address: str) -> tuple[float, float] | None:
    url = (
        'https://maps.googleapis.com/maps/api/geocode/json'
        f'?address={urllib.parse.quote(address)}'
        f'&key={GOOGLE_KEY}'
    )
    data = _google_get(url)
    if data.get('status') != 'OK' or not data.get('results'):
        return None
    loc = data['results'][0]['geometry']['location']
    return loc['lat'], loc['lng']


def resolve_latlng(lead: dict) -> tuple[float, float] | None:
    """Try place_id → CID lookup → address geocode."""
    maps_url = lead.get('maps_url') or ''

    place_id = extract_place_id(maps_url)
    if place_id:
        coords = resolve_latlng_from_place_id(place_id)
        if coords:
            return coords

    # Fallback: geocode by address
    addr = lead.get('addr') or lead.get('address') or ''
    city = lead.get('city') or 'Berlin'
    if addr:
        full_addr = addr if city.lower() in addr.lower() else f'{addr}, {city}'
        coords = resolve_latlng_from_address(full_addr)
        if coords:
            return coords

    return None


def check_street_view_available(lat: float, lng: float) -> bool:
    """
    Calls Street View Metadata API to confirm coverage exists.
    Returns False if status != 'OK' (i.e. no panorama nearby).
    Free endpoint — does not count toward Static API quota.
    """
    url = (
        'https://maps.googleapis.com/maps/api/streetview/metadata'
        f'?location={lat},{lng}'
        f'&radius=50'
        f'&key={GOOGLE_KEY}'
    )
    try:
        data = _google_get(url)
        return data.get('status') == 'OK'
    except Exception:
        return False


def build_street_view_url(lat: float, lng: float) -> str:
    """Builds the static Street View image URL (counts toward billing)."""
    params = urllib.parse.urlencode({
        'size':     f'{SV_WIDTH}x{SV_HEIGHT}',
        'location': f'{lat},{lng}',
        'fov':      SV_FOV,
        'pitch':    SV_PITCH,
        'source':   'outdoor',   # prefer outdoor panoramas (not indoor 360)
        'key':      GOOGLE_KEY,
    })
    return f'https://maps.googleapis.com/maps/api/streetview?{params}'


# ── Main logic ────────────────────────────────────────────────────────────────

def enrich_lead(lead: dict, dry: bool) -> dict:
    name = lead.get('name', f"id={lead['id']}")
    print(f"  [{lead['id']}] {name}")

    coords = resolve_latlng(lead)
    if not coords:
        print(f"         → coords: NOT FOUND (no maps_url / geocode failed)")
        return {'id': lead['id'], 'result': 'no_coords', 'url': None}

    lat, lng = coords
    print(f"         → coords: {lat:.5f}, {lng:.5f}")

    available = check_street_view_available(lat, lng)
    if not available:
        print(f"         → Street View: UNAVAILABLE — setting null")
        if not dry:
            sb_patch(lead['id'], {'street_view_url': None})
        return {'id': lead['id'], 'result': 'no_coverage', 'url': None}

    sv_url = build_street_view_url(lat, lng)
    print(f"         → Street View: OK")

    if dry:
        print(f"         → [DRY] would save URL to DB")
    else:
        result = sb_patch(lead['id'], {'street_view_url': sv_url})
        print(f"         → DB patch: {result}")

    return {'id': lead['id'], 'result': 'ok', 'url': sv_url}


def fetch_leads(city: str, limit: int, offset: int, ids: set) -> list:
    if ids:
        id_list = ','.join(str(i) for i in sorted(ids))
        return sb_get('beauty_leads', {
            'id':     f'in.({id_list})',
            'select': 'id,name,addr,city,maps_url',
        })

    params = {
        'select': 'id,name,addr,city,maps_url',
        'order':  'id.asc',
    }
    if city:
        params['city'] = f'eq.{city}'
    if limit:
        params['limit']  = str(limit)
        params['offset'] = str(offset)
    return sb_get('beauty_leads', params)


def parse_args():
    p = argparse.ArgumentParser(description='Enrich beauty_leads with Street View facade photos')
    p.add_argument('--city',    default='Berlin', help='City filter (default: Berlin)')
    p.add_argument('--limit',   type=int, default=100, help='Max leads (default: 100)')
    p.add_argument('--offset',  type=int, default=0,   help='Supabase offset (default: 0)')
    p.add_argument('--ids',     default='',            help='Comma-separated lead IDs')
    p.add_argument('--dry-run', action='store_true',   help='No DB writes, print URLs only')
    p.add_argument('--delay',   type=float, default=0.5, help='Seconds between requests (default: 0.5)')
    p.add_argument('--skip-existing', action='store_true',
                   help='Skip leads that already have street_view_url set')
    return p.parse_args()


def main():
    args  = parse_args()
    dry   = args.dry_run
    ids   = {int(x.strip()) for x in args.ids.split(',') if x.strip()} if args.ids else set()

    print(f'\n{"="*60}')
    print(f'  Street View Enricher  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  City: {args.city}  |  Limit: {args.limit}  |  Offset: {args.offset}')
    if ids:
        print(f'  ID filter: {sorted(ids)}')
    print(f'{"="*60}\n')

    leads = fetch_leads(args.city, args.limit, args.offset, ids)
    print(f'  Fetched {len(leads)} leads\n')

    if args.skip_existing:
        leads = [l for l in leads if not l.get('street_view_url')]
        print(f'  After skip-existing filter: {len(leads)} leads\n')

    stats = {'ok': 0, 'no_coverage': 0, 'no_coords': 0, 'total': len(leads)}

    for lead in leads:
        r = enrich_lead(lead, dry)
        stats[r['result']] = stats.get(r['result'], 0) + 1
        time.sleep(args.delay)

    print(f'\n{"="*60}')
    print(f'  DONE — total={stats["total"]} | ok={stats.get("ok",0)} | '
          f'no_coverage={stats.get("no_coverage",0)} | no_coords={stats.get("no_coords",0)}')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*60}\n')


if __name__ == '__main__':
    main()
