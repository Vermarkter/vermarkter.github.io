#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lead DNA Enricher — Vermarkter Elite
Збирає «ДНК» салонів: бренди, топ-послуги, цінові точки.
Використовує 10 паралельних потоків + Claude API для аналізу.
"""

import os
import sys
import io
import json
import time
import logging
import re
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ─── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL  = os.environ["SUPABASE_URL"]
SUPABASE_KEY  = os.environ["SUPABASE_KEY"]
ANTHROPIC_KEY = os.environ["ANTHROPIC_API_KEY"]

CITIES     = ["München", "Berlin"]
STATUS     = "READY TO SEND"
THREADS    = 10
MODEL      = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 1200

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("dna_enricher")

# ─── Supabase helpers ──────────────────────────────────────────────────────────

HEADERS_SB = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}


def sb_get(path: str, params: dict = None) -> list:
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    r = httpx.get(url, headers=HEADERS_SB, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def sb_upsert(table: str, payload: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {**HEADERS_SB, "Prefer": "resolution=merge-duplicates,return=minimal"}
    r = httpx.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()


def sb_patch(table: str, lead_id: int, payload: dict) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {"id": f"eq.{lead_id}"}
    r = httpx.patch(url, headers=HEADERS_SB, params=params, json=payload, timeout=30)
    r.raise_for_status()


# ─── Fetch leads ───────────────────────────────────────────────────────────────

def fetch_leads(city: str = None, limit: int = 0, offset: int = 0) -> list:
    if city:
        city_filter = f'"{city}"'
        city_param  = f"in.({city_filter})"
    else:
        city_param = "in.(" + ",".join(f'"{c}"' for c in CITIES) + ")"

    params = {
        "status": f"eq.{STATUS}",
        "city":   city_param,
        "select": "id,name,website,city,notes",
        "order":  "id.asc",
    }
    if limit:
        params["limit"]  = str(limit)
        params["offset"] = str(offset)

    leads = sb_get("beauty_leads", params)
    log.info(f"Знайдено {len(leads)} лідів зі статусом '{STATUS}'")
    return leads


# ─── Website scraping ─────────────────────────────────────────────────────────

def fetch_website(url: str, timeout: int = 15) -> str:
    if not url:
        return ""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        headers = {
            "User-Agent":      (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        }
        r = httpx.get(url, headers=headers, follow_redirects=True, timeout=timeout)
        r.raise_for_status()
        text = r.text
        text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>",   " ", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return text[:8000]
    except Exception as exc:
        log.warning(f"Не вдалось завантажити {url}: {exc}")
        return ""


# ─── Claude DNA analysis ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """
Ти — аналітик б'юті-індустрії. Тобі дають текст сайту перукарні / салону краси.

