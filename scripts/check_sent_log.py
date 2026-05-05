#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_sent_log.py — Sent email log + daily summary report.

Queries beauty_leads for EMAIL SENT records and writes a structured report
to reports/daily_summary.txt (always) and optionally to a CSV.

Usage:
  python scripts/check_sent_log.py
  python scripts/check_sent_log.py --limit 200
  python scripts/check_sent_log.py --city Nice
  python scripts/check_sent_log.py --limit 600 --csv sent_log.csv
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, csv
from datetime import datetime, timezone
from collections import defaultdict

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

FIELDS = 'id,name,city,email,last_contacted,last_error'


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


def fetch_errors() -> list:
    """Fetch leads with last_error set (any status, any city)."""
    url = (f"{SB_URL}/rest/v1/beauty_leads"
           f"?select=id,name,city,email,last_error,status"
           f"&last_error=not.is.null"
           f"&order=id.desc"
           f"&limit=100")
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return []


def fmt_date(val: str) -> str:
    if not val:
        return '—'
    return val[:10]


def build_report(leads: list, errors: list, city_filter: str, limit: int) -> str:
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    city_label = city_filter or 'ВСІ МІСТА'
    W = 72

    lines = []
    def ln(s=''):  lines.append(s)
    def sep(c='='): lines.append(c * W)

    # ── Header ────────────────────────────────────────────────────────────────
    sep()
    ln(f'  ЗВІТ РОЗСИЛКИ  |  {now_str}')
    ln(f'  Місто: {city_label}  |  Показано: {len(leads)} записів (ліміт {limit})')
    sep()

    # ── City breakdown ────────────────────────────────────────────────────────
    ln()
    ln('  ПО МІСТАХ:')
    ln('-' * W)

    city_counts: dict = defaultdict(int)
    city_today:  dict = defaultdict(int)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    for lead in leads:
        city = lead.get('city') or '—'
        city_counts[city] += 1
        if fmt_date(lead.get('last_contacted') or '') == today:
            city_today[city] += 1

    total_today = sum(city_today.values())
    for city in sorted(city_counts, key=lambda c: city_counts[c], reverse=True):
        today_n = city_today.get(city, 0)
        today_tag = f'  (+{today_n} сьогодні)' if today_n else ''
        ln(f'  {city:<20} {city_counts[city]:>5} відправлено{today_tag}')

    ln()
    ln(f'  ВСЬОГО у звіті:  {len(leads)}  |  Сьогодні: {total_today}')

    # ── Detail table ──────────────────────────────────────────────────────────
    ln()
    sep('-')
    col_date  = 12
    col_name  = 32
    col_city  = 14
    col_email = 36

    header = (
        f"  {'Дата':<{col_date}} "
        f"{'Назва салону':<{col_name}} "
        f"{'Місто':<{col_city}} "
        f"{'Email':<{col_email}}"
    )
    ln(header)
    sep('-')

    for lead in leads:
        date  = fmt_date(lead.get('last_contacted') or '')
        name  = (lead.get('name') or '—')[:col_name]
        city  = (lead.get('city') or '—')[:col_city]
        email = (lead.get('email') or '—')[:col_email]
        ln(f"  {date:<{col_date}} {name:<{col_name}} {city:<{col_city}} {email:<{col_email}}")

    sep('-')

    # ── Errors section ────────────────────────────────────────────────────────
    ln()
    if errors:
        sep('!')
        ln(f'  ПОМИЛКИ ВІДПРАВКИ  |  {len(errors)} записів з last_error')
        sep('!')
        ln()
        for err in errors:
            eid   = err.get('id', '?')
            ename = (err.get('name') or '—')[:40]
            ecity = (err.get('city') or '—')[:14]
            etext = (err.get('last_error') or '').replace('\n', ' ')[:120]
            ln(f'  ID {eid:<6} | {ename:<40} | {ecity}')
            ln(f'         Помилка: {etext}')
            ln()
    else:
        ln('  ПОМИЛКИ: немає — всі відправки пройшли успішно.')
        ln()

    sep()
    ln(f'  Звіт збережено: reports/daily_summary.txt')
    sep()

    return '\n'.join(lines)


def parse_args():
    p = argparse.ArgumentParser(description='Sent email log + daily summary report')
    p.add_argument('--limit', type=int, default=200, help='Max records to fetch (default: 200)')
    p.add_argument('--city',  default='',            help='Filter by city (default: all)')
    p.add_argument('--csv',   default='',            help='Also save detail to CSV')
    p.add_argument('--no-report', action='store_true', help='Skip writing reports/daily_summary.txt')
    return p.parse_args()


def main():
    args = parse_args()

    leads = fetch_sent(city=args.city, limit=args.limit)
    errors = fetch_errors()

    report = build_report(leads, errors, args.city, args.limit)

    # Always print to terminal
    print(report)

    # Save to reports/daily_summary.txt unless suppressed
    if not args.no_report:
        reports_dir = os.path.join(_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        out_path = os.path.join(reports_dir, 'daily_summary.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(report + '\n')
        print(f'\n  >> Звіт збережено: {out_path}')

    # Optional CSV
    if args.csv:
        csv_path = args.csv if os.path.isabs(args.csv) else os.path.join(_ROOT, args.csv)
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'date', 'name', 'city', 'email', 'last_error'])
            writer.writeheader()
            for lead in leads:
                writer.writerow({
                    'id':         lead.get('id', ''),
                    'date':       fmt_date(lead.get('last_contacted') or ''),
                    'name':       lead.get('name') or '',
                    'city':       lead.get('city') or '',
                    'email':      lead.get('email') or '',
                    'last_error': lead.get('last_error') or '',
                })
        print(f'  >> CSV збережено:  {csv_path}')


if __name__ == '__main__':
    main()
