// api/track.js — Email open tracking beacon
// Vercel Serverless Function
// GET /api/track?id={lead_id}&b={batch}
//
// 1. Records last_opened_at = now() in beauty_leads via Supabase REST API.
// 2. Fetches lead name + phone, fires Telegram alert to director.
// Returns a 1x1 transparent GIF so the <img> tag in the email loads silently.

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY; // service role key — set in Vercel env vars
const TG_TOKEN    = process.env.TELEGRAM_BOT_TOKEN;
const TG_CHAT_ID  = process.env.TELEGRAM_CHAT_ID;

// 1x1 transparent GIF (43 bytes)
const PIXEL = Buffer.from(
  'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
  'base64'
);

function buildWaLink(phone) {
  if (!phone) return null;
  // Normalize: keep digits + leading +
  const digits = phone.replace(/[^\d+]/g, '');
  const normalized = digits.startsWith('+') ? digits : '+' + digits;
  return 'https://wa.me/' + normalized.replace('+', '');
}

async function sendTelegram(name, waLink) {
  if (!TG_TOKEN || !TG_CHAT_ID) return;
  const waText = waLink ? waLink : '(kein Telefon)';
  const text = `🚀 ГАРЯЧИЙ КЛІЄНТ!\n*${name}* щойно відкрив імейл.\n\nНапиши йому в WhatsApp:\n${waText}`;
  await fetch(
    `https://api.telegram.org/bot${TG_TOKEN}/sendMessage`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TG_CHAT_ID,
        text,
        parse_mode: 'Markdown',
        disable_web_page_preview: true,
      }),
    }
  );
}

export default async function handler(req, res) {
  const leadId = parseInt(req.query.id, 10);

  if (leadId && SUPABASE_URL && SUPABASE_KEY) {
    try {
      // 1. Update last_opened_at
      await fetch(
        `${SUPABASE_URL}/rest/v1/beauty_leads?id=eq.${leadId}`,
        {
          method: 'PATCH',
          headers: {
            apikey: SUPABASE_KEY,
            Authorization: `Bearer ${SUPABASE_KEY}`,
            'Content-Type': 'application/json',
            Prefer: 'return=minimal',
          },
          body: JSON.stringify({ last_opened_at: new Date().toISOString() }),
        }
      );

      // 2. Fetch lead name + phone for Telegram alert
      const leadRes = await fetch(
        `${SUPABASE_URL}/rest/v1/beauty_leads?id=eq.${leadId}&select=name,phone`,
        {
          headers: {
            apikey: SUPABASE_KEY,
            Authorization: `Bearer ${SUPABASE_KEY}`,
          },
        }
      );
      const leads = await leadRes.json();
      if (Array.isArray(leads) && leads.length > 0) {
        const lead = leads[0];
        const waLink = buildWaLink(lead.phone);
        // Fire-and-forget — never block the pixel response
        sendTelegram(lead.name || `Lead #${leadId}`, waLink).catch(() => {});
      }
    } catch (_) {
      // Silently ignore — never break email rendering due to tracking failure
    }
  }

  res.setHeader('Content-Type', 'image/gif');
  res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  res.status(200).send(PIXEL);
}
