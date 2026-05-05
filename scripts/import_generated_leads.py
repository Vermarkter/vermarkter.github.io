#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_generated_leads.py — Import Claude Pro-generated offers into Supabase.

Reads a JSON array (from Claude Pro output) and updates:
  - email_funnel_json → {"letter_1_digital_mirror": "<generated email>"}
  - status            → "email_ready"

Input JSON format (one array, can be file or stdin):
  [
    {"id": 123, "letter_1": "Objet: ...\\n\\nBonjour,..."},
    {"id": 124, "letter_1": "Objet: ...\\n\\nBonjour,..."}
  ]

Usage:
  python scripts/import_generated_leads.py --file nice_offers.json
  python scripts/import_generated_leads.py --file nice_offers.json --dry-run
  cat nice_offers.json | python scripts/import_generated_leads.py --stdin
  python scripts/import_generated_leads.py --file nice_offers.json --status READY TO SEND
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _e(k):  return (os.environ.get(k) or '').strip()
def _c(s, k):
    try:    return (_cfg.get(s, k) or '').strip()
    except: return ''

SB_URL = _e('SUPABASE_URL') or _c('SUPABASE', 'url')
_svc   = _c('SUPABASE', 'service_role_key')
SB_KEY = (_e('SUPABASE_KEY')
          or (_svc if len(_svc) > 80 and 'PASTE' not in _svc else '')
          or _c('SUPABASE', 'anon_key'))

HDRS_PATCH = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}


def patch_lead(lead_id: int, letter: str, status: str, dry: bool) -> str:
    if dry:
        return 'dry'
    payload = json.dumps({
        'email_funnel_json': {'letter_1_digital_mirror': letter},
        'status':            status,
    }, ensure_ascii=False).encode('utf-8')
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=payload, headers=HDRS_PATCH, method='PATCH')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return 'ok'
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                return f'err {e.code}'
        except Exception as exc:
            time.sleep(1)
    return 'timeout'


def load_records(args) -> list:
    if args.stdin:
        raw = sys.stdin.read()
    elif args.file:
        path = args.file if os.path.isabs(args.file) else os.path.join(_ROOT, args.file)
        with open(path, encoding='utf-8') as f:
            raw = f.read()
    else:
        print('[ERROR] Provide --file or --stdin', file=sys.stderr)
        sys.exit(1)

    raw = raw.strip()

    # Strip markdown code fence if Claude Pro wrapped it
    if raw.startswith('```'):
        lines = raw.splitlines()
        raw = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f'[ERROR] JSON parse failed: {e}', file=sys.stderr)
        print('First 200 chars:', raw[:200], file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print('[ERROR] Expected JSON array at top level', file=sys.stderr)
        sys.exit(1)

    return data


def parse_args():
    p = argparse.ArgumentParser(description='Import Claude Pro-generated offers → Supabase')
    p.add_argument('--file',    default='', help='Path to JSON file with offers')
    p.add_argument('--stdin',   action='store_true', help='Read JSON from stdin')
    p.add_argument('--status',  default='email_ready', help='Status to set (default: email_ready)')
    p.add_argument('--dry-run', action='store_true',   help='No DB writes, preview only')
    p.add_argument('--delay',   type=float, default=0.1, help='Seconds between patches (default: 0.1)')
    return p.parse_args()


def main():
    args = parse_args()
    dry  = args.dry_run

    print(f'\n{"="*64}')
    print(f'  Import Generated Leads  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  Target status: {args.status}')
    print(f'{"="*64}\n')

    records = load_records(args)
    print(f'Loaded {len(records)} records from input\n')

    ok_count   = 0
    err_count  = 0
    skip_count = 0

    for rec in records:
        lead_id = rec.get('id')
        letter  = rec.get('letter_1') or rec.get('letter_1_digital_mirror') or ''

        if not lead_id:
            print(f'  [SKIP] No "id" field in record: {str(rec)[:80]}')
            skip_count += 1
            continue

        if not letter.strip():
            print(f'  [SKIP] id={lead_id} — empty letter_1')
            skip_count += 1
            continue

        preview = letter.replace('\n', ' ')[:80]
        result  = patch_lead(lead_id, letter.strip(), args.status, dry)

        icon = {'ok': '✓', 'dry': '~', 'timeout': '⏱'}.get(result, '✗')
        print(f'  [{icon}] id={lead_id} → {result}  |  {preview}...')

        if result in ('ok', 'dry'):
            ok_count += 1
        else:
            err_count += 1

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — ok={ok_count} | errors={err_count} | skipped={skip_count}')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
