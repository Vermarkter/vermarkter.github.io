# -*- coding: utf-8 -*-
"""
fast_uploader.py — Instant CRM patcher from agent output.

Usage:
  1. Paste the agent's batch into BATCH (below) in format:
       Назва салону — Текст повідомлення
  2. Run:  python scripts/fast_uploader.py

Each line is searched by name in beauty_leads (city München).
On match → custom_message + status='READY TO SEND' updated.
Multiple matches → all updated (rare, usually unique names).
No match → printed as NOT FOUND (fix manually via sniper_patch.py).
"""
import sys, io, json, time, urllib.request, urllib.parse, configparser

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

_cfg = configparser.ConfigParser()
_cfg.read(r'c:\Users\andri\OneDrive\Projects\агенство-новий\config.ini', encoding='utf-8')
SB_URL = _cfg['SUPABASE']['url'].strip()
_svc   = _cfg['SUPABASE']['service_role_key'].strip()
SB_KEY = _svc if (len(_svc) > 80 and 'PASTE' not in _svc and 'ВСТАВИТИ' not in _svc) \
         else _cfg['SUPABASE']['anon_key'].strip()
print('[key]', 'service_role' if SB_KEY == _svc else 'anon')

HDRS = {
    'apikey':        SB_KEY,
    'Authorization': 'Bearer ' + SB_KEY,
    'Content-Type':  'application/json',
}

STATUS = 'READY TO SEND'
SEP    = ' — '   # роздільник: «Назва — Повідомлення»

# =============================================================================
# ВСТАВИТИ СЮДИ — одна строка = «Назва — Текст»
# =============================================================================
BATCH = """
Hair Design & Barber — Hallo Hair Design & Barber Team, euer Salon ist top aufgestellt!
4secrets — Hallo 4secrets Team, ihr habt ein starkes Konzept!
"""
# =============================================================================


def find_ids(name: str) -> list[int]:
    enc = urllib.parse.quote(name, safe='')
    url = (f"{SB_URL}/rest/v1/beauty_leads"
           f"?select=id,name"
           f"&name=ilike.{enc}"
           f"&district=ilike.M%C3%BCnchen%25")
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=20) as r:
        rows = json.loads(r.read().decode('utf-8'))
    return [(row['id'], row['name']) for row in rows]


def patch_id(salon_id: int, message: str) -> int:
    payload = json.dumps({'custom_message': message, 'status': STATUS}).encode('utf-8')
    h = dict(HDRS); h['Prefer'] = 'return=minimal'
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/beauty_leads?id=eq.{salon_id}",
        data=payload, headers=h, method='PATCH'
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.request.HTTPError as e:
        return e.code


def parse_batch(raw: str) -> list[tuple[str, str]]:
    pairs = []
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if SEP not in line:
            print(f'  [SKIP bad format] {line[:80]}')
            continue
        idx  = line.index(SEP)
        name = line[:idx].strip()
        msg  = line[idx + len(SEP):].strip()
        if name and msg:
            pairs.append((name, msg))
    return pairs


def main():
    pairs = parse_batch(BATCH)
    if not pairs:
        print('BATCH порожній — вставте текст і запустіть знову.')
        return

    ok = fail = notfound = 0
    print(f'\n{"="*62}')
    print(f'  fast_uploader — {len(pairs)} записів  →  status="{STATUS}"')
    print(f'{"="*62}')

    for name, msg in pairs:
        matches = find_ids(name)
        if not matches:
            print(f'  [NOT FOUND] «{name}» — перевір назву або використай sniper_patch.py')
            notfound += 1
            time.sleep(0.1)
            continue

        for salon_id, matched_name in matches:
            code = patch_id(salon_id, msg)
            sym  = 'OK' if code in (200, 204) else f'ERR {code}'
            preview = msg[:55].replace('\n', ' ')
            print(f'  [{sym}] id={salon_id} «{matched_name}» | {preview}...')
            if code in (200, 204):
                ok += 1
            else:
                fail += 1
        time.sleep(0.15)

    print(f'{"="*62}')
    print(f'  DONE — OK: {ok} | FAILED: {fail} | NOT FOUND: {notfound}')


if __name__ == '__main__':
    main()
