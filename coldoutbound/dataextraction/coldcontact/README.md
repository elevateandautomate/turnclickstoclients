# Contact Bot

An automated system for website contact form filling and LinkedIn outreach.

## Features

- **Website Contact Form Automation**: Automatically finds and fills contact forms on target websites
- **LinkedIn Outreach**: Searches for contacts on LinkedIn and sends personalized connection requests
- **CSV Upload**: Upload CSV files with contact information
- **Progress Tracking**: Monitor the status of each contact through a web dashboard
- **Supabase Integration**: Store contact information and track progress in a Supabase database

## Requirements

- Python 3.8+
- Microsoft Edge WebDriver
- Supabase account
- LinkedIn account (for LinkedIn outreach)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/contact-bot.git
   cd contact-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure Supabase:
   - Create a Supabase account at https://supabase.io
   - Create a new project
   - Create a table named `contacts` with the following columns:
     - `id` (uuid, primary key)
     - `name` (text)
     - `email` (text)
     - `company` (text)
     - `website_url` (text)
     - `linkedin_url` (text)
     - `website_visited` (boolean, nullable)
     - `website_visited_message` (text, nullable)
     - `website_visited_timestamp` (timestamp, nullable)
     - `contact_form_found` (boolean, nullable)
     - `contact_form_found_message` (text, nullable)
     - `contact_form_found_timestamp` (timestamp, nullable)
     - `contact_form_submitted` (boolean, nullable)
     - `contact_form_submitted_message` (text, nullable)
     - `contact_form_submitted_timestamp` (timestamp, nullable)
     - `linkedin_connected` (boolean, nullable)
     - `linkedin_connected_message` (text, nullable)
     - `linkedin_connected_timestamp` (timestamp, nullable)
     - `error` (text, nullable)
     - `created_at` (timestamp with time zone, default: now())

4. Update configuration:
   - Open `contact_bot.py` and update the following variables:
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_KEY`: Your Supabase service role key
     - `LINKEDIN_USERNAME`: Your LinkedIn username
     - `LINKEDIN_PASSWORD`: Your LinkedIn password

## Usage

### Running the Web Interface

1. Start the Flask web server:
   ```
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

### Uploading CSV Files

1. Prepare a CSV file with the following columns:
   - `name`: Contact's name
   - `email`: Contact's email address
   - `company`: Company name
   - `website_url`: URL of the company website
   - `linkedin_url`: URL of the contact's LinkedIn profile (optional)

2. Upload the CSV file through the web interface

### Processing Contacts

1. After uploading a CSV file, the system will automatically start processing the contacts
2. You can also process existing contacts in the database by clicking the "Start Processing" button

### Monitoring Progress

1. Navigate to the Dashboard page to view the progress of each contact
2. The dashboard shows the status of each step:
   - Website Visited
   - Contact Form Found
   - Form Submitted
   - LinkedIn Connected

3. Click the info button to view detailed information about a contact
4. Click the retry button to retry processing a contact

## How It Works

1. **Website Contact Form Detection**:
   - The bot visits the target website
   - It searches for contact forms using various selectors
   - If a form is found, it fills in the contact information and submits it

2. **LinkedIn Outreach**:
   - The bot logs in to LinkedIn
   - It searches for the contact using their name and company
   - If found, it sends a connection request with a personalized message

3. **Status Tracking**:
   - Each step is tracked in the Supabase database
   - The web dashboard displays the status of each contact

## Customization

### Personalized Messages

You can customize the messages sent through contact forms and LinkedIn by modifying the following methods in `contact_bot.py`:

- `_generate_message()`: For contact form messages
- `_generate_linkedin_message()`: For LinkedIn connection requests

### Contact Form Detection

The bot uses various selectors to find contact forms. You can add more selectors in the `_find_contact_form()` method in `contact_bot.py`.

## Limitations

- The bot may not be able to find all contact forms, especially those with unusual structures or heavy JavaScript
- LinkedIn has rate limits for connection requests, so be careful not to send too many in a short period
- Some websites may have anti-bot measures that could block automated form submissions

## License

This project is licensed under the MIT License - see the LICENSE file for details.
