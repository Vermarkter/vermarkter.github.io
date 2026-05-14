// Brevo Transactional Webhooks — POST /api/brevo-webhook
// Events: delivered, hard_bounce, soft_bounce, blocked, spam_complaint
//
// Hard bounce  → nullify email, set status to wa_ready (has phone) or funnel_ready
// Soft bounce  → record last_error, keep email
// Spam         → status = 'НЕ ВІДПРАВЛЯТИ', record last_error
// Blocked      → record last_error
// Delivered    → record delivery timestamp in last_error (cleared) and notes

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_KEY;
const WEBHOOK_SECRET = process.env.BREVO_WEBHOOK_SECRET; // optional guard

const HEADERS = {
  apikey: SUPABASE_KEY,
  Authorization: `Bearer ${SUPABASE_KEY}`,
  'Content-Type': 'application/json',
  Prefer: 'return=minimal',
};

async function supabasePatch(filter, patch) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/beauty_leads?${filter}`, {
    method: 'PATCH',
    headers: HEADERS,
    body: JSON.stringify(patch),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Supabase PATCH ${res.status}: ${body}`);
  }
}

async function supabaseGet(filter, select) {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/beauty_leads?${filter}&select=${select}`,
    { headers: { apikey: SUPABASE_KEY, Authorization: `Bearer ${SUPABASE_KEY}` } }
  );
  if (!res.ok) throw new Error(`Supabase GET ${res.status}`);
  return res.json();
}

function buildFilter(event) {
  // Brevo may send lead_id via tags or customerId; fall back to email match
  const tags = event.tags || [];
  const leadIdTag = tags.find(t => /^lead_id:\d+$/.test(t));
  if (leadIdTag) {
    const id = leadIdTag.split(':')[1];
    return { filter: `id=eq.${id}`, source: `lead_id:${id}` };
  }
  const email = event.email || event.to;
  if (email) {
    return { filter: `email=eq.${encodeURIComponent(email)}`, source: `email:${email}` };
  }
  return null;
}

module.exports = async function handler(req, res) {
  // Only accept POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  // Optional secret guard (set BREVO_WEBHOOK_SECRET in Vercel env if desired)
  if (WEBHOOK_SECRET) {
    const provided = req.headers['x-brevo-secret'] || req.query.secret;
    if (provided !== WEBHOOK_SECRET) {
      console.warn('[brevo-webhook] Rejected: invalid secret');
      return res.status(401).json({ error: 'Unauthorized' });
    }
  }

  const ts = new Date().toISOString();
  let body = req.body;

  // Brevo sends either a single event object or an array
  const events = Array.isArray(body) ? body : [body];

  console.log(`[brevo-webhook] ${ts} received ${events.length} event(s)`);

  if (!SUPABASE_URL || !SUPABASE_KEY) {
    console.error('[brevo-webhook] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY');
    return res.status(500).json({ error: 'Server misconfigured' });
  }

  for (const event of events) {
    const eventType = (event.event || '').toLowerCase();
    const email     = event.email || event.to || '?';
    const messageId = event['message-id'] || event.messageId || '';

    console.log(`[brevo-webhook] event=${eventType} email=${email} messageId=${messageId}`);

    const loc = buildFilter(event);
    if (!loc) {
      console.warn(`[brevo-webhook] Cannot identify lead for event=${eventType} email=${email}`);
      continue;
    }

    try {
      if (eventType === 'delivered') {
        await supabasePatch(loc.filter, {
          last_error: null,
          last_contacted: ts,
        });
        console.log(`[brevo-webhook] delivered → cleared last_error, updated last_contacted (${loc.source})`);

      } else if (eventType === 'hard_bounce') {
        // Fetch lead to decide fallback status
        const leads = await supabaseGet(loc.filter, 'id,phone,status');
        const lead  = leads[0];

        let newStatus;
        if (lead) {
          const hasPhone = lead.phone && lead.phone.trim().length > 0;
          const curStatus = lead.status || '';
          // Don't downgrade a lead that's already in a worse/terminal state
          const terminal = ['НЕ ВІДПРАВЛЯТИ', 'spam_complaint'].includes(curStatus);
          if (!terminal) {
            newStatus = hasPhone ? 'wa_ready' : 'funnel_ready';
          }
        }

        const patch = {
          email: null,
          last_error: 'Hard Bounce',
        };
        if (newStatus) patch.status = newStatus;

        await supabasePatch(loc.filter, patch);
        console.log(`[brevo-webhook] hard_bounce → email=NULL, status=${newStatus || '(unchanged)'} (${loc.source})`);

      } else if (eventType === 'soft_bounce') {
        await supabasePatch(loc.filter, {
          last_error: 'Soft Bounce',
        });
        console.log(`[brevo-webhook] soft_bounce → last_error set (${loc.source})`);

      } else if (eventType === 'spam_complaint') {
        await supabasePatch(loc.filter, {
          status: 'НЕ ВІДПРАВЛЯТИ',
          last_error: 'Spam complaint',
        });
        console.log(`[brevo-webhook] spam_complaint → blocked (${loc.source})`);

      } else if (eventType === 'blocked') {
        const reason = event.reason || event.description || 'Brevo blocked';
        await supabasePatch(loc.filter, {
          last_error: `Brevo blocked: ${reason}`,
        });
        console.log(`[brevo-webhook] blocked reason="${reason}" (${loc.source})`);

      } else {
        console.log(`[brevo-webhook] unhandled event type: ${eventType}`);
      }
    } catch (err) {
      console.error(`[brevo-webhook] Error processing event=${eventType} (${loc.source}):`, err.message);
    }
  }

  // Brevo expects 200 OK quickly — always return 200
  return res.status(200).json({ ok: true, processed: events.length });
};
