#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
upload_berlin_212_271.py — Patch Berlin leads 212-271 with Elite messages (no URLs).

IDs 212-219: hand-crafted Elite WA-style texts (no funnel JSON exists for these).
IDs 220-271: letter_1_digital_mirror body from funnel JSONs, URLs stripped.

Usage:
  python scripts/upload_berlin_212_271.py           # live write
  python scripts/upload_berlin_212_271.py --dry-run
"""

import sys, io, json, re, argparse, os, urllib.request, configparser

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

URL_PATTERN = re.compile(
    r'https?://\S+|www\.\S+|\S+\.(de|com|eu|salon|berlin|info|net|org)\S*',
    re.IGNORECASE
)

def strip_urls(text):
    cleaned = URL_PATTERN.sub('', text)
    cleaned = re.sub(r'\n---\nWHY BUY:.*', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'Demo:\s*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'  +', ' ', cleaned)
    return cleaned.strip()

# ── IDs 212-219: Elite WA-style messages (personalized, no links) ──────────
MANUAL_MESSAGES = {
    212: (
        "Hey Raven Barber Shop! 💈 Euer Name taucht in Berlin als Referenz auf — "
        "House of Fade empfiehlt euch, Kunden fahren aus anderen Bezirken extra rüber. "
        "Das ist echter Ruf. Aber: keine eigene Domain, Buchung läuft durch eine Plattform. "
        "Jeder Termin kostet Provision — für Kunden, die ihr selbst aufgebaut habt. "
        "23 Berliner Barbershops haben ihre Unabhängigkeit zurückgewonnen. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir zeigen soll, wie das konkret aussieht."
    ),
    213: (
        "Hey The Blade Berlin! ✂️ Euer Streetwear-Stil und präzise Fades — "
        "das ist eine Marke, keine Zufälligkeit. "
        "Aber kein SSL-Zertifikat. Wer euch durch Empfehlung entdeckt und die Seite öffnet, "
        "sieht sofort eine Browser-Sicherheitswarnung statt eures Terminformulars. "
        "23 Berliner Salons haben diesen ersten Eindruck geändert. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir das Beispiel zeigen soll."
    ),
    214: (
        "Hey Barbabella Barbershop! \U0001f4a8 Barbabella — der Name hat Charakter. "
        "Eure Bewertungen sprechen von Präzision und Atmosphäre, die Kunden zurückbringt. "
        "Aber kein SSL, keine sichere Online-Buchung. Neukunden, die euch googeln, "
        "verlassen die Seite wegen einer Sicherheitswarnung — bevor sie den Buchungsbutton sehen. "
        "23 Berliner Salons haben diesen Moment geändert. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir das Beispiel zeigen soll."
    ),
    215: (
        "Hey FADE CLUB Mitte! \U0001f4a8 Mitte — bester Standort, maximale Laufkundschaft. "
        "Euer Instagram zeigt cleane Fades auf einem Niveau, das Kunden bindet. "
        "Das Problem: kein SSL. Wer spontan buchen will, sieht eine rote Warnung "
        "statt eines Buchungsformulars. In Mitte ist das täglich verlorenes Geschäft. "
        "23 Berliner Salons haben das behoben. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir das Beispiel zeigen soll."
    ),
    216: (
        "Hey Co Barbers Berlin! ✂️ Das Konzept — kollaborativer Space, mehrere Barber unter einem Dach — "
        "ist in Berlin einzigartig. Aber keine eigene Website, Buchung nur über Treatwell. "
        "Ihr zahlt Provision für jeden Kunden, den ihr selbst aufgebaut habt. "
        "23 Berliner Betriebe haben ihre Direktbuchungen zurückgewonnen. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir zeigen soll, wie ihr euch befreit."
    ),
    217: (
        "Hey Barberremz Berlin! ✂️ Skin Fades mit Rasiermesser-Finish — "
        "die Kanten-Arbeit auf @barberremz ist in Berlin eine Seltenheit. "
        "Aber kein gültiges SSL. Wer euch entdeckt und direkt buchen will, "
        "sieht eine Browserwarnung statt eines Terminformulars. "
        "23 Berliner Salons haben diesen ersten Eindruck geändert. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir das Beispiel zeigen soll."
    ),
    218: (
        "Hey KHALED’S BARBERSHOP! \U0001f4a8 Eure Stammkunden kommen wegen Khaleds persönlicher Betreuung "
        "und dem Handwerk, das er ins Detail trägt. Das zeigen eure Bewertungen klar. "
        "Aber keine sichere Website. Neukunden sehen beim ersten Klick eine Browser-Warnung — "
        "und buchen woanders. 23 Berliner Salons haben diese Kleinigkeit behoben. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir das Beispiel zeigen soll."
    ),
    219: (
        "Hey The Bathroom Barber Co-Working! \U0001f4a8 Barbershop als Co-Working-Space — "
        "das ist eine Idee, die in Berlin funktioniert. Aber nur über Treatwell buchbar, "
        "keine eigene Domain, keine direkte Kundenbeziehung. "
        "Jeder Termin bringt Provisionskosten statt reinen Gewinn. "
        "23 Berliner Betriebe haben Treatwell den Rücken gekehrt. "
        "Antworte mit \u201eVideo\u201c, wenn ich dir das Beispiel zeigen soll."
    ),
}

# ── IDs 220-271: load from funnel JSONs ─────────────────────────────────────
FUNNEL_FILES = [
    os.path.join(_ROOT, 'data', 'email_funnels_berlin_220_239.json'),
    os.path.join(_ROOT, 'data', 'email_funnels_berlin_240_259.json'),
    os.path.join(_ROOT, 'data', 'email_funnels_berlin_260_271.json'),
]

FUNNEL_MESSAGES = {}
for fpath in FUNNEL_FILES:
    data = json.load(open(fpath, encoding='utf-8'))
    for entry in data:
        lid  = entry['id']
        body = entry.get('email_funnel', {}) \
                    .get('letter_1_digital_mirror', {}) \
                    .get('body', '')
        if body:
            FUNNEL_MESSAGES[lid] = strip_urls(body)

# ── Merge ────────────────────────────────────────────────────────────────────
ALL_MESSAGES = {}
for lid, msg in MANUAL_MESSAGES.items():
    ALL_MESSAGES[lid] = msg
for lid, msg in FUNNEL_MESSAGES.items():
    ALL_MESSAGES[lid] = msg   # funnel wins for 220-271

# ── Patch ────────────────────────────────────────────────────────────────────
def patch_lead(lead_id, message):
    payload = {'custom_message': message, 'status': 'READY TO SEND'}
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    url  = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req  = urllib.request.Request(url, data=data, headers=HDRS, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    dry = args.dry_run

    print(f'\n{"="*64}')
    print(f'  Berlin Elite Patch 212-271  |  {"DRY-RUN" if dry else "LIVE WRITE"}')
    print(f'  Total: {len(ALL_MESSAGES)} leads')
    print(f'{"="*64}\n')

    ok = fail = 0
    for lid in sorted(ALL_MESSAGES.keys()):
        msg = ALL_MESSAGES[lid]
        # Sanity: must not contain any http(s) links
        has_link = bool(re.search(r'https?://', msg))
        length_tag = f'{len(msg)}c' + (' ⚠LONG' if len(msg) > 800 else '') + (' ⛔LINK' if has_link else '')
        print(f'  ID {lid:>3} | {length_tag}')
        print(f'         → {msg[:100].replace(chr(10), " ")}...')

        if not dry:
            code = patch_lead(lid, msg)
            sym  = 'OK' if code in (200, 204) else f'ERR {code}'
            print(f'         → DB: [{sym}]')
            if code in (200, 204): ok += 1
            else:                  fail += 1
        else:
            print(f'         → DB: [DRY-RUN]')
            ok += 1

    print(f'\n{"="*64}')
    print(f'  DONE — total={len(ALL_MESSAGES)} | ok={ok} | fail={fail}')
    if dry:
        print('  DRY-RUN: nothing written.')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
