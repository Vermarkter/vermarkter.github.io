#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
export_raw_leads.py — Export Nice leads to plain text for Claude Pro processing.

Fetches leads where email_funnel_json IS NULL and status != 'EMAIL SENT',
outputs compact dossier per lead for manual Claude Pro prompt input.

Usage:
  python scripts/export_raw_leads.py                      # 50 leads, Nice
  python scripts/export_raw_leads.py --limit 100
  python scripts/export_raw_leads.py --city Nice --limit 200
  python scripts/export_raw_leads.py --out my_leads.txt   # custom output file
  python scripts/export_raw_leads.py --offset 50          # skip first 50
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse

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

HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}

FIELDS = 'id,name,city,phone,email,website,notes,status'


def fetch_leads(city: str, limit: int, offset: int) -> list:
    city_enc = urllib.parse.quote(city, safe='')
    url = (
        f"{SB_URL}/rest/v1/beauty_leads"
        f"?select={FIELDS}"
        f"&city=eq.{city_enc}"
        f"&email_funnel_json=is.null"
        f"&status=neq.EMAIL%20SENT"
        f"&order=id.asc"
        f"&limit={limit}"
        f"&offset={offset}"
    )
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def format_lead(lead: dict) -> str:
    notes = (lead.get('notes') or '').strip()
    notes_short = notes[:200].replace('\n', ' ') if notes else '—'
    return (
        f"ID: {lead['id']} | "
        f"Name: {lead.get('name') or '—'} | "
        f"Website: {lead.get('website') or '—'} | "
        f"Phone: {lead.get('phone') or '—'} | "
        f"Email: {lead.get('email') or '—'} | "
        f"Notes: {notes_short}"
    )


def parse_args():
    p = argparse.ArgumentParser(description='Export Nice leads → plain text for Claude Pro')
    p.add_argument('--city',   default='Nice', help='City filter (default: Nice)')
    p.add_argument('--limit',  type=int, default=50, help='Max leads per file (default: 50)')
    p.add_argument('--offset', type=int, default=0,  help='Supabase offset (default: 0)')
    p.add_argument('--out',    default='', help='Output file (default: nice_raw_leads.txt)')
    return p.parse_args()


def main():
    args = parse_args()

    out_path = args.out or os.path.join(_ROOT, f'{args.city.lower()}_raw_leads.txt')

    print(f'\n{"="*64}')
    print(f'  Export Raw Leads  |  City: {args.city}  |  Limit: {args.limit}')
    print(f'  Filter: email_funnel_json IS NULL + status != EMAIL SENT')
    print(f'{"="*64}\n')

    print('Fetching from Supabase...')
    leads = fetch_leads(city=args.city, limit=args.limit, offset=args.offset)
    print(f'Fetched: {len(leads)} leads\n')

    if not leads:
        print('No leads matching filter. Check city/status/email_funnel_json.')
        return

    lines = [format_lead(l) for l in leads]

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'# Nice leads export — {len(leads)} records\n')
        f.write(f'# Filter: email_funnel_json IS NULL | status != EMAIL SENT\n')
        f.write(f'# City: {args.city} | offset={args.offset}\n')
        f.write('#\n')
        f.write('# Paste this block into Claude Pro with the Indépendance prompt.\n')
        f.write('# Claude should return JSON: [{"id": ..., "letter_1": "..."}, ...]\n')
        f.write('#\n\n')
        for line in lines:
            f.write(line + '\n')

    size_kb = os.path.getsize(out_path) / 1024
    print(f'  Output: {out_path}')
    print(f'  Lines:  {len(leads)}')
    print(f'  Size:   {size_kb:.1f} KB')
    print(f'\n  Next step:')
    print(f'  1. Open {out_path} → paste into Claude Pro with the prompt below')
    print(f'  2. Claude returns JSON array → save as nice_offers.json')
    print(f'  3. python scripts/import_generated_leads.py --file nice_offers.json')
    print(f'\n  --- PROMPT FOR CLAUDE PRO ---')
    print(f'  Pour chaque salon ci-dessous, génère une lettre email professionnelle')
    print(f'  en français (prompt Indépendance). Retourne un JSON array:')
    print(f'  [{{"id": 123, "letter_1": "Objet: ...\\n\\nBonjour,..."}}, ...]')
    print(f'  --- END PROMPT ---\n')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
