// Email open tracking pixel — GET /api/track?id={lead_id}
// Records last_opened_at in Supabase and fires Telegram alert.
// Returns 1x1 transparent GIF.

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;
const TG_TOKEN    = process.env.TELEGRAM_TOKEN || process.env.TELEGRAM_BOT_TOKEN;
const TG_CHAT_ID  = process.env.TELEGRAM_CHAT_ID;

const PIXEL = Buffer.from(
  'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
  'base64'
);

function buildWaLink(phone) {
  if (!phone) return null;
  const digits = phone.replace(/[^\d+]/g, '');
  const normalized = digits.startsWith('+') ? digits : '+' + digits;
  return 'https://wa.me/' + normalized.replace('+', '');
}

async function sendTelegram(name, city, waLink) {
  if (!TG_TOKEN || !TG_CHAT_ID) return;
  const waText = waLink ? waLink : '_(kein Telefon)_';
  const cityLine = city ? `Місто: ${city}\n` : '';
  const text = `🚀 ВІДКРИТТЯ ЛИСТА\\!\nСалон: *${name}*\n${cityLine}Написати в WhatsApp: ${waText}`;
  await fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TG_CHAT_ID, text,
      parse_mode: 'MarkdownV2',
      disable_web_page_preview: true,
    }),
  });
}

module.exports = async function handler(req, res) {
  const leadId = parseInt(req.query.id, 10);

  if (leadId && SUPABASE_URL && SUPABASE_KEY) {
    try {
      await fetch(`${SUPABASE_URL}/rest/v1/beauty_leads?id=eq.${leadId}`, {
        method: 'PATCH',
        headers: {
          apikey: SUPABASE_KEY,
          Authorization: `Bearer ${SUPABASE_KEY}`,
          'Content-Type': 'application/json',
          Prefer: 'return=minimal',
        },
        body: JSON.stringify({ last_opened_at: new Date().toISOString() }),
      });

      const leadRes = await fetch(
        `${SUPABASE_URL}/rest/v1/beauty_leads?id=eq.${leadId}&select=name,phone,city`,
        { headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` } }
      );
      const leads = await leadRes.json();
      if (Array.isArray(leads) && leads.length > 0) {
        const lead = leads[0];
        sendTelegram(lead.name || `Lead #${leadId}`, lead.city || '', buildWaLink(lead.phone)).catch(() => {});
      }
    } catch (_) {}
  }

  res.setHeader('Content-Type', 'image/gif');
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  res.status(200).send(PIXEL);
};
