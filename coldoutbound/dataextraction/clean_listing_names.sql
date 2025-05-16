-- SQL script to clean listing_name column by removing everything after the comma
-- This will update the listing_name column to keep only the part before the first comma

-- First, let's create a backup of the current data (optional but recommended)
-- Uncomment the following lines if you want to create a backup
-- CREATE TABLE IF NOT EXISTS core_data_backup AS SELECT * FROM public.core_data;
-- SELECT COUNT(*) FROM core_data_backup; -- Verify backup was created successfully

-- Update the listing_name column to keep only the part before the first comma
UPDATE public.core_data
SET listing_name = TRIM(SPLIT_PART(listing_name, ',', 1))
WHERE listing_name LIKE '%,%';

-- Verify the changes (this will show the first 10 updated records)
-- SELECT id, listing_name FROM public.core_data LIMIT 10;
