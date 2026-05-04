#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_batch_finalize.py — Download completed batch results and patch Supabase.

Checks batch status. If completed:
  - Downloads output JSONL
  - Parses each line: custom_id → lead ID, content → message text
  - PATCHes Supabase: custom_message + status='READY TO SEND'
  - Reports per-lead result

If still running, prints current progress and exits (use --wait to poll).

Usage:
  python scripts/sniper_batch_finalize.py --batch-id batch_abc123
  python scripts/sniper_batch_finalize.py --batch-id batch_abc123 --wait
  python scripts/sniper_batch_finalize.py --batch-id batch_abc123 --dry-run
  python scripts/sniper_batch_finalize.py --auto   # reads .batch_id.txt from batch/ dir
"""

import sys, io, os, json, argparse, configparser, time, urllib.request, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from openai import OpenAI
except ImportError:
    print('[ERROR] openai not installed. Run:  pip install openai', file=sys.stderr)
    sys.exit(1)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Config ────────────────────────────────────────────────────────────────────
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

OPENAI_KEY = (
    _env.get('OPENAI_API_KEY')
    or os.environ.get('OPENAI_API_KEY', '')
    or _cfg.get('OPENAI', 'api_key', fallback='')
).strip()

if not OPENAI_KEY or not OPENAI_KEY.startswith('sk-') or 'PASTE' in OPENAI_KEY:
    print('[ERROR] OPENAI_API_KEY missing or invalid.\n'
          '  Set in .env:  OPENAI_API_KEY=sk-proj-...', file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=OPENAI_KEY)

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS_PATCH = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

# ── Supabase patch ────────────────────────────────────────────────────────────
def patch_lead(lead_id, message):
    payload = json.dumps({
        'custom_message': message,
        'status': 'READY TO SEND',
    }).encode('utf-8')
    url = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req = urllib.request.Request(url, data=payload, headers=HDRS_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code

# ── Batch status helper ───────────────────────────────────────────────────────
def print_status(b):
    rc = b.request_counts
    total = rc.total if rc else '?'
    done  = rc.completed if rc else '?'
    fail  = rc.failed if rc else '?'
    print(f'  Status:     {b.status}')
    print(f'  Requests:   total={total}  completed={done}  failed={fail}')
    if b.expires_at:
        import datetime
        exp = datetime.datetime.fromtimestamp(b.expires_at).strftime('%Y-%m-%d %H:%M')
        print(f'  Expires at: {exp}')

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Batch Finalize — download results and patch Supabase')
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--batch-id', help='OpenAI Batch ID (batch_xxx...)')
    grp.add_argument('--auto',     action='store_true',
                     help='Auto-detect latest .batch_id.txt in batch/ directory')
    p.add_argument('--wait',    action='store_true',
                   help='Poll until completed (checks every 60s)')
    p.add_argument('--dry-run', action='store_true',
                   help='Parse results but do NOT write to Supabase')
    p.add_argument('--out-dir', default='',
                   help='Directory to save downloaded output JSONL (default: batch/)')
    return p.parse_args()

def resolve_batch_id(args):
    if args.batch_id:
        return args.batch_id
    # --auto: find newest .batch_id.txt
    pattern = os.path.join(_ROOT, 'batch', '*.batch_id.txt')
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if not files:
        print('[ERROR] No .batch_id.txt found in batch/ directory.', file=sys.stderr)
        sys.exit(1)
    path = files[0]
    with open(path, encoding='utf-8') as f:
        bid = f.read().strip()
    print(f'  Auto-detected batch ID: {bid}')
    print(f'  From: {path}')
    return bid

def main():
    args = parse_args()
    batch_id = resolve_batch_id(args)

    out_dir = args.out_dir if args.out_dir else os.path.join(_ROOT, 'batch')
    os.makedirs(out_dir, exist_ok=True)

    print(f'\n{"="*64}')
    print(f'  Sniper Batch Finalize  |  {"DRY-RUN" if args.dry_run else "LIVE"}')
    print(f'  Batch ID: {batch_id}')
    print(f'{"="*64}\n')

    # ── Poll loop ──────────────────────────────────────────────────────────────
    while True:
        batch = client.batches.retrieve(batch_id)
        print_status(batch)

        if batch.status == 'completed':
            break
        if batch.status in ('failed', 'expired', 'cancelled'):
            print(f'\n[ERROR] Batch ended with status: {batch.status}')
            if batch.errors:
                for e in (batch.errors.data or []):
                    print(f'  Error: {e}')
            sys.exit(1)

        if not args.wait:
            remaining = ('validating', 'in_progress', 'finalizing', 'cancelling')
            if batch.status in remaining:
                print(f'\n  Batch not yet completed. Re-run with --wait to poll, or check later.')
                print(f'  python scripts/sniper_batch_finalize.py --batch-id {batch_id}')
            sys.exit(0)

        print('  Waiting 60s...')
        time.sleep(60)
        print()

    # ── Download output file ───────────────────────────────────────────────────
    output_file_id = batch.output_file_id
    if not output_file_id:
        print('[ERROR] Batch completed but output_file_id is missing.', file=sys.stderr)
        sys.exit(1)

    print(f'\nDownloading output file: {output_file_id}')
    content = client.files.content(output_file_id)
    raw = content.read()

    out_file = os.path.join(out_dir, f'{batch_id}_output.jsonl')
    with open(out_file, 'wb') as f:
        f.write(raw)
    print(f'  Saved to: {out_file}')

    # ── Parse and patch ────────────────────────────────────────────────────────
    lines = raw.decode('utf-8').strip().split('\n')
    print(f'  Parsing {len(lines)} result lines...\n')

    ok = fail = skip = 0
    errors_detail = []

    for line in lines:
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            print(f'  [PARSE ERR] {e}', file=sys.stderr)
            fail += 1
            continue

        custom_id = obj.get('custom_id', '?')
        error     = obj.get('error')
        response  = obj.get('response', {})
        body      = response.get('body', {}) if response else {}
        choices   = body.get('choices', []) if body else []

        if error or not choices:
            reason = error or 'empty choices'
            print(f'  [FAIL] id={custom_id}: {reason}', file=sys.stderr)
            errors_detail.append(f'id={custom_id}: {reason}')
            fail += 1
            continue

        msg = choices[0].get('message', {}).get('content', '').strip()
        if not msg:
            print(f'  [SKIP] id={custom_id}: empty content')
            skip += 1
            continue

        preview = msg.replace('\n', ' ')[:80]
        print(f'  [OK]   id={custom_id}  ({len(msg)} chars)  {preview}...')

        if not args.dry_run:
            code = patch_lead(int(custom_id), msg)
            sym  = 'OK' if code in (200, 204) else f'ERR {code}'
            print(f'         → DB: [{sym}]')
            if code in (200, 204):
                ok += 1
            else:
                fail += 1
                errors_detail.append(f'id={custom_id}: DB PATCH returned {code}')
        else:
            print(f'         → DB: [DRY-RUN]')
            ok += 1

    print(f'\n{"="*64}')
    print(f'  DONE')
    print(f'  Patched OK:    {ok}')
    print(f'  Skipped:       {skip}')
    print(f'  Failed:        {fail}')
    if args.dry_run:
        print('  DRY-RUN: nothing written to Supabase.')
    if errors_detail:
        print(f'\n  Error details:')
        for e in errors_detail[:10]:
            print(f'    {e}')
        if len(errors_detail) > 10:
            print(f'    ... and {len(errors_detail)-10} more')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
