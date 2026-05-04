#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Live preview: 1 TR + 1 AR message via GPT-4o to verify updated prompts."""
import sys, io, os, json, configparser

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env(path):
    env = {}
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line: continue
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
    except: pass
    return env

_env = load_env(os.path.join(_ROOT, '.env'))
from openai import OpenAI
client = OpenAI(api_key=_env['OPENAI_API_KEY'])

# ── Inline prompts (copied from sniper_batch_prepare_multilang.py) ────────────
# Import via sys.path
sys.path.insert(0, os.path.join(_ROOT, 'scripts'))

# Manually extract constants by reading the file
_src_lines = open(os.path.join(_ROOT, 'scripts', 'sniper_batch_prepare_multilang.py'), encoding='utf-8').readlines()

# Find SYSTEM_PROMPT_TR and SYSTEM_PROMPT_AR by parsing the file
import ast, re

src_text = open(os.path.join(_ROOT, 'scripts', 'sniper_batch_prepare_multilang.py'), encoding='utf-8').read()

# Extract between triple-quotes for each prompt
def extract_prompt(src, var_name):
    # Match: VAR_NAME = """..."""
    pattern = re.compile(rf'{var_name}\s*=\s*"""(.*?)"""', re.DOTALL)
    m = pattern.search(src)
    return m.group(1) if m else None

SYSTEM_PROMPT_TR = extract_prompt(src_text, 'SYSTEM_PROMPT_TR')
SYSTEM_PROMPT_AR = extract_prompt(src_text, 'SYSTEM_PROMPT_AR')

assert SYSTEM_PROMPT_TR, 'Could not extract SYSTEM_PROMPT_TR'
assert SYSTEM_PROMPT_AR, 'Could not extract SYSTEM_PROMPT_AR'

# ── User prompt builder (inline copy) ────────────────────────────────────────
def build_user_prompt(lead, lang_tag):
    notes   = lead.get('notes') or ''
    website = lead.get('website') or 'keine Website bekannt'
    phone   = lead.get('phone') or 'unbekannt'
    city    = lead.get('city') or lead.get('district') or 'Deutschland'
    contact = 'WhatsApp' if phone and phone != 'unbekannt' else 'E-Mail'

    has_booking = 'booking=y' in notes.lower()
    mobile_ok   = 'mobile=y' in notes.lower()
    ssl_ok      = 'ssl=y' in notes.lower()

    weaknesses = []
    if not has_booking: weaknesses.append('kein Online-Booking')
    if not mobile_ok:   weaknesses.append('mobile Optimierung fehlt')
    if not ssl_ok:      weaknesses.append('SSL-Problem')

    weakness_text = (', '.join(weaknesses) + ' — das kostet Neukunden.') if weaknesses \
                    else 'Potenzial bei Neukunden-Gewinnung über Google und Meta.'

    lang_label = 'türkischstämmig (TR_priority)' if lang_tag == 'TR' else 'arabischstämmig (AR_priority)'

    return (f"Salon: {lead['name']}\n"
            f"Stadt: {city}\n"
            f"Website: {website}\n"
            f"Kontakt via: {contact}\n"
            f"Kundschaft: {lang_label}\n"
            f"Audit-Befund: {weakness_text}\n\n"
            f"Schreib eine WhatsApp-Erstkontakt-Nachricht laut System-Anweisungen.")

# ── Sample leads ──────────────────────────────────────────────────────────────
SAMPLE_TR = {
    'id': 929, 'name': 'Salon Selam',
    'city': 'Berlin', 'district': None,
    'phone': '+49 30 123456', 'email': None,
    'website': None,
    'notes': '',
    'custom_message': None, 'status': 'READY TO SEND',
}
SAMPLE_AR = {
    'id': 283, 'name': 'Orient Barbershop Mall Of Berlin',
    'city': 'Berlin', 'district': None,
    'phone': '+49 30 654321', 'email': None,
    'website': 'http://orient-barbershop.de',
    'notes': 'ssl=n booking=n',
    'custom_message': None, 'status': 'READY TO SEND',
}

# ── Preview function ──────────────────────────────────────────────────────────
def preview(lead, lang_tag):
    system = SYSTEM_PROMPT_TR if lang_tag == 'TR' else SYSTEM_PROMPT_AR
    user   = build_user_prompt(lead, lang_tag)

    print(f'\n{"="*66}')
    print(f'  PREVIEW [{lang_tag}] — {lead["name"]}')
    print(f'  User prompt:')
    for line in user.split('\n'):
        print(f'    {line}')
    print(f'  Calling GPT-4o...\n')

    resp = client.chat.completions.create(
        model='gpt-4o',
        max_tokens=600,
        temperature=0.75,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user',   'content': user},
        ]
    )
    msg = resp.choices[0].message.content.strip()

    print(f'  РЕЗУЛЬТАТ:')
    print(f'  {"-"*64}')
    print(msg)
    print(f'  {"-"*64}')

    # Char count per block
    blocks = [b.strip() for b in msg.split('\n\n') if b.strip()]
    labels = ['🇩🇪 DE', '🇹🇷 TR' if lang_tag == 'TR' else '🇸🇦 AR']
    for i, b in enumerate(blocks):
        label = labels[i] if i < len(labels) else f'Block {i+1}'
        status = '✅' if len(b) <= 480 else f'⚠️  ДОВГИЙ'
        print(f'  {label}: {len(b)} chars {status}')
    print(f'{"="*66}')
    return msg

# ── Run ───────────────────────────────────────────────────────────────────────
print('\n>>> ДИРЕКТОР — PREVIEW перед запуском батчу <<<')
print('    Нові промпти: 10 мов | без лінку | CTA = відео-демо')
preview(SAMPLE_TR, 'TR')
preview(SAMPLE_AR, 'AR')
print('\n>>> Якщо якість ОК — запускати перегенерацію батчу <<<\n')
