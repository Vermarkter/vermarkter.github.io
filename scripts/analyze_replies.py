#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_replies.py — Classifies client email replies via GPT-4o-mini
and updates lead status in Supabase.

Intent labels:
  HOT    — wants a video call or meeting
  INFO   — asks about price / details / how it works
  REFUSE — not interested, unsubscribe, stop

Usage modes:
  1. Single reply from --text argument:
       python scripts/analyze_replies.py --id 162 --text "Ja, gerne ein kurzes Video"

  2. Read reply from a .txt file:
       python scripts/analyze_replies.py --id 162 --file data/reply_162.txt

  3. Batch: CSV file with columns id,reply_text  (no header required if --no-header):
       python scripts/analyze_replies.py --csv data/replies.csv

  4. Fetch unread replies from IMAP mailbox (reads [SMTP] / [IMAP] config):
       python scripts/analyze_replies.py --imap --limit 50

Flags:
  --dry-run      Classify but do NOT update Supabase
  --no-patch     Same as --dry-run for status field only
  --force        Re-classify leads already at HOT/INFO/REFUSE (skip by default)
  --model        OpenAI model (default: gpt-4o-mini)
  --show-reason  Print GPT reasoning line after each result

Config required (config.ini):
  [OPENAI]  api_key, model (optional)
  [SUPABASE] url, service_role_key (or anon_key)
  [IMAP]    host, port, user, password  ← only for --imap mode
"""

import sys, io, os, json, csv, time, argparse, configparser, urllib.request, urllib.parse

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

OPENAI_KEY  = _e('OPENAI_API_KEY') or _c('OPENAI', 'api_key')
OPENAI_MODEL = _e('OPENAI_MODEL')  or _c('OPENAI', 'model') or 'gpt-4o-mini'
SB_URL      = _e('SUPABASE_URL')   or _c('SUPABASE', 'url')
SB_KEY      = (_e('SUPABASE_KEY')
               or _valid_jwt(_c('SUPABASE', 'service_role_key'))
               or _valid_jwt(_c('SUPABASE', 'anon_key')))

if not OPENAI_KEY or 'PASTE' in OPENAI_KEY:
    print('[ERROR] OpenAI api_key not set in config.ini [OPENAI] or OPENAI_API_KEY env var.',
          file=sys.stderr)
    sys.exit(1)
if not SB_URL or not SB_KEY:
    print('[ERROR] SUPABASE_URL / SUPABASE_KEY not configured.', file=sys.stderr)
    sys.exit(1)

# Status values written back to beauty_leads.status
STATUS_MAP = {
    'HOT':    'reply_hot',
    'INFO':   'reply_info',
    'REFUSE': 'reply_refused',
}

# ── GPT classifier ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You classify email replies from German beauty salon owners who received a sales email.
Reply with EXACTLY one line in this format (nothing else):
LABEL | one-sentence reason in English

Labels:
  HOT    — client wants to see a demo, schedule a call/meeting, or shows clear purchase intent
  INFO   — client asks about price, features, timeline, or requests more details
  REFUSE — client says not interested, please stop, unsubscribe, or is clearly negative

If the reply is ambiguous but leans positive → INFO.
If empty or unreadable → REFUSE."""

USER_TEMPLATE = "Reply text:\n\"\"\"\n{text}\n\"\"\""


def classify(text: str, model: str) -> tuple[str, str]:
    """
    Returns (label, reason).
    label: 'HOT' | 'INFO' | 'REFUSE'
    reason: GPT's one-sentence explanation
    """
    payload = {
        'model': model,
        'max_tokens': 60,
        'temperature': 0,
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': USER_TEMPLATE.format(text=text[:2000])},
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=data,
        headers={
            'Authorization': f'Bearer {OPENAI_KEY}',
            'Content-Type':  'application/json',
        },
        method='POST',
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                resp    = json.loads(r.read().decode('utf-8'))
                content = resp['choices'][0]['message']['content'].strip()
                break
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            if e.code == 429:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'OpenAI HTTP {e.code}: {body[:200]}')
        except Exception as exc:
            if attempt == 2:
                raise
            time.sleep(1)

    # Parse "LABEL | reason"
    if '|' in content:
        raw_label, reason = content.split('|', 1)
    else:
        raw_label, reason = content, ''

    label = raw_label.strip().upper()
    if label not in STATUS_MAP:
        # fallback: search for any known label in the response
        for lbl in STATUS_MAP:
            if lbl in content.upper():
                label = lbl
                break
        else:
            label = 'INFO'  # safe default

    return label, reason.strip()


