#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_email_brevo.py — Vermarkter Elite Email Sender via Brevo API.

Reads leads from Supabase (status=email_ready, has email_funnel_json),
renders personalized HTML emails with:
  • Street View facade photo as first screen (if street_view_url is set)
  • 1x1 tracking pixel linked to /api/track?id={lead_id}
  • Personalized subject + body from email_funnel_json.letter_1_digital_mirror

Usage:
  python scripts/send_email_brevo.py --dry-run
  python scripts/send_email_brevo.py --ids 260,261,262 --dry-run
  python scripts/send_email_brevo.py --letter letter_2_future_vision
  python scripts/send_email_brevo.py --limit 10

Requirements:
  config.ini [BREVO] api_key
  config.ini [SUPABASE] url + service_role_key
  Columns in beauty_leads: email, email_funnel_json, street_view_url, last_opened_at
"""

import sys, io, os, json, time, argparse, configparser, urllib.request, urllib.parse, html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Config ────────────────────────────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _env(k):  return (os.environ.get(k) or '').strip()
def _c(s, k): return (_cfg.get(s, k, fallback='') or '').strip()

SB_URL   = _env('SUPABASE_URL')  or _c('SUPABASE', 'url')
SB_KEY   = _env('SUPABASE_KEY')  or _c('SUPABASE', 'service_role_key') or _c('SUPABASE', 'anon_key')
BREVO_KEY     = _env('BREVO_API_KEY') or _c('BREVO', 'api_key')
FROM_EMAIL    = _c('BREVO', 'from_email') or 'hello@vermarkter.eu'
FROM_NAME     = _c('BREVO', 'from_name')  or 'Vermarkter'
DAILY_LIMIT   = int(_c('BREVO', 'daily_limit') or 300)
TRACK_BASE_URL = 'https://vermarkter.vercel.app/api/track'

if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE_URL / SUPABASE_KEY not configured.', file=sys.stderr)
    sys.exit(1)
if not BREVO_KEY or 'PASTE' in BREVO_KEY:
    print('[ERROR] BREVO api_key not configured in config.ini [BREVO].', file=sys.stderr)
    sys.exit(1)

# ── Supabase ──────────────────────────────────────────────────────────────────

_SB_READ  = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
_SB_PATCH = {**_SB_READ, 'Content-Type': 'application/json; charset=utf-8', 'Prefer': 'return=minimal'}


def sb_get(path, params=None):
    url = f"{SB_URL}/rest/v1/{path}"
    if params:
        url += '?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=_SB_READ), timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def sb_patch(lead_id, payload):
    url  = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(url, data=data, headers=_SB_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 'OK'
    except urllib.request.HTTPError as e:
        return f'ERR {e.code}'


def fetch_leads(ids: set, limit: int, city: str) -> list:
    params = {
        'status': 'eq.email_ready',
        'select': 'id,name,email,city,addr,street_view_url,email_funnel_json',
        'order':  'id.asc',
    }
    if ids:
        params = {'id': f'in.({",".join(str(i) for i in sorted(ids))})',
                  'select': params['select']}
    else:
        if city:
            params['city'] = f'eq.{city}'
        if limit:
            params['limit'] = str(limit)

    leads = sb_get('beauty_leads', params)
    return [l for l in leads if l.get('email') and l.get('email_funnel_json')]


# ── Email HTML builder ────────────────────────────────────────────────────────

LOGO_HTML = """
<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding:40px 0 20px;">
      <div style="
        font-family:'Courier New',monospace;
        font-size:22px;
        font-weight:bold;
        letter-spacing:4px;
        color:#d4a847;
        background:#0a0a0a;
        padding:18px 32px;
        border:1px solid #d4a847;
        display:inline-block;
      ">VERMARKTER</div>
      <div style="font-family:'Courier New',monospace;font-size:11px;color:#666;
                  letter-spacing:3px;margin-top:6px;">
        DIGITAL INFRASTRUCTURE FOR BERLIN'S BEST
      </div>
    </td>
  </tr>
