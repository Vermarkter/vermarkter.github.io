#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sniper_batch_prepare_fr.py — Build OpenAI Batch JSONL for French-market leads.

Prompt: "Indépendance" — targets premium salons in Nice/Cannes/Monaco/Paris.
Personalizes based on platform dependency (Treatwell/Planity/Booksy), rating,
booking presence. Output: professional French email + WhatsApp message.

Usage:
  python scripts/sniper_batch_prepare_fr.py                          # Nice, all new
  python scripts/sniper_batch_prepare_fr.py --city Nice --limit 200
  python scripts/sniper_batch_prepare_fr.py --city Nice --force
  python scripts/sniper_batch_prepare_fr.py --channel email          # email only
  python scripts/sniper_batch_prepare_fr.py --channel wa             # WA only

Output: batch/nice_fr_<timestamp>.jsonl
Run next: python scripts/sniper_batch_submit.py --file <output>
"""

import sys, io, os, json, argparse, configparser, urllib.request, urllib.parse, re
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
from scripts.signature import get_signature

# ── Config ────────────────────────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()

HDRS = {'apikey': SB_KEY, 'Authorization': 'Bearer ' + SB_KEY}

OPENAI_MODEL = 'gpt-4o'
FIELDS = 'id,name,city,district,phone,email,website,notes,custom_message,status'

DEMO_URL = 'https://vermarkter.vercel.app/services/beauty-industry/de/'

_MOBILE_RE = re.compile(r'\+33\s*[67]|\b0[67]\d{8}')

# ── Prompt "Indépendance" ──────────────────────────────────────────────────────
_SYSTEM_PROMPT_FR_WA_TMPL = """Tu es un conseiller d'élite en transformation digitale. Style : Moderne Professionnel.
Vouvoiement OBLIGATOIRE. Jamais « Salut » ou « Hey ».

CONTEXTE PRODUIT (OBLIGATOIRE — ne jamais restreindre) :
Notre pack digital comprend : site web + application mobile + réceptionniste IA 24h/24 + CRM.
Disponible en 10 langues : français, anglais, arabe, russe, ukrainien, turc, polonais, espagnol, chinois, allemand.
Prix : 1 000 € une seule fois. Zéro abonnement. Zéro commission.

PHILOSOPHIE "INDÉPENDANCE" :
Les plateformes comme Treatwell, Planity et Booksy prennent 15–30% de commission sur chaque réservation
et possèdent la relation client. Votre salon mérite sa propre infrastructure digitale.
Chaque client qui réserve via notre système appartient à vous — pas à une plateforme.

FEW-SHOT EXEMPLES (respecter exactement cette structure) :

Exemple Planity/Treatwell :
« Bonjour, vos réservations passent par Planity — vous payez une commission à chaque client et construisez leur base, pas la vôtre. Nous vous offrons votre propre réceptionniste IA (site + app + CRM) pour 1 000 € une fois. Zéro commission, 100 % indépendant. Puis-je vous envoyer une démo 60 secondes ? »

Exemple sans site :
« Bonjour, [Salon] n'a pas encore de site — des clients potentiels vous trouvent sur Google, cliquent sur un concurrent qui a la réservation en ligne. Votre propre site + app + IA en 10 langues pour 1 000 € unique. Démo 60 sec disponible — intéressé(e) ? »

Exemple premium (rating ≥ 4.8) :
« Bonjour, [Salon] est une référence à [Ville] — [N]★ pour [X] avis. Mais qui veut réserver le soir ou le dimanche doit appeler. Notre réceptionniste IA reçoit ces clients 24h/24, en français, anglais et arabe. 1 000 € une fois. Démo 60 sec ? »

RÈGLES (TOUTES OBLIGATOIRES) :
- MAXIMUM 480 caractères — compter exactement, couper sans pitié
- AUCUN lien dans le message — le lien est envoyé après réponse
- Planity/Treatwell/Booksy : nommer la plateforme si connue
- Pas de plateforme connue → parler de clients perdus hors heures d'ouverture
- CTA OBLIGATOIRE (LITTÉRAL) : « Puis-je vous envoyer une démo 60 secondes ? »
- Signature : {signature} (exactement cette chaîne — aucun lien, aucun ajout)
- Ton : professionnel, direct, jamais agressif

Output : UNIQUEMENT le texte du message WhatsApp — aucune explication."""

_SYSTEM_PROMPT_FR_EMAIL_TMPL = """Tu es un conseiller d'élite en transformation digitale. Style : Moderne Professionnel.
Vouvoiement OBLIGATOIRE. Jamais de ton familier.

CONTEXTE PRODUIT (OBLIGATOIRE — ne jamais restreindre) :
Notre pack digital comprend : site web + application mobile + réceptionniste IA 24h/24 + CRM.
Disponible en 10 langues : français, anglais, arabe, russe, ukrainien, turc, polonais, espagnol, chinois, allemand.
Prix : 1 000 € une seule fois. Zéro abonnement. Zéro commission.

