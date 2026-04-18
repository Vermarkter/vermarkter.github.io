# -*- coding: utf-8 -*-
"""
mass_email_sender.py — Vermarkter Beauty-Outreach E-Mail-Maschine
==================================================================
• Zieht aus Supabase beauty_leads alle Leads mit email IS NOT NULL
  und status = 'new'.
• Erzeugt pro Lead eine personalisierte HTML-Mail (DE oder EN), nutzt
  custom_message falls vorhanden — sonst Gold-Master-Fallback.
• Versendet per SMTP, markiert nach Erfolg status = 'sent'
  und last_contacted = NOW().

Setup:
  setx SMTP_HOST   "smtp.zoho.eu"         (einmalig)
  setx SMTP_PORT   "465"
  setx SMTP_USER   "hello@vermarkter.eu"
  setx SMTP_PASS   "***app-password***"
  setx SMTP_FROM   "Vermarkter <hello@vermarkter.eu>"

Dry-Run (kein Versand, kein DB-Update):
  python mass_email_sender.py --dry-run --limit 5

Echter Versand:
  python mass_email_sender.py --limit 50
"""

import os, sys, io, time, json, argparse, smtplib, ssl, re, configparser
import urllib.request, urllib.parse, urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text     import MIMEText
from email.utils         import formataddr, make_msgid

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Credentials (config.ini) ─────────────────────────────────────────────────
_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"), encoding="utf-8")
SB_URL  = _cfg["CREDENTIALS"]["supabase_url"]
SB_KEY  = _cfg["CREDENTIALS"]["supabase_key"]
SB_HEAD = {"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
           "Content-Type": "application/json"}

# ── Branding ────────────────────────────────────────────────────────────────
DEMO_URL   = "https://vermarkter.vercel.app/SERVICES/beauty-industry/de/"
SITE_URL   = "https://vermarkter.vercel.app/de/"
BRAND      = "Vermarkter"
REPLY_NAME = "Vermarkter Team"

# ── SMTP aus ENV ────────────────────────────────────────────────────────────
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "Vermarkter <hello@vermarkter.eu>")

# ── HTTP helpers ────────────────────────────────────────────────────────────
def sb_get(path):
    req = urllib.request.Request(SB_URL + path, headers=SB_HEAD)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def sb_patch(lead_id, payload):
    body = json.dumps(payload).encode("utf-8")
    h = dict(SB_HEAD); h["Prefer"] = "return=minimal"
    url = SB_URL + "/rest/v1/beauty_leads?id=eq." + str(lead_id)
    req = urllib.request.Request(url, data=body, headers=h, method="PATCH")
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status

def fetch_targets(limit):
    q = ("/rest/v1/beauty_leads?select=id,name,email,city,district,custom_message"
         "&email=not.is.null&status=eq.new&order=id.asc&limit=" + str(limit))
    return sb_get(q)

# ── Salutation + subject ────────────────────────────────────────────────────
def is_english_mailbox(email):
    dom = email.split("@", 1)[1].lower() if "@" in email else ""
    return dom.endswith((".com", ".co.uk", ".io"))

def salutation(name, lang):
    m = re.search(r"(?:Salon|Friseur|Studio|Barbier)\s+([A-Z][a-z]+)", name or "")
    fn = m.group(1) if m else None
    if lang == "en":
        return "Hi " + fn + "," if fn else "Hello,"
    return "Hallo " + fn + "!" if fn else "Guten Tag,"

def subject_for(lead, lang):
    name = lead.get("name") or "Ihr Salon"
    if lang == "en":
        return name + " — 24/7 AI booking, zero commission"
    return name + " — 24/7 KI-Buchung, null Provision"

# ── HTML template ───────────────────────────────────────────────────────────
# Zuerst versuchen, luxury_template.html von der Platte zu laden (dark-navy
# glassmorphism). Fallback: eingebettetes Minimal-Template.
def _load_luxury():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "luxury_template.html"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None