# ── Supabase ──────────────────────────────────────────────────────────────────

_SB_R = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
_SB_W = {**_SB_R, 'Content-Type': 'application/json; charset=utf-8', 'Prefer': 'return=minimal'}


def sb_patch(lead_id: int, payload: dict) -> str:
    url  = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(url, data=data, headers=_SB_W, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=20):
            return 'OK'
    except urllib.error.HTTPError as e:
        return f'ERR {e.code}: {e.read().decode("utf-8", errors="replace")[:120]}'


def sb_get_lead(lead_id: int) -> dict:
    url = (f"{SB_URL}/rest/v1/beauty_leads"
           f"?id=eq.{lead_id}&select=id,name,status&limit=1")
    with urllib.request.urlopen(
        urllib.request.Request(url, headers=_SB_R), timeout=20
    ) as r:
        rows = json.loads(r.read().decode('utf-8'))
        return rows[0] if rows else {}


# ── IMAP fetcher ──────────────────────────────────────────────────────────────

def fetch_imap_replies(limit: int) -> list[dict]:
    """
    Connects to IMAP (config.ini [IMAP] or [SMTP] fallback), reads UNSEEN emails
    in INBOX, tries to parse lead ID from subject or X-Lead-Id header.
    Returns list of {'id': int, 'text': str, 'subject': str, 'from': str}
    """
    import imaplib, email as emaillib
    from email.header import decode_header as dh

    host = _c('IMAP', 'host')     or _c('SMTP', 'host')
    port = int(_c('IMAP', 'port') or 993)
    user = _c('IMAP', 'user')     or _c('SMTP', 'user')
    pwd  = _c('IMAP', 'password') or _c('SMTP', 'password')

    if not host or not user or not pwd:
        print('[ERROR] IMAP credentials not found in config.ini [IMAP] section.', file=sys.stderr)
        sys.exit(1)

    def _decode_header(val):
        parts = dh(val or '')
        out = []
        for chunk, enc in parts:
            if isinstance(chunk, bytes):
                out.append(chunk.decode(enc or 'utf-8', errors='replace'))
            else:
                out.append(chunk)
        return ''.join(out)

    def _get_text(msg):
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == 'text/plain':
                    return part.get_payload(decode=True).decode(
                        part.get_content_charset() or 'utf-8', errors='replace')
        else:
            return msg.get_payload(decode=True).decode(
                msg.get_content_charset() or 'utf-8', errors='replace')
        return ''

    conn = imaplib.IMAP4_SSL(host, port)
    conn.login(user, pwd)
    conn.select('INBOX')

    _, msg_ids = conn.search(None, 'UNSEEN')
    all_ids = msg_ids[0].split()[-limit:]  # newest N

    results = []
    for mid in all_ids:
        _, data = conn.fetch(mid, '(RFC822)')
        msg     = emaillib.message_from_bytes(data[0][1])
        subject = _decode_header(msg.get('Subject', ''))
        from_   = _decode_header(msg.get('From', ''))
        text    = _get_text(msg)

        # Try to find lead ID: X-Lead-Id header first, then Subject match
        lead_id = None
        if msg.get('X-Lead-Id'):
            try: lead_id = int(msg['X-Lead-Id'])
            except ValueError: pass
        if not lead_id:
            import re
            m = re.search(r'lead[_\-]?id[:\s=]+(\d+)', subject, re.I)
            if m: lead_id = int(m.group(1))

        results.append({'id': lead_id, 'text': text, 'subject': subject, 'from': from_})

    conn.logout()
    return results


# ── Core processing ───────────────────────────────────────────────────────────

