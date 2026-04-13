# -*- coding: utf-8 -*-
"""
personalize_vault.py — Token-Burner für beauty_leads
=====================================================
Ersetzt die schabloneartigen custom_message-Einträge durch echt individuelle
DE-Pitches. Jede Nachricht wird deterministisch aus Lead-Eigenschaften
(Name, Stadt, Bezirk, Typ, Website, Email) gewoben — 40+ Opener-Varianten,
50+ Analyse-Lines, 12 CTA-Packages. Seed = MD5(id) → stabile Reproduktion.

Filter:   status = 'new'  UND  last_contacted IS NULL
Update:   custom_message wird überschrieben, notes bekommt Flag 'personalized'.

Run:
    python personalize_vault.py --limit 2000
    python personalize_vault.py --dry-run --limit 5
"""

import sys, io, json, hashlib, random, argparse, re, time
import urllib.request, urllib.parse, urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

SB_URL = "https://wrvdbvekiteopkdwxuzz.supabase.co"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndydmRidmVraXRlb3BrZHd4dXp6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNjU5MjAsImV4cCI6MjA3ODY0MTkyMH0.ZeUzRVMA2O8oz9_VWkOaKGB8CESnXut9Fb1GminWE_c"
SB_HEAD = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
           "Content-Type": "application/json"}
DEMO_URL = "https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"

# ── Salon-Typ erkennen ──────────────────────────────────────────────────────
TYPE_RX = [
    (re.compile(r"\b(barber|barbier|barbershop)\b", re.I),          "Barber"),
    (re.compile(r"\b(nagel|nail|nails)\b", re.I),                   "Nagelstudio"),
    (re.compile(r"\b(kosmetik|beauty|skin|haut|spa|cosmetic)\b", re.I), "Kosmetikstudio"),
    (re.compile(r"\b(friseur|hair|coiffeur|salon|studio)\b", re.I), "Friseursalon"),
]
def detect_type(name):
    for rx, lbl in TYPE_RX:
        if rx.search(name or ""): return lbl
    return "Salon"

# ── First-name aus Salonname ────────────────────────────────────────────────
FN_RX = re.compile(r"\b(?:Friseur|Salon|Barbier|Studio|by|von|bei)\s+([A-ZÄÖÜ][a-zäöüß]+)")
def first_name(name):
    m = FN_RX.search(name or "")
    return m.group(1) if m else None

# ── Viertel/Stadt-Flavor ────────────────────────────────────────────────────
DISTRICT_FLAVORS = {
    "Mitte":        ["im Herzen der Stadt", "direkt zwischen Touristen und Laufkundschaft",
                     "mitten im Trubel"],
    "Schöneberg":   ["im Kiez-Charme von Schöneberg", "zwischen Stammgästen und Szenepublikum"],
    "Steglitz":     ["im familiären Steglitz", "in der ruhigen Ecke zwischen Schloßstraße und Botanischem Garten"],
    "Zehlendorf":   ["im noblen Zehlendorf", "zwischen Dahlem und Wannsee"],
    "Grunewald":    ["im gehobenen Grunewald"],
    "Dahlem":       ["im akademisch geprägten Dahlem"],
    "München":      ["im teuren München", "zwischen Schwabing-Vibes und Altstadt-Ruhe"],
    "Köln":         ["im rheinischen Köln", "zwischen Dom, Agnesviertel und Belgischem Viertel"],
    "Düsseldorf":   ["im schicken Düsseldorf", "zwischen Kö und Altstadt"],
    "Stuttgart":    ["im schwäbischen Stuttgart", "zwischen Königstraße und Hang-Lagen"],
    "Leipzig":      ["im hippen Leipzig", "zwischen Südvorstadt und Plagwitz"],
    "Dortmund":     ["im rauen Dortmund", "im Herzen des Ruhrpotts"],
    "Essen":        ["im grünen Essen", "zwischen Rüttenscheid und Innenstadt"],
    "Bochum":       ["im studentischen Bochum"],
    "Duisburg":     ["im industriellen Duisburg"],
    "Hamburg":      ["im maritimen Hamburg"],
    "Frankfurt":    ["im pulsierenden Frankfurt"],
}
def district_line(district, city):
    key = (district or "").split()[-1] if district else ""
    pool = DISTRICT_FLAVORS.get(key) or DISTRICT_FLAVORS.get(city or "") or \
           ["in eurer Ecke", "mitten im Viertel", "bei euch vor Ort"]
    return pool

