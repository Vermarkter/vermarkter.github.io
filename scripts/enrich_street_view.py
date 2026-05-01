#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_street_view.py — Enriches beauty_leads with facade/salon photos.

Source: Google Place Photos API (photo_reference from place_id in maps_url).
Falls back to null if place has no photos.
Stores permanent lh3.googleusercontent.com URL in street_view_url column.

Features:
  - 10 parallel threads for speed (1710 Berlin + 380 München ≈ 30 min)
  - Paginated Supabase fetch (1000/page)
  - Resume support: skips leads already processed (street_view_url IS NOT NULL or = 'none')
  - Batch PATCH to Supabase (50 leads per request)
  - Progress saved to data/sv_progress.json every 50 leads
  - Graceful Ctrl+C: saves progress before exit

Usage:
  python scripts/enrich_street_view.py                     # all Berlin + München READY TO SEND
  python scripts/enrich_street_view.py --city Berlin       # Berlin only
  python scripts/enrich_street_view.py --ids 162,163,165   # specific IDs
  python scripts/enrich_street_view.py --dry-run           # no DB writes
  python scripts/enrich_street_view.py --threads 5         # fewer threads

Config: config.ini [GOOGLE] maps_api_key + [SUPABASE] url / anon_key
"""

import sys, io, os, re, json, time, argparse, configparser
import urllib.request, urllib.parse, urllib.error
import threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ─────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _e(k):  return (os.environ.get(k) or '').strip()
def _c(s, k):
    try:    return (_cfg.get(s, k) or '').strip()
    except: return ''

GOOGLE_KEY = _e('GOOGLE_MAPS_API_KEY') or _c('GOOGLE', 'maps_api_key')
SB_URL     = _e('SUPABASE_URL')        or _c('SUPABASE', 'url')

def _valid_key(s):
    """Returns s only if it looks like a real JWT/API key (ASCII, starts with eyJ, len>80)."""
    return s if (s and s.isascii() and s.startswith('eyJ') and len(s) > 80) else ''

SB_KEY = (_e('SUPABASE_KEY')
          or _valid_key(_c('SUPABASE', 'service_role_key'))
          or _valid_key(_c('SUPABASE', 'anon_key')))

if not GOOGLE_KEY:
    print('[ERROR] maps_api_key not in config.ini [GOOGLE]', file=sys.stderr); sys.exit(1)
if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE_URL/KEY not configured', file=sys.stderr); sys.exit(1)

PROGRESS_FILE = os.path.join(_ROOT, 'data', 'sv_progress.json')
CITIES        = ['Berlin', 'München']
BATCH_SIZE    = 50    # leads per Supabase PATCH batch
PAGE_SIZE     = 1000  # leads per Supabase GET page

# ── Thread-safe counters ───────────────────────────────────────────────────────
_lock    = threading.Lock()
_stats   = {'ok': 0, 'no_photo': 0, 'no_place': 0, 'error': 0, 'total': 0}
_pending = []   # (lead_id, street_view_url | None) collected for batch write

def _inc(key):
    with _lock:
        _stats[key] = _stats.get(key, 0) + 1
        _stats['total'] += 1

def _log(msg, end='\n'):
    with _lock:
        print(msg, end=end, flush=True)

# ── Supabase ───────────────────────────────────────────────────────────────────
# All header values must be ASCII — SB_KEY is always a JWT (ASCII-safe)
_SB_R = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
_SB_W = {**_SB_R, 'Content-Type': 'application/json; charset=utf-8', 'Prefer': 'return=minimal'}


def _http_get(url, headers=None, timeout=20):
    # urllib requires header values to be latin-1 encodable.
    # All our headers (JWT tokens, content-type) are ASCII-safe — no issue.
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8')


def _sb_get(path, params_dict):
    """GET from Supabase. Handles non-ASCII param values (e.g. München) via percent-encoding."""
    # Build query string with percent-encoding so ü → %C3%BC (HTTP-safe)
    qs  = '&'.join(f"{k}={urllib.parse.quote(str(v), safe=':.,*()!-')}"
                   for k, v in params_dict.items())
    url = f"{SB_URL}/rest/v1/{path}?{qs}"
    return json.loads(_http_get(url, _SB_R))


def sb_fetch_page(city, offset):
    """Fetch one page of READY TO SEND leads for a city."""
    return _sb_get('beauty_leads', {
        'status': 'eq.READY TO SEND',
        'city':   f'eq.{city}',
        'select': 'id,name,maps_url,street_view_url',
        'order':  'id.asc',
        'limit':  str(PAGE_SIZE),
        'offset': str(offset),
    })


def sb_fetch_by_ids(ids):
    id_str = ','.join(str(i) for i in sorted(ids))
    return _sb_get('beauty_leads', {
        'id':     f'in.({id_str})',
        'select': 'id,name,maps_url,street_view_url',
    })


def sb_patch_batch(batch: list[tuple[int, str | None]], dry: bool):
    """
    batch: list of (lead_id, url_or_none)
    Uses individual PATCH per lead (PostgREST doesn't support bulk PATCH with different values).
    Runs in parallel via threads for speed.
    """
    if dry:
        return

    def _do_patch(lead_id, sv_url):
        url     = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
        payload = json.dumps({'street_view_url': sv_url}, ensure_ascii=False).encode('utf-8')
        req     = urllib.request.Request(url, data=payload, headers=_SB_W, method='PATCH')
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=15) as r:
                    return 'ok'
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(2 ** attempt)
                else:
                    return f'err {e.code}'
            except Exception:
                time.sleep(1)
        return 'timeout'

    with ThreadPoolExecutor(max_workers=10) as pool:
        futs = {pool.submit(_do_patch, lid, url): lid for lid, url in batch}
        errs = [futs[f] for f in as_completed(futs) if f.result() != 'ok']
    if errs:
        _log(f'  [WARN] {len(errs)} PATCH errors for IDs: {errs[:10]}')


# ── Google Place Photos ────────────────────────────────────────────────────────

def _place_id_from_url(maps_url: str) -> str | None:
    """Extracts query_place_id=... or place_id=... from maps_url."""
    if not maps_url:
        return None
    m = re.search(r'query_place_id=([A-Za-z0-9_-]+)', maps_url)
    if m: return m.group(1)
    m = re.search(r'place_id[=:]([A-Za-z0-9_-]+)', maps_url)
    if m: return m.group(1)
    return None


def _get_photo_reference(place_id: str) -> str | None:
    """
    Fetches Place Details for photos field.
    Returns first photo_reference or None.
    """
    url = (
        'https://maps.googleapis.com/maps/api/place/details/json'
        f'?place_id={urllib.parse.quote(place_id)}'
        '&fields=photos'
        f'&key={GOOGLE_KEY}'
    )
    for attempt in range(3):
        try:
            raw  = _http_get(url, timeout=15)
            data = json.loads(raw)
            if data.get('status') != 'OK':
                return None
            photos = data.get('result', {}).get('photos', [])
            if not photos:
                return None
            # Prefer exterior photos: sort by width desc (wider = likely exterior shot)
            photos.sort(key=lambda p: p.get('width', 0), reverse=True)
            return photos[0]['photo_reference']
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                return None
        except Exception:
            time.sleep(1)
    return None


def _resolve_photo_url(photo_ref: str) -> str | None:
    """
    Calls Place Photo endpoint, follows redirect, returns final lh3.googleusercontent.com URL.
    The redirect URL is stable and doesn't require the API key on every email load.
    """
    url = (
        'https://maps.googleapis.com/maps/api/place/photo'
        f'?maxwidth=600&photo_reference={urllib.parse.quote(photo_ref)}&key={GOOGLE_KEY}'
    )
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                final = r.geturl()
                ctype = r.headers.get('Content-Type', '')
                if 'image' in ctype and 'googleusercontent.com' in final:
                    return final
                return None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                return None
        except Exception:
            time.sleep(1)
    return None


# ── Worker ─────────────────────────────────────────────────────────────────────

def process_lead(lead: dict) -> tuple[int, str | None, str]:
    """
    Returns (lead_id, photo_url_or_none, result_code).
    result_code: 'ok' | 'no_photo' | 'no_place' | 'error'
    """
    lead_id  = lead['id']
    name     = lead.get('name', f'id={lead_id}')
    maps_url = lead.get('maps_url') or ''

    place_id = _place_id_from_url(maps_url)
    if not place_id:
        return lead_id, None, 'no_place'

    photo_ref = _get_photo_reference(place_id)
    if not photo_ref:
        return lead_id, None, 'no_photo'

    photo_url = _resolve_photo_url(photo_ref)
    if not photo_url:
        return lead_id, None, 'no_photo'

    return lead_id, photo_url, 'ok'


# ── Progress persistence ───────────────────────────────────────────────────────

def load_progress() -> set:
    """Returns set of already-processed lead IDs."""
    try:
        with open(PROGRESS_FILE, encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('done', []))
    except FileNotFoundError:
        return set()


def save_progress(done: set):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'done':       sorted(done),
            'count':      len(done),
            'updated_at': datetime.now(timezone.utc).isoformat(),
        }, f, indent=2)


# ── Main ───────────────────────────────────────────────────────────────────────

def fetch_all_leads(cities: list[str], ids: set) -> list:
    if ids:
        return sb_fetch_by_ids(ids)

    leads = []
    for city in cities:
        offset = 0
        while True:
            page = sb_fetch_page(city, offset)
            leads.extend(page)
            _log(f'  Fetched {len(page)} from {city} (offset {offset}) — total so far: {len(leads)}')
            if len(page) < PAGE_SIZE:
                break
            offset += PAGE_SIZE
    return leads


def parse_args():
    p = argparse.ArgumentParser(description='Enrich beauty_leads with facade photos (Place Photos API)')
    p.add_argument('--city',    default='',  help='Single city (default: Berlin + München)')
    p.add_argument('--ids',     default='',  help='Comma-separated lead IDs')
    p.add_argument('--threads', type=int, default=10, help='Parallel threads (default: 10)')
    p.add_argument('--delay',   type=float, default=0.1, help='Delay between API calls per thread (default: 0.1)')
    p.add_argument('--dry-run', action='store_true', help='No DB writes')
    p.add_argument('--resume',  action='store_true', help='Skip IDs in data/sv_progress.json')
    p.add_argument('--reset',   action='store_true', help='Delete progress file and start fresh')
    return p.parse_args()


def main():
    args    = parse_args()
    dry     = args.dry_run
    ids     = {int(x.strip()) for x in args.ids.split(',') if x.strip()} if args.ids else set()
    cities  = [args.city] if args.city else CITIES

    print(f'\n{"="*64}')
    print(f'  Facade Photo Enricher  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  Cities: {cities}  |  Threads: {args.threads}')
    print(f'{"="*64}\n')

    # Progress file
    if args.reset and os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        print('  Progress file reset.\n')

    done_ids = load_progress() if args.resume else set()
    if done_ids:
        print(f'  Resuming — already done: {len(done_ids)} leads\n')

    # Fetch
    print('  Fetching leads from Supabase...')
    all_leads = fetch_all_leads(cities, ids)
    print(f'  Total fetched: {len(all_leads)}\n')

    # Filter: skip already processed and leads with existing street_view_url
    to_process = []
    skipped_existing = 0
    for lead in all_leads:
        if lead['id'] in done_ids:
            continue
        existing = lead.get('street_view_url')
        if existing and existing != 'none':
            skipped_existing += 1
            continue
        to_process.append(lead)

    print(f'  To process: {len(to_process)} | Skipped (existing): {skipped_existing}\n')

    if not to_process:
        print('  Nothing to do.')
        return

    # Process in parallel
    batch   = []
    done    = set(done_ids)
    _stats['total'] = 0

    def flush_batch():
        if batch:
            sb_patch_batch(batch[:], dry)
            done.update(lid for lid, _ in batch)
            save_progress(done)
            batch.clear()

    try:
        with ThreadPoolExecutor(max_workers=args.threads, thread_name_prefix='sv') as pool:
            futures = {pool.submit(process_lead, lead): lead for lead in to_process}

            for i, future in enumerate(as_completed(futures), 1):
                lead    = futures[future]
                name    = lead.get('name', f"id={lead['id']}")
                try:
                    lead_id, photo_url, code = future.result()
                except Exception as exc:
                    lead_id, photo_url, code = lead['id'], None, 'error'
                    _log(f'  [ERR] id={lead_id} {name}: {exc}')

                _inc(code)

                icon = {'ok': '✓', 'no_photo': '○', 'no_place': '✗', 'error': '!'}.get(code, '?')
                _log(f'  [{i:>4}/{len(to_process)}] {icon} id={lead_id} «{name[:40]}»'
                     + (f' → {photo_url[:60]}...' if photo_url else ''))

                with _lock:
                    batch.append((lead_id, photo_url))
                    if len(batch) >= BATCH_SIZE:
                        flush_batch()

                time.sleep(args.delay)

    except KeyboardInterrupt:
        _log('\n  [INTERRUPTED] Saving progress...')
    finally:
        flush_batch()

    print(f'\n{"="*64}')
    print(f'  DONE — total={_stats["total"]}')
    print(f'  ✓ ok={_stats.get("ok",0)}  ○ no_photo={_stats.get("no_photo",0)}'
          f'  ✗ no_place={_stats.get("no_place",0)}  ! error={_stats.get("error",0)}')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'  Progress saved: {PROGRESS_FILE}')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
