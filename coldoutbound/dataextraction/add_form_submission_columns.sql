-- SQL script to add form submission tracking columns to the core_data table
-- Run this in the Supabase SQL Editor if the columns don't exist

-- Add contact_form_submitted column (boolean)
ALTER TABLE core_data
ADD COLUMN IF NOT EXISTS contact_form_submitted boolean DEFAULT NULL;

-- Add contact_form_submitted_message column (text)
ALTER TABLE core_data
ADD COLUMN IF NOT EXISTS contact_form_submitted_message text DEFAULT NULL;

-- Add contact_form_submitted_timestamp column (timestamptz)
ALTER TABLE core_data
ADD COLUMN IF NOT EXISTS contact_form_submitted_timestamp timestamptz DEFAULT NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_core_data_contact_form_submitted
ON core_data(contact_form_submitted);

-- Create the exec_sql function (optional, for future use)
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
END;
$$;
