-- Migration: add Bavaria harvest columns to beauty_leads
-- Run this in Supabase Dashboard → SQL Editor

ALTER TABLE beauty_leads
  ADD COLUMN IF NOT EXISTS country       text,
  ADD COLUMN IF NOT EXISTS reviews_count integer,
  ADD COLUMN IF NOT EXISTS category      text,
  ADD COLUMN IF NOT EXISTS platform      text,
  ADD COLUMN IF NOT EXISTS pain_tags     text[];
