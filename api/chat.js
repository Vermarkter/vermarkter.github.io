// api/chat.js
module.exports = async (req, res) => {
  // CORS (можна звузити під свій домен)
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  try {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) return res.status(500).json({ error: 'OPENAI_API_KEY missing' });

    // читаємо тіло
    let body = req.body;
    if (!body || typeof body === 'string') {
      const raw = await new Promise((resolve) => {
        let acc = ''; req.on('data', c => acc += c); req.on('end', () => resolve(acc));
      });
      try { body = raw ? JSON.parse(raw) : {}; } catch { body = {}; }
    }

    const messages = Array.isArray(body?.messages) ? body.messages : null;
    const lang = (body?.lang || 'de').toLowerCase(); // одержуємо мову з фронта
    if (!messages) return res.status(400).json({ error: 'messages must be an array' });

    // Мапа мов для інструкції
    const langPhrase = {
      de: 'Відповідай НІМЕЦЬКОЮ мовою.',
      en: 'Відповідай АНГЛІЙСЬКОЮ мовою.',
      uk: 'Відповідай УКРАЇНСЬКОЮ мовою.',
      ru: 'Відповідай РОСІЙСЬКОЮ мовою.'
    }[lang] || 'Відповідай НІМЕЦЬКОЮ мовою.';

    // Твій чіткий системний промпт (з умови) + вимога мови
    const systemContent =
      'Ти — маркетолог із 8-річним досвідом. Відповідай практично, дієво та лаконічно (до 3 речень). ' +
      'Для Google Ads — надай структуру, гіпотези й метрики; для SMM — сформуй контент-план і воронки; для SEO — визнач пріоритети. ' +
      'Завжди завершуй відповідь коротким CTA: «Напишіть у Telegram @Marketing_in_Deutschland — надішлю план/кошторис». ' +
      'За запитом вкажи мінімальні ціни: створення сайту від 50€, запуск SMM від 50€, запуск Google Ads від 50€. ' +
      'Починай з короткого чекліста-плану дій для кожного запиту, щоб структуровано надавати відповідь. ' +
      langPhrase;

    const r = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        temperature: 0.4,
        messages: [{ role: 'system', content: systemContent }, ...messages]
      })
    });

    const data = await r.json();
    if (!r.ok) return res.status(500).json({ error: 'openai_error', detail: data });

    res.status(200).json({ reply: data?.choices?.[0]?.message?.content || 'No reply' });
  } catch (e) {
    res.status(500).json({ error: 'Server error' });
  }
};
