#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_engine.py — Automated GPT-4o outreach generator for beauty leads.

Fetches status='new' leads from Supabase, generates personalized German
WhatsApp/email messages via OpenAI GPT-4o, writes result back to CRM.

A/B structures (--ab flag):
  problem  — Pain-first: lead with a concrete problem, then offer
  story    — Story-first: mini narrative of another salon, then offer
  empathy  — Empathy-first: acknowledge their hard work, then offer (default)

Usage:
  python scripts/sniper_engine.py                        # 20 leads, empathy structure
  python scripts/sniper_engine.py --ab problem           # Pain-first structure
  python scripts/sniper_engine.py --ab story             # Story-first structure
  python scripts/sniper_engine.py --limit 40             # custom batch size
  python scripts/sniper_engine.py --dry-run              # generate only, no DB write
  python scripts/sniper_engine.py --city Berlin --limit 30
  python scripts/sniper_engine.py --ids 111,112,115      # specific IDs only
  python scripts/sniper_engine.py --ab all               # generate all 3 variants per lead

Config required in .env (project root):
  OPENAI_API_KEY=sk-...

Optional in config.ini:
  [OPENAI]
  model = gpt-4o
"""

import sys, io, json, time, argparse, os, urllib.request, urllib.parse, configparser, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from holiday_guard import guard_dispatch
try:
    from sniper_lang_detect import detect as _lang_detect, build_ua_bilingual_message
except ImportError:
    _lang_detect = lambda name: None
    build_ua_bilingual_message = None

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

OPENAI_KEY = (
    _env.get('OPENAI_API_KEY')
    or os.environ.get('OPENAI_API_KEY', '')
    or _cfg.get('OPENAI', 'api_key', fallback='')
).strip()
OPENAI_MODEL = 'gpt-4o'

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
# Style Guide (applied to every generated message)
# ---------------------------------------------------------------------------
STYLE_GUIDE = """
STYLE GUIDE — PFLICHT für jeden Text:

1. Leerzeichen vor € — IMMER: „1 000 €" (nicht „1000€" oder „1.000€")
   Korrekt: „für einmalig 1 000 €"

2. Deutsche Anführungszeichen — IMMER „..." (nicht "..." oder '...')
   Korrekt: Ihre Website wird als „unsicher" eingestuft.

3. Grammatik (Trennbare Verben) — KEIN Zusammenziehen:
   RICHTIG: „Das schreckt Kunden ab"
   FALSCH:  „Das abschreckt Kunden"

4. Anrede: ausschließlich „Sie" — kein Du, kein Hey, kein Hi

5. Keine Emojis außer am Anfang des Satzes wenn es die Struktur vorgibt
"""

# ---------------------------------------------------------------------------
# A/B System Prompts
# ---------------------------------------------------------------------------

_BASE_RULES = f"""
{STYLE_GUIDE}

AUSGABE-REGELN (ALLE PFLICHT):
- MAXIMAL 480 Zeichen — zähle exakt, kürze gnadenlos
- Angebot: Website + App + WhatsApp-Assistent — einmalig 1 000 €
- CTA (PFLICHT): „Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"
- Link: https://vermarkter.vercel.app/services/beauty-industry/de/
- Unterschrift: www.my-salon.eu (KEIN Name, nur die Domain)
- SSL-Treffer NUR wenn ssl=n in den Notizen
- Konkurrent NUR wenn explizit in den Notizen — dann namentlich nennen

Output: NUR den fertigen Nachrichtentext — keine Erklärungen, keine Kommentare.
"""

SYSTEM_PROMPTS = {

    'problem': f"""Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.

STRUKTUR — „Proблема-zuerst":
1. Benenne SOFORT das konkrete Problem des Salons (z. B. SSL, fehlendes Booking, schlechte Mobile-Darstellung)
2. Quantifiziere den Schaden kurz (% Kundenverlust, verpasste Buchungen)
3. Biete die Lösung an
4. CTA

Beispiel:
„Guten Tag, Ihre Website wird aktuell von Google als „unsicher" eingestuft. Das schreckt ca. 70 % der Besucher ab, noch bevor sie Ihre Arbeit sehen. Wir bieten Website + App + WhatsApp-Assistent für einmalig 1 000 €. Demo: https://vermarkter.vercel.app/services/beauty-industry/de/ Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"
{_BASE_RULES}""",

    'story': f"""Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.

STRUKTUR — „Geschichte-zuerst":
1. Beginne mit einer 1-Satz-Mini-Geschichte eines ähnlichen Salons in der gleichen Stadt
   (anonymisiert: „Ein Barbershop in Schwabing", „Ein Nagelstudio in Mitte")
2. Zeige das Ergebnis nach Einführung unserer App (konkrete Zahl: +30 % Buchungen, -5 verpasste Anrufe/Woche)
3. Überleite: „Das können wir auch für Sie umsetzen."
4. Angebot + CTA

