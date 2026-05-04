#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Upload Qwen personalised offers for Nice leads (IDs 4691-4730) to Supabase."""

import json, configparser, urllib.request, urllib.error, sys, io, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

cfg = configparser.ConfigParser()
with open('config.ini', encoding='utf-8') as f:
    cfg.read_file(f)

URL = cfg['SUPABASE']['url']
KEY = cfg['SUPABASE']['anon_key']

# ---------------------------------------------------------------------------
# Offer texts from Qwen report (keyed by lead ID, then channel)
# ---------------------------------------------------------------------------

OFFERS = {
    # --- WA offers ---
    4691: {
        "WA": None,  # channel=Email for this lead
        "Email": (
            "Objet : Votre marge sur chaque réservation — et si elle était 100 % à vous ?\n\n"
            "Bonjour,\n\n"
            "En analysant votre présence à Nice, j’observe une chose : vous attirez des clients fidèles… "
            "mais Planity prélève une commission sur chaque RDV, même ceux qui vous connaissent déjà. "
            "Sur un mois, cela représente un « profit non perçu » significatif — argent qui pourrait "
            "financer votre communication, votre équipe, ou votre développement.\n\n"
            "Imaginez : une plateforme de réservation à votre marque, disponible en 10 langues (français, anglais, "
            "arabe, ukrainien, etc.), où 100 % des revenus restent dans votre caisse. Votre prestige mérite une "
            "vitrine qui vous appartient entièrement.\n\n"
            "Seriez-vous disponible pour un échange de 10 minutes cette semaine ? Je vous montrerai concrètement "
            "comment transformer cette perte en levier de croissance.\n\n"
            "Bien à vous,"
        ),
    },
    4692: {
        "Email": (
            "Objet : Une question rapide sur votre visibilité à Nice\n\n"
            "Bonjour,\n\n"
            "Votre salon Hair Nice propose un service de qualité — et votre site le reflète bien. "
            "Mais votre concurrent vient peut-être de passer devant vous sur Google grâce à une stratégie "
            "d’acquisition digitale plus agressive.\n\n"
            "En 10 minutes, je peux vous montrer comment garder l’avantage sur votre marché local — et même "
            "attirer une clientèle internationale avec une interface multilingue (10 langues inclus).\n\n"
            "Seriez-vous disponible pour un court échange cette semaine ?\n\n"
            "Cordialement,"
        ),
    },
    4693: {
        "Email": (
            "Objet : Votre concurrent vient de vous dépasser sur Google — voici comment reprendre l’avantage\n\n"
            "Bonjour,\n\n"
            "Actuellement, quand un client potentiel tape « coiffeur Nice » ou « soin capillaire "
            "[votre quartier] », Google propose vos concurrents… pas vous. Chaque jour sans site web, c’est du "
            "chiffre d’affaires qui part ailleurs — un « profit non perçu » silencieux mais réel.\n\n"
            "La bonne nouvelle ? En 48h, vous pouvez disposer d’une vitrine professionnelle à votre marque, "
            "optimisée pour Google, avec réservation intégrée en 10 langues. Votre talent mérite d’être vu.\n\n"
            "Souhaitez-vous que je vous montre concrètement comment inverser la tendance ? Je reste à votre "
            "disposition pour un échange rapide.\n\n"
            "Bien à vous,"
        ),
    },
    4694: {
        "Email": (
            "Objet : Salon Carré d’Or — et si vos réservations travaillaient pour vous 24h/24 ?\n\n"
            "Bonjour,\n\n"
            "Votre adresse à Nice et votre positionnement haut de gamme sont de vraies forces. Mais votre site "
            "actuel capte-t-il vraiment tous vos clients potentiels en ligne ?\n\n"
            "Imaginez une plateforme de réservation à votre image, disponible en 10 langues, qui convertit chaque "
            "visite en rendez-vous — même à minuit, même pour une clientèle touristique internationale.\n\n"
            "Je serais ravi de vous présenter une démo personnalisée. Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4695: {
        "Email": (
            "Objet : Unik : Sécurisez vos réservations indépendamment d’Instagram\n\n"
            "Bonjour,\n\n"
            "Votre feed Instagram est une référence — mais dépendre d’un seul algorithme est risqué. "
            "Une mise à jour peut réduire votre portée, et donc vos réservations, du jour au lendemain.\n\n"
            "Et si vous aviez un canal de réservation qui vous appartient ? Une plateforme à votre marque, "
            "disponible en 10 langues, où vos clients réservent directement — sans intermédiaire, sans risque "
            "algorithmique. Votre créativité mérite cette stabilité.\n\n"
            "Je vous propose une démo personnalisée de 10 minutes. Quand seriez-vous disponible ?\n\n"
            "Bien cordialement,"
        ),
    },
    4696: {
        "WA": (
            "Votre travail sur les coupes et l’expérience client est vraiment remarquable. "
            "Mais payer des commissions Planity sur vos propres clients, c’est comme laisser de l’argent sur la table. "
            "Une démo vidéo de 3 minutes pour explorer une alternative sans frais ?"
        ),
    },
    4697: {
        "Email": (
            "Objet : Cynthia & Co — et si chaque clientèle internationale vous trouvait facilement ?\n\n"
            "Bonjour,\n\n"
            "Votre salon à Nice attire une clientèle fidèle — mais dans une ville touristique comme Nice, "
            "les opportunités internationales sont immenses. Votre site actuel est-il prêt à les capter ?\n\n"
            "Une plateforme multilingue (10 langues) à votre image pourrait doubler votre visibilité "
            "sans effort supplémentaire de votre part.\n\n"
            "Je serais heureux de vous montrer comment en 10 minutes. Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4698: {
        "Email": (
            "Objet : LE FIL DE L’ÂME — votre expertise mérite une vitrine à la hauteur\n\n"
            "Bonjour,\n\n"
            "Votre approche holistique du soin capillaire est rare à Nice. Mais est-ce que Google vous "
            "présente aux clients qui vous recherchent ?\n\n"
            "Une plateforme de réservation à votre marque, disponible en 10 langues, pourrait capturer "
            "cette clientèle internationale en quête d’une expérience unique comme la vôtre.\n\n"
            "Je vous propose un échange rapide pour vous montrer le potentiel. Quand seriez-vous disponible ?\n\n"
            "Bien à vous,"
        ),
    },
    4699: {
        "Email": (
            "Objet : Gaspard : votre talent mérite un canal indépendant d’Instagram\n\n"
            "Bonjour,\n\n"
            "Votre univers visuel captive — mais construire votre activité uniquement sur Instagram, "
            "c’est comme bâtir sur du sable. Une mise à jour d’algorithme peut réduire votre portée du jour "
            "au lendemain.\n\n"
            "Et si vous pouviez offrir à vos clients une plateforme de réservation à votre image, en 10 langues, "
            "qui vous appartient entièrement ?\n\n"
            "Je vous propose une démo de 10 minutes. Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4700: {
        "Email": (
            "Objet : Invisible sur Google ? Vos clients vous cherchent… et ne vous trouvent pas\n\n"
            "Bonjour,\n\n"
            "Votre style est unique — mais sans site web, Google ne peut pas vous référencer. "
            "Résultat : des clients idéaux choisissent vos concurrents simplement parce qu’ils apparaissent en premier.\n\n"
            "Imaginez : une plateforme à votre image, qui attire vos clients cibles, convertit les visites en RDV, "
            "et fonctionne en 10 langues pour capter une clientèle internationale à Nice. Votre prestige mérite "
            "cette visibilité.\n\n"
            "Je serais heureux de vous présenter une solution sur-mesure. Quand seriez-vous disponible pour un "
            "court échange ?\n\n"
            "Cordialement,"
        ),
    },
    4701: {
        "Email": (
            "Objet : Identity Hair Design — comment attirer plus de clients internationaux à Nice\n\n"
            "Bonjour,\n\n"
            "Votre salon bénéficie d’une belle présence en ligne. Mais Nice est une destination internationale "
            "— et vos concurrents commencent à proposer des réservations multilingues.\n\n"
            "En 10 minutes, je peux vous montrer comment rester en tête avec une plateforme disponible en "
            "10 langues, sans changer votre fonctionnement actuel.\n\n"
            "Quand seriez-vous disponible pour un court échange ?\n\n"
            "Bien à vous,"
        ),
    },
    4702: {
        "WA": (
            "Xena, votre présence en ligne est remarquable — mais dépendre de Facebook et des plateformes tierces, "
            "c’est risqué. Et si vos clients pouvaient réserver directement chez vous, sans intermédiaire ? "
            "Démo vidéo rapide pour voir comment ?"
        ),
    },
    4703: {
        "Email": (
            "Objet : Michel Barbera — et si vos commissions Planity finançaient votre prochaine campagne ?\n\n"
            "Bonjour,\n\n"
            "J’admire la qualité de votre prestation et votre attention aux détails. Pourtant, les commissions "
            "Planity grignotent silencieusement votre rentabilité — sur un mois, c’est un vrai budget manquant.\n\n"
            "Imaginez une plateforme à votre image, sans commission, disponible en 10 langues pour capter "
            "la clientèle internationale de Nice.\n\n"
            "Puis-je vous montrer concrètement comment in un échange de 10 minutes ?\n\n"
            "Bien à vous,"
        ),
    },
    4704: {
        "Email": (
            "Objet : Alias Coiffure — comment attirer plus de clients sans dépendre des plateformes\n\n"
            "Bonjour,\n\n"
            "Votre salon a une belle réputation à Nice. Mais votre site actuel vous permet-il de capter "
            "toute la clientèle internationale qui visite la côte ?\n\n"
            "En 10 minutes, je peux vous montrer comment transformer votre présence digitale en véritable "
            "moteur de réservations — multilingue, sans intermédiaire.\n\n"
            "Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4705: {
        "WA": (
            "MYSOKO, votre expertise en lissage est votre signature à Nice. Mais payer des plateformes "
            "pour vos propres clients, c’est une perte sèche. Démo vidéo pour voir comment garder 100 % "
            "de vos revenus ?"
        ),
    },
    4706: {
        "WA": (
            "KRISTEL, votre expertise en coiffure et onglerie mérite une vitrine digitale. Sans site, "
            "vous êtes invisible sur Google — et vos concurrents en profitent. Une démo vidéo rapide "
            "pour changer ça ?"
        ),
    },
    4707: {
        "Email": (
            "Objet : Jade & Co. — votre marge sur chaque réservation pourrait être 100 % à vous\n\n"
            "Bonjour,\n\n"
            "Votre salon rayonne à Nice, et c’est mérité ! Mais si vous pouviez économiser les commissions "
            "Planity sur chaque RDV, que feriez-vous de ce budget supplémentaire ?\n\n"
            "Une plateforme à votre image, sans commission, disponible en 10 langues — votre prestige mérite "
            "une vitrine qui vous appartient entièrement.\n\n"
            "Intéressé(e) par une démo vidéo rapide ? Quand seriez-vous disponible ?\n\n"
            "Bien à vous,"
        ),
    },
    4708: {
        "Email": (
            "Objet : Hair Bar Nice — votre visibilité en ligne mérite mieux\n\n"
            "Bonjour,\n\n"
            "Votre positionnement beauty à Nice est unique. Mais votre site actuel vous permet-il de capter "
            "tous les clients potentiels qui vous cherchent en ligne ?\n\n"
            "En 10 minutes, je peux vous montrer comment maximiser vos réservations avec une plateforme "
            "multilingue (10 langues) à votre image.\n\n"
            "Quand seriez-vous disponible pour un court échange ?\n\n"
            "Cordialement,"
        ),
    },
    4709: {
        "Email": (
            "Objet : Thierry Antoine — et si votre expertise atteignait une clientèle internationale ?\n\n"
            "Bonjour,\n\n"
            "Votre salon cumule coiffure et esthétique — un positionnement fort à Nice. Mais votre site "
            "actuel capte-t-il vraiment toute la clientèle touristique internationale ?\n\n"
            "Une interface multilingue (10 langues) pourrait transformer chaque visite en réservation "
            "— sans changer votre fonctionnement actuel.\n\n"
            "Je vous propose une démo de 10 minutes. Quand seriez-vous disponible ?\n\n"
            "Bien à vous,"
        ),
    },
    4710: {
        "Email": (
            "Objet : Max Gauthier — sécurisez vos réservations indépendamment d’Instagram\n\n"
            "Bonjour,\n\n"
            "Votre présence Instagram est impeccable, mais dépendre d’une seule plateforme est risqué. "
            "Une mise à jour d’algorithme peut réduire votre portée du jour au lendemain.\n\n"
            "Et si vous aviez un canal de réservation qui vous appartient ? Une plateforme à votre image, "
            "en 10 langues, sans dépendance algorithmique.\n\n"
            "Une courte démo vidéo pour découvrir comment ? Quand seriez-vous disponible ?\n\n"
            "Bien cordialement,"
        ),
    },
    4711: {
        "Email": (
            "Objet : South Side Barber — comment attirer plus de clients internationaux à Nice\n\n"
            "Bonjour,\n\n"
            "Votre barbershop à Nice a une vraie identité. Mais dans une ville touristique, les clients "
            "internationaux représentent une opportunité immense.\n\n"
            "En 10 minutes, je peux vous montrer comment votre site pourrait capturer cette clientèle "
            "avec une interface disponible en 10 langues.\n\n"
            "Quand seriez-vous disponible pour un court échange ?\n\n"
            "Cordialement,"
        ),
    },
    4712: {
        "WA": (
            "Seven Barbershop, votre style a une vraie identité à Nice ! Mais si chaque réservation vous "
            "rapportait 100 % de sa valeur, sans commission Planity ? Démo vidéo de 2 minutes pour voir "
            "comment ?"
        ),
    },
    4713: {
        "Email": (
            "Objet : West Barber Shop — et si vos commissions Planity devenaient votre budget pub ?\n\n"
            "Bonjour,\n\n"
            "Votre expertise en coloration est clairement un atout pour votre clientèle niçoise. Mais "
            "pourquoi partager vos revenus avec une plateforme pour vos propres clients ?\n\n"
            "Une solution sur-mesure, sans commission, disponible en 10 langues — votre marque mérite "
            "mieux qu’un intermédiaire.\n\n"
            "Puis-je vous montrer concrètement comment en 10 minutes ?\n\n"
            "Bien à vous,"
        ),
    },
    4714: {
        "Email": (
            "Objet : Le barbier de Nice — vos clients potentiels vous cherchent sur Google et ne vous trouvent pas\n\n"
            "Bonjour,\n\n"
            "Votre réputation à Nice est solide, mais Google ne vous « voit » pas sans site. "
            "Résultat : des clients choisissent vos concurrents.\n\n"
            "En 48h, vous pouvez disposer d’une vitrine professionnelle à votre marque, optimisée pour "
            "Google, avec réservation intégrée en 10 langues.\n\n"
            "Puis-je vous montrer en vidéo comment inverser la tendance ?\n\n"
            "Bien à vous,"
        ),
    },
    4715: {
        "WA": (
            "Barber House Port, votre réputation à Nice est solide mais Google ne vous « voit » pas sans site. "
            "Résultat : des clients choisissent vos concurrents. Puis-je vous montrer en vidéo comment "
            "inverser la tendance ?"
        ),
    },
    4716: {
        "Email": (
            "Objet : MY BARBER SHOP — votre talent mérite d’être trouvé en ligne\n\n"
            "Bonjour,\n\n"
            "Votre travail parle de lui-même — mais imaginez l’impact si chaque recherche "
            "« salon Nice » menait à vous ? Sans site, vous êtes invisible sur Google.\n\n"
            "En 48h, vous pouvez avoir une vitrine professionnelle à votre image, avec réservation "
            "intégrée en 10 langues.\n\n"
            "Une démo rapide pour explorer cette possibilité ?\n\n"
            "Bien à vous,"
        ),
    },
    4717: {
        "Email": (
            "Objet : Le local barbershop — comment être trouvé par vos clients idéaux\n\n"
            "Bonjour,\n\n"
            "Vous méritez d’être trouvé(e) facilement par vos clients idéaux. Sans site, c’est comme "
            "avoir une boutique sans enseigne.\n\n"
            "En 48h, vous pouvez disposer d’une vitrine digitale à votre image, optimisée pour Google, "
            "avec réservation en 10 langues.\n\n"
            "Souhaitez-vous voir en vidéo comment créer votre vitrine digitale ?\n\n"
            "Bien à vous,"
        ),
    },
    4718: {
        "WA": (
            "Best Barber, votre qualité de service est reconnue à Nice. Et si vos clients pouvaient "
            "réserver directement chez vous, sans intermédiaire, en 10 langues ? Démo vidéo rapide ?"
        ),
    },
    4719: {
        "WA": (
            "Man To Man, votre barbershop a du style à Nice ! Mais construire sur des plateformes tierces, "
            "c’est risqué. Et si vos clients réservaient directement chez vous, sans commission ? "
            "Démo vidéo de 2 minutes ?"
        ),
    },
    4720: {
        "Email": (
            "Objet : BLACKBOX Nice — comment capturer la clientèle internationale sur la Côte\n\n"
            "Bonjour,\n\n"
            "BLACKBOX Nice est un concept fort à Nice. Dans une ville touristique, la clientèle "
            "internationale représente une opportunité immense.\n\n"
            "Une interface multilingue (10 langues) à votre image pourrait doubler votre visibilité "
            "sans effort supplémentaire.\n\n"
            "Je serais ravi de vous présenter une démo personnalisée. Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4721: {
        # AR bilingual — WA channel (mobile +336)
        "WA": (
            "Bonjour Nabyl, votre travail chez Estika est remarquable — "
            "لفت انتباهي جودة خدماتكم في نيس. "
            "ومع ذلك، هل تعلمون أن عمولات Planity "
            "تقلل من أرباحكم حتى مع عملائكم "
            "المخلصين؟ "
            "هل تودون مشاهدة عرض فيديو قصير "
            "يوضح كيف يمكن لعملائكم الحجز "
            "بـ 10 لغات، بما فيها العربية؟"
        ),
    },
    4722: {
        "WA": (
            "My Barberhood, votre expertise est précieuse mais sans présence web autonome, vous laissez "
            "Google privilégier vos concurrents. Une courte démo vidéo pour reprendre la main sur votre "
            "visibilité ?"
        ),
    },
    4723: {
        "Email": (
            "Objet : KDH Barber Nice — et si vos commissions Planity devenaient votre levier de croissance ?\n\n"
            "Bonjour,\n\n"
            "KDH, votre style barbershop a une vraie identité à Nice. Cependant, payer Planity pour vos "
            "clients récurrents, c’est une perte sèche — un budget qui pourrait financer votre communication.\n\n"
            "Une plateforme à votre image, sans commission, disponible en 10 langues pour capter la "
            "clientèle internationale.\n\n"
            "Je vous propose une démo personnalisée. Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4724: {
        "Email": (
            "Objet : One Love Origin — votre talent mérite une vitrine digitale\n\n"
            "Bonjour,\n\n"
            "J’apprécie votre approche client — mais chaque jour sans site, c’est du chiffre d’affaires "
            "potentiel qui part ailleurs.\n\n"
            "En 48h, vous pouvez disposer d’une vitrine professionnelle à votre marque, optimisée pour "
            "Google, avec réservation intégrée en 10 langues.\n\n"
            "Intéressé(e) par une démo vidéo pour y remédier ?\n\n"
            "Bien à vous,"
        ),
    },
    4725: {
        "Email": (
            "Objet : SALON4MEN — comment attirer plus de clients sans commission\n\n"
            "Bonjour,\n\n"
            "Votre salon à Nice a une belle présence. Mais votre site actuel vous permet-il de "
            "maximiser chaque visite en ligne ?\n\n"
            "Une plateforme multilingue (10 langues) à votre image, sans intermédiaire, pourrait "
            "significativement augmenter vos réservations directes.\n\n"
            "Je serais ravi de vous montrer comment en 10 minutes. Quand seriez-vous disponible ?\n\n"
            "Cordialement,"
        ),
    },
    4726: {
        "Email": (
            "Objet : South Side Barber Studio — votre deuxième adresse mérite la même visibilité\n\n"
            "Bonjour,\n\n"
            "Avec deux adresses à Nice, South Side Barber a une présence forte. Mais cela double aussi "
            "vos opportunités digitales.\n\n"
            "Une plateforme multilingue (10 langues) pourrait transformer vos deux adresses en véritables "
            "aimants à clients internationaux.\n\n"
            "Je vous propose une démo de 10 minutes. Quand seriez-vous disponible ?\n\n"
            "Bien à vous,"
        ),
    },
    4727: {
        "WA": (
            "Barber Style, votre salon a du caractère, mais sans site vous êtes invisible pour les nouveaux "
            "clients qui cherchent en ligne. Puis-je vous montrer en vidéo comment changer ça en quelques "
            "clics ?"
        ),
    },
    4728: {
        "WA": (
            "Comptoir des Barbiers, votre talent mérite une vitrine qui vous appartient. Actuellement, "
            "sans site, vous dépendez des plateformes tierces. Souhaitez-vous voir en vidéo comment "
            "créer votre propre espace de réservation ?"
        ),
    },
    4729: {
        "WA": (
            "Barber Chic Nice, votre style est évident — mais sans site, vos clients potentiels ne vous "
            "trouvent pas sur Google. Une démo vidéo rapide pour voir comment créer votre vitrine "
            "digitale ?"
        ),
    },
    4730: {
        "Email": (
            "Objet : YU Barber — récupérez vos marges Planity et attirez une clientèle internationale\n\n"
            "Bonjour,\n\n"
            "Votre approche du soin capillaire est raffinée et vos clients le remarquent. Mais si chaque "
            "réservation vous rapportait 100 % de sa valeur ?\n\n"
            "Une plateforme à votre image, sans commission Planity, disponible en 10 langues pour capter "
            "la clientèle internationale à Nice.\n\n"
            "Une démo vidéo de 2 minutes pour voir comment ?\n\n"
            "Bien à vous,"
        ),
    },
}

# ---------------------------------------------------------------------------
# Load routing data
# ---------------------------------------------------------------------------
with open('data/nice_routing_40.json', encoding='utf-8') as f:
    leads = json.load(f)

routing = {l['id']: l for l in leads}

# ---------------------------------------------------------------------------
# Build PATCH payloads
# ---------------------------------------------------------------------------
def patch_lead(lead_id, payload):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        URL + f'/rest/v1/beauty_leads?id=eq.{lead_id}',
        data=data,
        method='PATCH',
        headers={
            'apikey': KEY,
            'Authorization': 'Bearer ' + KEY,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        }
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code

ok = 0
err = 0
skipped = 0

for lead_id, texts in OFFERS.items():
    r = routing.get(lead_id)
    if not r:
        print(f'  SKIP {lead_id} — not in routing data')
        skipped += 1
        continue

    channel = r['channel']  # WA or Email
    offer = texts.get(channel) or texts.get(list(texts.keys())[0])

    if offer is None:
        print(f'  SKIP {lead_id} — no offer text for channel {channel}')
        skipped += 1
        continue

    notes_val = f"channel={channel} | pain={r['pain']} | lang={r['lang']}"
    payload = {
        'custom_message': offer,
        'status': 'READY TO SEND',
        'notes': notes_val,
    }

    status = patch_lead(lead_id, payload)
    if status in (200, 204):
        print(f'  OK  {lead_id} | {channel:5} | {r["pain"]:8} | {r["lang"]} | {r["name"][:40]}')
        ok += 1
    else:
        print(f'  ERR {lead_id} HTTP {status} | {r["name"][:40]}')
        err += 1

    time.sleep(0.1)  # gentle rate limit

print()
print(f'Done: {ok} updated, {err} errors, {skipped} skipped')
