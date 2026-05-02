#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
run_elite_patch_compliments.py — Patch compliment_detail only (run AFTER SQL migration).
Requires: scripts/add_compliment_detail_column.sql run in Supabase SQL Editor first.
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
HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY,
        'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
DATA_FILE = os.path.join(_ROOT, 'data', 'elite_patch_berlin.json')


def patch_compliment(lead_id, compliment):
    body = json.dumps({'compliment_detail': compliment},
                      ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        f'{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}',
        data=body, headers=HDRS, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    with open(DATA_FILE, encoding='utf-8') as f:
        records = json.load(f)

    to_patch = [(r['id'], r['compliment']) for r in records if r.get('compliment')]
    print(f'\n{"="*60}')
    print(f'  Elite Patch — COMPLIMENTS ONLY  |  {"DRY-RUN" if args.dry_run else "LIVE"}')
    print(f'  IDs with compliment_detail: {len(to_patch)}')
    print(f'{"="*60}\n')

    ok = fail = 0
    for lid, compliment in to_patch:
        print(f'  ID {lid:>3} → {compliment[:65]}')
        if not args.dry_run:
            code = patch_compliment(lid, compliment)
            sym  = 'OK' if code in (200, 204) else f'ERR {code}'
            print(f'          [{sym}]')
            if code in (200, 204): ok += 1
            else:                  fail += 1
        else:
            print(f'          [DRY-RUN]')
            ok += 1

    print(f'\n{"="*60}')
    print(f'  DONE | ok={ok} fail={fail}')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
