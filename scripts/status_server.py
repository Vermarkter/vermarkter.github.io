#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
status_server.py — Lightweight HTTP server for Vermarkter live dashboard.

Serves:
  GET /          → status.html  (the Luxury dashboard page)
  GET /api/status → JSON with live metrics
  GET /favicon.svg → proxied from GitHub Pages

Metrics collected on every /api/status call:
  • Supabase: total leads, Berlin READY TO SEND, today EMAIL SENT
  • OpenAI Batch: pending batches count, in_progress count, last batch status
  • Brevo: emails sent today (via Brevo account stats API)
  • Disk usage
  • Uptime

Usage:
  python3 scripts/status_server.py              # default port 8080
  python3 scripts/status_server.py --port 9090
  python3 scripts/status_server.py --host 0.0.0.0 --port 8080

Run as daemon:
  nohup python3 /opt/vermarkter/scripts/status_server.py \
        --host 0.0.0.0 --port 8080 >> /opt/vermarkter/logs/status_server.log 2>&1 &

Firewall (DigitalOcean):
  ufw allow 8080/tcp
"""

import sys, io, os, json, time, glob, shutil, configparser, urllib.request, urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from threading import Lock

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BATCH = os.path.join(_ROOT, 'batch')
_LOGS  = os.path.join(_ROOT, 'logs')
_START = time.time()

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

try:
    SB_URL = _cfg['SUPABASE']['url'].strip()
    _svc   = _cfg['SUPABASE']['service_role_key'].strip()
    SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
             else _cfg['SUPABASE']['anon_key'].strip()
except (KeyError, configparser.NoSectionError):
    SB_URL = ''
    SB_KEY = ''

OPENAI_KEY = (
    _env.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY', '')
    or _cfg.get('OPENAI', 'api_key', fallback='')
).strip()

BREVO_KEY = (
    _env.get('BREVO_API_KEY') or os.environ.get('BREVO_API_KEY', '')
    or _cfg.get('BREVO', 'api_key', fallback='')
).strip()

SB_HDRS = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Prefer': 'count=exact',
    'Range-Unit': 'items',
    'Range': '0-0',
}

# ── Metric collectors ──────────────────────────────────────────────────────────
def _sb_count(params):
    """Return int count or -1 on error."""
    if not SB_URL or not SB_KEY:
        return -1
    url = f"{SB_URL}/rest/v1/beauty_leads?select=id{params}"
    try:
        req = urllib.request.Request(url, headers=SB_HDRS)
        with urllib.request.urlopen(req, timeout=8) as r:
            cr    = r.headers.get('Content-Range', '*/0')
            total = cr.split('/')[-1]
            return int(total) if total.isdigit() else -1
    except Exception:
        return -1


def collect_supabase():
    today_start = datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00+00:00')
    ok = _sb_count('') >= 0

    return {
        'online':        ok,
        'total_leads':   _sb_count(''),
        'berlin_ready':  _sb_count('&city=eq.Berlin&status=eq.READY TO SEND'),
        'email_sent_total': _sb_count('&status=eq.EMAIL SENT'),
        'wa_sent_total': _sb_count('&status=eq.sent'),
        'total_done':    _sb_count('&status=in.(sent,EMAIL SENT,replied,booked,CALLED)'),
    }


def collect_batches():
    """Read all *.batch_id.txt and poll OpenAI for status."""
    id_files = sorted(glob.glob(os.path.join(_BATCH, '*.batch_id.txt')))
    if not id_files:
        return {'pending': 0, 'in_progress': 0, 'completed_today': 0,
                'batches': [], 'openai_ok': None}

    if not OPENAI_KEY or not OPENAI_KEY.startswith('sk-'):
        return {'pending': len(id_files), 'in_progress': 0,
                'completed_today': 0, 'batches': [],
                'openai_ok': False, 'error': 'no API key'}

    batches   = []
    pending   = in_prog = comp_today = 0
    today     = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    openai_ok = True

    for path in id_files[:20]:   # cap at 20 to avoid slow startup
        try:
            with open(path, encoding='utf-8') as f:
                batch_id = f.read().strip()
        except Exception:
            continue

        url = f'https://api.openai.com/v1/batches/{batch_id}'
        req = urllib.request.Request(
            url,
            headers={'Authorization': f'Bearer {OPENAI_KEY}',
                     'Content-Type': 'application/json'}
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                b = json.loads(r.read().decode('utf-8'))
        except urllib.request.HTTPError as e:
            openai_ok = False
            b = {'id': batch_id, 'status': f'http_{e.code}', 'request_counts': {}}
        except Exception as e:
            openai_ok = False
            b = {'id': batch_id, 'status': 'error', 'request_counts': {}}

        status = b.get('status', '?')
        rc     = b.get('request_counts', {})
        total  = rc.get('total', 0) or 0
        done   = rc.get('completed', 0) or 0
        failed = rc.get('failed', 0) or 0

        if status in ('validating', 'in_progress', 'finalizing'):
            in_prog += 1
        if status not in ('completed', 'failed', 'expired', 'cancelled'):
            pending += 1

        batches.append({
            'file':    os.path.basename(path),
            'id':      batch_id[:24] + '…',
            'status':  status,
            'total':   total,
            'done':    done,
            'failed':  failed,
            'pct':     round(done / total * 100) if total else 0,
        })

    return {
        'pending':         pending,
        'in_progress':     in_prog,
        'completed_today': comp_today,
        'total_files':     len(id_files),
        'batches':         batches[:8],   # top 8 for display
        'openai_ok':       openai_ok,
    }


def collect_brevo():
    if not BREVO_KEY or not BREVO_KEY.startswith('xkeysib-'):
        return {'online': False, 'sent_today': -1, 'daily_limit': 300}

    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    url   = f'https://api.brevo.com/v3/smtp/statistics/events?days=1&limit=1'
    req   = urllib.request.Request(
        url,
        headers={'api-key': BREVO_KEY, 'Accept': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode('utf-8'))
            # events endpoint returns list; use aggregated stats instead
    except Exception:
        pass

    # Use aggregated stats endpoint — more reliable
    url2 = 'https://api.brevo.com/v3/smtp/statistics/aggregatedReport?days=1'
    req2 = urllib.request.Request(
        url2,
        headers={'api-key': BREVO_KEY, 'Accept': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req2, timeout=8) as r:
            agg = json.loads(r.read().decode('utf-8'))
            sent = agg.get('delivered', 0) + agg.get('softBounces', 0) + agg.get('hardBounces', 0)
            return {
                'online':      True,
                'sent_today':  agg.get('requests', sent),
                'delivered':   agg.get('delivered', 0),
                'bounced':     agg.get('softBounces', 0) + agg.get('hardBounces', 0),
                'daily_limit': int(_cfg.get('BREVO', 'daily_limit', fallback='300')),
            }
    except Exception as e:
        # Fallback: account info only (verifies connectivity)
        try:
            acc_req = urllib.request.Request(
                'https://api.brevo.com/v3/account',
                headers={'api-key': BREVO_KEY, 'Accept': 'application/json'}
            )
            with urllib.request.urlopen(acc_req, timeout=8) as r:
                return {'online': True, 'sent_today': -1,
                        'daily_limit': 300, 'note': 'stats unavailable'}
        except Exception:
            return {'online': False, 'sent_today': -1, 'daily_limit': 300}


def collect_disk():
    results = []
    for path in ['/', '/opt/vermarkter', _ROOT]:
        if os.path.exists(path):
            try:
                u = shutil.disk_usage(path)
                entry = {
                    'path':     path,
                    'free_gb':  round(u.free  / 1e9, 1),
                    'used_gb':  round(u.used  / 1e9, 1),
                    'total_gb': round(u.total / 1e9, 1),
                    'used_pct': round(u.used / u.total * 100, 1),
                }
                # Avoid duplicates (same device mounted at multiple paths)
                if not any(d['total_gb'] == entry['total_gb'] and
                           d['used_gb']  == entry['used_gb']  for d in results):
                    results.append(entry)
            except Exception:
                pass
    return results


def collect_logs():
    entries = {}
    for name in ['sniper_engine.log', 'mass_email.log', 'batch_watcher.log',
                 'lead_harvester.log', 'verify_sites.log']:
        p = os.path.join(_LOGS, name)
        if os.path.exists(p):
            sz = os.path.getsize(p)
            try:
                with open(p, encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                last = lines[-1].strip() if lines else ''
            except Exception:
                last = ''
            entries[name] = {'kb': round(sz / 1024, 1), 'last': last[-100:]}
    return entries


# ── Cached metrics (refresh every 60 s) ───────────────────────────────────────
_cache      = {}
_cache_lock = Lock()
_cache_ts   = 0
CACHE_TTL   = 60   # seconds


def get_metrics():
    global _cache, _cache_ts
    now = time.time()
    with _cache_lock:
        if now - _cache_ts > CACHE_TTL:
            _cache = {
                'supabase': collect_supabase(),
                'batches':  collect_batches(),
                'brevo':    collect_brevo(),
                'disk':     collect_disk(),
                'logs':     collect_logs(),
                'uptime_s': int(now - _START),
                'server_time': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            }
            _cache_ts = now
    return _cache


# ── HTML page (self-contained, loaded once) ────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="uk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>Vermarkter — Server Status</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#030303;--surf:rgba(255,255,255,.042);--border:rgba(255,255,255,.08);
  --pink:#ec4899;--purple:#8b5cf6;--cyan:#06b6d4;
  --green:#22c55e;--amber:#f59e0b;--red:#ef4444;--blue:#3b82f6;
  --text:#f1f5f9;--muted:rgba(241,245,249,.42);
  --grad:linear-gradient(135deg,#ec4899,#8b5cf6);
  --grad-g:linear-gradient(135deg,#22c55e,#16a34a);
  --grad-c:linear-gradient(135deg,#06b6d4,#6366f1);
  --grad-a:linear-gradient(135deg,#f59e0b,#ef4444);
}
html,body{min-height:100vh;background:var(--bg);color:var(--text);
  font-family:'Inter',system-ui,sans-serif;overflow-x:hidden}
body::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 55% 35% at 15% 15%,rgba(139,92,246,.13) 0%,transparent 60%),
    radial-gradient(ellipse 45% 30% at 85% 80%,rgba(236,72,153,.10) 0%,transparent 60%),
    radial-gradient(ellipse 35% 25% at 65%  5%,rgba(6,182,212,.07)  0%,transparent 55%)}
.wrap{position:relative;z-index:1;max-width:960px;margin:0 auto;padding:2rem 1rem 4rem}

/* Header */
.hdr{text-align:center;margin-bottom:2rem}
.logo-row{display:flex;align-items:center;justify-content:center;gap:.55rem;margin-bottom:.55rem}
.dot-live{width:9px;height:9px;border-radius:50%;background:var(--green);
  box-shadow:0 0 9px var(--green);animation:pulse 2s ease-in-out infinite;flex-shrink:0}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.55;transform:scale(.82)}}
.logo-txt{font-size:.75rem;font-weight:700;letter-spacing:1.6px;
  text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(1.7rem,4vw,2.8rem);font-weight:900;line-height:1.08;margin-bottom:.3rem}
.gt{background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.ts{font-size:.72rem;color:rgba(241,245,249,.28);margin-top:.4rem;letter-spacing:.2px}

/* Glass card */
.card{background:var(--surf);border:1px solid var(--border);border-radius:18px;
  backdrop-filter:blur(20px) saturate(160%);-webkit-backdrop-filter:blur(20px) saturate(160%);
  padding:1.4rem 1.6rem;margin-bottom:.9rem;position:relative;overflow:hidden;
  transition:border-color .2s}
.card:hover{border-color:rgba(255,255,255,.13)}
.card::before{content:'';position:absolute;inset:0;border-radius:inherit;pointer-events:none;
  background:linear-gradient(135deg,rgba(255,255,255,.028) 0%,transparent 55%)}
.card-title{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.9px;
  color:var(--muted);margin-bottom:1rem;display:flex;align-items:center;gap:.45rem}
.dot-s{width:6px;height:6px;border-radius:50%;flex-shrink:0}
.dot-ok{background:var(--green);box-shadow:0 0 5px var(--green)}
.dot-warn{background:var(--amber);box-shadow:0 0 5px var(--amber)}
.dot-err{background:var(--red);box-shadow:0 0 5px var(--red)}
.dot-off{background:var(--muted)}

/* Stat grid */
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:.8rem;margin-bottom:.9rem}
.sc{background:var(--surf);border:1px solid var(--border);border-radius:14px;
  padding:1.1rem 1rem;text-align:center;position:relative;overflow:hidden;
  transition:transform .18s,border-color .18s}
.sc:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.13)}
.sc::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;opacity:.75;border-radius:0 0 14px 14px}
.sc.pink::after{background:var(--grad)}
.sc.cyan::after{background:var(--grad-c)}
.sc.green::after{background:var(--grad-g)}
.sc.amber::after{background:var(--grad-a)}
.sc.blue::after{background:linear-gradient(135deg,#3b82f6,#6366f1)}
.sn{font-size:clamp(1.9rem,5vw,3rem);font-weight:900;line-height:1;margin-bottom:.2rem;
  background:var(--grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sc.cyan  .sn{background:var(--grad-c);-webkit-background-clip:text;background-clip:text}
.sc.green .sn{background:var(--grad-g);-webkit-background-clip:text;background-clip:text}
.sc.amber .sn{background:var(--grad-a);-webkit-background-clip:text;background-clip:text}
.sc.blue  .sn{background:linear-gradient(135deg,#3b82f6,#8b5cf6);-webkit-background-clip:text;background-clip:text}
.sl{font-size:.63rem;text-transform:uppercase;letter-spacing:.7px;color:var(--muted);font-weight:600}
.ss{font-size:.65rem;color:rgba(241,245,249,.28);margin-top:.18rem}

/* Progress bar */
.prog-wrap{margin:.6rem 0}
.prog-row{display:flex;justify-content:space-between;font-size:.7rem;color:var(--muted);margin-bottom:.28rem}
.prog{background:rgba(255,255,255,.07);border-radius:999px;height:6px;overflow:hidden}
.pf{height:100%;border-radius:999px;background:var(--grad);transition:width .9s ease}

/* Batch table */
.tbl{width:100%;border-collapse:collapse;font-size:.78rem}
.tbl th{text-align:left;padding:.45rem .6rem;font-size:.65rem;font-weight:700;
  text-transform:uppercase;letter-spacing:.55px;color:var(--muted);
  border-bottom:1px solid var(--border)}
.tbl td{padding:.48rem .6rem;border-bottom:1px solid rgba(255,255,255,.035)}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:rgba(255,255,255,.02)}
.badge{display:inline-flex;align-items:center;gap:.25rem;padding:.16rem .55rem;
  border-radius:50px;font-size:.64rem;font-weight:700;letter-spacing:.3px;white-space:nowrap}
.b-ok  {background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.25);color:var(--green)}
.b-run {background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.25);color:var(--amber)}
.b-err {background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.25);color:var(--red)}
.b-info{background:rgba(6,182,212,.12);border:1px solid rgba(6,182,212,.25);color:var(--cyan)}
.b-done{background:rgba(139,92,246,.12);border:1px solid rgba(139,92,246,.25);color:var(--purple)}

/* Disk bars */
.disk-row{display:flex;align-items:center;gap:.8rem;margin-bottom:.55rem;font-size:.78rem}
.disk-path{width:130px;color:var(--muted);flex-shrink:0;font-size:.7rem;font-family:monospace}
.disk-bar{flex:1;background:rgba(255,255,255,.07);border-radius:999px;height:5px;overflow:hidden}
.disk-fill{height:100%;border-radius:999px;transition:width .9s ease}
.disk-info{font-size:.68rem;color:var(--muted);white-space:nowrap;width:80px;text-align:right}

/* Log */
.log-row{font-size:.7rem;color:var(--muted);padding:.3rem 0;border-bottom:1px solid rgba(255,255,255,.035);
  display:flex;gap:.6rem;align-items:baseline}
.log-row:last-child{border-bottom:none}
.log-name{color:var(--cyan);font-family:monospace;flex-shrink:0;width:170px;font-size:.67rem}
.log-line{color:rgba(241,245,249,.28);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}

/* Status row */
.srv-row{display:flex;align-items:center;gap:.7rem;font-size:.82rem;flex-wrap:wrap}
.srv-item{display:flex;align-items:center;gap:.35rem;padding:.3rem .75rem;
  border-radius:50px;background:var(--surf);border:1px solid var(--border);font-size:.72rem}

/* Refresh */
.ref-row{text-align:center;margin-top:1.4rem}
.btn-ref{display:inline-flex;align-items:center;gap:.4rem;padding:.5rem 1.3rem;
  border-radius:50px;background:var(--surf);border:1px solid var(--border);
  color:var(--text);cursor:pointer;font-size:.78rem;font-weight:600;
  transition:all .18s;letter-spacing:.2px}
.btn-ref:hover{background:rgba(255,255,255,.07);border-color:rgba(255,255,255,.14)}
.btn-ref:active{transform:scale(.97)}
.spin{display:inline-block;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.uptime{font-size:.68rem;color:rgba(241,245,249,.25);margin-top:.5rem;text-align:center}
</style>
</head>
<body>
<div class="wrap">

  <div class="hdr">
    <div class="logo-row">
      <div class="dot-live"></div>
      <span class="logo-txt">Vermarkter · Server Status</span>
    </div>
    <h1><span class="gt">Live Dashboard</span></h1>
    <div class="ts" id="tsLine">Завантаження…</div>
  </div>

  <!-- Main stats -->
  <div class="sg" id="mainStats">
    <div class="sc pink"><div class="sn" id="sBerlinReady">—</div>
      <div class="sl">Berlin Ready</div><div class="ss">READY TO SEND</div></div>
    <div class="sc cyan"><div class="sn" id="sEmailSent">—</div>
      <div class="sl">Email надіслано</div><div class="ss" id="sEmailSub">всього</div></div>
    <div class="sc green"><div class="sn" id="sTotalDone">—</div>
      <div class="sl">Оброблено лідів</div><div class="ss">sent + email + booked</div></div>
    <div class="sc amber"><div class="sn" id="sBatchPending">—</div>
      <div class="sl">Batch в черзі</div><div class="ss" id="sBatchSub">OpenAI Batch API</div></div>
    <div class="sc blue"><div class="sn" id="sTotalLeads">—</div>
      <div class="sl">Лідів у базі</div><div class="ss">beauty_leads total</div></div>
  </div>

  <!-- Brevo progress -->
  <div class="card" id="brevoCard">
    <div class="card-title"><div class="dot-s dot-off" id="brevoDot"></div>Brevo Email Engine</div>
    <div class="prog-wrap">
      <div class="prog-row"><span id="brevoProgText">— / 300</span><span id="brevoProgPct">0%</span></div>
      <div class="prog"><div class="pf" id="brevoBar" style="width:0%"></div></div>
    </div>
    <div style="font-size:.7rem;color:var(--muted);margin-top:.5rem" id="brevoNote"></div>
  </div>

  <!-- Supabase -->
  <div class="card">
    <div class="card-title"><div class="dot-s dot-off" id="sbDot"></div>Supabase Database</div>
    <div class="srv-row" id="sbRow">
      <div class="srv-item"><span id="sbStatus">перевірка…</span></div>
    </div>
  </div>

  <!-- OpenAI Batches table -->
  <div class="card" id="batchCard">
    <div class="card-title"><div class="dot-s" id="oaiDot" style="background:var(--muted)"></div>OpenAI Batch Jobs</div>
    <div style="overflow-x:auto">
      <table class="tbl">
        <thead><tr>
          <th>Файл</th><th>Статус</th><th>Прогрес</th><th>Done/Total</th>
        </tr></thead>
        <tbody id="batchBody">
          <tr><td colspan="4" style="text-align:center;color:var(--muted);padding:.8rem">
            Завантаження…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Disk -->
  <div class="card">
    <div class="card-title"><div class="dot-s dot-ok"></div>Диск сервера</div>
    <div id="diskRows"></div>
  </div>

  <!-- Logs -->
  <div class="card">
    <div class="card-title"><div class="dot-s dot-ok"></div>Останні рядки логів</div>
    <div id="logRows"></div>
  </div>

  <div class="ref-row">
    <button class="btn-ref" onclick="refresh()">
      <svg id="refIcon" width="13" height="13" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="23 4 23 10 17 10"></polyline>
        <polyline points="1 20 1 14 7 14"></polyline>
        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
      </svg>
      Оновити
    </button>
    <div class="uptime" id="uptimeLine"></div>
  </div>

</div>
<script>
var REFRESH_MS = 60000;
var _timer;

function set(id, val) {
  var el = document.getElementById(id);
  if (el) el.textContent = (val === null || val === undefined || val === -1) ? '—' : val;
}
function dotClass(id, cls) {
  var el = document.getElementById(id);
  if (el) { el.className = 'dot-s ' + cls; }
}
function esc(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function fmtUptime(s) {
  var h = Math.floor(s/3600), m = Math.floor((s%3600)/60), sec = s%60;
  return (h>0 ? h+'г ' : '') + (m>0||h>0 ? m+'хв ' : '') + sec+'с';
}

function render(d) {
  var sb = d.supabase || {}, br = d.brevo || {}, bt = d.batches || {};

  // Timestamp
  set('tsLine', 'Оновлено: ' + new Date(d.server_time).toLocaleTimeString('uk-UA') +
      '  ·  ' + new Date(d.server_time).toLocaleDateString('uk-UA'));

  // Main stats
  set('sBerlinReady', sb.berlin_ready);
  set('sEmailSent',   sb.email_sent_total);
  set('sTotalDone',   sb.total_done);
  set('sTotalLeads',  sb.total_leads);
  set('sBatchPending', bt.pending >= 0 ? bt.pending : '—');

  if (bt.in_progress > 0)
    set('sBatchSub', bt.in_progress + ' у процесі');

  // Supabase dot
  dotClass('sbDot', sb.online ? 'dot-ok' : 'dot-err');
  document.getElementById('sbRow').innerHTML =
    '<div class="srv-item">' +
    '<span style="color:' + (sb.online ? 'var(--green)':'var(--red)') + '">' +
    (sb.online ? '● Online' : '● Offline') + '</span>' +
    '</div>' +
    '<div class="srv-item" style="color:var(--muted)">Leads: ' + (sb.total_leads||'?') + '</div>' +
    '<div class="srv-item" style="color:var(--muted)">Berlin ready: ' + (sb.berlin_ready||'0') + '</div>';

  // Brevo
  var brevoOnline = br.online;
  dotClass('brevoDot', brevoOnline ? 'dot-ok' : 'dot-err');
  var sent  = br.sent_today >= 0 ? br.sent_today : 0;
  var cap   = br.daily_limit || 300;
  var pct   = Math.min(100, sent > 0 ? Math.round(sent/cap*100) : 0);
  set('brevoProgText', (br.sent_today >= 0 ? sent : '?') + ' / ' + cap);
  set('brevoProgPct', pct + '%');
  document.getElementById('brevoBar').style.width = pct + '%';
  set('brevoNote', brevoOnline
    ? (br.sent_today >= 0
        ? 'Delivered: ' + (br.delivered||'?') + '  ·  Bounced: ' + (br.bounced||0)
        : br.note || 'Connected — stats unavailable for free plan')
    : 'Brevo offline або ключ не налаштовано');

  // Batch table
  var batches = bt.batches || [];
  dotClass('oaiDot', bt.openai_ok === false ? 'dot-err' : bt.in_progress > 0 ? 'dot-warn' : 'dot-ok');
  if (!batches.length) {
    document.getElementById('batchBody').innerHTML =
      '<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:.8rem">' +
      (bt.openai_ok === false ? '⚠ OpenAI API key не налаштовано' :
       'Немає активних batch-файлів') + '</td></tr>';
  } else {
    var SBADGE = {
      'completed':   '<span class="badge b-done">✓ done</span>',
      'in_progress': '<span class="badge b-run">⏳ running</span>',
      'finalizing':  '<span class="badge b-run">🔄 finalizing</span>',
      'validating':  '<span class="badge b-info">🔍 validating</span>',
      'failed':      '<span class="badge b-err">✗ failed</span>',
      'expired':     '<span class="badge b-err">⏰ expired</span>',
      'cancelled':   '<span class="badge b-err">🚫 cancelled</span>',
    };
    document.getElementById('batchBody').innerHTML = batches.map(function(b) {
      var pBar = '<div style="background:rgba(255,255,255,.07);border-radius:999px;height:5px;width:100px;overflow:hidden">' +
        '<div style="height:100%;width:' + (b.pct||0) + '%;background:var(--grad);border-radius:999px"></div></div>';
      var badge = SBADGE[b.status] || '<span class="badge b-info">' + esc(b.status) + '</span>';
      return '<tr><td style="font-family:monospace;font-size:.67rem;color:var(--muted)">' +
        esc(b.file.replace('.batch_id.txt','')) + '</td>' +
        '<td>' + badge + '</td>' +
        '<td>' + pBar + ' <span style="font-size:.65rem;color:var(--muted)">' + (b.pct||0) + '%</span></td>' +
        '<td style="color:var(--muted);font-size:.72rem">' + (b.done||0) + ' / ' + (b.total||'?') + '</td></tr>';
    }).join('');
  }

  // Disk
  var disks = d.disk || [];
  document.getElementById('diskRows').innerHTML = disks.map(function(dk) {
    var pct  = dk.used_pct || 0;
    var col  = pct > 85 ? 'var(--red)' : pct > 65 ? 'var(--amber)' : 'var(--green)';
    return '<div class="disk-row">' +
      '<div class="disk-path">' + esc(dk.path) + '</div>' +
      '<div class="disk-bar"><div class="disk-fill" style="width:' + pct + '%;background:' + col + '"></div></div>' +
      '<div class="disk-info">' + pct + '% · ' + dk.free_gb + 'GB вільно</div>' +
      '</div>';
  }).join('') || '<div style="color:var(--muted);font-size:.78rem">Дані відсутні</div>';

  // Logs
  var logs = d.logs || {};
  var keys = Object.keys(logs);
  document.getElementById('logRows').innerHTML = keys.length ? keys.map(function(name) {
    var info = logs[name];
    return '<div class="log-row">' +
      '<div class="log-name">' + esc(name) + '</div>' +
      '<div style="color:var(--muted);font-size:.67rem;white-space:nowrap;flex-shrink:0">' +
      info.kb + ' KB</div>' +
      '<div class="log-line">' + esc(info.last || '—') + '</div>' +
      '</div>';
  }).join('') : '<div style="color:var(--muted);font-size:.78rem">Логи не знайдено</div>';

  // Uptime
  set('uptimeLine', 'Сервер працює: ' + fmtUptime(d.uptime_s || 0));
}

function refresh() {
  var icon = document.getElementById('refIcon');
  if (icon) icon.classList.add('spin');
  fetch('/api/status')
    .then(function(r) { return r.json(); })
    .then(function(d) { render(d); })
    .catch(function(e) {
      set('tsLine', 'Помилка оновлення: ' + e.message);
    })
    .finally(function() {
      if (icon) icon.classList.remove('spin');
    });
}

refresh();
_timer = setInterval(refresh, REFRESH_MS);
</script>
</body>
</html>"""


