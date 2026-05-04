#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_fetch.py — Fetch next N München leads for Sniper agent.

Usage:
  python scripts/sniper_fetch.py          # 20 leads (default)
  python scripts/sniper_fetch.py 40       # custom count
  python scripts/sniper_fetch.py 20 50    # count + offset

Output: JSON array to stdout. Each object:
  { id, name, city, district, phone, email, website,
    maps_url, custom_message, notes }

Sniper workflow:
  1. Run this script → get JSON list
  2. Generate Elite messages for each lead
  3. Feed result to fast_uploader.py or sniper_patch.py
"""
import sys, io, json, urllib.request, configparser

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_cfg = configparser.ConfigParser()
_cfg.read(r'c:\Users\andri\OneDrive\Projects\агенство-новий\config.ini', encoding='utf-8')
SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}

FIELDS = 'id,name,city,district,phone,email,website,maps_url,custom_message,notes'

def fetch(limit=20, offset=0):
    url = (SB_URL + '/rest/v1/beauty_leads'
           '?select=' + FIELDS +
           '&district=ilike.M%C3%BCnchen%25'
           '&status=eq.new'
           '&order=id.asc'
           '&limit=' + str(limit) +
           '&offset=' + str(offset))
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def main():
    limit  = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    rows = fetch(limit, offset)

    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print('\n# ---', file=sys.stderr)
    print('# Fetched: %d leads (offset=%d)' % (len(rows), offset), file=sys.stderr)
    print('# Status filter: new | District: München*', file=sys.stderr)
    if rows:
        print('# ID range: %d – %d' % (rows[0]['id'], rows[-1]['id']), file=sys.stderr)

if __name__ == '__main__':
    main()
