#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
proxy_image_server.py — Secure Street View image proxy for Vermarkter emails.

Problem:
  street_view_url contains the Google Maps API key (key=AIzaSy...).
  It is safe in the internal CRM but MUST NOT be embedded in HTML emails.

Solution:
  This server proxies the image server-side — the API key never leaves the server.
  Email HTML uses the public proxy URL:
    https://my-salon.eu/proxy-image?lead_id=123

Endpoint:
  GET /proxy-image?lead_id=<integer>
    - Validates lead_id is a plain integer (no path traversal)
    - Looks up street_view_url in Supabase
    - Serves cached JPEG from disk if present
    - On cache miss: fetches from Google (server-side), caches, returns image/jpeg
    - Returns 404 if lead not found or street_view_url is null
    - Returns 502 if Google fetch fails

  GET /health
    - JSON status: uptime, stats counters, cache_dir

Security:
  - lead_id must be a plain non-negative integer (reject anything else)
  - Google Street View URL and API key never sent to client
  - No redirect to Google URL — image bytes are proxied
  - Cache files are named lead_<id>.jpg (no user-controlled path segment)

Caching:
  - Cache dir: /opt/vermarkter/cache/street_view/  (override: env PROXY_CACHE_DIR)
  - Filename: lead_<id>.jpg
  - Hit condition: file exists and size > 0
  - Response headers: Content-Type: image/jpeg, Cache-Control: public, max-age=604800

Logging events:
  cache_hit | cache_miss | google_fetch_ok | google_fetch_error
  lead_not_found | street_view_url_missing | db_error

Usage:
  python scripts/proxy_image_server.py              # port 8083
  python scripts/proxy_image_server.py --port 9001

Nginx config snippet (add to my-salon.eu vhost):
  location /proxy-image {
      proxy_pass         http://127.0.0.1:8083;
      proxy_set_header   Host $host;
      proxy_set_header   X-Real-IP $remote_addr;
      proxy_cache_bypass 1;
  }

Run as daemon on DigitalOcean:
  nohup python3 /opt/vermarkter/scripts/proxy_image_server.py \
        --host 0.0.0.0 --port 8083 >> /opt/vermarkter/logs/proxy_image.log 2>&1 &

Firewall (only needed if not behind nginx):
  ufw allow 8083/tcp
