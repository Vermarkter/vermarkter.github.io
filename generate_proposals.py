# -*- coding: utf-8 -*-
"""
generate_proposals.py — Vermarkter Salon-PDF-Generator
======================================================
Holt aus Supabase beauty_leads alle Salons OHNE Website und rendert
eine einseitige DE-Proposal als PDF:

  Aufbau: Headline mit Salon-Name → Kurzanalyse → Angebotsblock 1.000 €
          → Live-Demo-Link → Fußzeile mit Vermarkter-Branding.

Output:  proposals/<lead_id>_<slug>.pdf

Setup:   pip install reportlab

Run:     python generate_proposals.py --limit 50
         python generate_proposals.py --limit 0          (alle)
"""

import os, sys, io, re, json, argparse
import urllib.request, urllib.parse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units      import mm
from reportlab.pdfgen         import canvas
from reportlab.lib.colors     import HexColor
from reportlab.pdfbase        import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Supabase ────────────────────────────────────────────────────────────────
import configparser
from pathlib import Path
_cfg = configparser.ConfigParser()
_cfg.read(Path(__file__).parent / 'config.ini', encoding='utf-8')
SB_URL = _cfg.get('SUPABASE', 'url', fallback='').strip()
SB_KEY = _cfg.get('SUPABASE', 'service_role_key', fallback='').strip()
if not SB_KEY or 'ВСТАВИТИ' in SB_KEY or 'PASTE' in SB_KEY:
    SB_KEY = _cfg.get('SUPABASE', 'anon_key', fallback='').strip()
SB_HEAD = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY}

DEMO_URL = "https://vermarkter.vercel.app/services/beauty-industry/de/"
SITE_URL = "https://vermarkter.vercel.app/de/"
OUT_DIR  = "proposals"

# ── Colors (dunkles Premium-Branding) ──────────────────────────────────────
BG_DARK     = HexColor("#0a0a0f")
CARD_DARK   = HexColor("#11111a")
TEXT_LIGHT  = HexColor("#f1f5f9")
TEXT_MUTED  = HexColor("#94a3b8")
PINK        = HexColor("#ec4899")
PURPLE      = HexColor("#8b5cf6")
ACCENT      = HexColor("#f472b6")

# ── TTF-Fonts registrieren (Windows fallback) ──────────────────────────────
FONT_REG = "Helvetica"
FONT_BLD = "Helvetica-Bold"
for cand, name in [
    ("C:/Windows/Fonts/segoeui.ttf",  "Segoe"),
    ("C:/Windows/Fonts/segoeuib.ttf", "Segoe-Bold"),
]:
    try:
        pdfmetrics.registerFont(TTFont(name, cand))
        if "Bold" in name: FONT_BLD = name
        else:              FONT_REG = name
    except Exception:
        pass

# ── Supabase fetch ──────────────────────────────────────────────────────────
def fetch_no_site(limit):
    q = ("/rest/v1/beauty_leads?select=id,name,city,district,phone,email"
         "&website=is.null&order=id.asc")
    if limit > 0: q += "&limit=" + str(limit)
    req = urllib.request.Request(SB_URL + q, headers=SB_HEAD)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

# ── Slugify ─────────────────────────────────────────────────────────────────
SLUG_RX = re.compile(r"[^a-z0-9]+")
def slugify(s):
    s = (s or "salon").lower()
    s = s.replace("ä","ae").replace("ö","oe").replace("ü","ue").replace("ß","ss")
    s = SLUG_RX.sub("-", s).strip("-")
    return s[:40] or "salon"

