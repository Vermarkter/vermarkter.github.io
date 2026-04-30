#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_watcher.py — Poll OpenAI Batch API until all pending batches complete.

Reads every *.batch_id.txt from batch/ directory, polls status every N seconds,
and when status → 'completed' runs sniper_batch_finalize to write results to
Supabase. Logs to logs/batch_watcher.log.

Usage:
  python3 scripts/batch_watcher.py                    # watch all pending batches
  python3 scripts/batch_watcher.py --file batch/X.batch_id.txt  # single batch
  python3 scripts/batch_watcher.py --interval 60      # poll every 60s (default: 120)
  python3 scripts/batch_watcher.py --once             # one check, no loop
  python3 scripts/batch_watcher.py --notify telegram  # send Telegram on complete

Terminal statuses: completed, failed, expired, cancelled
"""

import sys, io, os, json, time, argparse, configparser, glob, urllib.request
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    from openai import OpenAI
except ImportError:
    print('[ERROR] openai not installed.  pip install openai', file=sys.stderr)
    sys.exit(1)

_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BATCH = os.path.join(_ROOT, 'batch')
_LOGS  = os.path.join(_ROOT, 'logs')
os.makedirs(_LOGS, exist_ok=True)

LOG_FILE = os.path.join(_LOGS, 'batch_watcher.log')

# ── Config ─────────────────────────────────────────────────────────────────────
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

TG_BOT_TOKEN = (
    _env.get('TELEGRAM_BOT_TOKEN')
    or os.environ.get('TELEGRAM_BOT_TOKEN', '')
    or _cfg.get('TELEGRAM', 'bot_token', fallback='')
).strip()

TG_CHAT_ID = (
    _env.get('TELEGRAM_CHAT_ID')
    or os.environ.get('TELEGRAM_CHAT_ID', '')
    or _cfg.get('TELEGRAM', 'chat_id', fallback='')
).strip()

if not OPENAI_KEY or not OPENAI_KEY.startswith('sk-') or 'PASTE' in OPENAI_KEY:
    print('[ERROR] OPENAI_API_KEY missing.  Set in .env: OPENAI_API_KEY=sk-proj-...', file=sys.stderr)
    sys.exit(1)

client = OpenAI(api_key=OPENAI_KEY)

TERMINAL = {'completed', 'failed', 'expired', 'cancelled'}
STATUS_EMOJI = {
    'validating':  '🔍',
    'in_progress': '⏳',
    'finalizing':  '🔄',
    'completed':   '✅',
    'failed':      '❌',
    'expired':     '⏰',
    'cancelled':   '🚫',
}

# ── Logger ─────────────────────────────────────────────────────────────────────
def log(msg, level='INFO'):
    ts  = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    line = f'[{ts}] [{level}] {msg}'
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

# ── Telegram notify ────────────────────────────────────────────────────────────
def tg_notify(text):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        log('Telegram not configured — skip notify', 'WARN')
        return
    url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
    payload = json.dumps({'chat_id': TG_CHAT_ID, 'text': text, 'parse_mode': 'HTML'}).encode()
    req = urllib.request.Request(url, data=payload,
                                  headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            log(f'Telegram notified: {r.status}')
    except Exception as e:
        log(f'Telegram error: {e}', 'WARN')

# ── Batch helpers ──────────────────────────────────────────────────────────────
def find_batch_id_files(single=None):
    if single:
        return [single] if os.path.exists(single) else []
    pattern = os.path.join(_BATCH, '*.batch_id.txt')
    return sorted(glob.glob(pattern))


def read_batch_id(path):
    try:
        with open(path, encoding='utf-8') as f:
            return f.read().strip()
    except Exception:
        return None


def mark_done(path):
    """Rename .batch_id.txt → .batch_id.done to exclude from future scans."""
    done_path = path.replace('.batch_id.txt', '.batch_id.done')
    try:
        os.rename(path, done_path)
        log(f'Archived: {os.path.basename(done_path)}')
    except Exception as e:
        log(f'Could not archive {path}: {e}', 'WARN')


def poll_batch(batch_id):
    """Return batch object or None on error."""
    try:
        return client.batches.retrieve(batch_id)
    except Exception as e:
        log(f'Error polling {batch_id}: {e}', 'ERROR')
        return None


def run_finalize(batch_id, output_file_id, id_file_path):
    """Download output JSONL and write results to Supabase via sniper_batch_finalize."""
    log(f'Downloading output for batch {batch_id} (file_id={output_file_id})')
    try:
        content = client.files.content(output_file_id)
        # Save output JSONL next to batch_id file
        out_path = id_file_path.replace('.batch_id.txt', '_output.jsonl')
        with open(out_path, 'wb') as f:
            f.write(content.read())
        log(f'Output saved: {os.path.basename(out_path)}')
    except Exception as e:
        log(f'Failed to download output: {e}', 'ERROR')
        return False

    # Run finalize script
    finalize_script = os.path.join(_ROOT, 'scripts', 'sniper_batch_finalize.py')
    if os.path.exists(finalize_script):
        import subprocess
        res = subprocess.run(
            [sys.executable, finalize_script, '--file', out_path],
            capture_output=True, text=True, encoding='utf-8'
        )
        if res.returncode == 0:
            log(f'Finalize OK:\n{res.stdout[-500:]}')
        else:
            log(f'Finalize ERROR:\n{res.stderr[-500:]}', 'ERROR')
        return res.returncode == 0
    else:
        log(f'sniper_batch_finalize.py not found — output saved, run manually', 'WARN')
        return True


# ── Core watch loop ────────────────────────────────────────────────────────────
def watch(args):
    interval  = args.interval
    once      = args.once
    single    = args.file
    notify    = args.notify

    log(f'Batch Watcher started | interval={interval}s | once={once}')

    while True:
        id_files = find_batch_id_files(single)

        if not id_files:
            log('No pending .batch_id.txt files found — nothing to watch.')
            break

        all_terminal = True

        for id_file in id_files:
            batch_id = read_batch_id(id_file)
            if not batch_id:
                log(f'Empty or unreadable: {id_file}', 'WARN')
                continue

            batch = poll_batch(batch_id)
            if batch is None:
                all_terminal = False
                continue

            status = batch.status
            emoji  = STATUS_EMOJI.get(status, '?')
            req_counts = batch.request_counts
            total   = getattr(req_counts, 'total',     '?')
            done    = getattr(req_counts, 'completed', '?')
            failed  = getattr(req_counts, 'failed',    0)

            log(f'{emoji} {os.path.basename(id_file)} | status={status} | {done}/{total} done, {failed} failed')

            if status == 'completed':
                output_file_id = batch.output_file_id
                log(f'COMPLETED: {batch_id} | output_file_id={output_file_id}')

                success = run_finalize(batch_id, output_file_id, id_file)

                msg = (f'✅ <b>Batch завершено!</b>\n'
                       f'ID: <code>{batch_id}</code>\n'
                       f'Запитів: {done}/{total} (failed: {failed})\n'
                       f'Finalize: {"OK ✓" if success else "ERROR ✗"}')
                if notify == 'telegram':
                    tg_notify(msg)
                else:
                    log(f'Notify (log-only):\n{msg}')

                mark_done(id_file)

            elif status in ('failed', 'expired', 'cancelled'):
                log(f'TERMINAL ERROR: {batch_id} → {status}', 'ERROR')
                err_file = batch.error_file_id
                msg = (f'{emoji} <b>Batch {status.upper()}</b>\n'
                       f'ID: <code>{batch_id}</code>\n'
                       f'Errors file_id: {err_file}')
                if notify == 'telegram':
                    tg_notify(msg)
                else:
                    log(f'Notify (log-only):\n{msg}')
                mark_done(id_file)

            else:
                # still running
                all_terminal = False

        if once or all_terminal:
            log('All batches in terminal state or --once flag set. Exiting.')
            break

        log(f'Sleeping {interval}s before next poll...')
        time.sleep(interval)


def main():
    p = argparse.ArgumentParser(description='batch_watcher — poll OpenAI Batch API')
    p.add_argument('--file',     default=None,  help='Single .batch_id.txt to watch')
    p.add_argument('--interval', type=int, default=120, help='Poll interval in seconds (default: 120)')
    p.add_argument('--once',     action='store_true',   help='Check once and exit')
    p.add_argument('--notify',   default='log',
                   choices=['log', 'telegram'], help='Notification channel (default: log)')
    args = p.parse_args()
    watch(args)


if __name__ == '__main__':
    main()
