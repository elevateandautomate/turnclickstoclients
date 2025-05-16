# Form Submission Tracking

This document explains how to set up and use the form submission tracking feature in the Contact Bot.

## Overview

The form submission tracking feature allows you to:

1. Track which contact forms were successfully submitted
2. See detailed error messages for failed submissions
3. View timestamps for each submission attempt
4. Filter and display failed submissions in the dashboard
5. Retry failed submissions with a single click

## Required Database Columns

For this feature to work properly, your Supabase table needs the following columns:

| Column Name | Type | Description |
|-------------|------|-------------|
| `contact_form_submitted` | boolean | Whether the form was successfully submitted |
| `contact_form_submitted_message` | text | Success message or error details |
| `contact_form_submitted_timestamp` | timestamptz | When the submission was attempted |

## Setting Up the Columns

### Option 1: Automatic Setup (Recommended)

The bot will attempt to automatically check for and create these columns when it starts up. However, this requires the `exec_sql` function to exist in your Supabase project, which it currently doesn't.

### Option 2: Manual Setup

1. Go to your [Supabase Dashboard](https://app.supabase.io)
2. Navigate to the Table Editor
3. Select the "dentist" table (or whatever your TABLE_NAME is)
4. Click "Add Column" and create each of the required columns:
   - `contact_form_submitted` (type: boolean, nullable: true)
   - `contact_form_submitted_message` (type: text, nullable: true)
   - `contact_form_submitted_timestamp` (type: timestamptz, nullable: true)

### Option 3: SQL Script

You can also run the following SQL in the Supabase SQL Editor:

```sql
-- Add contact_form_submitted column (boolean)
ALTER TABLE dentist 
ADD COLUMN IF NOT EXISTS contact_form_submitted boolean DEFAULT NULL;

-- Add contact_form_submitted_message column (text)
ALTER TABLE dentist 
ADD COLUMN IF NOT EXISTS contact_form_submitted_message text DEFAULT NULL;

-- Add contact_form_submitted_timestamp column (timestamptz)
ALTER TABLE dentist 
ADD COLUMN IF NOT EXISTS contact_form_submitted_timestamp timestamptz DEFAULT NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_dentist_contact_form_submitted 
ON dentist(contact_form_submitted);
```

## Creating the exec_sql Function (Optional)

If you want to enable automatic column creation, you can create the `exec_sql` function in your Supabase project:

1. Go to the SQL Editor in your Supabase dashboard
2. Create a new query
3. Paste this SQL:

```sql
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
END;
$$;
```

4. Run the query

## Using the Form Submission Tracking

### Viewing Form Submissions

1. Go to the dashboard
2. Click on the "Tracking" tab
3. Scroll down to the "Failed Form Submissions" section
4. You'll see a list of failed submissions with error messages and timestamps
5. Click the "Refresh" button to update the list

### Retrying Failed Submissions

1. Find the failed submission you want to retry
2. Click the "Retry" button
3. The bot will attempt to process the contact again

## Troubleshooting

### Columns Not Created Automatically

If you see an error message about missing columns:

1. Check the console logs for details
2. Follow the manual setup instructions above
3. Restart the application

### No Failed Submissions Showing

If the "Failed Form Submissions" section is empty:

1. Make sure you have the required columns in your database
2. Check that you have processed some contacts
3. Click the "Refresh" button to update the list

### Error Messages Not Detailed Enough

If you need more detailed error messages:

1. Check the application logs for more information
2. Look at the screenshots saved in the application directory
3. Try processing the contact with the browser visible (non-headless mode)

## Additional Information

- The form submission status is updated in real-time as the bot processes each contact
- The timestamp is in ISO format and will be displayed in your local timezone in the UI
- Failed submissions are stored with detailed error messages to help diagnose issues