Визнач:
1. brand_stack     — список косметичних брендів (Wella, Kerastase, Schwarzkopf, Oribe, L'Oréal, Goldwell, BHAVE, Davines тощо). Якщо не знайдено — порожній список.
2. top_service     — найдорожча / преміум послуга (Balayage, Extensions, Laser, Keratin, Color Correction тощо). Одна назва.
3. price_point     — ціна стандартної стрижки або базової послуги у форматі "€XX" або "€XX–€XX". Якщо невідомо — null.
4. positioning     — 1-2 слова: Budget / Mid-range / Premium / Luxury.
5. booking_system  — назва системи онлайн-запису (Treatwell, Booksy, Fresha, власна тощо) або null.

Відповідай ТІЛЬКИ валідним JSON без зайвого тексту:
{
  "brand_stack": [...],
  "top_service": "...",
  "price_point": "...",
  "positioning": "...",
  "booking_system": "..."
}
"""

HEADERS_AI = {
    "x-api-key":         ANTHROPIC_KEY,
    "anthropic-version": "2023-06-01",
    "content-type":      "application/json",
}


def analyze_with_claude(salon_name: str, website_text: str) -> dict:
    if not website_text:
        return {
            "brand_stack":    [],
            "top_service":    None,
            "price_point":    None,
            "positioning":    "Unknown",
            "booking_system": None,
            "enriched_at":    datetime.utcnow().isoformat(),
            "source":         "no_website",
        }

    user_msg = f"Салон: {salon_name}\n\nТекст сайту:\n{website_text}"

    payload = {
        "model":      MODEL,
        "max_tokens": MAX_TOKENS,
        "system":     SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": user_msg}],
    }

    for attempt in range(3):
        try:
            r = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers=HEADERS_AI,
                json=payload,
                timeout=60,
            )
            r.raise_for_status()
            raw = r.json()["content"][0]["text"].strip()
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"```$", "", raw).strip()
            dna = json.loads(raw)
            dna["enriched_at"] = datetime.utcnow().isoformat()
            dna["source"]      = "website_scraped"
            return dna
        except Exception as exc:
            log.warning(f"Claude спроба {attempt+1} для '{salon_name}': {exc}")
            time.sleep(2 ** attempt)

    return {
        "brand_stack":    [],
        "top_service":    None,
        "price_point":    None,
        "positioning":    "Unknown",
        "booking_system": None,
        "enriched_at":    datetime.utcnow().isoformat(),
        "source":         "analysis_failed",
    }


# ─── Save DNA ─────────────────────────────────────────────────────────────────

def ensure_table_exists() -> None:
    try:
        sb_get("lead_details", {"limit": "1"})
    except httpx.HTTPStatusError as e:
        if e.response.status_code in (404, 400):
            log.error(
                "Таблиця lead_details не існує!\n"
                "Виконай в Supabase SQL Editor:\n\n"
                "CREATE TABLE lead_details (\n"
                "  id             SERIAL PRIMARY KEY,\n"
                "  lead_id        INT UNIQUE REFERENCES beauty_leads(id),\n"
                "  brand_stack    JSONB,\n"
                "  top_service    TEXT,\n"
                "  price_point    TEXT,\n"
                "  positioning    TEXT,\n"
                "  booking_system TEXT,\n"
                "  source         TEXT,\n"
                "  enriched_at    TIMESTAMPTZ DEFAULT NOW()\n"
                ");\n"
            )
            raise


def save_dna(lead: dict, dna: dict) -> None:
    record = {
        "lead_id":        lead["id"],
        "brand_stack":    json.dumps(dna.get("brand_stack", [])),
        "top_service":    dna.get("top_service"),
        "price_point":    dna.get("price_point"),
        "positioning":    dna.get("positioning"),
        "booking_system": dna.get("booking_system"),
        "source":         dna.get("source"),
        "enriched_at":    dna.get("enriched_at"),
    }
    sb_upsert("lead_details", record)

    note_summary = (
        f"[DNA {dna.get('enriched_at', '')[:10]}] "
        f"Brands: {', '.join(dna.get('brand_stack', []) or ['—'])} | "
        f"Top: {dna.get('top_service') or '—'} | "
        f"Price: {dna.get('price_point') or '—'} | "
        f"{dna.get('positioning') or '—'}"
    )
    sb_patch("beauty_leads", lead["id"], {"notes": note_summary})


# ─── Worker ───────────────────────────────────────────────────────────────────

def enrich_lead(lead: dict) -> dict:
    name    = lead.get("name", "?")
    website = lead.get("website", "")
    log.info(f"Processing: {name} | {website or 'no website'}")

    website_text = fetch_website(website)
    dna = analyze_with_claude(name, website_text)
    save_dna(lead, dna)

    log.info(
        f"Done: {name} -> {dna.get('positioning')} | "
        f"brands={dna.get('brand_stack')} | "
        f"top={dna.get('top_service')} | "
        f"price={dna.get('price_point')}"
    )
    return {"lead_id": lead["id"], "name": name, "dna": dna}


# ─── Main ─────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Lead DNA Enricher — Vermarkter Elite")
    p.add_argument("--city",   default="München", help="City filter (default: München)")
    p.add_argument("--limit",  type=int, default=100, help="Max leads (default: 100)")
    p.add_argument("--offset", type=int, default=0,   help="Supabase offset (default: 0)")
    p.add_argument("--threads",type=int, default=THREADS, help=f"Parallel threads (default: {THREADS})")
    p.add_argument("--dry-run",action="store_true",   help="Fetch + scrape only, no Claude call, no DB write")
    return p.parse_args()


def main():
    args = parse_args()

    log.info("=" * 60)
    log.info("  LEAD DNA ENRICHER — Vermarkter Elite")
    log.info(f"  Model: {MODEL}  |  City: {args.city}  |  Limit: {args.limit}")
    log.info(f"  Threads: {args.threads}  |  {'DRY-RUN' if args.dry_run else 'LIVE'}")
    log.info("=" * 60)

    if not args.dry_run:
        ensure_table_exists()

    leads = fetch_leads(city=args.city, limit=args.limit, offset=args.offset)

    if not leads:
        log.warning("No leads found — check filters.")
        return

    results = []
    failed  = []

    with ThreadPoolExecutor(max_workers=args.threads, thread_name_prefix="enricher") as pool:
        if args.dry_run:
            for lead in leads:
                name = lead.get("name", "?")
                text = fetch_website(lead.get("website", ""))
                log.info(f"[DRY] {name} | website chars: {len(text)}")
                results.append({"lead_id": lead["id"], "name": name, "chars": len(text)})
        else:
            futures = {pool.submit(enrich_lead, lead): lead for lead in leads}
            for future in as_completed(futures):
                lead = futures[future]
                try:
                    results.append(future.result())
                except Exception as exc:
                    log.error(f"Error for {lead.get('name')}: {exc}")
                    failed.append(lead.get("id"))

    log.info("")
    log.info("=" * 60)
    log.info(f"  DONE: {len(results)} ok / {len(failed)} failed")
    if failed:
        log.info(f"  Failed IDs: {failed}")
    log.info("=" * 60)

    if not args.dry_run:
        report_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "dna_enrichment_report.json"
        )
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "run_at":  datetime.utcnow().isoformat(),
                "model":   MODEL,
                "city":    args.city,
                "total":   len(leads),
                "success": len(results),
                "failed":  failed,
                "results": results,
            }, f, ensure_ascii=False, indent=2)
        log.info(f"  Report saved: {report_path}")

    # Print first 3 results for Director review
    if results and not args.dry_run:
        print("\n" + "=" * 60)
        print("  ПЕРШІ 3 ДНК ДЛЯ ПЕРЕВІРКИ:")
        print("=" * 60)
        for r in results[:3]:
            dna = r.get("dna", {})
            print(f"\n  Салон: {r['name']} (id={r['lead_id']})")
            print(f"  Бренди:    {dna.get('brand_stack', [])}")
            print(f"  Топ послуга: {dna.get('top_service')}")
            print(f"  Ціна:      {dna.get('price_point')}")
            print(f"  Сегмент:   {dna.get('positioning')}")
            print(f"  Запис:     {dna.get('booking_system')}")
            print(f"  Джерело:   {dna.get('source')}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