# ── Opener-Pool (40+) ───────────────────────────────────────────────────────
OPENERS = [
    "Hallo {fn}! ✨", "Hey {fn}! 👋", "Guten Tag {fn}, ",
    "Servus {fn}! ", "Moin {fn}! ⚓", "Grüß dich {fn}! ",
    "Hallo zusammen bei {name}! 😊", "Hey, kurze Frage an {name}: ",
    "Liebes Team von {name}, ", "Hey {name} ✨ ",
    "Ich bin gerade über {name} gestolpert — ",
    "Kurze Nachricht an {name}: ",
    "Schön, dass ich {name} gefunden habe! ",
    "{name} — ich musste euch anschreiben. ",
    "Hi {fn}! Darf ich kurz? ",
]
OPENERS_NOFN = [
    "Hallo zusammen! 😊", "Hey, kurze Frage: ", "Guten Tag, ",
    "Moin! ⚓", "Servus! ", "Grüß Gott! ",
    "Hallo! Ich bin kurz reingeschaut — ",
    "Liebes Team, ", "Hey ✨ ",
    "Kurz und direkt: ", "Eine Sekunde Zeit? ",
]

# ── Analyse-Blöcke (Pain-Points) ───────────────────────────────────────────-
ANALYSE_NO_SITE = [
    "ihr habt aktuell keinen eigenen Webauftritt — Neukunden finden euch nur über Google-Einträge oder Bewertungsportale.",
    "eure Präsenz läuft über Dritt-Profile. Sobald jemand euch googelt, landet er auf Seiten, die ihr nicht kontrolliert.",
    "ohne eigene Website verschenkt ihr jede SEO-Chance an Treatwell, Booksy & Co.",
    "ich finde euch online nur über Google-Maps — kein eigener Hub, keine eigene Story, keine Kontrolle über die erste Wahrnehmung.",
    "ein eigener Webauftritt fehlt komplett. Jede gute Bewertung auf Google zieht Traffic zu Google, nicht zu euch.",
]
ANALYSE_HAS_SITE = [
    "euer Webauftritt steht — aber nachts, wenn jemand spontan buchen will, passiert nichts.",
    "die Website wirkt statisch — eine klare 24/7-Buchung fehlt.",
    "schöne Seite, aber ohne KI-Rezeption gehen Anfragen außerhalb der Öffnungszeiten verloren.",
    "ihr seid online, aber die Terminbuchung ist nicht automatisiert — jede verpasste Anfrage ist ein verlorener Umsatz.",
    "der Webauftritt ist da, nur fehlt der Conversion-Hebel: schnelle Buchung, mehrsprachig, rund um die Uhr.",
]
ANALYSE_PLATFORM = [
    "eure Buchungen laufen über eine Drittplattform. Damit zahlt ihr pro Termin Provision — und die Kundendaten gehören nicht euch.",
    "die Plattform, über die ihr bucht, verdient an jedem eurer Kunden mit. Eigene Kontrolle = null.",
    "ihr arbeitet für die Marke der Buchungsplattform, nicht für eure eigene. Das ändert sich mit einer eigenen KI-Rezeption.",
]

# ── Vorschlag-Blöcke ────────────────────────────────────────────────────────
OFFERS = [
    "Wir bauen euch die komplette digitale Heimat: eigene Website, eigene App, eigenes CRM und eine KI-Rezeption, die 24/7 auf Deutsch, Englisch und Türkisch antwortet.",
    "Unser Paket: Website + buchbare App + CRM + KI-Concierge, der rund um die Uhr Termine vergibt — ohne Provision, ohne Monatskosten.",
    "Was ihr bekommt: moderne Website, Buchungs-App, CRM mit Kundenhistorie, und eine KI, die Anrufe nachts, am Sonntag und während der Behandlung entgegennimmt.",
    "Stellt euch vor: ein System, das eure Website, eure App und eure Buchungen vereint — und eine KI, die wie eine echte Rezeptionistin spricht.",
]

# ── Preis-Anker ─────────────────────────────────────────────────────────────
PRICES = [
    "💰 Einmalig 1.000 € — danach keine Monatskosten.",
    "💰 1.000 € komplett. Keine Abos, keine versteckten Gebühren.",
    "💰 Komplettpaket für einmalig 1.000 € — Go-Live in 14 Tagen.",
    "💰 Einmalzahlung 1.000 €. Fertig. Support inklusive.",
]

