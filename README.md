# Vermarkter — Performance-Marketing Website

Новий проект маркетингового агентства з чистого аркуша.

> Last deploy: 2026-05-01 — Telegram tracking + personalization hardening

## Структура проекту

```
агенство-новий/
├── de/              # Німецька версія (головна)
│   └── index.html
├── ua/              # Українська версія
├── en/              # Англійська версія
├── pl/              # Польська версія
├── ru/              # Російська версія
├── tr/              # Турецька версія
├── JS/              # JavaScript файли
│   ├── calculator.js   # Калькулятор медіапланування
│   └── main.js         # Основна логіка
├── CSS/             # Додаткові стилі
├── LANG/            # JSON файли перекладів
├── SERVICES/        # Сторінки послуг
│   ├── google-ads/
│   ├── meta-ads/
│   └── crm-integration/
├── styles.css       # Головні стилі (dark + glassmorphism)
└── index.html       # Редірект на /de/
```

## Локальне тестування

### Варіант 1: Відкрити файл напряму
Відкрийте у браузері:
```
file:///C:/Users/andri/OneDrive/Projects/агенство-новий/de/index.html
```

### Варіант 2: Локальний сервер (Python)
```bash
# Python 3
python -m http.server 8000

# Відкрити в браузері
http://localhost:8000/de/
```

### Варіант 3: Локальний сервер (Node.js)
```bash
npx http-server -p 8000

# Відкрити в браузері
http://localhost:8000/de/
```

## Особливості

- ✅ Dark theme + Glassmorphism дизайн
- ✅ Робочий калькулятор з реальними формулами
- ✅ Чисті URL (/de/, /ua/ замість .html)
- ✅ Mobile-responsive
- ✅ Без frameworks (vanilla JS/CSS)

## Калькулятор

Використовує реальні формули медіапланування:
- Clicks = Budget / CPC
- Conversions = Clicks × CR%
- Revenue = Conversions × AOV
- Profit = Revenue - Budget
- ROAS = Revenue / Budget

## Deployment на GitHub Pages

### 1. Створіть репозиторій `vermarkter.github.io`

### 2. Додайте remote:
```bash
git remote add origin https://github.com/YOUR_USERNAME/vermarkter.github.io.git
git branch -M main
git push -u origin main
```

### 3. Налаштуйте GitHub Pages:
- Settings → Pages
- Source: Deploy from a branch
- Branch: main / (root)

Сайт буде доступний за адресою:
- https://vermarkter.github.io/de/
- https://vermarkter.github.io/ua/
- тощо

## TODOs

- [ ] Додати service pages (Google Ads, Meta Ads, CRM)
- [ ] Створити всі мовні версії (UA, EN, PL, RU, TR)
- [ ] Додати FAQ секцію
- [ ] Додати Reviews секцію
- [ ] Налаштувати форми зв'язку
- [ ] Додати chatbot інтеграцію

## Stack

- Pure HTML5
- Vanilla CSS (CSS Variables)
- Vanilla JavaScript (ES6)
- No build tools
- No dependencies

---

🤖 Created with Claude Code
