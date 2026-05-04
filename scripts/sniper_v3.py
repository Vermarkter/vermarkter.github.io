#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_v3.py — GPT-4o outreach engine with WA/Email channel split.

Splits leads into two channels:
  WhatsApp — mobile phone detected  → short message ≤500 chars
  Email     — email present, no mobile → detailed professional email

CTO prompt: dangerous-site flag + competitor context included.

Usage:
  python scripts/sniper_v3.py                        # 20 leads, München, live
  python scripts/sniper_v3.py --limit 40 --dry-run   # test without DB write
  python scripts/sniper_v3.py --city Berlin --limit 30
  python scripts/sniper_v3.py --ids 2222,2223,2224   # target specific IDs
  python scripts/sniper_v3.py --channel wa            # WhatsApp only
  python scripts/sniper_v3.py --channel email         # Email only

Requires:
  .env  →  OPENAI_API_KEY=sk-proj-...
  pip install openai
"""

import sys, io, os, json, time, argparse, re, configparser, urllib.request, urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from openai import OpenAI
except ImportError:
    print('[ERROR] openai not installed. Run:  pip install openai', file=sys.stderr)
    sys.exit(1)

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

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

OPENAI_KEY = (
    _env.get('OPENAI_API_KEY')
    or os.environ.get('OPENAI_API_KEY', '')
    or _cfg.get('OPENAI', 'api_key', fallback='')
).strip()
OPENAI_MODEL = 'gpt-4o'  # hardcoded — never downgrade to mini or 3.5

if not OPENAI_KEY or not OPENAI_KEY.startswith('sk-') or 'PASTE' in OPENAI_KEY:
    print('[ERROR] OPENAI_API_KEY missing or invalid.\n'
          '  Set in .env:  OPENAI_API_KEY=sk-proj-...', file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=OPENAI_KEY)

# ---------------------------------------------------------------------------
# Supabase headers
# ---------------------------------------------------------------------------
HDRS_GET = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}
HDRS_PATCH = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

FIELDS = 'id,name,city,district,phone,email,website,notes,custom_message'

# ---------------------------------------------------------------------------
# Channel detection
# ---------------------------------------------------------------------------
# Mobile prefixes in DE: 015x, 016x, 017x
_MOBILE_RE = re.compile(r'\+49\s*1[567]|\b01[567]')

def detect_channel(lead: dict) -> str:
    """Returns 'wa', 'email', or 'skip' (no contact info)."""
    phone = (lead.get('phone') or '').strip()
    email = (lead.get('email') or '').strip()
    if phone and _MOBILE_RE.search(phone):
        return 'wa'
    if email:
        return 'email'
    if phone:
        # Landline only — still prefer WA attempt if phone exists
        return 'wa'
    return 'skip'

# ---------------------------------------------------------------------------
# Audit note parser
# ---------------------------------------------------------------------------
def parse_notes(notes: str) -> dict:
    """Extract structured flags from audit: score=N | booking=y | mobile=y ..."""
    n = (notes or '').lower()
    return {
        'score':        _re_val(r'score=(\d+)', n),
        'has_booking':  'booking=y' in n,
        'mobile_ok':    'mobile=y' in n,
        'ssl_ok':       'ssl=y' in n,
        'dangerous':    'err=' in n or 'небезпечний' in n or 'deceptive' in n or 'phishing' in n,
        'no_website':   not (notes or '').strip() or 'personalized' in n,
        'priority':     'priority' in n,
    }

def _re_val(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else None

# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# CTO Ultimate system prompts v5
# ---------------------------------------------------------------------------
_CORE = """Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.
Anrede AUSSCHLIESSLICH „Sie". Niemals „Hey" oder „Hi".

GRAMMATIK-PFLICHT (Separable Verbs):
- RICHTIG: „Das schreckt ca. 70 % Ihrer potenziellen Kunden ab"
- FALSCH:  „Das abschreckt" — NIEMALS so schreiben

FEW-SHOT BEISPIELE (exakt so aufbauen):

Beispiel SSL:
„Guten Tag, Ihr Webauftritt wird aktuell von Google als „unsicher" eingestuft. Das schreckt ca. 70 % Ihrer potenziellen Kunden ab, noch bevor sie Ihre Arbeit sehen. Wir bieten Ihnen Website, App und WhatsApp-Assistent für einmalig 1.000 €. Hier ist die Demo: https://vermarkter.vercel.app/services/beauty-industry/de/ Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"

