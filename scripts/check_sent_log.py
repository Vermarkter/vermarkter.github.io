#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_sent_log.py — Show last N sent emails from beauty_leads.

Queries leads where status = 'EMAIL SENT', ordered by last_contacted DESC.

Usage:
  python scripts/check_sent_log.py
  python scripts/check_sent_log.py --limit 100
  python scripts/check_sent_log.py --city Nice
  python scripts/check_sent_log.py --limit 600 --csv sent_log.csv
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, csv

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

FIELDS = 'id,name,city,email,last_contacted'


def fetch_sent(city: str, limit: int) -> list:
    params = [
        f"select={FIELDS}",
        "status=eq.EMAIL%20SENT",
        "order=last_contacted.desc.nullslast",
        f"limit={limit}",
    ]
    if city:
        params.append(f"city=eq.{urllib.parse.quote(city, safe='')}")
    url = f"{SB_URL}/rest/v1/beauty_leads?" + '&'.join(params)
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def fmt_date(val: str) -> str:
    if not val:
        return '—'
    return val[:10]


def parse_args():
    p = argparse.ArgumentParser(description='Show last N sent emails from beauty_leads')
    p.add_argument('--limit', type=int, default=50, help='Number of records (default: 50)')
    p.add_argument('--city',  default='',           help='Filter by city (default: all cities)')
    p.add_argument('--csv',   default='',           help='Also save to CSV file')
    return p.parse_args()


def main():
    args = parse_args()

    city_label = args.city or 'ALL'
    print(f'\n{"="*72}')
    print(f'  Sent Email Log  |  City: {city_label}  |  Last {args.limit} records')
    print(f'{"="*72}\n')

    leads = fetch_sent(city=args.city, limit=args.limit)

    if not leads:
        print('No records with status=EMAIL SENT found.')
        return

    col_date  = 12
    col_name  = 32
    col_city  = 14
    col_email = 36

    header = (
        f"{'Дата':<{col_date}} "
        f"{'Назва салону':<{col_name}} "
        f"{'Місто':<{col_city}} "
        f"{'Email':<{col_email}}"
    )
    sep = '-' * (col_date + col_name + col_city + col_email + 3)

    print(header)
    print(sep)

    for lead in leads:
        date  = fmt_date(lead.get('last_contacted') or '')
        name  = (lead.get('name') or '—')[:col_name]
        city  = (lead.get('city') or '—')[:col_city]
        email = (lead.get('email') or '—')[:col_email]
        print(f"{date:<{col_date}} {name:<{col_name}} {city:<{col_city}} {email:<{col_email}}")

    print(sep)
    print(f'\nTotal shown: {len(leads)}')

    if args.csv:
        csv_path = args.csv if os.path.isabs(args.csv) else os.path.join(_ROOT, args.csv)
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'date', 'name', 'city', 'email'])
            writer.writeheader()
            for lead in leads:
                writer.writerow({
                    'id':    lead.get('id', ''),
                    'date':  fmt_date(lead.get('last_contacted') or ''),
                    'name':  lead.get('name') or '',
                    'city':  lead.get('city') or '',
                    'email': lead.get('email') or '',
                })
        print(f'CSV saved: {csv_path}')

    print(f'{"="*72}\n')


if __name__ == '__main__':
    main()
