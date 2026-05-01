#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_email_funnel.py — Writes email_funnel_json + sets status=email_ready.

Usage:
  python scripts/patch_email_funnel.py --file data/email_funnels_berlin.json
  python scripts/patch_email_funnel.py --file data/email_funnels_berlin.json --dry-run
  python scripts/patch_email_funnel.py --file data/email_funnels_berlin.json --ids 173,184,199

Input JSON format (list of objects):
  [
    {
      "id": 173,
      "email_funnel": {
        "letter_1": { "subject": "...", "body": "..." },
        "letter_2": { "subject": "...", "body": "..." },
        "letter_3": { "subject": "...", "body": "..." }
      }
    },
    ...
  ]

Requirements:
  SUPABASE_URL and SUPABASE_KEY must be set in environment OR config.ini [SUPABASE].
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_env(path):
    env = {}
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

_env = _load_env(os.path.join(_ROOT, '.env'))
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL = (
    os.environ.get('SUPABASE_URL')
    or _env.get('SUPABASE_URL')
    or _cfg.get('SUPABASE', 'url', fallback='')
).strip()

_svc = _cfg.get('SUPABASE', 'service_role_key', fallback='').strip()
SB_KEY = (
    os.environ.get('SUPABASE_KEY')
    or _env.get('SUPABASE_KEY')
    or (_svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) else '')
    or _cfg.get('SUPABASE', 'anon_key', fallback='')
).strip()

if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE_URL / SUPABASE_KEY not configured.', file=sys.stderr)
    sys.exit(1)

HDRS_PATCH = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json; charset=utf-8',
    'Prefer':        'return=minimal',
}

# ── Supabase PATCH ────────────────────────────────────────────────────────────

def patch_lead(lead_id: int, funnel_data: dict, dry: bool) -> str:
    """
    PATCHes beauty_leads SET email_funnel_json=..., status='email_ready'
    Returns 'OK', 'DRY', or 'ERR <code>'.
    """
    payload_obj = {
        'email_funnel_json': funnel_data,   # Supabase accepts nested JSON natively
        'status':            'email_ready',
    }
    # ensure_ascii=False → umlauts stored as ä ö ü, not \\u00e4 etc.
    payload_bytes = json.dumps(payload_obj, ensure_ascii=False).encode('utf-8')

    if dry:
        preview = json.dumps(funnel_data, ensure_ascii=False)[:120]
        print(f'    funnel preview: {preview}...')
        return 'DRY'

    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=payload_bytes, headers=HDRS_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 'OK' if r.status in (200, 204) else f'ERR {r.status}'
    except urllib.request.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:200]
        return f'ERR {e.code}: {body}'

# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Patch email_funnel_json into beauty_leads')
    p.add_argument('--file',    required=True, help='Path to JSON file with funnel data')
    p.add_argument('--ids',     default='',    help='Comma-separated IDs to process (default: all in file)')
    p.add_argument('--dry-run', action='store_true', help='Print what would be patched, no DB write')
    p.add_argument('--delay',   type=float, default=0.3, help='Seconds between requests (default: 0.3)')
    return p.parse_args()


def main():
    args = parse_args()
    dry  = args.dry_run
    id_filter = {int(x.strip()) for x in args.ids.split(',') if x.strip()} if args.ids else None

    # Load funnel data
    file_path = args.file if os.path.isabs(args.file) else os.path.join(_ROOT, args.file)
    with open(file_path, encoding='utf-8') as f:
        records = json.load(f)

    print(f'\n{"="*64}')
    print(f'  Email Funnel Patcher  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  File: {file_path}')
    print(f'  Records in file: {len(records)}')
    if id_filter:
        print(f'  ID filter: {sorted(id_filter)}')
    print(f'{"="*64}\n')

    ok = fail = skipped = 0

    for rec in records:
        lead_id = rec.get('id')
        if not lead_id:
            print(f'  [SKIP] Missing "id" field in record: {str(rec)[:60]}')
            skipped += 1
            continue

        if id_filter and lead_id not in id_filter:
            skipped += 1
            continue

        # Accept both {'email_funnel': {...}} and flat {'letter_1': {...}, ...}
        funnel = rec.get('email_funnel') or {
            k: v for k, v in rec.items()
            if k not in ('id', 'name', 'email_funnel')
        }

        name = rec.get('name', f'id={lead_id}')
        print(f'  [PATCH] id={lead_id} «{name}»')

        result = patch_lead(lead_id, funnel, dry)
        print(f'         → [{result}]')

        if result in ('OK', 'DRY'):
            ok += 1
        else:
            fail += 1

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — total={ok+fail+skipped} | patched={ok} | skipped={skipped} | fail={fail}')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
