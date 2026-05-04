#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mass_email_sender.py — Brevo API email sender for Vermarkter outreach.

Fetches leads with status='READY TO SEND' and a non-empty email from Supabase,
sends personalized emails via Brevo (Sendinblue) API, then patches status →
'EMAIL SENT' and logs the result.

Usage:
  python3 scripts/mass_email_sender.py              # up to 300 emails (daily limit)
  python3 scripts/mass_email_sender.py --limit 50   # custom batch size
  python3 scripts/mass_email_sender.py --dry-run    # generate only, no send + no DB write
  python3 scripts/mass_email_sender.py --city Berlin --limit 100
  python3 scripts/mass_email_sender.py --ids 45,46,47

Config required:
  /opt/vermarkter/.env  →  BREVO_API_KEY=xkeysib-...
  OR config.ini [BREVO] api_key = xkeysib-...

Brevo Free plan: 300 emails/day, 9000/month. No credit card needed.
"""

import sys, io, os, json, time, argparse, urllib.request, urllib.parse, configparser, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from holiday_guard import guard_dispatch

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

# Supabase
SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

# Brevo: .env takes priority over config.ini
BREVO_KEY = (
    _env.get('BREVO_API_KEY')
    or os.environ.get('BREVO_API_KEY', '')
    or _cfg.get('BREVO', 'api_key', fallback='')
).strip()

FROM_EMAIL = _cfg.get('BREVO', 'from_email', fallback='hello@vermarkter.eu').strip()
FROM_NAME  = _cfg.get('BREVO', 'from_name',  fallback='Vermarkter').strip()
DAILY_CAP  = int(_cfg.get('BREVO', 'daily_limit', fallback='300'))

BREVO_SEND_URL    = 'https://api.brevo.com/v3/smtp/email'
BREVO_ACCOUNT_URL = 'https://api.brevo.com/v3/account'

# Zoho SMTP fallback (used only when Brevo returns HTTP 429 / daily limit reached)
ZOHO_HOST  = _cfg.get('ZOHO', 'smtp_host',  fallback='smtp.zoho.eu').strip()
ZOHO_PORT  = int(_cfg.get('ZOHO', 'smtp_port', fallback='587'))
ZOHO_USER  = (_env.get('ZOHO_USER') or os.environ.get('ZOHO_USER', '')
              or _cfg.get('ZOHO', 'username', fallback='')).strip()
ZOHO_PASS  = (_env.get('ZOHO_PASS') or os.environ.get('ZOHO_PASS', '')
              or _cfg.get('ZOHO', 'password', fallback='')).strip()
ZOHO_FROM  = _cfg.get('ZOHO', 'from_email', fallback=FROM_EMAIL).strip()

_brevo_limit_hit = False   # module-level flag — set True when Brevo returns 429

if not BREVO_KEY or 'PASTE' in BREVO_KEY or not BREVO_KEY.startswith('xkeysib-'):
    print('[ERROR] BREVO_API_KEY not set or invalid.\n'
          '  Add to /opt/vermarkter/.env:\n'
          '  BREVO_API_KEY=xkeysib-...', file=sys.stderr)
    sys.exit(1)

HDRS_SB_GET = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
}
HDRS_SB_PATCH = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}
HDRS_BREVO = {
    'api-key': BREVO_KEY,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# ---------------------------------------------------------------------------
# Email template
# ---------------------------------------------------------------------------
EMAIL_SUBJECT = "Digitale Lösung für {name} — Demo in 60 Sekunden"

EMAIL_HTML = """\
<!DOCTYPE html>
<html lang="de">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;font-size:15px;line-height:1.6;color:#222;max-width:600px;margin:0 auto;padding:20px">
<p>{message}</p>
<hr style="border:none;border-top:1px solid #eee;margin:24px 0">
<p style="font-size:13px;color:#666">
  <strong>Vermarkter</strong> — Digitales Marketing für Salons &amp; Studios<br>
  <a href="https://vermarkter.github.io/de/" style="color:#2563eb">vermarkter.github.io</a> |
  <a href="mailto:hello@vermarkter.eu" style="color:#2563eb">hello@vermarkter.eu</a>
