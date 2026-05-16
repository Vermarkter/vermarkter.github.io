#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brevo_webhook_server.py — Lightweight HTTP server for Brevo transactional email webhooks.

Handles Brevo event notifications and patches Supabase beauty_leads accordingly.

Supported events:
  delivered      → log only (lead is already EMAIL SENT)
  hard_bounce    → email=null, last_error='Hard Bounce: {reason}',
                   status='wa_ready' if phone else 'funnel_ready'
  soft_bounce    → last_error='Soft Bounce: {reason}' (email kept)
  blocked        → last_error='Blocked: {reason}' (email kept)
  spam           → email=null, last_error='Spam complaint',
                   status='funnel_ready'

Security:
  Requests must include ?token=WEBHOOK_SECRET (configured in config.ini [BREVO] webhook_secret).
  If webhook_secret is not set, token check is skipped (dev mode).

Usage:
  python scripts/brevo_webhook_server.py              # port 8082
  python scripts/brevo_webhook_server.py --port 9000
  python scripts/brevo_webhook_server.py --host 0.0.0.0 --port 8082

Configure Brevo webhook URL:
  https://YOUR_DO_IP:8082/brevo/webhook?token=SECRET

Run as daemon on DigitalOcean:
  nohup python3 /opt/vermarkter/scripts/brevo_webhook_server.py \
        --host 0.0.0.0 --port 8082 >> /opt/vermarkter/logs/brevo_webhook_server.log 2>&1 &

Firewall:
  ufw allow 8082/tcp
