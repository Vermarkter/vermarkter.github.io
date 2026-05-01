-- Migration: add tracking columns to beauty_leads
-- Run in Supabase SQL Editor → New query → Run

ALTER TABLE beauty_leads
  ADD COLUMN IF NOT EXISTS last_opened_at  timestamptz,
  ADD COLUMN IF NOT EXISTS street_view_url text;

-- Index for quickly finding recently-opened leads in CRM dashboard
CREATE INDEX IF NOT EXISTS idx_beauty_leads_last_opened
  ON beauty_leads (last_opened_at DESC NULLS LAST)
  WHERE last_opened_at IS NOT NULL;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'beauty_leads'
  AND column_name IN ('last_opened_at', 'street_view_url')
ORDER BY column_name;
