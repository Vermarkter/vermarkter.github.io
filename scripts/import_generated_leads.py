#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import_generated_leads.py — Import Claude Pro-generated offers into Supabase.

Reads a JSON array and updates:
  - custom_message     ← wa_text
  - email_funnel_json  ← {
        "letter_1_digital_mirror": letter_1,
        "letter_2_future_vision":  letter_2,   (optional)
        "letter_3_scarcity":       letter_3,   (optional)
    }
  - status             ← "email_ready" (if any email text) | "new" (wa-only)
  - last_error         ← null  (cleared on import)

Signature rules (--check-signatures, default ON):
  - notes contains [Sniper FR UA] or lang=ua → expects "Андрій" somewhere in signature
  - otherwise (FR/AR/default)               → expects "Équipe Vermarkter" or "equipe vermarkter"
  Mismatches are printed as [WARN] but do NOT block the import.

Input JSON format (all fields optional except id):
  [
    {
      "id": 123,
      "whatsapp":               "Bonjour...",          // → custom_message
      "wa_text":                "Bonjour...",          // alias for whatsapp
      "letter_1_subject":       "Objet: ...",          // → email_funnel_json.letter_1_subject
      "letter_1_digital_mirror":"Bonjour,...",         // → email_funnel_json.letter_1_digital_mirror
      "letter_2_subject":       "Objet: ...",
      "letter_2_future_vision": "Bonjour,...",
      "letter_3_subject":       "Objet: ...",
      "letter_3_scarcity":      "Bonjour,..."
    },
    ...
  ]
  Any subset of fields is valid. status=email_ready if any letter present, else new.

Usage:
  python scripts/import_generated_leads.py --file cannes_offers.json
  python scripts/import_generated_leads.py --file cannes_offers.json --dry-run
  cat offers.json | python scripts/import_generated_leads.py --stdin
  python scripts/import_generated_leads.py --file offers.json --no-check-signatures
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, time, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _e(k):  return (os.environ.get(k) or '').strip()
def _c(s, k):
    try:    return (_cfg.get(s, k) or '').strip()
    except: return ''

SB_URL = _e('SUPABASE_URL') or _c('SUPABASE', 'url')
_svc   = _c('SUPABASE', 'service_role_key')
SB_KEY = (_e('SUPABASE_KEY')
          or (_svc if len(_svc) > 80 and 'PASTE' not in _svc else '')
          or _c('SUPABASE', 'anon_key'))

HDRS_PATCH = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal',
}

HDRS_GET = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
}

# Signature keywords by language tag
_SIG_UA = 'Андрій'
_SIG_FR = 'Équipe Vermarkter'
_SIG_FR_LOW = 'equipe vermarkter'


def _detect_lang_tag(notes: str) -> str:
    """Returns 'ua' if notes contain UA tag, else 'fr'."""
    if not notes:
        return 'fr'
    notes_up = notes.upper()
    if 'SNIPER FR UA' in notes_up:
        return 'ua'
    return 'fr'


def _check_signature(text: str, lang: str) -> bool:
    """Returns True if text contains the expected signature for the language."""
    if not text:
        return True  # no text → nothing to check
    if lang == 'ua':
        return _SIG_UA in text
    else:
        return _SIG_FR in text or _SIG_FR_LOW in text.lower()


def fetch_lead_notes(lead_ids: list) -> dict:
    """Fetch id→notes mapping for signature checking."""
    if not lead_ids:
        return {}
    id_str = ','.join(str(i) for i in lead_ids)
    url = f"{SB_URL}/rest/v1/beauty_leads?id=in.({id_str})&select=id,notes"
    req = urllib.request.Request(url, headers=HDRS_GET)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            rows = json.loads(r.read())
            return {row['id']: (row.get('notes') or '') for row in rows}
    except Exception as exc:
        print(f'  [WARN] Could not fetch notes for sig check: {exc}', file=sys.stderr)
        return {}


