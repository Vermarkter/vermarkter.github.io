# -*- coding: utf-8 -*-
"""
bulk_patch_messages.py — Batch 10 (20 Schwabing/Zentrum salons)
"""
import json, urllib.request, urllib.parse, configparser, os, sys, io, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'), encoding='utf-8')
SB_URL = _cfg['SUPABASE']['url']
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and '\u0412\u0421\u0422\u0410\u0412\u0418\u0422\u0418' not in _svc and 'PASTE' not in _svc) \
         else _cfg['SUPABASE']['anon_key']
print('[INFO] key role:', 'service_role' if SB_KEY == _svc else 'anon')

HDRS = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
    'Prefer':        'return=minimal'
}

MESSAGES = [
    {"name": "BULLFROG Barbershop",
     "custom_message": "Hallo! \U0001f60a BULLFROG in M\u00fcnchen-Zentrum \u2014 internationales Konzept, Luxury Shaving. Aber ich sehe: Terminanfragen laufen \u00fcber E-Mail. F\u00fcr ein Premium-Haus ist das unter eurem Niveau. Wir integrieren eine KI-Rezeption, die 24/7 bucht und euer Angebot erkl\u00e4rt. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Barber House Glockenbachviertel",
     "custom_message": "Hallo! \U0001f60a Barber House \u2014 stilvolles Ambiente, treue Kundschaft. Aber ich sehe: Eure Buchung l\u00e4uft \u00fcber externe Tools. Wir bauen euch eine eigene KI-Rezeption \u2014 komplett in eurer Marke, 24/7 erreichbar. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "BABACUT Hair Salon",
     "custom_message": "Hallo! \U0001f60a Zwei Standorte in M\u00fcnchen, Dyson-Produkte \u2014 BABACUT ist top! Aber ich sehe: Online-Buchung funktioniert nicht \u00fcber die eigene Seite. Verlorene Termine, jeden Tag. Wir l\u00f6sen das: KI-Rezeption f\u00fcr beide Standorte, 24/7-Buchung. \U0001f4b0 1.000\u00a0\u20ac pro Standort. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "The Goat Barbershop",
     "custom_message": "Hallo! \U0001f60a The Goat \u2014 professionelles Team! Aber ich sehe: keine eigene App, keine KI-Rezeption, die nachts Fragen beantwortet. Das macht gerade die Konkurrenz. Unsere Komplettl\u00f6sung: KI-Rezeption + App f\u00fcr 24/7-Buchungen. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "MUNICH HAIR STYLE",
     "custom_message": "Hallo! \U0001f60a Munich Hair Style an der Lindwurmstra\u00dfe \u2014 starker Ruf! Aber ich sehe: keine eigene Website, keine Online-Buchung. Wer euch googelt, findet fast nichts. Unsere Komplettl\u00f6sung: Website + App + KI-Rezeption f\u00fcr 24/7. \U0001f4b0 1.000\u00a0\u20ac, startklar in 2 Wochen. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Black Betty The Barbershop",
     "custom_message": "Hallo! \U0001f60a Black Betty \u2014 echt cooler Charakter! Aber ich sehe: keine Online-Buchung. Wer euch abends findet, muss anrufen. Das kostet euch t\u00e4glich Neukunden. Wir l\u00f6sen das: KI-Rezeption, die 24/7 Termine annimmt. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "s&bHairlounge",
     "custom_message": "Hallo! \U0001f60a 5,0 Sterne bei Google \u2014 absolute Topklasse! Aber ich sehe: f\u00fcr ein Studio auf diesem Niveau fehlt die eigene KI-Rezeption, die Kundinnen auch um Mitternacht empf\u00e4ngt. Das bauen wir euch: Website + App + KI f\u00fcr 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Barber Sascha Siemon",
     "custom_message": "Hallo Sascha! \U0001f60a Du bist in den M\u00fcnchner Top-10. Zurecht! Aber ich sehe: keine Website, keine Online-Buchung. Wer dich sucht, muss anrufen. Das ist zu wenig f\u00fcr dein Niveau. Wir bauen dir eine KI-Rezeption f\u00fcr 24/7-Buchungen. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "GK Haircut",
     "custom_message": "Hallo G\u00f6ksel! \U0001f60a An der Leopoldstra\u00dfe eine feste Gr\u00f6\u00dfe! Aber ich sehe: keine eigene Website \u2014 nur Treatwell. Du zahlst Provision f\u00fcr jeden Termin. Wir bieten dir eine eigene digitale Heimat: Website + App + KI-Rezeption. Die Kundin geh\u00f6rt dir. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "CUT MUNICH Friseur",
     "custom_message": "Hallo! \U0001f60a 5,0 Sterne in Schwabing! Aber ich sehe: keine Online-Buchung auf eurer Seite. In Schwabing erwarten die Leute mehr Komfort. Wir bauen euch eine KI-Rezeption, die 24/7 bucht und eure Kunden bei euch h\u00e4lt. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Hobby Friseur",
     "custom_message": "Hallo Reza! \U0001f60a Dein Team erreicht ganz Schwabing! Aber ich sehe: keine eigene Website \u2014 nur Treatwell. Die Provision geht an Fremde. Unsere Komplettl\u00f6sung: Website + App + KI-Rezeption f\u00fcr 24/7-Buchungen. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Beverly Hills Hair Style",
     "custom_message": "Hallo Frau Amiry! \U0001f60a 15 Jahre Stammkunden \u2014 Respekt! Aber ich sehe: keine Online-Buchung. Wer euch abends findet, geht weiter zur Konkurrenz. Wir l\u00f6sen das: KI-Rezeption, die 24/7 bucht \u2014 direkt auf eurer Website. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Hair Lounge Schwabing",
     "custom_message": "Hallo! \U0001f60a Hair Lounge \u2014 tolle Lage! Aber ich sehe: keine eigene Website, keine direkte Buchung. Wer euch sucht, landet beim Salon zwei Qu\u00e4rtale weiter. Unsere Komplettl\u00f6sung: Website + App + KI-Rezeption. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Pony Club",
     "custom_message": "Hallo! \U0001f60a 7 Standorte \u2014 eine echte Institution! Aber ich sehe: zu viele manuelle Schritte. Wir integrieren eine KI-Rezeption, die alle Filialen synchronisiert \u2014 24/7, automatisch. \U0001f4b0 1.000\u00a0\u20ac pro Standort. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Sanaz Beauty Lounge",
     "custom_message": "Hallo Sanaz! \U0001f60a 15 Jahre Erfahrung \u2014 echte St\u00e4rke! Aber ich sehe: keine eigene Website \u2014 nur Treatwell. Du baust ihre Plattform auf, statt deinen Brand. Wir geben dir deine eigene digitale Heimat mit KI-Rezeption. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Friseursalon Hairworld",
     "custom_message": "Hallo! \U0001f60a Seit Jahren eine feste Adresse, aber ich sehe: kein Online-Buchungssystem. Die Studierenden hier wollen nicht anrufen, sondern tippen. Wir geben euch eine KI-Rezeption, die 24/7 arbeitet. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "NEW CUT HAIRSTYLING",
     "custom_message": "Hallo! \U0001f60a Modisch up-to-date! Aber ich sehe: Wer einen Termin will, muss anrufen. In einem Kiez voller Digital Natives ist das ein No-Go. Unsere Komplettl\u00f6sung: Website + App + KI-Rezeption. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Royal Friseur",
     "custom_message": "Hallo! \U0001f60a 5,0 Sterne \u2014 der Name h\u00e4lt, was er verspricht! Aber ich sehe: keine Online-Buchung. Wer spontan abends buchen m\u00f6chte, kann das nicht. Wir geben euch eine KI-Rezeption f\u00fcr 24/7-Buchungen. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Paris Friseur",
     "custom_message": "Hallo! \U0001f60a Toller Standort am Kurfürstenplatz! Aber ich sehe: keine direkte Online-Buchung auf eurer Seite. In Schwabing erwarten Kundinnen genau das. Unsere Komplettl\u00f6sung: Website + App + KI-Rezeption. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
    {"name": "Georgis Friseure",
     "custom_message": "Hallo! \U0001f60a Verl\u00e4ssliche Qualit\u00e4t in Schwabing! Aber ich sehe: keine eigene Website. Neukunden suchen zuerst online \u2014 wer dort nicht vertreten ist, verliert an die Konkurrenz. Wir bauen euch das komplett: Website + App + KI-Rezeption. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/services/beauty-industry/de/"},
]

def sb_search(name):
    encoded = urllib.parse.quote(name, safe='')
    url = SB_URL + '/rest/v1/beauty_leads?select=id,name&name=ilike.*' + encoded + '*&limit=5'
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode('utf-8'))

def sb_patch(lead_id, msg):
    body = json.dumps({'custom_message': msg}).encode('utf-8')
    url  = SB_URL + '/rest/v1/beauty_leads?id=eq.' + str(lead_id)
    req  = urllib.request.Request(url, data=body, headers=HDRS, method='PATCH')
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status

ok = fail = not_found = 0
print('Starting bulk PATCH (%d items)...\n' % len(MESSAGES))

for item in MESSAGES:
    name = item['name']
    msg  = item['custom_message']
    try:
        results = sb_search(name)
        if not results:
            print('[NOT FOUND] %s' % name)
            not_found += 1
            continue
        lead = results[0]
        sb_patch(lead['id'], msg)
        print('[OK] id=%-6s  %s' % (lead['id'], lead['name'][:50]))
        ok += 1
        time.sleep(0.15)
    except Exception as e:
        print('[ERROR] %s: %s' % (name, e))
        fail += 1

print('\n' + '\u2500' * 29)
print('Done \u2014 updated: %d | not found: %d | errors: %d' % (ok, not_found, fail))
