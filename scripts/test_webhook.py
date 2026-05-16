#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_webhook.py — Send mock Brevo webhook events to verify the server works.

Tests (all safe — uses nonexistent emails, no real DB changes):
  0. GET /health              — server up?
  1. Auth: no token           — expect 401
  2. Auth: wrong token        — expect 401
  3. Auth: correct token      — expect 200
  4. Event: delivered         — log only, no DB write
  5. Event: hard_bounce       — lead_not_found (email doesn't exist)
  6. Event: soft_bounce       — lead_not_found
  7. Event: spam              — lead_not_found

Usage:
  # Test local instance (when running dev server on localhost):
  python scripts/test_webhook.py

  # Test DO server directly (HTTP):
  python scripts/test_webhook.py --host 46.101.217.35 --port 8082

  # Test production HTTPS via nginx (recommended after nginx setup):
  python scripts/test_webhook.py --url https://my-salon.eu/brevo/webhook

  # Quick smoke-test only (health + auth):
  python scripts/test_webhook.py --smoke
"""

import sys, io, os, json, time, argparse, configparser, urllib.request, urllib.parse
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_cfg  = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

def _c(s, k, fallback=''):
    try:    return (_cfg.get(s, k) or '').strip() or fallback
    except: return fallback

WEBHOOK_SECRET = _c('BREVO', 'webhook_secret', '')


def _do(method, url, body=None, headers=None) -> tuple:
    """Returns (status_code, response_text)."""
    h = headers or {}
    if body is not None:
        h['Content-Type'] = 'application/json; charset=utf-8'
    data = json.dumps(body, ensure_ascii=False).encode('utf-8') if body is not None else None
    req  = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')
    except Exception as ex:
        return 0, str(ex)


def _check(label, status, body, expect_code):
    ok = status == expect_code
    icon = 'OK' if ok else 'FAIL'
    print(f'  [{icon}] {label}')
    print(f'         HTTP {status} (expected {expect_code})')
    body_short = body[:200].replace('\n', ' ')
    if body_short:
        print(f'         {body_short}')
    return ok


def run_tests(base_url, token, smoke_only):
    passed = failed = 0

    # ── 0. Health check ───────────────────────────────────────────────────────
    health_url = base_url.replace('/brevo/webhook', '/health').split('?')[0]
    status, body = _do('GET', health_url)
    ok = _check('GET /health — server up', status, body, 200)
    (passed if ok else globals().update(failed=failed+1) or True) and (passed := passed + (1 if ok else 0))
    if not ok:
        print(f'\n  Server not reachable at {health_url}')
        print('  Start with: python scripts/brevo_webhook_server.py [--host 0.0.0.0] [--port 8082]')
        return passed, failed + 1

    if not ok:
        failed += 1
    else:
        passed += 1

    if status == 200:
        try:
            data = json.loads(body)
            print(f'         uptime={data.get("uptime_s", "?")}s  '
                  f'stats={json.dumps(data.get("stats", {}), ensure_ascii=False)}')
        except Exception:
            pass

    if smoke_only:
        print('\n  [smoke] Skipping event tests (--smoke flag).')
        return passed, failed

    # ── 1. Auth: no token ─────────────────────────────────────────────────────
    if token:
        url_no_auth = base_url.split('?')[0]
        status, body = _do('POST', url_no_auth, [{'event': 'delivered', 'email': 'x@x.com'}])
        ok = _check('Auth: no token → 401', status, body, 401)
        passed += ok; failed += not ok

        # ── 2. Auth: wrong token ──────────────────────────────────────────────
        url_bad_auth = base_url.split('?')[0] + '?token=WRONG_TOKEN'
        status, body = _do('POST', url_bad_auth, [{'event': 'delivered', 'email': 'x@x.com'}])
        ok = _check('Auth: wrong token → 401', status, body, 401)
        passed += ok; failed += not ok
    else:
        print('  [SKIP] Auth tests — no webhook_secret configured (dev mode)')

    # Build authenticated URL
    auth_url = base_url.split('?')[0]
    if token:
        auth_url += f'?token={token}'

    # ── 3. Valid auth ─────────────────────────────────────────────────────────
    status, body = _do('POST', auth_url, [{'event': 'delivered',
                                           'email': 'test-no-lead@example-vermarkter.de',
                                           'subject': 'Test subject'}])
    ok = _check('Auth: correct token → 200', status, body, 200)
    passed += ok; failed += not ok

    # ── 4. Event: delivered ───────────────────────────────────────────────────
    # log only, no DB write — safe to send even with a real lead email
    ev_delivered = [{'event': 'delivered',
                     'email': 'test-no-lead@example-vermarkter.de',
                     'subject': '[TEST] Webhook verification'}]
    status, body = _do('POST', auth_url, ev_delivered)
    ok = _check('Event: delivered (log only)', status, body, 200)
    passed += ok; failed += not ok

    # ── 5. Event: hard_bounce (nonexistent email → lead_not_found) ────────────
    ev_bounce = [{'event': 'hard_bounce',
                  'email': 'test-no-lead@example-vermarkter.de',
                  'reason': 'Mailbox does not exist (TEST)'}]
    status, body = _do('POST', auth_url, ev_bounce)
    ok = _check('Event: hard_bounce (email not in DB → safe)', status, body, 200)
    passed += ok; failed += not ok

    # ── 6. Event: soft_bounce ─────────────────────────────────────────────────
    ev_soft = [{'event': 'soft_bounce',
                'email': 'test-no-lead@example-vermarkter.de',
                'reason': 'Mailbox full (TEST)'}]
    status, body = _do('POST', auth_url, ev_soft)
    ok = _check('Event: soft_bounce (email not in DB → safe)', status, body, 200)
    passed += ok; failed += not ok

    # ── 7. Event: spam ────────────────────────────────────────────────────────
    ev_spam = [{'event': 'spam',
                'email': 'test-no-lead@example-vermarkter.de'}]
    status, body = _do('POST', auth_url, ev_spam)
    ok = _check('Event: spam (email not in DB → safe)', status, body, 200)
    passed += ok; failed += not ok

    return passed, failed


def main():
    p = argparse.ArgumentParser(description='Test brevo_webhook_server.py')
    g = p.add_mutually_exclusive_group()
    g.add_argument('--url',  default='', help='Full webhook URL incl. token param')
    g.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    p.add_argument('--port', type=int, default=8082, help='Server port (default: 8082)')
    p.add_argument('--smoke', action='store_true', help='Health + auth only, skip event tests')
    args = p.parse_args()

    if args.url:
        base_url = args.url
    else:
        base_url = f'http://{args.host}:{args.port}/brevo/webhook'
        if WEBHOOK_SECRET:
            base_url += f'?token={WEBHOOK_SECRET}'

    print(f'\n{"="*64}')
    print(f'  Brevo Webhook Test')
    print(f'  URL:    {base_url.replace(WEBHOOK_SECRET, "SECRET") if WEBHOOK_SECRET else base_url}')
    print(f'  Token:  {"set (" + str(len(WEBHOOK_SECRET)) + " chars)" if WEBHOOK_SECRET else "not set (dev mode)"}')
    print(f'{"="*64}\n')

    passed, failed = run_tests(base_url, WEBHOOK_SECRET, args.smoke)

    print(f'\n{"="*64}')
    result = 'ALL PASS' if failed == 0 else f'{failed} FAILED'
    print(f'  Result: {result}  ({passed} passed, {failed} failed)')
    print(f'{"="*64}\n')
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