def fetch_lead_emails(lead_ids: list) -> set:
    """Return set of lead IDs that already have a non-null email address."""
    if not lead_ids:
        return set()
    id_str = ','.join(str(i) for i in lead_ids)
    url = f"{SB_URL}/rest/v1/beauty_leads?id=in.({id_str})&email=not.is.null&select=id"
    req = urllib.request.Request(url, headers=HDRS_GET)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            rows = json.loads(r.read())
            return {row['id'] for row in rows}
    except Exception as exc:
        print(f'  [WARN] Could not fetch emails for status check: {exc}', file=sys.stderr)
        return set()


def patch_lead(lead_id: int,
               letter1: str, letter1_subj: str,
               letter2: str, letter2_subj: str,
               letter3: str, letter3_subj: str,
               wa_text: str, status: str, dry: bool) -> str:
    if dry:
        return 'dry'

    # Build email_funnel_json — body and subject stored as separate keys
    funnel = {}
    if letter1:
        funnel['letter_1_digital_mirror'] = letter1
    if letter1_subj:
        funnel['letter_1_subject'] = letter1_subj
    if letter2:
        funnel['letter_2_future_vision'] = letter2
    if letter2_subj:
        funnel['letter_2_subject'] = letter2_subj
    if letter3:
        funnel['letter_3_scarcity'] = letter3
    if letter3_subj:
        funnel['letter_3_subject'] = letter3_subj

    body = {'status': status, 'last_error': None}
    if funnel:
        body['email_funnel_json'] = funnel
    if wa_text:
        body['custom_message'] = wa_text

    payload = json.dumps(body, ensure_ascii=False).encode('utf-8')
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=payload, headers=HDRS_PATCH, method='PATCH')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return 'ok'
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                return f'err {e.code}'
        except Exception:
            time.sleep(1)
    return 'timeout'


