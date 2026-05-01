#!/usr/bin/env python3
"""
lead_analyser_pro.py — Secret Phrase Generator for Munich Leads
Uses Claude claude-sonnet-4-6 to craft one hyper-personalized opener per salon.

Usage:
    python scripts/lead_analyser_pro.py                        # all 100 leads
    python scripts/lead_analyser_pro.py --limit 10             # first 10
    python scripts/lead_analyser_pro.py --dry-run              # no API calls, show prompt
    python scripts/lead_analyser_pro.py --out data/phrases.json

Output JSON: [{id, name, address, secret_phrase}, ...]
"""

import argparse
import configparser
import json
import os
import sys
import time
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "munich_intelligence_100.json"
DEFAULT_OUT = ROOT / "data" / "munich_phrases.json"

cfg = configparser.ConfigParser()
cfg.read(ROOT / "config.ini", encoding="utf-8")
ANTHROPIC_KEY = cfg.get("ANTHROPIC", "api_key", fallback=None) \
             or os.environ.get("ANTHROPIC_API_KEY")

# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_district(address: str) -> str:
    """Best-effort: pull the street name as district proxy."""
    if not address:
        return "München"
    # e.g. "Lindwurmstraße 8, 80337 München" → "Lindwurmstraße"
    street = address.split(",")[0].strip()
    # Remove house number
    parts = street.rsplit(" ", 1)
    return parts[0] if len(parts) == 2 and parts[1][0].isdigit() else street


def classify_business(name: str, website: str | None) -> str:
    """Rough category from name keywords."""
    n = name.lower()
    if any(k in n for k in ["barber", "barbershop", "barber shop"]):
        return "Barbershop"
    if any(k in n for k in ["nail", "nails", "nagel"]):
        return "Nagelstudio"
    if any(k in n for k in ["kosmetik", "kosmetikstudio", "beauty", "beautysalon"]):
        return "Kosmetikstudio"
    if any(k in n for k in ["friseur", "haarschnitt", "coiffeur", "hair"]):
        return "Friseursalon"
    if any(k in n for k in ["permanent make", "microblading", "pigment", "brow", "lash"]):
        return "PMU & Brow Studio"
    if any(k in n for k in ["medical", "med", "laser", "refresh"]):
        return "Medical Beauty"
    return "Beauty-Salon"


def build_prompt(lead: dict) -> str:
    name    = lead.get("name", "")
    address = lead.get("address", "")
    website = lead.get("website") or "–"
    pain    = lead.get("pain_quote") or None
    pain_r  = lead.get("pain_rating")
    comp    = lead.get("competitor_name") or None
    comp_r  = lead.get("competitor_rating")
    our_r   = lead.get("our_rating")
    district = extract_district(address)
    category = classify_business(name, website)

    context_lines = [f"Salon: {name}", f"Kategorie: {category}", f"Standort: {district} (München)"]
    if website and website != "–":
        context_lines.append(f"Website: {website}")
    if our_r:
        context_lines.append(f"Google-Bewertung: {our_r}")
    if comp:
        comp_line = f"Stärkster Konkurrent: {comp}"
        if comp_r:
            comp_line += f" ({comp_r}★)"
        context_lines.append(comp_line)
    if pain and pain_r:
        context_lines.append(f"Schwachstelle laut 1-Stern-Rezension: \"{pain[:200]}\"")

    context = "\n".join(context_lines)

    return f"""Du bist ein Elite-B2B-Sales-Copywriter, spezialisiert auf Münchener Beauty-Salons.

Schreibe GENAU EINEN Satz — die perfekte Eröffnungszeile für eine persönliche Outreach-Nachricht.

Regeln:
- Auf Deutsch
- Maximal 2 Sätze / 50 Wörter
- Zeige echtes Insiderwissen über DIESEN spezifischen Salon (Standort, Nische, Konkurrenz, Schwachstelle)
- Keine generischen Phrasen wie "Ich habe Ihren Salon gefunden"
- Keine Erwähnung von KI oder Automatisierung
- Ton: professionell, respektvoll, leicht überraschend — als käme es von jemandem, der genau hingeschaut hat
- Erzeugt sofort das Gefühl: "Der kennt mein Business wirklich"

Salon-Daten:
{context}

Antworte NUR mit dem einen Satz. Kein Prefix, keine Erklärung."""


def call_claude(prompt: str, client) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=120,
        temperature=0.9,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Generate secret phrases for Munich leads")
    parser.add_argument("--limit",   type=int, default=0, help="Process only first N leads (0=all)")
    parser.add_argument("--dry-run", action="store_true",  help="Print prompts, no API calls")
    parser.add_argument("--out",     default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--resume",  action="store_true",  help="Skip leads already in output file")
    args = parser.parse_args()

    # Load leads
    with open(DATA_FILE, encoding="utf-8") as f:
        leads = json.load(f)

    if args.limit:
        leads = leads[:args.limit]

    total = len(leads)
    print(f"[lead_analyser_pro] {total} leads loaded from {DATA_FILE.name}")

    # Resume: load existing output
    existing = {}
    out_path = Path(args.out)
    if args.resume and out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            for row in json.load(f):
                existing[row["id"]] = row
        print(f"[resume] {len(existing)} phrases already exist — skipping")

    if args.dry_run:
        for i, lead in enumerate(leads[:3]):
            print(f"\n{'='*60}\nLead #{lead['id']} — {lead['name']}")
            print(build_prompt(lead))
        print(f"\n[dry-run] Would process {total} leads. Exiting.")
        return

    if not ANTHROPIC_KEY or ANTHROPIC_KEY.startswith("PASTE"):
        print("ERROR: ANTHROPIC_API_KEY not set in config.ini [ANTHROPIC] api_key")
        print("       or environment variable ANTHROPIC_API_KEY")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    results = list(existing.values())
    done_ids = set(existing.keys())

    for i, lead in enumerate(leads):
        lead_id = lead["id"]
        if lead_id in done_ids:
            print(f"  [{i+1}/{total}] #{lead_id} {lead['name'][:40]} — SKIPPED (exists)")
            continue

        prompt = build_prompt(lead)
        print(f"  [{i+1}/{total}] #{lead_id} {lead['name'][:40]} ...", end=" ", flush=True)

        try:
            phrase = call_claude(prompt, client)
            print(f"OK")
            print(f"    → {phrase[:100]}")
        except Exception as e:
            print(f"ERROR: {e}")
            phrase = f"[ERROR: {e}]"

        results.append({
            "id":           lead_id,
            "name":         lead["name"],
            "address":      lead.get("address", ""),
            "category":     classify_business(lead["name"], lead.get("website")),
            "secret_phrase": phrase,
        })

        # Save incrementally after every lead
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # Polite rate-limit pause between calls
        if i < total - 1:
            time.sleep(0.4)

    print(f"\n[done] {len(results)} phrases saved → {out_path}")

    # Pretty-print summary
    print("\n── SAMPLE OUTPUT ───────────────────────────────────────")
    for row in results[:5]:
        print(f"\n#{row['id']} {row['name']}")
        print(f"  {row['secret_phrase']}")


if __name__ == "__main__":
    main()
