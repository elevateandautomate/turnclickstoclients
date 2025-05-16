-- SQL script to rename the dentist table to core_data and add niche column
-- Run this in the Supabase SQL Editor

-- First, check if the core_data table already exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'core_data') THEN
        RAISE NOTICE 'Table core_data already exists. Skipping rename operation.';
    ELSE
        -- Rename the dentist table to core_data
        ALTER TABLE IF EXISTS dentist RENAME TO core_data;
        RAISE NOTICE 'Table dentist renamed to core_data.';
    END IF;
END
$$;

-- Add niche column to core_data table if it doesn't exist
ALTER TABLE core_data 
ADD COLUMN IF NOT EXISTS niche text DEFAULT 'dentist';

-- Update all existing records to have 'dentist' as the niche
UPDATE core_data
SET niche = 'dentist'
WHERE niche IS NULL OR niche = '';

-- Create index for better performance when filtering by niche
CREATE INDEX IF NOT EXISTS idx_core_data_niche 
ON core_data(niche);

-- Drop any old indexes from the dentist table name if they exist
DROP INDEX IF EXISTS idx_dentist_niche;
DROP INDEX IF EXISTS idx_dentist_contact_form_submitted;

-- Create proper indexes on the core_data table
CREATE INDEX IF NOT EXISTS idx_core_data_contact_form_submitted 
ON core_data(contact_form_submitted);

-- Output confirmation message
DO $$
BEGIN
    RAISE NOTICE 'Table setup complete. The table is now named core_data with a niche column.';
    RAISE NOTICE 'All existing records have been set to niche = dentist.';
END
$$;
