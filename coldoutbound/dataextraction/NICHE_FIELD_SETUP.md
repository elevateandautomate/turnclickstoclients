# Niche Field Setup

This document explains how to set up and use the "niche" field in your contact database.

## Overview

The "niche" field allows you to:

1. Categorize contacts by their industry or market segment
2. Filter and sort contacts based on their niche
3. Run targeted outreach campaigns for specific niches
4. Track performance metrics by niche

## Setting Up the Niche Column

### Step 1: Add the Column to Your Database

Run the SQL script in the Supabase SQL Editor:

```sql
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
```

### Step 2: Verify the Column Was Added

Run the test script to check if the niche column exists:

```bash
python test_exec_sql.py
```

You should see output like:

```
=== Testing exec_sql function ===
Successfully initialized Supabase client.
Error: {'code': 'PGRST202', 'details': 'Searched for the function public.exec_sql...', 'hint': None, 'message': 'Could not find the function public.exec_sql(query) in the schema cache'}

The exec_sql function may not exist in your Supabase project.
You need to create it with the following SQL:

CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
END;
$$;


=== Checking niche column ===
Successfully initialized Supabase client.
✅ The 'niche' column already exists in the table.
✅ All records have a niche value set.
```

## Using the Niche Field

### In the Dashboard

The niche field is now displayed in the "Failed Form Submissions" section of the tracking tab. Each contact will show their niche category.

### When Adding New Contacts

When adding new contacts to the database, you can specify their niche. If no niche is specified, the default value "dentist" will be used.

### Filtering by Niche

You can filter contacts by niche in your SQL queries:

```sql
-- Get all contacts in the "dentist" niche
SELECT * FROM dentist WHERE niche = 'dentist';

-- Get all contacts in the "lawyer" niche
SELECT * FROM dentist WHERE niche = 'lawyer';
```

## Adding New Niches

To add contacts with different niches, you can:

1. Insert new records with a specific niche value
2. Update existing records to change their niche

Example:

```sql
-- Insert a new contact with a different niche
INSERT INTO dentist (name, company, website_url, niche)
VALUES ('John Smith', 'Smith Law Firm', 'https://smithlaw.com', 'lawyer');

-- Update an existing contact's niche
UPDATE dentist
SET niche = 'lawyer'
WHERE id = '123';
```

## Best Practices

1. **Consistent Naming**: Use consistent naming conventions for niches (e.g., all lowercase, singular form)
2. **Limited Categories**: Start with a small set of well-defined niches rather than creating too many specific ones
3. **Documentation**: Keep a list of your defined niches and their criteria
4. **Regular Review**: Periodically review and clean up your niche categories

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

### Missing Niche Values

If some records don't have a niche value, run:

```sql
UPDATE dentist
SET niche = 'dentist'
WHERE niche IS NULL OR niche = '';
```

### Performance Issues

If you have a large number of records and queries are slow, make sure the index was created:

```sql
CREATE INDEX IF NOT EXISTS idx_dentist_niche 
ON dentist(niche);
```