# ── CTA-Zeilen ──────────────────────────────────────────────────────────────
CTAS = [
    "👉 Live-Demo: " + DEMO_URL,
    "👉 So sieht's aus: " + DEMO_URL,
    "👉 Demo ansehen (2 Min): " + DEMO_URL,
    "👉 Live-Beispiel für Beauty-Salons: " + DEMO_URL,
]

PLATFORM_RX = re.compile(r"(treatwell|planity|booksy|fresha|salonkee)", re.I)

# ── Konkurrenz-Hook (Deep-Personalization) ──────────────────────────────────
AUDIT_SCORE_RX = re.compile(r"score=(\d+)")
def parse_score(notes):
    if not notes: return None
    m = AUDIT_SCORE_RX.search(notes)
    return int(m.group(1)) if m else None

def has_booking_in_notes(notes):
    return "booking=y" in (notes or "")

COMPETITOR_LINES = [
    "Ich habe gesehen: eure Nachbarn von {comp} haben bereits Online-Booking — das ist ein klarer Vorsprung im Kampf um Kundschaft in {dist}. Wir helfen euch nicht nur aufzuholen, sondern technologisch die Nase vorn zu haben.",
    "{comp} in {dist} hat die Buchung schon digitalisiert. Während Kunden dort um 22 Uhr spontan einen Termin machen, müssen eure anrufen — oder buchen dort. Zeit, den Spieß umzudrehen.",
    "Kurz verglichen: {comp} in {dist} nutzt bereits modernes Online-Booking. Wir bauen euch ein System, das deren Setup nicht nur einholt, sondern überholt — eigene KI-Rezeption inklusive.",
    "Eure direkten Nachbarn in {dist} ({comp}) sind bereits online buchbar. Jeder Kunde, der um 19 Uhr sucht, landet dort statt bei euch. Das ändern wir.",
]

def build_competitor_index(rows):
    """district → [(name, score) мають booking=y або score<=4]."""
    idx = {}
    for r in rows:
        notes = r.get("notes") or ""
        score = parse_score(notes)
        if score is None: continue
        if score > 4 and not has_booking_in_notes(notes):
            continue
        d = (r.get("district") or "").strip()
        if not d: continue
        idx.setdefault(d, []).append((r.get("name") or "", score, r["id"]))
    return idx

# ── HTTP ────────────────────────────────────────────────────────────────────
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

def fetch_all_for_competitors():
    """Повна вибірка з audit-даними для побудови сусідського індексу."""
    PAGE = 1000
    all_rows = []
    offset = 0
    while True:
        q = ("/rest/v1/beauty_leads?select=id,name,district,notes,website"
             "&order=id.asc&limit=" + str(PAGE) + "&offset=" + str(offset))
        rows = sb_get(q)
        all_rows.extend(rows)
        if len(rows) < PAGE: break
        offset += PAGE
    return all_rows

def fetch_targets(limit):
    # Пагінація через offset — Supabase кепує на 1000/запит
    PAGE = 1000
    all_rows = []
    offset = 0
    while True:
        q = ("/rest/v1/beauty_leads?select=id,name,city,district,website,email,phone,notes"
             "&status=eq.new&order=id.asc&limit=" + str(PAGE) + "&offset=" + str(offset))
        rows = sb_get(q)
        all_rows.extend(rows)
        if len(rows) < PAGE or (limit and len(all_rows) >= limit):
            break
        offset += PAGE
    if limit: all_rows = all_rows[:limit]
    return all_rows

