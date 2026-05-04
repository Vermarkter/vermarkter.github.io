#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_batch_prepare.py — Build OpenAI Batch API .jsonl input file.

Fetches all status='new' leads for a city, writes one JSONL line per lead.
Each line is a complete /v1/chat/completions request with custom_id = lead ID.

Usage:
  python scripts/sniper_batch_prepare.py                        # Berlin, all new
  python scripts/sniper_batch_prepare.py --city München
  python scripts/sniper_batch_prepare.py --city Berlin --limit 500
  python scripts/sniper_batch_prepare.py --city Berlin --force  # include leads with existing message
  python scripts/sniper_batch_prepare.py --out batch/berlin_batch.jsonl

Output: batch/berlin_batch_<timestamp>.jsonl  (or --out path)
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, re
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Config ────────────────────────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}

OPENAI_MODEL = 'gpt-4o'  # hardcoded — never downgrade to mini or 3.5
FIELDS = 'id,name,city,district,phone,email,website,notes,custom_message'

# ── Ultimate v5 System Prompt ─────────────────────────────────────────────────
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

# ── Supabase fetch (paginated) ────────────────────────────────────────────────
def fetch_all_leads(city, limit, force):
    leads = []
    offset = 0
    page_size = 1000
    city_enc = urllib.parse.quote(city, safe='')
    while True:
        effective_limit = min(page_size, limit - len(leads)) if limit else page_size
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&city=eq.{city_enc}"
               f"&status=eq.new"
               f"&order=id.asc"
               f"&limit={effective_limit}"
               f"&offset={offset}")
        req = urllib.request.Request(url, headers=HDRS)
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode('utf-8'))
        leads.extend(batch)
        if len(batch) < effective_limit or (limit and len(leads) >= limit):
            break
        offset += page_size
    if limit:
        leads = leads[:limit]
    if not force:
        leads = [l for l in leads if not l.get('custom_message')]
    return leads

# ── User prompt builder (mirrors sniper_engine.py) ───────────────────────────
def build_user_prompt(lead):
    notes    = lead.get('notes') or ''
    website  = lead.get('website') or 'keine Website bekannt'
    phone    = lead.get('phone') or 'unbekannt'
    city     = lead.get('city') or lead.get('district') or 'Deutschland'
    contact  = 'WhatsApp' if phone and phone != 'unbekannt' else 'E-Mail'

    has_booking = 'booking=y' in notes.lower()
    mobile_ok   = 'mobile=y' in notes.lower()
    ssl_ok      = 'ssl=y' in notes.lower()

    weaknesses = []
    if not has_booking: weaknesses.append('kein Online-Booking')
    if not mobile_ok:   weaknesses.append('mobile Optimierung fehlt')
    if not ssl_ok:      weaknesses.append('SSL-Problem')

    weakness_text = (', '.join(weaknesses) + ' — das kostet Neukunden.') if weaknesses \
                    else 'Potenzial bei Neukunden-Gewinnung über Google und Meta.'

    return (f"Salon: {lead['name']}\n"
            f"Stadt: {city}\n"
            f"Website: {website}\n"
            f"Kontakt via: {contact}\n"
            f"Audit-Befund: {weakness_text}\n\n"
            f"Schreib eine WhatsApp-Erstkontakt-Nachricht laut System-Anweisungen.")

# ── JSONL builder ─────────────────────────────────────────────────────────────
def build_jsonl_line(lead):
    return json.dumps({
        "custom_id": str(lead['id']),
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": OPENAI_MODEL,
            "max_tokens": 300,
            "temperature": 0.75,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_prompt(lead)},
            ]
        }
    }, ensure_ascii=False)

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Batch Prepare — build OpenAI batch JSONL')
    p.add_argument('--city',  default='Berlin')
    p.add_argument('--limit', type=int, default=0, help='Max leads (0 = all)')
    p.add_argument('--force', action='store_true', help='Include leads that already have custom_message')
    p.add_argument('--out',   default='', help='Output file path (default: batch/<city>_batch_<ts>.jsonl)')
    return p.parse_args()

def main():
    args = parse_args()

    out_dir = os.path.join(_ROOT, 'batch')
    os.makedirs(out_dir, exist_ok=True)

    if args.out:
        out_path = args.out if os.path.isabs(args.out) else os.path.join(_ROOT, args.out)
    else:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = os.path.join(out_dir, f"{args.city.lower()}_batch_{ts}.jsonl")

    print(f'\n{"="*64}')
    print(f'  Sniper Batch Prepare  |  city={args.city}  |  model={OPENAI_MODEL}')
    print(f'  force={args.force}  |  limit={args.limit or "all"}')
    print(f'{"="*64}\n')

    print('Fetching leads from Supabase...')
    leads = fetch_all_leads(args.city, args.limit or 0, args.force)

    if not leads:
        print('No leads found — nothing to do.')
        return

    print(f'Fetched {len(leads)} leads → writing JSONL...')

    with open(out_path, 'w', encoding='utf-8') as f:
        for lead in leads:
            f.write(build_jsonl_line(lead) + '\n')

    size_kb = os.path.getsize(out_path) / 1024
    print(f'\n  Output: {out_path}')
    print(f'  Lines:  {len(leads)}')
    print(f'  Size:   {size_kb:.1f} KB')
    print(f'\n  Next step:')
    print(f'  python scripts/sniper_batch_submit.py --file "{out_path}"')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