def process_one(lead_id: int | None, text: str, dry: bool, force: bool,
                model: str, show_reason: bool) -> dict:
    """
    Classify one reply. Optionally patch Supabase.
    Returns result dict.
    """
    text = text.strip()
    if not text:
        return {'id': lead_id, 'label': 'REFUSE', 'reason': 'empty reply', 'patched': False}

    # Skip if already classified (unless --force)
    if lead_id and not force:
        lead = sb_get_lead(lead_id)
        if lead.get('status', '') in STATUS_MAP.values():
            print(f'  [SKIP] id={lead_id} already {lead["status"]}')
            return {'id': lead_id, 'label': None, 'reason': 'already classified', 'patched': False}

    label, reason = classify(text, model)

    icon = {'HOT': '🔥', 'INFO': 'ℹ️', 'REFUSE': '🚫'}.get(label, '?')
    name_hint = f' (id={lead_id})' if lead_id else ''
    line = f'  {icon}  {label}{name_hint}'
    if show_reason:
        line += f'  ← {reason}'
    print(line)

    patched = False
    if lead_id and not dry:
        status = STATUS_MAP[label]
        result = sb_patch(lead_id, {'status': status, 'reply_text': text[:1000]})
        patched = result == 'OK'
        if not patched:
            print(f'     [WARN] Supabase patch: {result}')

    return {'id': lead_id, 'label': label, 'reason': reason, 'patched': patched}


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description='Classify email replies → HOT / INFO / REFUSE')
    src = p.add_mutually_exclusive_group()
    src.add_argument('--text',  default='', help='Reply text directly in CLI')
    src.add_argument('--file',  default='', help='Path to .txt file with reply text')
    src.add_argument('--csv',   default='', help='CSV with columns: id,reply_text')
    src.add_argument('--imap',  action='store_true', help='Fetch UNSEEN from IMAP inbox')

    p.add_argument('--id',          type=int, default=0,  help='Lead ID (for --text / --file)')
    p.add_argument('--limit',       type=int, default=50, help='Max replies to fetch (--imap)')
    p.add_argument('--no-header',   action='store_true',  help='CSV has no header row')
    p.add_argument('--dry-run',     action='store_true',  help='Classify only, no Supabase write')
    p.add_argument('--force',       action='store_true',  help='Re-classify already-labelled leads')
    p.add_argument('--model',       default=OPENAI_MODEL, help=f'OpenAI model (default: {OPENAI_MODEL})')
    p.add_argument('--show-reason', action='store_true',  help='Print GPT reasoning per result')
    return p.parse_args()


def main():
    args = parse_args()
    dry  = args.dry_run

    print(f'\n{"="*60}')
    print(f'  Reply Classifier  |  model={args.model}  |  {"DRY-RUN" if dry else "LIVE"}')
    print(f'{"="*60}\n')

    results = []

    # ── Mode 1: single --text
    if args.text:
        r = process_one(args.id or None, args.text, dry, args.force, args.model, args.show_reason)
        results.append(r)

    # ── Mode 2: --file
    elif args.file:
        with open(args.file, encoding='utf-8') as f:
            text = f.read()
        r = process_one(args.id or None, text, dry, args.force, args.model, args.show_reason)
        results.append(r)

    # ── Mode 3: --csv
    elif args.csv:
        with open(args.csv, encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            if not args.no_header:
                next(reader, None)
            rows = [(row[0].strip(), row[1].strip()) for row in reader if len(row) >= 2]

        print(f'  Loaded {len(rows)} rows from {args.csv}\n')
        for raw_id, text in rows:
            lead_id = int(raw_id) if raw_id.isdigit() else None
            r = process_one(lead_id, text, dry, args.force, args.model, args.show_reason)
            results.append(r)
            time.sleep(0.3)  # rate-limit OpenAI mini

    # ── Mode 4: --imap
    elif args.imap:
        replies = fetch_imap_replies(args.limit)
        print(f'  Fetched {len(replies)} UNSEEN emails from IMAP\n')
        for reply in replies:
            if not reply['id']:
                print(f'  [SKIP] No lead ID found — From: {reply["from"]} | Subject: {reply["subject"][:50]}')
                continue
            r = process_one(reply['id'], reply['text'], dry, args.force, args.model, args.show_reason)
            results.append(r)
            time.sleep(0.3)

    else:
        print('  No input specified. Use --text, --file, --csv, or --imap.')
        print('  Run with --help for usage.')
        return

    # ── Summary
    hot    = sum(1 for r in results if r['label'] == 'HOT')
    info   = sum(1 for r in results if r['label'] == 'INFO')
    refuse = sum(1 for r in results if r['label'] == 'REFUSE')
    skip   = sum(1 for r in results if r['label'] is None)

    print(f'\n{"="*60}')
    print(f'  DONE — total={len(results)} | 🔥 HOT={hot} | ℹ️  INFO={info} | 🚫 REFUSE={refuse} | skip={skip}')
    if dry:
        print('  DRY-RUN: Supabase NOT updated.')
    print(f'{"="*60}\n')

    # Hot leads — print names for immediate follow-up
    hot_leads = [r for r in results if r['label'] == 'HOT' and r['id']]
    if hot_leads:
        print('  🔥 HOT leads to contact NOW:')
        for r in hot_leads:
            print(f'     id={r["id"]}  ← {r["reason"]}')
        print()


if __name__ == '__main__':
    main()
