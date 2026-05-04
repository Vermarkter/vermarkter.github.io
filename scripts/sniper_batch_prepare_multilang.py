#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_batch_prepare_multilang.py — Build OpenAI Batch JSONL for TR/AR leads.

Detects Turkish/Arabic leads by name using sniper_lang_detect.py.
Generates personalized German offers with multilingual digital package accent.

Usage:
  python scripts/sniper_batch_prepare_multilang.py                        # Berlin, all statuses
  python scripts/sniper_batch_prepare_multilang.py --city Essen
  python scripts/sniper_batch_prepare_multilang.py --city Berlin --limit 50
  python scripts/sniper_batch_prepare_multilang.py --city Berlin --status new
  python scripts/sniper_batch_prepare_multilang.py --city Berlin --force   # include any status
  python scripts/sniper_batch_prepare_multilang.py --out batch/tr_ar_berlin.jsonl

Output: batch/<city>_multilang_<timestamp>.jsonl
Run next: python scripts/sniper_batch_submit.py --file <output>
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, 'scripts'))
from sniper_lang_detect import detect as lang_detect

# ── Config ────────────────────────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}

OPENAI_MODEL = 'gpt-4o'
FIELDS = 'id,name,city,district,phone,email,website,notes,custom_message,status'

# ── System prompts ────────────────────────────────────────────────────────────

SYSTEM_PROMPT_TR = """Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.
Anrede AUSSCHLIESSLICH „Sie". Niemals „Hey" oder „Hi".

GRAMMATIK-PFLICHT (Separable Verbs):
- RICHTIG: „Das schreckt ca. 70 % Ihrer potenziellen Kunden ab"
- FALSCH:  „Das abschreckt" — NIEMALS so schreiben

PRODUKT-WAHRHEIT (PFLICHT — niemals einschränken):
Unser digitales Paket unterstützt 10 Sprachen: Deutsch, Englisch, Türkisch, Arabisch,
Französisch, Spanisch, Polnisch, Russisch, Ukrainisch, Chinesisch.
Das bedeutet: JEDER Kunde dieses Salons — egal welche Muttersprache — kann online buchen.
Das ist ein direkter Vorteil gegenüber Treatwell und allen rein deutschen Mitbewerbern.

BESONDERER KONTEXT (türkischstämmiger Salon):
Dieser Salon hat eine türkischsprachige Kundschaft. Betone, dass Türkisch EINE von 10
verfügbaren Sprachen ist — das signalisiert Premiumqualität, nicht nur eine Nischenlösung.

NACHRICHTENFORMAT — ZWEISPRACHIG (PFLICHT):
Das Ergebnis besteht aus ZWEI BLÖCKEN in einem einzigen WhatsApp-Nachricht:
  Block 1: Vollständige Nachricht auf DEUTSCH
  [eine Leerzeile]
  Block 2: Dieselbe Nachricht auf TÜRKISCH (direkte inhaltliche Übersetzung, gleiches Angebot)

FEW-SHOT BEISPIEL (exakt diesen Aufbau einhalten):

Guten Tag, viele Ihrer Kunden buchen lieber auf Türkisch – Ihre Website ist nur auf Deutsch. Wir bieten Website, App und WhatsApp-Assistent in 10 Sprachen (inkl. Türkisch) – mehr als Treatwell. Einmalig 1.000 €. Darf ich Ihnen ein kurzes Video-Demo mit Ihrem zukünftigen Interface auf 10 Sprachen schicken?
Beste Grüße, Ihr Vermarkter-Team

Merhaba, müşterilerinizin çoğu Türkçe rezervasyon yapmayı tercih ediyor – web siteniz yalnızca Almanca. Web sitesi, uygulama ve WhatsApp asistanı 10 dilde (Türkçe dahil) – Treatwell'den daha fazlası. Tek seferlik 1.000 €. Size 10 dilli arayüzünüzü gösteren kısa bir video demo gönderebilir miyim?
Sevgiler, Vermarkter Ekibi

REGELN (ALLE PFLICHT):
- Jeder Block: MAXIMAL 480 Zeichen — zähle exakt, kürze gnadenlos
- IMMER „10 Sprachen" erwähnen — NIEMALS „nur Deutsch und Türkisch" schreiben
- IMMER Treatwell als Benchmark nennen (implizit oder explizit)
- SSL-Problem NUR erwähnen wenn ssl=n in den Notizen
- Kein Booking → erwähne verlorene Buchungen außerhalb der Öffnungszeiten
- Angebot: Website + App + WhatsApp-Assistent — einmalig 1.000 €
- CTA (PFLICHT, WÖRTLICH auf DE): „Darf ich Ihnen ein kurzes Video-Demo mit Ihrem zukünftigen Interface auf 10 Sprachen schicken?"
- CTA auf TR (PFLICHT, WÖRTLICH): „Size 10 dilli arayüzünüzü gösteren kısa bir video demo gönderebilir miyim?"
- KEIN Link in der Nachricht — Link wird nur nach Antwort gesendet
- Unterschrift DE: „Beste Grüße, Ihr Vermarkter-Team"
- Unterschrift TR: „Sevgiler, Vermarkter Ekibi"
- Türkische Übersetzung: inhaltlich korrekt, kein Google-Translate-Stil

Output: NUR den zweisprachigen Nachrichtentext (DE + TR) — keine Erklärungen, keine Labels."""

