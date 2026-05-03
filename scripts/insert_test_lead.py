#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
insert_test_lead.py — Insert Director's test lead into beauty_leads.

Usage:
  python scripts/insert_test_lead.py
  python scripts/insert_test_lead.py --dry-run
"""
import sys, io, json, os, urllib.request, configparser, argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = configparser.ConfigParser()
cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')
SB_URL = cfg['SUPABASE']['url'].strip()
_svc   = cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else cfg['SUPABASE']['anon_key'].strip()
HDRS = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

TEST_LEAD = {
    'name':   'Andriy Test',
    'city':   'Berlin',
    'email':  'andreychupryna@gmail.com',
    'phone':  '+49000000000',
    'status': 'READY TO SEND',
    'notes':  'test=y director=y',
}


def insert(lead):
    body = json.dumps(lead, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        f'{SB_URL}/rest/v1/beauty_leads',
        data=body, headers=HDRS, method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.request.HTTPError as e:
        return e.code, e.read().decode('utf-8')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    print('\n' + '='*60)
    print('  Insert Test Lead  |', 'DRY-RUN' if args.dry_run else 'LIVE')
    print('  Data:', TEST_LEAD)
    print('='*60)

    if args.dry_run:
        print('\n  [DRY-RUN] Would insert:')
        for k, v in TEST_LEAD.items():
            print(f'    {k}: {v}')
        print('\n  No DB write.')
        return

    code, result = insert(TEST_LEAD)
    if code in (200, 201):
        inserted = result if isinstance(result, list) else [result]
        new_id = inserted[0].get('id', '?') if inserted else '?'
        print(f'\n  [OK] Inserted — new ID: {new_id}')
        print(f'  Name:   {TEST_LEAD["name"]}')
        print(f'  Email:  {TEST_LEAD["email"]}')
        print(f'  Phone:  {TEST_LEAD["phone"]}')
        print(f'  Status: {TEST_LEAD["status"]}')
    else:
        print(f'\n  [ERR {code}] {result}')

    print('='*60)


if __name__ == '__main__':
    main()
