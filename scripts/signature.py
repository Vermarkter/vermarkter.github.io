#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
signature.py — Vermarkter Elite: get_signature(lead) helper.

Rules:
  1. Default cold-contact signature: "Team My-Salon" (DACH/EU)
  2. France (city in FR_CITIES): "Équipe My-Salon"
  3. Ukrainian signal detected in name/owner_name/notes/brand: "Andrii | My-Salon"

Priority: Ukrainian signal > France > default.

Usage:
    from scripts.signature import get_signature
    sig = get_signature(lead)   # lead is a dict with keys: name, city, notes, etc.
"""

import re

# ── Ukrainian name markers (transliterated) ───────────────────────────────────
_UA_NAMES = {
    "andrii", "andriy", "oleksandr", "olexandr", "olena", "iryna",
    "yuliia", "tetiana", "tetyana", "mykhailo", "mykola", "bohdan",
    "yaroslav", "yevhen", "evhen", "yevheniia", "ievheniia", "sofiia",
    "anastasiia", "liudmyla", "lyudmyla", "halyna", "svitlana",
    "kateryna", "nadiia", "oleh", "serhii", "sergii", "ihor",
    "taras", "volodymyr", "vladyslav", "ostap", "nazar", "solomiia",
    "yaroslava", "bohdana", "zoryana", "lesia", "lesya", "ulyana",
    "uliana", "stepan", "zinaida", "zinovii", "zinoviy",
}

# ── Ukrainian context markers ─────────────────────────────────────────────────
_UA_CONTEXT = re.compile(
    r'\b(ukrainian|ukraine|ukr(?!\w)|ua(?!\w)|україн|україна|украин'
    r'|ukrainisch|ukrainische|київ|kyiv|lviv|львів|odesa|odessa)\b',
    re.IGNORECASE,
)

# ── French cities ─────────────────────────────────────────────────────────────
_FR_CITIES = {'nice', 'cannes', 'paris', 'lyon', 'marseille', 'monaco',
              'bordeaux', 'toulouse', 'strasbourg', 'nantes', 'lille'}

# ── Word tokenizer (letters only, lowercase) ──────────────────────────────────
_WORD_RE = re.compile(r"[a-zA-ZÀ-öø-ÿ']+")


def _has_ukrainian_signal(lead: dict) -> bool:
    fields = [
        lead.get('name') or '',
        lead.get('owner_name') or '',
        lead.get('notes') or '',
        lead.get('brand') or '',
    ]
    blob = ' '.join(fields)

    # Check context markers first (regex, handles Cyrillic too)
    if _UA_CONTEXT.search(blob):
        return True

    # Check name markers as whole words
    words = {w.lower() for w in _WORD_RE.findall(blob)}
    return bool(words & _UA_NAMES)


def get_signature(lead: dict) -> str:
    """Return the correct cold-contact signature string for this lead."""
    if _has_ukrainian_signal(lead):
        return 'Andrii | My-Salon'

    city = (lead.get('city') or lead.get('district') or '').strip().lower()
    if city in _FR_CITIES:
        return 'Équipe My-Salon'

    return 'Team My-Salon'