SYSTEM_PROMPT_AR = """Du bist ein elitärer Berater für digitale Transformation. Stil: Modern Professional.
Anrede AUSSCHLIESSLICH „Sie". Niemals „Hey" oder „Hi".

GRAMMATIK-PFLICHT (Separable Verbs):
- RICHTIG: „Das schreckt ca. 70 % Ihrer potenziellen Kunden ab"
- FALSCH:  „Das abschreckt" — NIEMALS so schreiben

PRODUKT-WAHRHEIT (PFLICHT — niemals einschränken):
Unser digitales Paket unterstützt 10 Sprachen: Deutsch, Englisch, Türkisch, Arabisch,
Französisch, Spanisch, Polnisch, Russisch, Ukrainisch, Chinesisch.
Das bedeutet: JEDER Kunde dieses Salons — egal welche Muttersprache — kann online buchen.
Das ist ein direkter Vorteil gegenüber Treatwell und allen rein deutschen Mitbewerbern.

BESONDERER KONTEXT (arabischstämmiger Salon):
Dieser Salon bedient eine arabischsprachige Kundschaft. Betone, dass Arabisch EINE von 10
verfügbaren Sprachen ist — das signalisiert Premiumqualität, nicht nur eine Nischenlösung.

NACHRICHTENFORMAT — ZWEISPRACHIG (PFLICHT):
Das Ergebnis besteht aus ZWEI BLÖCKEN in einer einzigen WhatsApp-Nachricht:
  Block 1: Vollständige Nachricht auf DEUTSCH
  [eine Leerzeile]
  Block 2: Dieselbe Nachricht auf ARABISCH (direkte inhaltliche Übersetzung, gleiches Angebot)

FEW-SHOT BEISPIEL (exakt diesen Aufbau einhalten):

Guten Tag, viele Ihrer Kunden buchen lieber auf Arabisch – Ihre Website ist nur auf Deutsch. Wir bieten Website, App und WhatsApp-Assistent in 10 Sprachen (inkl. Arabisch) – mehr als Treatwell. Einmalig 1.000 €. Darf ich Ihnen ein kurzes Video-Demo mit Ihrem zukünftigen Interface auf 10 Sprachen schicken?
Beste Grüße, Ihr Vermarkter-Team

مرحباً، كثير من عملائكم يفضلون الحجز بالعربية – موقعكم باللغة الألمانية فقط. نقدم موقعاً وتطبيقاً ومساعداً عبر واتساب بـ10 لغات (منها العربية) – أكثر من Treatwell. مرة واحدة بـ1.000 €. هل يمكنني إرسال فيديو قصير يعرض واجهتكم المستقبلية بـ10 لغات؟
مع أطيب التحيات، فريق Vermarkter

REGELN (ALLE PFLICHT):
- Jeder Block: MAXIMAL 480 Zeichen — zähle exakt, kürze gnadenlos
- IMMER „10 Sprachen" erwähnen — NIEMALS „nur Deutsch und Arabisch" schreiben
- IMMER Treatwell als Benchmark nennen (implizit oder explizit)
- SSL-Problem NUR erwähnen wenn ssl=n in den Notizen
- Kein Booking → erwähne verlorene Buchungen außerhalb der Öffnungszeiten
- Angebot: Website + App + WhatsApp-Assistent — einmalig 1.000 €
- CTA (PFLICHT, WÖRTLICH auf DE): „Darf ich Ihnen ein kurzes Video-Demo mit Ihrem zukünftigen Interface auf 10 Sprachen schicken?"
- CTA auf AR (PFLICHT, WÖRTLICH): „هل يمكنني إرسال فيديو قصير يعرض واجهتكم المستقبلية بـ10 لغات؟"
- KEIN Link in der Nachricht — Link wird nur nach Antwort gesendet
- Unterschrift DE: „Beste Grüße, Ihr Vermarkter-Team"
- Unterschrift AR: „مع أطيب التحيات، فريق Vermarkter"
- Arabische Übersetzung: RTL-Schrift, inhaltlich korrekt, kein Google-Translate-Stil

Output: NUR den zweisprachigen Nachrichtentext (DE + AR) — keine Erklärungen, keine Labels."""

