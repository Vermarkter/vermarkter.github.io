# -*- coding: utf-8 -*-
"""
sales_scripts.py — «Книга продажів» für Vermarkter-Team
========================================================
Генерує індивідуальні txt-файли для першої партії мобільних номерів:
  • назва салону, місто, район
  • wa.me-посилання з пре-заповненим текстом
  • 3 варіанти «дотискаючих» відповідей, зшитих під цей конкретний салон

Filter:  is_mobile = true   (перша партія — Berlin Batches 1-3, LIMIT 188)
Sort:    id ASC
Output:  sales_book/<id>_<slug>.txt

Run:
    python sales_scripts.py --limit 188 --out sales_book
"""

import sys, io, os, re, json, argparse, hashlib, random
import urllib.request, urllib.parse, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SB_URL = "https://wrvdbvekiteopkdwxuzz.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndydmRidmVraXRlb3BrZHd4dXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjU5MjAsImV4cCI6MjA3ODY0MTkyMH0.ZeUzRVMA2O8oz9_VWkOaKGB8CESnXut9Fb1GminWE_c"
SB_HEAD = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY}
DEMO_URL = "https://vermarkter.vercel.app/services/beauty-industry/de/"

SLUG = re.compile(r"[^a-z0-9]+")
def slugify(s):
    s = (s or "salon").lower().replace("ä","ae").replace("ö","oe") \
                              .replace("ü","ue").replace("ß","ss")
    return SLUG.sub("-", s).strip("-")[:40] or "salon"

def clean_phone_for_wa(phone):
    """'+49 30 1234567' → '493012345667' (nur digits, no +)."""
    digits = re.sub(r"\D", "", phone or "")
    # DE mobile starts with 015/016/017 after country code 49
    if digits.startswith("0") and not digits.startswith("00"):
        digits = "49" + digits[1:]
    return digits

MOBILE_RX = re.compile(r"^\+49\s*1[5-7]")
def fetch_mobile(limit):
    """Fallback: is_mobile пустий в більшості записів. Беремо всі з phone і
    фільтруємо по префіксу +49 15/16/17 (DE-mobile)."""
    # Спочатку is_mobile=true
    q1 = ("/rest/v1/beauty_leads?select=id,name,city,district,phone,email,website,custom_message"
          "&is_mobile=eq.true&order=id.asc")
    req = urllib.request.Request(SB_URL + q1, headers=SB_HEAD)
    with urllib.request.urlopen(req, timeout=20) as r:
        rows = json.loads(r.read().decode("utf-8"))
    if len(rows) >= limit:
        return rows[:limit]
    # Потім — heuristic fallback по префіксу
    PAGE = 1000
    offset = 0
    all_rows = list(rows)
    seen = {r["id"] for r in rows}
    while len(all_rows) < limit:
        q2 = ("/rest/v1/beauty_leads?select=id,name,city,district,phone,email,website,custom_message"
              "&phone=not.is.null&order=id.asc&limit=" + str(PAGE) + "&offset=" + str(offset))
        req = urllib.request.Request(SB_URL + q2, headers=SB_HEAD)
        with urllib.request.urlopen(req, timeout=20) as r:
            page = json.loads(r.read().decode("utf-8"))
        if not page: break
        for rec in page:
            if rec["id"] in seen: continue
            if MOBILE_RX.match(rec.get("phone") or ""):
                all_rows.append(rec); seen.add(rec["id"])
                if len(all_rows) >= limit: break
        if len(page) < PAGE: break
        offset += PAGE
    return all_rows[:limit]

