-- SQL script to add LinkedIn tracking columns to the core_data table
-- Run this in the Supabase SQL Editor

-- Add linkedin_connected column (boolean, nullable)
ALTER TABLE public.core_data 
ADD COLUMN IF NOT EXISTS linkedin_connected BOOLEAN DEFAULT NULL;

-- Add linkedin_connected_message column (text, nullable)
ALTER TABLE public.core_data 
ADD COLUMN IF NOT EXISTS linkedin_connected_message TEXT DEFAULT NULL;

-- Add linkedin_connected_timestamp column (timestamptz, nullable)
ALTER TABLE public.core_data 
ADD COLUMN IF NOT EXISTS linkedin_connected_timestamp TIMESTAMPTZ DEFAULT NULL;

-- Add an index on linkedin_connected for faster queries
CREATE INDEX IF NOT EXISTS idx_core_data_linkedin_connected 
ON public.core_data (linkedin_connected);

-- Add an index on linkedin_connected_timestamp for faster sorting
CREATE INDEX IF NOT EXISTS idx_core_data_linkedin_connected_timestamp 
ON public.core_data (linkedin_connected_timestamp);

-- Grant permissions to authenticated users
GRANT SELECT, UPDATE ON public.core_data TO authenticated;

-- Verify the columns were added
SELECT 
  column_name, 
  data_type, 
  is_nullable 
FROM 
  information_schema.columns 
WHERE 
  table_name = 'core_data' AND 
  column_name IN ('linkedin_connected', 'linkedin_connected_message', 'linkedin_connected_timestamp');
