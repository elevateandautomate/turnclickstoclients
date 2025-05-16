# Testing the Form Submission Tracking Feature

Follow these steps to test the form submission tracking feature:

## Step 1: Check for Failed Submissions in the Database

Run the check_failed_submissions.py script to verify that there are failed submissions in the database:

```bash
python check_failed_submissions.py
```

This script will:
1. Connect to your Supabase database
2. Check for records with contact_form_submitted = false
3. Check for records with contact_form_submitted = NULL
4. Display the details of any failed submissions found
5. Offer to add a test record if no failed submissions are found

## Step 2: Restart the Server

Stop the current server (if it's running) by pressing Ctrl+C in the terminal, then start it again:

```bash
python app.py
```

## Step 3: Test the Tracking Page

1. Open your browser and navigate to http://127.0.0.1:5000/
2. Click on the "Tracking" tab
3. Look for the "Failed Form Submissions" section
4. Click the "Refresh" button

## Step 4: Check the Browser Console

1. Open the browser's developer tools (F12 or right-click > Inspect)
2. Go to the Console tab
3. Run this command to test the API directly:
   ```javascript
   testFailedSubmissionsAPI();
   ```
4. Check the console output for any errors or data issues

## Step 5: Check the Server Logs

Look at the terminal where the Flask application is running for any error messages or debugging output.

## Step 6: Try Processing a Contact

If you want to test the full flow:

1. Go to the dashboard
2. Click "Process Contacts"
3. Set the limit to 1
4. Choose "Browser Mode: Visible" to see what's happening
5. Click "Start Processing"
6. After processing completes, go back to the "Tracking" tab
7. Click "Refresh" in the "Failed Form Submissions" section

## Troubleshooting

If you're still having issues:

1. Make sure the TABLE_NAME is set to "core_data" in both app.py and contact_bot.py
2. Verify that the core_data table has the necessary columns:
   - contact_form_submitted (boolean)
   - contact_form_submitted_message (text)
   - contact_form_submitted_timestamp (timestamptz)
   - niche (text)
3. Check that your Supabase URL and API key are correct
4. Try adding a test record directly to the database using the SQL Editor:

```sql
INSERT INTO core_data (
    id,
    name, 
    company, 
    website_url, 
    niche,
    contact_form_submitted,
    contact_form_submitted_message,
    contact_form_submitted_timestamp
) VALUES (
    gen_random_uuid(),
    'Test Failed Contact', 
    'Test Failed Company', 
    'https://testfailed.com', 
    'dentist',
    false,
    'This is a test error message for tracking',
    NOW()
);
```
