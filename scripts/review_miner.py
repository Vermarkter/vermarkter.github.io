#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
review_miner.py — Mine negative Google reviews for Munich leads.

For each lead:
  1. Resolve place_id via Places Text Search if missing
  2. Fetch up to 5 reviews via Places Details API (sorted by newest)
  3. Filter to negative reviews (rating 1–2)
  4. Extract pain essence via regex + keyword classifier
  5. Export to data/munich_pains_100.json

Pain categories (used by sniper):
  waiting_time  · booking_problem · language_barrier · rude_staff
  dirty_salon   · price_quality   · no_show          · opening_hours
  communication · result_quality  · parking          · other

Output per lead:
  {id, name, place_id, address, pains: [{rating, date, author, text,
   pain_tags, pain_summary, sniper_hook}]}

Usage:
  python3 scripts/review_miner.py
  python3 scripts/review_miner.py --city Munich --start-id 2127 --limit 100
  python3 scripts/review_miner.py --dry-run      # no Supabase writes
  python3 scripts/review_miner.py --ids 2127,2128,2129
  python3 scripts/review_miner.py --resume       # skip already-processed IDs
"""

import sys, io, os, json, re, time, argparse, configparser, urllib.request, urllib.parse
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA = os.path.join(_ROOT, 'data')
_LOGS = os.path.join(_ROOT, 'logs')
os.makedirs(_DATA, exist_ok=True)
os.makedirs(_LOGS, exist_ok=True)

OUTPUT_FILE = os.path.join(_DATA, 'munich_pains_100.json')
LOG_FILE    = os.path.join(_LOGS, 'review_miner.log')

# ── Config ─────────────────────────────────────────────────────────────────────
def _load_env(path):
    env = {}
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return env

_env = _load_env(os.path.join(_ROOT, '.env'))
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(_ROOT, 'config.ini'), encoding='utf-8')

try:
    SB_URL = _cfg['SUPABASE']['url'].strip()
    _svc   = _cfg['SUPABASE']['service_role_key'].strip()
    SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
             else _cfg['SUPABASE']['anon_key'].strip()
except (KeyError, configparser.NoSectionError):
    print('[ERROR] config.ini missing [SUPABASE] section.', file=sys.stderr)
    sys.exit(1)

MAPS_KEY = (
    _env.get('GOOGLE_MAPS_API_KEY')
    or os.environ.get('GOOGLE_MAPS_API_KEY', '')
    or _cfg.get('GOOGLE', 'maps_api_key', fallback='')
).strip()

OPENAI_KEY = (
    _env.get('OPENAI_API_KEY')
    or os.environ.get('OPENAI_API_KEY', '')
    or _cfg.get('OPENAI', 'api_key', fallback='')
).strip()

if not MAPS_KEY or 'PASTE' in MAPS_KEY or not MAPS_KEY.startswith('AIza'):
    print('[ERROR] GOOGLE_MAPS_API_KEY missing or invalid in config.ini [GOOGLE] maps_api_key',
          file=sys.stderr)
    sys.exit(1)

USE_AI = bool(OPENAI_KEY and OPENAI_KEY.startswith('sk-') and 'PASTE' not in OPENAI_KEY)

# ── Supabase headers ───────────────────────────────────────────────────────────
HDRS_GET = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
}
HDRS_PATCH = {
    'apikey': SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
}

# ── Google Places API URLs ─────────────────────────────────────────────────────
PLACES_SEARCH_URL  = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
PLACES_DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

# ── Pain keyword taxonomy ──────────────────────────────────────────────────────
# Each entry: (tag, [german_patterns], [english_patterns], sniper_hook_de)
PAIN_TAXONOMY = [
    (
        'waiting_time',
        [r'warte[tn]|wartezeit|stunde[n]? gewartet|zu lange|ewig gewartet|verspätung|zu spät|pünktlichkeit'],
        [r'wait(ing|ed)|long wait|hours? waiting|late|delayed|punctual'],
        'Ihre Kunden beklagen sich über lange Wartezeiten — unser Online-Buchungssystem eliminiert das.',
    ),
    (
        'booking_problem',
        [r'termin.?(nicht|kaum|schwer|unmöglich)|nicht erreichbar|niemand (geht ran|nimmt ab)|kein rückruf|telefonisch|buchung'],
        [r'can.?t book|no appointment|unreachable|no callback|booking system|hard to reach'],
        'Kunden können keinen Termin vereinbaren — mit unserem 24/7-Buchungssystem buchen sie direkt.',
    ),
    (
        'language_barrier',
        [r'sprach(e|problem|barriere|kenntnisse)|kein (deutsch|englisch|türkisch|arabisch)|verständigung|nicht verstanden'],
        [r'language (barrier|problem)|no english|no german|communication problem|misunderstood'],
        'Sprachbarriere kostet Sie Kunden — wir bauen eine mehrsprachige Buchungsseite für Sie.',
    ),
    (
        'rude_staff',
        [r'unhöflich|unfreundlich|frech|arrogant|respektlos|grob|pampig|schlechte behandlung|ignoriert'],
        [r'rude|unfriendly|arrogant|disrespectful|ignored|bad attitude|dismissive'],
        'Bewertungen über unfreundliches Personal schaden Ihrem Ruf — wir zeigen Ihnen, wie Sie das umkehren.',
    ),
    (
        'dirty_salon',
        [r'schmutzig|dreckig|unhygienisch|nicht sauber|hygiene|staub|schimmel|ekelhaft'],
        [r'dirty|unclean|unhygienic|filthy|dust|mold|disgusting'],
        'Hygienebeschwerden sind der schnellste Weg, Kunden zu verlieren — wir helfen bei der Online-Reputation.',
    ),
    (
        'price_quality',
        [r'zu teuer|preis.?leistung|überteuert|nicht wert|abzocke|enttäuscht.*preis|preis.*enttäuscht'],
        [r'overpriced|too expensive|not worth|price.quality|rip.?off|disappointed.*price'],
        'Kunden empfinden Ihr Preis-Leistungs-Verhältnis als schlecht — wir helfen, den Wert sichtbar zu machen.',
    ),
    (
        'no_show',
        [r'nicht erschienen|nicht da|geschlossen obwohl|trotz termin|vergebens|umsonst hingefahren'],
        [r'no.show|not there|closed when|wasted trip|didn.t show'],
        'Termine wurden nicht eingehalten — automatische Erinnerungen reduzieren No-Shows um 80 %.',
    ),
    (
        'opening_hours',
        [r'öffnungszeiten|zu früh|zu früh geschlossen|nicht geöffnet|falscher.* zeit|zeiten.*(falsch|stimmen nicht)'],
        [r'opening hours|closed early|wrong hours|not open|hours (wrong|incorrect)'],
        'Falsche Öffnungszeiten online frustrieren Kunden — wir pflegen Ihr Google-Profil korrekt.',
    ),
    (
        'result_quality',
        [r'ergebnis.*(schlecht|enttäuschend|nicht gut)|schlecht.*(schnitt|färb|nagel|wax)|erwartet.*nicht|nacharbeiten'],
        [r'bad (result|cut|color|job)|disappointed with|not what (i|we) expected|had to redo'],
        'Qualitätsbeschwerden zerstören die Reputation — wir helfen, positive Erfahrungen sichtbar zu machen.',
    ),
    (
        'communication',
        [r'keine (antwort|reaktion|rückmeldung)|nicht reagiert|ignoriert.*nachricht|whatsapp.*gelesen|ghosted'],
        [r'no response|didn.t reply|ignored (my|the) message|ghosted|no reaction'],
        'Kunden fühlen sich ignoriert — unser WhatsApp-Assistent antwortet sofort, 24/7.',
    ),
    (
        'parking',
        [r'parkplatz|parken (schwierig|unmöglich|kein)|keine parkm'],
        [r'parking (difficult|impossible|no)|no parking|can.t park'],
        'Schlechte Erreichbarkeit — wir können Wegbeschreibung und Parktipps in Ihre Buchungsseite integrieren.',
    ),
]

# ── Logging ────────────────────────────────────────────────────────────────────
def log(msg, level='INFO'):
    ts   = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] [{level}] {msg}'
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except Exception:
        pass

# ── Supabase helpers ───────────────────────────────────────────────────────────
def sb_fetch_leads(city, start_id, limit, ids=None):
    """Fetch leads with id >= start_id, paginating as needed."""
    if ids:
        id_list = ','.join(str(i) for i in ids)
        params = (f"select=id,name,city,address,website,place_id,maps_url"
                  f"&id=in.({id_list})"
                  f"&order=id.asc")
        url = f"{SB_URL}/rest/v1/beauty_leads?{params}"
        req = urllib.request.Request(url, headers=HDRS_GET)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:
            log(f'sb_fetch_leads error: {e}', 'ERROR')
            return []

    all_leads = []
    offset    = 0
    page_size = 100
    while len(all_leads) < limit:
        fetch = min(page_size, limit - len(all_leads))
        params = (f"select=id,name,city,address,website,place_id,maps_url"
                  f"&city=eq.{urllib.parse.quote(city, safe='')}"
                  f"&id=gte.{start_id}"
                  f"&order=id.asc"
                  f"&limit={fetch}"
                  f"&offset={offset}")
        url = f"{SB_URL}/rest/v1/beauty_leads?{params}"
        req = urllib.request.Request(url, headers=HDRS_GET)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                page = json.loads(r.read().decode('utf-8'))
        except Exception as e:
            log(f'sb_fetch page error (offset={offset}): {e}', 'ERROR')
            break
        all_leads.extend(page)
        if len(page) < fetch:
            break
        offset += fetch
    return all_leads


def sb_patch_place_id(lead_id, place_id):
    """Cache resolved place_id back to Supabase."""
    payload = json.dumps({'place_id': place_id}).encode('utf-8')
    url     = f"{SB_URL}/rest/v1/beauty_leads?id=eq.{lead_id}"
    req     = urllib.request.Request(url, data=payload, headers=HDRS_PATCH, method='PATCH')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception:
        return 0

# ── Google Places helpers ──────────────────────────────────────────────────────
def _gmaps_get(url, params):
    """GET Google Maps API endpoint, return parsed JSON or {}."""
    full_url = url + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(full_url, headers={'User-Agent': 'Vermarkter-ReviewMiner/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        log(f'GMaps HTTP {e.code} for {url}', 'WARN')
        return {}
    except Exception as e:
        log(f'GMaps error: {e}', 'WARN')
        return {}


def resolve_place_id(lead):
    """Return place_id string or None. Uses existing value if present."""
    # 1. Already in DB
    if lead.get('place_id') and lead['place_id'].startswith('ChIJ'):
        return lead['place_id']

    # 2. Extract from maps_url  (?query_place_id=ChIJ...)
    maps_url = lead.get('maps_url', '')
    if maps_url:
        m = re.search(r'query_place_id=(ChIJ[^&\s]+)', maps_url)
        if m:
            return m.group(1)

    # 3. Text Search fallback
    name    = lead.get('name', '')
    address = lead.get('address', '')
    query   = f"{name} {address}".strip()
    if not query:
        return None

    data = _gmaps_get(PLACES_SEARCH_URL, {
        'input':     query,
        'inputtype': 'textquery',
        'fields':    'place_id',
        'language':  'de',
        'key':       MAPS_KEY,
    })
    candidates = data.get('candidates', [])
    if candidates:
        return candidates[0].get('place_id')
    return None


def fetch_reviews(place_id, max_reviews=5):
    """
    Fetch reviews for place_id via Places Details API.
    Returns list of review dicts or [].
    """
    data = _gmaps_get(PLACES_DETAILS_URL, {
        'place_id': place_id,
        'fields':   'review,name,rating',
        'language': 'de',    # request German — shows original if translated
        'reviews_sort': 'newest',
        'key':      MAPS_KEY,
    })
    result = data.get('result', {})
    reviews = result.get('reviews', [])
    return reviews[:max_reviews]

# ── Pain analysis ──────────────────────────────────────────────────────────────
def regex_classify(text):
    """Return list of pain tags matching the review text."""
    t   = text.lower()
    hits = []
    for tag, de_patterns, en_patterns, _ in PAIN_TAXONOMY:
        for pat in de_patterns + en_patterns:
            if re.search(pat, t, re.IGNORECASE):
                hits.append(tag)
                break
    return hits if hits else ['other']


def regex_summary(text, tags):
    """Build a short German pain summary sentence from tags + text."""
    # Extract the most painful phrase (first sentence ≤ 100 chars)
    sentences = re.split(r'[.!?]\s+', text.strip())
    snippet   = next((s.strip() for s in sentences if len(s.strip()) > 15), text[:120])
    if len(snippet) > 120:
        snippet = snippet[:117] + '…'

    # Map tags to human-readable German
    TAG_DE = {
        'waiting_time':   'lange Wartezeiten',
        'booking_problem':'Buchungsprobleme',
        'language_barrier':'Sprachbarriere',
        'rude_staff':     'unfreundliches Personal',
        'dirty_salon':    'Hygienemängel',
        'price_quality':  'schlechtes Preis-Leistungs-Verhältnis',
        'no_show':        'Termin nicht eingehalten',
        'opening_hours':  'falsche Öffnungszeiten',
        'result_quality': 'schlechte Arbeitsqualität',
        'communication':  'fehlende Reaktion auf Nachrichten',
        'parking':        'Parkprobleme',
        'other':          'allgemeine Unzufriedenheit',
    }
    tag_labels = [TAG_DE.get(t, t) for t in tags]
    summary    = ' / '.join(tag_labels)
    return summary, snippet


def ai_classify(text, tags_fallback):
    """
    Use OpenAI to extract pain essence in one sentence.
    Falls back to regex result on any error.
    Returns (tags, summary, snippet).
    """
    if not USE_AI:
        summary, snippet = regex_summary(text, tags_fallback)
        return tags_fallback, summary, snippet

    prompt = (
        'Du bist ein Sales-Analyst. Analysiere diesen deutschen Google-Bewertungstext '
        'und antworte NUR mit einem JSON-Objekt mit zwei Schlüsseln:\n'
        '  "tags": Liste aus 1-3 Strings aus: waiting_time, booking_problem, '
        'language_barrier, rude_staff, dirty_salon, price_quality, no_show, '
        'opening_hours, result_quality, communication, parking, other\n'
        '  "summary": Ein kurzer deutscher Satz (max 15 Wörter), der das Kernproblem nennt.\n\n'
        f'Bewertungstext: """{text[:600]}"""'
    )

    payload = json.dumps({
        'model':      'gpt-4o-mini',
        'max_tokens': 120,
        'temperature': 0,
        'messages': [{'role': 'user', 'content': prompt}],
    }, ensure_ascii=False).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {OPENAI_KEY}',
            'Content-Type': 'application/json',
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            resp  = json.loads(r.read().decode('utf-8'))
            raw   = resp['choices'][0]['message']['content'].strip()
            # Strip markdown code fences if present
            raw   = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw, flags=re.DOTALL).strip()
            parsed = json.loads(raw)
            tags    = parsed.get('tags', tags_fallback) or tags_fallback
            summary = parsed.get('summary', '')
            _, snippet = regex_summary(text, tags)
            return tags, summary, snippet
    except Exception as e:
        log(f'AI classify error: {e} — falling back to regex', 'WARN')
        summary, snippet = regex_summary(text, tags_fallback)
        return tags_fallback, summary, snippet


def build_sniper_hook(tags):
    """Return the best sniper hook sentence for the tag set."""
    # Priority order matters — booking_problem and waiting_time are highest-value hooks
    PRIORITY = [
        'booking_problem', 'waiting_time', 'communication',
        'language_barrier', 'rude_staff', 'result_quality',
        'price_quality', 'no_show', 'opening_hours',
        'dirty_salon', 'parking', 'other',
    ]
    hook_map = {tag: hook for tag, _, _, hook in PAIN_TAXONOMY}
    for t in PRIORITY:
        if t in tags:
            return hook_map.get(t, '')
    return hook_map.get('other', '')


def analyze_review(review):
    """
    Returns enriched review dict with pain_tags, pain_summary, sniper_hook.
    """
    text   = review.get('text', '')
    rating = review.get('rating', 0)

    if not text:
        return None

    # Regex pass first (free, fast)
    regex_tags             = regex_classify(text)
    tags, summary, snippet = ai_classify(text, regex_tags)

    return {
        'rating':        rating,
        'author':        review.get('author_name', ''),
        'date':          review.get('relative_time_description', ''),
        'time':          review.get('time', 0),
        'text':          text,
        'pain_snippet':  snippet,
        'pain_tags':     tags,
        'pain_summary':  summary,
        'sniper_hook':   build_sniper_hook(tags),
    }

# ── Main ───────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description='review_miner — mine negative Google reviews')
    p.add_argument('--city',     default='Munich', help='City filter (default: Munich)')
    p.add_argument('--start-id', type=int, default=2127, dest='start_id',
                   help='Minimum lead ID to process (default: 2127)')
    p.add_argument('--limit',    type=int, default=100, help='Max leads (default: 100)')
    p.add_argument('--ids',      default='', help='Comma-separated lead IDs (overrides city/start-id)')
    p.add_argument('--dry-run',  action='store_true', dest='dry_run',
                   help='Do not write place_id back to Supabase')
    p.add_argument('--resume',   action='store_true',
                   help='Skip lead IDs already present in output file')
    p.add_argument('--min-rating', type=int, default=2, dest='min_rating',
                   help='Max star rating to include (default: 2 = only 1-2 stars)')
    p.add_argument('--max-reviews', type=int, default=3, dest='max_reviews',
                   help='Max negative reviews to keep per lead (default: 3)')
    p.add_argument('--delay',    type=float, default=0.25,
                   help='Seconds between API calls (default: 0.25)')
    p.add_argument('--output',   default=OUTPUT_FILE,
                   help=f'Output JSON path (default: {OUTPUT_FILE})')
    return p.parse_args()


def main():
    args = parse_args()

    log(f'review_miner START | city={args.city} start_id={args.start_id} '
        f'limit={args.limit} ai={"ON" if USE_AI else "OFF (regex only)"}')

    # Load existing output for --resume
    existing = {}
    if args.resume and os.path.exists(args.output):
        try:
            with open(args.output, encoding='utf-8') as f:
                for entry in json.load(f):
                    existing[entry['id']] = entry
            log(f'Resume: loaded {len(existing)} existing entries')
        except Exception as e:
            log(f'Could not load existing output: {e}', 'WARN')

    # Fetch leads
    ids = [int(x.strip()) for x in args.ids.split(',') if x.strip()] if args.ids else None
    leads = sb_fetch_leads(args.city, args.start_id, args.limit, ids=ids)

    if not leads:
        print(f'No leads found for city={args.city} id>={args.start_id}')
        return

    log(f'Fetched {len(leads)} leads from Supabase')

    results    = list(existing.values())   # carry over resumed entries
    done_ids   = set(existing.keys())
    processed  = skipped = no_place = no_neg = errors = 0
    ai_calls   = 0

    W = 70
    print(f'\n{"═"*W}')
    print(f'  REVIEW MINER  |  {len(leads)} leads  |  AI: {"ON (gpt-4o-mini)" if USE_AI else "OFF (regex)"}')
    print(f'{"═"*W}\n')

    for i, lead in enumerate(leads):
        lid  = lead['id']
        name = lead.get('name', f'Lead {lid}')

        if lid in done_ids:
            log(f'[{i+1}/{len(leads)}] SKIP (resumed) id={lid}')
            skipped += 1
            continue

        print(f'  [{i+1:>4}/{len(leads)}] id={lid:<6} {name[:40]:<40}', end=' ', flush=True)

        # 1. Resolve place_id
        place_id = resolve_place_id(lead)
        if not place_id:
            print('⚠ no place_id')
            no_place += 1
            results.append({
                'id': lid, 'name': name,
                'place_id': None, 'address': lead.get('address', ''),
                'pains': [], '_status': 'no_place_id',
            })
            continue

        # Cache place_id if it was missing
        if not lead.get('place_id') and not args.dry_run:
            sb_patch_place_id(lid, place_id)

        time.sleep(args.delay)   # respect Google QPS limit

        # 2. Fetch reviews
        try:
            reviews = fetch_reviews(place_id, max_reviews=10)
        except Exception as e:
            print(f'✗ fetch error: {e}')
            errors += 1
            results.append({
                'id': lid, 'name': name,
                'place_id': place_id, 'address': lead.get('address', ''),
                'pains': [], '_status': f'error: {str(e)[:60]}',
            })
            continue

        time.sleep(args.delay)

        # 3. Filter negative reviews (≤ min_rating stars)
        neg_reviews = [r for r in reviews if r.get('rating', 5) <= args.min_rating]

        if not neg_reviews:
            print(f'✓ {len(reviews)} reviews, 0 negative')
            no_neg += 1
            results.append({
                'id': lid, 'name': name,
                'place_id': place_id, 'address': lead.get('address', ''),
                'total_reviews_fetched': len(reviews),
                'pains': [], '_status': 'no_negative_reviews',
            })
            processed += 1
            continue

        # Keep only top N negative reviews (most recent first)
        neg_reviews = sorted(neg_reviews, key=lambda r: r.get('time', 0), reverse=True)
        neg_reviews = neg_reviews[:args.max_reviews]

        # 4. Analyze each negative review
        pains = []
        for rev in neg_reviews:
            if not rev.get('text', '').strip():
                continue
            ai_calls += 1 if USE_AI else 0
            enriched = analyze_review(rev)
            if enriched:
                pains.append(enriched)
            time.sleep(args.delay * 0.5)   # small gap between AI calls

        # Aggregate top pain tags across all reviews
        all_tags = []
        for p in pains:
            all_tags.extend(p.get('pain_tags', []))
        tag_counts = {}
        for t in all_tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
        top_tags = sorted(tag_counts, key=tag_counts.get, reverse=True)[:3]

        # Best sniper hook = hook from most frequent tag
        best_hook = build_sniper_hook(top_tags) if top_tags else ''

        entry = {
            'id':                    lid,
            'name':                  name,
            'place_id':              place_id,
            'address':               lead.get('address', ''),
            'website':               lead.get('website', ''),
            'total_reviews_fetched': len(reviews),
            'negative_count':        len(pains),
            'top_pain_tags':         top_tags,
            'best_sniper_hook':      best_hook,
            'pains':                 pains,
            '_status':               'ok',
        }
        results.append(entry)
        processed += 1

        pain_str = ', '.join(top_tags[:2]) if top_tags else 'other'
        print(f'✓ {len(reviews)} reviews, {len(pains)} neg → [{pain_str}]')

    # ── Save output ────────────────────────────────────────────────────────────
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # ── Summary ────────────────────────────────────────────────────────────────
    ok_entries    = [r for r in results if r.get('_status') == 'ok']
    total_pains   = sum(len(r.get('pains', [])) for r in ok_entries)
    all_top_tags  = []
    for r in ok_entries:
        all_top_tags.extend(r.get('top_pain_tags', []))
    tag_freq = {}
    for t in all_top_tags:
        tag_freq[t] = tag_freq.get(t, 0) + 1
    top_global = sorted(tag_freq, key=tag_freq.get, reverse=True)[:5]

    print(f'\n{"═"*W}')
    print(f'  DONE')
    print(f'  Processed: {processed}  |  No place_id: {no_place}  |  No neg: {no_neg}  |  Errors: {errors}')
    print(f'  Total negative reviews collected: {total_pains}')
    print(f'  AI calls used: {ai_calls}')
    print(f'  Top pain categories: {", ".join(top_global)}')
    print(f'  Output → {args.output}')
    print(f'{"═"*W}\n')

    log(f'review_miner DONE | processed={processed} pains={total_pains} '
        f'output={args.output}')


if __name__ == '__main__':
    main()
