-- SQL script to add niche column to the dentist table and set default value
-- Run this in the Supabase SQL Editor

-- Add niche column (text)
ALTER TABLE dentist 
ADD COLUMN IF NOT EXISTS niche text DEFAULT 'dentist';

-- Update all existing records to have 'dentist' as the niche
UPDATE dentist
SET niche = 'dentist'
WHERE niche IS NULL OR niche = '';

-- Create index for better performance when filtering by niche
CREATE INDEX IF NOT EXISTS idx_dentist_niche 
ON dentist(niche);

-- Note: This will set all existing records to have 'dentist' as the niche
-- Future records can have different niches assigned when they're created
