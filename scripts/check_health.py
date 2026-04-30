#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_health.py — Server health check for Vermarkter outreach stack.

Checks:
  1. Disk usage (/, /opt/vermarkter)
  2. Supabase connectivity (beauty_leads count)
  3. Today's send stats (whatsapp_logs + EMAIL SENT from beauty_leads)
  4. Leads pipeline summary (READY TO SEND remaining)

Usage:
  python3 scripts/check_health.py
  python3 scripts/check_health.py --json      # machine-readable JSON output
  python3 scripts/check_health.py --city Berlin
"""

import sys, io, os, json, time, argparse, urllib.request, urllib.parse, configparser, shutil
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    SB_URL = ''
    SB_KEY = ''

HDRS = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Prefer': 'count=exact',
    'Range-Unit': 'items',
    'Range': '0-0',
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def _sb_count(endpoint, params=''):
    """Return (count, error_str). count=-1 on failure."""
    url = f"{SB_URL}/rest/v1/{endpoint}?select=id{params}"
    req = urllib.request.Request(url, headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            cr = r.headers.get('Content-Range', '*/0')
            total = cr.split('/')[-1]
            return int(total) if total != '*' else -1, None
    except urllib.request.HTTPError as e:
        return -1, f"HTTP {e.code}"
    except Exception as e:
        return -1, str(e)[:80]


def _sb_json(endpoint, params=''):
    url = f"{SB_URL}/rest/v1/{endpoint}?{params}"
    req = urllib.request.Request(url, headers={**HDRS, 'Range': '0-999'})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode('utf-8')), None
    except urllib.request.HTTPError as e:
        return [], f"HTTP {e.code}"
    except Exception as e:
        return [], str(e)[:80]


def _disk(path='/'):
    try:
        usage = shutil.disk_usage(path)
        total_gb = usage.total / 1e9
        used_gb  = usage.used  / 1e9
        free_gb  = usage.free  / 1e9
        pct      = usage.used / usage.total * 100
        return {'path': path, 'total_gb': round(total_gb, 1),
                'used_gb': round(used_gb, 1), 'free_gb': round(free_gb, 1),
                'used_pct': round(pct, 1)}
    except Exception as e:
        return {'path': path, 'error': str(e)}


def _ok(val):  return '✓' if val else '✗'
def _warn(pct): return '⚠' if pct > 80 else ''

# ── Main ───────────────────────────────────────────────────────────────────────
def run(city=None, as_json=False):
    result = {}
    now_utc = datetime.now(timezone.utc)
    today   = now_utc.strftime('%Y-%m-%d')

    # 1. Disk
    disks = []
    for path in ['/', '/opt/vermarkter', _ROOT]:
        if os.path.exists(path):
            d = _disk(path)
            if 'error' not in d and not any(x['path'] == path for x in disks):
                disks.append(d)
    result['disk'] = disks

    # 2. Supabase ping — beauty_leads total
    if SB_URL and SB_KEY:
        total_leads, err = _sb_count('beauty_leads')
        result['supabase'] = {
            'ok': err is None and total_leads >= 0,
            'total_leads': total_leads,
            'error': err,
        }

        # 3a. Email stats today (EMAIL SENT in beauty_leads — no timestamp filter,
        #     but whatsapp_logs has sent_at so we can do real today filter)
        email_today, _ = _sb_count(
            'beauty_leads',
            f'&status=eq.EMAIL SENT'
        )

        # 3b. WhatsApp logs today
        today_start = today + 'T00:00:00+00:00'
        wa_today, wa_err = _sb_count(
            'whatsapp_logs',
            f'&sent_at=gte.{urllib.parse.quote(today_start, safe="")}'
        )
        wa_sent, _    = _sb_count(
            'whatsapp_logs',
            f'&sent_at=gte.{urllib.parse.quote(today_start, safe="")}&delivery_status=eq.sent'
        )
        wa_failed, _  = _sb_count(
            'whatsapp_logs',
            f'&sent_at=gte.{urllib.parse.quote(today_start, safe="")}&delivery_status=eq.failed'
        )

        # 3c. Pipeline
        ready_params = '&status=eq.READY TO SEND'
        if city:
            ready_params += f'&city=eq.{urllib.parse.quote(city, safe="")}'
        ready, _ = _sb_count('beauty_leads', ready_params)

        berlin_ready, _ = _sb_count('beauty_leads', '&status=eq.READY TO SEND&city=eq.Berlin')
        total_sent, _   = _sb_count('beauty_leads', '&status=in.(sent,EMAIL SENT)')

        result['stats'] = {
            'date':          today,
            'email_sent_total':  email_today,
            'wa_today':      wa_today,
            'wa_sent_today': wa_sent,
            'wa_failed_today': wa_failed,
            'wa_table_ok':   wa_err is None,
            'ready_to_send': ready,
            'berlin_ready':  berlin_ready,
            'total_sent_ever': total_sent,
        }
    else:
        result['supabase'] = {'ok': False, 'error': 'config.ini not found or missing SUPABASE section'}
        result['stats'] = {}

    # 4. Log files
    log_dir = os.path.join(_ROOT, 'logs')
    logs = {}
    for name in ['sniper_engine.log', 'mass_email.log', 'lead_harvester.log']:
        p = os.path.join(log_dir, name)
        if os.path.exists(p):
            size = os.path.getsize(p)
            try:
                with open(p, encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                last = lines[-1].strip() if lines else ''
            except Exception:
                last = ''
            logs[name] = {'size_kb': round(size / 1024, 1), 'last_line': last[-120:]}
        else:
            logs[name] = {'size_kb': 0, 'last_line': 'file not found'}
    result['logs'] = logs

    result['checked_at'] = now_utc.isoformat(timespec='seconds')

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # ── Pretty print ───────────────────────────────────────────────────────────
    W = 60
    print(f'\n{"═"*W}')
    print(f'  VERMARKTER — SERVER HEALTH CHECK')
    print(f'  {now_utc.strftime("%Y-%m-%d %H:%M:%S UTC")}')
    print(f'{"═"*W}')

    # Disk
    print(f'\n  DISK USAGE')
    for d in result['disk']:
        if 'error' in d:
            print(f'    {d["path"]:30s}  ERROR: {d["error"]}')
        else:
            bar_len = 20
            filled  = int(bar_len * d['used_pct'] / 100)
            bar     = '█' * filled + '░' * (bar_len - filled)
            warn    = _warn(d['used_pct'])
            print(f'    {d["path"]:20s}  [{bar}] {d["used_pct"]:5.1f}%  '
                  f'{d["used_gb"]:.1f}/{d["total_gb"]:.1f} GB  {warn}')

    # Supabase
    sb = result.get('supabase', {})
    print(f'\n  SUPABASE')
    status_sym = _ok(sb.get('ok'))
    if sb.get('ok'):
        print(f'    {status_sym} Connected  |  beauty_leads: {sb["total_leads"]:,} rows')
    else:
        print(f'    {status_sym} UNREACHABLE  |  {sb.get("error", "?")}')

    # Stats
    st = result.get('stats', {})
    if st:
        print(f'\n  TODAY\'S STATS  ({st.get("date", today)})')
        print(f'    Emails sent (total/EMAIL SENT):  {st.get("email_sent_total", "?"):>6}')
        wt = st.get("wa_table_ok")
        wa_label = '' if wt else '  ⚠ whatsapp_logs table missing'
        print(f'    WA messages today:               {st.get("wa_today", "?"):>6}{wa_label}')
        print(f'      ├─ delivered:                  {st.get("wa_sent_today", "?"):>6}')
        print(f'      └─ failed:                     {st.get("wa_failed_today", "?"):>6}')
        print(f'\n  PIPELINE')
        if city:
            print(f'    Ready to send ({city}):          {st.get("ready_to_send", "?"):>6}')
        else:
            print(f'    Ready to send (all):             {st.get("ready_to_send", "?"):>6}')
        print(f'    Ready — Berlin:                  {st.get("berlin_ready", "?"):>6}')
        print(f'    Total sent ever:                 {st.get("total_sent_ever", "?"):>6}')

    # Logs
    print(f'\n  LOG FILES')
    for name, info in result['logs'].items():
        print(f'    {name:<30s}  {info["size_kb"]:>7.1f} KB')
        if info['last_line'] and info['last_line'] != 'file not found':
            print(f'      └─ {info["last_line"]}')

    print(f'\n{"═"*W}\n')


def main():
    p = argparse.ArgumentParser(description='Vermarkter server health check')
    p.add_argument('--city', default=None, help='City filter for pipeline stats')
    p.add_argument('--json', action='store_true', dest='as_json', help='Output raw JSON')
    args = p.parse_args()
    run(city=args.city, as_json=args.as_json)


if __name__ == '__main__':
    main()