# ── PDF renderer ────────────────────────────────────────────────────────────
def wrap_text(c, text, font, size, max_w):
    """Simple greedy word wrap."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def render_pdf(lead, out_path):
    name = (lead.get("name") or "Ihr Salon").strip()
    city = (lead.get("city") or "Berlin").strip()
    district = (lead.get("district") or "").strip()
    rating = lead.get("rating")
    nrev   = lead.get("user_ratings_total")

    W, H = A4
    c = canvas.Canvas(out_path, pagesize=A4)

    # Hintergrund
    c.setFillColor(BG_DARK); c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header-Band (Gradient-Approximation: zwei Rects)
    c.setFillColor(PINK);   c.rect(0, H-22*mm, W/2, 22*mm, fill=1, stroke=0)
    c.setFillColor(PURPLE); c.rect(W/2, H-22*mm, W/2, 22*mm, fill=1, stroke=0)

    # V-Logo
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(FONT_BLD, 22)
    c.drawString(18*mm, H-15*mm, "V  Vermarkter")

    # Subtitle rechts
    c.setFont(FONT_REG, 9)
    c.drawRightString(W-18*mm, H-15*mm, "Digitale Heimat für Beauty-Profis")

    # Main Card
    card_x, card_y, card_w, card_h = 15*mm, 30*mm, W-30*mm, H-60*mm
    c.setFillColor(CARD_DARK)
    c.roundRect(card_x, card_y, card_w, card_h, 8*mm, fill=1, stroke=0)

    inner_x = card_x + 14*mm
    inner_w = card_w - 28*mm
    y = card_y + card_h - 16*mm

    # Headline
    c.setFillColor(TEXT_LIGHT)
    c.setFont(FONT_BLD, 22)
    headline = "Analyse für " + name
    for line in wrap_text(c, headline, FONT_BLD, 22, inner_w):
        c.drawString(inner_x, y, line); y -= 10*mm
    y -= 2*mm

    # Location sub-line
    loc_parts = [p for p in [district or city] if p]
    if loc_parts:
        c.setFillColor(ACCENT); c.setFont(FONT_REG, 11)
        c.drawString(inner_x, y, "· ".join(loc_parts))
        y -= 8*mm

    # Analyse-Block
    c.setFillColor(TEXT_LIGHT); c.setFont(FONT_BLD, 13)
    c.drawString(inner_x, y, "Das sehen wir"); y -= 7*mm
    c.setFillColor(TEXT_MUTED); c.setFont(FONT_REG, 11)

    rating_note = ""
    if rating and nrev:
        rating_note = "Ihre " + str(rating) + "★ bei " + str(nrev) + " Bewertungen zeigen echte Qualität — aber "
    analyse = (rating_note +
        "wer Sie online sucht, landet auf Google-Profilen und Drittportalen, "
        "nicht auf Ihrer eigenen Seite. Neue Kundschaft kann Sie nachts oder "
        "am Wochenende nicht spontan buchen. Jeder verlorene Anruf ist ein "
        "verlorener Termin.")
    for line in wrap_text(c, analyse, FONT_REG, 11, inner_w):
        c.drawString(inner_x, y, line); y -= 6*mm
    y -= 3*mm

    # Lösung-Block
    c.setFillColor(TEXT_LIGHT); c.setFont(FONT_BLD, 13)
    c.drawString(inner_x, y, "Unser Vorschlag"); y -= 7*mm
    c.setFillColor(TEXT_MUTED); c.setFont(FONT_REG, 11)
    loesung = ("Eigene Website + Buchungs-App + CRM mit 24/7 KI-Rezeption. "
               "Die KI spricht Deutsch, Englisch und Türkisch, beantwortet "
               "Preise und Öffnungszeiten und bucht Termine direkt in Ihren Kalender.")
    for line in wrap_text(c, loesung, FONT_REG, 11, inner_w):
        c.drawString(inner_x, y, line); y -= 6*mm
    y -= 5*mm

    # Preis-Highlight-Box
    box_h = 26*mm
    c.setFillColor(HexColor("#1a1a2e"))
    c.roundRect(inner_x, y-box_h, inner_w, box_h, 4*mm, fill=1, stroke=0)
    c.setFillColor(ACCENT); c.setFont(FONT_BLD, 24)
    c.drawString(inner_x+8*mm, y-11*mm, "1.000 € einmalig")
    c.setFillColor(TEXT_MUTED); c.setFont(FONT_REG, 10)
    c.drawString(inner_x+8*mm, y-17*mm, "Website + App + CRM + KI-Rezeption · keine Monatskosten")
    c.drawString(inner_x+8*mm, y-22*mm, "Go-Live: 14 Tage · DSGVO-konform · Support inklusive")
    y -= box_h + 6*mm

    # CTA-Zeile
    c.setFillColor(PINK);   c.roundRect(inner_x, y-12*mm, 70*mm, 10*mm, 3*mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff")); c.setFont(FONT_BLD, 11)
    c.drawString(inner_x+6*mm, y-8*mm, "Live-Demo ansehen →")
    c.setFillColor(TEXT_MUTED); c.setFont(FONT_REG, 9)
    c.drawString(inner_x+74*mm, y-8*mm, DEMO_URL)
    y -= 16*mm

    # Footer
    c.setFillColor(TEXT_MUTED); c.setFont(FONT_REG, 8)
    c.drawString(inner_x, card_y + 8*mm,
                 "Vermarkter · hello@vermarkter.eu · " + SITE_URL)
    c.drawRightString(inner_x+inner_w, card_y + 8*mm,
                      "Persönliches Angebot für " + name[:40])

    c.showPage()
    c.save()

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50, help="0 = alle")
    ap.add_argument("--out",   default=OUT_DIR)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print("Vermarkter Proposal-PDF-Generator")
    leads = fetch_no_site(args.limit)
    print("Leads ohne Website:", len(leads))

    ok = fail = 0
    for i, lead in enumerate(leads, 1):
        slug = slugify(lead.get("name"))
        path = os.path.join(args.out, str(lead["id"]) + "_" + slug + ".pdf")
        try:
            render_pdf(lead, path)
            ok += 1
            print("[%d/%d] OK %s" % (i, len(leads), path))
        except Exception as e:
            fail += 1
            print("[%d/%d] FAIL %s — %s" % (i, len(leads), lead.get("name"), e))

    print("\nDONE — generated: %d | failed: %d" % (ok, fail))

if __name__ == "__main__":
    main()