def load_records(args) -> list:
    if args.stdin:
        raw = sys.stdin.read()
    elif args.file:
        path = args.file if os.path.isabs(args.file) else os.path.join(_ROOT, args.file)
        with open(path, encoding='utf-8') as f:
            raw = f.read()
    else:
        print('[ERROR] Provide --file or --stdin', file=sys.stderr)
        sys.exit(1)

    raw = raw.strip()

    # Strip markdown code fence if Claude Pro wrapped it
    if raw.startswith('```'):
        lines = raw.splitlines()
        raw = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f'[ERROR] JSON parse failed: {e}', file=sys.stderr)
        print('First 200 chars:', raw[:200], file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print('[ERROR] Expected JSON array at top level', file=sys.stderr)
        sys.exit(1)

    return data


def parse_args():
    p = argparse.ArgumentParser(description='Import Claude Pro-generated offers → Supabase')
    p.add_argument('--file',    default='', help='Path to JSON file with offers')
    p.add_argument('--stdin',   action='store_true', help='Read JSON from stdin')
    p.add_argument('--status',  default='email_ready', help='Status to set (default: email_ready)')
    p.add_argument('--dry-run', action='store_true',   help='No DB writes, preview only')
    p.add_argument('--delay',   type=float, default=0.1, help='Seconds between patches (default: 0.1)')
    p.add_argument('--no-check-signatures', action='store_true',
                   help='Skip signature language validation')
    return p.parse_args()


def main():
    args = parse_args()
    dry  = args.dry_run
    check_sigs = not args.no_check_signatures

    print(f'\n{"="*64}')
    print(f'  Import Generated Leads  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'  Target status: {args.status}  |  Sig-check: {"ON" if check_sigs else "OFF"}')
    print(f'{"="*64}\n')

    records = load_records(args)
    print(f'Loaded {len(records)} records from input\n')

    # Pre-fetch notes for signature checking
    all_ids = [rec.get('id') for rec in records if rec.get('id')]
    notes_map  = fetch_lead_notes(all_ids) if check_sigs else {}
    emails_set = fetch_lead_emails(all_ids)

    ok_count   = 0
    err_count  = 0
    skip_count = 0
    sig_warn   = 0

    for rec in records:
        lead_id = rec.get('id')
        letter1      = (rec.get('letter_1') or rec.get('letter_1_digital_mirror') or '').strip()
        letter1_subj = (rec.get('letter_1_subject') or '').strip()
        letter2      = (rec.get('letter_2') or rec.get('letter_2_future_vision')  or '').strip()
        letter2_subj = (rec.get('letter_2_subject') or '').strip()
        letter3      = (rec.get('letter_3') or rec.get('letter_3_scarcity')       or '').strip()
        letter3_subj = (rec.get('letter_3_subject') or '').strip()
        wa_text      = (rec.get('wa_text') or rec.get('whatsapp') or '').strip()

        if not lead_id:
            print(f'  [SKIP] No "id" field in record: {str(rec)[:80]}')
            skip_count += 1
            continue

        if not letter1 and not letter2 and not letter3 and not wa_text:
            print(f'  [SKIP] id={lead_id} — no letter_1/2/3 and no wa_text')
            skip_count += 1
            continue

        # Hard block: reject any record containing URLs or domain suffixes.
        # AI-generated text must never include links — they indicate a hallucinated
        # or incorrectly formatted batch that would damage deliverability.
        _all_text = ' '.join([letter1, letter2, letter3, wa_text])
        _link_rx  = re.compile(r'https?://|www\.|\.eu\b|\.de\b|\.fr\b|\.com\b|\.net\b', re.I)
        _link_hit = _link_rx.search(_all_text)
        if _link_hit:
            print(f'  [BLOCK] id={lead_id} — URL/domain found: "{_link_hit.group(0)}" — import rejected for this record')
            err_count += 1
            continue

        # Status: email_ready only if letters exist AND lead already has an email address.
        # Without an email address, storing letters as 'funnel_ready' avoids false-positives
        # in the send queue — the dispatcher requires email IS NOT NULL.
        has_letters = bool(letter1 or letter2 or letter3)
        has_email_addr = lead_id in emails_set
        if has_letters and has_email_addr:
            status = args.status  # → 'email_ready' (default)
        elif has_letters:
            status = 'funnel_ready'  # letters generated but no email yet
        else:
            status = 'new'  # wa-only or empty

        # Signature check
        if check_sigs and has_letters:
            notes = notes_map.get(lead_id, '')
            lang  = _detect_lang_tag(notes)
            # Check all present letters
            for lname, ltext in [('letter_1', letter1), ('letter_2', letter2), ('letter_3', letter3)]:
                if ltext and not _check_signature(ltext, lang):
                    expected = _SIG_UA if lang == 'ua' else _SIG_FR
                    print(f'  [WARN] id={lead_id} {lname}: signature mismatch '
                          f'(lang={lang}, expected "{expected}")')
                    sig_warn += 1

        # Channel tag for display
        channel_tag = []
        if has_letters:
            parts = []
            if letter1: parts.append('L1')
            if letter2: parts.append('L2')
            if letter3: parts.append('L3')
            channel_tag.append('EMAIL(' + '+'.join(parts) + ')')
        if wa_text: channel_tag.append('WA')
        tag_str = '+'.join(channel_tag)

        preview = (letter1 or letter2 or wa_text).replace('\n', ' ')[:70]
        result  = patch_lead(lead_id,
                             letter1, letter1_subj,
                             letter2, letter2_subj,
                             letter3, letter3_subj,
                             wa_text, status, dry)

        icon = {'ok': 'OK', 'dry': '~', 'timeout': 'TO'}.get(result, 'ERR')
        print(f'  [{icon}] id={lead_id} [{tag_str}] status={status}  |  {preview}...')

        if result in ('ok', 'dry'):
            ok_count += 1
        else:
            err_count += 1

        time.sleep(args.delay)

    print(f'\n{"="*64}')
    print(f'  DONE — ok={ok_count} | errors={err_count} | skipped={skip_count}')
    if sig_warn:
        print(f'  SIG WARNINGS: {sig_warn} (check manually)')
    if dry:
        print('  DRY-RUN: nothing written to DB.')
    print(f'{"="*64}\n')


if __name__ == '__main__':
    main()