Beispiel:
„Guten Tag, ein Barbershop in Schwabing hat nach Einführung unserer App ca. 30 % mehr Buchungen pro Woche verzeichnet — ohne zusätzliche Werbung. Das können wir auch für Sie umsetzen: Website + App + WhatsApp-Assistent, einmalig 1 000 €. Demo: https://vermarkter.vercel.app/services/beauty-industry/de/ Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"
{_BASE_RULES}""",

    'empathy': f"""Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.

STRUKTUR — „Empathie-zuerst":
1. Erkenne an, wie viel Arbeit hinter einem gut geführten Salon steckt (1 Satz, kein Schmeicheln)
2. Benenne das eine Problem, das trotz harter Arbeit Kunden kostet (Buchungen, Erreichbarkeit, SSL)
3. Biete eine einfache Lösung an
4. CTA

Beispiel:
„Guten Tag, ein gut geführter Salon verdient Kunden, die ihn auch online finden und buchen können. Aktuell erschwert Ihre fehlende Online-Buchung genau das — Kunden, die nach 18 Uhr suchen, gehen zum Nächsten. Wir lösen das: Website + App + WhatsApp-Assistent, einmalig 1 000 €. Demo: https://vermarkter.vercel.app/services/beauty-industry/de/ Soll ich Ihnen ein 60-Sekunden-Video-Demo dazu schicken?"
{_BASE_RULES}""",
}

AB_VARIANTS = ['problem', 'story', 'empathy']

# ---------------------------------------------------------------------------
# Style Guide validator
# ---------------------------------------------------------------------------
def validate_style(text):
    """Returns list of violations found in generated text."""
    issues = []

    # Rule 1: space before € (allow   €, non-breaking space, or thin space)
    # Flag: digit(s) directly adjacent to € with no space at all
    if re.search(r'\d€', text):
        issues.append('Kein Leerzeichen vor € (z.B. „1000€" → „1 000 €")')

    # Rule 2: straight quotes instead of German typographic quotes
    if re.search(r'"[^"]*"', text):
        issues.append('Falsche Anführungszeichen — bitte „..." statt "..." verwenden')

    # Rule 3: trennbare Verben — common patterns
    separable = ['abschreckt', 'aufzeigt', 'einbringt', 'einloggt', 'abläuft', 'ausschaut']
    for v in separable:
        if v in text.lower():
            issues.append(f'Trennbares Verb zusammengezogen: „{v}"')

    # Rule 4: informal address
    if re.search(r'\b(hey|hi|du |dein|deine)\b', text.lower()):
        issues.append('Informelle Anrede gefunden (Du/Hey/Hi) — nur „Sie" erlaubt')

    return issues


def fix_style(text):
    """Auto-fix the easy violations (€ spacing, straight quotes → DE quotes)."""
    # Fix: digit immediately before € → add non-breaking space (U+00A0)
    text = re.sub(r'(\d)(€)', r'\1 \2', text)

    # Fix: "text" → „text" (simple heuristic — works for most cases)
    # Only replace pairs of straight quotes that are clearly wrapping a word/phrase
    text = re.sub(r'"([^"]{1,60})"', r'„\1"', text)

    return text


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------
FIELDS = 'id,name,city,district,phone,email,website,notes,custom_message,compliment_detail'

def fetch_leads(city='München', limit=20, offset=0, ids=None, force=False):
    if ids:
        id_list = ','.join(str(i) for i in ids)
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&id=in.({id_list})"
               f"&order=id.asc")
        # When --force is set, skip status filter so we can overwrite READY TO SEND leads
        if not force:
            url += '&status=eq.new'
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


def patch_lead(lead_id, message, ab_variant=None):
    payload = {'custom_message': message, 'status': 'READY TO SEND'}
    if ab_variant:
        payload['notes_ab'] = ab_variant  # store which variant won (if column exists)
    data = json.dumps(payload).encode('utf-8')
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=data, headers=HDRS_SB_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code

# ---------------------------------------------------------------------------
# OpenAI helper
# ---------------------------------------------------------------------------
def build_user_prompt(lead):
    website    = lead.get('website')           or 'keine Website bekannt'
    phone      = lead.get('phone')             or 'unbekannt'
    notes      = lead.get('notes')             or ''
    city       = lead.get('city') or lead.get('district') or 'München'
    contact    = 'WhatsApp' if phone and phone != 'unbekannt' else 'E-Mail'
    compliment = lead.get('compliment_detail') or ''

    has_booking = 'booking=y' in notes.lower()
    mobile_ok   = 'mobile=y'  in notes.lower()
    ssl_ok      = 'ssl=y'     in notes.lower()

    weaknesses = []
    if not has_booking: weaknesses.append('kein Online-Booking')
    if not mobile_ok:   weaknesses.append('mobile Optimierung fehlt')
    if not ssl_ok:      weaknesses.append('SSL-Problem')

    weakness_text = (', '.join(weaknesses) + ' — das kostet Neukunden.') if weaknesses \
                    else 'Potenzial bei Neukunden-Gewinnung über Google und Meta.'

    prompt = (f"Salon: {lead['name']}\n"
              f"Stadt: {city}\n"
              f"Website: {website}\n"
              f"Kontakt via: {contact}\n"
              f"Audit-Befund: {weakness_text}\n")

    if compliment:
        prompt += f"Besonderes Kompliment (aus Instagram): {compliment}\n"
        prompt += "(Optional: baue das Kompliment natürlich in die Eröffnung ein, max 1 Satz)\n"

    prompt += "\nSchreib eine WhatsApp-Erstkontakt-Nachricht laut System-Anweisungen."
    return prompt


def generate_message(lead, ab_variant='empathy'):
    # UA detection: bilingual message bypasses GPT entirely
    lang = _lang_detect(lead.get('name', ''))
    if lang == 'UA' and build_ua_bilingual_message:
        return build_ua_bilingual_message(lead)

    system = SYSTEM_PROMPTS[ab_variant]
    body = json.dumps({
        'model': OPENAI_MODEL,
        'max_tokens': 300,
        'temperature': 0.75,
        'messages': [
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': build_user_prompt(lead)},
        ]
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=body, headers=HDRS_OAI, method='POST'
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode('utf-8'))

    raw = data['choices'][0]['message']['content'].strip()
    return fix_style(raw)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Engine — GPT-4o outreach generator')
    p.add_argument('--city',    default='München', help='City filter (default: München)')
    p.add_argument('--limit',   type=int, default=20, help='Max leads per run (default: 20)')
    p.add_argument('--offset',  type=int, default=0,  help='Supabase offset (default: 0)')
    p.add_argument('--ids',     default='', help='Comma-separated IDs to target (overrides city/limit)')
    p.add_argument('--dry-run', action='store_true', help='Generate messages but do NOT write to DB')
    p.add_argument('--force',   action='store_true', help='Overwrite existing custom_message if status=new')
    p.add_argument('--delay',   type=float, default=1.2, help='Seconds between API calls (default: 1.2)')
    p.add_argument('--ab',      default='empathy',
                   choices=['problem', 'story', 'empathy', 'all'],
                   help='A/B structure: problem | story | empathy | all (default: empathy)')
    return p.parse_args()


def main():
    args = parse_args()
    if not args.dry_run:
        guard_dispatch('sniper_engine')
    dry  = args.dry_run
    ids  = [int(x.strip()) for x in args.ids.split(',') if x.strip()] if args.ids else None
    ab   = args.ab

    variants_to_run = AB_VARIANTS if ab == 'all' else [ab]

    print(f'\n{"="*64}')
    print(f'  Sniper Engine  |  model={OPENAI_MODEL}  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  City: {args.city}  |  limit={args.limit}  |  offset={args.offset}')
    print(f'  A/B structure: {ab}')
    if ids:        print(f'  IDs override: {ids}')
    if args.force: print(f'  --force: overwriting existing messages for status=new leads')
    print(f'{"="*64}\n')

    leads = fetch_leads(city=args.city, limit=args.limit, offset=args.offset, ids=ids, force=args.force)
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

        lang_tag = _lang_detect(name)
        for variant in variants_to_run:
            try:
                msg = generate_message(lead, ab_variant=variant)
                preview = msg[:80].replace('\n', ' ')

                # Style validation (skip for bilingual UA messages — different format)
                if lang_tag == 'UA':
                    issue_tag = '  ✓ UA-BILINGUAL'
                else:
                    issues = validate_style(msg)
                    issue_tag = f'  ⚠ {"; ".join(issues)}' if issues else '  ✓ Style OK'

                lang_label = f'[{lang_tag}]' if lang_tag else ''
                label = f'[{variant.upper()}]{lang_label}' if ab == 'all' else f'[GEN]{lang_label}'
                print(f'  {label}  id={lid} «{name}»')
                print(f'         → {preview}...')
                print(f'         {issue_tag}')

                # Only write the first (or only) variant to DB
                if not dry and variant == variants_to_run[0]:
                    code = patch_lead(lid, msg, ab_variant=variant)
                    sym  = 'OK' if code in (200, 204) else f'ERR {code}'
                    print(f'         → DB: [{sym}]')
                    if code in (200, 204): ok += 1
                    else:                  fail += 1
                elif dry:
                    print(f'         → DB: [DRY-RUN, not written]')
                    if variant == variants_to_run[0]: ok += 1
                else:
                    print(f'         → DB: [variant preview only, not written]')

            except Exception as e:
                print(f'  [ERR]  id={lid} «{name}» [{variant}]: {e}', file=sys.stderr)
                if variant == variants_to_run[0]: fail += 1

            if len(variants_to_run) > 1:
                time.sleep(0.5)  # small pause between variants for same lead

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — processed={ok+skipped+fail} | '
          f'uploaded={ok} | skipped={skipped} | fail={fail}')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