Beispiel Konkurrent:
„Sehr geehrtes Team, Kunden in Ihrem Viertel buchen aktuell eher bei [Konkurrent], da dort eine direkte Online-Buchung möglich ist. Wir machen Sie digital unabhängig für einmalig 1.000 €. Demo: https://vermarkter.vercel.app/services/beauty-industry/de/ Soll ich Ihnen ein Video-Demo schicken?"

REGELN (ALLE PFLICHT):
- SSL-Treffer NUR wenn ssl=n — exakt wie Beispiel SSL oben
- Konkurrent NUR wenn explizit in Notizen genannt — dann namentlich
- Kein Konkurrent → allgemeiner Kundenverlust außerhalb der Öffnungszeiten
- Angebot: Website + App + WhatsApp-Assistent — einmalig 1.000 €
- CTA (PFLICHT): „Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"
- Link: https://vermarkter.vercel.app/services/beauty-industry/de/
- Unterschrift: www.my-salon.eu (KEIN Name, nur Domain)"""

SYSTEM_WA = (
    _CORE + "\n\n"
    "KANAL: WhatsApp\n"
    "- MAXIMAL 480 Zeichen — zähle exakt, kürze gnadenlos\n"
    "- Format: 3–4 knappe Sätze, kein Fließtext-Block\n"
    "- Keine Emojis\n"
    "- Output: NUR den fertigen WhatsApp-Text, keine Erklärungen"
)

SYSTEM_EMAIL = (
    _CORE + "\n\n"
    "KANAL: E-Mail\n"
    "- Erste Zeile: 'Betreff: ...' (präzise, kein Clickbait)\n"
    "- Länge: 120–180 Wörter — strukturiert, kein Fließtext-Wust\n"
    "- Aufbau: Problem → Angebot → CTA (60-Sekunden-Video-Demo)\n"
    "- Klingt personalisiert, kein Massenmail-Ton\n"
    "- Output: NUR Betreff + E-Mail-Text, keine Erklärungen"
)

def _weaknesses(flags: dict, website: str) -> str:
    issues = []
    if flags['dangerous']:
        issues.append('⚠️ Ihre Website wird von Google als GEFÄHRLICH / BETRÜGERISCH markiert — '
                      'Besucher sehen eine Sicherheitswarnung und verlassen die Seite sofort')
    if not flags['has_booking']:
        issues.append('kein Online-Booking → Neukunden wählen Konkurrenten mit direkter Buchung')
    if not flags['mobile_ok']:
        issues.append('mobile Darstellung nicht optimiert → 70 % der Suchenden kommen per Smartphone')
    if not flags['ssl_ok'] and not flags['dangerous']:
        issues.append('SSL-Zertifikat fehlt oder abgelaufen → Google wertet die Seite ab')
    if not website or website in ('None', ''):
        issues.append('keine Website gefunden → unsichtbar für Neukunden bei Google')
    return '; '.join(issues) if issues else 'Potenzial bei digitaler Sichtbarkeit und Neukunden-Gewinnung'

def build_prompt(lead: dict, channel: str) -> str:
    flags    = parse_notes(lead.get('notes') or '')
    website  = lead.get('website') or ''
    city     = lead.get('city') or lead.get('district') or 'Deutschland'
    phone    = lead.get('phone') or ''
    email    = lead.get('email') or ''
    problems = _weaknesses(flags, website)

    competitor_note = ''
    if flags['priority']:
        competitor_note = ('Hinweis: dieser Salon hat keine eigene Website. '
                           'Konkurrenten in der Nähe sind besser aufgestellt. '
                           'Betone den Wettbewerbsnachteil konkret.')

    wa_instruction  = 'Schreib eine WhatsApp-Nachricht (MAX 500 Zeichen!).' if channel == 'wa' \
                      else 'Schreib eine professionelle Kalt-E-Mail (mit Betreff-Zeile).'

    return (
        f"Salon: {lead['name']}\n"
        f"Stadt: {city}\n"
        f"Website: {website or 'keine'}\n"
        f"Telefon: {phone or '—'}\n"
        f"E-Mail: {email or '—'}\n"
        f"Gefundene Probleme: {problems}\n"
        f"{competitor_note}\n\n"
        f"{wa_instruction}"
    )

# ---------------------------------------------------------------------------
# GPT-4o call
# ---------------------------------------------------------------------------
def generate(lead: dict, channel: str) -> str:
    system = SYSTEM_WA if channel == 'wa' else SYSTEM_EMAIL
    max_tok = 200 if channel == 'wa' else 500

    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=max_tok,
        temperature=0.75,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': build_prompt(lead, channel)},
        ]
    )
    msg = resp.choices[0].message.content.strip()

    # Hard enforce WA length
    if channel == 'wa' and len(msg) > 500:
        msg = msg[:497] + '...'

    return msg

# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------
def fetch_leads(city='München', limit=20, offset=0, ids=None):
    if ids:
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&id=in.({','.join(str(i) for i in ids)})"
               f"&status=eq.new&order=id.asc")
    else:
        city_enc = urllib.parse.quote(city, safe='')
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&city=eq.{city_enc}"
               f"&status=eq.new&order=id.asc"
               f"&limit={limit}&offset={offset}")
    req = urllib.request.Request(url, headers=HDRS_GET)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def patch_lead(lead_id: int, message: str, channel: str) -> int:
    payload = json.dumps({
        'custom_message': message,
        'status': 'READY TO SEND',
        'channel': channel,          # wa | email — store for dispatcher
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}",
        data=payload, headers=HDRS_PATCH, method='PATCH'
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='Sniper v3 — GPT-4o WA/Email split engine')
    p.add_argument('--city',    default='München')
    p.add_argument('--limit',   type=int, default=20)
    p.add_argument('--offset',  type=int, default=0)
    p.add_argument('--ids',     default='', help='Comma-separated IDs')
    p.add_argument('--channel', choices=['wa', 'email', 'both'], default='both')
    p.add_argument('--dry-run', action='store_true', help='No DB writes')
    p.add_argument('--delay',   type=float, default=1.5, help='Seconds between API calls')
    return p.parse_args()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    args = parse_args()
    dry  = args.dry_run
    ids  = [int(x.strip()) for x in args.ids.split(',') if x.strip()] if args.ids else None

    print(f'\n{"="*66}')
    print(f'  Sniper v3  |  model={OPENAI_MODEL}  |  channel={args.channel}  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  City: {args.city}  |  limit={args.limit}  |  offset={args.offset}')
    if ids: print(f'  IDs override: {ids}')
    print(f'{"="*66}\n')

    leads = fetch_leads(city=args.city, limit=args.limit, offset=args.offset, ids=ids)
    if not leads:
        print('No leads found.')
        return

    counts = {'wa': 0, 'email': 0, 'skip': 0, 'already': 0, 'fail': 0}

    for lead in leads:
        lid  = lead['id']
        name = lead['name']

        if lead.get('custom_message'):
            print(f'  [SKIP already] id={lid} «{name}»')
            counts['already'] += 1
            continue

        ch = detect_channel(lead)

        if args.channel != 'both' and ch != args.channel:
            print(f'  [SKIP channel={ch}] id={lid} «{name}»')
            continue

        if ch == 'skip':
            print(f'  [NO CONTACT]   id={lid} «{name}» — no phone or email')
            counts['skip'] += 1
            continue

        tag = 'WA  ' if ch == 'wa' else 'EMAIL'
        try:
            msg = generate(lead, ch)
            preview = msg.replace('\n', ' ')[:90]
            print(f'  [{tag}] id={lid} «{name}»  ({len(msg)} chars)')
            print(f'         {preview}...')

            if not dry:
                code = patch_lead(lid, msg, ch)
                ok = code in (200, 204)
                print(f'         → DB: {"OK" if ok else f"ERR {code}"}')
                if ok: counts[ch] += 1
                else:  counts['fail'] += 1
            else:
                print(f'         → DB: [DRY-RUN]')
                counts[ch] += 1

        except Exception as e:
            print(f'  [ERR] id={lid} «{name}»: {e}', file=sys.stderr)
            counts['fail'] += 1

        time.sleep(args.delay)

    total = counts['wa'] + counts['email']
    print(f'\n{"="*66}')
    print(f'  DONE — WA: {counts["wa"]} | Email: {counts["email"]} | '
          f'Skip: {counts["skip"]} | Already: {counts["already"]} | Fail: {counts["fail"]}')
    if dry:
        print('  DRY-RUN: nothing written.')
    print(f'{"="*66}')


if __name__ == '__main__':
    main()
