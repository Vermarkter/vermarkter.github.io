# -*- coding: utf-8 -*-
"""
lead_harvester.py — Total Germany Beauty Database
==================================================
Збирає салони краси з Google Maps по списку поштових індексів (PLZ),
збагачує даними (телефон, сайт, email) та записує в Supabase beauty_leads.

Дедуплікація: канонічний maps_url містить place_id → впізнаємо існуючі записи.
Якщо запис існує — PATCH (оновлення); якщо ні — POST (вставка).

Персоналізація: одразу генерує унікальне DE-повідомлення (Gold Master) і
зберігає в custom_message.

Запуск:
    python lead_harvester.py 10115 10117 10178 10179
"""

import sys, io, time, re, json, hashlib, random, configparser, os
import urllib.request, urllib.parse, urllib.error
import ssl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Credentials (config.ini) ─────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding="utf-8")
GMAPS_KEY = _cfg["CREDENTIALS"]["gmaps_key"]
SB_URL    = _cfg["CREDENTIALS"]["supabase_url"]
SB_KEY    = _cfg["CREDENTIALS"]["supabase_key"]

SB_HEAD   = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
             "Content-Type": "application/json"}

KEYWORDS  = ["Friseur", "Barbershop", "Kosmetikstudio", "Nagelstudio"]
PAUSE_API = 0.25
HTTP_CTX  = ssl.create_default_context()
HTTP_CTX.check_hostname = False
HTTP_CTX.verify_mode    = ssl.CERT_NONE

DEMO_URL  = "https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"

# ── Helpers: HTTP ─────────────────────────────────────────────────────────────
def safe(s, n=60):
    if s is None: return ""
    return str(s)[:n].encode("ascii", "replace").decode("ascii")

def http_get(url, timeout=8, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=HTTP_CTX) as r:
        return r.read()

def gmaps_get(endpoint, params):
    params = dict(params); params["key"] = GMAPS_KEY
    url = "https://maps.googleapis.com/maps/api/" + endpoint + "?" + urllib.parse.urlencode(params)
    raw = http_get(url, timeout=15).decode("utf-8")
    return json.loads(raw)