</table>
"""


def build_street_view_block(sv_url: str, addr: str, demo_url: str = '') -> str:
    """
    Facade photo with a centered Play-button overlay — looks like a video thumbnail.
    The entire block is a clickable link to demo_url (if provided).
    Works in Gmail, Apple Mail, Outlook Web, iOS/Android mail apps.
    """
    street      = addr.split(',')[0].strip() if addr else 'Ihrem Salon'
    safe_street = html.escape(street)
    safe_photo  = html.escape(sv_url)
    safe_demo   = html.escape(demo_url) if demo_url else '#'

    # SVG Play button: white circle + red filled triangle, semi-transparent bg
    play_svg = (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "width='88' height='88' viewBox='0 0 88 88'%3E"
        "%3Ccircle cx='44' cy='44' r='44' fill='rgba(0,0,0,0.55)'/%3E"
        "%3Ccircle cx='44' cy='44' r='42' fill='none' "
        "stroke='rgba(255,255,255,0.9)' stroke-width='2'/%3E"
        "%3Cpolygon points='35,28 35,60 64,44' fill='%23ff0000'/%3E"
        "%3C/svg%3E"
    )

    return f"""
<table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr>
    <td align="center" style="padding:0 0 0;">
      <!--[if !mso]><!-->
      <a href="{safe_demo}" target="_blank"
         style="display:block;position:relative;font-size:0;line-height:0;
                text-decoration:none;border-radius:4px 4px 0 0;overflow:hidden;">
        <img src="{safe_photo}"
             width="600" height="400"
             alt="Ihr Salon — {safe_street}"
             style="display:block;width:100%;max-width:600px;height:auto;
                    border:0;border-radius:4px 4px 0 0;" />
        <!-- Play overlay: centered absolutely over the photo -->
        <img src="{play_svg}"
             width="88" height="88"
             alt=""
             style="display:block;position:absolute;
                    top:50%;left:50%;
                    margin-top:-44px;margin-left:-44px;
                    border:0;pointer-events:none;" />
      </a>
      <!--<![endif]-->
      <!--[if mso]>
      <a href="{safe_demo}" target="_blank">
        <img src="{safe_photo}" width="600" height="400"
             alt="Ihr Salon" style="display:block;border:0;" />
      </a>
      <![endif]-->
    </td>
  </tr>
  <tr>
    <td align="center"
        style="background:#111;padding:12px 24px 20px;
               border-radius:0 0 4px 4px;border:1px solid #222;">
      <a href="{safe_demo}" target="_blank" style="text-decoration:none;">
        <span style="font-family:'Courier New',monospace;font-size:12px;
                     color:#888;letter-spacing:1px;">
          Ich war heute digital vor Ihrem Salon in
          <strong style="color:#d4a847;">{safe_street}</strong> —
          und habe etwas Wichtiges entdeckt.
          <span style="color:#ff4444;font-weight:bold;">▶ Video ansehen</span>
        </span>
      </a>
    </td>
  </tr>
