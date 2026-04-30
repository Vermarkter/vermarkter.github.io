#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_engine.py — Automated GPT-4o outreach generator for beauty leads.

Fetches status='new' leads from Supabase, generates personalized German
WhatsApp/email messages via OpenAI GPT-4o, writes result back to CRM.

Usage:
  python scripts/sniper_engine.py              # 20 leads, dry-run off
  python scripts/sniper_engine.py --limit 40   # custom batch size
  python scripts/sniper_engine.py --dry-run    # generate only, no DB write
  python scripts/sniper_engine.py --city Berlin --limit 30
  python scripts/sniper_engine.py --ids 111,112,115   # specific IDs only

Config required in .env (project root):
  OPENAI_API_KEY=sk-...

Optional in config.ini:
  [OPENAI]
  model = gpt-4o
"""

import sys, io, json, time, argparse, os, urllib.request, urllib.parse, configparser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from holiday_guard import guard_dispatch

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_env(path):
    """Minimal .env loader — no external deps required."""
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

# OpenAI key: .env takes priority, fallback → config.ini [OPENAI] api_key
OPENAI_KEY = (
    _env.get('OPENAI_API_KEY')
    or os.environ.get('OPENAI_API_KEY', '')
    or _cfg.get('OPENAI', 'api_key', fallback='')
).strip()
OPENAI_MODEL = 'gpt-4o'  # hardcoded — never downgrade to mini or 3.5

if not OPENAI_KEY or 'PASTE' in OPENAI_KEY or not OPENAI_KEY.startswith('sk-'):
    print('[ERROR] OPENAI_API_KEY not set.\n'
          '  Add to .env in project root:\n'
          '  OPENAI_API_KEY=sk-proj-...', file=sys.stderr)
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
HDRS_OAI = {
    'Authorization': 'Bearer ' + OPENAI_KEY,
    'Content-Type': 'application/json',
}

# ---------------------------------------------------------------------------
# System prompt — CTO Ultimate v5
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.
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
- MAXIMAL 480 Zeichen — zähle exakt, kürze gnadenlos
- SSL-Treffer NUR wenn ssl=n in den Notizen — exakt wie Beispiel SSL oben
- Konkurrent NUR wenn explizit in den Notizen genannt — dann namentlich erwähnen
- Kein Konkurrent in Notizen → schreib über allgemeinen Kundenverlust außerhalb der Öffnungszeiten
- Angebot: Website + App + WhatsApp-Assistent — einmalig 1.000 €
- CTA (PFLICHT): „Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"
- Link: https://vermarkter.vercel.app/services/beauty-industry/de/
- Unterschrift: www.my-salon.eu (KEIN Name, nur die Domain)

Output: NUR den fertigen Nachrichtentext — keine Erklärungen, keine Kommentare."""

# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------
FIELDS = 'id,name,city,district,phone,email,website,notes,custom_message'

def fetch_leads(city='München', limit=20, offset=0, ids=None):
    if ids:
        id_list = ','.join(str(i) for i in ids)
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&id=in.({id_list})"
               f"&status=eq.new"
               f"&order=id.asc")
    else:
        city_enc = urllib.parse.quote(city, safe='')
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&city=eq.{city_enc}"
               f"&status=eq.new"
               f"&order=id.asc"
               f"&limit={limit}"
               f"&offset={offset}")
    req = urllib.request.Request(url, headers=HDRS_SB_GET)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))


def patch_lead(lead_id, message):
    payload = json.dumps({'custom_message': message, 'status': 'READY TO SEND'}).encode('utf-8')
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=payload, headers=HDRS_SB_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code

