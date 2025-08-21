// api/chat.js — Vercel Serverless Function (CommonJS)

module.exports = async (req, res) => {
  // --- CORS ---
  res.setHeader('Access-Control-Allow-Origin', '*'); // за потреби заміни на твій фронтенд-домен
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) return res.status(500).json({ error: 'OPENAI_API_KEY missing' });

    // --- Парсимо тіло запиту ---
    let body = req.body;
    if (!body || typeof body !== 'object') {
      const raw = await new Promise((resolve) => {
        let acc = '';
        req.on('data', c => acc += c);
        req.on('end', () => resolve(acc));
      });
      try { body = raw ? JSON.parse(raw) : {}; } catch { body = {}; }
    }

    const messages = Array.isArray(body.messages) ? body.messages : [];
    const lang = (body.lang || 'de').toLowerCase();

    if (messages.length === 0) {
      return res.status(400).json({ error: 'messages must be a non-empty array' });
    }

    // --- Мова відповіді ---
    const langPhrase = {
      de: 'Antworte auf DEUTSCH.',
      en: 'Answer in ENGLISH.',
      uk: 'Відповідай УКРАЇНСЬКОЮ.',
      ru: 'Отвечай на РУССКОМ.'
    }[lang] || 'Antworte auf DEUTSCH.';

    // --- Системний промпт (коротко, без списків) ---
    const systemContent =
      'Ти — маркетолог із 8-річним досвідом. Відповідай практично, дієво і дуже коротко — максимум у 3 речення. ' +
      'Без Markdown, без списків, без нумерацій, без заголовків: лише звичайний текст. ' +
      'Для Google Ads — стисла структура + 1–2 гіпотези + ключова метрика; для SMM — стисла ідея контент‑плану + воронка; ' +
      'для SEO — 2–3 пріоритети. 
      'За запитом вкажи мінімальні ціни: створення сайту від 50€, запуск SMM від 50€, запуск Google Ads від 50€. ' +
      langPhrase;

    // --- Виклик OpenAI ---
    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        temperature: 0.4,
        messages: [{ role: 'system', content: systemContent }, ...messages]
      })
    });

    const data = await r.json();
    if (!r.ok) {
      return res.status(500).json({ error: 'openai_error', detail: data });
    }

    // --- Санітизація та обрізання до 3 речень ---
    function sanitize(txt) {
      if (!txt) return '';
      // прибрати Markdown/буліти/заголовки/зайві переноси
      txt = txt.replace(/[#*_`>]+/g, ' ')
               .replace(/^[\s\-•\d.)]+/gm, '')   // буліти/нумерація на початку рядків
               .replace(/\s{2,}/g, ' ')
               .replace(/\n+/g, ' ')
               .trim();
      // максимум 3 речення
      const sentences = txt.split(/(?<=[.!?])\s+/).slice(0, 3);
      let out = sentences.join(' ').trim();
      // гарантувати CTA наприкінці
      const cta = ' Напишіть у Telegram @Marketing_in_Deutschland — надішлю план/кошторис.';
      if (!out.toLowerCase().includes('@marketing_in_deutschland')) out += cta;
      return out;
    }

    const replyRaw = data?.choices?.[0]?.message?.content || '';
    const reply = sanitize(replyRaw) || 'Напишіть у Telegram @Marketing_in_Deutschland — надішлю план/кошторис.';
    return res.status(200).json({ reply });

  } catch (e) {
    return res.status(500).json({ error: 'Server error' });
  }
};