</table>
"""


def build_logo_fallback_block() -> str:
    return LOGO_HTML


def build_demo_url(salon_name: str = '') -> str:
    base = 'https://vermarkter.vercel.app/services/beauty-industry/de/'
    if salon_name:
        return base + '?s=' + urllib.parse.quote(salon_name, safe='')
    return base


def body_to_html(body_text: str, salon_name: str = '') -> str:
    """Convert plain-text email body to styled HTML paragraphs."""
    demo_url = build_demo_url(salon_name)

    lines = body_text.strip().split('\n')
    parts = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            parts.append('<tr><td style="height:12px;"></td></tr>')
            continue
        # WHY BUY line → hidden metadata (not shown to recipient)
        if stripped.startswith('WHY BUY:') or stripped.startswith('---'):
            parts.append(f'<!-- {html.escape(stripped)} -->')
            continue
        # Section headers (ALL CAPS lines)
        if stripped.isupper() and len(stripped) > 4:
            parts.append(
                f'<tr><td style="padding:16px 0 4px;">'
                f'<span style="font-family:\'Courier New\',monospace;font-size:11px;'
                f'color:#d4a847;letter-spacing:2px;font-weight:bold;">'
                f'{html.escape(stripped)}</span></td></tr>'
            )
            continue
        # Bullet points (— prefix)
        if stripped.startswith('—') or stripped.startswith('-'):
            parts.append(
                f'<tr><td style="padding:3px 0 3px 16px;">'
                f'<span style="font-family:Arial,sans-serif;font-size:15px;'
                f'color:#ccc;line-height:1.6;">{html.escape(stripped)}</span>'
                f'</td></tr>'
            )
            continue
        # Numbered items
        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1] == '.':
            parts.append(
                f'<tr><td style="padding:8px 0 4px;">'
                f'<span style="font-family:Arial,sans-serif;font-size:15px;'
                f'color:#eee;font-weight:bold;line-height:1.6;">{html.escape(stripped)}</span>'
                f'</td></tr>'
            )
            continue
        # Demo link line
        if 'Demo:' in stripped or 'vermarkter.vercel.app' in stripped:
            parts.append(
                f'<tr><td style="padding:16px 0 8px;text-align:center;">'
                f'<a href="{html.escape(demo_url)}" '
                f'style="display:inline-block;background:#d4a847;color:#000;'
                f'font-family:\'Courier New\',monospace;font-size:13px;font-weight:bold;'
                f'letter-spacing:2px;padding:14px 32px;text-decoration:none;'
                f'border-radius:2px;">→ DEMO ANSEHEN (90 SEK)</a></td></tr>'
            )
            continue
        # Regular paragraph
        parts.append(
            f'<tr><td style="padding:4px 0;">'
            f'<span style="font-family:Arial,sans-serif;font-size:15px;'
            f'color:#ccc;line-height:1.7;">{html.escape(stripped)}</span>'
            f'</td></tr>'
        )
    return '\n'.join(parts)


def build_html_email(lead: dict, letter_key: str) -> tuple[str, str]:
    """
    Returns (subject, html_body).
    letter_key: 'letter_1_digital_mirror' | 'letter_2_future_vision' | 'letter_3_social_proof_scarcity'
    """
    funnel  = lead['email_funnel_json']
    letter  = funnel.get(letter_key) or funnel.get(list(funnel.keys())[0])
    lead_id = lead['id']
    name    = lead.get('name', '')
    addr    = lead.get('addr') or ''

    # Subject — use first subject option
    subjects = letter.get('subject_options') or []
    subject  = subjects[0] if subjects else f'Wichtige Information für {name}'

    # Tracking pixel URL
    pixel_url = f"{TRACK_BASE_URL}?id={lead_id}"

    # Personalized demo URL (shared by hero thumbnail link + demo button in body)
    demo_url = build_demo_url(name)

    # First screen: Street View thumbnail (with Play overlay) or logo fallback
    sv_url = lead.get('street_view_url')
    if sv_url:
        hero_block = build_street_view_block(sv_url, addr, demo_url=demo_url)
    else:
        hero_block = build_logo_fallback_block()

    # Body text → HTML rows (demo button also uses same personalized URL)
    body_text = letter.get('body', '')
    body_rows = body_to_html(body_text, salon_name=name)

    html_body = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(subject)}</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;">
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:#0a0a0a;min-height:100vh;">
  <tr>
    <td align="center" style="padding:20px 10px 40px;">

      <!-- Email container -->
      <table width="600" cellpadding="0" cellspacing="0" border="0"
             style="max-width:600px;width:100%;">

        <!-- HERO: Street View or Logo -->
        <tr><td>{hero_block}</td></tr>

        <!-- Spacer -->
        <tr><td style="height:24px;"></td></tr>

        <!-- BODY -->
        <tr>
          <td style="background:#111;border:1px solid #1e1e1e;
                     border-radius:4px;padding:32px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              {body_rows}
            </table>
          </td>
        </tr>

        <!-- FOOTER -->
        <tr>
          <td style="padding:24px 0 8px;text-align:center;">
            <span style="font-family:'Courier New',monospace;font-size:10px;
                         color:#444;letter-spacing:1px;">
              Vermarkter — vermarkter.vercel.app<br>
              Sie erhalten diese E-Mail, weil wir eine geschäftliche Relevanz für Ihr Unternehmen sehen.<br>
              <a href="mailto:hello@vermarkter.eu?subject=Abmeldung"
                 style="color:#555;text-decoration:underline;">Abmelden</a>
            </span>
          </td>
        </tr>

      </table>

      <!-- TRACKING PIXEL (1x1, invisible) -->
      <img src="{pixel_url}" width="1" height="1"
           alt="" style="display:block;width:1px;height:1px;border:0;"
           loading="lazy" />

    </td>
  </tr>
</table>
</body>
</html>"""

    return subject, html_body


