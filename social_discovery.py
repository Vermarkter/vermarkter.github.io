# -*- coding: utf-8 -*-
"""
social_discovery.py — Instagram-Hunter für email-lose Leads
============================================================
Плюс-стратегія B: для кожного ліда без email пробуємо знайти
прямий лінк на Instagram.

Джерела пошуку:
  1. Власний сайт салону → <a href="instagram.com/..."> / og:url / meta-теги
  2. Якщо на сайті немає — DuckDuckGo HTML search (no API key):
     'site:instagram.com "{salon name}" {city}'
     → парсимо перший результат з uddg=... redirect

Зберігаємо знайдений IG-handle в `notes` (додаємо "ig=@handle").
Фейли (handle не знайдено) — ігноруємо без запису.

Run:
    python social_discovery.py --limit 50 --delay 1.0
    python social_discovery.py --dry-run --limit 10
"""

import sys, io, re, ssl, json, time, argparse
import urllib.request, urllib.parse, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import configparser
from pathlib import Path
_cfg = configparser.ConfigParser()
_cfg.read(Path(__file__).parent / 'config.ini', encoding='utf-8')
SB_URL = _cfg.get('SUPABASE', 'url', fallback='').strip()
SB_KEY = _cfg.get('SUPABASE', 'service_role_key', fallback='').strip()
if not SB_KEY or 'ВСТАВИТИ' in SB_KEY or 'PASTE' in SB_KEY:
    SB_KEY = _cfg.get('SUPABASE', 'anon_key', fallback='').strip()
SB_HEAD = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
           "Content-Type": "application/json"}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36 VermarkterSocial/1.0")

IG_URL_RX = re.compile(
    r"(?:https?://)?(?:www\.)?instagram\.com/"
    r"([a-zA-Z0-9_.]{2,30})/?", re.I)
BAD_HANDLES = {"explore", "accounts", "p", "reel", "reels", "stories",
               "instagram", "about", "privacy", "login", "direct",
               "share", "tv", "developer", "rsrc", "static", "cdn"}
# Blockiert Datei-artige Artefakte: rsrc.php, image.jpg, etc.
FILE_EXT_RX = re.compile(r"\.(php|html?|js|css|jpe?g|png|gif|svg|webp)$", re.I)

# ── HTTP ───────────────────────────────────────────────────────────────────
def http_get(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
        "Accept": "text/html,*/*", "Accept-Language": "de,en;q=0.7"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read(300_000).decode("utf-8", errors="ignore")

def sb_get(path):
    req = urllib.request.Request(SB_URL + path, headers=SB_HEAD)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def sb_patch(lead_id, payload):
    body = json.dumps(payload).encode("utf-8")
    h = dict(SB_HEAD); h["Prefer"] = "return=minimal"
    url = SB_URL + "/rest/v1/beauty_leads?id=eq." + str(lead_id)
    req = urllib.request.Request(url, data=body, headers=h, method="PATCH")
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status

def fetch_targets(limit):
    PAGE = 1000
    all_rows = []
    offset = 0
    while True:
        q = ("/rest/v1/beauty_leads?select=id,name,city,district,website,notes"
             "&email=is.null&order=id.asc&limit=" + str(PAGE) + "&offset=" + str(offset))
        rows = sb_get(q)
        all_rows.extend(rows)
        if len(rows) < PAGE or (limit and len(all_rows) >= limit):
            break
        offset += PAGE
    if limit: all_rows = all_rows[:limit]
    return all_rows

# ── Extraktor ──────────────────────────────────────────────────────────────
def find_ig_handle(html):
    for m in IG_URL_RX.finditer(html or ""):
        handle = m.group(1).strip().lower().rstrip(".")
        if (handle and handle not in BAD_HANDLES and not handle.isdigit()
                and not FILE_EXT_RX.search(handle)):
            return handle
    return None

def scrape_site(url):
    if not url: return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        html = http_get(url, timeout=7)
    except Exception:
        return None
    h = find_ig_handle(html)
    if h: return h
    # Fallback: /kontakt, /impressum, footer
    for path in ("/kontakt", "/impressum", "/contact", "/about"):
        try:
            html = http_get(url.rstrip("/") + path, timeout=5)
        except Exception:
            continue
        h = find_ig_handle(html)
        if h: return h
    return None

DDG_URL = "https://html.duckduckgo.com/html/?q="
DDG_LINK_RX = re.compile(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"', re.I)
DDG_REDIR_RX = re.compile(r"uddg=([^&]+)")

def ddg_search_ig(name, city):
    q = 'site:instagram.com "%s" %s' % (name, city or "")
    try:
        html = http_get(DDG_URL + urllib.parse.quote(q), timeout=8)
    except Exception:
        return None
    # Перший результат
    for m in DDG_LINK_RX.finditer(html):
        href = m.group(1)
        # DuckDuckGo робить redirect /l/?uddg=<encoded>
        r = DDG_REDIR_RX.search(href)
        target = urllib.parse.unquote(r.group(1)) if r else href
        h = find_ig_handle(target)
        if h: return h
    return None

def hunt(lead):
    # 1. Власний сайт
    if lead.get("website"):
        h = scrape_site(lead["website"])
        if h: return h, "site"
    # 2. DuckDuckGo
    h = ddg_search_ig(lead.get("name") or "", lead.get("city") or "")
    if h: return h, "ddg"
    return None, None

def merge_ig_notes(old, handle):
    old = (old or "").strip()
    cleaned = re.sub(r"\|?\s*ig=@?[a-zA-Z0-9_.]+", "", old).strip(" |")
    tag = "ig=@" + handle
    return (cleaned + " | " + tag).strip(" |") if cleaned else tag

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=1.2)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Vermarkter Social Discovery (IG Hunter)")
    targets = fetch_targets(args.limit)
    print("Email-lose Leads:", len(targets))

    hits = misses = fails = 0
    for i, lead in enumerate(targets, 1):
        t0 = time.time()
        try:
            handle, src = hunt(lead)
        except Exception as e:
            fails += 1
            handle, src = None, "err:" + str(e)[:30]

        dt = time.time() - t0
        name = (lead.get("name") or "")[:32]
        if handle:
            hits += 1
            if args.dry_run:
                print("[%d/%d] %-32s → @%s (via %s, %.1fs)" %
                      (i, len(targets), name, handle, src, dt))
            else:
                try:
                    new_notes = merge_ig_notes(lead.get("notes"), handle)
                    sb_patch(lead["id"], {"notes": new_notes})
                    if hits % 20 == 0 or i == len(targets):
                        print("[%d/%d] HIT @%s — %s" % (i, len(targets), handle, name))
                except Exception as e:
                    fails += 1
                    print("[%d/%d] PATCH FAIL id=%s: %s" %
                          (i, len(targets), lead["id"], e))
        else:
            misses += 1
            if i % 50 == 0:
                print("[%d/%d] miss — %s" % (i, len(targets), name))

        if args.delay and i < len(targets):
            time.sleep(args.delay)

    print("\nDONE — IG-handles: %d | misses: %d | errors: %d" % (hits, misses, fails))

if __name__ == "__main__":
    main()