# ── Rebuttals (3 Varianten pro Salon) ──────────────────────────────────────
REBUT_PRICE = [
    ("«Zu teuer»",
     "Einmalig 1.000 € entspricht ca. 3–4 Haarschnitten pro Woche im ersten Monat. "
     "Nach Monat 1 läuft alles profitabel — ohne Abo, ohne versteckte Gebühren. "
     "Plus: die KI-Rezeption fängt auch verpasste Anrufe nachts auf — das sind bei euch "
     "realistisch 5-10 verlorene Termine pro Woche."),
    ("«Können wir uns leisten?»",
     "Rechnen wir kurz: durchschnittlicher Ticket bei {type} ≈ 45-60 €. "
     "Ein einziger zusätzlicher Termin pro Woche durch 24/7-Buchung = ca. 2.400 € extra/Jahr. "
     "Investment amortisiert sich in 5-6 Monaten, danach ist jeder KI-Termin reiner Gewinn."),
    ("«Warum so günstig?»",
     "Wir sind kein Konzern mit 200 Mitarbeitern. Wir bauen in 14 Tagen direkt für euch, "
     "ohne Zwischenhändler. Günstig heißt nicht billig — heißt effizient."),
]
REBUT_TIME = [
    ("«Keine Zeit»",
     "Genau deshalb die KI-Rezeption. Ihr macht eure Kunst am Stuhl, wir kümmern uns um "
     "die Telefon-Flut, die Online-Buchung, die Erinnerungen. Setup dauert ~14 Tage, "
     "euer Zeitaufwand: 1× 45-Min-Kickoff + 2× 15-Min-Review. Fertig."),
    ("«Wir machen das später»",
     "Jede Woche ohne 24/7-Buchung = 3-8 verlorene Termine. Bei 45 € Ticket = 135-360 € "
     "verpasster Umsatz pro Woche. Das sind ca. 13.000 €/Jahr, die einfach versickern."),
    ("«Wir haben schon Google»",
     "Google zeigt euch — aber Google bucht nicht. Der Kunde klickt auf euren Namen, "
     "sieht Öffnungszeiten, ruft an... und wenn besetzt ist: weiter zum Nächsten. "
     "Mit eigener Buchungs-App kommt er direkt in euren Kalender."),
]
REBUT_TRUST = [
    ("«Ist das seriös?»",
     "Wir zeigen live, wie's bei anderen Salons läuft — Demo unter " + DEMO_URL + ". "
     "Zahlung erst nach Go-Live, DSGVO-Vertrag inkl., Hosting auf deutschen Servern."),
    ("«Wir kennen euch nicht»",
     "Verstehe. Genau deshalb: 30-Min-Videocall, ich zeige die Demo live an eurem "
     "Beispiel, ihr stellt Fragen. Erst wenn's passt, reden wir über Vertrag."),
    ("«KI auf Türkisch funktioniert nicht»",
     "Wir haben die Sprach-Engine explizit auf türkisch + deutsch + englisch trainiert. "
     "Demo-Anruf gern — ihr hört es selbst. Die meisten glauben es erst nach dem Test."),
]
REBUT_TECH = [
    ("«Kein Interesse an Technik»",
     "Deshalb macht ALLES die KI — ihr müsst nur an der Tür öffnen. Wir kümmern uns "
     "um Hosting, Updates, Sprach-Tuning. Ihr bekommt einmal im Monat eine "
     "1-seitige Zusammenfassung: Termine, Anrufe, Umsatz."),
    ("«Wir haben keine App»",
     "Eben deshalb. In 14 Tagen habt ihr eine — mit eurem Logo, euren Farben, "
     "eurer Leistungsliste. Der Kunde bucht aus dem Bett, ihr seht es sofort im Dashboard."),
    ("«Was, wenn die KI Fehler macht?»",
     "Jeder Termin wird euch als Benachrichtigung zugeschickt, ihr bestätigt per Klick. "
     "Bei unklaren Fällen leitet die KI an eure Nummer weiter. Ihr habt immer das letzte Wort."),
]
POOLS = [REBUT_PRICE, REBUT_TIME, REBUT_TRUST, REBUT_TECH]

SALON_TYPE_RX = [
    (re.compile(r"\b(barber|barbier|barbershop)\b", re.I), "Barbershop"),
    (re.compile(r"\b(nagel|nail|nails)\b", re.I),          "Nagelstudio"),
    (re.compile(r"\b(kosmetik|beauty|skin|spa)\b", re.I),  "Kosmetikstudio"),
    (re.compile(r"\b(friseur|hair|coiffeur)\b", re.I),     "Friseursalon"),
]
def detect_type(name):
    for rx, lbl in SALON_TYPE_RX:
        if rx.search(name or ""): return lbl
    return "Salon"

WA_OPENERS = [
    "Hallo! Ich bin Andrii von Vermarkter. Ich habe mir {name} angesehen — "
    "kurze Frage: interessiert euch eine eigene Buchungs-App + KI-Rezeption "
    "für einmalig 1.000 €? Live-Demo: " + DEMO_URL,
    "Hey {name} ✨ Kurz und direkt: eigene Website + App + CRM + 24/7 KI-Rezeption "
    "für einmalig 1.000 €. Kein Abo. Demo: " + DEMO_URL,
    "Guten Tag! Wir bauen für Beauty-Salons in {city} komplette Digital-Pakete "
    "(Website + App + KI-Buchung) für einmalig 1.000 €. {name} wäre ein perfekter Kandidat. "
    "Demo: " + DEMO_URL,
]

