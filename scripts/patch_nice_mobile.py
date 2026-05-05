#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
patch_nice_mobile.py — Mark French mobile numbers in Nice as is_mobile=true.

Finds all Nice leads where phone starts with +336 or +337 and sets is_mobile=True.

Usage:
  python scripts/patch_nice_mobile.py          # dry-run (show only)
  python scripts/patch_nice_mobile.py --apply  # actually patch DB
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

HDRS_READ = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
}
HDRS_WRITE = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}


def fetch_nice_leads():
    """Fetch all Nice leads that have a phone number."""
    url = (SB_URL + '/rest/v1/beauty_leads'
           '?select=id,name,phone,is_mobile'
           '&city=eq.Nice'
           '&phone=not.is.null'
           '&limit=2000')
    req = urllib.request.Request(url, headers=HDRS_READ)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def is_french_mobile(phone: str) -> bool:
    digits = ''.join(c for c in (phone or '') if c.isdigit())
    return digits.startswith('336') or digits.startswith('337')


def patch_lead(lead_id: int) -> None:
    url  = SB_URL + f'/rest/v1/beauty_leads?id=eq.{lead_id}'
    data = json.dumps({'is_mobile': True}).encode('utf-8')
    req  = urllib.request.Request(url, data=data, headers=HDRS_WRITE, method='PATCH')
    with urllib.request.urlopen(req, timeout=15) as r:
        r.read()


def main():
    p = argparse.ArgumentParser(description='Patch Nice French mobile numbers → is_mobile=true')
    p.add_argument('--apply', action='store_true', help='Actually write to DB (default: dry-run)')
    args = p.parse_args()

    print(f'\n{"="*64}')
    print(f'  patch_nice_mobile  |  {"APPLY" if args.apply else "DRY-RUN"}')
    print(f'{"="*64}\n')

    leads = fetch_nice_leads()
    print(f'Fetched {len(leads)} Nice leads with phone\n')

    targets = [l for l in leads if is_french_mobile(l.get('phone', ''))]
    already = [l for l in targets if l.get('is_mobile')]
    to_patch = [l for l in targets if not l.get('is_mobile')]

    print(f'French mobile (+336/+337): {len(targets)}')
    print(f'  Already is_mobile=true:  {len(already)}')
    print(f'  Needs patching:          {len(to_patch)}\n')

    if not to_patch:
        print('Nothing to do.')
        print(f'{"="*64}\n')
        return

    print(f'{"ID":<8} {"Phone":<18} {"Name":<32}')
    print('-' * 60)
    for l in to_patch:
        print(f'{l["id"]:<8} {(l.get("phone") or ""):<18} {(l.get("name") or "")[:32]:<32}')

    if not args.apply:
        print(f'\nDry-run complete. Re-run with --apply to patch {len(to_patch)} leads.')
        print(f'{"="*64}\n')
        return

    print(f'\nPatching {len(to_patch)} leads...')
    ok = 0
    fail = 0
    for l in to_patch:
        try:
            patch_lead(l['id'])
            ok += 1
            print(f'  [OK]  {l["id"]} — {l.get("name", "")}')
        except Exception as e:
            fail += 1
            print(f'  [ERR] {l["id"]} — {e}', file=sys.stderr)

    print(f'\nDone: {ok} patched, {fail} errors')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