PHILOSOPHIE "INDÉPENDANCE" :
Les plateformes comme Treatwell, Planity et Booksy prennent 15–30% de commission sur chaque réservation
et possèdent la relation client. Votre salon mérite sa propre infrastructure digitale.
Chaque client qui réserve via notre système appartient à vous — pas à une plateforme.

FEW-SHOT EXEMPLE E-MAIL (respecter exactement) :
Objet : Votre salon mérite mieux que Planity

Bonjour,

Vos réservations transitent actuellement par Planity — ce qui signifie une commission prélevée à chaque client et une base de données clients qui appartient à leur plateforme, pas à vous.

Nous proposons une alternative : votre propre site web, application mobile et réceptionniste IA disponible 24h/24 en 10 langues — pour 1 000 € une seule fois, sans abonnement.

Résultat : zéro commission, clients fidélisés directement, réservations automatiques même le dimanche.

Puis-je vous envoyer une démo de 60 secondes ?

Cordialement,
{signature}

RÈGLES (TOUTES OBLIGATOIRES) :
- Première ligne : « Objet : ... » (précis, pas de clickbait)
- Longueur : 120–180 mots — structuré, pas de blocs de texte massifs
- Structure : Problème → Solution → CTA
- Ton personnalisé, pas d'e-mail de masse
- CTA OBLIGATOIRE : « Puis-je vous envoyer une démo de 60 secondes ? »
- Signature : {signature}
- AUCUN lien cliquable dans le corps
- Mentionner la plateforme si connue (Planity/Treatwell/Booksy)