</p>
<p style="font-size:11px;color:#aaa">
  Sie erhalten diese Nachricht, weil Ihr Salon in unserer Recherche als potenzielle Partnerschaft identifiziert wurde.
  <a href="mailto:hello@vermarkter.eu?subject=Abmeldung" style="color:#aaa">Abmelden</a>
</p>
</body>
</html>
"""

EMAIL_TEXT = "{message}\n\n--\nVermarkter — Digitales Marketing\nhttps://vermarkter.github.io/de/\nhello@vermarkter.eu"

# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------
FIELDS = 'id,name,city,district,email,custom_message,status'

def fetch_leads(city=None, limit=300, offset=0, ids=None):
    if ids:
        id_list = ','.join(str(i) for i in ids)
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&id=in.({id_list})"
               f"&email=not.is.null"
               f"&email=neq."
               f"&custom_message=not.is.null"
               f"&order=id.asc")
    else:
        filters = (f"&status=eq.READY%20TO%20SEND"
                   f"&email=not.is.null"
                   f"&custom_message=not.is.null"
                   f"&order=id.asc"
                   f"&limit={limit}"
                   f"&offset={offset}")
        if city:
            filters = f"&city=eq.{urllib.parse.quote(city, safe='')}" + filters
        url = f"{SB_URL}/rest/v1/beauty_leads?select={FIELDS}" + filters

    req = urllib.request.Request(url, headers=HDRS_SB_GET)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def patch_lead_sent(lead_id):
    payload = json.dumps({'status': 'EMAIL SENT'}).encode('utf-8')
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=payload, headers=HDRS_SB_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code

# ---------------------------------------------------------------------------
# Brevo API helpers
# ---------------------------------------------------------------------------
def brevo_account_info():
    req = urllib.request.Request(BREVO_ACCOUNT_URL, headers=HDRS_BREVO)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception:
        return {}


def brevo_send(to_email, to_name, subject, html_body, text_body):
    payload = json.dumps({
        'sender':  {'name': FROM_NAME, 'email': FROM_EMAIL},
        'to':      [{'email': to_email, 'name': to_name}],
        'subject': subject,
        'htmlContent': html_body,
        'textContent': text_body,
        'replyTo': {'email': FROM_EMAIL, 'name': FROM_NAME},
        'headers': {'X-Mailer': 'Vermarkter-Sniper/1.0'},
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(BREVO_SEND_URL, data=payload, headers=HDRS_BREVO, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            resp = json.loads(r.read().decode('utf-8'))
            return True, resp.get('messageId', 'ok')
    except urllib.request.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        if e.code == 429:
            global _brevo_limit_hit
            _brevo_limit_hit = True
        return False, f"HTTP {e.code}: {body[:200]}"


def zoho_send(to_email, to_name, subject, html_body, text_body):
    """Send via Zoho SMTP (fallback when Brevo daily limit is hit)."""
    if not ZOHO_USER or not ZOHO_PASS:
        return False, 'Zoho credentials not configured (ZOHO_USER / ZOHO_PASS missing)'

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'{FROM_NAME} <{ZOHO_FROM}>'
    msg['To']      = f'{to_name} <{to_email}>'
    msg['Reply-To'] = ZOHO_FROM
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html',  'utf-8'))

    try:
        with smtplib.SMTP(ZOHO_HOST, ZOHO_PORT, timeout=20) as s:
            s.ehlo()
            s.starttls()
            s.login(ZOHO_USER, ZOHO_PASS)
            s.sendmail(ZOHO_FROM, [to_email], msg.as_bytes())
        return True, 'zoho-smtp-ok'
    except smtplib.SMTPAuthenticationError as e:
        return False, f'Zoho auth error: {e}'
    except smtplib.SMTPException as e:
        return False, f'Zoho SMTP error: {e}'


def send_with_fallback(to_email, to_name, subject, html_body, text_body):
    """Try Brevo first; on 429 (daily limit) switch to Zoho SMTP for this run."""
    global _brevo_limit_hit

    if not _brevo_limit_hit:
        ok, result = brevo_send(to_email, to_name, subject, html_body, text_body)
        if ok:
            return True, 'brevo', result
        if _brevo_limit_hit:
            print('  [FALLBACK] Brevo limit hit — switching to Zoho SMTP', flush=True)
            ok2, res2 = zoho_send(to_email, to_name, subject, html_body, text_body)
            return ok2, 'zoho', res2
        return False, 'brevo', result

    # Already in Zoho mode for this run
    ok, result = zoho_send(to_email, to_name, subject, html_body, text_body)
    return ok, 'zoho', result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='mass_email_sender — Brevo API outreach')
    p.add_argument('--city',    default=None,  help='City filter (default: all cities)')
    p.add_argument('--limit',   type=int, default=DAILY_CAP, help=f'Max emails (default: {DAILY_CAP})')
    p.add_argument('--offset',  type=int, default=0, help='Supabase offset (default: 0)')
    p.add_argument('--ids',     default='', help='Comma-separated IDs to target')
    p.add_argument('--dry-run', action='store_true', help='Build emails but do NOT send or write to DB')
    p.add_argument('--delay',   type=float, default=0.4, help='Seconds between sends (default: 0.4)')
    return p.parse_args()


def main():
    args = parse_args()
    if not args.dry_run:
        guard_dispatch('mass_email_sender')
    dry  = args.dry_run
    limit = min(args.limit, DAILY_CAP)
    ids  = [int(x.strip()) for x in args.ids.split(',') if x.strip()] if args.ids else None

    print(f'\n{"="*64}')
    print(f'  Mass Email Sender  |  Engine: Brevo API  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  From: {FROM_EMAIL}  |  Daily cap: {DAILY_CAP}  |  This run: {limit}')
    if args.city: print(f'  City filter: {args.city}')
    if ids:       print(f'  IDs override: {ids}')
    print(f'{"="*64}')

    # Verify Brevo account
    if not dry:
        acc = brevo_account_info()
        if acc.get('email'):
            plan = acc.get('plan', [{}])[0].get('type', '?') if acc.get('plan') else '?'
            print(f'  Brevo account: {acc["email"]} | Plan: {plan}')
        else:
            print('  [WARN] Could not verify Brevo account — check API key')
    print()

    leads = fetch_leads(city=args.city, limit=limit, offset=args.offset, ids=ids)
    if not leads:
        print('No leads found matching criteria (status=READY TO SEND, email not null).')
        return

    # Filter out leads without email
    leads = [l for l in leads if l.get('email', '').strip()]
    print(f'Fetched {len(leads)} leads with email. Sending...\n')

    ok = fail = skipped = 0

    for lead in leads:
        lid     = lead['id']
        name    = lead.get('name', 'Salon')
        email   = lead['email'].strip()
        message = (lead.get('custom_message') or '').strip()

        if not message:
            print(f'  [SKIP] id={lid} «{name}» — no custom_message')
            skipped += 1
            continue

        subject   = EMAIL_SUBJECT.format(name=name)
        html_body = EMAIL_HTML.format(message=message.replace('\n', '<br>'))
        text_body = EMAIL_TEXT.format(message=message)

        print(f'  [SEND] id={lid} «{name}» → {email}')

        if dry:
            print(f'         Subject: {subject}')
            print(f'         Preview: {message[:80].replace(chr(10)," ")}...')
            print(f'         → [DRY-RUN, not sent]')
            ok += 1
        else:
            success, engine, result = send_with_fallback(email, name, subject, html_body, text_body)
            if success:
                code = patch_lead_sent(lid)
                db_sym = 'DB OK' if code in (200, 204) else f'DB ERR {code}'
                print(f'         → [SENT via {engine.upper()}] msgId={result} | [{db_sym}]')
                ok += 1
            else:
                print(f'         → [FAIL via {engine.upper()}] {result}', file=sys.stderr)
                fail += 1

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — total={ok+fail+skipped} | sent={ok} | skipped={skipped} | fail={fail}')
    if dry:
        print('  DRY-RUN: nothing sent or written to DB.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
