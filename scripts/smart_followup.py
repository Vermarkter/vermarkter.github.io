#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_followup.py — Auto WhatsApp follow-up for leads who opened the email
but haven't replied within a configurable grace period.

Trigger condition (AND of all three):
  1. last_opened_at IS NOT NULL  (tracking pixel fired)
  2. last_opened_at <= NOW() - grace_hours  (grace period elapsed)
  3. status NOT IN replied statuses  (no reply yet: reply_hot / reply_info / reply_refused / replied)

Action:
  Prints (or sends) a personalized WhatsApp message template.
  Optionally patches status → 'followup_sent' in Supabase so we don't re-send.

WhatsApp message (German, warm tone):
  "Guten Tag [Name], wir haben gesehen, dass Sie sich unseren Audit angeschaut haben.
   Konnten Sie das Video bereits ansehen? Wir würden uns über Ihr Feedback freuen. 🎬"

Modes:
  --dry-run     Print messages, no Supabase write
  --send        Actually write status=followup_sent to Supabase
  --grace 2     Hours to wait after open before following up (default: 2)
  --ids 1,2,3   Process specific lead IDs only
  --city Berlin Filter by city
  --limit 50    Max leads per run

Usage:
  python scripts/smart_followup.py --dry-run
  python scripts/smart_followup.py --send --grace 3
  python scripts/smart_followup.py --ids 162,163 --dry-run
"""

import sys, io, os, json, time, argparse, configparser, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _e(k):  return (os.environ.get(k) or '').strip()
def _c(s, k): return (_cfg.get(s, k, fallback='') or '').strip()

def _valid_jwt(s):
    return s if (s and s.isascii() and s.startswith('eyJ') and len(s) > 80) else ''

SB_URL = _e('SUPABASE_URL') or _c('SUPABASE', 'url')
SB_KEY = (_e('SUPABASE_KEY')
          or _valid_jwt(_c('SUPABASE', 'service_role_key'))
          or _valid_jwt(_c('SUPABASE', 'anon_key')))

if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE_URL / KEY not configured.', file=sys.stderr)
    sys.exit(1)

# Statuses that mean "already replied — skip follow-up"
REPLIED_STATUSES = {'reply_hot', 'reply_info', 'reply_refused', 'replied',
                    'followup_sent', 'booked', 'CALLED'}

_SB_R = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
_SB_W = {**_SB_R, 'Content-Type': 'application/json; charset=utf-8', 'Prefer': 'return=minimal'}

# ── Supabase helpers ──────────────────────────────────────────────────────────

def sb_fetch_opened_leads(grace_hours: float, ids: set, city: str, limit: int) -> list:
    """
    Fetch leads where:
      - last_opened_at IS NOT NULL
      - last_opened_at <= now() - grace_hours
      - status NOT IN replied statuses
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=grace_hours)).isoformat()

    params = {
        'select':         'id,name,phone,city,addr,status,last_opened_at',
        'last_opened_at': f'not.is.null',
        'order':          'last_opened_at.desc',
    }

    if ids:
        id_str = ','.join(str(i) for i in sorted(ids))
        params = {
            'id':     f'in.({id_str})',
            'select': params['select'],
        }
    else:
        params['last_opened_at'] = f'lte.{cutoff}'
        if city:
            params['city'] = f'eq.{city}'
        if limit:
            params['limit'] = str(limit)

    qs  = '&'.join(f"{k}={urllib.parse.quote(str(v), safe=':.,*()!-')}"
                   for k, v in params.items())
    url = f"{SB_URL}/rest/v1/beauty_leads?{qs}"

    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=_SB_R), timeout=20
        ) as r:
            leads = json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f'[ERROR] Supabase fetch failed: {e}', file=sys.stderr)
        return []

    # Filter out already-replied in Python (PostgREST `not.in` syntax is tricky)
    cutoff_dt = datetime.now(timezone.utc) - timedelta(hours=grace_hours)
    result = []
    for lead in leads:
        if lead.get('status') in REPLIED_STATUSES:
            continue
        opened_raw = lead.get('last_opened_at')
        if not opened_raw:
            continue
        # Parse ISO timestamp from Supabase
        try:
            opened_dt = datetime.fromisoformat(opened_raw.replace('Z', '+00:00'))
        except ValueError:
            continue
        if ids:
            result.append(lead)
        elif opened_dt <= cutoff_dt:
            result.append(lead)

    return result