"""

import sys, io, os, json, time, argparse, configparser, urllib.request, urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGS  = os.path.join(_ROOT, 'logs')
os.makedirs(_LOGS, exist_ok=True)

_LOG_FILE = os.path.join(_LOGS, 'brevo_webhook.log')
_START    = time.time()

# ── Config ─────────────────────────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _c(s, k, fallback=''):
    try:    return (_cfg.get(s, k) or '').strip() or fallback
    except: return fallback

SB_URL         = _c('SUPABASE', 'url').rstrip('/')
SB_KEY         = (_c('SUPABASE', 'service_role_key')
                  or _c('SUPABASE', 'anon_key'))
WEBHOOK_SECRET = _c('BREVO', 'webhook_secret', '')   # empty = no auth check (dev)

if not SB_URL or not SB_KEY:
    print('[WEBHOOK] ERROR: SUPABASE url/key not configured', file=sys.stderr)
    sys.exit(1)

_SB_R = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
_SB_W = {**_SB_R, 'Content-Type': 'application/json; charset=utf-8', 'Prefer': 'return=minimal'}

# ── Counters ───────────────────────────────────────────────────────────────────
_stats = {
    'delivered': 0, 'hard_bounce': 0, 'soft_bounce': 0,
    'blocked': 0, 'spam': 0, 'other': 0, 'errors': 0,
    'total_events': 0,
}


def _log(msg):
    ts  = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    try:
        with open(_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


# ── Supabase helpers ───────────────────────────────────────────────────────────

def _sb_get_lead_by_email(email: str) -> dict | None:
    """Find lead by email. Returns first match or None."""
    enc = urllib.parse.quote(email, safe='')
    url = f"{SB_URL}/rest/v1/beauty_leads?email=eq.{enc}&select=id,phone,status&limit=1"
    try:
        req = urllib.request.Request(url, headers=_SB_R)
        with urllib.request.urlopen(req, timeout=10) as r:
            rows = json.loads(r.read().decode('utf-8'))
            return rows[0] if rows else None
    except Exception as ex:
        _log(f'[ERROR] sb_get_lead_by_email({email}): {ex}')
        return None


def _sb_patch(lead_id: int, payload: dict) -> bool:
    url  = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req  = urllib.request.Request(url, data=body, headers=_SB_W, method='PATCH')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
                return True
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2 ** attempt)
            else:
                _log(f'[ERROR] sb_patch(id={lead_id}): HTTP {e.code}')
                return False
        except Exception as ex:
            _log(f'[ERROR] sb_patch(id={lead_id}): {ex}')
            if attempt < 2:
                time.sleep(1)
    return False


# ── Event processors ───────────────────────────────────────────────────────────

def _handle_delivered(ev: dict):
    """delivered — log only, no DB change."""
    email   = ev.get('email', '?')
    subject = ev.get('subject', '')
    _log(f'[DELIVERED] {email} | subject={subject[:60]}')
    _stats['delivered'] += 1


def _handle_hard_bounce(ev: dict):
    """
    hard_bounce:
      - email = null
      - last_error = 'Hard Bounce: {reason}'
      - status = 'wa_ready' if phone else 'funnel_ready'
    """
    email  = ev.get('email', '')
    reason = ev.get('reason', 'no reason given')
    _log(f'[HARD_BOUNCE] {email} | reason={reason}')
    _stats['hard_bounce'] += 1

    if not email:
        _log('[HARD_BOUNCE] No email in event — skipping')
        return

    lead = _sb_get_lead_by_email(email)
    if not lead:
        _log(f'[HARD_BOUNCE] Lead not found for email={email}')
        return

    has_phone   = bool((lead.get('phone') or '').strip())
    new_status  = 'wa_ready' if has_phone else 'funnel_ready'
    patch = {
        'email':      None,
        'last_error': f'Hard Bounce: {reason}',
        'status':     new_status,
    }
    ok = _sb_patch(lead['id'], patch)
    _log(f'[HARD_BOUNCE] id={lead["id"]} patched: email=null status={new_status} ok={ok}')


def _handle_soft_bounce(ev: dict):
    """
    soft_bounce:
      - last_error = 'Soft Bounce: {reason}'
      - email and status kept (retry possible)
    """
    email  = ev.get('email', '')
    reason = ev.get('reason', 'no reason given')
    _log(f'[SOFT_BOUNCE] {email} | reason={reason}')
    _stats['soft_bounce'] += 1

    if not email:
        return

    lead = _sb_get_lead_by_email(email)
    if not lead:
        _log(f'[SOFT_BOUNCE] Lead not found for email={email}')
        return

    ok = _sb_patch(lead['id'], {'last_error': f'Soft Bounce: {reason}'})
    _log(f'[SOFT_BOUNCE] id={lead["id"]} last_error set ok={ok}')


def _handle_blocked(ev: dict):
    """
    blocked:
      - last_error = 'Blocked: {reason}'
      - email and status kept
    """
    email  = ev.get('email', '')
    reason = ev.get('reason', 'no reason given')
    _log(f'[BLOCKED] {email} | reason={reason}')
    _stats['blocked'] += 1

    if not email:
        return

    lead = _sb_get_lead_by_email(email)
    if not lead:
        _log(f'[BLOCKED] Lead not found for email={email}')
        return

    ok = _sb_patch(lead['id'], {'last_error': f'Blocked: {reason}'})
    _log(f'[BLOCKED] id={lead["id"]} last_error set ok={ok}')


def _handle_spam(ev: dict):
    """
    spam:
      - email = null (must never email again)
      - last_error = 'Spam complaint'
      - status = 'funnel_ready'
    """
    email = ev.get('email', '')
    _log(f'[SPAM] {email}')
    _stats['spam'] += 1

    if not email:
        return

    lead = _sb_get_lead_by_email(email)
    if not lead:
        _log(f'[SPAM] Lead not found for email={email}')
        return

    ok = _sb_patch(lead['id'], {
        'email':      None,
        'last_error': 'Spam complaint',
        'status':     'funnel_ready',
    })
    _log(f'[SPAM] id={lead["id"]} email=null status=funnel_ready ok={ok}')


_HANDLERS = {
    'delivered':   _handle_delivered,
    'hard_bounce': _handle_hard_bounce,
    'hardBounce':  _handle_hard_bounce,   # Brevo sends both spellings
    'soft_bounce': _handle_soft_bounce,
    'softBounce':  _handle_soft_bounce,
    'blocked':     _handle_blocked,
    'spam':        _handle_spam,
}


def process_events(events: list):
    for ev in events:
        _stats['total_events'] += 1
        event_type = ev.get('event', '')
        handler    = _HANDLERS.get(event_type)
        if handler:
            try:
                handler(ev)
            except Exception as ex:
                _stats['errors'] += 1
                _log(f'[ERROR] handler for {event_type}: {ex}')
        else:
            _stats['other'] += 1
            _log(f'[EVENT] unhandled type={event_type!r} email={ev.get("email","?")}')


# ── HTTP Handler ───────────────────────────────────────────────────────────────

class WebhookHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
        print(f'[{ts}] {self.address_string()} {fmt % args}', flush=True)

    def _parse_qs(self) -> dict:
        parsed = urllib.parse.urlparse(self.path)
        return dict(urllib.parse.parse_qsl(parsed.query))

    def _send(self, code: int, body: bytes, ct: str = 'application/json'):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self, qs: dict) -> bool:
        if not WEBHOOK_SECRET:
            return True  # dev mode — no auth
        return qs.get('token', '') == WEBHOOK_SECRET

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/health':
            body = json.dumps({
                'status':       'ok',
                'uptime_s':     int(time.time() - _START),
                'stats':        _stats,
                'server_time':  datetime.now(timezone.utc).isoformat(timespec='seconds'),
            }, ensure_ascii=False).encode('utf-8')
            self._send(200, body)
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        path = self.path.split('?')[0]
        qs   = self._parse_qs()

        if path != '/brevo/webhook':
            self._send(404, b'{"error":"not found"}')
            return

        if not self._authorized(qs):
            _log(f'[AUTH] Unauthorized request from {self.address_string()}')
            self._send(401, b'{"error":"unauthorized"}')
            return

        # Read body
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw    = self.rfile.read(length)
            data   = json.loads(raw.decode('utf-8'))
        except Exception as ex:
            _log(f'[ERROR] Bad request body: {ex}')
            self._send(400, b'{"error":"invalid json"}')
            return

        # Brevo sends either a list or a single object
        events = data if isinstance(data, list) else [data]
        _log(f'[WEBHOOK] {len(events)} event(s) from {self.address_string()}')

        process_events(events)

        self._send(200, b'{"ok":true}')


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='Brevo webhook server for Vermarkter')
    p.add_argument('--host', default='0.0.0.0', help='Bind host (default: 0.0.0.0)')
    p.add_argument('--port', type=int, default=8082, help='Port (default: 8082)')
    args = p.parse_args()

    _log(f'[START] Brevo webhook server starting on {args.host}:{args.port}')
    _log(f'[START] Supabase: {SB_URL}')
    _log(f'[START] Auth: {"token required" if WEBHOOK_SECRET else "NO AUTH (dev mode)"}')
    _log(f'[START] Log: {_LOG_FILE}')
    _log(f'[START] Endpoint: POST http://HOST:{args.port}/brevo/webhook'
         + (f'?token=SECRET' if WEBHOOK_SECRET else ''))

    server = HTTPServer((args.host, args.port), WebhookHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log('[STOP] Server stopped.')


if __name__ == '__main__':
    main()