# ── Brevo sender ──────────────────────────────────────────────────────────────

BREVO_SEND_URL = 'https://api.brevo.com/v3/smtp/email'
BREVO_HEADERS  = {
    'api-key':      BREVO_KEY,
    'Content-Type': 'application/json; charset=utf-8',
    'Accept':       'application/json',
}


def send_via_brevo(to_email: str, to_name: str, subject: str, html_body: str, dry: bool) -> str:
    payload = {
        'sender':   {'name': FROM_NAME, 'email': FROM_EMAIL},
        'to':       [{'email': to_email, 'name': to_name}],
        'subject':  subject,
        'htmlContent': html_body,
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')

    if dry:
        preview = html_body[:200].replace('\n', ' ')
        print(f"         [DRY] To: {to_email} | Subject: {subject[:60]}")
        return 'DRY'

    req = urllib.request.Request(BREVO_SEND_URL, data=data, headers=BREVO_HEADERS, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode('utf-8'))
            msg_id = resp.get('messageId', '?')
            return f'OK:{msg_id}'
    except urllib.request.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')[:300]
        return f'ERR {e.code}: {body}'


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Send personalized emails via Brevo')
    p.add_argument('--ids',     default='',   help='Comma-separated lead IDs')
    p.add_argument('--city',    default='',   help='Filter by city')
    p.add_argument('--limit',   type=int, default=DAILY_LIMIT,
                   help=f'Max emails to send (default: {DAILY_LIMIT})')
    p.add_argument('--letter',  default='letter_1_digital_mirror',
                   choices=['letter_1_digital_mirror',
                            'letter_2_future_vision',
                            'letter_3_social_proof_scarcity'],
                   help='Which funnel letter to send (default: letter_1)')
    p.add_argument('--delay',   type=float, default=1.0,
                   help='Seconds between sends (default: 1.0)')
    p.add_argument('--dry-run', action='store_true',
                   help='Build emails and print, no actual sending')
    p.add_argument('--save-html', action='store_true',
                   help='Save rendered HTML to data/email_preview_{id}.html for review')
    return p.parse_args()


def main():
    args   = parse_args()
    dry    = args.dry_run
    ids    = {int(x.strip()) for x in args.ids.split(',') if x.strip()} if args.ids else set()

    print(f'\n{"="*64}')
    print(f'  Brevo Email Sender  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  Letter: {args.letter}')
    print(f'  Limit: {args.limit}  |  Delay: {args.delay}s')
    if ids:
        print(f'  ID filter: {sorted(ids)}')
    print(f'{"="*64}\n')

    leads = fetch_leads(ids, args.limit, args.city)
    print(f'  Leads with email + funnel: {len(leads)}\n')

    if not leads:
        print('  No leads found — check status=email_ready and email_funnel_json is set.')
        return

    ok = fail = skipped = 0

    for lead in leads:
        lead_id = lead['id']
        email   = lead.get('email', '').strip()
        name    = lead.get('name', f'id={lead_id}')

        if not email:
            print(f'  [SKIP] id={lead_id} — no email address')
            skipped += 1
            continue

        print(f'  [SEND] id={lead_id} «{name}» → {email}')
        print(f'         sv_url: {"YES" if lead.get("street_view_url") else "no (logo fallback)"}')

        try:
            subject, html_body = build_html_email(lead, args.letter)
        except Exception as e:
            print(f'         → [ERR] build failed: {e}')
            fail += 1
            continue

        if args.save_html:
            preview_path = os.path.join(_ROOT, 'data', f'email_preview_{lead_id}.html')
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            with open(preview_path, 'w', encoding='utf-8') as f:
                f.write(html_body)
            print(f'         → HTML saved: {preview_path}')

        result = send_via_brevo(email, name, subject, html_body, dry)
        print(f'         → [{result}]')

        if result.startswith('OK') or result == 'DRY':
            ok += 1
            if not dry:
                sb_patch(lead_id, {'status': 'email_sent'})
        else:
            fail += 1

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — total={ok+fail+skipped} | sent={ok} | skipped={skipped} | fail={fail}')
    if dry:
        print('  DRY-RUN: nothing sent.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
