#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_batch_submit.py — Upload JSONL to OpenAI and run Batch jobs in chunks.

OpenAI limit: 90 000 enqueued tokens per org (~100 leads/chunk at 780 tok/lead).
This script splits the JSONL automatically and processes chunks sequentially,
waiting for each batch to complete before submitting the next.

Usage:
  python scripts/sniper_batch_submit.py --file batch/berlin_batch_XXXXXX.jsonl
  python scripts/sniper_batch_submit.py --file batch/berlin_batch_XXXXXX.jsonl --chunk-size 80
  python scripts/sniper_batch_submit.py --file batch/berlin_batch_XXXXXX.jsonl --chunk-size 80 --dry-run

Each completed chunk patches Supabase immediately via sniper_batch_finalize logic.
Batch IDs are saved to batch/<name>_chunk_N.batch_id.txt for recovery.
"""

import sys, io, os, json, argparse, configparser, time, urllib.request

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

# ── OpenAI: submit one chunk ──────────────────────────────────────────────────
def submit_chunk(lines, chunk_path):
    chunk_bytes = '\n'.join(lines).encode('utf-8')
    # Write temp chunk file
    with open(chunk_path, 'wb') as f:
        f.write(chunk_bytes)
    with open(chunk_path, 'rb') as f:
        upload = client.files.create(file=f, purpose='batch')
    batch = client.batches.create(
        input_file_id=upload.id,
        endpoint='/v1/chat/completions',
        completion_window='24h',
    )
    return batch.id

# ── OpenAI: poll until done ───────────────────────────────────────────────────
POLL_INTERVAL = 60  # seconds

def wait_for_batch(batch_id, chunk_num, total_chunks):
    print(f'    Polling batch {batch_id}...')
    while True:
        b = client.batches.retrieve(batch_id)
        rc = b.request_counts
        done  = rc.completed if rc else 0
        total = rc.total     if rc else '?'
        fail  = rc.failed    if rc else 0
        print(f'    [{chunk_num}/{total_chunks}] status={b.status}  '
              f'completed={done}/{total}  failed={fail}')
        if b.status == 'completed':
            return b
        if b.status in ('failed', 'expired', 'cancelled'):
            print(f'[ERROR] Batch {batch_id} ended with: {b.status}', file=sys.stderr)
            return None
        time.sleep(POLL_INTERVAL)

# ── Process completed batch output → patch Supabase ──────────────────────────
def finalize_chunk(batch, out_dir, chunk_num, dry_run):
    output_file_id = batch.output_file_id
    if not output_file_id:
        print(f'    [WARN] No output_file_id for batch {batch.id}')
        return 0, 0

    raw = client.files.content(output_file_id).read()
    out_path = os.path.join(out_dir, f'chunk_{chunk_num:03d}_{batch.id}_output.jsonl')
    with open(out_path, 'wb') as f:
        f.write(raw)

    ok = fail = 0
    for line in raw.decode('utf-8').strip().split('\n'):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception:
            fail += 1
            continue

        custom_id = obj.get('custom_id', '?')
        error     = obj.get('error')
        choices   = (obj.get('response', {}) or {}).get('body', {}).get('choices', [])

        if error or not choices:
            print(f'      [FAIL] id={custom_id}: {error or "empty"}', file=sys.stderr)
            fail += 1
            continue

        msg = choices[0].get('message', {}).get('content', '').strip()
        if not msg:
            fail += 1
            continue

        if not dry_run:
            code = patch_lead(int(custom_id), msg)
            if code in (200, 204):
                ok += 1
            else:
                print(f'      [DB ERR] id={custom_id}: HTTP {code}', file=sys.stderr)
                fail += 1
        else:
            ok += 1

    return ok, fail

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Batch Submit — chunked OpenAI batch pipeline')
    p.add_argument('--file',       required=True, help='Input .jsonl from sniper_batch_prepare.py')
    p.add_argument('--chunk-size', type=int, default=80,
                   help='Leads per batch chunk (default: 80, safe under 90k token limit)')
    p.add_argument('--dry-run',    action='store_true', help='Submit batches but skip Supabase writes')
    p.add_argument('--start-chunk',type=int, default=1,
                   help='Resume from chunk N (skip earlier chunks)')
    return p.parse_args()

def main():
    args  = parse_args()
    fpath = args.file if os.path.isabs(args.file) else os.path.join(_ROOT, args.file)

    if not os.path.exists(fpath):
        print(f'[ERROR] File not found: {fpath}', file=sys.stderr)
        sys.exit(1)

    with open(fpath, encoding='utf-8') as f:
        all_lines = [l for l in f.read().strip().split('\n') if l.strip()]

    total_leads = len(all_lines)
    chunk_size  = args.chunk_size
    chunks      = [all_lines[i:i+chunk_size] for i in range(0, total_leads, chunk_size)]
    total_chunks = len(chunks)

    out_dir = os.path.dirname(fpath)
    base    = os.path.splitext(os.path.basename(fpath))[0]

    print(f'\n{"="*64}')
    print(f'  Sniper Batch Submit  |  {"DRY-RUN" if args.dry_run else "LIVE"}')
    print(f'  File:        {os.path.basename(fpath)}')
    print(f'  Total leads: {total_leads}')
    print(f'  Chunk size:  {chunk_size}  →  {total_chunks} chunks')
    print(f'  Start chunk: {args.start_chunk}')
    print(f'{"="*64}\n')

    grand_ok = grand_fail = 0

    for i, chunk_lines in enumerate(chunks, start=1):
        if i < args.start_chunk:
            print(f'  [SKIP] Chunk {i}/{total_chunks} (before --start-chunk)')
            continue

        chunk_path = os.path.join(out_dir, f'{base}_chunk_{i:03d}.jsonl')
        print(f'\n--- Chunk {i}/{total_chunks} ({len(chunk_lines)} leads) ---')

        try:
            batch_id = submit_chunk(chunk_lines, chunk_path)
        except Exception as e:
            print(f'  [ERR] Submit failed: {e}', file=sys.stderr)
            grand_fail += len(chunk_lines)
            continue

        print(f'  Batch ID: {batch_id}')
        id_file = chunk_path.replace('.jsonl', '.batch_id.txt')
        with open(id_file, 'w', encoding='utf-8') as f:
            f.write(batch_id)

        batch = wait_for_batch(batch_id, i, total_chunks)
        if not batch:
            grand_fail += len(chunk_lines)
            continue

        ok, fail = finalize_chunk(batch, out_dir, i, args.dry_run)
        grand_ok   += ok
        grand_fail += fail
        print(f'  Chunk {i} done — OK: {ok}  Fail: {fail}')

    print(f'\n{"="*64}')
    print(f'  ALL CHUNKS COMPLETE')
    print(f'  Patched OK: {grand_ok}')
    print(f'  Failed:     {grand_fail}')
    print(f'  Total:      {grand_ok + grand_fail}')
    if args.dry_run:
        print('  DRY-RUN: nothing written to Supabase.')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