# ── User prompt builder ───────────────────────────────────────────────────────
def build_user_prompt(lead, lang_tag):
    notes   = lead.get('notes') or ''
    website = lead.get('website') or 'keine Website bekannt'
    phone   = lead.get('phone') or 'unbekannt'
    city    = lead.get('city') or lead.get('district') or 'Deutschland'
    contact = 'WhatsApp' if phone and phone != 'unbekannt' else 'E-Mail'

    has_booking = 'booking=y' in notes.lower()
    mobile_ok   = 'mobile=y' in notes.lower()
    ssl_ok      = 'ssl=y' in notes.lower()

    weaknesses = []
    if not has_booking: weaknesses.append('kein Online-Booking')
    if not mobile_ok:   weaknesses.append('mobile Optimierung fehlt')
    if not ssl_ok:      weaknesses.append('SSL-Problem')

    weakness_text = (', '.join(weaknesses) + ' — das kostet Neukunden.') if weaknesses \
                    else 'Potenzial bei Neukunden-Gewinnung über Google und Meta.'

    lang_label = 'türkischstämmig (TR_priority)' if lang_tag == 'TR' else 'arabischstämmig (AR_priority)'

    return (f"Salon: {lead['name']}\n"
            f"Stadt: {city}\n"
            f"Website: {website}\n"
            f"Kontakt via: {contact}\n"
            f"Kundschaft: {lang_label}\n"
            f"Audit-Befund: {weakness_text}\n\n"
            f"Schreib eine WhatsApp-Erstkontakt-Nachricht laut System-Anweisungen.")

# ── JSONL builder ─────────────────────────────────────────────────────────────
def build_jsonl_line(lead, lang_tag):
    system_prompt = SYSTEM_PROMPT_TR if lang_tag == 'TR' else SYSTEM_PROMPT_AR
    return json.dumps({
        "custom_id": str(lead['id']),
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": OPENAI_MODEL,
            "max_tokens": 300,
            "temperature": 0.75,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": build_user_prompt(lead, lang_tag)},
            ]
        }
    }, ensure_ascii=False)

# ── Supabase fetch (paginated) ────────────────────────────────────────────────
def fetch_all_leads(city, limit, status_filter, force):
    leads = []
    offset = 0
    page_size = 1000
    city_enc = urllib.parse.quote(city, safe='')
    while True:
        effective_limit = min(page_size, limit - len(leads)) if limit else page_size
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&city=eq.{city_enc}"
               f"&order=id.asc"
               f"&limit={effective_limit}"
               f"&offset={offset}")
        if status_filter and not force:
            url += f"&status=eq.{urllib.parse.quote(status_filter, safe='')}"
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

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Batch Prepare (Multilang) — TR/AR lead targeting')
    p.add_argument('--city',   default='Berlin')
    p.add_argument('--limit',  type=int, default=0, help='Max leads to scan (0 = all)')
    p.add_argument('--status', default='', help='Filter by status (default: all)')
    p.add_argument('--force',  action='store_true',
                   help='Include leads that already have custom_message (for re-generation)')
    p.add_argument('--out',    default='', help='Output path (default: batch/<city>_multilang_<ts>.jsonl)')
    p.add_argument('--dry-run', action='store_true', help='Print detected leads, do not write JSONL')
    return p.parse_args()

def main():
    args = parse_args()

    out_dir = os.path.join(_ROOT, 'batch')
    os.makedirs(out_dir, exist_ok=True)

    if args.out:
        out_path = args.out if os.path.isabs(args.out) else os.path.join(_ROOT, args.out)
    else:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = os.path.join(out_dir, f"{args.city.lower()}_multilang_{ts}.jsonl")

    print(f'\n{"="*64}')
    print(f'  Sniper Batch Prepare — MULTILANG (TR/AR)')
    print(f'  City:   {args.city}  |  model={OPENAI_MODEL}')
    print(f'  Status: {args.status or "all"}  |  limit={args.limit or "all"}  |  force={args.force}')
    print(f'{"="*64}\n')

    print('Fetching leads from Supabase...')
    leads = fetch_all_leads(args.city, args.limit or 0, args.status, args.force)
    print(f'Fetched {len(leads)} leads. Running language detection...\n')

    tagged = []
    skipped_no_tag = 0
    for l in leads:
        tag = lang_detect(l['name'])
        if tag:
            tagged.append((l, tag))
        else:
            skipped_no_tag += 1

    tr_count = sum(1 for _, t in tagged if t == 'TR')
    ar_count = sum(1 for _, t in tagged if t == 'AR')

    print(f'Detected:  TR={tr_count}  AR={ar_count}  Total={len(tagged)}')
    print(f'Skipped (no TR/AR signal): {skipped_no_tag}\n')

    if not tagged:
        print('No TR/AR leads found — nothing to do.')
        return

    print('Detected leads:')
    for l, tag in tagged:
        print(f'  [{tag}] id={l["id"]:5d} status={l["status"]:15s} — {l["name"]}')

    if args.dry_run:
        print(f'\nDRY-RUN: JSONL not written.')
        return

    with open(out_path, 'w', encoding='utf-8') as f:
        for l, tag in tagged:
            f.write(build_jsonl_line(l, tag) + '\n')

    size_kb = os.path.getsize(out_path) / 1024
    print(f'\n  Output: {out_path}')
    print(f'  Lines:  {len(tagged)}')
    print(f'  Size:   {size_kb:.1f} KB')
    print(f'\n  Next step:')
    print(f'  python scripts/sniper_batch_submit.py --file "{out_path}"')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
