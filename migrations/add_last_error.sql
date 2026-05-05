-- Run once in Supabase → SQL Editor
ALTER TABLE beauty_leads ADD COLUMN IF NOT EXISTS last_error text;
