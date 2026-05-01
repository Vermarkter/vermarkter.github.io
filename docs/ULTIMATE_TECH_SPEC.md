# Технічна Конституція Vermarkter
## Повна архітектурна специфікація · v1.0 · Травень 2026

---

## ЗМІСТ

1. [Огляд системи та місія](#1-огляд-системи-та-місія)
2. [Архітектура бази даних](#2-архітектура-бази-даних)
3. [Логіка снайперських офферів](#3-логіка-снайперських-офферів)
4. [Структура email-воронки](#4-структура-email-воронки)
5. [Frontend: лендінг-система](#5-frontend-лендінг-система)
6. [Backend: Python-інфраструктура](#6-backend-python-інфраструктура)
7. [Serverless: Vercel API](#7-serverless-vercel-api)
8. [Аналітика та моніторинг](#8-аналітика-та-моніторинг)
9. [10 Вразливостей та план виправлення](#9-10-вразливостей-та-план-виправлення)
10. [Інструкція розгортання на нових серверах](#10-інструкція-розгортання-на-нових-серверах)
11. [Roadmap та масштабування](#11-roadmap-та-масштабування)

---

## 1. Огляд системи та місія

### 1.1 Що таке Vermarkter

Vermarkter — це B2B outreach-машина, побудована для продажу IT/Marketing-пакетів салонам краси, барбершопам і косметичним студіям у Берліні та Мюнхені. Система повністю автоматизує цикл:

```
Виявлення ліда → Збагачення даними → Персоналізований email → 
Tracking відкриття → Telegram-сповіщення → Follow-up → Booking
```

Архітектура побудована на принципі «нульового сервера» — жодних власних VPS для основного потоку. Vercel (serverless), Supabase (PostgreSQL-as-a-service) і Brevo (email delivery) формують безсерверний стек, який коштує ~$0/місяць при поточних обсягах.

### 1.2 Стек технологій

| Шар | Технологія | Призначення |
|-----|-----------|-------------|
| Database | Supabase (PostgreSQL) | Зберігання лідів, статусів, аналітики |
| Email Delivery | Brevo API | 300 листів/день безкоштовно |
| Serverless | Vercel (Node.js) | Tracking pixel, API endpoints |
| Frontend | Vanilla HTML/CSS/JS | 48 лендінг-сторінок (6 мов × 8 типів) |
| Hosting | GitHub Pages | `vermarkter.github.io` |
| Enrichment | Google Maps Places API | Фото фасадів, рейтинги, відгуки |
| AI Analysis | Claude claude-sonnet-4-6 | Персоналізовані фрази, аналіз лідів |
| AI Classification | GPT-4o-mini | Класифікація відповідей HOT/INFO/REFUSE |
| Monitoring | Python HTTP server | Dashboard на порту 8888 |

### 1.3 Географічний фокус

- **Phase 1 (активна):** Берлін — ~1710 лідів, 95.9% покритих фото
- **Phase 2 (в процесі):** Мюнхен — 100 лідів у `munich_intelligence_100.json`
- **Phase 3 (запланована):** Відень, Цюрих, Гамбург

### 1.4 Ключові метрики

- **База лідів:** 1710+ салонів Берліна, 100 Мюнхена
- **Покриття фото:** 1640/1710 = 95.9%
- **Email ліміт:** 300/день (Brevo free tier)
- **Delivery rate:** мета >95% (Brevo репутація)
- **Open rate:** мета >35% (персоналізація + pixel tracking)

---

## 2. Архітектура бази даних

### 2.1 Основна таблиця: `beauty_leads`

```sql
CREATE TABLE beauty_leads (
    id                  SERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    address             TEXT,
    city                TEXT DEFAULT 'Berlin',
    phone               TEXT,
    email               TEXT,
    website             TEXT,
    maps_url            TEXT,
    place_id            TEXT,
    our_rating          NUMERIC(3,1),
    
    -- Competitor intelligence
    competitor_name     TEXT,
    competitor_rating   NUMERIC(3,1),
    competitor_address  TEXT,
    
    -- Pain signal (1-star review mining)
    pain_quote          TEXT,
    pain_rating         INTEGER,
    
    -- Visual enrichment
    street_view_url     TEXT,     -- Google Places photo URL
    
    -- Email funnel
    email_funnel_json   JSONB,    -- {subject, body, demo_url, ...}
    
    -- Tracking & CRM
    status              TEXT DEFAULT 'new',
    last_opened_at      TIMESTAMPTZ,
    reply_text          TEXT,
    
    -- Metadata
    created_at          TIMESTAMPTZ DEFAULT now(),
    updated_at          TIMESTAMPTZ DEFAULT now()
);
```

### 2.2 Статусна машина (State Machine)

```
new
 │
 ├─── email_sent      (Brevo відправив)
 │     │
 │     ├─── [pixel fired] → last_opened_at updated
 │     │
 │     ├─── reply_hot      (GPT: хоче demo/зустріч)
 │     ├─── reply_info     (GPT: питає ціну)
 │     ├─── reply_refused  (GPT: не цікаво)
 │     │
 │     └─── followup_sent  (WhatsApp follow-up через 2г після відкриття)
 │
 ├─── booked          (підтвердив demo-дзвінок)
 ├─── CALLED          (дзвінок відбувся)
 └─── closed_lost     (остаточна відмова)
```

### 2.3 Індекси (рекомендовані)

```sql
CREATE INDEX idx_beauty_leads_status ON beauty_leads(status);
CREATE INDEX idx_beauty_leads_city ON beauty_leads(city);
CREATE INDEX idx_beauty_leads_last_opened ON beauty_leads(last_opened_at) 
    WHERE last_opened_at IS NOT NULL;
CREATE INDEX idx_beauty_leads_email ON beauty_leads(email) 
    WHERE email IS NOT NULL;
```

### 2.4 Row Level Security (RLS)

Поточний стан: RLS вимкнено (використовуємо `service_role_key` з Python, `anon_key` для Vercel tracking). 

**Рекомендована конфігурація RLS:**

```sql
-- Enable RLS
ALTER TABLE beauty_leads ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS (для Python scripts)
-- anon role — тільки UPDATE last_opened_at через tracking pixel
CREATE POLICY "tracking_pixel_update" ON beauty_leads
    FOR UPDATE
    TO anon
    USING (true)
    WITH CHECK (
        -- Дозволяємо оновлювати ТІЛЬКИ last_opened_at
        (xmax = 0) OR (last_opened_at IS NOT NULL)
    );
```

### 2.5 JSONB структура `email_funnel_json`

```json
{
  "subject": "Digitale Lösung für Beauty Lounge — Demo in 60 Sekunden",
  "preview_text": "Wir haben Ihren Salon analysiert...",
  "body_lines": [
    "Sehr geehrte Frau Müller,",
    "...",
    "Mit freundlichen Grüßen"
  ],
  "demo_url": "https://vermarkter.github.io/services/beauty-industry/de/?s=Beauty%20Lounge",
  "tracking_pixel_url": "https://vermarkter-kohl.vercel.app/api/track?id=162",
  "cta_label": "Kostenlose Demo ansehen",
  "generated_at": "2026-05-01T12:00:00Z",
  "batch": 4,
  "language": "de"
}
```

### 2.6 Важливі SQL міграції

Всі міграції зберігаються в `scripts/*.sql`. Виконуються вручну через Supabase SQL Editor:

```
scripts/add_email_funnel_column.sql   -- email_funnel_json jsonb
scripts/add_reply_columns.sql          -- reply_text text
scripts/add_tracking_column.sql        -- last_opened_at timestamptz
scripts/whatsapp_logs_schema.sql       -- таблиця логів WhatsApp
```

---

## 3. Логіка снайперських офферів

### 3.1 Концепція Sniper Engine

Снайперський оффер — це не масова розсилка. Це гіперперсоналізоване повідомлення, побудоване на 5 шарах розвідки:

```
Шар 1: Базова ідентифікація (назва, адреса, район)
Шар 2: Competitor Intelligence (хто конкурент, його рейтинг)
Шар 3: Pain Signal (1-зіркові відгуки — реальні скарги клієнтів)
Шар 4: Visual Proof (фото фасаду через Google Places)
Шар 5: Brand DNA (тип бізнесу, сайт, позиціонування)
```

### 3.2 Пайплайн збагачення даних

```
scripts/sniper_fetch.py
    │
    ├── Google Maps Places Search API
    │   └── place_id, rating, address, maps_url
    │
    └── scripts/enrich_street_view.py
            │
            ├── Places Photos API (v1)
            │   └── street_view_url (фото фасаду)
            │
            └── Supabase PATCH → beauty_leads.street_view_url
```

**`scripts/sniper_fetch.py`** — основний скрейпер:
```python
# Логіка пошуку: текстовий запит по Maps API
search_query = f"{salon_name} {city}"
# → places/textsearch endpoint
# → extracting: place_id, name, rating, address, website
```

**`scripts/enrich_street_view.py`** — збагачення фото:
```python
# Google Places Photos API v1
# GET /v1/places/{place_id}?fields=photos
# → photoUri: "https://maps.googleapis.com/maps/api/place/photo?..."
# → перший результат = фото фасаду
```

### 3.3 Pain Mining: алгоритм пошуку слабкостей

```python
# scripts/fetch_reviews.py
# Алгоритм:
# 1. Беремо place_id ліда
# 2. Запит до Places API: reviews (rating <= 2)
# 3. Якщо є — зберігаємо найемоційніший (за довжиною + ключові слова)
# 4. Поля: pain_quote, pain_rating

PAIN_KEYWORDS = [
    'warten', 'abgesagt', 'termin', 'krank', 'bescheid',
    'nicht', 'schlecht', 'nie wieder', 'enttäuscht'
]
# Текст з хоча б одним ключовим словом = релевантний pain
```

### 3.4 Competitor Intelligence

```python
# scripts/sniper_fetch.py
# Конкурент = найближчий бізнес з тієї ж категорії
# але з ВИЩИМ рейтингом
# Логіка:
# 1. nearbySearch навколо координат ліда (radius=500m)
# 2. Фільтр: тип=beauty_salon|hair_care|spa
# 3. Сортування: rating DESC
# 4. Перший результат != сам лід → конкурент
```

### 3.5 Lead DNA Enricher

`scripts/lead_dna_enricher.py` — найважчий аналітичний модуль:

```python
# Для кожного ліда:
# 1. Fetch website HTML
# 2. Витягнути: бренд-продукти (Olaplex, BABOR, Kerastase)
#              соцмережі (Instagram followers)
#              методи бронювання (Treatwell, Booksy, власна)
#              цінова категорія (keywords: premium, luxus, günstig)
# 3. Зберегти в Supabase як JSON
```

### 3.6 Secret Phrase Generation (Claude claude-sonnet-4-6)

`scripts/lead_analyser_pro.py` — AI-генерація персоналізованих фраз:

```
Вхід: {name, address, category, competitor, pain_quote, our_rating}
↓
Промпт для Claude: "Ти elite B2B copywriter. Напиши 1 речення-відкривачку..."
↓
Вихід: "Da Ihr Salon direkt gegenüber vom stark bewerteten [Konkurrent] liegt, 
        wissen wir genau, was Ihre Kunden heute entscheiden lässt."
```

Промпт-інжиніринг:
- `temperature=0.9` — висока варіативність, кожна фраза унікальна
- `max_tokens=120` — жорстке обмеження довжини
- Система-інструкція містить заборони: без "KI", без "Automatisierung", без генеричних фраз

---

## 4. Структура email-воронки

### 4.1 Загальна архітектура воронки

```
День 0: Cold Email (Brevo) — персоналізований, з фото фасаду + Play-кнопка
   ↓
Tracking Pixel (Vercel) → Supabase UPDATE last_opened_at
   ↓ (якщо відкрито)
Telegram Alert → Директор отримує ім'я + WhatsApp ліда
   ↓ (якщо не відповів через 2 години)
Day 2: Smart Follow-up (WhatsApp) — "Ви переглянули наш аудит?"
   ↓
Відповідь → GPT-4o-mini класифікує: HOT / INFO / REFUSE
   ↓
HOT → Booking дзвінок (Calendly)
INFO → Ціновий лист + FAQ
REFUSE → Архів (6-місячний cooldown)
```

### 4.2 HTML Email архітектура

**Файл:** `scripts/send_email_brevo.py`

Структура HTML листа (MSO-сумісний):

```
┌─────────────────────────────────┐
│  HEADER: Vermarkter logo + nav  │
├─────────────────────────────────┤
│  HERO BLOCK:                    │
│  [Фото фасаду салону]           │
│  [▶ Play button overlay]        │  ← SVG data URI
│  (клік → персоналізований demo) │
├─────────────────────────────────┤
│  BODY: персоналізований текст   │
│  • Pain point згадка            │
│  • 3 переваги системи           │
│  • CTA кнопка (demo URL ?s=)    │
├─────────────────────────────────┤
│  SOCIAL PROOF: рейтинги         │
├─────────────────────────────────┤
│  FOOTER: unsubscribe + legal    │
└─────────────────────────────────┘
<!--[if mso]> Outlook fallback  <![endif]-->
```

### 4.3 Tracking Pixel механіка

```html
<!-- В кінці email body -->
<img src="https://vermarkter-kohl.vercel.app/api/track?id=162" 
     width="1" height="1" style="display:none;" />
```

**Vercel Function flow:**
```
GET /api/track?id=162
    │
    ├── PATCH beauty_leads SET last_opened_at=now() WHERE id=162
    │
    ├── GET beauty_leads WHERE id=162 (name, phone, city)
    │
    ├── POST api.telegram.org/sendMessage
    │   └── "🚀 ВІДКРИТТЯ ЛИСТА!\nСалон: Beauty Lounge\nМісто: Berlin\nWhatsApp: wa.me/..."
    │
    └── Response: 1×1 transparent GIF (43 bytes)
```

### 4.4 Персоналізація URL: ?s= параметр

Механіка:
```
Email link: https://vermarkter.github.io/services/beauty-industry/de/?s=Beauty%20Lounge
    ↓
JS на лендінгу:
    1. URLSearchParams.get('s') → "Beauty Lounge" (вже decoded)
    2. Attempt 1: inline querySelector → h1.innerHTML = "Exklusive IT-Lösung für Beauty Lounge"
    3. Attempt 2: DOMContentLoaded (fallback)
    4. Attempt 3: setInterval 100ms × 20 (robust fallback)
    5. data-personalized="1" → guard проти подвійного застосування
```

### 4.5 Smart Follow-up логіка

**Файл:** `scripts/smart_followup.py`

```python
GRACE_HOURS = 2  # якщо відкрив але не відповів через 2 години

def should_followup(lead):
    if lead.last_opened_at is None:
        return False
    delta = (now_utc() - lead.last_opened_at).total_seconds() / 3600
    if delta < GRACE_HOURS:
        return False
    if lead.status in REPLIED_STATUSES:
        return False
    return True

# WhatsApp повідомлення:
def build_wa_message(lead):
    if delta < 6:   text = "heute"
    elif delta < 30: text = "gestern"
    else:            text = "vor Kurzem"
    
    return f"""Guten Tag {first_name},
ich habe gesehen, dass Sie {text} unseren personalisierten Salon-Audit 
angesehen haben. Konnte ich Ihnen damit weiterhelfen?
Falls Sie Fragen haben oder eine kurze Demo wünschen — ich bin diese Woche verfügbar."""
```

### 4.6 Reply Classification (GPT-4o-mini)

**Файл:** `scripts/analyze_replies.py`

```python
SYSTEM_PROMPT = """
Du klassifizierst Antworten auf Sales-Emails für Beauty-Salons.
Antworte NUR mit: LABEL | kurze Begründung

Labels:
HOT   — will Demo, Termin, Gespräch, oder fragt aktiv nach nächsten Schritten
INFO  — fragt nach Preis, Details, Funktionen ohne klares Interesse
REFUSE — lehnt ab, kein Interesse, Stopp-Signale
"""

# Token-Kosten: ~$0.00015 pro Antwort
# 1000 Antworten = $0.15
```

### 4.7 Batch Management

Воронка розбита на пронумеровані batch:

```
Batch 1: IDs 173-199   (Berlin, Mitte)
Batch 2: IDs 220-239   (Berlin, Prenzlauer Berg)
Batch 3: IDs 240-259   (Berlin, Friedrichshain)
Batch 4: IDs 260-271   (Berlin, Beauty/Friseur Mitte)
Batch 5+: (заплановані)
```

Кожен batch = JSON файл з готовими email-текстами в `email_funnel_json`.

---

## 5. Frontend: лендінг-система

### 5.1 Архітектура 48 сторінок

```
vermarkter.github.io/
├── services/
│   └── beauty-industry/
│       ├── de/         ← REFERENCE STANDARD
│       │   ├── index.html              (Beauty Industry overview)
│       │   ├── google-ads.html
│       │   ├── meta-ads.html
│       │   ├── tiktok-ads.html
│       │   ├── seo.html
│       │   ├── crm-integration.html
│       │   ├── website-development.html
│       │   └── contact.html
│       ├── en/  (≡ DE structure)
│       ├── pl/
│       ├── ru/
│       ├── tr/
│       └── ua/
├── styles.css          ← ЄДИНИЙ глобальний stylesheet
├── js/
│   ├── main.js         ← ініціалізація, nav, scroll
│   ├── calculator.js   ← ROI калькулятор
│   ├── matrix.js       ← digital rain canvas
│   ├── fx.js           ← parallax + blur-reveal
│   ├── analytics.js    ← GA4 events
│   ├── consent.js      ← GDPR cookie banner
│   ├── chatbot.js      ← вбудований чатбот
│   └── telegram-service.js ← Supabase form submissions
└── api/
    └── track.js        ← Vercel serverless tracking
```

### 5.2 JavaScript модулі

**`js/main.js`** — ядро:
- `initNav()` — sticky навбар, hamburger меню
- `initScrollToTop()` — кнопка вгору (видима після 300px)
- `loadMatrixScript()` — lazy-load matrix.js
- `loadFxScript()` — lazy-load fx.js (parallax + blur-reveal)
- `initPainPeek()` — горизонтальний scroll pain-cards на mobile

**`js/matrix.js`** — Deep Void palette:
- Canvas 2D API, requestAnimationFrame loop
- ~60 колонок символів з різними швидкостями
- Палітра: `#7b6cff` (head) → `#1a0033` (deep tail)
- Scroll boost: прискорення при скролі
- Mobile адаптація: 3× ширші колонки = менше обчислень

**`js/fx.js`** — luxury visual effects:
- Mouse parallax: `[data-depth]` атрибут, LERP=0.072, MAX_SHIFT=18px
- Blur-reveal: IntersectionObserver, threshold=0.07
- CSS transition: `opacity + translateY(28px) + blur(10px)` → clear
- Prefers-reduced-motion: вимикає всі анімації

**`js/calculator.js`** — ROI калькулятор:
- 6 input fields: рекламний бюджет, конверсія, середній чек, etc.
- Формула: `netProfit = revenue - adSpend - serviceFee`
- `Math.max(0, netProfit)` — захист від від'ємних значень
- Popup: `openCalcAuditPopup()` → форма → Brevo webhook

### 5.3 CSS архітектура

**`styles.css`** — єдиний файл (~1800 рядків):
- CSS custom properties: `--color-primary`, `--text-secondary`, etc.
- Mobile-first responsive
- Критичні mobile fixes:
  - `.stats-grid`: `width:100% !important` — виправлення обрізання
  - `.scroll-to-top`: `bottom:190px !important` — над WA/TG кнопками
  - `#matrix-canvas`: `opacity:0.4; filter:saturate(2) brightness(1.6)`
- Blur-reveal classes: `.blur-hidden`, `.blur-visible`
- `[data-depth]`: `will-change:transform; backface-visibility:hidden`

### 5.4 DE як еталон

Принцип: всі інші мовні версії мають відповідати структурі DE. Перевірка відповідності:

```bash
# Перевірити що всі мовні версії мають однакову кількість секцій
for lang in en pl ru tr ua; do
    echo "$lang: $(grep -c '<section' services/beauty-industry/$lang/index.html) sections"
done
```

---

## 6. Backend: Python-інфраструктура

### 6.1 Каталог скриптів

| Скрипт | Функція | Тригер |
|--------|---------|--------|
| `sniper_fetch.py` | Збір лідів з Google Maps | Вручну |
| `enrich_street_view.py` | Додавання фото фасадів | Вручну після fetch |
| `fetch_reviews.py` | Mining 1-зіркових відгуків | Вручну |
| `lead_dna_enricher.py` | Аналіз сайту, бренд-стек | Вручну |
| `lead_analyser_pro.py` | AI secret phrases (Claude) | Вручну |
| `send_email_brevo.py` | Надсилання email-кампаній | Вручну + --dry-run |
| `analyze_replies.py` | Класифікація відповідей GPT | По розкладу або вручну |
| `smart_followup.py` | Follow-up генерація | По розкладу |
| `fast_uploader.py` | Масовий upload WhatsApp текстів | Вручну |
| `status_server.py` | Dashboard HTTP server | `python scripts/status_server.py` |
| `batch_watcher.py` | Моніторинг batch прогресу | Фонова задача |
| `check_health.py` | Health check Supabase + APIs | Cron або вручну |
| `holiday_guard.py` | Перевірка нерабочих днів | Перед розсилкою |
| `patch_email_funnel.py` | Масовий патч email_funnel_json | Після підготовки batch |
| `review_miner.py` | Глибокий mining відгуків | Вручну |
| `verify_berlin_sites.py` | Верифікація URL сайтів | Вручну |
| `mass_email_sender.py` | Масова розсилка (legacy) | Застарілий |

### 6.2 Конфігураційна система

**`config.ini`** — єдине джерело конфігурації для всіх Python скриптів:

```ini
[SUPABASE]
url = https://wrvdbvekiteopkdwxuzz.supabase.co
anon_key = eyJ...   # для читання (public)
service_role_key =  # для запису (НІКОЛИ не комітити)

[GOOGLE]
maps_api_key = AIzaSy...  # обмежити по IP/referrer

[ANTHROPIC]
api_key = sk-ant-...  # Claude API

[OPENAI]
api_key = sk-proj-...  # GPT-4o-mini для аналізу відповідей
model = gpt-4o

[BREVO]
api_key = xkeysib-...
from_email = hello@vermarkter.eu
from_name = Vermarkter
daily_limit = 300

[SMTP]
host = smtp.zoho.eu
port = 465
user = hello@vermarkter.eu
password = ...
```

**Стандартний патерн читання:**

```python
import configparser
from pathlib import Path

ROOT = Path(__file__).parent.parent
cfg = configparser.ConfigParser()
cfg.read(ROOT / 'config.ini', encoding='utf-8')

SB_URL = cfg['SUPABASE']['url'].strip()
SB_KEY = cfg['SUPABASE'].get('service_role_key', '').strip()
if not SB_KEY or 'ВСТАВИТИ' in SB_KEY:
    SB_KEY = cfg['SUPABASE']['anon_key'].strip()
```

### 6.3 Supabase клієнт патерн

Всі скрипти використовують прямі HTTP-запити (без SDK) для максимальної прозорості:

```python
import urllib.request
import json

def sb_patch(table: str, lead_id: int, payload: dict) -> bool:
    url = f"{SB_URL}/rest/v1/{table}?id=eq.{lead_id}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='PATCH')
    req.add_header('apikey', SB_KEY)
    req.add_header('Authorization', f'Bearer {SB_KEY}')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Prefer', 'return=minimal')
    try:
        urllib.request.urlopen(req, timeout=15)
        return True
    except Exception as e:
        print(f'[PATCH ERROR] id={lead_id}: {e}')
        return False
```

### 6.4 Dashboard (status_server.py)

HTTP-сервер на порту 8888:

```
GET /        → HTML dashboard
GET /api/stats → JSON метрики

Метрики:
- Leads по статусу (new/email_sent/reply_hot/...)
- Pie chart: HOT vs INFO vs REFUSE
- Leads з фото vs без
- Follow-up надіслано
- Canvas donut chart (160×160)
```

Запуск:
```bash
python scripts/status_server.py
# → http://localhost:8888
```

---

## 7. Serverless: Vercel API

### 7.1 `api/track.js` — Email Open Tracking

**Endpoint:** `GET /api/track?id={leadId}`

**Flow:**
1. Parse `leadId` як integer (захист від injection)
2. `PATCH beauty_leads` → `last_opened_at = now()`
3. `GET beauty_leads` → `name, phone, city`
4. `POST api.telegram.org` → Telegram сповіщення
5. Response: 1×1 GIF (43 байти), `Cache-Control: no-store`

**Env vars (Vercel Settings):**
```
SUPABASE_URL=https://wrvdbvekiteopkdwxuzz.supabase.co
SUPABASE_SERVICE_KEY=eyJ... (service role — НІКОЛИ не anon)
TELEGRAM_TOKEN=123456789:AAF...
TELEGRAM_CHAT_ID=ваш_chat_id
```

### 7.2 Vercel конфігурація

```json
// vercel.json (рекомендований)
{
  "functions": {
    "api/track.js": {
      "maxDuration": 10
    }
  },
  "headers": [
    {
      "source": "/api/track",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    }
  ]
}
```

---

## 8. Аналітика та моніторинг

### 8.1 Рівні трекінгу

```
Рівень 1: Email Open (tracking pixel) → Supabase + Telegram
Рівень 2: Link Click (UTM params) → GA4
Рівень 3: Demo Page Visit (?s= URL) → GA4 custom event
Рівень 4: Calculator Use → GA4 event + Telegram
Рівень 5: Form Submit → Brevo + Supabase + Telegram
```

### 8.2 GA4 Custom Events (js/analytics.js)

```javascript
// При зміні H1 персоналізацією
gtag('event', 'personalized_view', {
    salon_name: name,
    source: 'email_campaign'
});

// При use калькулятора
gtag('event', 'calculator_result', {
    net_profit: netProfit,
    roi_percent: roi
});
```

### 8.3 Ключові KPI для відстеження

| KPI | Визначення | Мета |
|-----|-----------|------|
| Open Rate | last_opened_at / email_sent | >35% |
| Response Rate | (reply_hot + reply_info) / email_sent | >8% |
| Hot Rate | reply_hot / email_sent | >3% |
| Follow-up Conversion | booked / followup_sent | >15% |
| Photo Coverage | leads з фото / total leads | >95% |

---

## 9. 10 Вразливостей та план виправлення

### CRITICAL

#### V-01: API ключі в git-репозиторії
**Файли:** `config.ini`, `.env`  
**Ризик:** Brevo ключ дозволяє надсилати email від нашого домену. Google Maps ключ = billing abuse. Anon Supabase ключ = читання всієї бази.

**Виправлення:**
```bash
# Крок 1: Ротація ключів (ЗРОБИТИ ЗАРАЗ)
# - Brevo: Settings → API Keys → Revoke + New
# - Google Maps: Console → Credentials → Regenerate
# - Supabase: Project Settings → API → Reset keys

# Крок 2: Видалення з git-історії
pip install git-filter-repo
git filter-repo --path config.ini --invert-paths
git push origin main --force  # ОБЕРЕЖНО: повідомити команду

# Крок 3: config.ini в .gitignore (вже є, але перевірити)
echo "config.ini" >> .gitignore
echo ".env" >> .gitignore

# Крок 4: Використовувати змінні середовища
# GitHub Actions: Settings → Secrets
# Vercel: Project Settings → Environment Variables
```

#### V-02: Exposed JWT в client-side JS
**Файл:** `js/telegram-service.js`  
**Ризик:** Supabase anon key видний у вихідному коді → атакуючий може читати дані.

**Виправлення:**
```javascript
// НЕ РОБИТИ:
const SUPABASE_ANON_KEY = 'eyJ...'; // hardcoded

// ПРАВИЛЬНО: proxy через Vercel function
// Весь доступ до Supabase — через /api/submit-form
// Клієнт ніколи не торкається Supabase напряму
```

### HIGH

#### V-03: IDOR у /api/track
**Проблема:** Будь-хто може викликати `/api/track?id=162` і підробити відкриття листа.  
**Виправлення:**
```javascript
// Додати HMAC підпис до tracking URL
// При генерації листа:
const sig = hmac(leadId + timestamp, TRACKING_SECRET);
const url = `/api/track?id=${leadId}&t=${timestamp}&s=${sig}`;

// У track.js:
const expected = hmac(leadId + t, process.env.TRACKING_SECRET);
if (sig !== expected) {
    return res.status(200).send(PIXEL); // тихо ігнорувати
}
```

#### V-04: Rate Limiting відсутній
**Проблема:** `/api/track` може бути спамований → Supabase quota exhaustion + Telegram spam.  
**Виправлення:**
```javascript
// Vercel Edge Config або in-memory Map
const seen = new Map(); // leadId → timestamp

export default async function handler(req, res) {
    const now = Date.now();
    const last = seen.get(leadId) || 0;
    
    if (now - last < 60_000) { // 1 хвилина дедуплікація
        return res.status(200).send(PIXEL); // ігнорувати
    }
    seen.set(leadId, now);
    // ... продовжити
}
```

#### V-05: GDPR — PII в Telegram без consent
**Проблема:** Ім'я, місто, номер телефону клієнта надсилаються у Telegram без явної згоди.  
**Виправлення:**
```javascript
// Маскування номера телефону
function maskPhone(phone) {
    if (!phone) return '–';
    return phone.slice(0, 4) + '****' + phone.slice(-3);
}

// Telegram повідомлення: тільки перші літери імені
const initials = name.split(' ').map(w => w[0]+'.').join(' ');
const text = `🚀 ВІДКРИТТЯ!\nСалон: ${initials} (${city})\n[деталі в CRM]`;
```

#### V-06: Email SMTP Injection
**Файл:** `scripts/send_email_brevo.py`  
**Проблема:** Назва салону (name) потрапляє в Subject без санітизації — CRLF injection.  
**Виправлення:**
```python
def safe_subject(name: str) -> str:
    # Видалити всі newline символи
    clean = re.sub(r'[\r\n\x00]', ' ', name)
    return f"Digitale Lösung für {clean[:50]} — Demo in 60 Sekunden"
```

#### V-07: XSS через street_view_url
**Проблема:** `sv_url` потрапляє в HTML email як URL атрибут — `javascript:` схема.  
**Виправлення:**
```python
def safe_url(url: str) -> str:
    if not url:
        return ''
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return ''  # відхилити будь-яку не-HTTP URL
    return html.escape(url)
```

### MEDIUM

#### V-08: Відсутній Audit Log
**Проблема:** Неможливо відстежити хто що робив і коли — ні для скриптів, ні для API.  
**Виправлення:**
```sql
CREATE TABLE audit_log (
    id          SERIAL PRIMARY KEY,
    action      TEXT NOT NULL,   -- 'email_sent', 'status_changed', etc.
    lead_id     INTEGER,
    old_value   TEXT,
    new_value   TEXT,
    actor       TEXT,            -- 'script:send_email' або 'api:track'
    created_at  TIMESTAMPTZ DEFAULT now()
);
```

#### V-09: Hardcoded Windows шляхи
**Файли:** `scripts/fast_uploader.py`, `scripts/sniper_fetch.py`  
**Проблема:** `r'c:\Users\andri\...'` — не портабельно.  
**Виправлення:**
```python
# ЗАВЖДИ використовувати:
ROOT = Path(__file__).parent.parent
cfg.read(ROOT / 'config.ini', encoding='utf-8')
# Не: r'c:\Users\...\config.ini'
```

#### V-10: ThreadPoolExecutor без timeout
**Файл:** `scripts/enrich_street_view.py`  
**Проблема:** `max_workers=10` без timeout на HTTP-запити → hanging threads.  
**Виправлення:**
```python
with ThreadPoolExecutor(max_workers=5) as pool:  # знизити до 5
    futures = {pool.submit(enrich_one, lead, timeout=10): lead 
               for lead in leads}
    for future in as_completed(futures, timeout=300):  # 5 хвилин max
        try:
            result = future.result(timeout=15)
        except TimeoutError:
            print(f"[TIMEOUT] Lead #{futures[future]['id']}")
```

---

## 10. Інструкція розгортання на нових серверах

### 10.1 Необхідні акаунти

Перед початком отримати credentials до:
1. **GitHub** — репозиторій `Vermarkter/vermarkter.github.io`
2. **Supabase** — `https://wrvdbvekiteopkdwxuzz.supabase.co`
3. **Vercel** — проект `vermarkter-kohl`
4. **Brevo** — аккаунт `maps.werbung@gmail.com`
5. **Google Cloud Console** — Maps API key
6. **Anthropic Console** — Claude API key
7. **Telegram** — bot token + chat ID

### 10.2 Локальна розробка (Windows)

```powershell
# 1. Клонувати репозиторій
git clone https://github.com/Vermarkter/vermarkter.github.io.git
cd vermarkter.github.io

# 2. Встановити Python залежності
pip install anthropic openai httpx brevo-python

# 3. Скопіювати та заповнити config.ini
# (НІКОЛИ не комітити з реальними ключами)
copy config.ini.example config.ini
notepad config.ini

# 4. Перевірити підключення до Supabase
python scripts/check_health.py

# 5. Запустити dashboard
python scripts/status_server.py
# → http://localhost:8888
```

### 10.3 Розгортання на Linux/Docker

```bash
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir \
    anthropic \
    openai \
    httpx \
    requests

# Використовувати env vars замість config.ini
ENV SUPABASE_URL=""
ENV SUPABASE_SERVICE_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV OPENAI_API_KEY=""
ENV BREVO_API_KEY=""
ENV GOOGLE_MAPS_API_KEY=""

CMD ["python", "scripts/status_server.py"]
```

```bash
# docker-compose.yml
version: '3.8'
services:
  vermarkter:
    build: .
    ports:
      - "8888:8888"
    env_file:
      - .env.production  # НЕ в git
    restart: unless-stopped
```

### 10.4 Vercel розгортання

```bash
# Встановити Vercel CLI
npm i -g vercel

# Зайти в аккаунт
vercel login

# Деплой (з кореня проекту)
vercel --prod

# Встановити env vars
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_KEY
vercel env add TELEGRAM_TOKEN
vercel env add TELEGRAM_CHAT_ID
```

### 10.5 GitHub Pages

Автоматично при push в `main`:
```bash
git add .
git commit -m "feat: опис змін"
git push origin main
# → автоматично деплоїться на vermarkter.github.io
```

**Важливо:** GitHub Pages обслуговує ТІЛЬКИ статичні файли. `api/track.js` — це Vercel function, не GitHub Pages.

### 10.6 Supabase налаштування

```bash
# 1. Запустити міграції в Supabase SQL Editor
# (URL: https://supabase.com/dashboard/project/wrvdbvekiteopkdwxuzz/sql)

# Порядок виконання:
# 1) scripts/add_tracking_column.sql
# 2) scripts/add_email_funnel_column.sql
# 3) scripts/add_reply_columns.sql
# 4) scripts/whatsapp_logs_schema.sql
```

### 10.7 Перший запуск email-кампанії

```bash
# Крок 1: Перевірити дані
python scripts/check_health.py

# Крок 2: Dry-run (без реальних листів)
python scripts/send_email_brevo.py --ids 162,163 --dry-run --save-html

# Крок 3: Переглянути preview
# Відкрити /tmp/email_preview_162.html в браузері

# Крок 4: Тестовий відправ на власну адресу
python scripts/send_email_brevo.py --ids 162 --test-email andreychupryna@gmail.com

# Крок 5: Реальний відправ (малий batch)
python scripts/send_email_brevo.py --ids 162,163,164 

# Крок 6: Моніторинг dashboard
python scripts/status_server.py
# → http://localhost:8888
```

### 10.8 Щоденний workflow

```bash
# Ранок (09:00):
# 1. Перевірити Telegram — чи були відкриття листів
# 2. Запустити analyze_replies.py якщо є відповіді
python scripts/analyze_replies.py --imap

# День (12:00):
# 3. Надіслати новий batch (max 300/день)
python scripts/send_email_brevo.py --batch 5

# Вечір (18:00):
# 4. Smart follow-up для тих, хто відкрив але не відповів
python scripts/smart_followup.py --grace-hours 6

# 5. Перевірити dashboard
python scripts/status_server.py
```

### 10.9 Troubleshooting

**Проблема:** Personalization не працює на лендінгу  
**Діагностика:**
```javascript
// В консолі браузера:
console.log(new URLSearchParams(location.search).get('s'));
// Має показати назву салону
console.log(document.querySelector('h1').getAttribute('data-personalized'));
// Має бути "1" якщо застосовано
```

**Проблема:** Tracking pixel не спрацьовує  
**Діагностика:**
```bash
# Перевірити Vercel logs
vercel logs --follow

# Тестовий запит
curl "https://vermarkter-kohl.vercel.app/api/track?id=162"
# Має повернути 1x1 GIF (Content-Type: image/gif)
```

**Проблема:** Brevo email йде в спам  
**Checklist:**
- SPF record: `vermarkter.eu TXT "v=spf1 include:sendinblue.com ~all"`
- DKIM: Brevo Dashboard → Senders → Domain verification
- DMARC: `_dmarc.vermarkter.eu TXT "v=DMARC1; p=quarantine"`
- Відсутність спам-слів в subject ("безкоштовно", "гарантовано")

**Проблема:** Matrix canvas не видно  
```css
/* Перевірити в styles.css: */
#matrix-canvas {
    opacity: 0.4 !important;
    filter: saturate(2) brightness(1.6);
}
```

---

## 11. Roadmap та масштабування

### 11.1 Короткострокові завдання (травень 2026)

- [ ] Ротація всіх API ключів (V-01)
- [ ] SQL міграції в Supabase (add_email_funnel_column + add_reply_columns)
- [ ] Перша валідаційна розсилка 3 листи (IDs 260-262)
- [ ] HMAC підпис для tracking pixel (V-03)
- [ ] Запустити lead_analyser_pro.py для Munich 100

### 11.2 Середньострокові (червень-серпень 2026)

- [ ] Масштабування на Мюнхен (100 → 500 лідів)
- [ ] Автоматизація respond-loop (IMAP + GPT + Calendly)
- [ ] A/B тестування subject lines (3 варіанти)
- [ ] Розширення на Відень і Гамбург
- [ ] Upgrade Brevo до платного (3000/день)

### 11.3 Довгострокові (Q4 2026)

- [ ] Self-hosted tracking (замість Vercel → власний сервер)
- [ ] Власна CRM замість Supabase-lite
- [ ] Мобільний додаток для директора (push замість Telegram)
- [ ] Автоматичне бронювання через Calendly API
- [ ] Розширення на 10 міст Германії

### 11.4 Масштабування бази лідів

```
Поточний стан:
  Berlin: 1710 leads ✓
  Munich: 100 leads ✓

Phase 2 target:
  Munich: 500 leads
  Hamburg: 300 leads
  Vienna: 200 leads

Команди для нового міста:
  python scripts/sniper_fetch.py --city "Hamburg" --category beauty_salon --limit 300
  python scripts/enrich_street_view.py --city Hamburg
  python scripts/fetch_reviews.py --city Hamburg
```

---

## APPENDIX A: Змінні середовища — повний довідник

| Змінна | Де встановити | Що робить |
|--------|--------------|-----------|
| `SUPABASE_URL` | config.ini, Vercel | URL Supabase проекту |
| `SUPABASE_SERVICE_KEY` | config.ini, Vercel | Повний доступ до БД |
| `SUPABASE_ANON_KEY` | config.ini | Публічний readonly доступ |
| `GOOGLE_MAPS_API_KEY` | config.ini | Places API, Photos API |
| `ANTHROPIC_API_KEY` | config.ini, .env | Claude claude-sonnet-4-6 |
| `OPENAI_API_KEY` | config.ini, .env | GPT-4o-mini класифікація |
| `BREVO_API_KEY` | config.ini | Email delivery |
| `TELEGRAM_TOKEN` | Vercel env | Bot API token |
| `TELEGRAM_CHAT_ID` | Vercel env | Chat ID для сповіщень |

---

## APPENDIX B: Glossary

| Термін | Визначення |
|--------|-----------|
| **Lead** | Запис у `beauty_leads` — один салон краси |
| **Sniper offer** | Гіперперсоналізований email, побудований на 5 шарах розвідки |
| **Pain signal** | 1-зіркова рецензія від клієнта — реальна слабкість салону |
| **Tracking pixel** | 1×1 GIF в email → фіксує відкриття листа |
| **Secret phrase** | AI-генерований відкривач для outreach повідомлення |
| **Batch** | Група лідів (20-30), підготовлених до розсилки |
| **DNA enrichment** | Аналіз сайту: бренди, booking, соцмережі |
| **DE reference** |德語 версія лендінгу — еталон для всіх 6 мов |
| **Hot lead** | GPT-класифікація: хоче demo або зустріч |
| **Grace period** | 2 години після відкриття листа → якщо не відповів = follow-up |

---

*Документ підготовлено: Травень 2026*  
*Версія: 1.0*  
*Мова: Українська (технічні терміни — англійська)*
