-- SQL script to add a test failed form submission
-- Run this in the Supabase SQL Editor

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

-- Add another test record with NULL form submission status
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
    'Test NULL Contact', 
    'Test NULL Company', 
    'https://testnull.com', 
    'lawyer',
    NULL,
    'This contact has NULL submission status',
    NOW()
);

-- Verify the records were added
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
    name IN ('Test Failed Contact', 'Test NULL Contact')
ORDER BY 
    contact_form_submitted_timestamp DESC;
