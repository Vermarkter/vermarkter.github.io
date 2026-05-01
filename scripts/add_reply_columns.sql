-- Migration: add reply tracking columns to beauty_leads
-- Run in Supabase SQL Editor → New query → Run

ALTER TABLE beauty_leads
  ADD COLUMN IF NOT EXISTS reply_text text;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'beauty_leads'
  AND column_name = 'reply_text'
ORDER BY column_name;
