#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_emails.py — Scrape missing emails for existing beauty_leads.

Finds leads where email IS NULL and website IS NOT NULL,
visits homepage + /contact /impressum /kontakt pages,
extracts first usable email, PATCHes it into Supabase.

Usage:
  python scripts/enrich_emails.py --city Nice           # dry-run (show only)
  python scripts/enrich_emails.py --city Nice --apply   # write to DB
  python scripts/enrich_emails.py --city Nice --city Cannes --limit 50 --apply
  python scripts/enrich_emails.py --all-fr --apply      # Nice + Cannes together

Config: config.ini [SUPABASE] url / anon_key or service_role_key
"""

import sys
import io
import os
import re
import json
import time
import argparse
import configparser
import urllib.request
import urllib.parse
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────────────────────────
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

HTTP_CTX = ssl.create_default_context()
HTTP_CTX.check_hostname = False
HTTP_CTX.verify_mode    = ssl.CERT_NONE

THREADS = 8

# ── Email scraper (same logic as lead_harvester.py) ───────────────────────────
EMAIL_RX  = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
BAD_EMAIL = re.compile(r'\.(png|jpg|jpeg|gif|webp|svg|css|js|woff|woff2|ttf)$', re.I)
BAD_DOMAINS = {'sentry.io', 'wixpress.com', 'example.com', 'domain.com',
               'email.com', 'yourname.com', 'youremail.com'}


def http_get(url, timeout=8):
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/124.0 Safari/537.36',
                 'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'}
    )
    with urllib.request.urlopen(req, timeout=timeout, context=HTTP_CTX) as r:
        raw = r.read()
    try:
        return raw.decode('utf-8', errors='ignore')
    except Exception:
        return raw.decode('latin-1', errors='ignore')


def scrape_email(website: str) -> str | None:
    if not website:
        return None
    if not website.startswith('http'):
        website = 'https://' + website

    base = website.rstrip('/')
    # Contact/imprint pages likely to have email (FR + DE patterns)
    candidates = [
        base,
        base + '/contact',
        base + '/contact-us',
        base + '/contactez-nous',
        base + '/nous-contacter',
        base + '/impressum',
        base + '/kontakt',
        base + '/imprint',
        base + '/a-propos',
        base + '/about',
    ]

    found = []
    for url in candidates[:6]:
        try:
            html = http_get(url, timeout=8)
        except Exception:
            continue

        # mailto: links first (most reliable)
        for m in re.finditer(r'mailto:([^"\'\s>?]+)', html, re.I):
            e = m.group(1).split('?')[0].strip().lower()
            if e and not BAD_EMAIL.search(e):
                domain = e.split('@')[-1] if '@' in e else ''
                if domain and domain not in BAD_DOMAINS:
                    found.append(e)

        # plaintext email patterns
        for m in EMAIL_RX.finditer(html):
            e = m.group(0).strip().lower()
            if not e or BAD_EMAIL.search(e):
                continue
            domain = e.split('@')[-1] if '@' in e else ''
            if not domain or domain in BAD_DOMAINS:
                continue
            if 'sentry' in e or 'wixpress' in e or 'example' in e:
                continue
            found.append(e)

        if found:
            break

    if not found:
        return None

    # Prefer common business prefixes
    for pref in ('info@', 'contact@', 'kontakt@', 'hallo@', 'hello@',
                 'mail@', 'office@', 'salon@', 'booking@', 'reservation@'):
        for e in found:
            if e.startswith(pref):
                return e
    return found[0]


# ── Supabase helpers ──────────────────────────────────────────────────────────

def sb_get(path: str) -> list:
    req = urllib.request.Request(SB_URL + path, headers=HDRS_READ)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch_email(lead_id: int, email: str) -> None:
    url  = SB_URL + f'/rest/v1/beauty_leads?id=eq.{lead_id}'
    data = json.dumps({'email': email}).encode('utf-8')
    req  = urllib.request.Request(url, data=data, headers=HDRS_WRITE, method='PATCH')
    with urllib.request.urlopen(req, timeout=15) as r:
        r.read()


def fetch_leads_missing_email(cities: list, limit: int) -> list:
    city_param = ','.join(f'"{c}"' for c in cities)
    qs = urllib.parse.urlencode({
        'select': 'id,name,website,city,email',
        'city':   f'in.({city_param})',
        'email':  'is.null',
        'website':'not.is.null',
        'order':  'id.asc',
        'limit':  str(limit if limit else 2000),
    })
    return sb_get('/rest/v1/beauty_leads?' + qs)


# ── Worker ────────────────────────────────────────────────────────────────────

def process_lead(lead: dict, apply: bool) -> dict:
    lid  = lead['id']
    name = lead.get('name', '?')
    site = lead.get('website', '')

    email = scrape_email(site)
    status = 'skip'

    if email:
        if apply:
            try:
                sb_patch_email(lid, email)
                status = 'patched'
            except Exception as e:
                status = f'error:{e}'
        else:
            status = 'found'

    return {'id': lid, 'name': name, 'website': site, 'email': email, 'status': status}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='Enrich missing emails for beauty_leads')
    p.add_argument('--city',   action='append', default=[],
                   metavar='CITY', help='City filter, repeatable (default: Nice)')
    p.add_argument('--all-fr', action='store_true',
                   help='Shortcut for --city Nice --city Cannes')
    p.add_argument('--limit',  type=int, default=0,
                   help='Max leads to process (0 = all)')
    p.add_argument('--threads', type=int, default=THREADS,
                   help=f'Parallel threads (default: {THREADS})')
    p.add_argument('--apply',  action='store_true',
                   help='Write emails to DB (default: dry-run, print only)')
    args = p.parse_args()

    cities = list(args.city)
    if args.all_fr:
        cities += ['Nice', 'Cannes']
    cities = list(dict.fromkeys(cities)) or ['Nice']

    mode = 'APPLY' if args.apply else 'DRY-RUN'
    print(f'\n{"="*64}')
    print(f'  enrich_emails.py  |  {mode}')
    print(f'  Cities: {", ".join(cities)}  |  Limit: {args.limit or "all"}  |  Threads: {args.threads}')
    print(f'{"="*64}\n')

    leads = fetch_leads_missing_email(cities, args.limit)
    print(f'Leads with website but no email: {len(leads)}\n')

    if not leads:
        print('Nothing to do.')
        return

    results  = []
    found    = 0
    patched  = 0
    errors   = 0
    no_email = 0

    with ThreadPoolExecutor(max_workers=args.threads, thread_name_prefix='enrich') as pool:
        futures = {pool.submit(process_lead, lead, args.apply): lead for lead in leads}
        done    = 0
        for future in as_completed(futures):
            done += 1
            try:
                r = future.result()
            except Exception as exc:
                lead = futures[future]
                r = {'id': lead['id'], 'name': lead.get('name', '?'),
                     'website': lead.get('website', ''), 'email': None,
                     'status': f'error:{exc}'}

            results.append(r)

            if r['status'] == 'patched':
                patched += 1
                tag = '[PATCH]'
            elif r['status'] == 'found':
                found += 1
                tag = '[FOUND]'
            elif r['status'].startswith('error'):
                errors += 1
                tag = '[ERR]  '
            else:
                no_email += 1
                tag = '[----]  '

            email_str = r['email'] or '—'
            print(f'  {tag} {str(r["id"]):<6} {(r["name"] or "")[:30]:<30}  {email_str}')
            sys.stdout.flush()

    print(f'\n{"="*64}')
    if args.apply:
        print(f'  Patched to DB:  {patched}')
        print(f'  Errors:         {errors}')
    else:
        print(f'  Emails found:   {found}  (dry-run — not written)')
    print(f'  No email found: {no_email}')
    print(f'  Total checked:  {len(leads)}')
    if not args.apply and found:
        print(f'\n  Re-run with --apply to write {found} emails to Supabase.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
