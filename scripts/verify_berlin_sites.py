#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_berlin_sites.py — Mass URL health checker for Berlin leads.

For each lead with a website URL:
  1. HTTP status check  (200 / 3xx / 4xx / 5xx / timeout / DNS error)
  2. Dead-site keyword detection  ('Expired', 'Domain for sale', 'Parked', ...)
  3. SSL certificate audit  (days until expiry → hook: 'SSL läuft in N Tagen ab')

Auto-tagging in Supabase:
  • status → 'dead_site'      if unreachable / parked / expired domain
  • ssl_expires_in_days       saved to notes/custom field (PATCH beauty_leads)

Usage:
  python3 scripts/verify_berlin_sites.py
  python3 scripts/verify_berlin_sites.py --city Munich --limit 200
  python3 scripts/verify_berlin_sites.py --dry-run          # no DB writes
  python3 scripts/verify_berlin_sites.py --workers 20       # concurrency
  python3 scripts/verify_berlin_sites.py --report report.json
  python3 scripts/verify_berlin_sites.py --ssl-only         # only check SSL
  python3 scripts/verify_berlin_sites.py --dead-only        # only tag dead sites

Requires: Python 3.8+ (stdlib only — no extra packages needed)
"""

import sys, io, os, json, time, argparse, configparser, ssl, socket, threading
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGS = os.path.join(_ROOT, 'logs')
os.makedirs(_LOGS, exist_ok=True)

LOG_FILE = os.path.join(_LOGS, 'verify_sites.log')

# ── Config ─────────────────────────────────────────────────────────────────────
def _load_env(path):
    env = {}
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

_env = _load_env(os.path.join(_ROOT, '.env'))
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

try:
    SB_URL = _cfg['SUPABASE']['url'].strip()
    _svc   = _cfg['SUPABASE']['service_role_key'].strip()
    SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
             else _cfg['SUPABASE']['anon_key'].strip()
except (KeyError, configparser.NoSectionError):
    print('[ERROR] config.ini missing [SUPABASE] section.', file=sys.stderr)
    sys.exit(1)

HDRS_GET = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
}
HDRS_PATCH = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

# ── Constants ──────────────────────────────────────────────────────────────────
HTTP_TIMEOUT   = 10       # seconds per HTTP request
SSL_TIMEOUT    = 8        # seconds for SSL handshake
FETCH_LIMIT    = 1000     # Supabase page size (max per request)
SSL_WARN_DAYS  = 30       # flag SSL certs expiring within N days
SSL_URGENT_DAYS = 7       # 'urgent' threshold

# Keywords that indicate a parked / dead / for-sale domain
DEAD_KEYWORDS = [
    'expired', 'domain for sale', 'domain is for sale', 'parked domain',
    'this domain', 'buy this domain', 'domain parking', 'sedoparking',
    'hugedomains', 'godaddy.com/domainforsale', 'underconstruction',
    'coming soon', 'website coming soon', 'site coming soon',
    'under maintenance', 'account suspended', 'account has been suspended',
    'bandwidth exceeded', 'cpu quota exceeded',
    'this site can', 'this webpage is not available',
    'page not found', '404 not found',
    'web hosting',       # catch generic hosting landing pages
]

# HTTP User-Agent — mimic a real browser to avoid trivial blocks
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
      'AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124.0.0.0 Safari/537.36')

# ── Logging ────────────────────────────────────────────────────────────────────
_log_lock = threading.Lock()

def log(msg, level='INFO'):
    ts   = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] [{level}] {msg}'
    with _log_lock:
        print(line, flush=True)
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        except Exception:
            pass

# ── Supabase helpers ───────────────────────────────────────────────────────────
def sb_fetch_page(city, limit, offset, status_filter=None):
    """Fetch one page of leads with website field set."""
    params = (
        f"select=id,name,city,website,status,email"
        f"&city=eq.{urllib.parse.quote(city, safe='')}"
        f"&website=not.is.null"
        f"&website=neq."
        f"&order=id.asc"
        f"&limit={limit}"
        f"&offset={offset}"
    )
    if status_filter:
        params += f"&status=eq.{urllib.parse.quote(status_filter, safe='')}"

    url = f"{SB_URL}/rest/v1/beauty_leads?{params}"
    req = urllib.request.Request(url, headers=HDRS_GET)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        log(f'sb_fetch_page error (offset={offset}): {e}', 'ERROR')
        return []


def sb_fetch_all(city, status_filter=None):
    """Paginate through all matching leads."""
    leads = []
    offset = 0
    while True:
        page = sb_fetch_page(city, FETCH_LIMIT, offset, status_filter)
        leads.extend(page)
        if len(page) < FETCH_LIMIT:
            break
        offset += FETCH_LIMIT
    return leads


def sb_patch(lead_id, payload_dict):
    """PATCH a single lead. Returns HTTP status code."""
    url     = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    payload = json.dumps(payload_dict, ensure_ascii=False).encode('utf-8')
    req     = urllib.request.Request(url, data=payload, headers=HDRS_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code
    except Exception as e:
        log(f'sb_patch lead {lead_id} error: {e}', 'WARN')
        return 0

# ── URL normalisation ──────────────────────────────────────────────────────────
def normalise_url(raw):
    """Ensure URL has a scheme; return None if unusable."""
    if not raw:
        return None
    raw = raw.strip().rstrip('/')
    if raw.startswith('//'):
        raw = 'https:' + raw
    if not raw.startswith(('http://', 'https://')):
        raw = 'https://' + raw
    # Basic sanity — must have a dot in the host
    try:
        p = urllib.parse.urlparse(raw)
        if '.' not in p.netloc:
            return None
    except Exception:
        return None
    return raw


def extract_hostname(url):
    try:
        return urllib.parse.urlparse(url).hostname or ''
    except Exception:
        return ''

# ── HTTP checker ───────────────────────────────────────────────────────────────
def http_check(url):
    """
    Returns dict:
      status_code  int | None
      final_url    str
      error        str | None
      is_dead      bool
      dead_reason  str | None
      body_snippet str (first 2 KB lowercased for keyword scan)
    """
    result = {
        'status_code': None,
        'final_url':   url,
        'error':       None,
        'is_dead':     False,
        'dead_reason': None,
        'body_snippet': '',
    }

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': UA,
            'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
        }
    )

    # Allow up to 3 redirects manually so we can capture the final URL
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE   # we do cert checks separately

    try:
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx),
            urllib.request.HTTPCookieProcessor(),
        )
        with opener.open(req, timeout=HTTP_TIMEOUT) as resp:
            result['status_code'] = resp.status
            result['final_url']   = resp.url

            # Read first 4 KB for keyword scanning
            raw = resp.read(4096)
            try:
                snippet = raw.decode('utf-8', errors='replace').lower()
            except Exception:
                snippet = ''
            result['body_snippet'] = snippet

    except urllib.error.HTTPError as e:
        result['status_code'] = e.code
        result['error']       = f'HTTP {e.code}'
        if e.code in (400, 404, 410, 451, 500, 502, 503, 521, 522, 523, 525):
            result['is_dead']     = True
            result['dead_reason'] = f'HTTP {e.code}'

    except urllib.error.URLError as e:
        reason = str(e.reason)
        result['error'] = reason
        # DNS / connection failures → dead
        if any(x in reason.lower() for x in
               ('name or service not known', 'nodename nor servname',
                'no address associated', 'connection refused',
                'connection timed out', 'network is unreachable',
                'errno 11001',   # Windows DNS fail
                'getaddrinfo failed')):
            result['is_dead']     = True
            result['dead_reason'] = 'DNS/connection failure'
        else:
            result['is_dead']     = True
            result['dead_reason'] = f'URLError: {reason[:80]}'

    except socket.timeout:
        result['error']       = 'timeout'
        result['is_dead']     = True
        result['dead_reason'] = 'timeout'

    except Exception as e:
        result['error']       = str(e)[:100]
        result['is_dead']     = True
        result['dead_reason'] = f'exception: {str(e)[:60]}'

    # Keyword scan on body if we got a 200 but body looks dead
    if not result['is_dead'] and result['body_snippet']:
        body = result['body_snippet']
        for kw in DEAD_KEYWORDS:
            if kw in body:
                result['is_dead']     = True
                result['dead_reason'] = f'keyword: "{kw}"'
                break

    return result


# ── SSL checker ────────────────────────────────────────────────────────────────
def ssl_check(hostname, port=443):
    """
    Returns dict:
      valid          bool
      expires_at     str (ISO) | None
      days_left      int | None
      error          str | None
      is_expired     bool
      is_urgent      bool   (< SSL_URGENT_DAYS)
      is_warning     bool   (< SSL_WARN_DAYS)
    """
    result = {
        'valid':      False,
        'expires_at': None,
        'days_left':  None,
        'error':      None,
        'is_expired': False,
        'is_urgent':  False,
        'is_warning': False,
    }

    if not hostname:
        result['error'] = 'no hostname'
        return result

    ctx = ssl.create_default_context()
    ctx.check_hostname = False   # we handle expiry ourselves
    ctx.verify_mode    = ssl.CERT_OPTIONAL

    try:
        with socket.create_connection((hostname, port), timeout=SSL_TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    result['error'] = 'no cert returned'
                    return result

                not_after = cert.get('notAfter')
                if not not_after:
                    result['error'] = 'no notAfter in cert'
                    return result

                # Parse: 'Jun 25 12:00:00 2025 GMT'
                expire_dt = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                expire_dt = expire_dt.replace(tzinfo=timezone.utc)
                now_utc   = datetime.now(timezone.utc)
                days_left = (expire_dt - now_utc).days

                result['valid']      = True
                result['expires_at'] = expire_dt.isoformat(timespec='seconds')
                result['days_left']  = days_left
                result['is_expired'] = days_left < 0
                result['is_urgent']  = 0 <= days_left < SSL_URGENT_DAYS
                result['is_warning'] = SSL_URGENT_DAYS <= days_left < SSL_WARN_DAYS

    except ssl.SSLCertVerificationError as e:
        result['error'] = f'SSL verify error: {str(e)[:80]}'
    except ssl.SSLError as e:
        result['error'] = f'SSL error: {str(e)[:80]}'
    except (socket.timeout, TimeoutError):
        result['error'] = 'SSL timeout'
    except ConnectionRefusedError:
        result['error'] = 'connection refused (no HTTPS?)'
    except OSError as e:
        result['error'] = f'OS error: {str(e)[:80]}'
    except Exception as e:
        result['error'] = f'exception: {str(e)[:80]}'

    return result


# ── Per-lead worker ────────────────────────────────────────────────────────────
def check_lead(lead, args):
    """
    Run HTTP + SSL checks for one lead.
    Returns a result dict.
    """
    lid      = lead['id']
    name     = lead.get('name', '')
    raw_url  = lead.get('website', '')
    city     = lead.get('city', '')
    status   = lead.get('status', '')

    url = normalise_url(raw_url)
    if not url:
        return {
            'id': lid, 'name': name, 'city': city, 'raw_url': raw_url,
            'url': None, 'http': None, 'ssl': None,
            'verdict': 'SKIP', 'reason': 'invalid URL', 'tag_applied': False,
        }

    hostname = extract_hostname(url)

    # ── HTTP check ──
    http = None
    if not args.ssl_only:
        http = http_check(url)

    # ── SSL check ──
    ssl_res = None
    if not args.dead_only and hostname:
        ssl_res = ssl_check(hostname)

    # ── Verdict ────
    is_dead = http.get('is_dead', False) if http else False

    if is_dead:
        verdict = 'DEAD'
        reason  = http.get('dead_reason', 'unknown')
    elif http and http.get('status_code') and http['status_code'] >= 400:
        verdict = 'ERROR'
        reason  = f"HTTP {http['status_code']}"
    elif http and http.get('error') and not http.get('status_code'):
        verdict = 'UNREACHABLE'
        reason  = http['error'][:60]
    else:
        verdict = 'OK'
        reason  = f"HTTP {http['status_code']}" if http and http.get('status_code') else 'SSL only'

    # SSL override: if SSL expired and site is otherwise alive → still valuable lead but note it
    ssl_note = ''
    if ssl_res:
        if ssl_res.get('is_expired'):
            ssl_note = f" | SSL EXPIRED {abs(ssl_res['days_left'])}d ago"
        elif ssl_res.get('is_urgent'):
            ssl_note = f" | SSL URGENT {ssl_res['days_left']}d left"
        elif ssl_res.get('is_warning'):
            ssl_note = f" | SSL {ssl_res['days_left']}d left"
        elif ssl_res.get('error'):
            ssl_note = f" | SSL err: {ssl_res['error'][:40]}"

    return {
        'id':          lid,
        'name':        name,
        'city':        city,
        'raw_url':     raw_url,
        'url':         url,
        'http':        http,
        'ssl':         ssl_res,
        'verdict':     verdict,
        'reason':      reason + ssl_note,
        'tag_applied': False,
    }


# ── DB writer ──────────────────────────────────────────────────────────────────
def apply_tags(results, dry_run):
    """Write status=dead_site and ssl info to Supabase for matching leads."""
    patched = 0
    for r in results:
        if r['verdict'] == 'SKIP':
            continue

        patch = {}

        # Tag dead sites
        if r['verdict'] in ('DEAD', 'UNREACHABLE') and r.get('http'):
            patch['status'] = 'dead_site'

        # Write SSL info into a JSON notes blob
        ssl_res = r.get('ssl')
        if ssl_res and ssl_res.get('valid'):
            days = ssl_res.get('days_left')
            # Store ssl_days_left as a note we can use for sniper hooks
            # We append to existing notes via a text prefix; store as structured JSON
            # using a dedicated column if it exists, else skip silently
            if days is not None:
                patch['ssl_days_left'] = days   # column must exist in beauty_leads

        if not patch:
            continue

        if dry_run:
            r['tag_applied'] = True   # mark for report even in dry-run
            continue

        code = sb_patch(r['id'], patch)
        r['tag_applied'] = code in (200, 204)
        if r['tag_applied']:
            patched += 1
        else:
            log(f"PATCH failed lead {r['id']} ({r['name']}): HTTP {code}", 'WARN')

    return patched


# ── Report printer ─────────────────────────────────────────────────────────────
def print_report(results, elapsed, dry_run, report_path=None):
    total       = len(results)
    ok_cnt      = sum(1 for r in results if r['verdict'] == 'OK')
    dead_cnt    = sum(1 for r in results if r['verdict'] == 'DEAD')
    unreach_cnt = sum(1 for r in results if r['verdict'] == 'UNREACHABLE')
    err_cnt     = sum(1 for r in results if r['verdict'] == 'ERROR')
    skip_cnt    = sum(1 for r in results if r['verdict'] == 'SKIP')
    tagged_cnt  = sum(1 for r in results if r['tag_applied'])

    ssl_expired = [r for r in results if r.get('ssl') and r['ssl'].get('is_expired')]
    ssl_urgent  = [r for r in results if r.get('ssl') and r['ssl'].get('is_urgent')]
    ssl_warn    = [r for r in results if r.get('ssl') and r['ssl'].get('is_warning')]
    no_ssl      = [r for r in results if r.get('ssl') and r['ssl'].get('error')]

    W = 68
    print(f'\n{"═"*W}')
    print(f'  SITE VERIFICATION REPORT{"  [DRY-RUN]" if dry_run else ""}')
    print(f'  Checked {total} sites in {elapsed:.1f}s')
    print(f'{"═"*W}')
    print(f'  ✅  OK / reachable:      {ok_cnt:>5}')
    print(f'  💀  Dead / parked:       {dead_cnt:>5}')
    print(f'  🔌  Unreachable:         {unreach_cnt:>5}')
    print(f'  ⚠️   HTTP error:          {err_cnt:>5}')
    print(f'  ⏭️   Skipped (no URL):    {skip_cnt:>5}')
    print(f'  🏷️   Tagged dead_site:    {tagged_cnt:>5}')
    print(f'{"─"*W}')
    print(f'  SSL expired:             {len(ssl_expired):>5}')
    print(f'  SSL urgent (<{SSL_URGENT_DAYS}d):       {len(ssl_urgent):>5}')
    print(f'  SSL warning (<{SSL_WARN_DAYS}d):      {len(ssl_warn):>5}')
    print(f'  SSL error / no HTTPS:    {len(no_ssl):>5}')
    print(f'{"═"*W}')

    # Top dead sites
    if dead_cnt + unreach_cnt > 0:
        print(f'\n  DEAD / UNREACHABLE SITES (first 20):')
        shown = 0
        for r in results:
            if r['verdict'] in ('DEAD', 'UNREACHABLE') and shown < 20:
                print(f'    [{r["id"]:>6}] {r["name"][:28]:<28}  {r["raw_url"][:40]:<40}  → {r["reason"][:50]}')
                shown += 1

    # Top SSL-urgent
    if ssl_urgent:
        print(f'\n  SSL URGENT (expires in <{SSL_URGENT_DAYS} days):')
        for r in ssl_urgent[:15]:
            days = r['ssl']['days_left']
            print(f'    [{r["id"]:>6}] {r["name"][:28]:<28}  {r["url"][:40]:<40}  → {days}d left')

    if ssl_warn:
        print(f'\n  SSL WARNING (expires in {SSL_URGENT_DAYS}–{SSL_WARN_DAYS} days):')
        for r in ssl_warn[:15]:
            days = r['ssl']['days_left']
            print(f'    [{r["id"]:>6}] {r["name"][:28]:<28}  {r["url"][:40]:<40}  → {days}d left')

    print()

    # JSON dump
    if report_path:
        out = {
            'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'summary': {
                'total': total, 'ok': ok_cnt, 'dead': dead_cnt,
                'unreachable': unreach_cnt, 'error': err_cnt, 'skip': skip_cnt,
                'tagged': tagged_cnt,
                'ssl_expired': len(ssl_expired), 'ssl_urgent': len(ssl_urgent),
                'ssl_warning': len(ssl_warn),
            },
            'results': [
                {
                    'id':      r['id'],
                    'name':    r['name'],
                    'url':     r['raw_url'],
                    'verdict': r['verdict'],
                    'reason':  r['reason'],
                    'http_status': r['http']['status_code'] if r.get('http') else None,
                    'ssl_days_left': r['ssl']['days_left'] if r.get('ssl') else None,
                    'ssl_expires_at': r['ssl']['expires_at'] if r.get('ssl') else None,
                }
                for r in results
            ]
        }
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        log(f'Report saved → {report_path}')


# ── Main ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='verify_berlin_sites — mass URL health check')
    p.add_argument('--city',     default='Berlin', help='City filter (default: Berlin)')
    p.add_argument('--limit',    type=int, default=0,
                   help='Max leads to process (default: all)')
    p.add_argument('--offset',   type=int, default=0, help='Skip first N leads')
    p.add_argument('--workers',  type=int, default=15,
                   help='Concurrent threads (default: 15, max recommended: 30)')
    p.add_argument('--dry-run',  action='store_true', dest='dry_run',
                   help='Check sites but do NOT write to Supabase')
    p.add_argument('--ssl-only', action='store_true', dest='ssl_only',
                   help='Skip HTTP check, only audit SSL certs')
    p.add_argument('--dead-only', action='store_true', dest='dead_only',
                   help='Skip SSL check, only detect and tag dead sites')
    p.add_argument('--status-filter', default=None, dest='status_filter',
                   help='Only check leads with this status (e.g. "READY TO SEND")')
    p.add_argument('--report',   default=None,
                   help='Path to save JSON report (e.g. data/berlin_site_report.json)')
    p.add_argument('--ids',      default='',
                   help='Comma-separated lead IDs to check (ignores city/limit)')
    return p.parse_args()


def main():
    args = parse_args()

    workers = min(max(1, args.workers), 50)   # hard-cap at 50
    dry     = args.dry_run

    print(f'\n{"═"*68}')
    print(f'  VERIFY BERLIN SITES  |  city={args.city}  |  workers={workers}')
    print(f'  {"DRY-RUN — no DB writes" if dry else "LIVE — will tag dead_site in Supabase"}')
    print(f'{"═"*68}\n')

    # ── Fetch leads ────────────────────────────────────────────────────────────
    if args.ids:
        id_list = [int(x.strip()) for x in args.ids.split(',') if x.strip()]
        # Fetch by IDs (two-step: fetch all Berlin, filter locally — avoids URL length issues)
        log(f'Fetching leads by ID list: {id_list}')
        all_leads = sb_fetch_all(args.city, args.status_filter)
        leads = [l for l in all_leads if l['id'] in id_list]
    else:
        log(f'Fetching leads for city={args.city}, status={args.status_filter or "any"}...')
        leads = sb_fetch_all(args.city, args.status_filter)

    if args.offset:
        leads = leads[args.offset:]
    if args.limit:
        leads = leads[:args.limit]

    if not leads:
        print('No leads with website field found. Check city / status filter.')
        return

    log(f'Processing {len(leads)} leads with {workers} workers...\n')
    start = time.time()

    # ── Concurrent checks ──────────────────────────────────────────────────────
    results  = []
    done_cnt = 0
    lock     = threading.Lock()

    def worker(lead):
        return check_lead(lead, args)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(worker, lead): lead for lead in leads}
        for fut in as_completed(futures):
            try:
                res = fut.result()
            except Exception as e:
                lead = futures[fut]
                res  = {
                    'id': lead['id'], 'name': lead.get('name', ''), 'city': lead.get('city', ''),
                    'raw_url': lead.get('website', ''), 'url': None,
                    'http': None, 'ssl': None,
                    'verdict': 'SKIP', 'reason': f'worker exception: {e}', 'tag_applied': False,
                }

            with lock:
                results.append(res)
                done_cnt += 1
                # Progress line (overwrite in terminal)
                pct     = done_cnt / len(leads) * 100
                verdict = res['verdict']
                sym     = {'OK': '✅', 'DEAD': '💀', 'UNREACHABLE': '🔌',
                           'ERROR': '⚠️', 'SKIP': '⏭️'}.get(verdict, '?')
                print(f'\r  [{done_cnt:>5}/{len(leads)}] {pct:5.1f}%  '
                      f'{sym} {res["name"][:25]:<25}  {verdict:<12}  {res["reason"][:40]}',
                      end='', flush=True)

    print()  # newline after progress
    elapsed = time.time() - start

    # ── Tag dead sites ─────────────────────────────────────────────────────────
    patched = apply_tags(results, dry_run=dry)
    if patched:
        log(f'Tagged {patched} leads as dead_site in Supabase.')
    elif dry:
        log('DRY-RUN: no DB writes performed.')

    # ── Report ─────────────────────────────────────────────────────────────────
    print_report(results, elapsed, dry_run=dry, report_path=args.report)


if __name__ == '__main__':
    main()
