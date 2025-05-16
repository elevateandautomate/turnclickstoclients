-- Add last_updated column to the core_data table
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT now();