def render_file(lead, rng):
    name   = (lead.get("name") or "Ihr Salon").strip()
    city   = (lead.get("city") or "Berlin").strip()
    distr  = (lead.get("district") or city).strip()
    phone  = (lead.get("phone") or "").strip()
    wa_num = clean_phone_for_wa(phone)
    stype  = detect_type(name)
    opener = rng.choice(WA_OPENERS).replace("{name}", name).replace("{city}", city)
    wa_msg = urllib.parse.quote(opener)
    wa_link = "https://wa.me/" + wa_num + "?text=" + wa_msg if wa_num else "(kein Mobil)"

    # 3 Rebuttal-Varianten aus verschiedenen Pools
    pools_shuffled = list(POOLS)
    rng.shuffle(pools_shuffled)
    rebuttals = []
    for pool in pools_shuffled[:3]:
        label, text = rng.choice(pool)
        rebuttals.append((label, text.replace("{type}", stype)))

    # Text-Datei zusammensetzen
    lines = []
    lines.append("=" * 70)
    lines.append("SALES SCRIPT · " + name)
    lines.append("=" * 70)
    lines.append("")
    lines.append("Typ:       " + stype)
    lines.append("Stadt:     " + city)
    lines.append("Bezirk:    " + distr)
    lines.append("Telefon:   " + (phone or "—"))
    lines.append("E-Mail:    " + (lead.get("email") or "—"))
    lines.append("Website:   " + (lead.get("website") or "—"))
    lines.append("")
    lines.append("WhatsApp-Link (Pre-Filled):")
    lines.append("  " + wa_link)
    lines.append("")
    lines.append("Opener-Text (pre-filled in WA-Link):")
    lines.append("  " + opener)
    lines.append("")
    lines.append("─" * 70)
    lines.append("REBUTTALS — 3 dotiskayuchi Varianten")
    lines.append("─" * 70)
    for n, (label, text) in enumerate(rebuttals, 1):
        lines.append("")
        lines.append("%d) %s" % (n, label))
        lines.append("   " + text)
    lines.append("")
    lines.append("─" * 70)
    lines.append("NÄCHSTER SCHRITT")
    lines.append("─" * 70)
    lines.append("• Ziel: 30-Min-Videocall buchen (Calendly/Zoom).")
    lines.append("• Bei Zustimmung → Demo live zeigen → Vertrag per DocuSign.")
    lines.append("• Go-Live in 14 Tagen, Zahlung erst nach Launch.")
    lines.append("")
    return "\n".join(lines)

def fetch_all(limit=0):
    """Усі ліди зі статусом new, пагінація по 1000."""
    PAGE = 1000
    all_rows, offset = [], 0
    while True:
        q = ("/rest/v1/beauty_leads?select=id,name,city,district,phone,email,website,custom_message"
             "&order=id.asc&limit=" + str(PAGE) + "&offset=" + str(offset))
        req = urllib.request.Request(SB_URL + q, headers=SB_HEAD)
        with urllib.request.urlopen(req, timeout=30) as r:
            page = json.loads(r.read().decode("utf-8"))
        if not page: break
        all_rows.extend(page)
        if len(page) < PAGE or (limit and len(all_rows) >= limit): break
        offset += PAGE
    if limit: all_rows = all_rows[:limit]
    return all_rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=188)
    ap.add_argument("--out",   default="sales_book")
    ap.add_argument("--all",   action="store_true",
                    help="Всі ліди, не тільки мобільні (consolidated mode)")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print("Vermarkter Sales-Book Generator")
    if args.all:
        leads = fetch_all(args.limit if args.limit != 188 else 0)
        print("All leads:", len(leads))
    else:
        leads = fetch_mobile(args.limit)
        print("Mobile-Leads:", len(leads))

    ok = fail = 0
    for i, lead in enumerate(leads, 1):
        seed = int(hashlib.md5(str(lead["id"]).encode()).hexdigest()[:10], 16)
        rng  = random.Random(seed)
        try:
            txt = render_file(lead, rng)
            slug = slugify(lead.get("name"))
            path = os.path.join(args.out, "%s_%s.txt" % (lead["id"], slug))
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            ok += 1
        except Exception as e:
            fail += 1
            print("[%d/%d] FAIL id=%s: %s" % (i, len(leads), lead.get("id"), e))

    print("DONE — files: %d | failed: %d" % (ok, fail))

if __name__ == "__main__":
    main()
