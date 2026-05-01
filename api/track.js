// api/track.js — Email open tracking beacon
// Vercel Serverless Function
// GET /api/track?id={lead_id}&b={batch}
//
// Records last_opened_at = now() in beauty_leads via Supabase REST API.
// Returns a 1x1 transparent GIF so the <img> tag in the email loads silently.

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY; // service role key — set in Vercel env vars

// 1x1 transparent GIF (43 bytes)
const PIXEL = Buffer.from(
  'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
  'base64'
);

export default async function handler(req, res) {
  const leadId = parseInt(req.query.id, 10);

  if (leadId && SUPABASE_URL && SUPABASE_KEY) {
    try {
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
