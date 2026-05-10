#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
migrate_funnel_keys.py — Normalize email_funnel_json key names across all leads.

Renames non-standard keys to the canonical set:
  letter_1  / letter_1_dm   / letter_1_mirror  → letter_1_digital_mirror
  letter_2  / letter_2_fv                       → letter_2_future_vision
  letter_3  / letter_3_sc   / letter_3_scarcity → letter_3_scarcity  (already canonical)
  letter_1_subject / letter_2_subject / letter_3_subject → kept as-is (flat subject fields)

Only writes back rows where at least one key was renamed.

Usage:
  python scripts/migrate_funnel_keys.py --dry-run          # preview changes
  python scripts/migrate_funnel_keys.py                     # apply to all cities
  python scripts/migrate_funnel_keys.py --city Cannes       # one city only
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _c(s, k):
    try:    return (_cfg.get(s, k) or '').strip()
    except: return ''

SB_URL = _c('SUPABASE', 'url')
_svc   = _c('SUPABASE', 'service_role_key')
SB_KEY = (_svc if len(_svc) > 80 and 'PASTE' not in _svc else '') or _c('SUPABASE', 'anon_key')

if not SB_URL or not SB_KEY:
    print('[ERROR] Missing SUPABASE url/key in config.ini', file=sys.stderr)
    sys.exit(1)

H_READ  = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}
H_WRITE = {**H_READ, 'Content-Type': 'application/json', 'Prefer': 'return=minimal'}

# ── Key rename map ─────────────────────────────────────────────────────────────
# Maps any non-canonical key → canonical key.
# Keys already canonical are left untouched.
RENAME = {
    # Letter 1 variants
    'letter_1':               'letter_1_digital_mirror',
    'letter_1_dm':            'letter_1_digital_mirror',
    'letter_1_mirror':        'letter_1_digital_mirror',
    'letter1':                'letter_1_digital_mirror',
    'letter_1_body':          'letter_1_digital_mirror',

    # Letter 2 variants
    'letter_2':               'letter_2_future_vision',
    'letter_2_fv':            'letter_2_future_vision',
    'letter2':                'letter_2_future_vision',
    'letter_2_body':          'letter_2_future_vision',

    # Letter 3 variants
    'letter_3':               'letter_3_scarcity',
    'letter_3_sc':            'letter_3_scarcity',
    'letter3':                'letter_3_scarcity',
    'letter_3_body':          'letter_3_scarcity',
    'letter_3_social_proof_scarcity': 'letter_3_scarcity',
}

CANONICAL = {
    'letter_1_digital_mirror',
    'letter_2_future_vision',
    'letter_3_scarcity',
    # flat subject/body fields — kept as-is
    'letter_1_subject',
    'letter_2_subject',
    'letter_3_subject',
    'letter_1_body',
    'letter_2_body',
    'letter_3_body',
}


def normalize(fj: dict) -> tuple[dict, list]:
    """Return (new_dict, list_of_renames). Empty list = no changes."""
    renames = []
    new = {}
    for k, v in fj.items():
        target = RENAME.get(k)
        if target and target != k:
            renames.append((k, target))
            new[target] = v
        else:
            new[k] = v
    return new, renames


def sb_fetch(city=None, offset=0, batch=500) -> list:
    params = {
        'select':            'id,email_funnel_json',
        'email_funnel_json': 'not.is.null',
        'order':             'id.asc',
        'limit':             str(batch),
        'offset':            str(offset),
    }
    if city:
        params['city'] = f'eq.{city}'
    qs = '&'.join(f'{k}={urllib.parse.quote(str(v), safe="=.,*():!-")}' for k, v in params.items())
    url = f'{SB_URL}/rest/v1/beauty_leads?{qs}'
    with urllib.request.urlopen(urllib.request.Request(url, headers=H_READ), timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch(lead_id: int, fj: dict) -> None:
    url  = f'{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}'
    data = json.dumps({'email_funnel_json': fj}, ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(url, data=data, headers=H_WRITE, method='PATCH')
    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()


def main():
    p = argparse.ArgumentParser(description='Normalize email_funnel_json key names')
    p.add_argument('--city',    default=None, help='Limit to one city (default: all)')
    p.add_argument('--dry-run', action='store_true', help='Preview only, no DB writes')
    args = p.parse_args()

    mode = 'DRY-RUN' if args.dry_run else 'LIVE'
    print(f'\n{"="*64}')
    print(f'  migrate_funnel_keys.py  |  {mode}')
    print(f'  City: {args.city or "ALL"}')
    print(f'{"="*64}\n')

    total_checked = 0
    total_renamed = 0
    total_patched = 0
    errors        = 0
    offset        = 0

    while True:
        batch = sb_fetch(city=args.city, offset=offset)
        if not batch:
            break

        for row in batch:
            total_checked += 1
            lead_id = row['id']
            fj = row.get('email_funnel_json')

            if isinstance(fj, str):
                try:
                    fj = json.loads(fj)
                except Exception:
                    continue
            if not isinstance(fj, dict):
                continue

            new_fj, renames = normalize(fj)
            if not renames:
                continue

            total_renamed += len(renames)
            rename_str = ', '.join(f'{old}→{new}' for old, new in renames)
            print(f'  id={lead_id}: {rename_str}')

            if not args.dry_run:
                try:
                    sb_patch(lead_id, new_fj)
                    total_patched += 1
                except Exception as e:
                    print(f'    [ERR] patch failed: {e}', file=sys.stderr)
                    errors += 1

        offset += len(batch)
        if len(batch) < 500:
            break

    print(f'\n{"="*64}')
    print(f'  Checked:      {total_checked}')
    print(f'  Keys renamed: {total_renamed}')
    if args.dry_run:
        print(f'  DRY-RUN: nothing written.')
    else:
        print(f'  Rows patched: {total_patched}')
        print(f'  Errors:       {errors}')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
