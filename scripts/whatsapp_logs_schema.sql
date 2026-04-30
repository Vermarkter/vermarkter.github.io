-- whatsapp_logs: history of all outgoing WhatsApp messages
-- Run once in Supabase SQL Editor (Table Editor → SQL)

CREATE TABLE IF NOT EXISTS whatsapp_logs (
    id              bigserial PRIMARY KEY,
    lead_id         bigint       NOT NULL REFERENCES beauty_leads(id) ON DELETE CASCADE,
    message_text    text         NOT NULL,
    sent_at         timestamptz  NOT NULL DEFAULT now(),
    delivery_status text         NOT NULL DEFAULT 'pending'
        CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
    provider        text         NOT NULL DEFAULT 'manual'
        CHECK (provider IN ('manual', 'waba', 'twilio', 'ultramsg', 'maytapi')),
    message_id      text,                -- provider-side message ID
    error_message   text,                -- last error, if delivery_status = 'failed'
    created_at      timestamptz  NOT NULL DEFAULT now()
);

-- Index for fast lookup by lead
CREATE INDEX IF NOT EXISTS idx_whatsapp_logs_lead_id ON whatsapp_logs(lead_id);

-- Index for status-based queries (e.g. retry all 'failed')
CREATE INDEX IF NOT EXISTS idx_whatsapp_logs_status  ON whatsapp_logs(delivery_status);

-- Optional: RLS — allow anon key to INSERT (for bot), restrict SELECT to service_role
-- ALTER TABLE whatsapp_logs ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "insert_own" ON whatsapp_logs FOR INSERT WITH CHECK (true);
-- CREATE POLICY "select_service" ON whatsapp_logs FOR SELECT USING (auth.role() = 'service_role');
