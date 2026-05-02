-- Migration: add compliment_detail column to beauty_leads
-- Stores Instagram-sourced compliment: exact timestamp, specific skill, or unique feature
-- Run in Supabase SQL Editor → New query → Run

ALTER TABLE beauty_leads
  ADD COLUMN IF NOT EXISTS compliment_detail text;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'beauty_leads'
  AND column_name = 'compliment_detail'
ORDER BY column_name;