# ── HTTP Handler ───────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Suppress default access log to keep stdout clean
        ts = datetime.now(timezone.utc).strftime('%H:%M:%S')
        print(f'[{ts}] {self.address_string()} {fmt % args}', flush=True)

    def do_GET(self):
        path = self.path.split('?')[0]

        if path in ('/', '/index.html', '/status.html'):
            self._send(200, 'text/html; charset=utf-8', HTML.encode('utf-8'))

        elif path == '/api/status':
            try:
                data = get_metrics()
                body = json.dumps(data, ensure_ascii=False).encode('utf-8')
                self._send(200, 'application/json; charset=utf-8', body,
                           extra_headers=[('Cache-Control', 'no-store'),
                                          ('Access-Control-Allow-Origin', '*')])
            except Exception as e:
                err = json.dumps({'error': str(e)}).encode('utf-8')
                self._send(500, 'application/json', err)

        elif path == '/health':
            self._send(200, 'text/plain', b'ok')

        else:
            self._send(404, 'text/plain', b'Not found')

    def _send(self, code, ct, body, extra_headers=None):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Length', str(len(body)))
        if extra_headers:
            for k, v in extra_headers:
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    import argparse
    p = argparse.ArgumentParser(description='Vermarkter status server')
    p.add_argument('--host', default='0.0.0.0', help='Bind host (default: 0.0.0.0)')
    p.add_argument('--port', type=int, default=8080, help='Port (default: 8080)')
    args = p.parse_args()

    print(f'[STATUS SERVER] Starting on http://{args.host}:{args.port}')
    print(f'[STATUS SERVER] Dashboard: http://46.101.217.35:{args.port}')
    print(f'[STATUS SERVER] API:       http://46.101.217.35:{args.port}/api/status')
    print(f'[STATUS SERVER] Supabase:  {"OK" if SB_URL else "NOT CONFIGURED"}')
    print(f'[STATUS SERVER] Brevo:     {"OK" if BREVO_KEY.startswith("xkeysib-") else "NOT CONFIGURED"}')
    print(f'[STATUS SERVER] OpenAI:    {"OK" if OPENAI_KEY.startswith("sk-") else "NOT CONFIGURED"}')
    print(f'[STATUS SERVER] Press Ctrl+C to stop\n')

    # Warm up cache immediately so first request is fast
    try:
        get_metrics()
        print('[STATUS SERVER] Metrics cache warmed up')
    except Exception as e:
        print(f'[STATUS SERVER] Cache warm-up error (non-fatal): {e}')

    server = HTTPServer((args.host, args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n[STATUS SERVER] Stopped.')


if __name__ == '__main__':
    main()