"""

import sys, io, os, json, time, argparse, configparser, urllib.request, urllib.parse
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_LOGS      = os.path.join(_ROOT, 'logs')
_CACHE_DIR = (os.environ.get('PROXY_CACHE_DIR') or '').strip() or '/opt/vermarkter/cache/street_view'
os.makedirs(_LOGS, exist_ok=True)

_LOG_FILE = os.path.join(_LOGS, 'proxy_image.log')
_START    = time.time()

# ── Config ─────────────────────────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _c(s, k, fallback=''):
    try:    return (_cfg.get(s, k) or '').strip() or fallback
    except: return fallback

SB_URL = _c('SUPABASE', 'url').rstrip('/')
SB_KEY = (_c('SUPABASE', 'service_role_key') or _c('SUPABASE', 'anon_key'))

if not SB_URL or not SB_KEY:
    print('[PROXY] ERROR: SUPABASE url/key not configured', file=sys.stderr)
    sys.exit(1)

_SB_H = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}

# ── Stats ──────────────────────────────────────────────────────────────────────
_stats = {
    'total': 0, 'cache_hit': 0, 'cache_miss': 0,
    'google_fetch_ok': 0, 'google_fetch_error': 0,
    'lead_not_found': 0, 'street_view_url_missing': 0, 'db_error': 0,
}


def _log(msg):
    ts   = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    try:
        with open(_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass


# ── Supabase ───────────────────────────────────────────────────────────────────

def _fetch_sv_url(lead_id: int) -> tuple:
    """
    Returns (found: bool, sv_url: str | None).
    found=False means the lead row does not exist (or DB error).
    found=True, sv_url=None means row exists but street_view_url is null.
    """
    url = (f"{SB_URL}/rest/v1/beauty_leads"
           f"?id=eq.{lead_id}&select=street_view_url&limit=1")
    try:
        req = urllib.request.Request(url, headers=_SB_H)
        with urllib.request.urlopen(req, timeout=10) as r:
            rows = json.loads(r.read().decode('utf-8'))
        if not rows:
            return False, None
        sv = (rows[0].get('street_view_url') or '').strip() or None
        return True, sv
    except Exception as ex:
        _log(f'[DB_ERROR] id={lead_id}: {ex}')
        _stats['db_error'] += 1
        return False, None


# ── Cache ──────────────────────────────────────────────────────────────────────

def _cache_path(lead_id: int) -> str:
    return os.path.join(_CACHE_DIR, f'lead_{lead_id}.jpg')


def _cache_get(lead_id: int) -> bytes | None:
    path = _cache_path(lead_id)
    try:
        if os.path.isfile(path) and os.path.getsize(path) > 0:
            with open(path, 'rb') as f:
                return f.read()
    except Exception:
        pass
    return None


def _cache_put(lead_id: int, data: bytes) -> None:
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        with open(_cache_path(lead_id), 'wb') as f:
            f.write(data)
    except Exception as ex:
        _log(f'[CACHE_WRITE_ERR] id={lead_id}: {ex}')


# ── Google fetch ───────────────────────────────────────────────────────────────

def _fetch_google(sv_url: str) -> bytes | None:
    """Download JPEG from Google Street View Static API. Returns bytes or None."""
    try:
        req = urllib.request.Request(sv_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            ctype = r.headers.get('Content-Type', '')
            data  = r.read()
        # Verify JPEG magic bytes: FF D8 FF
        if 'image' in ctype and len(data) > 3 and data[:3] == b'\xff\xd8\xff':
            return data
        _log(f'[GOOGLE_ERR] Non-JPEG response Content-Type={ctype} len={len(data)}')
        return None
    except urllib.error.HTTPError as e:
        _log(f'[GOOGLE_ERR] HTTP {e.code}')
        return None
    except Exception as ex:
        _log(f'[GOOGLE_ERR] {ex}')
        return None


# ── HTTP handler ───────────────────────────────────────────────────────────────

class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
        print(f'[{ts}] {self.address_string()} {fmt % args}', flush=True)

    def _send_image(self, data: bytes):
        self.send_response(200)
        self.send_header('Content-Type', 'image/jpeg')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'public, max-age=604800')
        self.end_headers()
        self.wfile.write(data)

    def _send_err(self, code: int, msg: str):
        body = msg.encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # Health check
        if parsed.path == '/health':
            body = json.dumps({
                'status':    'ok',
                'uptime_s':  int(time.time() - _START),
                'stats':     _stats,
                'cache_dir': _CACHE_DIR,
                'server_time': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if parsed.path != '/proxy-image':
            self._send_err(404, 'not found')
            return

        qs = dict(urllib.parse.parse_qsl(parsed.query))

        # Security: lead_id must be a plain non-negative integer
        raw_id = qs.get('lead_id', '')
        if not raw_id.isdigit() or int(raw_id) == 0:
            self._send_err(400, 'lead_id must be a positive integer')
            return

        lead_id = int(raw_id)
        _stats['total'] += 1

        # ── 1. Cache hit ───────────────────────────────────────────────────────
        cached = _cache_get(lead_id)
        if cached:
            _stats['cache_hit'] += 1
            _log(f'[CACHE_HIT] id={lead_id} size={len(cached)}')
            self._send_image(cached)
            return

        _stats['cache_miss'] += 1

        # ── 2. Supabase lookup ─────────────────────────────────────────────────
        found, sv_url = _fetch_sv_url(lead_id)

        if not found:
            _stats['lead_not_found'] += 1
            _log(f'[LEAD_NOT_FOUND] id={lead_id}')
            self._send_err(404, 'lead not found')
            return

        if not sv_url:
            _stats['street_view_url_missing'] += 1
            _log(f'[SV_URL_MISSING] id={lead_id}')
            self._send_err(404, 'no street_view_url for this lead')
            return

        # ── 3. Google fetch (API key stays server-side) ────────────────────────
        data = _fetch_google(sv_url)

        if data:
            _stats['google_fetch_ok'] += 1
            _cache_put(lead_id, data)
            _log(f'[GOOGLE_FETCH_OK] id={lead_id} size={len(data)}')
            self._send_image(data)
        else:
            _stats['google_fetch_error'] += 1
            _log(f'[GOOGLE_FETCH_ERROR] id={lead_id}')
            self._send_err(502, 'upstream image unavailable')


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description='Street View image proxy for Vermarkter emails')
    p.add_argument('--host', default='0.0.0.0', help='Bind host (default: 0.0.0.0)')
    p.add_argument('--port', type=int, default=8083, help='Port (default: 8083)')
    args = p.parse_args()

    _log(f'[START] Image proxy starting on {args.host}:{args.port}')
    _log(f'[START] Supabase: {SB_URL}')
    _log(f'[START] Cache dir: {_CACHE_DIR}')
    _log(f'[START] Log: {_LOG_FILE}')
    _log(f'[START] Endpoint: GET http://HOST:{args.port}/proxy-image?lead_id=<id>')

    server = HTTPServer((args.host, args.port), ProxyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log('[STOP] Server stopped.')


if __name__ == '__main__':
    main()
