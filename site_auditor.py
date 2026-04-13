# -*- coding: utf-8 -*-
"""
site_auditor.py — Intelligent Website-Scoring für beauty_leads
===============================================================
Für jeden Lead mit website IS NOT NULL:
  • lädt die Startseite (Timeout 8s)
  • prüft Online-Booking (Booksy/Treatwell/Planity/Fresha/Calendly/.../iframe)
  • prüft Mobile-Friendliness (viewport-meta, max-width media-query)
  • schätzt das Design-Alter (Tech-Stack-Heuristik:
        WordPress-5+ / TailwindCSS / React / Next / Vue / Shopify → modern
        jQuery-1.x / Flash / <frameset> / inline-px-fonts → alt)

Scoring 1..10 (je höher — desto IDEALER Kunde für uns):
  + 4 Punkte wenn KEIN Online-Booking
  + 2 Punkte wenn NICHT mobile-friendly
  + 2 Punkte wenn Design alt
  + 1 Punkt  wenn KEIN SSL
  + 1 Punkt  wenn Seite < 10 KB (leere Holding-Page)

Keine lead_score-Spalte? Wir schreiben JSON in `notes`:
  notes = "score=7 | booking=n | mobile=y | design=legacy"
Update per PATCH.

Run:
    python site_auditor.py --limit 50 --delay 1.0
    python site_auditor.py --dry-run --limit 10
"""

import sys, io, re, ssl, json, time, argparse
import urllib.request, urllib.parse, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SB_URL = "https://wrvdbvekiteopkdwxuzz.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndydmRidmVraXRlb3BrZHd4dXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjU5MjAsImV4cCI6MjA3ODY0MTkyMH0.ZeUzRVMA2O8oz9_VWkOaKGB8CESnXut9Fb1GminWE_c"
SB_HEAD = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
           "Content-Type": "application/json"}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36 VermarkterAudit/1.0")

# ── Regex-Heuristiken ──────────────────────────────────────────────────────
BOOKING_RX = re.compile(
    r"(booksy|treatwell|planity|fresha|calendly|shore\.com|salonkee|"
    r"simplybook|timify|bookitit|reservio|acuityscheduling|"
    r"termin-?buch|online-?termin|jetzt-?buchen|buchungs-?tool|"
    r"calendar-widget|iframe[^>]+(book|calendar|termin))", re.I)
MOBILE_VIEWPORT = re.compile(r'<meta[^>]+name=["\']viewport["\']', re.I)
MEDIA_QUERY     = re.compile(r"@media[^{]*\(max-width", re.I)

MODERN_STACK = re.compile(
    r"(tailwindcss|react|next\.js|vue\.js|svelte|gatsby|"
    r"wp-includes/js/dist/[^\"]*\b6\.|gutenberg|elementor)", re.I)
LEGACY_MARK  = re.compile(
    r"(<frameset|<frame\s|<font\s|shockwave|flash\.swf|"
    r"jquery[/-]1\.|prototype\.js|mootools|"
    r"<table[^>]+border=[\"']?[1-9])", re.I)

# ── HTTP ───────────────────────────────────────────────────────────────────
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
        q = ("/rest/v1/beauty_leads?select=id,name,website,notes"
             "&website=not.is.null&order=id.asc&limit=" + str(PAGE) +
             "&offset=" + str(offset))
        rows = sb_get(q)
        all_rows.extend(rows)
        if len(rows) < PAGE or (limit and len(all_rows) >= limit):
            break
        offset += PAGE
    if limit: all_rows = all_rows[:limit]
    return all_rows

