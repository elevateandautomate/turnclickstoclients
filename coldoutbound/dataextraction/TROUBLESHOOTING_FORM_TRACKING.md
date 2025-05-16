# Troubleshooting Form Submission Tracking

This guide will help you troubleshoot issues with the form submission tracking feature.

## Common Issues and Solutions

### 1. Failed Submissions Not Showing in the Dashboard

If you've processed contacts but don't see any failed submissions in the tracking tab:

#### Check the Database

First, verify that failed submissions are properly recorded in the database:

```sql
-- Run this in the Supabase SQL Editor
SELECT 
    id, 
    name, 
    company, 
    website_url, 
    niche, 
    contact_form_submitted, 
    contact_form_submitted_message, 
    contact_form_submitted_timestamp
FROM 
    core_data
WHERE 
    contact_form_submitted = false
    OR contact_form_submitted IS NULL
ORDER BY 
    contact_form_submitted_timestamp DESC
LIMIT 20;
```

If this query returns records but they don't appear in the dashboard, there might be an issue with the API or the JavaScript code.

#### Test the API Directly

You can test the API endpoint directly in your browser:

1. Open a new browser tab
2. Navigate to: `http://127.0.0.1:5000/api/form-submissions?failed=true`
3. You should see a JSON response with the failed submissions

#### Use the Browser Console

You can use the browser console to debug:

1. Open the browser's developer tools (F12 or right-click > Inspect)
2. Go to the Console tab
3. Run this command:
   ```javascript
   testFailedSubmissionsAPI();
   ```
4. Check the console output for any errors or data issues

### 2. Form Submission Status Not Being Updated

If the form submission status isn't being updated in the database:

#### Check the Bot's Update Status Method

The bot updates the form submission status using the `_update_status` method. Make sure it's working correctly:

1. Add some debug logging to the method
2. Process a contact and check the logs
3. Verify that the method is being called with the correct parameters

#### Check for Database Permissions

Make sure your Supabase API key has the necessary permissions:

1. Go to the Supabase dashboard
2. Navigate to "Authentication" > "Policies"
3. Verify that there are appropriate policies for the core_data table
4. If needed, add a policy to allow updating the table:
   ```sql
   CREATE POLICY "Allow updating core_data" 
   ON core_data FOR UPDATE USING (true);
   ```

### 3. Adding Test Data

If you want to add test data to verify the tracking works:

```sql
-- Add a test record with a failed form submission
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

After adding test data, refresh the dashboard and click the "Refresh" button in the Failed Form Submissions section.

### 4. Checking the Browser Console for Errors

If you're still having issues, check the browser console for errors:

1. Open the browser's developer tools (F12 or right-click > Inspect)
2. Go to the Console tab
3. Look for any error messages
4. If you see CORS errors, make sure your Flask app is properly configured
5. If you see JavaScript errors, check the dashboard.html file for issues

### 5. Restarting the Application

Sometimes a simple restart can fix connection issues:

1. Stop the Flask application (Ctrl+C in the terminal)
2. Start it again:
   ```bash
   python app.py
   ```
3. Refresh the dashboard and try again

## Advanced Troubleshooting

### Checking the Server Logs

Check the terminal where you're running the Flask application for any error messages, especially related to the `/api/form-submissions` endpoint.

### Manually Testing the API

You can use tools like curl or Postman to test the API:

```bash
curl http://127.0.0.1:5000/api/form-submissions?failed=true
```

### Checking the Network Tab

1. Open the browser's developer tools (F12)
2. Go to the Network tab
3. Click the "Refresh" button in the Failed Form Submissions section
4. Look for a request to `/api/form-submissions`
5. Click on it to see the request and response details

## If All Else Fails

If you've tried everything and still can't get the tracking to work:

1. Make sure all the required columns exist in your database
2. Verify that the TABLE_NAME constant is set to "core_data" in both app.py and contact_bot.py
3. Check that your Supabase URL and API key are correct
4. Try processing a contact with the browser visible (non-headless mode) to see what's happening
5. Look at the screenshots saved in the application directory for clues
