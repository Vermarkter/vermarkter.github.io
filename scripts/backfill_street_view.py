#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backfill_street_view.py — Backfill street_view_url for a specific batch_id.

Source: Google Street View Static API (location=name,city query).
Note: Place Photos API is IP-restricted; Street View Static works unrestricted.
Stores direct Street View Static URL in street_view_url column (Phase 1: CRM only).

Usage:
  python scripts/backfill_street_view.py --batch-id augsburg_wa_regen_01 --dry-run
  python scripts/backfill_street_view.py --batch-id augsburg_wa_regen_01 --apply
  python scripts/backfill_street_view.py --ids 5490,5491,5494 --dry-run
  python scripts/backfill_street_view.py --batch-id augsburg_wa_regen_01 --apply --force

Flags:
  --batch-id   Filter by batch_id in Supabase
  --ids        Comma-separated lead IDs (alternative to --batch-id)
  --dry-run    Default: show what would be written, no DB changes
  --apply      Actually write to Supabase (must be explicit)
  --force      Overwrite existing street_view_url (default: skip if not null)
  --threads    Parallel threads (default: 5)
  --size       Street View image size (default: 600x400)
"""

import sys, io, os, json, time, argparse, configparser
import urllib.request, urllib.parse, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ─────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _e(k):
    return (os.environ.get(k) or '').strip()
def _c(s, k):
    try:    return (_cfg.get(s, k) or '').strip()
    except: return ''

GOOGLE_KEY = _e('GOOGLE_MAPS_API_KEY') or _c('GOOGLE', 'maps_api_key')
SB_URL     = _e('SUPABASE_URL')        or _c('SUPABASE', 'url').rstrip('/')

def _valid_key(s):
    return s if (s and s.isascii() and s.startswith('eyJ') and len(s) > 80) else ''

SB_KEY = (_e('SUPABASE_KEY')
          or _valid_key(_c('SUPABASE', 'service_role_key'))
          or _valid_key(_c('SUPABASE', 'anon_key')))

if not GOOGLE_KEY:
    print('[ERROR] maps_api_key not found in config.ini [GOOGLE]', file=sys.stderr)
    sys.exit(1)
if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE URL/KEY not configured', file=sys.stderr)
    sys.exit(1)

_SB_R = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
_SB_W = {**_SB_R, 'Content-Type': 'application/json; charset=utf-8', 'Prefer': 'return=minimal'}

PAGE_SIZE = 1000

# ── Supabase helpers ───────────────────────────────────────────────────────────

def _http_get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8')


def _sb_get(path, params_dict):
    qs  = '&'.join(f"{k}={urllib.parse.quote(str(v), safe=':.,*()!-')}"
                   for k, v in params_dict.items())
    url = f"{SB_URL}/rest/v1/{path}?{qs}"
    return json.loads(_http_get(url, _SB_R))


def fetch_by_batch(batch_id):
    leads, offset = [], 0
    while True:
        page = _sb_get('beauty_leads', {
            'batch_id': f'eq.{batch_id}',
            'select':   'id,name,city,maps_url,street_view_url',
            'order':    'id.asc',
            'limit':    str(PAGE_SIZE),
            'offset':   str(offset),
        })
        leads.extend(page)
        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return leads


def fetch_by_ids(ids):
    id_str = ','.join(str(i) for i in sorted(ids))
    return _sb_get('beauty_leads', {
        'id':     f'in.({id_str})',
        'select': 'id,name,city,maps_url,street_view_url',
    })


def patch_lead(lead_id, sv_url):
    url     = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    payload = json.dumps({'street_view_url': sv_url}, ensure_ascii=False).encode('utf-8')
    req     = urllib.request.Request(url, data=payload, headers=_SB_W, method='PATCH')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                r.read()
                return 'ok'
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                return f'http_{e.code}'
        except Exception as ex:
            time.sleep(1)
            if attempt == 2:
                return f'err:{ex}'
    return 'timeout'


# ── Google Street View Static API ─────────────────────────────────────────────
# Note: Place Photos API is IP-restricted on this key.
# Street View Static works without IP restriction.
# URL includes API key — acceptable for Phase 1 (CRM preview only, not email).

SV_SIZE = '600x400'


def build_sv_url(name, city, size=None):
    location = f'{name}, {city}'
    return (
        'https://maps.googleapis.com/maps/api/streetview'
        f'?size={size or SV_SIZE}'
        f'&location={urllib.parse.quote(location)}'
        '&source=outdoor'
        f'&key={GOOGLE_KEY}'
    )


def check_sv_url(sv_url):
    """Returns True if the URL returns a real JPEG (not a generic 'no image' tile)."""
    for attempt in range(3):
        try:
            req = urllib.request.Request(sv_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as r:
                ctype = r.headers.get('Content-Type', '')
                header = r.read(3)
            # JPEG magic bytes: FF D8 FF
            return 'image' in ctype and header == b'\xff\xd8\xff'
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                return False
        except Exception:
            time.sleep(1)
    return False


def process_lead(lead, size=None):
    lead_id = lead['id']
    name    = (lead.get('name') or '').strip()
    city    = (lead.get('city') or '').strip()

    if not name or not city:
        return lead_id, None, 'no_name_city'

    sv_url = build_sv_url(name, city, size)
    if check_sv_url(sv_url):
        return lead_id, sv_url, 'ok'
    return lead_id, None, 'no_photo'


# ── Main ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Backfill street_view_url by batch_id or IDs')
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--batch-id', help='batch_id to process')
    grp.add_argument('--ids',      help='Comma-separated lead IDs')
    p.add_argument('--dry-run', action='store_true', default=True,
                   help='Do not write to DB (default: True)')
    p.add_argument('--apply',   action='store_true',
                   help='Write results to Supabase (overrides --dry-run)')
    p.add_argument('--force',   action='store_true',
                   help='Overwrite existing street_view_url (default: skip)')
    p.add_argument('--threads', type=int, default=5,
                   help='Parallel threads (default: 5)')
    p.add_argument('--size',    default='600x400',
                   help='Street View image size (default: 600x400)')
    return p.parse_args()


def main():
    args    = parse_args()
    dry     = not args.apply
    ids_set = {int(x.strip()) for x in args.ids.split(',') if x.strip()} if args.ids else set()
    global SV_SIZE
    SV_SIZE = args.size

    print(f'\n{"="*68}')
    print(f'  Street View Backfill  |  {"DRY-RUN (no DB writes)" if dry else "LIVE — writing to DB"}')
    if args.batch_id:
        print(f'  Batch: {args.batch_id}')
    else:
        print(f'  IDs: {sorted(ids_set)}')
    print(f'  force={args.force}  threads={args.threads}')
    print(f'{"="*68}\n')

    # ── Fetch ─────────────────────────────────────────────────────────────────
    print('  Fetching leads from Supabase...')
    if ids_set:
        all_leads = fetch_by_ids(ids_set)
    else:
        all_leads = fetch_by_batch(args.batch_id)
    print(f'  Fetched: {len(all_leads)} leads\n')

    if not all_leads:
        print('  No leads found. Check batch_id or IDs.')
        return

    # ── Split: process vs skip ────────────────────────────────────────────────
    to_process, skipped = [], []
    for lead in all_leads:
        existing = lead.get('street_view_url')
        if existing and existing != 'none' and not args.force:
            skipped.append(lead)
        else:
            to_process.append(lead)

    no_name = [l for l in to_process if not (l.get('name') and l.get('city'))]
    has_name = [l for l in to_process if l.get('name') and l.get('city')]

    print(f'  Total         : {len(all_leads)}')
    print(f'  Skipped (existing sv_url, no --force) : {len(skipped)}')
    print(f'  Skipped (no name/city)                : {len(no_name)}')
    print(f'  To process                            : {len(has_name)}')
    print()

    if not has_name:
        print('  Nothing to process — all leads already have street_view_url or are missing name/city.')
        return

    # ── Process ───────────────────────────────────────────────────────────────
    results  = []   # (lead_id, name, photo_url_or_none, code)
    stats    = {'ok': 0, 'no_photo': 0, 'no_place': 0, 'error': 0}

    with ThreadPoolExecutor(max_workers=args.threads, thread_name_prefix='sv') as pool:
        futures = {pool.submit(process_lead, lead, args.size): lead for lead in has_name}
        total   = len(futures)

        for i, future in enumerate(as_completed(futures), 1):
            lead = futures[future]
            name = lead.get('name', f"id={lead['id']}")
            try:
                lead_id, photo_url, code = future.result()
            except Exception as exc:
                lead_id, photo_url, code = lead['id'], None, 'error'
                print(f'  [ERR] id={lead_id}: {exc}')

            stats[code] = stats.get(code, 0) + 1
            results.append((lead_id, name, photo_url, code))

            icon = {'ok': 'OK', 'no_photo': '--', 'no_place': 'XX', 'error': '!!'}[code]
            url_preview = (photo_url[:70] + '...') if photo_url else 'none'
            print(f'  [{i:>3}/{total}] [{icon}] id={lead_id} {name[:35]:<35} {url_preview}')

    # ── Write to DB ───────────────────────────────────────────────────────────
    ok_results = [(lid, url) for lid, name, url, code in results if code == 'ok']

    if not dry and ok_results:
        print(f'\n  Writing {len(ok_results)} URLs to Supabase...')
        write_ok, write_err = 0, 0
        for lead_id, photo_url in ok_results:
            r = patch_lead(lead_id, photo_url)
            if r == 'ok':
                write_ok += 1
            else:
                write_err += 1
                print(f'  [PATCH ERR] id={lead_id}: {r}')
        print(f'  Wrote: {write_ok}/{len(ok_results)}  Errors: {write_err}')

    # ── Report ────────────────────────────────────────────────────────────────
    print(f'\n{"="*68}')
    print(f'  REPORT{"  (DRY-RUN — nothing written)" if dry else ""}')
    print(f'{"="*68}')
    print(f'  Total leads in batch    : {len(all_leads)}')
    print(f'  Already had sv_url      : {len(skipped)}')
    print(f'  No name/city            : {len(no_name)}')
    print(f'  Processed               : {len(has_name)}')
    print(f'    Found photo (ok)      : {stats.get("ok", 0)}')
    print(f'    No Street View photo  : {stats.get("no_photo", 0)}')
    print(f'    No name/city          : {stats.get("no_name_city", 0)}')
    print(f'    Errors                : {stats.get("error", 0)}')
    print()

    found_urls = [(lid, name, url) for lid, name, url, code in results if code == 'ok']
    if found_urls:
        print(f'  Preview — first {min(5, len(found_urls))} found URLs:')
        for lid, name, url in found_urls[:5]:
            # Truncate the key in display
            disp = url
            if 'key=' in disp:
                disp = disp[:disp.index('key=')] + 'key=***'
            print(f'    id={lid} {name[:30]:<30} {disp[:80]}')
    else:
        print('  No Street View photos found.')

    if no_name:
        print(f'\n  Leads without name/city (cannot query Street View):')
        for lead in no_name:
            print(f'    id={lead["id"]} {lead.get("name","")[:40]}')

    print()
    if dry:
        print('  DRY-RUN complete. To write to DB: add --apply')
    else:
        print('  APPLY complete.')
    print(f'{"="*68}\n')


if __name__ == '__main__':
    main()
