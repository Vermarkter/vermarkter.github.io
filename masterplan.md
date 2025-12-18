# masterplan.md (FINAL · HTML/CSS/JS aligned)

## 30-second Elevator Pitch

**Vermarkter** — performance-маркетинг для малого бізнесу в Європі.
Ми показуємо реальні цифри ще до старту реклами й продаємо маркетинг без тиску, дзвінків і "магії".

---

## Problem

- Малий бізнес не розуміє, куди йдуть рекламні гроші
- Агенції продають кліки замість результату
- Обіцянки ≠ цифри
- Страх "зливу бюджету"

---

## Mission

Зробити маркетинг:
- **зрозумілим**
- **рахованим**
- **прогнозованим**
для малого бізнесу.

---

## Target Audience

- Малий бізнес у Європі
- Самозайняті підприємці
- Локальні сервіси, e-commerce
- Українці в Європі (окремий фокус UA)

---

## Product Strategy

### Core Product

**Фіксований старт-пакет**
*(ціна змінна, не хардкодиться в інтерфейсі)*

**Принципи:**
- чіткий обсяг
- швидкий старт
- без контрактів
- без тиску

---

## Value Proposition System

### Global UTP #1 (Hero)
> Маркетинг для малого бізнесу, який рахується.

### Global UTP #2 (Support)
> Ми не продаємо кліки.
> Ми рахуємо, скільки бізнес може заробити.

---

## Services (SEO-first)

Кожна послуга = окрема сторінка + окреме УТП.

1. **Google Ads**
2. **Meta Ads**
3. **TikTok Ads**
4. **Websites**
5. **SEO**
6. **CRM Integration**

---

## Calculator (Trust Core)

- Реальний калькулятор медіапланування
- CPC, CPM, CTR, CR, AOV, ROAS
- Показує прогноз, не обіцянку
- Основа довіри та рішення про співпрацю

---

# Calculator Logic Specifications (MANDATORY)

## Purpose

The calculator must simulate a **real media planning model** used in performance marketing.

It is **not** a demo, estimator, or "marketing widget".

Its goal:
- show realistic limits
- explain economics of ads
- build trust through transparent math

---

## Input Parameters (User-controlled)

### Traffic & Budget
- `ad_platform` — Google Ads / Meta Ads / TikTok Ads *(affects defaults only)*
- `monthly_budget` (€)
- `cpc` (€) **or** `cpm` (€)
  *(depending on platform type)*

### Performance Metrics
- `ctr` (%) — Click-through rate
- `conversion_rate` (%) — from click to lead or purchase
- `average_order_value` (€)

### Optional (advanced / toggle)
- `repeat_purchase_rate` (%}
- `gross_margin` (%)

---

## Core Formulas (DO NOT SIMPLIFY)

### 1️⃣ Clicks

**If CPC-based:**
```
clicks = monthly_budget / cpc
```

**If CPM-based:**
```
impressions = (monthly_budget / cpm) * 1000
clicks = impressions * (ctr / 100)
```

### 2️⃣ Conversions (Leads or Sales)
```
conversions = clicks * (conversion_rate / 100)
```

### 3️⃣ Revenue
```
revenue = conversions * average_order_value
```

**If repeat purchases enabled:**
```
adjusted_revenue = revenue * (1 + repeat_purchase_rate / 100)
```

### 4️⃣ Profit
```
profit = revenue - monthly_budget
```

**If gross margin enabled:**
```
profit = revenue * (gross_margin / 100) - monthly_budget
```

### 5️⃣ ROAS
```
roas = revenue / monthly_budget
```

---

## Output Metrics (Displayed to User)

- **Clicks**
- **Conversions** (Leads / Sales)
- **Revenue** (€)
- **Profit** (€)
- **ROAS** (x)

All outputs must:
- be rounded logically (no long decimals)
- update in real-time
- never show `NaN`, `Infinity`, or negative nonsense values

---

## Validation & Edge Cases (CRITICAL)

- If `monthly_budget ≤ 0` → show "Enter a budget"
- If `cpc = 0` or `cpm = 0` → block calculation
- If `conversion_rate > 20%` → show subtle warning:
  **"Це дуже високий CR. Перевірте реалістичність."**
- If `ROAS < 1` → highlight result as unprofitable *(neutral, not red alarm)*

---

## UX Rules (Calculator Behavior)

- No page reloads
- All calculations **client-side** (JavaScript)
- Calculation logic **separated from DOM rendering**
- Results **animate slowly** (calm, not casino-style)
- Numbers must feel **"considered"**, not **"exciting"**

---

## Mandatory Disclaimers (Visible in UI)

**Above calculator:**
> Це реальний калькулятор медіапланування.
> Тут використовуються ті самі формули, що й у щоденній роботі маркетолога.

**Below calculator:**
> Результат — це прогноз, а не обіцянка.
> Маркетинг починається з чесних цифр.

---

## Philosophical Constraint

The calculator must **reduce unrealistic expectations**, not inflate them.

If numbers look bad — **that is still a successful outcome**.

---

# Brand Principles

- Calm
- Rational
- Honest
- Supportive
- No hype

---

# Tech Stack (MVP — HARD CONSTRAINT)

## Frontend

- **Pure HTML5**
- **Vanilla CSS** (no frameworks)
- **Vanilla JavaScript** (ES6)
- **No build tools**
- **No React**
- **No TypeScript**
- **No Node.js**
- **No bundlers**

👉 **Сайт має відкриватись як `index.html` у браузері.**

---

## Compliance

- GDPR
- Privacy Policy (DE compliant)
- Multilingual consistency

---

# Roadmap

## MVP
- UA version
- Homepage
- Service pages
- Calculator
- CTA → Telegram / Email

## V1
- Multilingual
- Reviews
- Smart assistant (text-based)

## V2
- CRM
- Saved calculations (localStorage)
- PDF media plan

---

# Risks & Mitigation

| Risk | Solution |
|------|----------|
| Недовіра | калькулятор + дисклеймери |
| Ламані стилі | mobile-first + CSS variables |
| Over-engineering | no frameworks |

---