HTML_TPL = _load_luxury() or """<!doctype html>
<html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title></head>
<body style="margin:0;padding:0;background:#0a0a0f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#f1f5f9;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0f;padding:32px 16px;">
  <tr><td align="center">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;background:#11111a;border:1px solid rgba(255,255,255,.06);border-radius:18px;overflow:hidden;">
      <tr><td style="padding:28px 32px 8px 32px;">
        <div style="display:inline-block;width:44px;height:44px;line-height:44px;text-align:center;border-radius:12px;background:linear-gradient(135deg,#ec4899,#8b5cf6);font-weight:900;font-size:22px;color:#fff;">V</div>
        <span style="display:inline-block;vertical-align:middle;margin-left:10px;font-weight:800;letter-spacing:.3px;font-size:18px;color:#f1f5f9;">Vermarkter</span>
      </td></tr>
      <tr><td style="padding:8px 32px 0 32px;">
        <p style="margin:16px 0 6px 0;font-size:16px;line-height:1.55;color:#e2e8f0;">{salut}</p>
        <div style="font-size:15px;line-height:1.65;color:#cbd5e1;white-space:pre-wrap;">{body}</div>
      </td></tr>
      <tr><td align="center" style="padding:26px 32px 8px 32px;">
        <a href="{demo}" style="display:inline-block;padding:14px 28px;border-radius:12px;background:linear-gradient(135deg,#ec4899,#8b5cf6);color:#fff;text-decoration:none;font-weight:800;font-size:15px;letter-spacing:.3px;">{cta}</a>
      </td></tr>
      <tr><td align="center" style="padding:6px 32px 26px 32px;">
        <a href="{site}" style="color:#94a3b8;font-size:13px;text-decoration:none;">{site_label}</a>
      </td></tr>
      <tr><td style="padding:18px 32px 26px 32px;border-top:1px solid rgba(255,255,255,.06);">
        <p style="margin:0;font-size:12px;line-height:1.5;color:#64748b;">{signoff}<br>{brand} · {reply_name}</p>
        <p style="margin:10px 0 0 0;font-size:11px;color:#475569;">{unsub}</p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>
"""

def render_html(lead, lang):
    name = lead.get("name") or "Ihr Salon"
    salut = salutation(name, lang)
    body  = (lead.get("custom_message") or "").strip()
    if not body:
        if lang == "en":
            body = (name + " — we build your own digital presence: Website + App + CRM "
                    "with a 24/7 AI receptionist. One-time 1,000 €. No monthly fees.")
        else:
            body = (name + " — wir bauen deine eigene digitale Heimat: Website + App + CRM "
                    "mit 24/7 KI-Rezeption. Einmalig 1.000 €. Keine Monatskosten.")

    if lang == "en":
        cta = "See live demo"
        site_label = "vermarkter.vercel.app"
        signoff = "Best regards,"
        unsub = ("You receive this message because your salon is listed publicly. "
                 "Reply STOP to opt out.")
        subject = subject_for(lead, lang)
    else:
        cta = "Live-Demo ansehen"
        site_label = "vermarkter.vercel.app"
        signoff = "Mit besten Grüßen,"
        unsub = ("Du erhältst diese Nachricht, weil dein Salon öffentlich gelistet ist. "
                 "Antworte STOP, um dich auszutragen.")
        subject = subject_for(lead, lang)

    html = HTML_TPL.format(
        lang=lang, subject=subject, salut=salut, body=body,
        demo=DEMO_URL, cta=cta, site=SITE_URL, site_label=site_label,
        signoff=signoff, brand=BRAND, reply_name=REPLY_NAME, unsub=unsub)
    plain = salut + "\n\n" + body + "\n\n" + cta + ": " + DEMO_URL + "\n\n" + signoff + "\n" + BRAND
    return subject, html, plain

# ── SMTP send ──────────────────────────────────────────────────────────────-
def send_one(lead, dry_run):
    email = (lead.get("email") or "").strip()
    if not email:
        return False, "no email"
    lang = "en" if is_english_mailbox(email) else "de"
    subject, html, plain = render_html(lead, lang)

    if dry_run:
        print("   [DRY] →", email, "|", subject[:60])
        return True, "dry"

    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return False, "SMTP env missing"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_FROM
    msg["To"]      = email
    msg["Message-ID"] = make_msgid(domain="vermarkter.eu")
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html,  "html",  "utf-8"))

    ctx = ssl.create_default_context()
    try:
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=20) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
                s.ehlo(); s.starttls(context=ctx); s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, "smtp: " + str(e)

# ── Main ───────────────────────────────────────────────────────────────────-
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit",   type=int, default=50, help="max leads per run")
    ap.add_argument("--dry-run", action="store_true", help="render only, no SMTP, no DB patch")
    ap.add_argument("--delay",   type=float, default=4.0, help="seconds between sends")
    args = ap.parse_args()

    print("Vermarkter Mass Email Sender")
    print("SMTP:", SMTP_HOST or "(env missing)", "| dry_run:", args.dry_run, "| limit:", args.limit)

    targets = fetch_targets(args.limit)
    print("Targets:", len(targets))

    ok = fail = 0
    for i, lead in enumerate(targets, 1):
        name = (lead.get("name") or "")[:40]
        print("[%d/%d] %s → %s" % (i, len(targets), name, lead.get("email")), end=" ")
        sent, note = send_one(lead, args.dry_run)
        if sent:
            ok += 1
            print("OK", note)
            if not args.dry_run:
                try:
                    sb_patch(lead["id"], {"status": "sent",
                                          "last_contacted": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                except Exception as e:
                    print("   [patch fail]", e)
        else:
            fail += 1
            print("FAIL", note)
        if not args.dry_run and i < len(targets):
            time.sleep(args.delay)

    print("\nDONE — sent: %d | failed: %d" % (ok, fail))

if __name__ == "__main__":
    main()
