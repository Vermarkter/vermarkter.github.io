-- Migration: add email_funnel_json column to beauty_leads
-- Run in Supabase SQL Editor → New query → Run

ALTER TABLE beauty_leads
  ADD COLUMN IF NOT EXISTS email_funnel_json jsonb;

-- Optional index for leads that have a funnel loaded
CREATE INDEX IF NOT EXISTS idx_beauty_leads_email_funnel
  ON beauty_leads USING gin (email_funnel_json)
  WHERE email_funnel_json IS NOT NULL;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'beauty_leads'
  AND column_name = 'email_funnel_json';
