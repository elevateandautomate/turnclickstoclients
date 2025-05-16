# Table Rename and Niche Column Setup

This document explains how to rename the "dentist" table to "core_data" and add a "niche" column to categorize your contacts.

## Overview

We're making two important changes to your database structure:

1. **Renaming the Table**: Changing the table name from "dentist" to "core_data" to reflect its new purpose as a general contact database
2. **Adding a Niche Column**: Adding a "niche" column to categorize contacts by their industry or market segment

## Step 1: Run the SQL Script

Run the following SQL script in the Supabase SQL Editor:

```sql
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
```

## Step 2: Verify the Changes

After running the SQL script, you can verify the changes by:

1. Going to the Supabase Table Editor
2. Checking that the "core_data" table exists
3. Checking that the "niche" column exists in the table
4. Verifying that all records have "dentist" as their niche value

## Step 3: Restart the Application

After making these database changes, restart the application to ensure it uses the new table name and structure.

## Using the Niche Field

### Viewing Niches in the Dashboard

The niche field is displayed in the "Failed Form Submissions" section of the tracking tab. Each contact will show their niche category with a blue badge.

### Adding Contacts with Different Niches

When adding new contacts to the database, you can specify their niche. If no niche is specified, the default value "dentist" will be used.

### Filtering by Niche

You can filter contacts by niche in your SQL queries:

```sql
-- Get all contacts in the "dentist" niche
SELECT * FROM core_data WHERE niche = 'dentist';

-- Get all contacts in the "lawyer" niche
SELECT * FROM core_data WHERE niche = 'lawyer';
```

## Common Niches

Here are some common niches you might want to use:

- dentist
- lawyer
- doctor
- realtor
- accountant
- consultant
- coach
- therapist
- architect
- contractor
- designer
- photographer

## Troubleshooting

### Table Not Found Error

If you see an error like "relation 'dentist' does not exist", it means the application is still trying to use the old table name. Make sure you've:

1. Run the SQL script to rename the table
2. Updated the TABLE_NAME constant in the code
3. Restarted the application

### Missing Niche Values

If some records don't have a niche value, run:

```sql
UPDATE core_data
SET niche = 'dentist'
WHERE niche IS NULL OR niche = '';
```

### Performance Issues

If you have a large number of records and queries are slow, make sure the indexes were created:

```sql
CREATE INDEX IF NOT EXISTS idx_core_data_niche 
ON core_data(niche);

CREATE INDEX IF NOT EXISTS idx_core_data_contact_form_submitted 
ON core_data(contact_form_submitted);
```