def sb_patch_followup(lead_id: int) -> str:
    url  = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    data = json.dumps({'status': 'followup_sent'}, ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(url, data=data, headers=_SB_W, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=20):
            return 'OK'
    except urllib.request.HTTPError as e:
        return f'ERR {e.code}'
    except Exception as e:
        return f'ERR {e}'


# ── Message builder ───────────────────────────────────────────────────────────

def build_wa_message(lead: dict) -> str:
    """
    Personalized WhatsApp follow-up message.
    Warm, short, non-pushy — references their specific action (opened the email).
    """
    name = lead.get('name', '').strip()
    # Extract salon first name for greeting if name is long (e.g. "Pink & Grey Nails Berlin")
    # Use full name — more professional in B2B context
    greeting_name = name if name else 'Guten Tag'

    opened_raw = lead.get('last_opened_at', '')
    opened_time = ''
    if opened_raw:
        try:
            dt = datetime.fromisoformat(opened_raw.replace('Z', '+00:00'))
            local_hour = dt.hour  # UTC — Berlin is UTC+1/+2, close enough for "Heute/Gestern"
            now_utc = datetime.now(timezone.utc)
            delta_h = (now_utc - dt).total_seconds() / 3600
            if delta_h < 24:
                opened_time = 'heute'
            elif delta_h < 48:
                opened_time = 'gestern'
            else:
                opened_time = 'vor Kurzem'
        except ValueError:
            opened_time = 'kürzlich'

    msg = (
        f"Guten Tag, {greeting_name}! 👋\n\n"
        f"Wir haben gesehen, dass Sie sich {opened_time} unseren digitalen Audit "
        f"angeschaut haben — vielen Dank dafür! 🙏\n\n"
        f"Konnten Sie das Video bereits ansehen? "
        f"Wir würden uns sehr über Ihr kurzes Feedback freuen. 🎬\n\n"
        f"Falls Sie Fragen haben oder eine kurze Demo wünschen — "
        f"ich bin gerne für Sie da!\n\n"
        f"Mit freundlichen Grüßen,\nVermarkter Team"
    )
    return msg


def format_phone(phone: str) -> str:
    """Normalizes phone to international format hint for WhatsApp."""
    if not phone:
        return '—'
    digits = ''.join(c for c in phone if c.isdigit() or c == '+')
    if digits.startswith('0') and not digits.startswith('00'):
        digits = '+49' + digits[1:]
    elif digits.startswith('00'):
        digits = '+' + digits[2:]
    return digits


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description='Send WhatsApp follow-up to leads who opened email but not replied'
    )
    p.add_argument('--grace',   type=float, default=2.0,
                   help='Hours after open before follow-up triggers (default: 2)')
    p.add_argument('--ids',     default='', help='Comma-separated lead IDs to force-check')
    p.add_argument('--city',    default='', help='Filter by city')
    p.add_argument('--limit',   type=int, default=100, help='Max leads per run (default: 100)')
    p.add_argument('--send',    action='store_true',
                   help='Patch status=followup_sent in Supabase after printing')
    p.add_argument('--dry-run', action='store_true',
                   help='Print messages only, no Supabase write (default behavior)')
    return p.parse_args()


def main():
    args  = parse_args()
    live  = args.send and not args.dry_run
    ids   = {int(x.strip()) for x in args.ids.split(',') if x.strip()} if args.ids else set()

    print(f'\n{"="*64}')
    print(f'  Smart Follow-up  |  grace={args.grace}h  |  {"LIVE — will patch Supabase" if live else "DRY-RUN"}')
    if ids:
        print(f'  ID filter: {sorted(ids)}')
    print(f'{"="*64}\n')

    leads = sb_fetch_opened_leads(args.grace, ids, args.city, args.limit)
    print(f'  Leads eligible for follow-up: {len(leads)}\n')

    if not leads:
        print('  Nothing to do.')
        print('  (Either no leads opened email yet, grace period not elapsed,')
        print('   or all openers already have a reply status.)\n')
        return

    sent_count = 0

    for lead in leads:
        lead_id   = lead['id']
        name      = lead.get('name', f'id={lead_id}')
        phone     = format_phone(lead.get('phone') or '')
        status    = lead.get('status', '?')
        opened_at = lead.get('last_opened_at', '?')
        city      = lead.get('city', '')

        msg = build_wa_message(lead)

        print(f'  ─── id={lead_id} | {name} | {city}')
        print(f'      Status: {status}  |  Opened: {opened_at}')
        print(f'      Phone:  {phone}')
        print(f'      WhatsApp URL: https://wa.me/{phone.replace("+", "").replace(" ", "")}')
        print()
        print('  ┌─ MESSAGE ' + '─' * 50)
        for line in msg.split('\n'):
            print(f'  │ {line}')
        print('  └' + '─' * 60)
        print()

        if live:
            result = sb_patch_followup(lead_id)
            print(f'      Supabase patch → followup_sent: [{result}]')
            if result == 'OK':
                sent_count += 1
        else:
            sent_count += 1

        time.sleep(0.1)

    print(f'{"="*64}')
    print(f'  DONE — {len(leads)} leads processed | {sent_count} messages {"sent" if live else "ready to send"}')
    if not live:
        print('  Add --send flag to mark leads as followup_sent in Supabase.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
