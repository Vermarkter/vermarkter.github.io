# -*- coding: utf-8 -*-
"""
bulk_patch_messages.py — Оновлює custom_message у beauty_leads за name (ilike)
"""
import json, urllib.request, urllib.parse, configparser, os, sys, io, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── Credentials ──────────────────────────────────────────────────────────────
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

# ── Messages to patch ─────────────────────────────────────────────────────────
MESSAGES = [
    {"name": "Almas Barbershop",
     "custom_message": "Hallo! \U0001f60a Almas Barbershop an der Zweibr\u00fcckenstra\u00dfe \u2014 5,0 Sterne, perfekte Qualit\u00e4t! Aber ich sehe: keine Online-Buchung. Jeder Anruf w\u00e4hrend des Schnitts st\u00f6rt den Fokus auf den Kunden. Wir geben euch eine KI-Rezeption, die 24/7 f\u00fcr euch antwortet und bucht. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Next Level Barber Shop",
     "custom_message": "Hallo! \U0001f60a \u201eNext Level\u201c ist ein Versprechen. Aber beim Booking seid ihr noch auf dem alten Level. Wer abends sucht, will sofort per Chat buchen. Unsere KI-Rezeption bringt eure Infrastruktur auf 5-Sterne-Niveau. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Barbershop by ben",
     "custom_message": "Hallo Ben! \U0001f60a \u201eBy ben\u201c ist pers\u00f6nlich und top bewertet. Aber wenn das Telefon klingelt, w\u00e4hrend du schneidest, verlierst du Neukunden. Unsere KI-Rezeption \u00fcbernimmt das Management im Chat, damit du dich voll auf dein Handwerk konzentrieren kannst. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Vits. Barbery",
     "custom_message": "Hallo! \U0001f60a Vits. Barbery steht f\u00fcr Stil. In zentraler Lage suchen Kunden Professionalit\u00e4t \u2014 auch digital. Wer bei euch nicht sofort online buchen kann, geht zur Konkurrenz. Unsere KI-Rezeption sichert euch diese Termine 24/7. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Barber Handwerk",
     "custom_message": "Hallo! \U0001f60a Wahres Handwerk braucht Fokus. Aber st\u00e4ndige Telefonanrufe unterbrechen die Arbeit. Wir bauen euch eine KI-Rezeption, die Buchungen per Chat \u00fcbernimmt, w\u00e4hrend ihr im Stuhl gl\u00e4nzt. Einmalig 1.000\u00a0\u20ac, keine Monatskosten. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Gentleman Premium Barbershop",
     "custom_message": "Hallo! \U0001f60a Premium-Service f\u00e4ngt beim ersten Klick an. Ein Gentleman wartet nicht auf den R\u00fcckruf \u2014 er bucht per App. Wir integrieren eine KI-Rezeption, die so exklusiv arbeitet wie euer Team. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "KIDA RAMADAN Barbershop",
     "custom_message": "Hallo Kida! \U0001f60a Dein Name ist eine Marke in Schwabing. Aber wer dich googelt, muss anrufen. In einem Kiez voller Young Professionals ist das eine H\u00fcrde. Wir geben dir deine eigene KI-Rezeption f\u00fcr 24/7-Buchungen per Chat. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Friseursalon Hairworld",
     "custom_message": "Hallo! \U0001f60a Mitten im Uni-Viertel suchen Studierende Termine um Mitternacht per Handy. Wer da nicht digital buchbar ist, verliert diese Zielgruppe. Unsere KI-Rezeption macht die Hairworld von morgen 24/7 bereit. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Dilon & Sam \u2013 Die Barbiere",
     "custom_message": "Hallo Dilon, hallo Sam! \U0001f60a Zwei Barbiere, ein tolles Konzept! Aber die Koordination von zwei Kalendern kostet Zeit. Unsere KI-Rezeption synchronisiert eure Termine automatisch per Chat, 24/7. Einmalig 1.000\u00a0\u20ac, kein Abo. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Barberella Maxvorstadt",
     "custom_message": "Hallo! \U0001f60a Barberella hat Kult-Status! Aber warum verdient Treatwell an eurer Bekanntheit mit? Jede Buchung \u00fcber eure eigene KI-Rezeption geh\u00f6rt zu 100% euch. Holt euch eure Unabh\u00e4ngigkeit zur\u00fcck f\u00fcr 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "KEN NYN \u2013 Art of Hair",
     "custom_message": "Hallo! \U0001f60a Kunst am Haar braucht eine digitale Visitenkarte auf Augenh\u00f6he. Aber ich sehe: keine KI-Rezeption. Wer abends sucht, findet bei euch keinen direkten Weg. Wir bauen euch ein High-End System, das so elegant ist wie euer Salon. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "HDHaircut",
     "custom_message": "Hallo! \U0001f60a High Definition beim Schnitt, aber Standard beim Booking? Wer per Telefon buchen muss, erlebt keine HD-Erfahrung von Anfang an. Unsere KI-Rezeption bringt High Definition in euer Terminmanagement. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Azad Friseur",
     "custom_message": "Hallo! \U0001f60a \u201eAzad\u201c bedeutet frei. Aber bist du frei, wenn das Telefon st\u00e4ndig klingelt? Unsere KI-Rezeption \u00fcbernimmt das Buchen per Chat, damit du dich auf das Wesentliche konzentrieren kannst. Einmalig 1.000\u00a0\u20ac, fertig. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "G\u00fcl\u015fen Tasch AVEDA SALON",
     "custom_message": "Hallo G\u00fcl\u015fen! \U0001f60a Dein AVEDA-Konzept ist Premium. Deine Kunden w\u00e4hlen bewusst Qualit\u00e4t. Ein moderner Buchungsprozess per Chat ist f\u00fcr dieses Klientel ein Muss. Wir bauen dir die exklusive KI-Rezeption f\u00fcr einmalig 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Barber House Flughafen",
     "custom_message": "Hallo! \U0001f60a Ein Salon am Flughafen braucht 24/7 digitale Pr\u00e4senz. Piloten und internationale G\u00e4ste buchen spontan auf dem Weg zum Gate. Wir geben euch die KI-Rezeption auf DE/EN, die Termine ohne Anrufe sichert. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Paris Barbershop Erding",
     "custom_message": "Hallo! \U0001f60a Erding w\u00e4chst, aber wer dich googelt, muss oft noch anrufen. Der erste Salon in Erding, der 24/7 KI-Booking per Chat anbietet, gewinnt das Rennen um die Neukunden. Sei dieser Leader f\u00fcr einmalig 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Kolmikov's Barber Shop",
     "custom_message": "Hallo! \U0001f60a Dein Name steht f\u00fcr Charakter in Erding. Aber wer dich sucht, soll dich sofort digital buchen k\u00f6nnen \u2014 ohne Warten am Telefon. Unsere KI-Rezeption \u00fcbernimmt den Empfang f\u00fcr dich. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Gentleman's Cut M\u00fcnchen",
     "custom_message": "Hallo Wisam! \U0001f60a Old School Barbierkunst trifft Morgen \u2014 sei der technologische Leader in Schwabing. Tausche Planity gegen dein eigenes System: Website\u00a0+\u00a0App\u00a0+\u00a0KI. Die Kundin geh\u00f6rt dir, nicht der Plattform. \U0001f4b0 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "L'Amour Beauty Perlach Plaza",
     "custom_message": "Hallo! \U0001f60a In der Perlach Plaza ist viel los. Laufkundschaft will sofort wissen: Wann ist frei? Unsere KI-Rezeption mit Echtzeit-Slot-Anzeige sichert dir diese Kunden direkt per Chat. \U0001f4b0 1.000\u00a0\u20ac einmalig. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
    {"name": "Barberella Haidhausen",
     "custom_message": "Hallo! \U0001f60a Haidhausen liebt Originale! Aber Treatwell verdient an deinem Ruf. Mit deiner eigenen KI-Rezeption baust du deine eigene Marke auf, nicht deren Plattform. Hol dir die Kundenbindung zur\u00fcck f\u00fcr einmalig 1.000\u00a0\u20ac. \U0001f449 https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────
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

# ── Main ──────────────────────────────────────────────────────────────────────
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
