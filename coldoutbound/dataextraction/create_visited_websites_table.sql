-- SQL script to create the visited_websites table in Supabase

-- Create the visited_websites table
CREATE TABLE IF NOT EXISTS public.visited_websites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    website_url TEXT UNIQUE NOT NULL,
    visited_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Add comment to the table
COMMENT ON TABLE public.visited_websites IS 'Table to track websites visited by the contact bot';

-- Add comments to columns
COMMENT ON COLUMN public.visited_websites.id IS 'Unique identifier for the record';
COMMENT ON COLUMN public.visited_websites.website_url IS 'URL of the visited website';
COMMENT ON COLUMN public.visited_websites.visited_at IS 'Timestamp when the website was visited';
COMMENT ON COLUMN public.visited_websites.status IS 'Status of the visit (e.g., visiting, form_submitted, form_failed)';
COMMENT ON COLUMN public.visited_websites.created_at IS 'Timestamp when the record was created';

-- Create index on website_url for faster lookups
CREATE INDEX IF NOT EXISTS idx_visited_websites_url ON public.visited_websites(website_url);

-- Set up Row Level Security (RLS)
ALTER TABLE public.visited_websites ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" 
ON public.visited_websites 
FOR ALL 
TO authenticated 
USING (true);

-- Create policy to allow service role to manage all records
CREATE POLICY "Allow service role to manage all records" 
ON public.visited_websites 
FOR ALL 
TO service_role 
USING (true);

-- Grant permissions to authenticated users
GRANT ALL ON public.visited_websites TO authenticated;
GRANT USAGE ON SEQUENCE public.visited_websites_id_seq TO authenticated;