Output : UNIQUEMENT Objet + texte e-mail — aucune explication."""


def build_system_prompt_fr(lead, channel):
    sig = get_signature(lead)
    tmpl = _SYSTEM_PROMPT_FR_WA_TMPL if channel == 'wa' else _SYSTEM_PROMPT_FR_EMAIL_TMPL
    return tmpl.format(signature=sig)

PLATFORM_RX = re.compile(r'(treatwell|planity|booksy|fresha|salonkee)', re.I)

# ── Channel detection ─────────────────────────────────────────────────────────
def detect_channels(lead):
    """Returns list of channels for this lead: ['wa'], ['email'], ['wa','email'], or []."""
    phone = (lead.get('phone') or '').strip()
    email = (lead.get('email') or '').strip()
    channels = []
    if phone and _MOBILE_RE.search(phone):
        channels.append('wa')
    elif phone:
        channels.append('wa')
    if email:
        channels.append('email')
    return channels


def detect_channel(lead):
    """Legacy single-channel helper — returns first channel or 'skip'."""
    chs = detect_channels(lead)
    return chs[0] if chs else 'skip'

# ── User prompt builder ───────────────────────────────────────────────────────
def build_user_prompt(lead, channel):
    notes   = (lead.get('notes') or '').lower()
    website = lead.get('website') or ''
    phone   = lead.get('phone') or ''
    email   = lead.get('email') or ''
    city    = lead.get('city') or lead.get('district') or 'Nice'
    rating  = lead.get('rating') or 0
    nrev    = lead.get('user_ratings_total') or 0

    has_booking = 'booking=y' in notes
    ssl_ok      = 'ssl=y' in notes
    dangerous   = 'err=' in notes or 'deceptive' in notes or 'phishing' in notes

    plat = ''
    if website:
        m = PLATFORM_RX.search(website.lower())
        if m:
            plat = m.group(1).capitalize()

    issues = []
    if dangerous:
        issues.append('DANGER : site signalé par Google comme dangereux/trompeur — avertissement visible')
    if plat:
        issues.append(f'réservations via {plat} — commission prélevée, base clients appartient à la plateforme')
    if not has_booking and not plat:
        issues.append('pas de réservation en ligne — clients perdus hors heures d\'ouverture')
    if not ssl_ok and not dangerous:
        issues.append('certificat SSL absent ou expiré — Google déclasse le site')
    if not website:
        issues.append('aucun site web — invisible pour les nouveaux clients sur Google')

    problems = '; '.join(issues) if issues else 'potentiel de croissance digitale et acquisition nouveaux clients'

    channel_instr = (
        'Rédige un message WhatsApp (MAX 480 caractères !).'
        if channel == 'wa'
        else 'Rédige un e-mail professionnel de prospection (avec ligne Objet).'
    )

    return (
        f"Salon : {lead['name']}\n"
        f"Ville : {city}\n"
        f"Site web : {website or 'aucun'}\n"
        f"Téléphone : {phone or '—'}\n"
        f"E-mail : {email or '—'}\n"
        f"Note Google : {rating or '—'} ({nrev or 0} avis)\n"
        f"Problèmes détectés : {problems}\n\n"
        f"{channel_instr}"
    )

# ── JSONL builder ─────────────────────────────────────────────────────────────
def build_jsonl_line(lead, channel):
    system = build_system_prompt_fr(lead, channel)
    max_tok = 200 if channel == 'wa' else 500
    return json.dumps({
        'custom_id': f"{lead['id']}_{channel}",
        'method': 'POST',
        'url': '/v1/chat/completions',
        'body': {
            'model': OPENAI_MODEL,
            'max_tokens': max_tok,
            'temperature': 0.75,
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user',   'content': build_user_prompt(lead, channel)},
            ]
        }
    }, ensure_ascii=False)

# ── Supabase fetch ────────────────────────────────────────────────────────────
def fetch_leads(city, limit, force, min_rating):
    leads = []
    offset = 0
    page_size = 1000
    city_enc = urllib.parse.quote(city, safe='')
    while True:
        effective_limit = min(page_size, limit - len(leads)) if limit else page_size
        url = (f"{SB_URL}/rest/v1/beauty_leads"
               f"?select={FIELDS}"
               f"&city=eq.{city_enc}"
               f"&status=eq.new"
               f"&order=id.asc"
               f"&limit={effective_limit}"
               f"&offset={offset}")
        req = urllib.request.Request(url, headers=HDRS)
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.loads(r.read().decode('utf-8'))
        leads.extend(batch)
        if len(batch) < effective_limit or (limit and len(leads) >= limit):
            break
        offset += page_size
    if limit:
        leads = leads[:limit]
    if not force:
        leads = [l for l in leads if not l.get('custom_message')]
    if min_rating:
        leads = [l for l in leads if (l.get('rating') or 0) >= min_rating]
    return leads

# ── CLI ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='Sniper Batch Prepare FR — prompt Indépendance')
    p.add_argument('--city',       default='Nice')
    p.add_argument('--limit',      type=int, default=0, help='Max leads (0 = all)')
    p.add_argument('--force',      action='store_true', help='Include leads with existing message')
    p.add_argument('--channel',    choices=['wa', 'email', 'both'], default='both')
    p.add_argument('--min-rating', type=float, default=0.0, help='Min Google rating filter')
    p.add_argument('--out',        default='', help='Output path (default: batch/nice_fr_<ts>.jsonl)')
    return p.parse_args()

def main():
    args = parse_args()

    out_dir = os.path.join(_ROOT, 'batch')
    os.makedirs(out_dir, exist_ok=True)

    if args.out:
        out_path = args.out if os.path.isabs(args.out) else os.path.join(_ROOT, args.out)
    else:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out_path = os.path.join(out_dir, f"{args.city.lower()}_fr_{ts}.jsonl")

    print(f'\n{"="*64}')
    print(f'  Sniper Batch FR  |  Prompt: Indépendance  |  model={OPENAI_MODEL}')
    print(f'  City: {args.city}  |  channel={args.channel}  |  limit={args.limit or "all"}')
    print(f'  min_rating={args.min_rating}  |  force={args.force}')
    print(f'{"="*64}\n')

    print('Fetching leads from Supabase...')
    leads = fetch_leads(args.city, args.limit or 0, args.force, args.min_rating)

    if not leads:
        print('No new leads found — run lead_harvester.py first:')
        print('  python scripts/lead_harvester.py --plz 06000 06100 06200 06300 --city Nice')
        return

    # Channel split — a lead with mobile+email generates two JSONL lines
    wa_leads    = []
    email_leads = []
    both_leads  = []
    skip_leads  = []

    for l in leads:
        chs = detect_channels(l)
        if 'wa' in chs and 'email' in chs:
            both_leads.append(l)
        elif 'wa' in chs:
            wa_leads.append(l)
        elif 'email' in chs:
            email_leads.append(l)
        else:
            skip_leads.append(l)

    print(f'Fetched {len(leads)} leads:')
    print(f'  WA only:    {len(wa_leads)}')
    print(f'  Email only: {len(email_leads)}')
    print(f'  Both:       {len(both_leads)}')
    print(f'  Skip:       {len(skip_leads)} (no contact)')

    to_process = []
    if args.channel in ('wa', 'both'):
        to_process.extend((l, 'wa') for l in wa_leads)
        to_process.extend((l, 'wa') for l in both_leads)
    if args.channel in ('email', 'both'):
        to_process.extend((l, 'email') for l in email_leads)
        to_process.extend((l, 'email') for l in both_leads)

    if not to_process:
        print('Nothing to process for selected channel.')
        return

    print(f'\nWriting {len(to_process)} JSONL lines → {out_path}')

    with open(out_path, 'w', encoding='utf-8') as f:
        for lead, ch in to_process:
            f.write(build_jsonl_line(lead, ch) + '\n')

    size_kb = os.path.getsize(out_path) / 1024
    print(f'\n  Output: {out_path}')
    print(f'  Lines:  {len(to_process)}')
    print(f'  Size:   {size_kb:.1f} KB')
    print(f'\n  Next step:')
    print(f'  python scripts/sniper_batch_submit.py --file "{out_path}"')
    print(f'{"="*64}')


if __name__ == '__main__':
    main()
