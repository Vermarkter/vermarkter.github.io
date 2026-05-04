#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_batch_review.py — Download batch results for human review. NO Supabase writes.

Downloads completed OpenAI batch output, saves to data/review_multilang_berlin.json,
and prints a review table: ID | Name | Lang | Message text.

Usage:
  python scripts/sniper_batch_review.py --batch-id batch_xxx
  python scripts/sniper_batch_review.py --auto          # reads latest .batch_id.txt
  python scripts/sniper_batch_review.py --auto --wait   # poll until completed

IMPORTANT: This script NEVER writes to Supabase. Review-only.
"""

import sys, io, os, json, argparse, configparser, time, glob as globmod

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
    print('[ERROR] OPENAI_API_KEY missing.', file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=OPENAI_KEY)

# ── Also load lead metadata from the original JSONL for name/lang lookup ─────
def load_lead_meta(batch_dir):
    """Return dict: custom_id -> {name, lang} from the source JSONL."""
    meta = {}
    pattern = os.path.join(batch_dir, 'berlin_multilang_*.jsonl')
    files = [f for f in globmod.glob(pattern)
             if 'chunk' not in os.path.basename(f) and 'output' not in os.path.basename(f)]
    if not files:
        return meta
    src = sorted(files)[-1]
    with open(src, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                cid = obj.get('custom_id', '')
                msgs = obj.get('body', {}).get('messages', [])
                user_msg = next((m['content'] for m in msgs if m['role'] == 'user'), '')
                sys_msg  = next((m['content'] for m in msgs if m['role'] == 'system'), '')
                name = ''
                for part in user_msg.split('\n'):
                    if part.startswith('Salon:'):
                        name = part.replace('Salon:', '').strip()
                        break
                lang = 'TR' if 'türkischstämmig' in user_msg else ('AR' if 'arabischstämmig' in user_msg else '?')
                meta[cid] = {'name': name, 'lang': lang}
            except Exception:
                pass
    return meta

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Batch Review — download results, NO DB writes')
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--batch-id', help='OpenAI Batch ID')
    grp.add_argument('--auto',     action='store_true', help='Auto-detect latest .batch_id.txt')
    p.add_argument('--wait', action='store_true', help='Poll until completed (every 60s)')
    p.add_argument('--out', default='data/review_multilang_berlin.json',
                   help='Output JSON path (default: data/review_multilang_berlin.json)')
    return p.parse_args()

def resolve_batch_id(args):
    if args.batch_id:
        return args.batch_id
    pattern = os.path.join(_ROOT, 'batch', '*.batch_id.txt')
    files = sorted(globmod.glob(pattern), key=os.path.getmtime, reverse=True)
    if not files:
        print('[ERROR] No .batch_id.txt in batch/.', file=sys.stderr)
        sys.exit(1)
    path = files[0]
    with open(path, encoding='utf-8') as f:
        bid = f.read().strip()
    print(f'  Auto-detected: {bid}  ({os.path.basename(path)})')
    return bid

def main():
    args = parse_args()
    batch_id = resolve_batch_id(args)
    out_path = args.out if os.path.isabs(args.out) else os.path.join(_ROOT, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    batch_dir = os.path.join(_ROOT, 'batch')
    meta = load_lead_meta(batch_dir)

    print(f'\n{"="*64}')
    print(f'  Sniper Batch Review  |  READ-ONLY — no DB writes')
    print(f'  Batch ID: {batch_id}')
    print(f'  Output:   {out_path}')
    print(f'{"="*64}\n')

    # ── Poll until completed ──────────────────────────────────────────────────
    while True:
        batch = client.batches.retrieve(batch_id)
        rc = batch.request_counts
        total = rc.total if rc else '?'
        done  = rc.completed if rc else '?'
        fail  = rc.failed if rc else '?'
        print(f'  Status: {batch.status}  completed={done}/{total}  failed={fail}')

        if batch.status == 'completed':
            break
        if batch.status in ('failed', 'expired', 'cancelled'):
            print(f'[ERROR] Batch ended: {batch.status}', file=sys.stderr)
            sys.exit(1)
        if not args.wait:
            print(f'\n  Not yet completed. Re-run with --wait to poll.')
            print(f'  python scripts/sniper_batch_review.py --batch-id {batch_id} --wait')
            sys.exit(0)
        print('  Waiting 60s...')
        time.sleep(60)
        print()

    # ── Download output ───────────────────────────────────────────────────────
    print(f'\nDownloading results...')
    raw = client.files.content(batch.output_file_id).read()
    raw_path = os.path.join(batch_dir, f'{batch_id}_output.jsonl')
    with open(raw_path, 'wb') as f:
        f.write(raw)
    print(f'  Raw saved: {raw_path}')

    # ── Parse results ─────────────────────────────────────────────────────────
    records = []
    fail = 0
    for line in raw.decode('utf-8').strip().split('\n'):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except Exception:
            fail += 1
            continue

        cid     = obj.get('custom_id', '?')
        error   = obj.get('error')
        choices = (obj.get('response', {}) or {}).get('body', {}).get('choices', [])

        m = meta.get(cid, {})
        name = m.get('name', '?')
        lang = m.get('lang', '?')

        if error or not choices:
            records.append({'id': cid, 'name': name, 'lang': lang,
                            'message': None, 'error': str(error or 'empty')})
            fail += 1
            continue

        msg = choices[0].get('message', {}).get('content', '').strip()
        records.append({'id': cid, 'name': name, 'lang': lang, 'message': msg, 'error': None})

    # ── Save JSON ─────────────────────────────────────────────────────────────
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f'  Review JSON saved: {out_path}  ({len(records)} records)\n')

    # ── Print review table ────────────────────────────────────────────────────
    ok_records = [r for r in records if r['message']]
    print(f'{"="*64}')
    print(f'  REVIEW TABLE — {len(ok_records)} messages for CTO approval')
    print(f'  NOTHING has been written to Supabase.')
    print(f'{"="*64}\n')
    print(f'  {"ID":>6}  {"Lang":4}  {"Name":<35}  Повідомлення')
    print(f'  {"-"*6}  {"-"*4}  {"-"*35}  {"-"*50}')
    for r in records:
        if r['error']:
            print(f'  {r["id"]:>6}  {r["lang"]:4}  {r["name"]:<35}  [ERROR: {r["error"]}]')
        else:
            preview = (r['message'] or '').replace('\n', ' ')
            print(f'  {r["id"]:>6}  {r["lang"]:4}  {r["name"]:<35}  {preview}')

    print(f'\n{"="*64}')
    print(f'  Total:   {len(records)}   OK: {len(ok_records)}   Errors: {fail}')
    print(f'  Файл для Qwen: {out_path}')
    print(f'\n  Для завантаження в Supabase після схвалення CTO:')
    print(f'  python scripts/sniper_batch_approve.py --file "{out_path}"')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
