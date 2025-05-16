-- Add enriched columns to the core_data table

-- First, add the enriched_all_contacts column to store all alternative contacts as JSON
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_all_contacts JSONB;

-- Add columns for first name, last name, and niche
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_first_name TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_last_name TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_niche TEXT;

-- Add columns for email and phone
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_email TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_email_first TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_phone TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_phone_first TEXT;

-- Add columns for social media
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_facebook TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_facebook_first TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_twitter TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_twitter_first TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_linkedin TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_linkedin_first TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_instagram TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_instagram_first TEXT;

-- Add columns for other contact information
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_address TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_business_hours TEXT;
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS enriched_contact_persons TEXT;

-- Add a flag to indicate alternative contacts were found
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS alternative_contact_found BOOLEAN DEFAULT FALSE;