# ---------------------------------------------------------------------------
# OpenAI helper
# ---------------------------------------------------------------------------
def build_user_prompt(lead):
    website  = lead.get('website') or 'keine Website bekannt'
    phone    = lead.get('phone')   or 'unbekannt'
    notes    = lead.get('notes')   or ''
    city     = lead.get('city')    or lead.get('district') or 'München'
    contact  = 'WhatsApp' if phone and phone != 'unbekannt' else 'E-Mail'

    # parse audit notes for context
    has_booking = 'booking=y' in notes.lower()
    mobile_ok   = 'mobile=y' in notes.lower()
    ssl_ok      = 'ssl=y' in notes.lower()

    weaknesses = []
    if not has_booking: weaknesses.append('kein Online-Booking')
    if not mobile_ok:   weaknesses.append('mobile Optimierung fehlt')
    if not ssl_ok:      weaknesses.append('SSL-Problem')

    weakness_text = (', '.join(weaknesses) + ' — das kostet Neukunden.')  if weaknesses \
                    else 'Potenzial bei Neukunden-Gewinnung über Google und Meta.'

    return (f"Salon: {lead['name']}\n"
            f"Stadt: {city}\n"
            f"Website: {website}\n"
            f"Kontakt via: {contact}\n"
            f"Audit-Befund: {weakness_text}\n\n"
            f"Schreib eine WhatsApp-Erstkontakt-Nachricht laut System-Anweisungen.")


def generate_message(lead):
    body = json.dumps({
        'model': OPENAI_MODEL,
        'max_tokens': 300,
        'temperature': 0.75,
        'messages': [
            {'role': 'system',  'content': SYSTEM_PROMPT},
            {'role': 'user',    'content': build_user_prompt(lead)},
        ]
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=body, headers=HDRS_OAI, method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8'))

    return data['choices'][0]['message']['content'].strip()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Engine — GPT-4o outreach generator')
    p.add_argument('--city',    default='München', help='City filter (default: München)')
    p.add_argument('--limit',   type=int, default=20, help='Max leads per run (default: 20)')
    p.add_argument('--offset',  type=int, default=0,  help='Supabase offset (default: 0)')
    p.add_argument('--ids',     default='',  help='Comma-separated IDs to target (overrides city/limit)')
    p.add_argument('--dry-run', action='store_true', help='Generate messages but do NOT write to DB')
    p.add_argument('--force',   action='store_true', help='Overwrite existing custom_message if status=new')
    p.add_argument('--delay',   type=float, default=1.2, help='Seconds between API calls (default: 1.2)')
    return p.parse_args()


def main():
    args = parse_args()
    if not args.dry_run:
        guard_dispatch('sniper_engine')
    dry  = args.dry_run
    ids  = [int(x.strip()) for x in args.ids.split(',') if x.strip()] if args.ids else None

    print(f'\n{"="*64}')
    print(f'  Sniper Engine  |  model={OPENAI_MODEL}  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  City: {args.city}  |  limit={args.limit}  |  offset={args.offset}')
    if ids:        print(f'  IDs override: {ids}')
    if args.force: print(f'  --force: overwriting existing messages for status=new leads')
    print(f'{"="*64}\n')

    leads = fetch_leads(city=args.city, limit=args.limit, offset=args.offset, ids=ids)
    if not leads:
        print('No leads found matching criteria.')
        return

    print(f'Fetched {len(leads)} leads. Generating messages...\n')

    ok = fail = skipped = 0
    for lead in leads:
        lid  = lead['id']
        name = lead['name']

        if lead.get('custom_message') and not args.force:
            print(f'  [SKIP] id={lid} «{name}» — already has message')
            skipped += 1
            continue

        try:
            msg = generate_message(lead)
            preview = msg[:80].replace('\n', ' ')
            print(f'  [GEN]  id={lid} «{name}»')
            print(f'         → {preview}...')

            if not dry:
                code = patch_lead(lid, msg)
                sym  = 'OK' if code in (200, 204) else f'ERR {code}'
                print(f'         → DB: [{sym}]')
                if code in (200, 204): ok += 1
                else:                  fail += 1
            else:
                print(f'         → DB: [DRY-RUN, not written]')
                ok += 1

        except Exception as e:
            print(f'  [ERR]  id={lid} «{name}»: {e}', file=sys.stderr)
            fail += 1

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — generated={ok+skipped+fail} | '
          f'uploaded={ok} | skipped={skipped} | fail={fail}')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