def sb_get(path):
    req = urllib.request.Request(SB_URL + path, headers=SB_HEAD)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def sb_write(method, path, payload, prefer="return=representation"):
    body = json.dumps(payload).encode("utf-8")
    h    = dict(SB_HEAD); h["Prefer"] = prefer
    req  = urllib.request.Request(SB_URL + path, data=body, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read().decode("utf-8")
            return r.status, json.loads(data) if data else None
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

# ── Google Maps: text search + place details ─────────────────────────────────
def maps_text_search(query):
    """Повертає всі результати з пагінацією (до 60 місць)."""
    results = []
    params  = {"query": query, "language": "de", "region": "de"}
    for _ in range(3):  # max 3 сторінки = 60 results
        data = gmaps_get("place/textsearch/json", params)
        results.extend(data.get("results", []))
        token = data.get("next_page_token")
        if not token: break
        time.sleep(2.0)  # next_page_token потребує паузу
        params = {"pagetoken": token}
    return results

def place_details(place_id):
    fields = "name,formatted_address,formatted_phone_number,international_phone_number,website,rating,user_ratings_total,types,url"
    data   = gmaps_get("place/details/json", {"place_id": place_id, "fields": fields, "language": "de"})
    return data.get("result", {})

# ── Email scraping ───────────────────────────────────────────────────────────
EMAIL_RX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
BAD_EMAIL = re.compile(r"\.(png|jpg|jpeg|gif|webp|svg|css|js|woff|woff2|ttf)$", re.I)

def scrape_email(website):
    if not website: return None
    candidates = [website]
    base = website.rstrip("/")
    candidates.extend([base + p for p in ("/impressum","/kontakt","/imprint","/contact")])
    found = []
    for url in candidates[:5]:
        try:
            html = http_get(url, timeout=6).decode("utf-8", errors="ignore")
        except Exception:
            continue
        # mailto first
        for m in re.finditer(r'mailto:([^"\'\s>]+)', html, re.I):
            e = m.group(1).split("?")[0].strip()
            if e and not BAD_EMAIL.search(e): found.append(e)
        # plaintext
        for m in EMAIL_RX.finditer(html):
            e = m.group(0).strip()
            if e and not BAD_EMAIL.search(e) and "sentry" not in e.lower() and "wixpress" not in e.lower():
                found.append(e)
        if found: break
    if not found: return None
    # prefer info@ / kontakt@ / hallo@
    for pref in ("info@","kontakt@","hallo@","mail@","office@"):
        for e in found:
            if e.lower().startswith(pref): return e.lower()
    return found[0].lower()

# ── DE message generator (Gold Master) ───────────────────────────────────────
PLATFORM_RX = re.compile(r"(treatwell|planity|booksy|fresha|salonkee)", re.I)

OPENERS = [
    "Hallo! 😄 ", "Hey! 👋 ", "Guten Tag! ✨ ", "Hallo zusammen! 😄 ",
    "Servus! 👋 ", "Moin! 😄 ",
]

def first_name(name):
    # Витягуємо ім'я з назви салону, якщо очевидно (Friseur Mehmet → Mehmet)
    m = re.search(r"\b(?:Friseur|Salon|Barbier|Studio|by|von)\s+([A-ZÄÖÜ][a-zäöüß]+)", name)
    return m.group(1) if m else None

def gen_message(rec):
    """rec: dict with name, website, rating, user_ratings_total, district, phone."""
    seed   = int(hashlib.md5((rec["place_id"] or rec["name"]).encode()).hexdigest()[:8], 16)
    rng    = random.Random(seed)
    name   = rec["name"]
    site   = (rec.get("website") or "").lower()
    rating = rec.get("rating") or 0
    nrev   = rec.get("user_ratings_total") or 0
    fn     = first_name(name)
    greet  = rng.choice(OPENERS)
    if fn: greet = greet.replace("Hallo!", "Hallo " + fn + "!").replace("Hey!", "Hey " + fn + "!")

    # Сигнал: яка платформа використовується
    plat_match = PLATFORM_RX.search(site)
    has_site   = bool(rec.get("website"))

    if plat_match:
        plat = plat_match.group(1).capitalize()
        body = (f"{name} — schön, dass du online buchbar bist. Aber ich sehe: "
                f"deine Buchungen laufen über {plat}. Du baust deren Marke auf, nicht deine eigene, "
                f"und zahlst Provision pro Termin. Mit unserer eigenen KI-Rezeption gehört "
                f"die Kundin DIR — direkter Draht, null Provision, 24/7 Buchung.")
    elif not has_site:
        if rating >= 4.7 and nrev >= 30:
            body = (f"Top-Bewertungen ({rating}★, {nrev} Reviews) — du machst echt gute Arbeit. "
                    f"Aber ohne eigene Website findet dich neuer Kundschaft fast nur über Google. "
                    f"Wir bauen dir deine eigene digitale Heimat: Website + App + KI-Rezeption.")
        else:
            body = (f"Ich sehe: kein eigener Webauftritt für {name}. Wer dich googelt, "
                    f"landet auf Bewertungsportalen, nicht auf DIR. Zeit für deine eigene "
                    f"Online-Präsenz mit 24/7 KI-Rezeption.")
    elif rating >= 4.8 and nrev >= 50:
        body = (f"{rating}★ bei {nrev} Bewertungen — {name} ist eine Institution. "
                f"Aber wer nachts oder am Sonntag buchen will, erreicht euch nur per Telefon. "
                f"Unsere KI-Rezeption empfängt diese Kunden 24/7 — auf Deutsch, Englisch und Türkisch.")
    elif rating and rating < 4.3:
        body = (f"Ich sehe Potenzial bei {name}. Eine moderne Website mit klarer Buchung und "
                f"KI-Rezeption verbessert nicht nur die Conversion — sie hebt euch sofort von "
                f"der Konkurrenz im Viertel ab.")
    else:
        body = (f"{name} hat eine schöne Online-Präsenz. Aber wer abends spontan einen Termin will, "
                f"muss anrufen — und ruft im Zweifel nicht zurück. Mit unserer KI-Rezeption "
                f"bucht der Kunde sofort, automatisch, in jeder Sprache.")

    pkg  = rng.choice([
        "💰 Komplettpaket (Website + App + CRM + KI) für einmalig 1.000 €. Keine Monatskosten.",
        "💰 Alles inklusive (Website + App + CRM + KI-Rezeption): einmalig 1.000 €.",
        "💰 1.000 € einmalig — Website, App, CRM und KI in einem Paket.",
    ])
    return greet + body + " " + pkg + " 👉 " + DEMO_URL

# ── Supabase upsert ──────────────────────────────────────────────────────────
def canon_maps_url(place_id):
    return "https://www.google.com/maps/place/?q=place_id:" + place_id

def find_existing(maps_url):
    q = "/rest/v1/beauty_leads?select=id&maps_url=eq." + urllib.parse.quote(maps_url, safe="")
    rows = sb_get(q)
    return rows[0]["id"] if rows else None

def upsert_lead(rec):
    payload = {
        "name":           rec["name"],
        "city":           rec["city"],
        "phone":          rec.get("phone"),
        "email":          rec.get("email"),
        "website":        rec.get("website"),
        "district":       rec.get("district"),
        "maps_url":       rec["maps_url"],
        "status":         "new",
        "custom_message": rec["custom_message"],
    }
    existing_id = find_existing(rec["maps_url"])
    if existing_id:
        # PATCH без перезапису ручних правок: оновлюємо лише пусті поля + дані з Maps
        patch = {k:v for k,v in payload.items() if v is not None and k != "status"}
        sb_write("PATCH", "/rest/v1/beauty_leads?id=eq." + str(existing_id),
                 patch, prefer="return=minimal")
        return "updated", existing_id
    code, resp = sb_write("POST", "/rest/v1/beauty_leads", [payload])
    if code in (200, 201):
        new_id = resp[0]["id"] if isinstance(resp, list) and resp else None
        return "inserted", new_id
    return "error:" + str(code), None

# ── District extractor ───────────────────────────────────────────────────────
def parse_district(formatted_address, plz):
    """Beispiel: 'Friedrichstr. 1, 10117 Berlin' → ('Berlin', 'Mitte')."""
    parts = [p.strip() for p in formatted_address.split(",")]
    city  = "Berlin"
    for p in parts:
        if re.search(r"\b\d{5}\b", p):
            tokens = p.split()
            for i,t in enumerate(tokens):
                if re.match(r"\d{5}", t) and i+1 < len(tokens):
                    city = " ".join(tokens[i+1:])
                    break
    plz_to_district = {
        "10115":"Berlin Mitte","10117":"Berlin Mitte",
        "10178":"Berlin Mitte","10179":"Berlin Mitte",
        "10777":"Berlin Schöneberg","10779":"Berlin Schöneberg",
        "10781":"Berlin Schöneberg","10783":"Berlin Schöneberg",
        "10823":"Berlin Schöneberg","10825":"Berlin Schöneberg",
        "10827":"Berlin Schöneberg","10829":"Berlin Schöneberg",
        "12163":"Berlin Steglitz","12165":"Berlin Steglitz",
        "12167":"Berlin Steglitz","12169":"Berlin Steglitz",
        "14163":"Berlin Zehlendorf","14165":"Berlin Zehlendorf",
        "14167":"Berlin Zehlendorf","14169":"Berlin Zehlendorf",
        "14193":"Berlin Grunewald","14195":"Berlin Dahlem",
        "14197":"Berlin Schmargendorf","14199":"Berlin Grunewald",
    }
    if plz in plz_to_district:
        return city, plz_to_district[plz]
    # Немає в мапі — використовуємо розпізнане з адреси місто як район
    return city, city

# ── Main ─────────────────────────────────────────────────────────────────────
def harvest(plz_list):
    seen_ids = set()
    inserted = updated = errors = 0

    # Prefix-based city hint (щоб запит до Google Maps не містив "Berlin" для інших міст)
    plz_prefix_city = {
        "04":"Leipzig","10":"Berlin","12":"Berlin","14":"Berlin",
        "20":"Hamburg","22":"Hamburg","28":"Bremen","30":"Hannover",
        "40":"Düsseldorf","50":"Köln","60":"Frankfurt",
        "70":"Stuttgart","80":"München",
    }
    plz_prefix3_city = {
        "441":"Dortmund","447":"Bochum",
        "451":"Essen","470":"Duisburg","471":"Duisburg",
    }
    for plz in plz_list:
        print("\n" + "="*60)
        print("PLZ %s — Suche..." % plz)
        city_hint = plz_prefix3_city.get(plz[:3]) or plz_prefix_city.get(plz[:2], "Deutschland")
        for kw in KEYWORDS:
            query = "%s %s %s" % (kw, plz, city_hint)
            print("  > %s" % query, end=" ", flush=True)
            try:
                results = maps_text_search(query)
            except Exception as e:
                print("FAIL:", e); continue
            print("→ %d Treffer" % len(results))
            for r in results:
                pid = r.get("place_id")
                if not pid or pid in seen_ids: continue
                seen_ids.add(pid)

                try:
                    d = place_details(pid)
                except Exception as e:
                    print("    [details fail %s] %s" % (safe(r.get("name")), e))
                    continue
                time.sleep(PAUSE_API)

                name = d.get("name") or r.get("name") or ""
                addr = d.get("formatted_address") or r.get("formatted_address") or ""
                phone= d.get("international_phone_number") or d.get("formatted_phone_number")
                site = d.get("website")
                rate = d.get("rating")
                nrev = d.get("user_ratings_total")
                city, district = parse_district(addr, plz)

                email = None
                if site:
                    try:
                        email = scrape_email(site)
                    except Exception:
                        email = None

                rec = {
                    "place_id": pid,
                    "name": name, "city": city, "district": district,
                    "phone": phone, "email": email, "website": site,
                    "rating": rate, "user_ratings_total": nrev,
                    "maps_url": canon_maps_url(pid),
                }
                rec["custom_message"] = gen_message(rec)

                try:
                    action, _id = upsert_lead(rec)
                except Exception as e:
                    print("    [upsert fail %s] %s" % (safe(name), e))
                    errors += 1; continue

                tag = "INS" if action == "inserted" else ("UPD" if action == "updated" else "ERR")
                print("    [%s] %s | tel=%s mail=%s site=%s" % (
                    tag, safe(name, 35),
                    "y" if phone else "-",
                    "y" if email else "-",
                    "y" if site  else "-"))
                if action == "inserted": inserted += 1
                elif action == "updated": updated += 1
                else: errors += 1

    return inserted, updated, errors, len(seen_ids)

if __name__ == "__main__":
    plz_list = sys.argv[1:] if len(sys.argv) > 1 else ["10115","10117","10178","10179"]
    print("Total Germany Beauty Database — Harvester")
    print("PLZ-Pakete: " + ", ".join(plz_list))
    t0 = time.time()
    ins, upd, err, total = harvest(plz_list)
    dt = time.time() - t0
    print("\n" + "="*60)
    print("FERTIG за %.1fs" % dt)
    print("Унікальні place_id оброблено: %d" % total)
    print("  Додано нових:    %d" % ins)
    print("  Оновлено:        %d" % upd)
    print("  Помилки:         %d" % err)
