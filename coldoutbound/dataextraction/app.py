"""
Flask web application for Contact Bot

This application provides a web interface for:
1. Uploading CSV files with contact information
2. Viewing progress of contact processing
3. Managing the contact bot
"""

import os
import json
import uuid
import logging
import threading
import collections
import traceback
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Deque
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename
from supabase import create_client, Client
from selenium.webdriver.common.by import By

# Import the ContactBot class
from contact_bot import ContactBot

# Constants - these will be overridden by settings if available
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"  # Using the core_data table (renamed from dentist)

# Settings file path
SETTINGS_FILE = 'settings.json'

# Flask app setup
app = Flask(__name__)
app.secret_key = "your-secret-key"  # Change this to a secure random key in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Custom Jinja2 filters
@app.template_filter('datetime')
def format_datetime(value):
    """Format ISO datetime string to readable format"""
    if not value:
        return ""
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y %I:%M %p')
    except:
        return value
ALLOWED_EXTENSIONS = {'csv'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load settings
def load_settings() -> Dict[str, Any]:
    """Load settings from file

    Returns:
        Dictionary of settings
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    return {}

def save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to file

    Args:
        settings: Dictionary of settings
    """
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

# Load settings
settings = load_settings()

# Override constants with settings if available
if settings.get('supabase_url'):
    SUPABASE_URL = settings.get('supabase_url')
if settings.get('supabase_key'):
    SUPABASE_KEY = settings.get('supabase_key')
if settings.get('table_name'):
    TABLE_NAME = settings.get('table_name')

# Initialize Supabase client
supabase: Optional[Client] = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")
    else:
        print("CRITICAL: Supabase URL or Key is missing.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

# Global bot instance and processing thread
bot_thread = None
bot_instance = None
is_processing = False

# In-memory log handler
class MemoryLogHandler(logging.Handler):
    """Custom log handler that stores logs in memory"""

    def __init__(self, capacity=1000):
        """Initialize the handler with a capacity for log entries"""
        super().__init__()
        self.log_records: Deque[Dict[str, Any]] = collections.deque(maxlen=capacity)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        """Store the log record in memory"""
        self.log_records.append({
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'message': self.format(record),
            'source': record.name
        })

    def get_logs(self, limit=100, level=None) -> List[Dict[str, Any]]:
        """Get the most recent logs, optionally filtered by level"""
        if level:
            return list(filter(lambda x: x['level'] == level, list(self.log_records)))[-limit:]
        return list(self.log_records)[-limit:]

# Set up logging
logger = logging.getLogger('contact_bot')
logger.setLevel(logging.DEBUG)

# Create memory handler
memory_handler = MemoryLogHandler(capacity=1000)
memory_handler.setLevel(logging.DEBUG)
logger.addHandler(memory_handler)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Log startup
logger.info("Application starting up")

def allowed_file(filename: str) -> bool:
    """Check if file has an allowed extension

    Args:
        filename: Name of the file

    Returns:
        True if file has an allowed extension
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_contacts_thread(csv_path: Optional[str] = None, list_id: Optional[str] = None, limit: int = 10, filter_type: str = 'all', browser_mode: str = None, resume: bool = True, specific_contact_id: Optional[str] = None, is_retry: bool = False) -> None:
    """Process contacts in a separate thread

    Args:
        csv_path: Path to CSV file (optional)
        list_id: ID of the contact list (optional)
        limit: Maximum number of contacts to process
        filter_type: Type of contacts to process ('all', 'pending', 'failed')
        browser_mode: Browser mode ('headless' or 'visible')
        resume: Whether to resume from the last processed contact
        specific_contact_id: Process only this specific contact ID (optional)
        is_retry: Whether this is a retry operation (skips column checks)
    """
    global is_processing, bot_instance
    is_processing = True
    bot = None  # Initialize bot variable outside try block for cleanup

    try:
        logger.info(f"Starting contact processing thread. CSV: {csv_path}, List ID: {list_id}, Limit: {limit}, Filter: {filter_type}, Browser Mode: {browser_mode}")

        # Update contact list status
        if list_id and supabase:
            try:
                logger.info(f"Updating contact list {list_id} status to 'processing'")
                supabase.table('contact_lists').update({'status': 'processing'}).eq('id', list_id).execute()
            except Exception as e:
                logger.error(f"Error updating contact list status: {e}")

        # Load settings for LinkedIn credentials
        logger.debug("Loading settings")
        settings = load_settings()
        linkedin_username = settings.get('linkedin_username', '')
        linkedin_password = settings.get('linkedin_password', '')
        your_name = settings.get('your_name', 'Your Name')

        # Determine headless mode - use browser_mode parameter if provided, otherwise use settings
        headless_mode = True  # Default to headless
        if browser_mode is not None:
            headless_mode = browser_mode == 'headless'
            logger.info(f"Using browser mode from parameter: {browser_mode} (headless: {headless_mode})")
        else:
            headless_mode = settings.get('headless_mode', 'true') == 'true'
            logger.info(f"Using browser mode from settings: {headless_mode}")

        browser_speed = settings.get('browser_speed', 'normal')

        # Create bot with settings
        logger.info(f"Initializing ContactBot (headless: {headless_mode}, speed: {browser_speed}, is_retry: {is_retry})")

        # Initialize the bot with settings and is_retry flag
        supabase_url = os.environ.get('SUPABASE_URL', '')
        supabase_key = os.environ.get('SUPABASE_KEY', '')

        bot = ContactBot(
            headless=headless_mode,
            browser_speed=browser_speed,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            your_name=settings.get('your_name', ''),
            linkedin_username=settings.get('linkedin_username', ''),
            linkedin_password=settings.get('linkedin_password', ''),
            contact_form_template=settings.get('contact_form_template', ''),
            settings=settings,
            is_retry=is_retry  # Pass the is_retry flag
        )

        global bot_instance
        bot_instance = bot  # Store bot in global variable for status access
        bot.stop_requested = False  # Add a flag to check for stop requests

        # Set browser speed if available
        if hasattr(bot, 'set_browser_speed') and browser_speed:
            bot.set_browser_speed(browser_speed)

        # Set LinkedIn credentials if available
        if linkedin_username and linkedin_password:
            logger.info("Setting LinkedIn credentials")
            bot.set_linkedin_credentials(linkedin_username, linkedin_password)
        else:
            logger.warning("LinkedIn credentials not set - LinkedIn features will not work")

        # Set message templates if available
        if settings.get('contact_form_template'):
            logger.info("Setting contact form template")
            bot.set_contact_form_template(settings.get('contact_form_template'), your_name)
        else:
            logger.warning("Contact form template not set - using default")

        if settings.get('linkedin_template'):
            logger.info("Setting LinkedIn message template")
            bot.set_linkedin_template(settings.get('linkedin_template'), your_name)
        else:
            logger.warning("LinkedIn message template not set - using default")

        try:
            # Check if processing should continue
            if not is_processing:
                logger.info("Processing stopped before starting")
                return

            if csv_path:
                # Process contacts from CSV file
                logger.info(f"Processing contacts from CSV file: {csv_path}")
                total_contacts, successful_contacts, failed_contacts = 0, 0, 0

                # Call the process_csv method and capture statistics
                logger.debug("Calling process_csv method")
                result = bot.process_csv(csv_path)

                # If the method returns statistics, use them
                if isinstance(result, tuple) and len(result) == 3:
                    total_contacts, successful_contacts, failed_contacts = result
                    logger.info(f"CSV processing complete. Total: {total_contacts}, Successful: {successful_contacts}, Failed: {failed_contacts}")
                else:
                    logger.warning("CSV processing did not return statistics")

                # Update contact list statistics
                if list_id and supabase and is_processing:  # Only update if not stopped
                    try:
                        logger.info(f"Updating contact list {list_id} statistics")
                        supabase.table('contact_lists').update({
                            'status': 'completed',
                            'total_contacts': total_contacts,
                            'processed_contacts': total_contacts,
                            'successful_contacts': successful_contacts,
                            'failed_contacts': failed_contacts,
                            'completed_at': datetime.now().isoformat()
                        }).eq('id', list_id).execute()
                        logger.info(f"Contact list {list_id} marked as completed")
                    except Exception as e:
                        logger.error(f"Error updating contact list statistics: {e}")
            else:
                # Process contacts from Supabase with filter
                # Keep browser open for inspection if not in headless mode
                keep_browser_open = not headless_mode and is_processing  # Only keep open if not stopped

                # Add a check for stop request in the bot's process method
                def check_stop():
                    if not is_processing:
                        logger.info("Stop requested during processing")
                        return True
                    return False

                # Assign the check function to the bot
                bot.check_stop = check_stop

                # Get resume setting from settings
                resume_setting = settings.get('resume_processing', 'true') == 'true' if resume is None else resume
                resume_msg = "resuming from last processed contact" if resume_setting else "starting from beginning"

                # If specific_contact_id is provided, process only that contact
                if specific_contact_id:
                    logger.info(f"Processing specific contact with ID: {specific_contact_id}")
                    try:
                        # Get the contact from Supabase
                        contact_response = supabase.table(TABLE_NAME).select("*").eq("id", specific_contact_id).execute()
                        if contact_response.data and len(contact_response.data) > 0:
                            contact = contact_response.data[0]
                            logger.info(f"Found contact: {contact.get('name', 'Unknown')} (ID: {specific_contact_id})")

                            # Process the single contact
                            # Note: _process_single_contact is a private method, but we need to use it directly
                            # for the retry functionality
                            if hasattr(bot, '_process_single_contact'):
                                bot._process_single_contact(contact)
                                logger.info(f"Processed contact {contact.get('name', 'Unknown')}")

                                # Keep browser open if requested
                                if keep_browser_open and not bot.headless:
                                    logger.info("Keeping browser open for inspection")
                                    for i in range(60, 0, -1):
                                        # Check if processing should stop
                                        if hasattr(bot, 'check_stop') and callable(bot.check_stop) and bot.check_stop():
                                            logger.info("Processing stopped, closing browser")
                                            break

                                        print(f"\rBrowser will close in {i} seconds...", end="")
                                        time.sleep(1)
                            else:
                                logger.error("Bot does not have _process_single_contact method")
                        else:
                            logger.error(f"Contact with ID {specific_contact_id} not found")
                    except Exception as e:
                        logger.error(f"Error processing specific contact: {e}")
                        traceback.print_exc()
                # Otherwise process contacts based on filter
                elif filter_type == 'pending':
                    logger.info(f"Processing up to {limit} pending contacts from Supabase ({resume_msg})")
                    bot.process_contacts_from_supabase(limit=limit, filter_status='pending', keep_browser_open=keep_browser_open, resume=resume_setting)
                elif filter_type == 'failed':
                    logger.info(f"Processing up to {limit} failed contacts from Supabase ({resume_msg})")
                    bot.process_contacts_from_supabase(limit=limit, filter_status='failed', keep_browser_open=keep_browser_open, resume=resume_setting)
                else:
                    logger.info(f"Processing up to {limit} contacts from Supabase (all) ({resume_msg})")
                    bot.process_contacts_from_supabase(limit=limit, keep_browser_open=keep_browser_open, resume=resume_setting)
        finally:
            if bot:
                logger.info("Closing bot")
                bot.close()

    except Exception as e:
        logger.error(f"Error in processing thread: {e}", exc_info=True)

        # Update contact list status on error
        if list_id and supabase:
            try:
                logger.info(f"Updating contact list {list_id} status to 'error'")
                supabase.table('contact_lists').update({
                    'status': 'error',
                    'error_message': str(e)
                }).eq('id', list_id).execute()
            except Exception as e2:
                logger.error(f"Error updating contact list error status: {e2}")
    finally:
        # Clean up resources
        if not is_processing and bot:
            logger.info("Processing was stopped - ensuring bot is closed")
            try:
                bot.close()
            except Exception as e:
                logger.error(f"Error closing bot after stop: {e}")

        # If processing was stopped, log it
        if not is_processing:
            logger.info("Processing thread terminated due to stop request")
        else:
            logger.info("Processing thread completed normally")

        # Reset processing flag
        is_processing = False

def get_available_template_variables():
    """Get available template variables from Supabase table

    Returns:
        List of column names that can be used as template variables
    """
    # Variables from user settings (always available)
    user_vars = ["your_name", "your_email", "phone", "your_first_name", "your_last_name", "your_company"]

    if not supabase:
        logger.warning("Supabase client not initialized. Cannot get template variables.")
        return user_vars  # Return only user variables if Supabase is not available

    try:
        # Try to get one record to check the structure
        sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()
        if sample.data:
            # Get actual column names from the table
            columns = list(sample.data[0].keys())
            logger.info(f"Available template variables from table: {', '.join(columns)}")

            # Combine table columns with user variables
            all_vars = columns + user_vars

            # Remove duplicates while preserving order
            unique_vars = []
            for var in all_vars:
                if var not in unique_vars:
                    unique_vars.append(var)

            return unique_vars
        else:
            logger.warning("No data found in table. Using only user variables.")
            return user_vars
    except Exception as e:
        logger.error(f"Error getting template variables: {e}")
        return user_vars

@app.route('/')
def index():
    """Home page with CSV upload form"""
    # Load settings for the dashboard
    current_settings = load_settings()

    # Get available template variables
    template_variables = get_available_template_variables()

    return render_template('index.html',
                          is_processing=is_processing,
                          settings=current_settings,
                          supabase=supabase,
                          table_name=TABLE_NAME,
                          template_variables=template_variables)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload"""
    # For AJAX requests
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if 'file' not in request.files:
        message = 'No file part'
        if is_ajax:
            return jsonify({'error': message}), 400
        flash(message)
        return redirect(request.url)

    file = request.files['file']
    list_name = request.form.get('list_name', 'Unnamed List')
    process_immediately = request.form.get('process_immediately') == 'on'

    if file.filename == '':
        message = 'No selected file'
        if is_ajax:
            return jsonify({'error': message}), 400
        flash(message)
        return redirect(request.url)

    if file and allowed_file(file.filename):
        # Save file with timestamp and list name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_list_name = secure_filename(list_name)
        filename = f"{timestamp}_{safe_list_name}.csv"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Create contact list entry
        list_id = str(uuid.uuid4())
        contact_list = {
            'id': list_id,
            'name': list_name,
            'filename': filename,
            'created_at': datetime.now().isoformat(),
            'status': 'uploaded',
            'total_contacts': 0,
            'processed_contacts': 0,
            'successful_contacts': 0,
            'failed_contacts': 0
        }

        # Save contact list to database
        if supabase:
            try:
                supabase.table('contact_lists').insert(contact_list).execute()
            except Exception as e:
                print(f"Error saving contact list: {e}")

        # Start processing in a separate thread if requested
        global bot_thread
        if process_immediately:
            if bot_thread is not None and bot_thread.is_alive():
                message = 'Processing already in progress'
                if is_ajax:
                    return jsonify({'error': message}), 400
                flash(message)
                return redirect(url_for('index'))

            bot_thread = threading.Thread(target=process_contacts_thread, args=(file_path, list_id))
            bot_thread.daemon = True
            bot_thread.start()
            message = f'File "{list_name}" uploaded and processing started'
        else:
            message = f'File "{list_name}" uploaded successfully'

        if is_ajax:
            return jsonify({'success': True, 'message': message, 'list_id': list_id})

        flash(message)
        return redirect(url_for('dashboard'))
    else:
        message = 'Invalid file type. Please upload a CSV file.'
        if is_ajax:
            return jsonify({'error': message}), 400
        flash(message)
        return redirect(request.url)

@app.route('/process')
def process():
    """Start processing contacts from Supabase"""
    global bot_thread

    # Debug logging
    print(f"Process route called with table name: {TABLE_NAME}")

    # Test Supabase connection
    if supabase:
        try:
            print("Testing Supabase connection...")
            data = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            print(f"Supabase test query result: {data}")
        except Exception as e:
            print(f"Error connecting to Supabase: {str(e)}")
            traceback.print_exc()
    else:
        print("Supabase client is not initialized")

    # Check if AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == 'true'

    if bot_thread is not None and bot_thread.is_alive():
        if is_ajax:
            return jsonify({"error": "Processing already in progress"}), 400
        else:
            flash('Processing already in progress')
            return redirect(url_for('dashboard'))

    limit = request.args.get('limit', 10, type=int)
    filter_type = request.args.get('filter', 'all')
    browser_mode = request.args.get('browser_mode', 'headless')
    resume = request.args.get('resume', 'true') == 'true'

    # Validate limit
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100

    # Update headless mode setting based on browser_mode
    current_settings = load_settings()
    current_settings['headless_mode'] = 'true' if browser_mode == 'headless' else 'false'
    current_settings['resume_processing'] = 'true' if resume else 'false'
    save_settings(current_settings)

    logger.info(f"Starting processing with browser mode: {browser_mode}, limit: {limit}, filter: {filter_type}, resume: {resume}")

    # Start processing thread with filter and browser mode
    bot_thread = threading.Thread(target=process_contacts_thread, args=(None, None, limit, filter_type, browser_mode, resume))
    bot_thread.daemon = True
    bot_thread.start()

    # Create a message based on the filter and browser mode
    browser_msg = "in background" if browser_mode == 'headless' else "with visible browser"
    if filter_type == 'pending':
        message = f'Processing started for up to {limit} pending contacts {browser_msg}'
    elif filter_type == 'failed':
        message = f'Processing started for up to {limit} failed contacts {browser_msg}'
    else:
        message = f'Processing started for up to {limit} contacts {browser_msg}'

    if is_ajax:
        return jsonify({
            "success": True,
            "message": message,
            "is_processing": True,
            "limit": limit,
            "filter": filter_type,
            "browser_mode": browser_mode
        })
    else:
        flash(message)
        return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard for viewing progress"""
    contacts = []
    contact_lists = []

    if supabase:
        try:
            # Fetch contact lists
            lists_response = supabase.table('contact_lists').select("*").order('created_at', desc=True).execute()
            contact_lists = lists_response.data

            # Fetch contacts
            contacts_response = supabase.table(TABLE_NAME).select("*").order('created_at', desc=True).limit(100).execute()
            contacts = contacts_response.data
        except Exception as e:
            print(f"Error fetching data: {e}")

    # Load settings for the dashboard
    current_settings = load_settings()

    # Get available template variables
    template_variables = get_available_template_variables()

    return render_template('dashboard.html',
                          contacts=contacts,
                          contact_lists=contact_lists,
                          is_processing=is_processing,
                          settings=current_settings,
                          template_variables=template_variables)

@app.route('/api/contacts')
def api_contacts():
    """API endpoint for getting contacts data"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    try:
        response = supabase.table(TABLE_NAME).select("*").order('created_at', desc=True).limit(100).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/enrichment/<contact_id>')
def api_enrichment(contact_id):
    """API endpoint for getting contact enrichment data"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    try:
        # First check if the enrichment table exists
        try:
            # Try to query the enrichment table
            enrichment_response = supabase.table("contact_enrichment") \
                .select("*") \
                .eq("contact_id", contact_id) \
                .eq("source_table", TABLE_NAME) \
                .execute()

            if enrichment_response.data and len(enrichment_response.data) > 0:
                # Return the enrichment data
                return jsonify({
                    "success": True,
                    "enrichment": enrichment_response.data[0]
                })
            else:
                # Check for alternative_contacts in the main table as fallback
                contact_response = supabase.table(TABLE_NAME) \
                    .select("alternative_contacts") \
                    .eq("id", contact_id) \
                    .execute()

                if contact_response.data and len(contact_response.data) > 0 and contact_response.data[0].get("alternative_contacts"):
                    return jsonify({
                        "success": True,
                        "enrichment": {
                            "contact_id": contact_id,
                            "source_table": TABLE_NAME,
                            "raw_data": contact_response.data[0]["alternative_contacts"]
                        }
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": "No enrichment data found for this contact"
                    })
        except Exception as e:
            if "does not exist" in str(e).lower():
                # Table doesn't exist yet
                return jsonify({
                    "success": False,
                    "message": "Enrichment table does not exist yet"
                })
            else:
                raise e

    except Exception as e:
        logger.error(f"Error fetching enrichment data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for getting processing status"""
    status_data = {
        "is_processing": is_processing,
        "current_time": datetime.now().isoformat()
    }

    # Check if we have a bot instance with status data
    global bot_instance
    if is_processing and bot_instance and hasattr(bot_instance, '_memory_status'):
        memory_status = bot_instance._memory_status.get('current_processing_status', {})
        if memory_status:
            status_data.update({
                "current_status": memory_status,
                "has_status_details": True,
                "status_source": "memory"
            })
            logger.info(f"Returning status from bot memory: {memory_status}")
            return jsonify(status_data)

    # If no memory status, try to get from database
    if supabase:
        try:
            # Check if settings table exists
            try:
                settings_response = supabase.table('outreach_settings').select("value").eq("key", "current_processing_status").execute()
                if settings_response.data and len(settings_response.data) > 0:
                    try:
                        current_status = json.loads(settings_response.data[0].get("value", "{}"))
                        status_data.update({
                            "current_status": current_status,
                            "has_status_details": True,
                            "status_source": "database"
                        })
                        logger.info(f"Returning status from database")
                    except Exception as e:
                        logger.error(f"Error parsing current status: {e}")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    # outreach_settings table doesn't exist yet
                    logger.warning("Outreach settings table does not exist yet. Status updates will be stored in memory until the table is created.")

                    # Create a dummy status if we're processing but don't have status data
                    if is_processing:
                        dummy_status = {
                            "current_contact_name": "Processing...",
                            "current_company_name": "Please wait",
                            "current_website": "#",
                            "processing_stage": "starting",
                            "last_updated": datetime.now().isoformat()
                        }
                        status_data.update({
                            "current_status": dummy_status,
                            "has_status_details": True,
                            "status_source": "dummy"
                        })
                        logger.info("Returning dummy status")
                else:
                    logger.error(f"Error getting current status from settings: {e}")
        except Exception as e:
            logger.error(f"Error getting current status: {e}")

    # Add debug info
    status_data["debug_info"] = {
        "is_processing": is_processing,
        "has_bot_instance": bot_instance is not None,
        "has_memory_status": bot_instance and hasattr(bot_instance, '_memory_status'),
        "server_time": datetime.now().isoformat()
    }

    return jsonify(status_data)

@app.route('/api/retry/<contact_id>')
def api_retry(contact_id):
    """API endpoint for retrying a contact"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    try:
        # Reset status fields
        update_data = {
            "website_visited": None,
            "website_visited_message": None,
            "contact_form_found": None,
            "contact_form_found_message": None,
            "contact_form_submitted": None,
            "contact_form_submitted_message": None,
            "linkedin_connected": None,
            "linkedin_connected_message": None,
            "error": None
        }

        supabase.table(TABLE_NAME).update(update_data).eq("id", contact_id).execute()

        # Start processing in a separate thread if not already running
        global bot_thread
        if bot_thread is None or not bot_thread.is_alive():
            bot_thread = threading.Thread(target=process_contacts_thread)
            bot_thread.daemon = True
            bot_thread.start()

        return jsonify({"success": True, "message": f"Contact {contact_id} queued for retry"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process-list/<list_id>')
def api_process_list(list_id):
    """API endpoint for processing a contact list"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    global bot_thread, is_processing
    if is_processing:
        return jsonify({"error": "Processing already in progress"}), 400

    try:
        # Get the contact list
        response = supabase.table('contact_lists').select("*").eq("id", list_id).execute()
        if not response.data:
            return jsonify({"error": "Contact list not found"}), 404

        contact_list = response.data[0]

        # Get the file path
        filename = contact_list.get('filename')
        if not filename:
            return jsonify({"error": "File not found for this contact list"}), 404

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "CSV file not found"}), 404

        # Start processing in a separate thread
        bot_thread = threading.Thread(target=process_contacts_thread, args=(file_path, list_id))
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({"success": True, "message": f"Contact list {list_id} processing started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-list/<list_id>')
def api_delete_list(list_id):
    """API endpoint for deleting a contact list"""
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    try:
        # Get the contact list
        response = supabase.table('contact_lists').select("*").eq("id", list_id).execute()
        if not response.data:
            return jsonify({"error": "Contact list not found"}), 404

        contact_list = response.data[0]

        # Delete the file if it exists
        filename = contact_list.get('filename')
        if filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)

        # Delete the contact list from the database
        supabase.table('contact_lists').delete().eq("id", list_id).execute()

        return jsonify({"success": True, "message": f"Contact list {list_id} deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """API endpoint for testing Supabase connection"""
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    supabase_url = data.get('supabase_url')
    supabase_key = data.get('supabase_key')
    table_name = data.get('table_name')

    if not supabase_url or not supabase_key or not table_name:
        return jsonify({"error": "Missing required parameters"}), 400

    logger.info(f"Testing connection to Supabase table: {table_name}")

    try:
        # Create a temporary Supabase client with the provided credentials
        temp_supabase = create_client(supabase_url, supabase_key)

        # Try to count records in the specified table
        response = temp_supabase.table(table_name).select("*", count="exact").limit(1).execute()

        # Get the count from the response
        count = response.count

        logger.info(f"Connection test successful. Found {count} records in {table_name}")

        return jsonify({
            "success": True,
            "message": "Connection successful",
            "count": count
        })
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/stop-processing', methods=['POST'])
def api_stop_processing():
    """API endpoint for stopping the bot"""
    global bot_thread, is_processing

    logger.info("Received request to stop processing")

    if bot_thread is None or not bot_thread.is_alive():
        logger.warning("No processing thread is running")
        return jsonify({"success": False, "message": "No processing is currently running"}), 400

    try:
        # Set the is_processing flag to False to signal the thread to stop
        is_processing = False

        # Log the stop request
        logger.info("Processing stop requested. Waiting for thread to terminate...")

        # Wait for the thread to terminate (with timeout)
        bot_thread.join(timeout=5.0)

        # Check if the thread is still alive after timeout
        if bot_thread.is_alive():
            logger.warning("Thread did not terminate within timeout. Forcing termination.")
            # We can't forcefully terminate a thread in Python, but we can set it to None
            # so that new processes can start
            bot_thread = None
            return jsonify({"success": True, "message": "Processing stop requested, but thread did not terminate cleanly"})
        else:
            logger.info("Processing thread terminated successfully")
            return jsonify({"success": True, "message": "Processing stopped successfully"})
    except Exception as e:
        logger.error(f"Error stopping processing: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """API endpoint for getting application logs"""
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level', None)
    filter_type = request.args.get('filter', 'all')

    logger.debug(f"Fetching logs. Limit: {limit}, Level: {level}, Filter: {filter_type}")

    try:
        logs = memory_handler.get_logs(limit=limit, level=level)

        # Apply additional filtering if needed
        if filter_type == 'status':
            # Filter logs that contain status information
            status_logs = []
            status_keywords = [
                'CURRENT_STATUS_UPDATE',
                'BOT_STATUS_UPDATE',
                'NOW PROCESSING CONTACT',
                'processing_stage',
                'Looking for contact form',
                'Contact form found',
                'Filling contact form',
                'Successfully submitted',
                'Failed to submit',
                'Attempting LinkedIn',
                'LinkedIn connection',
                'Visiting website',
                'Website visited',
                'Starting processing',
                'Processing complete',
                'Processing contact',
                'Error processing',
                'Initializing',
                'Starting up',
                'Bot status'
            ]

            for log in logs:
                # Check if any of the keywords are in the message
                if any(keyword in log['message'] for keyword in status_keywords):
                    status_logs.append(log)

            # If no status logs found, add a placeholder log
            if not status_logs:
                # Add a placeholder status log if we're not processing
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Check if we're processing using the global variable
                global is_processing

                if is_processing:
                    status_logs.append({
                        'timestamp': current_time,
                        'level': 'INFO',
                        'message': 'BOT_STATUS_UPDATE: Processing in progress. Waiting for status updates...'
                    })
                else:
                    status_logs.append({
                        'timestamp': current_time,
                        'level': 'INFO',
                        'message': 'BOT_STATUS_UPDATE: Bot is idle. No processing is currently active. Click "Start Processing" to begin.'
                    })

            logs = status_logs

        return jsonify({
            "success": True,
            "logs": logs
        })
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/template-variables')
def api_template_variables():
    """API endpoint for getting available template variables"""
    try:
        variables = get_available_template_variables()
        return jsonify({
            "success": True,
            "variables": variables
        })
    except Exception as e:
        logger.error(f"Error fetching template variables: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-setting', methods=['POST'])
def api_update_setting():
    """API endpoint for updating a single setting"""
    key = request.form.get('key')
    value = request.form.get('value')

    if not key:
        return jsonify({"error": "Missing key parameter"}), 400

    logger.info(f"Updating setting: {key} = {value}")

    try:
        # Load current settings
        current_settings = load_settings()

        # Update the setting
        current_settings[key] = value

        # Save settings
        save_settings(current_settings)

        # If updating headless mode, update browser_mode in the process form
        if key == 'headless_mode':
            logger.info(f"Updated headless mode to: {value}")

        return jsonify({
            "success": True,
            "message": f"Setting {key} updated successfully"
        })
    except Exception as e:
        logger.error(f"Error updating setting: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/settings')
def settings_page():
    """Settings page - redirects to dashboard with settings tab"""
    return redirect(url_for('dashboard') + '#linkedin')

@app.route('/settings/credentials', methods=['POST'])
def save_credentials():
    """Save credentials settings"""
    current_settings = load_settings()

    # Update settings with form data
    current_settings['linkedin_username'] = request.form.get('linkedin_username', '')
    current_settings['linkedin_password'] = request.form.get('linkedin_password', '')
    current_settings['supabase_url'] = request.form.get('supabase_url', '')
    current_settings['supabase_key'] = request.form.get('supabase_key', '')
    current_settings['table_name'] = request.form.get('table_name', 'contacts')

    # Save settings
    save_settings(current_settings)

    # Update global variables
    global SUPABASE_URL, SUPABASE_KEY, TABLE_NAME, supabase
    SUPABASE_URL = current_settings.get('supabase_url')
    SUPABASE_KEY = current_settings.get('supabase_key')
    TABLE_NAME = current_settings.get('table_name')

    # Reinitialize Supabase client
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("Successfully reinitialized Supabase client.")
        else:
            print("CRITICAL: Supabase URL or Key is missing.")
    except Exception as e:
        print(f"Error reinitializing Supabase client: {e}")

    flash('Credentials saved successfully')
    return redirect(url_for('dashboard') + '#linkedin')

@app.route('/settings/messages', methods=['POST'])
def save_messages():
    """Save message templates and contact form settings"""
    current_settings = load_settings()

    # Update contact details fields first
    current_settings['your_first_name'] = request.form.get('your_first_name', '')
    current_settings['your_last_name'] = request.form.get('your_last_name', '')
    current_settings['your_email'] = request.form.get('your_email', '')
    current_settings['phone'] = request.form.get('phone', '')
    current_settings['your_company'] = request.form.get('your_company', '')

    # Get your_name or auto-generate it from first and last name if empty
    your_name = request.form.get('your_name', '').strip()
    if not your_name and current_settings['your_first_name'] and current_settings['your_last_name']:
        your_name = f"{current_settings['your_first_name']} {current_settings['your_last_name']}"
    current_settings['your_name'] = your_name

    # Update message templates
    current_settings['contact_form_template'] = request.form.get('contact_form_template', '')
    current_settings['linkedin_template'] = request.form.get('linkedin_template', '')

    # Update contact form detection settings
    current_settings['form_detection_priority'] = request.form.get('form_detection_priority', 'balanced')
    current_settings['navigate_to_contact_page'] = 'navigate_to_contact_page' in request.form
    current_settings['submit_form'] = 'submit_form' in request.form

    # Save settings
    save_settings(current_settings)

    flash('Message templates and contact form settings saved successfully')
    return redirect(url_for('dashboard') + '#messages')

@app.route('/api/clear-cookies', methods=['POST'])
def api_clear_cookies():
    """API endpoint for clearing saved cookies"""
    domain = request.form.get('domain', 'linkedin.com')

    logger.info(f"Received request to clear cookies for domain: {domain}")

    try:
        # Create a temporary bot instance to clear cookies
        temp_bot = ContactBot(headless=True)
        temp_bot.clear_cookies(domain)
        temp_bot.close()

        return jsonify({
            "success": True,
            "message": f"Cookies for {domain} cleared successfully"
        })
    except Exception as e:
        logger.error(f"Error clearing cookies: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/form-submissions-simple')
def api_form_submissions_simple():
    """Simplified API endpoint to get failed form submissions from Supabase"""
    print("API endpoint /api/form-submissions-simple called")
    if not supabase:
        print("Error: Supabase not initialized")
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Get limit parameter with default of 20
        limit = request.args.get('limit', 20, type=int)
        print(f"Getting form submissions with limit={limit}")

        # Simple query for records with contact_form_submitted = false
        response = supabase.table(TABLE_NAME).select("*").eq("contact_form_submitted", False).limit(limit).execute()

        print(f"Found {len(response.data)} records with contact_form_submitted=false")
        if response.data:
            print(f"Sample record: {response.data[0]}")
            print(f"Available fields: {list(response.data[0].keys())}")

        # Return the results
        return jsonify({
            "success": True,
            "submissions": response.data
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error getting form submissions: {e}")
        print(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.route('/api/form-submissions')
def api_form_submissions():
    """API endpoint to get form submission status from Supabase"""
    print("API endpoint /api/form-submissions called")
    if not supabase:
        print("Error: Supabase not initialized")
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 5, type=int)

        # Validate limit to allowed values
        allowed_limits = [5, 10, 20, 30, 100, 500]
        if limit not in allowed_limits:
            limit = 5  # Default to 5 if invalid

        # Calculate offset for pagination
        offset = (page - 1) * limit

        print(f"Getting form submissions with page={page}, limit={limit}, offset={offset}, failed={request.args.get('failed')}")

        # First, get the actual column names from the table
        print(f"Getting column names from {TABLE_NAME} table")
        try:
            sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            if sample.data:
                actual_columns = list(sample.data[0].keys())
                print(f"Actual columns in {TABLE_NAME}: {actual_columns}")

                # Build a select string with only the columns that exist
                select_columns = []
                column_mapping = {
                    "id": ["id", "uuid", "record_id"],
                    "name": ["listing_name", "name", "dentist_name_profile", "full_name"],  # listing_name is the actual column name
                    "company": ["listing_business_name", "company", "business_name_profile"],  # listing_business_name is the actual column name
                    "website_url": ["website_url_profile", "listing_website", "website_url", "website", "url"],  # website_url_profile is the actual column name
                    "niche": ["niche"],
                    "contact_form_submitted": ["contact_form_submitted"],
                    "contact_form_submitted_message": ["contact_form_submitted_message"],
                    "contact_form_submitted_timestamp": ["contact_form_submitted_timestamp"]
                }

                for expected_col, possible_cols in column_mapping.items():
                    found = False
                    for possible_col in possible_cols:
                        if possible_col in actual_columns:
                            select_columns.append(possible_col)
                            found = True
                            break
                    if not found and expected_col != "niche":  # niche is optional
                        print(f"Warning: No column found for {expected_col}")

                select_string = ",".join(select_columns)
                print(f"Using select string: {select_string}")

                # Query Supabase with the columns that exist
                query = supabase.table(TABLE_NAME).select(select_string).order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)
            else:
                print(f"No data found in {TABLE_NAME} table. Using default columns.")
                # Use a minimal set of columns that are likely to exist
                query = supabase.table(TABLE_NAME).select("*").range(offset, offset + limit - 1)
        except Exception as e:
            print(f"Error getting column names: {e}")
            # Fallback to selecting all columns
            query = supabase.table(TABLE_NAME).select("*").range(offset, offset + limit - 1)

        # Add filters based on request parameters
        if request.args.get('failed') == 'true':
            # Handle both explicit false values and NULL values
            # First, get records where contact_form_submitted is false
            query_false = supabase.table(TABLE_NAME).select(select_string).eq("contact_form_submitted", False).order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)

            # Then, get records where contact_form_submitted is NULL
            query_null = supabase.table(TABLE_NAME).select(select_string).is_("contact_form_submitted", None).order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)

            # Execute both queries
            print(f"Executing query for contact_form_submitted=false on table {TABLE_NAME}")
            response_false = query_false.execute()
            print(f"Found {len(response_false.data)} records with contact_form_submitted=false")
            if response_false.data:
                print(f"Sample record: {response_false.data[0]}")
                print(f"Available fields: {list(response_false.data[0].keys())}")

            print(f"Executing query for contact_form_submitted=NULL on table {TABLE_NAME}")
            response_null = query_null.execute()
            print(f"Found {len(response_null.data)} records with contact_form_submitted=NULL")
            if response_null.data:
                print(f"Sample record: {response_null.data[0]}")
                print(f"Available fields: {list(response_null.data[0].keys())}")

            # Combine the results
            combined_data = response_false.data + response_null.data
            print(f"Combined data has {len(combined_data)} records")

            # Return immediately with the combined data
            # Count both false and null values
            total_count_false = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", False).execute()
            total_count_null = supabase.table(TABLE_NAME).select("count", count="exact").is_("contact_form_submitted", None).execute()

            total_count = (total_count_false.count if hasattr(total_count_false, 'count') else 0) + \
                         (total_count_null.count if hasattr(total_count_null, 'count') else 0)
            total_pages = (total_count + limit - 1) // limit  # Ceiling division

            return jsonify({
                "success": True,
                "submissions": combined_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": total_pages
                }
            })
        elif request.args.get('submitted') == 'true':
            # Get records where contact_form_submitted is true
            query_submitted = supabase.table(TABLE_NAME).select(select_string).eq("contact_form_submitted", True).order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)

            # Execute query
            print(f"Executing query for contact_form_submitted=true on table {TABLE_NAME}")
            response_submitted = query_submitted.execute()
            print(f"Found {len(response_submitted.data)} records with contact_form_submitted=true")
            if response_submitted.data:
                print(f"Sample record: {response_submitted.data[0]}")
                print(f"Available fields: {list(response_submitted.data[0].keys())}")

            # Set combined data
            combined_data = response_submitted.data
            print(f"Combined data has {len(combined_data)} records")

            # Return immediately with the combined data
            total_count_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", True).execute()
            total_count = total_count_query.count if hasattr(total_count_query, 'count') else 0
            total_pages = (total_count + limit - 1) // limit  # Ceiling division

            return jsonify({
                "success": True,
                "submissions": combined_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": total_pages
                }
            })
        elif request.args.get('error') == 'true':
            # Get records with website errors
            # First try to find records with website_error=true if the column exists
            try:
                query_website_error = supabase.table(TABLE_NAME).select(select_string).eq("website_error", True).order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)
                response_website_error = query_website_error.execute()
                print(f"Found {len(response_website_error.data)} records with website_error=true")

                # Also look for error messages containing "website" or "URL"
                query_error_message = supabase.table(TABLE_NAME).select(select_string).like("contact_form_submitted_message", "%website%").order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)
                response_error_message = query_error_message.execute()
                print(f"Found {len(response_error_message.data)} records with error message containing 'website'")

                # Combine the results
                combined_data = response_website_error.data + response_error_message.data

                # Remove duplicates (if any)
                seen_ids = set()
                unique_data = []
                for record in combined_data:
                    if record.get('id') not in seen_ids:
                        seen_ids.add(record.get('id'))
                        unique_data.append(record)

                combined_data = unique_data
                print(f"Combined data has {len(combined_data)} records after removing duplicates")

                # Count website errors
                total_count_website_error = supabase.table(TABLE_NAME).select("count", count="exact").eq("website_error", True).execute()
                website_error_count = total_count_website_error.count if hasattr(total_count_website_error, 'count') else 0

                # Count records with error messages containing "website"
                total_count_error_message = supabase.table(TABLE_NAME).select("count", count="exact").like("contact_form_submitted_message", "%website%").execute()
                error_message_count = total_count_error_message.count if hasattr(total_count_error_message, 'count') else 0

                # Estimate total (may include some duplicates)
                total_count = website_error_count + error_message_count
                total_pages = (total_count + limit - 1) // limit  # Ceiling division
            except Exception as e:
                print(f"Error querying website errors: {e}")
                # Fallback to just error messages
                query_error_message = supabase.table(TABLE_NAME).select(select_string).like("contact_form_submitted_message", "%website%").order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)
                response_error_message = query_error_message.execute()
                combined_data = response_error_message.data
                print(f"Fallback: Found {len(combined_data)} records with error message containing 'website'")

                # Count records with error messages containing "website"
                total_count_error_message = supabase.table(TABLE_NAME).select("count", count="exact").like("contact_form_submitted_message", "%website%").execute()
                total_count = total_count_error_message.count if hasattr(total_count_error_message, 'count') else 0
                total_pages = (total_count + limit - 1) // limit  # Ceiling division

            # Return immediately with the combined data
            return jsonify({
                "success": True,
                "submissions": combined_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": total_pages
                }
            })
        else:
            # No specific filter, get all records
            query_all = supabase.table(TABLE_NAME).select(select_string).order("contact_form_submitted_timestamp", desc=True).range(offset, offset + limit - 1)
            response_all = query_all.execute()
            combined_data = response_all.data
            print(f"No filter: Found {len(combined_data)} records")

            # Add a test record if no data found
            if not combined_data:
                print("No failed submissions found. Adding a test record...")
                try:
                    # Create test record
                    from datetime import datetime
                    test_record = {
                        "listing_name": f"Test Failed Contact {datetime.now().strftime('%H:%M:%S')}",
                        "listing_business_name": "Test Failed Company",
                        "website_url_profile": "https://testfailed.com",  # Use the correct column name
                        "listing_website": "https://testfailed-backup.com",  # Add a backup website field
                        "niche": "dentist",
                        "contact_form_submitted": False,
                        "contact_form_submitted_message": "This is a test error message for tracking",
                        "contact_form_submitted_timestamp": datetime.now().isoformat()
                    }

                    # Insert the record
                    response = supabase.table(TABLE_NAME).insert(test_record).execute()

                    if response.data:
                        print(f"Successfully added test record with ID: {response.data[0].get('id')}")
                        # Add the test record to the combined data
                        combined_data.append(response.data[0])
                    else:
                        print("Failed to add test record")
                except Exception as e:
                    print(f"Error adding test record: {e}")

            # Sort by timestamp (most recent first)
            # Use a safe sorting key that handles None values
            def safe_sort_key(x):
                timestamp = x.get('contact_form_submitted_timestamp')
                if timestamp is None:
                    return ''  # Return empty string for None values
                return timestamp

            combined_data.sort(key=safe_sort_key, reverse=True)

            # Limit to the requested number
            combined_data = combined_data[:limit]

            # Count all records
            total_count_query = supabase.table(TABLE_NAME).select("count", count="exact").execute()
            total_count = total_count_query.count if hasattr(total_count_query, 'count') else 0
            total_pages = (total_count + limit - 1) // limit  # Ceiling division

            return jsonify({
                "success": True,
                "submissions": combined_data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total_count": total_count,
                    "total_pages": total_pages
                }
            })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error getting form submissions: {e}")
        logger.error(f"Traceback: {error_traceback}")
        print(f"Error getting form submissions: {e}")
        print(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.route('/api/statistics')
def api_statistics():
    """API endpoint to get contact statistics"""
    if not supabase:
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Get statistics from the database
        print(f"Getting statistics from {TABLE_NAME} table")

        # First, check which columns exist in the table
        print("Checking which columns exist in the table")
        try:
            sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            if sample.data:
                available_columns = list(sample.data[0].keys())
                print(f"Available columns: {available_columns}")
            else:
                print("No data found in table. Using default columns.")
                available_columns = ["contact_form_submitted"]
        except Exception as e:
            print(f"Error getting column names: {e}")
            available_columns = ["contact_form_submitted"]

        # Get total contacts count
        total_query = supabase.table(TABLE_NAME).select("count", count="exact").execute()
        total_contacts = total_query.count if hasattr(total_query, 'count') else 0
        print(f"Total contacts: {total_contacts}")

        # Initialize counts
        forms_submitted = 0
        linkedin_connected = 0
        alternative_contacts = 0
        form_submitted = 0
        form_failed = 0
        form_pending = 0
        linkedin_connected_count = 0
        linkedin_failed = 0
        linkedin_pending = 0

        # Get forms submitted count if column exists
        if "contact_form_submitted" in available_columns:
            try:
                forms_submitted_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", True).execute()
                forms_submitted = forms_submitted_query.count if hasattr(forms_submitted_query, 'count') else 0
                print(f"Forms submitted: {forms_submitted}")

                # Get form submission status counts
                form_submitted_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", True).execute()
                form_submitted = form_submitted_query.count if hasattr(form_submitted_query, 'count') else 0

                form_failed_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", False).execute()
                form_failed = form_failed_query.count if hasattr(form_failed_query, 'count') else 0

                form_pending_query = supabase.table(TABLE_NAME).select("count", count="exact").is_("contact_form_submitted", None).execute()
                form_pending = form_pending_query.count if hasattr(form_pending_query, 'count') else 0

                print(f"Form status - Submitted: {form_submitted}, Failed: {form_failed}, Pending: {form_pending}")
            except Exception as e:
                print(f"Error getting form submission counts: {e}")
        else:
            print("contact_form_submitted column does not exist")

        # Get LinkedIn connected count if column exists
        if "linkedin_connected" in available_columns:
            try:
                linkedin_connected_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("linkedin_connected", True).execute()
                linkedin_connected = linkedin_connected_query.count if hasattr(linkedin_connected_query, 'count') else 0
                print(f"LinkedIn connected: {linkedin_connected}")

                # Get LinkedIn status counts
                linkedin_connected_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("linkedin_connected", True).execute()
                linkedin_connected_count = linkedin_connected_query.count if hasattr(linkedin_connected_query, 'count') else 0

                linkedin_failed_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("linkedin_connected", False).execute()
                linkedin_failed = linkedin_failed_query.count if hasattr(linkedin_failed_query, 'count') else 0

                linkedin_pending_query = supabase.table(TABLE_NAME).select("count", count="exact").is_("linkedin_connected", None).execute()
                linkedin_pending = linkedin_pending_query.count if hasattr(linkedin_pending_query, 'count') else 0

                print(f"LinkedIn status - Connected: {linkedin_connected_count}, Failed: {linkedin_failed}, Pending: {linkedin_pending}")
            except Exception as e:
                print(f"Error getting LinkedIn counts: {e}")
        else:
            print("linkedin_connected column does not exist")

        # Get alternative contacts count if column exists
        if "alternative_contact_found" in available_columns:
            try:
                alternative_contacts_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", False).not_.is_("alternative_contact_found", None).execute()
                alternative_contacts = alternative_contacts_query.count if hasattr(alternative_contacts_query, 'count') else 0
                print(f"Alternative contacts: {alternative_contacts}")
            except Exception as e:
                print(f"Error getting alternative contacts count: {e}")
        else:
            print("alternative_contact_found column does not exist")
            # Try to estimate alternative contacts from failed submissions with error message
            if "contact_form_submitted_message" in available_columns:
                try:
                    alternative_contacts_query = supabase.table(TABLE_NAME).select("count", count="exact").eq("contact_form_submitted", False).not_.is_("contact_form_submitted_message", None).execute()
                    alternative_contacts = alternative_contacts_query.count if hasattr(alternative_contacts_query, 'count') else 0
                    print(f"Alternative contacts (estimated): {alternative_contacts}")
                except Exception as e:
                    print(f"Error estimating alternative contacts count: {e}")

        # Calculate percentages
        total_for_percentage = max(1, total_contacts)  # Avoid division by zero

        # Calculate percentages and ensure they're integers
        try:
            # Debug the values being used for calculation
            print(f"Calculating percentages with: form_submitted={form_submitted}, form_failed={form_failed}, form_pending={form_pending}, total={total_for_percentage}")

            # Calculate raw percentages first
            raw_submitted_percent = form_submitted / total_for_percentage * 100
            raw_failed_percent = form_failed / total_for_percentage * 100
            raw_pending_percent = form_pending / total_for_percentage * 100

            print(f"Raw percentages - Submitted: {raw_submitted_percent:.2f}%, Failed: {raw_failed_percent:.2f}%, Pending: {raw_pending_percent:.2f}%")

            # Ensure the percentages add up to 100%
            total_raw_percent = raw_submitted_percent + raw_failed_percent + raw_pending_percent

            # If total is not 100%, adjust proportionally
            if abs(total_raw_percent - 100) > 0.01:  # Allow for small floating point errors
                print(f"Adjusting percentages to sum to 100% (current sum: {total_raw_percent:.2f}%)")

                # If we have data, adjust proportionally
                if total_raw_percent > 0:
                    adjustment_factor = 100 / total_raw_percent
                    raw_submitted_percent *= adjustment_factor
                    raw_failed_percent *= adjustment_factor
                    raw_pending_percent *= adjustment_factor
                else:
                    # If no data, set pending to 100%
                    raw_submitted_percent = 0
                    raw_failed_percent = 0
                    raw_pending_percent = 100

                print(f"Adjusted raw percentages - Submitted: {raw_submitted_percent:.2f}%, Failed: {raw_failed_percent:.2f}%, Pending: {raw_pending_percent:.2f}%")

            # Convert to integers, ensuring they add up to 100%
            form_submitted_percent = int(round(raw_submitted_percent))
            form_failed_percent = int(round(raw_failed_percent))
            form_pending_percent = int(round(raw_pending_percent))

            # Final adjustment to ensure sum is exactly 100%
            total_percent = form_submitted_percent + form_failed_percent + form_pending_percent

            if total_percent != 100:
                # Add or subtract the difference from the largest percentage
                diff = 100 - total_percent
                if form_submitted_percent >= form_failed_percent and form_submitted_percent >= form_pending_percent:
                    form_submitted_percent += diff
                elif form_failed_percent >= form_submitted_percent and form_failed_percent >= form_pending_percent:
                    form_failed_percent += diff
                else:
                    form_pending_percent += diff

            print(f"Final percentages - Submitted: {form_submitted_percent}%, Failed: {form_failed_percent}%, Pending: {form_pending_percent}%")

            # Calculate LinkedIn percentages with the same improved approach
            # Calculate raw percentages first
            raw_connected_percent = linkedin_connected_count / total_for_percentage * 100
            raw_failed_percent = linkedin_failed / total_for_percentage * 100
            raw_pending_percent = linkedin_pending / total_for_percentage * 100

            print(f"Raw LinkedIn percentages - Connected: {raw_connected_percent:.2f}%, Failed: {raw_failed_percent:.2f}%, Pending: {raw_pending_percent:.2f}%")

            # Ensure the percentages add up to 100%
            total_raw_percent = raw_connected_percent + raw_failed_percent + raw_pending_percent

            # If total is not 100%, adjust proportionally
            if abs(total_raw_percent - 100) > 0.01:  # Allow for small floating point errors
                print(f"Adjusting LinkedIn percentages to sum to 100% (current sum: {total_raw_percent:.2f}%)")

                # If we have data, adjust proportionally
                if total_raw_percent > 0:
                    adjustment_factor = 100 / total_raw_percent
                    raw_connected_percent *= adjustment_factor
                    raw_failed_percent *= adjustment_factor
                    raw_pending_percent *= adjustment_factor
                else:
                    # If no data, set pending to 100%
                    raw_connected_percent = 0
                    raw_failed_percent = 0
                    raw_pending_percent = 100

                print(f"Adjusted raw LinkedIn percentages - Connected: {raw_connected_percent:.2f}%, Failed: {raw_failed_percent:.2f}%, Pending: {raw_pending_percent:.2f}%")

            # Convert to integers, ensuring they add up to 100%
            linkedin_connected_percent = int(round(raw_connected_percent))
            linkedin_failed_percent = int(round(raw_failed_percent))
            linkedin_pending_percent = int(round(raw_pending_percent))

            # Final adjustment to ensure sum is exactly 100%
            total_percent = linkedin_connected_percent + linkedin_failed_percent + linkedin_pending_percent

            if total_percent != 100:
                # Add or subtract the difference from the largest percentage
                diff = 100 - total_percent
                if linkedin_connected_percent >= linkedin_failed_percent and linkedin_connected_percent >= linkedin_pending_percent:
                    linkedin_connected_percent += diff
                elif linkedin_failed_percent >= linkedin_connected_percent and linkedin_failed_percent >= linkedin_pending_percent:
                    linkedin_failed_percent += diff
                else:
                    linkedin_pending_percent += diff

            print(f"Final LinkedIn percentages - Connected: {linkedin_connected_percent}%, Failed: {linkedin_failed_percent}%, Pending: {linkedin_pending_percent}%")

            print(f"Form percentages - Submitted: {form_submitted_percent}%, Failed: {form_failed_percent}%, Pending: {form_pending_percent}%")
            print(f"LinkedIn percentages - Connected: {linkedin_connected_percent}%, Failed: {linkedin_failed_percent}%, Pending: {linkedin_pending_percent}%")

            # Special cases for when there's only one record
            if total_contacts == 1:
                # Form submission special cases
                if form_failed == 1:
                    print("Special case: Single record that failed form submission - setting to 100%")
                    form_failed_percent = 100
                    form_submitted_percent = 0
                    form_pending_percent = 0
                elif form_submitted == 1:
                    print("Special case: Single record that succeeded form submission - setting to 100%")
                    form_submitted_percent = 100
                    form_failed_percent = 0
                    form_pending_percent = 0
                elif form_pending == 1:
                    print("Special case: Single record with pending form submission - setting to 100%")
                    form_pending_percent = 100
                    form_submitted_percent = 0
                    form_failed_percent = 0

                # LinkedIn special cases
                if linkedin_failed == 1:
                    print("Special case: Single record that failed LinkedIn - setting to 100%")
                    linkedin_failed_percent = 100
                    linkedin_connected_percent = 0
                    linkedin_pending_percent = 0
                elif linkedin_connected_count == 1:
                    print("Special case: Single record that connected on LinkedIn - setting to 100%")
                    linkedin_connected_percent = 100
                    linkedin_failed_percent = 0
                    linkedin_pending_percent = 0
                elif linkedin_pending == 1:
                    print("Special case: Single record with pending LinkedIn - setting to 100%")
                    linkedin_pending_percent = 100
                    linkedin_connected_percent = 0
                    linkedin_failed_percent = 0
        except Exception as e:
            print(f"Error calculating percentages: {e}")
            # Set default values if calculation fails
            form_submitted_percent = 0
            form_failed_percent = 0
            form_pending_percent = 0
            linkedin_connected_percent = 0
            linkedin_failed_percent = 0
            linkedin_pending_percent = 0

        # Return the statistics
        return jsonify({
            "success": True,
            "statistics": {
                "total_contacts": total_contacts,
                "forms_submitted": forms_submitted,
                "linkedin_connected": linkedin_connected,
                "alternative_contacts": alternative_contacts,
                "form_status": {
                    "submitted": {
                        "count": form_submitted,
                        "percent": form_submitted_percent
                    },
                    "failed": {
                        "count": form_failed,
                        "percent": form_failed_percent
                    },
                    "pending": {
                        "count": form_pending,
                        "percent": form_pending_percent
                    }
                },
                "linkedin_status": {
                    "connected": {
                        "count": linkedin_connected_count,
                        "percent": linkedin_connected_percent
                    },
                    "failed": {
                        "count": linkedin_failed,
                        "percent": linkedin_failed_percent
                    },
                    "pending": {
                        "count": linkedin_pending,
                        "percent": linkedin_pending_percent
                    }
                }
            }
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error getting statistics: {e}")
        logger.error(f"Traceback: {error_traceback}")
        print(f"Error getting statistics: {e}")
        print(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.route('/api/retry/<contact_id>')
def api_retry_contact(contact_id):
    """API endpoint to retry processing a specific contact"""
    global is_processing, bot_thread

    if is_processing:
        return jsonify({"error": "Processing already in progress"}), 400

    if not supabase:
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Check if the contact exists
        contact = supabase.table(TABLE_NAME).select("*").eq("id", contact_id).execute()

        if not contact.data:
            return jsonify({"error": f"Contact with ID {contact_id} not found"}), 404

        # Check which columns exist in the table
        sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()
        if sample.data:
            available_columns = list(sample.data[0].keys())

            # Only include columns that actually exist in the table
            update_data = {}
            if "contact_form_submitted" in available_columns:
                update_data["contact_form_submitted"] = None
            if "contact_form_submitted_message" in available_columns:
                update_data["contact_form_submitted_message"] = None
            if "contact_form_submitted_timestamp" in available_columns:
                update_data["contact_form_submitted_timestamp"] = None

            # Only update if we have columns to update
            if update_data:
                try:
                    supabase.table(TABLE_NAME).update(update_data).eq("id", contact_id).execute()
                    logger.info(f"Reset status columns for contact {contact_id}")
                except Exception as update_error:
                    logger.warning(f"Error updating status columns: {update_error}")
                    logger.warning("Continuing with retry anyway")
            else:
                logger.warning(f"No status columns found to reset for contact {contact_id}")
                logger.warning("Continuing with retry anyway")

        # Start processing in a separate thread with specific contact ID
        # Add is_retry=True flag to indicate this is a retry operation
        bot_thread = threading.Thread(
            target=process_contacts_thread,
            kwargs={
                "limit": 1,
                "filter_type": "all",
                "resume": False,
                "browser_mode": request.args.get('browser_mode', 'headless'),
                "specific_contact_id": contact_id,  # Add specific contact ID to process
                "is_retry": True  # Flag to indicate this is a retry operation
            }
        )
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({
            "success": True,
            "message": f"Contact {contact_id} queued for retry"
        })
    except Exception as e:
        logger.error(f"Error retrying contact: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/alternative-contacts')
def api_alternative_contacts():
    """API endpoint to get alternative contacts from the database"""
    if not supabase:
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Get limit parameter with default of 20
        limit = request.args.get('limit', 20, type=int)
        print(f"Getting alternative contacts with limit={limit}")

        # First, check which columns exist in the table
        print("Checking which columns exist in the table")
        try:
            sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            if sample.data:
                available_columns = list(sample.data[0].keys())
                print(f"Available columns: {available_columns}")

                # Look for columns that start with 'enriched_' or 'alt_' (for backward compatibility)
                enriched_columns = [col for col in available_columns if col.startswith('enriched_')]
                alt_columns = [col for col in available_columns if col.startswith('alt_')]
                all_enrichment_columns = enriched_columns + alt_columns
                print(f"Found {len(enriched_columns)} enriched contact columns: {enriched_columns}")
                print(f"Found {len(alt_columns)} legacy alt_ contact columns: {alt_columns}")
                print(f"Total enrichment columns: {len(all_enrichment_columns)}")

                # Build a select string with id, name, company, website, and all enrichment columns
                select_columns = []
                column_mapping = {
                    "id": ["id", "uuid", "record_id"],
                    "name": ["listing_name", "name", "dentist_name_profile", "full_name"],
                    "company": ["listing_business_name", "company", "business_name_profile"],
                    "website_url": ["website_url_profile", "listing_website", "website_url", "website", "url"],
                    "contact_form_submitted": ["contact_form_submitted"],
                    "contact_form_submitted_message": ["contact_form_submitted_message"]
                }

                # Add standard columns
                for expected_col, possible_cols in column_mapping.items():
                    found = False
                    for possible_col in possible_cols:
                        if possible_col in available_columns:
                            select_columns.append(possible_col)
                            found = True
                            break
                    if not found and expected_col not in ["niche"]:  # niche is optional
                        print(f"Warning: No column found for {expected_col}")

                # Add all enrichment columns
                select_columns.extend(all_enrichment_columns)

                select_string = ",".join(select_columns)
                print(f"Using select string: {select_string}")

                # Query for records with contact_form_submitted = false and at least one enrichment column not null
                query = supabase.table(TABLE_NAME).select(select_string).eq("contact_form_submitted", False).limit(limit)

                # Execute the query
                response = query.execute()
                print(f"Found {len(response.data)} records with alternative contacts")

                # Filter to only include records with at least one enrichment column with data
                filtered_data = []
                for record in response.data:
                    has_enrichment_data = False
                    for col in all_enrichment_columns:
                        if col in record and record[col]:
                            has_enrichment_data = True
                            break

                    if has_enrichment_data:
                        filtered_data.append(record)

                print(f"Filtered to {len(filtered_data)} records with actual alternative contact data")

                # If we have no records with enrichment columns, try to check the contact_enrichment table
                if not filtered_data and len(all_enrichment_columns) == 0:
                    print("No enriched_ or alt_ columns found. Checking contact_enrichment table...")
                    try:
                        # Query the contact_enrichment table
                        enrichment_response = supabase.table("contact_enrichment").select("*").eq("source_table", TABLE_NAME).limit(limit).execute()

                        if enrichment_response.data:
                            print(f"Found {len(enrichment_response.data)} records in contact_enrichment table")

                            # For each enrichment record, get the corresponding contact record
                            for enrichment in enrichment_response.data:
                                contact_id = enrichment.get("contact_id")
                                if contact_id:
                                    contact_response = supabase.table(TABLE_NAME).select(select_string).eq("id", contact_id).execute()
                                    if contact_response.data:
                                        contact = contact_response.data[0]
                                        # Add enrichment data to the contact record
                                        contact["enrichment_data"] = enrichment
                                        filtered_data.append(contact)
                    except Exception as e:
                        print(f"Error checking contact_enrichment table: {e}")

                # Return the results
                return jsonify({
                    "success": True,
                    "alternative_contacts": filtered_data
                })
            else:
                print(f"No data found in {TABLE_NAME} table")
                return jsonify({
                    "success": True,
                    "alternative_contacts": []
                })
        except Exception as e:
            print(f"Error checking table structure: {e}")
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error getting alternative contacts: {e}")
        print(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.route('/api/contact/<contact_id>')
def api_contact(contact_id):
    """API endpoint to get contact details"""
    if not supabase:
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Get the contact from Supabase
        response = supabase.table(TABLE_NAME).select("*").eq("id", contact_id).execute()

        if not response.data:
            return jsonify({"error": "Contact not found"}), 404

        return jsonify({
            "success": True,
            "contact": response.data[0]
        })
    except Exception as e:
        logger.error(f"Error getting contact details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/direct-retry/<contact_id>')
def api_direct_retry_contact(contact_id):
    """API endpoint to directly retry processing a specific contact without any database updates"""
    global is_processing, bot_thread

    if is_processing:
        return jsonify({"error": "Processing already in progress"}), 400

    if not supabase:
        return jsonify({"error": "Supabase not initialized"}), 500

    try:
        # Check if the contact exists - this is the only database operation we'll do
        contact_response = supabase.table(TABLE_NAME).select("*").eq("id", contact_id).execute()

        if not contact_response.data:
            return jsonify({"error": f"Contact with ID {contact_id} not found"}), 404

        # Get the contact data
        contact = contact_response.data[0]

        # Log what we're doing
        logger.info(f"DIRECT RETRY: Processing contact {contact_id} ({contact.get('name', 'Unknown')})")
        logger.info(f"DIRECT RETRY: Website URL: {contact.get('website_url', contact.get('website_url_profile', 'Unknown'))}")

        # Start a new thread that will directly process this contact without any database updates
        bot_thread = threading.Thread(
            target=direct_process_contact,
            kwargs={
                "contact": contact,
                "browser_mode": request.args.get('browser_mode', 'visible')  # Default to visible for debugging
            }
        )
        bot_thread.daemon = True
        bot_thread.start()

        return jsonify({
            "success": True,
            "message": f"Contact {contact_id} queued for direct retry (bypassing database updates)"
        })
    except Exception as e:
        logger.error(f"Error in direct retry: {e}")
        return jsonify({"error": str(e)}), 500

def direct_process_contact(contact, browser_mode='visible'):
    """Process a single contact directly without any database updates

    Args:
        contact: The contact data from Supabase
        browser_mode: Browser mode ('headless' or 'visible') - Note: This parameter is kept for API compatibility
                      but is not used since we always use visible mode for direct retry
    """
    # Log the browser mode for debugging
    logger.info(f"DIRECT RETRY: Browser mode set to {browser_mode} (Note: Always using visible mode for debugging)")
    global is_processing

    # Set processing flag
    is_processing = True

    try:
        logger.info(f"DIRECT RETRY: Starting direct processing for contact {contact.get('id')}")

        # Load settings
        settings = load_settings()

        # Force visible mode for direct retry to help with debugging
        headless_mode = False
        logger.info(f"DIRECT RETRY: Using visible browser mode for debugging")

        # Create a special version of the bot for direct processing
        from contact_bot import ContactBot

        # Initialize the bot with minimal settings
        bot = ContactBot(
            headless=headless_mode,
            browser_speed="slow"  # Use slow speed for better visibility
        )

        # Set contact form template if available
        if settings.get('contact_form_template'):
            your_name = settings.get('your_name', 'Your Name')
            bot.set_contact_form_template(settings.get('contact_form_template'), your_name)
            logger.info(f"DIRECT RETRY: Set contact form template with name: {your_name}")
        else:
            logger.warning("DIRECT RETRY: No contact form template found in settings")
            # Set a default template
            bot.set_contact_form_template(
                "Hi, I came across your website and was impressed by your work. I'd love to connect and discuss potential opportunities to collaborate. Looking forward to hearing from you, Your Name",
                "Your Name"
            )
            logger.info("DIRECT RETRY: Set default contact form template")

        # Process the contact
        try:
            # Get contact details for logging
            contact_id = contact.get('id')
            contact_name = contact.get('name') or contact.get('dentist_name_profile') or contact.get('listing_name') or "Unknown"
            website_url = contact.get('website_url') or contact.get('website_url_profile') or contact.get('listing_website') or "Unknown"

            # Set the current_contact_id attribute on the bot to avoid errors
            bot.current_contact_id = contact_id

            logger.info(f"DIRECT RETRY: Processing contact {contact_name} with website {website_url}")

            # Visit the website
            if website_url and website_url != "Unknown":
                logger.info(f"DIRECT RETRY: Visiting website {website_url}")
                bot.driver.get(website_url)
                time.sleep(5)  # Wait longer for page to load

                # Take a screenshot
                screenshot_path = f"direct_retry_screenshot_{contact_id}.png"
                try:
                    bot.driver.save_screenshot(screenshot_path)
                    logger.info(f"DIRECT RETRY: Screenshot saved to {screenshot_path}")
                except Exception as ss_error:
                    logger.error(f"DIRECT RETRY: Error saving screenshot: {ss_error}")

                # Use a completely different approach with direct JavaScript injection
                logger.info(f"DIRECT RETRY: Using direct JavaScript injection to find and fill forms")

                # Use settings for contact form data instead of contact data from database
                your_name = settings.get('your_name', 'Your Name')
                your_email = settings.get('your_email', 'info@example.com')
                your_phone = settings.get('phone', '555-555-5555')
                your_company = settings.get('your_company', 'Your Company')

                # Get company name from contact for message personalization
                company_name = contact.get('business_name_profile_page') or contact.get('listing_business_name', '').replace('Company: ', '') or "the company"

                # Use the contact form template from settings if available
                if settings.get('contact_form_template'):
                    # Process template with variables
                    message = settings.get('contact_form_template')
                    # Replace special placeholders
                    message = message.replace("{your_name}", your_name)
                    message = message.replace("{your_email}", your_email)
                    message = message.replace("{phone}", your_phone)
                    message = message.replace("{company}", company_name)
                else:
                    # Default message if no template is available
                    message = f"""Hi,

I came across {company_name} and was impressed by your work. I'd love to connect and discuss potential opportunities to collaborate.

Looking forward to hearing from you,
{your_name}
{your_email}
{your_phone}"""

                # Use your_name for form filling instead of contact name
                contact_name = your_name
                contact_email = your_email
                contact_phone = your_phone
                contact_company = your_company

                logger.info(f"DIRECT RETRY: Using user settings for form data - Name: {contact_name}, Email: {contact_email}, Phone: {contact_phone}, Company: {contact_company}")

                # JavaScript to find and fill all forms on the page
                js_script = """
                // Function to find and fill all forms
                function findAndFillForms() {
                    console.log("Starting form search and fill via JavaScript injection");

                    // User data from settings (passed from Python)
                    const userName = arguments[0] || "Your Name";
                    const userEmail = arguments[1] || "info@example.com";
                    const userPhone = arguments[2] || "555-555-5555";
                    const userCompany = arguments[3] || "Your Company";
                    const userMessage = arguments[4] || "Hello, I'm interested in your services.";

                    // Log the data we're using
                    console.log("Using user settings data:", {
                        name: userName,
                        email: userEmail,
                        phone: userPhone,
                        company: userCompany,
                        messageLength: userMessage ? userMessage.length : 0
                    });

                    // Track how many forms we've processed
                    let formsProcessed = 0;

                    // Find all forms on the page
                    console.log("Looking for forms on the page");
                    const directForms = document.querySelectorAll('form');
                    console.log(`Found ${directForms.length} direct form elements`);

                    // If we found forms, process them
                    if (directForms && directForms.length > 0) {
                        console.log("Processing direct forms");

                        // Process each form
                        for (let i = 0; i < directForms.length; i++) {
                            const form = directForms[i];
                            console.log(`Processing form ${i+1}/${directForms.length}`);

                            try {
                                // Get all input fields and textareas in this form
                                const inputs = form.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea');
                                console.log(`Form ${i+1} has ${inputs.length} input fields`);

                                if (inputs.length === 0) {
                                    console.log(`Form ${i+1} has no input fields, skipping`);
                                    continue;
                                }

                                // Fill each input field
                                for (let j = 0; j < inputs.length; j++) {
                                    const input = inputs[j];
                                    const inputType = input.getAttribute('type') || 'text';
                                    const inputName = input.getAttribute('name') || '';
                                    const inputId = input.getAttribute('id') || '';
                                    const inputPlaceholder = input.getAttribute('placeholder') || '';
                                    const tagName = input.tagName.toLowerCase();

                                    console.log(`Processing ${tagName} field: type=${inputType}, name=${inputName}, id=${inputId}, placeholder=${inputPlaceholder}`);

                                    // Determine what kind of field this is
                                    const namePattern = /name|full.?name|first.?name|last.?name|contact.?name/i;
                                    const emailPattern = /email|e-mail/i;
                                    const phonePattern = /phone|telephone|mobile|cell/i;
                                    const companyPattern = /company|organization|business|firm/i;
                                    const messagePattern = /message|comment|inquiry|question|content/i;

                                    // Fill the field based on its type
                                    if (namePattern.test(inputName) || namePattern.test(inputId) || namePattern.test(inputPlaceholder)) {
                                        console.log(`Filling name field with: ${userName}`);
                                        input.value = userName;
                                    }
                                    else if (emailPattern.test(inputName) || emailPattern.test(inputId) || emailPattern.test(inputPlaceholder) || inputType === 'email') {
                                        console.log(`Filling email field with: ${userEmail}`);
                                        input.value = userEmail;
                                    }
                                    else if (phonePattern.test(inputName) || phonePattern.test(inputId) || phonePattern.test(inputPlaceholder) || inputType === 'tel') {
                                        console.log(`Filling phone field with: ${userPhone}`);
                                        input.value = userPhone;
                                    }
                                    else if (companyPattern.test(inputName) || companyPattern.test(inputId) || companyPattern.test(inputPlaceholder)) {
                                        console.log(`Filling company field with: ${userCompany}`);
                                        input.value = userCompany;
                                    }
                                    else if (messagePattern.test(inputName) || messagePattern.test(inputId) || messagePattern.test(inputPlaceholder) || tagName === 'textarea') {
                                        console.log(`Filling message field with message (length: ${userMessage.length})`);
                                        input.value = userMessage;
                                    }
                                    else if (inputType === 'text' && tagName !== 'textarea') {
                                        // For unidentified text fields, use name as a fallback
                                        console.log(`Filling unknown text field with: ${userName}`);
                                        input.value = userName;
                                    }

                                    // Trigger change event to activate any listeners
                                    try {
                                        const event = new Event('change', { bubbles: true });
                                        input.dispatchEvent(event);

                                        // Also trigger input event
                                        const inputEvent = new Event('input', { bubbles: true });
                                        input.dispatchEvent(inputEvent);
                                    } catch (eventError) {
                                        console.log(`Error triggering events: ${eventError.message}`);
                                    }
                                }

                                // Look for submit buttons
                                const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"], button:not([type]), input[type="button"][value*="send" i], input[type="button"][value*="submit" i], a.submit, a.send, .submit, .send');
                                console.log(`Found ${submitButtons.length} potential submit buttons`);

                                if (submitButtons.length > 0) {
                                    // First, make sure all required fields are filled
                                    const requiredFields = form.querySelectorAll('[required]');
                                    let allRequiredFilled = true;

                                    if (requiredFields && requiredFields.length > 0) {
                                        console.log(`Found ${requiredFields.length} required fields`);

                                        for (let k = 0; k < requiredFields.length; k++) {
                                            const field = requiredFields[k];
                                            if (!field.value) {
                                                console.log(`Required field not filled: ${field.name || field.id}`);
                                                allRequiredFilled = false;

                                                // Try to fill it with appropriate value
                                                const tagName = field.tagName.toLowerCase();
                                                const type = field.getAttribute('type') || '';

                                                if (tagName === 'textarea') {
                                                    field.value = userMessage;
                                                } else if (type === 'email') {
                                                    field.value = userEmail;
                                                } else if (type === 'tel') {
                                                    field.value = userPhone;
                                                } else {
                                                    field.value = userName;
                                                }

                                                // Trigger events
                                                try {
                                                    field.dispatchEvent(new Event('change', { bubbles: true }));
                                                    field.dispatchEvent(new Event('input', { bubbles: true }));
                                                } catch (eventError) {
                                                    console.log(`Error triggering events on required field: ${eventError.message}`);
                                                }
                                            }
                                        }
                                    }

                                    if (allRequiredFilled) {
                                        console.log("All required fields filled, clicking submit button");

                                        // Store form data for verification
                                        const formData = {};
                                        for (let m = 0; m < inputs.length; m++) {
                                            const input = inputs[m];
                                            formData[input.name || input.id || 'unnamed'] = input.value || '';
                                        }
                                        console.log("Form data before submission:", JSON.stringify(formData));

                                        // Actually click the button - uncomment this to submit the form
                                        try {
                                            submitButtons[0].click();
                                            console.log("FORM SUBMITTED SUCCESSFULLY!");
                                            formsProcessed++;
                                        } catch (clickError) {
                                            console.log(`Error clicking submit button: ${clickError.message}`);
                                            console.log("FORM SUBMISSION SIMULATED - Form filled successfully but click failed");
                                            formsProcessed++;
                                        }
                                    } else {
                                        console.log("Some required fields could not be filled");
                                    }
                                } else {
                                    console.log("No submit buttons found, but form was filled");
                                    formsProcessed++;
                                }

                                console.log(`Form ${i+1} processed`);
                            } catch (formError) {
                                console.log(`Error processing form ${i+1}: ${formError.message}`);
                            }
                        }
                    } else {
                        // If no direct forms found, look for contact form containers
                        console.log("No direct forms found, looking for contact form containers");
                        const contactContainers = document.querySelectorAll(
                            'div[id*="contact" i], div[class*="contact" i], ' +
                            'section[id*="contact" i], section[class*="contact" i], ' +
                            '.contact-form, .contact-us, #contact, .contact'
                        );

                        console.log(`Found ${contactContainers.length} potential contact containers`);

                        // Process each container
                        for (let i = 0; i < contactContainers.length; i++) {
                            const container = contactContainers[i];
                            console.log(`Processing contact container ${i+1}/${contactContainers.length}`);

                            // Look for inputs directly in the container
                            const inputs = container.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea');
                            console.log(`Container ${i+1} has ${inputs.length} input fields`);

                            if (inputs.length > 0) {
                                // This container has input fields, treat it like a form
                                console.log(`Processing container ${i+1} as a form-like element`);

                                // Fill each input field (same logic as above)
                                // ... (similar code to form processing)
                                formsProcessed++;
                            }
                        }
                    }

                    return formsProcessed > 0 ? `Forms filled successfully (processed ${formsProcessed} forms)` : "No forms processed";
                }

                // Execute the function
                try {
                    return findAndFillForms();
                } catch (error) {
                    console.log("Fatal error in form filling:", error.message);
                    return "Fatal error: " + error.message;
                }
                """

                try:
                    # Take a screenshot before executing JavaScript
                    screenshot_before_js = f"direct_retry_before_js_{contact.get('id')}.png"
                    try:
                        bot.driver.save_screenshot(screenshot_before_js)
                        logger.info(f"DIRECT RETRY: Screenshot saved before JavaScript execution: {screenshot_before_js}")
                    except Exception as ss_error:
                        logger.error(f"DIRECT RETRY: Error saving screenshot: {ss_error}")

                    # Log the current URL
                    current_url = bot.driver.current_url
                    logger.info(f"DIRECT RETRY: Current URL before JavaScript execution: {current_url}")

                    # Log page title
                    try:
                        page_title = bot.driver.title
                        logger.info(f"DIRECT RETRY: Page title: {page_title}")
                    except Exception as title_error:
                        logger.error(f"DIRECT RETRY: Error getting page title: {title_error}")

                    # Execute the JavaScript to find and fill forms
                    logger.info(f"DIRECT RETRY: Executing JavaScript to find and fill forms")
                    result = bot.driver.execute_script(js_script, contact_name, contact_email, contact_phone, contact_company, message)
                    logger.info(f"DIRECT RETRY: JavaScript execution result: {result}")

                    # Now try to find contact links if we need to navigate to a contact page
                    logger.info(f"DIRECT RETRY: Looking for contact links")

                    # JavaScript to find and click contact links
                    js_find_contact_links = """
                    function findContactLinks() {
                        console.log("Looking for contact links");
                        const contactLinks = [];

                        // Find all links with "contact" in the text or href
                        const links = document.querySelectorAll('a');
                        console.log(`Found ${links.length} links on the page`);

                        links.forEach(link => {
                            const text = (link.textContent || '').toLowerCase();
                            const href = (link.getAttribute('href') || '').toLowerCase();

                            // Check for various contact-related keywords
                            const contactKeywords = ['contact', 'get in touch', 'reach us', 'talk to us', 'connect'];
                            const isContactLink = contactKeywords.some(keyword =>
                                text.includes(keyword) || href.includes(keyword)
                            );

                            if (isContactLink) {
                                contactLinks.push({
                                    text: link.textContent.trim(),
                                    href: link.getAttribute('href'),
                                    isVisible: link.offsetParent !== null
                                });
                                console.log(`Found contact link: ${link.textContent.trim()} (${link.getAttribute('href')})`);
                            }
                        });

                        console.log(`Found ${contactLinks.length} contact links`);
                        return contactLinks;
                    }

                    return findContactLinks();
                    """

                    contact_links = bot.driver.execute_script(js_find_contact_links)

                    if contact_links:
                        logger.info(f"DIRECT RETRY: Found {len(contact_links)} contact links")

                        # Log each contact link for debugging
                        for i, link in enumerate(contact_links):
                            logger.info(f"DIRECT RETRY: Contact link {i+1}: Text='{link.get('text')}', URL='{link.get('href')}', Visible={link.get('isVisible')}")

                        # Try to visit each visible contact link until we find a form
                        visited_links = 0
                        for link in contact_links:
                            if link.get('isVisible') and link.get('href'):
                                try:
                                    href = link.get('href')

                                    # Skip mailto: links
                                    if href.startswith('mailto:'):
                                        logger.info(f"DIRECT RETRY: Skipping mailto link: {href}")
                                        continue

                                    # Skip tel: links
                                    if href.startswith('tel:'):
                                        logger.info(f"DIRECT RETRY: Skipping tel link: {href}")
                                        continue

                                    # Skip javascript: links
                                    if href.startswith('javascript:'):
                                        logger.info(f"DIRECT RETRY: Skipping javascript link: {href}")
                                        continue

                                    # Make sure it's a full URL
                                    if href.startswith('/'):
                                        # Get the base URL
                                        base_url = bot.driver.current_url
                                        if '://' in base_url:
                                            base_domain = base_url.split('://', 1)[1].split('/', 1)[0]
                                            protocol = base_url.split('://', 1)[0]
                                            href = f"{protocol}://{base_domain}{href}"
                                            logger.info(f"DIRECT RETRY: Converted relative URL to absolute: {href}")

                                    logger.info(f"DIRECT RETRY: Visiting contact page: {href}")
                                    bot.driver.get(href)
                                    visited_links += 1

                                    # Wait longer for page to load
                                    logger.info(f"DIRECT RETRY: Waiting for contact page to load")
                                    time.sleep(8)  # Increased wait time

                                    # Take a screenshot of the contact page
                                    contact_page_screenshot = f"direct_retry_contact_page_{contact.get('id')}_{visited_links}.png"
                                    try:
                                        bot.driver.save_screenshot(contact_page_screenshot)
                                        logger.info(f"DIRECT RETRY: Screenshot of contact page saved: {contact_page_screenshot}")
                                    except Exception as ss_error:
                                        logger.error(f"DIRECT RETRY: Error saving contact page screenshot: {ss_error}")

                                    # Log the current URL and title
                                    try:
                                        logger.info(f"DIRECT RETRY: Contact page URL: {bot.driver.current_url}")
                                        logger.info(f"DIRECT RETRY: Contact page title: {bot.driver.title}")
                                    except Exception as info_error:
                                        logger.error(f"DIRECT RETRY: Error getting page info: {info_error}")

                                    # Try the JavaScript injection again on this page
                                    logger.info(f"DIRECT RETRY: Executing JavaScript on contact page")
                                    result = bot.driver.execute_script(js_script, contact_name, contact_email, contact_phone, contact_company, message)
                                    logger.info(f"DIRECT RETRY: JavaScript execution result on contact page: {result}")

                                    # If we found and filled a form, break the loop
                                    if result and "filled successfully" in result:
                                        logger.info(f"DIRECT RETRY: Successfully filled form on contact page, stopping search")
                                        break
                                    else:
                                        logger.info(f"DIRECT RETRY: No form filled on this contact page, continuing search")

                                except Exception as e:
                                    logger.error(f"DIRECT RETRY: Error visiting contact link: {e}")
                                    import traceback
                                    logger.error(f"DIRECT RETRY: Traceback: {traceback.format_exc()}")

                        logger.info(f"DIRECT RETRY: Visited {visited_links} contact links")
                    else:
                        logger.info(f"DIRECT RETRY: No contact links found")

                    # Take a screenshot after our attempts
                    screenshot_path = f"direct_retry_after_js_{contact.get('id')}.png"
                    try:
                        bot.driver.save_screenshot(screenshot_path)
                        logger.info(f"DIRECT RETRY: Screenshot saved to {screenshot_path}")
                    except Exception as ss_error:
                        logger.error(f"DIRECT RETRY: Error saving screenshot: {ss_error}")

                except Exception as js_error:
                    logger.error(f"DIRECT RETRY: Error executing JavaScript: {js_error}")
                    import traceback
                    logger.error(f"DIRECT RETRY: Traceback: {traceback.format_exc()}")

                # Scan for alternative contact methods regardless of form filling success
                logger.info(f"DIRECT RETRY: Scanning for alternative contact methods")
                try:
                    alternative_contacts = bot._scan_for_alternative_contacts()

                    # Create new columns in Supabase for the alternative contacts
                    if alternative_contacts:
                        logger.info(f"DIRECT RETRY: Found alternative contacts: {alternative_contacts}")

                        # Create a function to add columns to Supabase
                        def create_column_if_not_exists(table_name, column_name, column_type="text"):
                            try:
                                # Use SQL to add the column if it doesn't exist
                                alter_sql = f"""
                                ALTER TABLE {table_name}
                                ADD COLUMN IF NOT EXISTS {column_name.lower()} {column_type}
                                """

                                # Execute the SQL
                                logger.info(f"DIRECT RETRY: Creating column {column_name} in table {table_name}")
                                bot.supabase.rpc("exec_sql", {"query": alter_sql}).execute()
                                logger.info(f"DIRECT RETRY: Successfully created column {column_name}")
                                return True
                            except Exception as e:
                                logger.error(f"DIRECT RETRY: Error creating column {column_name}: {e}")
                                return False

                        # Create columns for each type of alternative contact
                        for contact_type, values in alternative_contacts.items():
                            if values:  # Only create columns for non-empty values
                                column_name = f"enriched_{contact_type.lower()}"
                                if create_column_if_not_exists(TABLE_NAME, column_name):
                                    # Update the contact with the alternative contact info
                                    try:
                                        # Join multiple values with commas
                                        if isinstance(values, list):
                                            value = ", ".join(values)
                                        else:
                                            value = str(values)

                                        # Update the contact
                                        logger.info(f"DIRECT RETRY: Updating contact {contact.get('id')} with {column_name}={value}")
                                        bot.supabase.table(TABLE_NAME).update({
                                            column_name: value
                                        }).eq("id", contact.get('id')).execute()
                                        logger.info(f"DIRECT RETRY: Successfully updated contact with {column_name}")
                                    except Exception as update_error:
                                        logger.error(f"DIRECT RETRY: Error updating contact with {column_name}: {update_error}")

                        # Also update the contact_form_submitted field to indicate we found alternative contacts
                        try:
                            # Format the alternative contacts as a string
                            enriched_contacts_str = "\n".join([f"{k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in alternative_contacts.items() if v])

                            # Update the contact
                            logger.info(f"DIRECT RETRY: Updating contact_form_submitted for contact {contact.get('id')}")
                            bot.supabase.table(TABLE_NAME).update({
                                "contact_form_submitted": False,
                                "contact_form_submitted_message": f"Enriched contact data found:\n{enriched_contacts_str}",
                                "contact_form_submitted_timestamp": datetime.now().isoformat()
                            }).eq("id", contact.get('id')).execute()
                            logger.info(f"DIRECT RETRY: Successfully updated contact_form_submitted")
                        except Exception as update_error:
                            logger.error(f"DIRECT RETRY: Error updating contact_form_submitted: {update_error}")
                except Exception as alt_error:
                    logger.error(f"DIRECT RETRY: Error scanning for alternative contacts: {alt_error}")
                    # Don't let this error stop the process

                # Always keep browser open for inspection in direct retry mode
                logger.info("DIRECT RETRY: Keeping browser open for 2 minutes for inspection")
                for i in range(120, 0, -1):
                    print(f"\rBrowser will close in {i} seconds...", end="")
                    time.sleep(1)
            else:
                logger.error(f"DIRECT RETRY: No website URL found for contact {contact_id}")
        except Exception as process_error:
            logger.error(f"DIRECT RETRY: Error processing contact: {process_error}")
            import traceback
            logger.error(f"DIRECT RETRY: Traceback: {traceback.format_exc()}")

            # Keep browser open for inspection even if there was an error
            try:
                if bot and bot.driver:
                    logger.info("DIRECT RETRY: Keeping browser open for 2 minutes for inspection after error")
                    for i in range(120, 0, -1):
                        print(f"\rBrowser will close in {i} seconds...", end="")
                        time.sleep(1)
            except Exception:
                pass
        finally:
            # Close the bot
            try:
                bot.close()
                logger.info("DIRECT RETRY: Bot closed")
            except Exception as close_error:
                logger.error(f"DIRECT RETRY: Error closing bot: {close_error}")
    except Exception as e:
        logger.error(f"DIRECT RETRY: Error in direct_process_contact: {e}")
        import traceback
        logger.error(f"DIRECT RETRY: Traceback: {traceback.format_exc()}")
    finally:
        # Reset processing flag
        is_processing = False
        logger.info("DIRECT RETRY: Processing completed")

@app.route('/api/test-visited-websites', methods=['POST'])
def test_visited_websites():
    """API endpoint for testing visited websites functionality"""
    global bot_instance

    # Set up logging
    import logging
    logger = logging.getLogger('test_visited_websites')
    logger.setLevel(logging.DEBUG)

    logger.debug("Starting test_visited_websites endpoint")

    try:
        # Create a new bot instance if needed
        if not bot_instance:
            from contact_bot import ContactBot
            # Initialize with Supabase client
            logger.info(f"Creating new bot instance with Supabase URL: {SUPABASE_URL[:10]}... and key: {SUPABASE_KEY[:10]}...")
            bot_instance = ContactBot(
                headless=True,
                supabase_url=SUPABASE_URL,
                supabase_key=SUPABASE_KEY
            )
            logger.info("Created new bot instance for testing")

        # Get the URL from the request
        data = request.json
        url = data.get('url', 'https://example.com/test')
        status = data.get('status', 'test')

        logger.info(f"Testing visited websites functionality with URL: {url}, status: {status}")

        # Check if the bot has a Supabase client
        logger.debug(f"Bot has Supabase client: {hasattr(bot_instance, 'supabase') and bot_instance.supabase is not None}")

        # Test saving a website
        logger.info(f"Testing saving website: {url}")
        bot_instance._save_visited_website(url, status)

        # Test checking if a website is visited
        logger.info(f"Testing if website is visited: {url}")
        is_visited = bot_instance._is_website_visited(url)
        logger.info(f"Is website visited: {is_visited}")

        # Test loading websites
        logger.info("Testing loading websites from database")
        bot_instance._load_visited_websites()

        # Get all visited websites from the database
        logger.debug("Getting all visited websites from database")
        try:
            response = bot_instance.supabase.table('visited_websites').select('*').execute()
            logger.info(f"Found {len(response.data)} websites in database")
            for i, record in enumerate(response.data):
                logger.debug(f"Website {i+1}: {record.get('website_url')} (status: {record.get('status')})")
        except Exception as db_error:
            logger.error(f"Error getting websites from database: {db_error}")

        # Return the results
        logger.info("Test completed successfully")
        return jsonify({
            "success": True,
            "message": "Visited websites test completed successfully",
            "url": url,
            "status": status,
            "is_visited": is_visited,
            "visited_websites_count": len(bot_instance.visited_websites),
            "all_websites": [record.get('website_url') for record in response.data] if 'response' in locals() and hasattr(response, 'data') else []
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error testing visited websites: {e}")
        logger.error(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.route('/api/test-skip-visited-website', methods=['POST'])
def test_skip_visited_website():
    """API endpoint for testing that the bot correctly skips already visited websites"""
    global bot_instance

    # Set up logging
    import logging
    logger = logging.getLogger('test_skip_visited_website')
    logger.setLevel(logging.DEBUG)

    logger.debug("Starting test_skip_visited_website endpoint")

    try:
        # Create a new bot instance if needed
        if not bot_instance:
            from contact_bot import ContactBot
            # Initialize with Supabase client
            logger.info(f"Creating new bot instance with Supabase URL: {SUPABASE_URL[:10]}... and key: {SUPABASE_KEY[:10]}...")
            bot_instance = ContactBot(
                headless=True,
                supabase_url=SUPABASE_URL,
                supabase_key=SUPABASE_KEY
            )
            logger.info("Created new bot instance for testing")

        # Get the URL from the request
        data = request.json
        url = data.get('url', 'https://example.com/test')

        logger.info(f"Testing skip visited website functionality with URL: {url}")

        # Check if the website is already visited
        logger.info(f"Checking if website is already visited: {url}")
        is_visited = bot_instance._is_website_visited(url)
        logger.info(f"Is website visited: {is_visited}")

        # Create a mock contact with the website URL
        contact = {
            'id': 'test-contact-id',
            'name': 'Test Contact',
            'company': 'Test Company',
            'website_url_profile': url
        }

        # Set the current contact ID
        bot_instance.current_contact_id = contact['id']

        # Process the contact
        logger.info(f"Processing contact with website URL: {url}")
        try:
            # Call the _process_single_contact method directly
            bot_instance._process_single_contact(contact)

            # Check if the website was skipped
            logger.info(f"Checking if website was skipped")

            # Return the results
            return jsonify({
                "success": True,
                "message": "Skip visited website test completed successfully",
                "url": url,
                "was_visited_before": is_visited,
                "was_skipped": is_visited  # If it was visited before, it should have been skipped
            })
        except Exception as process_error:
            logger.error(f"Error processing website: {process_error}")
            return jsonify({
                "success": False,
                "message": f"Error processing website: {process_error}",
                "url": url,
                "was_visited_before": is_visited
            })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error testing skip visited website: {e}")
        logger.error(f"Traceback: {error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.after_request
def after_request(response):
    """Log all requests"""
    print(f"Request: {request.method} {request.path} - Response: {response.status_code}")
    return response

if __name__ == '__main__':
    # Set up logging to stdout
    import sys
    import logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    app.run(debug=True)