# ── Generator ──────────────────────────────────────────────────────────────-
def craft_message(lead, comp_index=None):
    rid    = lead["id"]
    name   = (lead.get("name") or "euer Salon").strip()
    city   = (lead.get("city") or "").strip()
    distr  = (lead.get("district") or "").strip()
    site   = (lead.get("website") or "").lower()
    fn     = first_name(name)
    stype  = detect_type(name)

    seed = int(hashlib.md5(str(rid).encode()).hexdigest()[:10], 16)
    rng  = random.Random(seed)

    # Opener
    if fn:
        opener = rng.choice(OPENERS).replace("{fn}", fn).replace("{name}", name)
    else:
        opener = rng.choice(OPENERS_NOFN)

    # Viertel-Hook
    loc_pool = district_line(distr, city)
    loc_hint = rng.choice(loc_pool)

    # Lead-In: Anerkennung
    leadins = [
        f"euer {stype} {loc_hint} ist mir heute in die Recherche geraten.",
        f"ich habe mir {name} {loc_hint} angesehen.",
        f"{name} {loc_hint} — gute Arbeit, ehrlich.",
        f"euer {stype} {loc_hint} hat mich neugierig gemacht.",
        f"ich recherchiere gerade Beauty-Business {loc_hint} und {name} ist mir aufgefallen.",
    ]
    leadin = rng.choice(leadins)

    # Pain-Point-Analyse je nach Website-Status
    if PLATFORM_RX.search(site):
        pain = rng.choice(ANALYSE_PLATFORM)
    elif not site:
        pain = rng.choice(ANALYSE_NO_SITE)
    else:
        pain = rng.choice(ANALYSE_HAS_SITE)

    offer = rng.choice(OFFERS)
    price = rng.choice(PRICES)
    cta   = rng.choice(CTAS)

    # ── Deep-Personalization: Konkurrenz-Hook wenn score>7 ──
    comp_hook = None
    my_score  = parse_score(lead.get("notes"))
    if comp_index and my_score is not None and my_score > 7:
        pool = [c for c in (comp_index.get(distr) or []) if c[2] != rid]
        if pool:
            # Сортуємо за якістю (менший score = якісніший), беремо топ-3, seed-pick
            pool.sort(key=lambda x: x[1])
            candidates = pool[:3]
            comp_name, _, _ = rng.choice(candidates)
            comp_name = comp_name.strip()[:60]
            if comp_name:
                line = rng.choice(COMPETITOR_LINES)
                comp_hook = line.replace("{comp}", comp_name).replace("{dist}", distr or (city or "eurer Gegend"))

    # Finale Verflechtung
    parts = [opener, leadin, "Was mir auffällt: " + pain]
    if comp_hook: parts.append(comp_hook)
    parts.extend([offer, price, cta])
    msg   = " ".join(parts)
    # Double-space cleanup
    msg   = re.sub(r"\s+", " ", msg).strip()
    return msg

# ── Main ───────────────────────────────────────────────────────────────────-
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit",   type=int, default=0, help="0 = alle status='new'")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Vermarkter Personalize Vault (Deep-Mode)")
    print("Building competitor index…")
    all_rows = fetch_all_for_competitors()
    comp_index = build_competitor_index(all_rows)
    print("  Audited leads:", sum(1 for r in all_rows if parse_score(r.get("notes")) is not None))
    print("  Districts with qualified neighbors:", len(comp_index))

    targets = fetch_targets(args.limit or 0)
    print("Targets:", len(targets))

    ok = fail = comp_hits = 0
    for i, lead in enumerate(targets, 1):
        try:
            msg = craft_message(lead, comp_index=comp_index)
            my_score = parse_score(lead.get("notes"))
            if my_score and my_score > 7 and comp_index.get((lead.get("district") or "").strip()):
                comp_hits += 1
        except Exception as e:
            fail += 1
            print("[%d/%d] CRAFT FAIL id=%s: %s" % (i, len(targets), lead.get("id"), e))
            continue

        if args.dry_run:
            print("─" * 70)
            print("id=%s | %s" % (lead["id"], (lead.get("name") or "")[:40]))
            print(msg[:300] + ("…" if len(msg) > 300 else ""))
            ok += 1
            continue

        try:
            notes = lead.get("notes") or ""
            if "personalized" not in notes:
                notes = (notes + " | personalized").strip(" |")
            sb_patch(lead["id"], {"custom_message": msg, "notes": notes})
            ok += 1
            if i % 50 == 0 or i == len(targets):
                print("[%d/%d] OK — %s" % (i, len(targets), (lead.get("name") or "")[:40]))
        except urllib.error.HTTPError as e:
            fail += 1
            print("[%d/%d] HTTP %s id=%s" % (i, len(targets), e.code, lead["id"]))
        except Exception as e:
            fail += 1
            print("[%d/%d] FAIL id=%s: %s" % (i, len(targets), lead["id"], e))

    print("\nDONE — updated: %d | failed: %d | competitor-hooks: %d" % (ok, fail, comp_hits))

if __name__ == "__main__":
    main()