def fetch_html(url, timeout=8):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    req = urllib.request.Request(url, headers={"User-Agent": UA,
        "Accept": "text/html,*/*", "Accept-Language": "de,en;q=0.7"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        data = r.read(400_000)  # max 400 KB
        return url, data.decode("utf-8", errors="ignore")

# ── Scoring ────────────────────────────────────────────────────────────────
def score_site(url, html):
    flags = {"booking": False, "mobile": False, "design": "modern",
             "ssl": url.startswith("https://"), "size": len(html)}
    h = html[:300_000]  # обмежуємо дорогі regex

    flags["booking"] = bool(BOOKING_RX.search(h))
    flags["mobile"]  = bool(MOBILE_VIEWPORT.search(h) or MEDIA_QUERY.search(h))

    if LEGACY_MARK.search(h):
        flags["design"] = "legacy"
    elif MODERN_STACK.search(h):
        flags["design"] = "modern"
    else:
        flags["design"] = "unclear"

    score = 1
    if not flags["booking"]: score += 4
    if not flags["mobile"]:  score += 2
    if flags["design"] == "legacy":   score += 2
    elif flags["design"] == "unclear": score += 1
    if not flags["ssl"]:     score += 1
    if flags["size"] < 10_000: score += 1
    score = min(score, 10)
    return score, flags

def audit_one(lead):
    url = lead.get("website")
    if not url:
        return None, {"err": "no website"}
    try:
        final_url, html = fetch_html(url)
    except urllib.error.HTTPError as e:
        return 9, {"err": "http " + str(e.code), "booking": False,
                   "mobile": False, "design": "unknown", "ssl": False}
    except Exception as e:
        # Site offline / DNS fail → ідеальний кандидат (score 10)
        return 10, {"err": str(e)[:60], "booking": False,
                    "mobile": False, "design": "offline", "ssl": False}
    return score_site(final_url, html)

def notes_blob(score, flags):
    parts = ["score=" + str(score),
             "booking=" + ("y" if flags.get("booking") else "n"),
             "mobile="  + ("y" if flags.get("mobile")  else "n"),
             "design="  + str(flags.get("design", "?")),
             "ssl="     + ("y" if flags.get("ssl")     else "n")]
    if flags.get("err"): parts.append("err=" + flags["err"])
    return "audit: " + " | ".join(parts)

def merge_notes(old, new_blob):
    old = (old or "").strip()
    # видаляємо попередній audit-блок
    cleaned = re.sub(r"audit:\s*[^|]*(\|\s*[^|]+)*", "", old).strip(" |")
    return (cleaned + " | " + new_blob).strip(" |") if cleaned else new_blob

# ── Main ───────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--delay", type=float, default=0.8)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Vermarkter Site Auditor")
    targets = fetch_targets(args.limit)
    print("Sites zu auditieren:", len(targets))

    ok = fail = 0
    dist = {i: 0 for i in range(1, 11)}
    for i, lead in enumerate(targets, 1):
        t0 = time.time()
        score, flags = audit_one(lead)
        dt = time.time() - t0

        if score is None:
            fail += 1
            print("[%d/%d] SKIP %s — %s" %
                  (i, len(targets), (lead.get("name") or "")[:30], flags.get("err")))
            continue

        blob = notes_blob(score, flags)
        dist[score] = dist.get(score, 0) + 1
        if args.dry_run:
            print("[%d/%d] %-30s score=%d  %s  (%.1fs)" %
                  (i, len(targets), (lead.get("name") or "")[:30],
                   score, blob, dt))
        else:
            try:
                new_notes = merge_notes(lead.get("notes"), blob)
                sb_patch(lead["id"], {"notes": new_notes})
                ok += 1
                if i % 25 == 0 or i == len(targets):
                    print("[%d/%d] score=%d %s" %
                          (i, len(targets), score, (lead.get("name") or "")[:40]))
            except Exception as e:
                fail += 1
                print("[%d/%d] PATCH FAIL id=%s: %s" %
                      (i, len(targets), lead["id"], e))

        if args.delay and i < len(targets):
            time.sleep(args.delay)

    print("\nDONE — audited: %d | failed: %d" % (ok, fail))
    print("Score-Verteilung:", {k: v for k, v in dist.items() if v})

if __name__ == "__main__":
    main()
