"""
Contact Bot - Automated website contact form filling and LinkedIn outreach

This script:
1. Reads contact information from Supabase table
2. Visits target website URLs
3. Finds and fills contact forms
4. Searches LinkedIn for users and sends connection requests
5. Updates status in Supabase table
"""

import os
import time
import random
import csv
import json
import re
import traceback
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple, Set
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import Select

# Supabase
from supabase import create_client, Client

# Import enhanced modules
try:
    # First try to import the enhanced form field classifier
    from enhanced_form_ml import EnhancedFormFieldClassifier
    print("Using enhanced form field classifier")
except ImportError:
    try:
        # Fall back to the Supabase-enabled classifier
        from form_ml_supabase import FormFieldClassifier
        print("Using Supabase-enabled form field classifier")
    except ImportError:
        try:
            # Fall back to the original classifier if Supabase version is not available
            from form_ml import FormFieldClassifier
            print("Using local file-based form field classifier")
        except ImportError:
            FormFieldClassifier = None
            print("Form field classifier not available")

# Import intelligent form submission
try:
    from intelligent_form_submission import IntelligentFormSubmission
    print("Using intelligent form submission")
except ImportError:
    IntelligentFormSubmission = None
    print("Intelligent form submission not available")

# Import advanced form discovery
try:
    from advanced_form_discovery import AdvancedFormDiscovery
    print("Using advanced form discovery")
except ImportError:
    AdvancedFormDiscovery = None
    print("Advanced form discovery not available")

# Import enhanced data enrichment
try:
    from enhanced_data_enrichment import EnhancedDataEnrichment
    print("Using enhanced data enrichment")
except ImportError:
    EnhancedDataEnrichment = None
    print("Enhanced data enrichment not available")

# Import intelligent LinkedIn integration
try:
    from intelligent_linkedin import IntelligentLinkedIn
    print("Using intelligent LinkedIn integration")
except ImportError:
    IntelligentLinkedIn = None
    print("Intelligent LinkedIn integration not available")

# Constants
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://eumhqssfvkyuepyrtlqj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck")
TABLE_NAME = os.getenv("SUPABASE_TABLE", "core_data")  # Using the core_data table (renamed from dentist)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MSEDGEDRIVER_LOG_PATH = os.path.join(BASE_DIR, 'msedgedriver.log')

# LinkedIn credentials - should be stored securely in production
# These will be loaded from environment variables or settings
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "")  # LinkedIn username from environment
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")  # LinkedIn password from environment

class ContactBot:
    """Bot for automating contact form filling and LinkedIn outreach"""

    def __init__(self, headless: bool = False, browser_speed: str = "normal",
                 supabase_url: str = "", supabase_key: str = "",
                 your_name: str = "Your Name",
                 linkedin_username: str = "", linkedin_password: str = "",
                 contact_form_template: str = None, settings: Dict[str, Any] = None,
                 is_retry: bool = False):
        """Initialize the bot with all required parameters

        Args:
            headless: Whether to run the browser in headless mode
            browser_speed: Browser speed setting ('fast', 'normal', or 'slow')
            supabase_url: Supabase URL
            supabase_key: Supabase API key
            your_name: Your name to use in templates
            linkedin_username: LinkedIn username/email
            linkedin_password: LinkedIn password
            contact_form_template: Contact form message template
            settings: Additional settings
            is_retry: Whether this is a retry operation (skips column checks)
        """
        # Default speed settings
        self.browser_speed = browser_speed or "normal"
        self.page_load_delay = 2
        self.action_delay = 1

        # Track visited websites to prevent duplicate visits
        self.visited_websites = set()
        self.headless = headless  # Store headless mode setting

        # Load previously visited websites from database
        print("DEBUG: About to call _load_visited_websites from __init__")
        self._load_visited_websites()
        print("DEBUG: Finished calling _load_visited_websites from __init__")

        # Store retry flag
        self.is_retry = is_retry
        print(f"Initialized with is_retry={is_retry}")

        # Cookie persistence settings
        self.cookies_dir = os.path.join(BASE_DIR, 'cookies')
        self.linkedin_cookies_file = os.path.join(self.cookies_dir, 'linkedin_cookies.pkl')

        # Create cookies directory if it doesn't exist
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)

        # Set credentials
        self.linkedin_username = linkedin_username or LINKEDIN_USERNAME
        self.linkedin_password = linkedin_password or LINKEDIN_PASSWORD
        self.contact_form_template = contact_form_template
        self.linkedin_template = None
        self.your_name = your_name or "Your Name"

        # Override Supabase credentials if provided
        global SUPABASE_URL, SUPABASE_KEY
        if supabase_url:
            SUPABASE_URL = supabase_url
        if supabase_key:
            SUPABASE_KEY = supabase_key

        # Initialize components
        self.supabase = self._init_supabase()
        self.driver = self._init_webdriver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        self.linkedin_logged_in = False

        # Settings
        self.settings = settings or self._load_settings()

        # Apply settings
        self.set_browser_speed(self.browser_speed)

        # Initialize enhanced components

        # Initialize machine learning components
        self.field_classifier = None
        try:
            # Try to use the enhanced form field classifier first
            if 'EnhancedFormFieldClassifier' in globals():
                self.field_classifier = EnhancedFormFieldClassifier(supabase_client=self.supabase)
                print("Initialized enhanced form field classifier")
            elif FormFieldClassifier is not None:
                # Fall back to the original classifier
                self.field_classifier = FormFieldClassifier(supabase_client=self.supabase)
                print("Initialized original form field classifier")

            if self.field_classifier and self.field_classifier.is_trained:
                print("Loaded machine learning model for form field recognition")
            elif self.field_classifier:
                print("Machine learning model for form field recognition not trained yet")
        except Exception as e:
            print(f"Error initializing form field classifier: {e}")
            self.field_classifier = None

        # Initialize intelligent form submission
        self.intelligent_form_submission = None
        if 'IntelligentFormSubmission' in globals():
            try:
                self.intelligent_form_submission = IntelligentFormSubmission(
                    driver=self.driver,
                    field_classifier=self.field_classifier,
                    settings=self.settings
                )
                print("Initialized intelligent form submission")
            except Exception as e:
                print(f"Error initializing intelligent form submission: {e}")

        # Initialize advanced form discovery
        self.advanced_form_discovery = None
        if 'AdvancedFormDiscovery' in globals():
            try:
                self.advanced_form_discovery = AdvancedFormDiscovery(
                    driver=self.driver,
                    settings=self.settings
                )
                print("Initialized advanced form discovery")
            except Exception as e:
                print(f"Error initializing advanced form discovery: {e}")

        # Initialize enhanced data enrichment
        self.enhanced_data_enrichment = None
        if 'EnhancedDataEnrichment' in globals():
            try:
                self.enhanced_data_enrichment = EnhancedDataEnrichment(
                    driver=self.driver,
                    supabase_client=self.supabase,
                    settings=self.settings
                )
                print("Initialized enhanced data enrichment")
            except Exception as e:
                print(f"Error initializing enhanced data enrichment: {e}")

        # Initialize intelligent LinkedIn integration
        self.intelligent_linkedin = None
        if 'IntelligentLinkedIn' in globals():
            try:
                self.intelligent_linkedin = IntelligentLinkedIn(
                    driver=self.driver,
                    settings=self.settings
                )
                print("Initialized intelligent LinkedIn integration")
            except Exception as e:
                print(f"Error initializing intelligent LinkedIn integration: {e}")

        # Initialize counter for tracking processed contacts
        self.contacts_processed = 0

    def set_linkedin_credentials(self, username: str, password: str) -> None:
        """Set LinkedIn credentials

        Args:
            username: LinkedIn username/email
            password: LinkedIn password
        """
        self.linkedin_username = username
        self.linkedin_password = password
        print("LinkedIn credentials set.")

    def set_contact_form_template(self, template: str, your_name: str) -> None:
        """Set contact form message template

        Args:
            template: Message template with placeholders
            your_name: Your name to use in the template
        """
        self.contact_form_template = template
        self.your_name = your_name
        print("Contact form template set.")

        # Show available template variables
        print("\nAvailable template variables for your message:")
        variables = self.get_available_template_variables()
        print(", ".join(["{" + var + "}" for var in variables]))
        print("\nExample: 'Hi {name}, I noticed {company} is doing great work...'")

        # Check if template contains any variables that aren't available
        import re
        template_vars = re.findall(r'\{([^}]+)\}', template)
        unavailable_vars = [var for var in template_vars if var not in variables]
        if unavailable_vars:
            print(f"\nWarning: Your template contains variables that may not be available: {', '.join(unavailable_vars)}")
            print("These variables might not be replaced if the data is missing.")

    def set_linkedin_template(self, template: str, your_name: str) -> None:
        """Set LinkedIn message template

        Args:
            template: Message template with placeholders
            your_name: Your name to use in the template
        """
        self.linkedin_template = template
        self.your_name = your_name
        print("LinkedIn template set.")

        # Show available template variables
        print("\nAvailable template variables for your LinkedIn message:")
        variables = self.get_available_template_variables()
        print(", ".join(["{" + var + "}" for var in variables]))
        print("\nNote: LinkedIn messages have a 300 character limit.")

        # Check if template contains any variables that aren't available
        import re
        template_vars = re.findall(r'\{([^}]+)\}', template)
        unavailable_vars = [var for var in template_vars if var not in variables]
        if unavailable_vars:
            print(f"\nWarning: Your template contains variables that may not be available: {', '.join(unavailable_vars)}")
            print("These variables might not be replaced if the data is missing.")

    def get_available_template_variables(self) -> List[str]:
        """Get available template variables from Supabase table columns

        Returns:
            List of column names that can be used as template variables
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot get template variables.")
            return ["name", "company", "email", "phone", "your_name", "your_email", "first_name",
                    "your_first_name", "your_last_name", "your_company", "default_message"]  # Return default variables

        try:
            # Try to get one record to check the structure
            sample = self.supabase.table(TABLE_NAME).select("*").limit(1).execute()
            if sample.data:
                columns = list(sample.data[0].keys())
                print(f"Available template variables from table: {', '.join(columns)}")

                # Add special variables
                special_vars = [
                    "your_name", "your_email", "phone", "first_name",
                    "your_first_name", "your_last_name", "your_company", "default_message"
                ]
                for var in special_vars:
                    if var not in columns:
                        columns.append(var)

                return columns
            else:
                print("No data found in table. Using default template variables.")
                return ["name", "company", "email", "phone", "your_name", "your_email", "first_name",
                        "your_first_name", "your_last_name", "your_company", "default_message"]
        except Exception as e:
            print(f"Error getting template variables: {e}")
            return ["name", "company", "email", "phone", "your_name", "your_email", "first_name",
                    "your_first_name", "your_last_name", "your_company", "default_message"]

    def set_browser_speed(self, speed: str) -> None:
        """Set browser navigation speed

        Args:
            speed: Speed setting ('fast', 'normal', or 'slow')
        """
        self.browser_speed = speed

        # Set delay times based on speed
        if speed == 'fast':
            self.page_load_delay = 1
            self.action_delay = 0.5
            print("Browser speed set to fast")
        elif speed == 'slow':
            self.page_load_delay = 5
            self.action_delay = 2
            print("Browser speed set to slow (good for debugging)")
        else:  # normal
            self.page_load_delay = 2
            self.action_delay = 1
            print("Browser speed set to normal")

    def _init_supabase(self) -> Optional[Client]:
        """Initialize Supabase client

        Returns:
            Supabase client or None if initialization fails
        """
        print("DEBUG: Starting _init_supabase method")
        try:
            # Try to get credentials from instance variables first
            supabase_url = getattr(self, 'supabase_url', None) or SUPABASE_URL
            supabase_key = getattr(self, 'supabase_key', None) or SUPABASE_KEY
            print(f"DEBUG: Supabase URL available: {bool(supabase_url)}, Key available: {bool(supabase_key)}")

            # If not available, try to get from environment variables
            if not supabase_url:
                supabase_url = os.getenv("SUPABASE_URL")
                if supabase_url:
                    self.supabase_url = supabase_url
                    print("DEBUG: Got Supabase URL from environment variable")

            if not supabase_key:
                supabase_key = os.getenv("SUPABASE_KEY")
                if supabase_key:
                    self.supabase_key = supabase_key
                    print("DEBUG: Got Supabase key from environment variable")

            if supabase_url and supabase_key:
                print("DEBUG: Creating Supabase client with URL and key")
                supabase = create_client(supabase_url, supabase_key)
                print("Successfully initialized Supabase client.")

                # Test the connection by making a simple query
                try:
                    print("DEBUG: Testing Supabase connection with a simple query")
                    test_response = supabase.table('visited_websites').select('count', count='exact').limit(1).execute()
                    print(f"DEBUG: Test query response: {test_response}")
                    print("DEBUG: Supabase connection test successful")
                except Exception as test_error:
                    print(f"DEBUG: Supabase connection test failed: {test_error}")
                    if "does not exist" in str(test_error).lower():
                        print("DEBUG: The visited_websites table does not exist yet")
                    else:
                        print(f"DEBUG: Other error in test query: {test_error}")

                # Ensure the table has the necessary columns for tracking form submissions
                self._ensure_form_submission_columns(supabase)

                return supabase
            else:
                print("CRITICAL: Supabase URL or Key is missing.")
                return None
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _ensure_form_submission_columns(self, supabase: Client) -> None:
        """Ensure the table has the necessary columns for tracking form submissions

        Args:
            supabase: Supabase client
        """
        try:
            # Check if the table exists and has the necessary columns
            try:
                # Try to get one record to check the structure
                sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()

                if sample.data:
                    columns = sample.data[0].keys()
                    missing_columns = []

                    # Check for required columns
                    required_columns = [
                        "contact_form_submitted",
                        "contact_form_submitted_message",
                        "contact_form_submitted_timestamp",
                        "niche"
                    ]

                    for column in required_columns:
                        if column not in columns:
                            missing_columns.append(column)

                    if missing_columns:
                        print(f"Missing columns in {TABLE_NAME} table: {', '.join(missing_columns)}")
                        print("The exec_sql function is not available in your Supabase project.")
                        print("Please add the following columns manually in the Supabase dashboard:")

                        for column in missing_columns:
                            if column == "contact_form_submitted":
                                print(f"- {column}: boolean (nullable)")
                            elif column == "contact_form_submitted_message":
                                print(f"- {column}: text (nullable)")
                            elif column == "contact_form_submitted_timestamp":
                                print(f"- {column}: timestamptz (nullable)")
                            elif column == "niche":
                                print(f"- {column}: text (default: 'dentist')")

                        print("\nTo add these columns in the Supabase dashboard:")
                        print("1. Go to your Supabase project dashboard")
                        print("2. Click on 'Table Editor' in the left sidebar")
                        print(f"3. Select the '{TABLE_NAME}' table")
                        print("4. Click on 'Add Column' and create each of the columns listed above")

                        # Try to update a record to see if the columns already exist
                        # This will fail if the columns don't exist, but it's a good way to check
                        try:
                            # Try to update a record with the new columns
                            # This will fail if the columns don't exist
                            test_update = {
                                "contact_form_submitted": None,
                                "contact_form_submitted_message": None,
                                "contact_form_submitted_timestamp": None
                            }

                            # Get the ID of the first record
                            first_id = sample.data[0].get("id")
                            if first_id:
                                # Try to update the record
                                supabase.table(TABLE_NAME).update(test_update).eq("id", first_id).execute()
                                print("\nGood news! The columns appear to exist even though they weren't in the sample data.")
                                print("You can ignore the previous message about adding columns manually.")
                        except Exception as e:
                            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                                print("\nConfirmed: The columns do not exist and need to be added manually.")
                            else:
                                print(f"\nError testing columns: {e}")
                    else:
                        print(f"All required columns exist in {TABLE_NAME} table.")
                else:
                    print(f"No data found in {TABLE_NAME} table. Cannot check structure.")
                    print("Please make sure you have at least one record in the table.")
                    print("The following columns are required for form submission tracking:")
                    print("- contact_form_submitted: boolean (nullable)")
                    print("- contact_form_submitted_message: text (nullable)")
                    print("- contact_form_submitted_timestamp: timestamptz (nullable)")
            except Exception as e:
                print(f"Error checking table structure: {e}")
                print("You may need to manually add these columns in the Supabase dashboard.")
                print("Required columns: contact_form_submitted (boolean), contact_form_submitted_message (text), contact_form_submitted_timestamp (timestamptz)")
        except Exception as e:
            print(f"Error ensuring form submission columns: {e}")

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from settings.json

        Returns:
            Dictionary of settings
        """
        try:
            settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    return json.load(f)
            else:
                print("Settings file not found. Using default settings.")
                return {}
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def _init_webdriver(self, headless: bool) -> webdriver.Edge:
        """Initialize Selenium WebDriver

        Args:
            headless: Whether to run the browser in headless mode

        Returns:
            WebDriver instance
        """
        edge_options = EdgeOptions()
        if headless:
            edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")

        try:
            edge_service = EdgeService(log_output=MSEDGEDRIVER_LOG_PATH, verbose=True)
            print(f"Starting WebDriver with logging to: {MSEDGEDRIVER_LOG_PATH}")
            driver = webdriver.Edge(service=edge_service, options=edge_options)
        except Exception as e:
            print(f"Error initializing EdgeService with logging: {e}. Falling back.")
            driver = webdriver.Edge(options=edge_options)

        print("WebDriver started.")
        return driver

    def process_contacts(self, limit: int = None, offset: int = None, niche: str = None, start_from_last: bool = True) -> None:
        """Process contacts from the database

        Args:
            limit: Maximum number of contacts to process
            offset: Number of contacts to skip
            niche: Filter contacts by niche
            start_from_last: Start from the last processed contact
        """
        # Reset the counter for tracking processed contacts for ML retraining
        self.contacts_processed = 0
        # Process contacts using the process_contacts_from_supabase method
        self.process_contacts_from_supabase(limit=limit, resume=start_from_last)

        # Retrain the field classifier after processing a batch of contacts
        if self.field_classifier and hasattr(self.field_classifier, 'retrain_with_all_data'):
            print("Retraining field classifier with all collected examples...")
            if self.retrain_field_classifier():
                print("Field classifier successfully retrained with new examples")
            else:
                print("Field classifier retraining failed or no new examples available")

    def process_contacts_from_supabase(self, limit: int = 10, filter_status: str = None, keep_browser_open: bool = False, resume: bool = True) -> None:
        """Process contacts from Supabase table

        Args:
            limit: Maximum number of contacts to process
            filter_status: Filter by status ('pending', 'failed', or None for all)
            keep_browser_open: Whether to keep the browser open after processing
            resume: Whether to resume from the last processed contact
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot process contacts.")
            return

        try:
            # Start building the query
            query = self.supabase.table(TABLE_NAME).select("*")

            # Get the last processed contact ID if resume is enabled
            last_processed_id = None
            if resume:
                try:
                    # Get the last processed contact ID from outreach_settings
                    settings_response = self.supabase.table('outreach_settings').select("value").eq("key", "last_processed_contact_id").execute()
                    if settings_response.data and len(settings_response.data) > 0:
                        last_processed_id = settings_response.data[0].get("value")
                        print(f"Resuming from last processed contact ID: {last_processed_id}")
                except Exception as e:
                    print(f"Error getting last processed contact ID: {e}")

            # Apply filters based on the table structure
            # First, check if the table has the expected columns
            try:
                # Try to get one record to check the structure
                sample = self.supabase.table(TABLE_NAME).select("*").limit(1).execute()
                if sample.data:
                    columns = sample.data[0].keys()
                    print(f"Available columns in table: {', '.join(columns)}")

                    # Apply filters based on available columns
                    if 'contact_form_submitted' in columns:
                        if filter_status == 'pending':
                            query = query.is_("contact_form_submitted", None)
                        elif filter_status == 'failed':
                            query = query.eq("contact_form_submitted", False)

                    # If website_url is a required column, filter out records without it
                    if 'website_url' in columns:
                        query = query.not_.is_("website_url", None)

                    # If resuming, start from the last processed contact
                    if resume and last_processed_id and 'id' in columns:
                        print(f"Excluding previously processed contact with ID: {last_processed_id}")

                        # Instead of using timestamp, use the ID directly to exclude the last processed contact
                        # This ensures we don't process the same contact again
                        query = query.neq("id", last_processed_id)

                        # Also add a check to ensure we don't process contacts that have already been processed
                        # This is a more robust approach that prevents processing the same contact multiple times
                        if 'contact_form_submitted' in columns:
                            # If we're filtering by status, we've already applied this filter
                            if filter_status is None:
                                # Only apply this filter if we're not already filtering by status
                                if 'contact_form_submitted_timestamp' in columns:
                                    # If we have a timestamp column, use it to order by most recently processed first
                                    query = query.order('contact_form_submitted_timestamp', desc=True)
                                    print("Ordering by most recently processed contacts first")
            except Exception as e:
                print(f"Error checking table structure: {e}")

            # Order by contact_form_submitted status first (NULL first), then by created_at
            # This ensures we process unprocessed contacts first, then in order of creation
            if 'contact_form_submitted' in columns:
                # First, get contacts that haven't been processed yet (NULL values first)
                print("Ordering by unprocessed contacts first, then by creation date")
                # We can't directly order by NULL first in Supabase, so we'll use a workaround
                # by ordering by contact_form_submitted (which puts TRUE/FALSE before NULL)
                # and then reversing the order with desc=True
                query = query.order("contact_form_submitted", desc=True)

            # Then order by created_at as a secondary sort
            query = query.order("created_at", desc=False)

            # Limit the number of records
            query = query.limit(limit)

            # Execute the query
            response = query.execute()
            contacts = response.data
            print(f"Found {len(contacts)} contacts to process.")

            # Process each contact, checking for stop requests between contacts
            for i, contact in enumerate(contacts):
                # Check if processing should stop
                if hasattr(self, 'check_stop') and callable(self.check_stop) and self.check_stop():
                    print(f"Processing stopped after {i} contacts")
                    break

                # Log more detailed information about the contact being processed
                print(f"Processing contact {i+1} of {len(contacts)}: ID {contact.get('id')}")

                # Process the contact
                self._process_single_contact(contact)

            # If keep_browser_open is True, wait for user input before closing
            if keep_browser_open and not self.headless:
                # Check if processing should stop before keeping browser open
                if hasattr(self, 'check_stop') and callable(self.check_stop) and self.check_stop():
                    print("Processing stopped, not keeping browser open")
                    return

                print("\n\n========================================")
                print("BROWSER KEPT OPEN FOR INSPECTION")
                print("The browser will remain open for 60 seconds so you can inspect it.")
                print("You can close this terminal window to end the process early.")
                print("========================================\n\n")

                # Keep browser open for 60 seconds, checking for stop requests
                for i in range(60, 0, -1):
                    # Check if processing should stop
                    if hasattr(self, 'check_stop') and callable(self.check_stop) and self.check_stop():
                        print("\rProcessing stopped, closing browser...                   ")
                        break

                    print(f"\rBrowser will close in {i} seconds...", end="")
                    time.sleep(1)
                print("\rBrowser closing now...                   ")

        except Exception as e:
            print(f"Error processing contacts from Supabase: {e}")
            traceback.print_exc()

    def process_csv(self, csv_file_path: str) -> None:
        """Process contacts from CSV file

        Args:
            csv_file_path: Path to CSV file
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot process CSV.")
            return

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Insert into Supabase if not already exists
                    self._insert_contact_if_not_exists(row)

            # Now process the contacts
            self.process_contacts_from_supabase()

        except Exception as e:
            print(f"Error processing CSV file: {e}")
            traceback.print_exc()

    def _insert_contact_if_not_exists(self, contact_data: Dict[str, Any]) -> None:
        """Insert contact into Supabase if it doesn't already exist

        Args:
            contact_data: Contact data to insert
        """
        try:
            # Check if contact already exists
            response = self.supabase.table(TABLE_NAME) \
                .select("id") \
                .eq("email", contact_data.get("email", "")) \
                .execute()

            if response.data and len(response.data) > 0:
                print(f"Contact with email {contact_data.get('email')} already exists.")
                return

            # Insert new contact
            self.supabase.table(TABLE_NAME).insert(contact_data).execute()
            print(f"Inserted new contact: {contact_data.get('name', 'Unknown')}")

        except Exception as e:
            print(f"Error inserting contact: {e}")

    def process_contact(self, contact: Dict[str, Any], contact_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a single contact

        Args:
            contact: Contact data
            contact_id: Optional contact ID for status updates

        Returns:
            Updated contact data
        """
        # Store the current contact ID for use in other methods
        self.current_contact_id = contact_id

        print(f"\n{'='*50}")
        print(f"Processing contact: {contact.get('name', 'Unknown')} - {contact.get('company', 'Unknown')}")
        print(f"{'='*50}\n")

        # Process the contact and return the updated data
        # This is a placeholder for the actual implementation
        return contact

    def _process_single_contact(self, contact: Dict[str, Any]) -> None:
        """Process a single contact

        Args:
            contact: Contact data from Supabase
        """
        # Get contact ID - this is required
        contact_id = contact.get("id")
        if not contact_id:
            print("Error: Contact is missing ID field")
            return

        # Store the current contact ID for use in other methods
        self.current_contact_id = contact_id

        # Get contact name and company for better logging
        contact_name = contact.get("name") or contact.get("dentist_name_profile") or "Unknown"
        company_name = contact.get("company") or contact.get("business_name_profile_page") or contact.get("listing_business_name") or "Unknown"
        website_url = contact.get("website_url") or contact.get("website_url_profile") or "Unknown"

        # Log the contact being processed with clear formatting
        print("\n" + "="*80)
        print(f"🔍 NOW PROCESSING CONTACT: {contact_name} at {company_name}")
        print(f"🌐 Website: {website_url}")
        print(f"🆔 Contact ID: {contact_id}")
        print("="*80 + "\n")

        # Update the current status in settings for UI display
        try:
            self._update_current_status({
                "current_contact_id": contact_id,
                "current_contact_name": contact_name,
                "current_company_name": company_name,
                "current_website": website_url,
                "processing_stage": "starting",
                "last_updated": datetime.now().isoformat()
            })
        except Exception as e:
            print(f"Error updating current status: {e}")

        # Get website URL - this is required for processing
        if not website_url or website_url == "Unknown" or website_url.strip() == "":
            error_msg = "No website URL found in contact data"
            print(error_msg)

            # Mark the record as processed with error status
            try:
                # Update website_visited status
                self._update_status(contact_id, "website_visited", False, error_msg)

                # Mark as processed with error
                self._update_status(contact_id, "error", True, error_msg)

                # Also mark contact_form_submitted as False to prevent reprocessing
                self._update_status(contact_id, "contact_form_submitted", False, "Cannot process: " + error_msg)

                # Update the timestamp to mark as processed
                timestamp = datetime.now().isoformat()
                self._update_status(contact_id, "contact_form_submitted_timestamp", timestamp)

                # Direct database update as a fallback
                try:
                    self.supabase.table(TABLE_NAME).update({
                        "contact_form_submitted": False,
                        "contact_form_submitted_message": "Cannot process: " + error_msg,
                        "contact_form_submitted_timestamp": timestamp,
                        "error": True
                    }).eq("id", contact_id).execute()
                    print(f"✅ Database record updated to mark as processed with error")
                except Exception as db_error:
                    print(f"Warning: Direct database update failed: {db_error}")
            except Exception as status_error:
                print(f"Warning: Could not update status: {status_error}")

            # Update the processing stage in the status
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "error",
                "error_message": error_msg,
                "last_updated": datetime.now().isoformat()
            })

            print(f"⚠️ Skipping contact {contact_id} ({contact_name}) due to missing website URL")

            # Update the last processed contact ID in settings to prevent reprocessing
            try:
                # Check if settings table exists and create it if needed
                self._ensure_settings_table_exists()

                # Update or insert the last processed contact ID
                settings_response = self.supabase.table('outreach_settings').select("id").eq("key", "last_processed_contact_id").execute()
                if settings_response.data and len(settings_response.data) > 0:
                    # Update existing record
                    self.supabase.table('outreach_settings').update({"value": contact_id, "updated_at": "now()"}).eq("key", "last_processed_contact_id").execute()
                else:
                    # Insert new record
                    self.supabase.table('outreach_settings').insert({"key": "last_processed_contact_id", "value": contact_id}).execute()

                print(f"✅ Updated last processed contact ID to {contact_id}")
            except Exception as e:
                print(f"❌ Error updating last processed contact ID: {e}")

            return

        # Validate URL format
        if not website_url.startswith(('http://', 'https://')):
            # Try to fix the URL by adding https://
            fixed_url = 'https://' + website_url
            print(f"Website URL doesn't start with http:// or https://, attempting to fix: {website_url} -> {fixed_url}")
            website_url = fixed_url

        # Update the processing stage in the status
        self._update_current_status({
            "current_contact_id": self.current_contact_id,
            "current_contact_name": contact_name,
            "current_company_name": company_name,
            "current_website": website_url,
            "processing_stage": "visiting_website",
            "last_updated": datetime.now().isoformat()
        })

        # Check if we've already visited this website (in memory or database)
        if self._is_website_visited(website_url):
            error_msg = f"Website already visited: {website_url}"
            print(f"Error: {error_msg}")
            self._update_status(contact_id, "website_visited", False, error_msg)
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "error",
                "error_message": error_msg,
                "last_updated": datetime.now().isoformat()
            })
            return

        # Visit the website
        try:
            print(f"Visiting website: {website_url}")

            # Add to visited websites set and save to database
            self.visited_websites.add(website_url)
            self._save_visited_website(website_url, "visiting")

            # Set a page load timeout to handle unresponsive websites
            self.driver.set_page_load_timeout(30)  # 30 seconds timeout

            try:
                # Set a maximum wait time for page load
                start_time = time.time()
                max_load_time = 30  # Maximum 30 seconds to load the page

                print(f"Attempting to load website: {website_url}")
                self.driver.get(website_url)

                # Wait for page to load with timeout
                wait_time = 0
                while wait_time < max_load_time:
                    # Check if page has loaded
                    page_state = self.driver.execute_script('return document.readyState;')
                    if page_state == 'complete':
                        print(f"Page loaded successfully after {wait_time:.1f} seconds")
                        break

                    # Sleep for a short interval
                    time.sleep(1)
                    wait_time = time.time() - start_time

                    # Print progress every 5 seconds
                    if wait_time % 5 < 1:
                        print(f"Still loading page... ({wait_time:.1f} seconds elapsed)")

                # Additional delay based on speed setting
                time.sleep(self.page_load_delay)

                # Check if we timed out
                if wait_time >= max_load_time:
                    print(f"⚠️ Page load timed out after {max_load_time} seconds, but continuing anyway")

                # Take screenshot for debugging
                screenshot_path = f"screenshot_{contact_id}.png"
                try:
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")
                except Exception as e:
                    print(f"Error saving screenshot: {e}")

                # Check if the page loaded successfully
                page_source = self.driver.page_source
                if "404" in page_source and ("not found" in page_source.lower() or "page not found" in page_source.lower()):
                    error_msg = "Website returned a 404 Not Found error"
                    print(f"Error: {error_msg}")
                    self._update_status(contact_id, "website_visited", False, error_msg)
                    self._update_current_status({
                        "current_contact_id": self.current_contact_id,
                        "processing_stage": "error",
                        "error_message": error_msg,
                        "last_updated": datetime.now().isoformat()
                    })
                    return

                # Update status
                self._update_status(contact_id, "website_visited", True)
                print(f"Successfully visited website for contact {contact_id}")

            except TimeoutException as te:
                # Handle timeout exception
                error_msg = f"Website timed out: {website_url}"
                print(f"Error: {error_msg}")
                self._update_status(contact_id, "website_visited", False, error_msg)
                self._update_current_status({
                    "current_contact_id": self.current_contact_id,
                    "processing_stage": "error",
                    "error_message": error_msg,
                    "last_updated": datetime.now().isoformat()
                })

                # Reset the timeout and continue to the next contact
                self.driver.set_page_load_timeout(300)  # Reset to a higher value
                return

            # Check for stop request after visiting website
            if hasattr(self, 'check_stop') and callable(self.check_stop) and self.check_stop():
                print(f"Processing stopped after visiting website for contact {contact_id}")
                return

            # Find contact form with a 20-second timeout
            print(f"Looking for contact form on {website_url} (20-second timeout)")
            form_search_start_time = time.time()
            form_search_timeout = 20  # 20 seconds timeout for finding contact form

            # Set a timeout for finding the contact form
            contact_form = None
            try:
                # Use a separate thread to find the contact form with timeout
                from concurrent.futures import ThreadPoolExecutor, TimeoutError
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(self._find_contact_form)
                    try:
                        contact_form = future.result(timeout=form_search_timeout)
                    except TimeoutError:
                        print(f"⏱️ Contact form search timed out after {form_search_timeout} seconds")
                        # Update status to indicate timeout
                        self._update_status(contact_id, "contact_form_submitted", False,
                                          f"Contact form search timed out after {form_search_timeout} seconds")
            except Exception as timeout_error:
                print(f"Error during contact form search with timeout: {timeout_error}")
                traceback.print_exc()

            # Check if we found a contact form
            if not contact_form:
                print(f"No contact form found for {contact_name} on {website_url} within {form_search_timeout} seconds")
                # Use contact_form_submitted instead of contact_form_found for compatibility
                if "timed out" not in self._get_status(contact_id, "contact_form_submitted_message", ""):
                    self._update_status(contact_id, "contact_form_submitted", False, "Contact form not found")

                # Try to find alternative contact methods
                print("Scanning for alternative contact methods...")
                alternative_contacts = self._scan_for_alternative_contacts()
                if alternative_contacts:
                    print(f"Found alternative contact methods: {alternative_contacts}")
                    self._update_alternative_contacts(contact_id, alternative_contacts)

                # Update the processing stage in the status
                self._update_current_status({
                    "current_contact_id": self.current_contact_id,
                    "processing_stage": "completed",  # Mark as completed even if we didn't find a form
                    "last_updated": datetime.now().isoformat()
                })
                return

            print(f"Contact form found for {contact_name} on {website_url}")
            # Use contact_form_submitted with None (pending) status to indicate form was found but not submitted yet
            self._update_status(contact_id, "contact_form_submitted", None, "Contact form found, preparing to submit")

            # Check for stop request after finding contact form
            if hasattr(self, 'check_stop') and callable(self.check_stop) and self.check_stop():
                print(f"Processing stopped after finding contact form for contact {contact_id}")
                return

            # Fill contact form with a 20-second timeout
            print(f"Filling contact form for {contact_name} (20-second timeout)")
            form_fill_timeout = 20  # 20 seconds timeout for filling and submitting form

            # Use a separate thread to fill the contact form with timeout and retries
            success = False
            message = "Form submission timed out"
            try:
                from concurrent.futures import ThreadPoolExecutor, TimeoutError
                with ThreadPoolExecutor() as executor:
                    # Use our new retry method instead of directly calling _fill_contact_form
                    future = executor.submit(self._fill_contact_form_with_retries, contact)
                    try:
                        success, message = future.result(timeout=form_fill_timeout * 3)  # Increased timeout for retries
                    except TimeoutError:
                        print(f"⏱️ Form submission with retries timed out after {form_fill_timeout * 3} seconds")
                        # Update status to indicate timeout
                        success = False
                        message = f"Form submission with retries timed out after {form_fill_timeout * 3} seconds"
            except Exception as timeout_error:
                print(f"Error during form submission with timeout: {timeout_error}")
                traceback.print_exc()
                success = False
                message = f"Error during form submission: {str(timeout_error)}"

            # Check if form was filled but not submitted due to setting
            if success and "not submitted (submit_form setting is disabled)" in message:
                # Use a special status to indicate form was filled but not submitted due to setting
                self._update_status(contact_id, "contact_form_submitted", "skipped", message)
                print(f"Form filled but submission skipped due to submit_form setting for {contact_name}")

                # Update the processing stage in the status with skipped flag
                self._update_current_status({
                    "current_contact_id": self.current_contact_id,
                    "processing_stage": "completed",
                    "form_submission_skipped": True,
                    "last_updated": datetime.now().isoformat()
                })
            else:
                # Normal status update based on success
                if success:
                    print(f"Successfully submitted contact form for {contact_name}")
                    # Mark website as successfully submitted in visited_websites table
                    self._save_visited_website(website_url, "form_submitted")
                else:
                    print(f"Failed to submit contact form for {contact_name}: {message}")
                    # Mark website as failed in visited_websites table
                    self._save_visited_website(website_url, "form_failed")

                # Update the status in the database
                self._update_status(contact_id, "contact_form_submitted", success, message)

            # Always scan for alternative contact methods regardless of form submission success
            print("Scanning for alternative contact methods for data enrichment...")
            alternative_contacts = self._scan_for_alternative_contacts()
            if alternative_contacts:
                print(f"Found alternative contact methods: {alternative_contacts}")

                # Use the direct method to add columns to the main table
                self._update_enriched_data_columns(contact_id, alternative_contacts)
                print("Data enrichment completed and saved directly to main table with enriched_ prefix")
            else:
                print("No alternative contact methods found during data enrichment scan")

            # Update the processing stage to indicate we're done with the contact form
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "completed",  # Mark as fully completed
                "last_updated": datetime.now().isoformat()
            })

            # Add a timestamp to mark this record as fully processed
            timestamp = datetime.now().isoformat()
            # Make sure the processed_timestamp column exists
            self._check_and_create_column("processed_timestamp")
            self._update_status(contact_id, "processed_timestamp", timestamp)
            print(f"✅ Record {contact_id} marked as completed at {timestamp}")

            # Check for stop request after filling contact form
            if hasattr(self, 'check_stop') and callable(self.check_stop) and self.check_stop():
                print(f"Processing stopped after filling contact form for contact {contact_id}")
                return

            # Add a delay after form submission to allow time to see the form submission
            print(f"Waiting 10 seconds after form submission to allow time to see the results...")
            time.sleep(10)
            print(f"Delay complete. Continuing with processing.")

            # Check if we're in retry mode - if so, log but don't skip LinkedIn connection
            if hasattr(self, 'is_retry') and self.is_retry:
                print(f"RETRY MODE: But still attempting LinkedIn connection for {contact_name}")

            # Connect on LinkedIn if URL is available or if we have a name
            linkedin_url = contact.get("linkedin_url") or contact.get("LinkedIn") or contact.get("linkedin") or contact.get("linkedin_url_profile")

            if linkedin_url or contact_name:
                print(f"Attempting LinkedIn connection for {contact_name}")
                try:
                    linkedin_success, linkedin_message = self._connect_on_linkedin(contact)
                    if linkedin_success:
                        print(f"Successfully connected with {contact_name} on LinkedIn")
                    else:
                        print(f"Failed to connect with {contact_name} on LinkedIn: {linkedin_message}")

                    # Try to update the status, but don't fail if the column doesn't exist
                    try:
                        # First check if the linkedin_connected column exists
                        print(f"Attempting to update LinkedIn status in database for contact {contact_id}")
                        self._update_status(contact_id, "linkedin_connected", linkedin_success, linkedin_message)
                        print(f"Successfully updated LinkedIn status in database: {linkedin_success}")

                        # Also update the timestamp
                        try:
                            self._update_status(contact_id, "linkedin_connected_timestamp", datetime.now().isoformat())
                            print(f"Successfully updated LinkedIn timestamp in database")
                        except Exception as timestamp_error:
                            print(f"Warning: Could not update LinkedIn timestamp: {timestamp_error}")
                    except Exception as linkedin_status_error:
                        print(f"Warning: Could not update LinkedIn status: {linkedin_status_error}")
                        print("Continuing with processing anyway")
                except Exception as linkedin_error:
                    print(f"Error during LinkedIn connection: {linkedin_error}")
                    print("Continuing with processing anyway")
            else:
                print(f"No LinkedIn information available for {contact_name}")

        except Exception as e:
            # Check for common URL-related errors
            error_msg = str(e).lower()
            if "invalid url" in error_msg or "malformed url" in error_msg or "unknown url" in error_msg:
                error_msg = f"Invalid website URL: {website_url}"
            elif "name resolution" in error_msg or "dns" in error_msg:
                error_msg = f"Website domain not found: {website_url}"
            elif "connection refused" in error_msg or "connection failed" in error_msg:
                error_msg = f"Website connection refused: {website_url}"
            elif "ssl" in error_msg or "certificate" in error_msg:
                error_msg = f"Website SSL/security error: {website_url}"
            else:
                error_msg = f"Error processing contact {contact_name}: {e}"

            print(error_msg)
            traceback.print_exc()
            self._update_status(contact_id, "website_visited", False, error_msg)

            # Try to reset the page load timeout in case it was changed
            try:
                self.driver.set_page_load_timeout(300)  # Reset to a higher value
            except:
                pass

            # Update the processing stage in the status
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "error",
                "error_message": error_msg,
                "last_updated": datetime.now().isoformat()
            })

        print(f"Completed processing contact: {contact_id} ({contact_name})")
        print("-" * 50)

        # Increment the contacts processed counter in the parent method if it exists
        if hasattr(self, 'contacts_processed'):
            self.contacts_processed += 1

            # Retrain the model periodically (every 5 contacts)
            if self.contacts_processed % 5 == 0 and self.field_classifier:
                print(f"Processed {self.contacts_processed} contacts. Retraining field classifier...")
                if self.retrain_field_classifier():
                    print("Field classifier successfully retrained with new examples")
                else:
                    print("Field classifier retraining failed or no new examples available")

        # Update the last processed contact ID in settings
        try:
            # Check if outreach_settings table exists
            try:
                self.supabase.table('outreach_settings').select("count", count="exact").limit(1).execute()
            except Exception as e:
                if "does not exist" in str(e).lower():
                    # Create outreach_settings table
                    sql = """
                    CREATE TABLE IF NOT EXISTS public.outreach_settings (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        key TEXT UNIQUE NOT NULL,
                        value TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                    );
                    """
                    self.supabase.rpc("exec_sql", {"query": sql}).execute()
                    print("Created outreach_settings table")

            # Update or insert the last processed contact ID
            settings_response = self.supabase.table('outreach_settings').select("id").eq("key", "last_processed_contact_id").execute()
            if settings_response.data and len(settings_response.data) > 0:
                # Update existing record
                self.supabase.table('outreach_settings').update({"value": contact_id, "updated_at": "now()"}).eq("key", "last_processed_contact_id").execute()
            else:
                # Insert new record
                self.supabase.table('outreach_settings').insert({"key": "last_processed_contact_id", "value": contact_id}).execute()

            print(f"✅ Updated last processed contact ID to {contact_id}")
        except Exception as e:
            print(f"❌ Error updating last processed contact ID: {e}")

    def _ensure_settings_table_exists(self) -> None:
        """Ensure the outreach_settings table exists in the database"""
        try:
            # Check if outreach_settings table exists
            try:
                self.supabase.table('outreach_settings').select("count", count="exact").limit(1).execute()
                # Table exists
                return
            except Exception as e:
                if "does not exist" in str(e).lower():
                    # Create outreach_settings table
                    sql = """
                    CREATE TABLE IF NOT EXISTS public.outreach_settings (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        key TEXT UNIQUE NOT NULL,
                        value TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                    );
                    """
                    try:
                        self.supabase.rpc("exec_sql", {"query": sql}).execute()
                        print("Created outreach_settings table")
                    except Exception as create_error:
                        print(f"Could not create outreach_settings table using RPC: {create_error}")
                        # Try alternative methods or inform the user
                        print("Please create an 'outreach_settings' table in your Supabase database with columns: id, key, value, created_at, updated_at")
                else:
                    # Some other error
                    print(f"Error checking if outreach_settings table exists: {e}")
        except Exception as e:
            print(f"Error ensuring outreach_settings table exists: {e}")

    def _load_visited_websites(self) -> None:
        """Load previously visited websites from the database"""
        print("DEBUG: Starting _load_visited_websites method")

        # Check if self.supabase attribute exists
        if not hasattr(self, 'supabase'):
            print("DEBUG: self.supabase attribute doesn't exist yet, will load websites later")
            return

        # Check if self.supabase is initialized
        if not self.supabase:
            print("Supabase client not initialized. Cannot load visited websites.")
            return

        try:
            # Check if the visited_websites table exists
            try:
                print("DEBUG: Checking if visited_websites table exists")
                response = self.supabase.table('visited_websites').select('*').limit(1).execute()
                print(f"DEBUG: Response from visited_websites table check: {response}")
                if not response.data:
                    print("No previously visited websites found in database.")
                    return
            except Exception as e:
                # Table might not exist
                print(f"Error checking visited_websites table: {e}")
                print("DEBUG: Table might not exist, skipping table creation as it should be created manually")
                return

            # Load all visited websites
            print("DEBUG: Loading all visited websites from database")
            response = self.supabase.table('visited_websites').select('website_url').execute()
            print(f"DEBUG: Response from select all websites: {response}")
            if response.data:
                for record in response.data:
                    url = record.get('website_url')
                    if url:
                        # Normalize URL by removing protocol and www
                        normalized_url = self._normalize_url(url)
                        self.visited_websites.add(normalized_url)
                        print(f"DEBUG: Added {url} (normalized to {normalized_url}) to visited websites")
                print(f"Loaded {len(self.visited_websites)} previously visited websites from database.")
            else:
                print("DEBUG: No websites found in the database")
        except Exception as e:
            print(f"Error loading visited websites: {e}")
            import traceback
            traceback.print_exc()

    def _save_visited_website(self, url: str, status: str = 'visited') -> None:
        """Save a visited website to the database

        Args:
            url: Website URL
            status: Status of the visit (e.g., 'visited', 'form_submitted', 'failed')
        """
        print(f"DEBUG: Starting _save_visited_website method for URL: {url}, status: {status}")
        if not self.supabase:
            print("Supabase client not initialized. Cannot save visited website.")
            return

        try:
            # Normalize URL
            normalized_url = self._normalize_url(url)
            print(f"DEBUG: Normalized URL: {normalized_url}")

            # Add to in-memory set
            self.visited_websites.add(normalized_url)
            print(f"DEBUG: Added to in-memory set, set now contains {len(self.visited_websites)} URLs")

            # Save to database
            print(f"DEBUG: Attempting to save to database table 'visited_websites'")
            data = {
                'website_url': url,
                'visited_at': 'now()',
                'status': status
            }
            print(f"DEBUG: Data to insert: {data}")

            response = self.supabase.table('visited_websites').upsert(data).execute()
            print(f"DEBUG: Database response: {response}")
            print(f"Saved visited website: {url} with status: {status}")
        except Exception as e:
            print(f"Error saving visited website: {e}")
            import traceback
            traceback.print_exc()

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison

        Args:
            url: URL to normalize

        Returns:
            Normalized URL
        """
        if not url:
            return ""

        # Remove protocol (http://, https://)
        normalized = re.sub(r'^https?://', '', url.lower())

        # Remove www.
        normalized = re.sub(r'^www\.', '', normalized)

        # Remove trailing slash
        normalized = normalized.rstrip('/')

        return normalized

    def _is_website_visited(self, url: str) -> bool:
        """Check if a website has been visited before

        Args:
            url: Website URL to check

        Returns:
            True if the website has been visited before, False otherwise
        """
        if not url:
            return False

        # Normalize URL
        normalized_url = self._normalize_url(url)

        # Check in-memory set
        return normalized_url in self.visited_websites

    def _update_current_status(self, status_data: Dict[str, Any]) -> None:
        """Update the current processing status in settings

        Args:
            status_data: Dictionary with status information
        """
        try:
            # Add timestamp if not present
            if 'last_updated' not in status_data:
                status_data['last_updated'] = datetime.now().isoformat()

            # Always print the status data to the console for debugging
            print(f"CURRENT_STATUS_UPDATE: {json.dumps(status_data)}")

            # Log additional status message for better visibility in the status panel
            if 'processing_stage' in status_data:
                stage = status_data['processing_stage']
                contact_name = status_data.get('current_contact_name', 'Unknown')
                company_name = status_data.get('current_company_name', 'Unknown')

                # Create a user-friendly status message based on the stage
                stage_messages = {
                    'starting': f"Starting to process {contact_name} at {company_name}",
                    'visiting_website': f"Visiting website for {contact_name} at {company_name}",
                    'finding_contact_form': f"Looking for contact form on {company_name} website",
                    'filling_form': f"Filling contact form for {company_name}",
                    'submitting_form': f"Submitting contact form to {company_name}",
                    'connecting_linkedin': f"Connecting with {contact_name} on LinkedIn",
                    'completed': f"Completed processing {contact_name} at {company_name}"
                }

                # Check for form submission status flags
                if 'form_submission_success' in status_data:
                    if status_data['form_submission_success'] is True:
                        stage_messages['completed'] = f"Successfully submitted form for {company_name} with confirmation"
                    elif status_data.get('form_submission_uncertain', False):
                        stage_messages['completed'] = f"Form submitted for {company_name} but result uncertain"
                    elif status_data.get('form_submission_skipped', False):
                        stage_messages['completed'] = f"Form filled but not submitted for {company_name} (submit_form setting disabled)"

                # Check for error status with more details
                if stage == 'error':
                    if 'error_message' in status_data:
                        stage_messages['error'] = f"Error: {status_data['error_message']} for {contact_name} at {company_name}"
                    else:
                        stage_messages['error'] = f"Error processing {contact_name} at {company_name}"

                status_message = stage_messages.get(stage, f"{stage} - Processing {contact_name} at {company_name}")

                # Log the status message with a special prefix that will be picked up by the status filter
                print(f"BOT_STATUS_UPDATE: {status_message}")

                # Also log to the logger if available
                if hasattr(self, 'logger') and self.logger:
                    self.logger.info(f"BOT_STATUS_UPDATE: {status_message}")

            # Ensure we always have contact information in the status data
            # This prevents the UI from showing "Unknown" when refreshing
            if hasattr(self, '_memory_status') and self._memory_status.get('current_processing_status'):
                last_status = self._memory_status.get('current_processing_status', {})

                # Preserve contact name if not in current status
                if ('current_contact_name' not in status_data or
                    not status_data['current_contact_name'] or
                    status_data['current_contact_name'] == 'Unknown'):
                    if 'current_contact_name' in last_status and last_status['current_contact_name']:
                        status_data['current_contact_name'] = last_status['current_contact_name']

                # Preserve company name if not in current status
                if ('current_company_name' not in status_data or
                    not status_data['current_company_name'] or
                    status_data['current_company_name'] == 'Unknown'):
                    if 'current_company_name' in last_status and last_status['current_company_name']:
                        status_data['current_company_name'] = last_status['current_company_name']

                # Preserve website if not in current status
                if ('current_website' not in status_data or
                    not status_data['current_website'] or
                    status_data['current_website'] == 'Unknown' or
                    status_data['current_website'] == '#'):
                    if 'current_website' in last_status and last_status['current_website']:
                        status_data['current_website'] = last_status['current_website']

            # Store the status in memory regardless of database status
            if not hasattr(self, '_memory_status'):
                self._memory_status = {}
            self._memory_status['current_processing_status'] = status_data

            # Check if outreach_settings table exists and create it if it doesn't
            try:
                self.supabase.table('outreach_settings').select("count", count="exact").limit(1).execute()
            except Exception as e:
                if "does not exist" in str(e).lower():
                    # Create outreach_settings table
                    sql = """
                    CREATE TABLE IF NOT EXISTS public.outreach_settings (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        key TEXT UNIQUE NOT NULL,
                        value TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                    );
                    """
                    try:
                        self.supabase.rpc("exec_sql", {"query": sql}).execute()
                        print("Created outreach_settings table")
                    except Exception as create_error:
                        # If the RPC method doesn't exist, try a different approach
                        print(f"Could not create outreach_settings table using RPC: {create_error}")
                        # Try to create the table using a direct SQL query if your Supabase setup allows it
                        # This is a fallback and may not work in all environments
                        try:
                            # This is a simplified approach - in a real app, you might need to use a migration tool
                            # or set up the table through the Supabase dashboard
                            print("Please create an 'outreach_settings' table in your Supabase database with columns: id, key, value, created_at, updated_at")
                            return
                        except Exception as direct_error:
                            print(f"Could not create outreach_settings table directly: {direct_error}")
                            return

            # Convert the status data to JSON
            status_json = json.dumps(status_data)

            # Update or insert the current status
            settings_response = self.supabase.table('outreach_settings').select("id").eq("key", "current_processing_status").execute()
            if settings_response.data and len(settings_response.data) > 0:
                # Update existing record
                self.supabase.table('outreach_settings').update({"value": status_json, "updated_at": "now()"}).eq("key", "current_processing_status").execute()
            else:
                # Insert new record
                self.supabase.table('outreach_settings').insert({"key": "current_processing_status", "value": status_json}).execute()
        except Exception as e:
            print(f"Error updating current status: {e}")



    def _handle_dropdown(self, dropdown_element):
        """Handle dropdown fields intelligently

        Args:
            dropdown_element: Dropdown element to handle

        Returns:
            True if dropdown was handled successfully, False otherwise
        """
        try:
            # Create a Select object
            select = Select(dropdown_element)
            options = select.options

            # Skip the first option if it's a placeholder
            start_index = 1 if len(options) > 1 else 0

            # Try to find a sensible option
            for option in options[start_index:]:
                option_text = option.text.lower()
                # Skip empty or placeholder options
                if not option_text or option_text in ['select', 'choose', 'please select']:
                    continue

                # Prefer options that sound positive or neutral
                positive_words = ['yes', 'interested', 'general', 'inquiry', 'information']
                if any(word in option_text for word in positive_words):
                    select.select_by_visible_text(option.text)
                    print(f"Selected dropdown option: '{option.text}'")
                    return True

            # If no good option found, select the first non-placeholder
            if len(options) > start_index:
                select.select_by_index(start_index)
                print(f"Selected first non-placeholder option: '{options[start_index].text}'")
                return True

            return False
        except Exception as e:
            print(f"Error handling standard dropdown: {e}")

            # Fallback for non-standard dropdowns (div-based)
            try:
                # Click to open dropdown
                dropdown_element.click()
                time.sleep(0.5)

                # Find and click a dropdown item
                dropdown_items = self.driver.find_elements(By.CSS_SELECTOR, '.dropdown-item, .select-option, li')
                if dropdown_items and len(dropdown_items) > 1:
                    dropdown_items[1].click()
                    print("Selected item from non-standard dropdown")
                    return True
            except Exception as e2:
                print(f"Error handling non-standard dropdown: {e2}")

            return False

    def _fill_contact_form_with_retries(self, contact: Dict[str, Any]) -> tuple[bool, str]:
        """Fill and submit contact form with multiple retry attempts using intelligent form submission if available

        This method will try to fill and submit the form up to 3 times,
        using different strategies for each attempt and learning from previous failures.

        Args:
            contact: Contact data

        Returns:
            Tuple of (success, message)
        """
        # Use intelligent form submission if available
        if self.intelligent_form_submission:
            print("Using intelligent form submission with adaptive retry logic")
            # Find the form again to make sure we have a fresh reference
            form = self._find_contact_form()
            if not form:
                return False, "Contact form not found for intelligent submission"

            success, message = self.intelligent_form_submission.fill_form_with_retries(
                form_element=form,
                contact_data=contact,
                max_attempts=3
            )

            # Update our submission log with data from the intelligent form submission
            if hasattr(self.intelligent_form_submission, 'submission_log'):
                self.submission_log = self.intelligent_form_submission.submission_log

            return success, message

        # Fall back to original retry logic
        MAX_ATTEMPTS = 3
        print(f"Starting form submission with up to {MAX_ATTEMPTS} attempts using standard retry logic")

        # Store the original form HTML for analysis between attempts
        try:
            original_form_html = self.driver.find_element(By.TAG_NAME, "form").get_attribute('outerHTML')
        except:
            original_form_html = None

        # Track all attempts for reporting
        attempt_results = []

        # Try different strategies for each attempt
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"\n{'='*20} ATTEMPT {attempt} OF {MAX_ATTEMPTS} {'='*20}")

            # Different strategies for each attempt
            if attempt == 1:
                # First attempt: Standard approach with AI analysis
                print("Using standard approach with AI analysis for first attempt")
                strategy = "standard_with_ai"
            elif attempt == 2:
                # Second attempt: More aggressive approach with different selectors
                print("Using aggressive approach with expanded selectors for second attempt")
                strategy = "aggressive"
                # Analyze previous failure
                self._analyze_form_submission_failure(attempt_results[-1], original_form_html)
            else:
                # Third attempt: Fallback to basic approach with JavaScript injection
                print("Using fallback approach with JavaScript injection for final attempt")
                strategy = "javascript_fallback"
                # Analyze all previous failures
                self._analyze_form_submission_failures(attempt_results, original_form_html)

            # Attempt to fill and submit the form with the current strategy
            success, message = self._fill_contact_form_with_strategy(contact, strategy, attempt)

            # Store the result of this attempt
            attempt_results.append({
                "attempt": attempt,
                "strategy": strategy,
                "success": success,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

            # If successful, return immediately
            if success:
                print(f"✅ Form submission successful on attempt {attempt} using {strategy} strategy")
                # Add attempt information to the message
                return True, f"Form submitted successfully on attempt {attempt} using {strategy} strategy: {message}"

            print(f"❌ Attempt {attempt} failed: {message}")

            # If this isn't the last attempt, refresh the form for the next attempt
            if attempt < MAX_ATTEMPTS:
                print(f"Preparing for next attempt...")
                try:
                    # Try to refresh the page to get a clean form
                    self.driver.refresh()
                    time.sleep(3)  # Wait for page to reload

                    # Find the form again
                    form = self._find_contact_form()
                    if not form:
                        print("Could not find form after refresh, trying to navigate back")
                        # Try to navigate back to the contact page
                        self._navigate_to_contact_page()
                        time.sleep(2)
                        form = self._find_contact_form()
                        if not form:
                            print("Could not find form after navigation, aborting retry attempts")
                            break
                except Exception as e:
                    print(f"Error refreshing form for next attempt: {e}")
                    # Try to navigate back to the contact page as a fallback
                    try:
                        self._navigate_to_contact_page()
                        time.sleep(2)
                    except:
                        print("Could not navigate back to contact page, aborting retry attempts")
                        break

        # If we get here, all attempts failed
        print(f"❌ All {MAX_ATTEMPTS} form submission attempts failed")

        # Compile a detailed failure report
        failure_report = "Form submission failed after multiple attempts:\n"
        for result in attempt_results:
            failure_report += f"- Attempt {result['attempt']} ({result['strategy']}): {result['message']}\n"

        return False, failure_report

    def _fill_contact_form_with_strategy(self, contact: Dict[str, Any], strategy: str, attempt: int) -> tuple[bool, str]:
        """Fill and submit contact form using a specific strategy

        Args:
            contact: Contact data
            strategy: Strategy to use ('standard_with_ai', 'aggressive', 'javascript_fallback')
            attempt: Current attempt number

        Returns:
            Tuple of (success, message)
        """
        print(f"Filling form with {strategy} strategy (attempt {attempt})")

        # Adjust settings based on strategy
        original_browser_speed = self.browser_speed
        original_action_delay = self.action_delay

        try:
            if strategy == "aggressive":
                # Use slower speed for more careful filling
                self.browser_speed = "slow"
                self.action_delay = 2
                # Expand the list of selectors for each field type
                self._expand_field_selectors()
            elif strategy == "javascript_fallback":
                # Use fastest speed for JavaScript approach
                self.browser_speed = "fast"
                self.action_delay = 0.5

            # Call the standard fill method with strategy information
            return self._fill_contact_form(contact, strategy=strategy, attempt=attempt)
        finally:
            # Restore original settings
            self.browser_speed = original_browser_speed
            self.action_delay = original_action_delay

    def _expand_field_selectors(self):
        """Expand the list of selectors for each field type to be more aggressive in finding fields"""
        # This method would dynamically expand the selectors used for finding form fields
        # We'll implement this in a separate method
        print("Expanding field selectors for aggressive form filling")

        # We'll implement the actual expansion in the _fill_contact_form method
        # by checking if strategy == "aggressive"

    def _analyze_form_submission_failure(self, failure_result: Dict[str, Any], form_html: str):
        """Analyze a form submission failure to improve next attempt

        Args:
            failure_result: Result of the failed attempt
            form_html: Original form HTML for analysis
        """
        print("Analyzing form submission failure to improve next attempt")

        if not form_html:
            print("No form HTML available for analysis")
            return

        try:
            # Look for validation messages or error indicators in the current page
            error_elements = self.driver.find_elements(By.CSS_SELECTOR,
                ".error, .form-error, .invalid-feedback, .validation-error, .field-error, .alert, .alert-danger")

            if error_elements:
                print(f"Found {len(error_elements)} error messages on the form")
                for error in error_elements:
                    try:
                        error_text = error.text.strip()
                        if error_text:
                            print(f"Error message: '{error_text}'")
                            # Store this error for use in the next attempt
                            if not hasattr(self, 'form_errors'):
                                self.form_errors = []
                            self.form_errors.append(error_text)
                    except:
                        pass

            # Analyze the form structure for required fields
            required_fields = []
            try:
                # Find all required fields
                required_elements = self.driver.find_elements(By.CSS_SELECTOR, "[required], [aria-required='true']")
                for element in required_elements:
                    field_id = element.get_attribute('id') or ''
                    field_name = element.get_attribute('name') or ''
                    field_type = element.get_attribute('type') or ''
                    field_placeholder = element.get_attribute('placeholder') or ''

                    required_fields.append({
                        'id': field_id,
                        'name': field_name,
                        'type': field_type,
                        'placeholder': field_placeholder
                    })

                if required_fields:
                    print(f"Found {len(required_fields)} required fields that must be filled")
                    # Store required fields for use in the next attempt
                    self.required_fields = required_fields
            except Exception as e:
                print(f"Error analyzing required fields: {e}")

            # Check for CAPTCHA or reCAPTCHA
            try:
                captcha_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    ".g-recaptcha, .recaptcha, .captcha, iframe[src*='recaptcha'], iframe[src*='captcha']")
                if captcha_elements:
                    print(f"⚠️ CAPTCHA detected on the form - this may prevent automated submission")
                    # Store this information for use in the next attempt
                    self.captcha_detected = True
            except:
                pass

        except Exception as e:
            print(f"Error analyzing form submission failure: {e}")

    def _analyze_form_submission_failures(self, all_failures: List[Dict[str, Any]], form_html: str):
        """Analyze all form submission failures to determine best final approach

        Args:
            all_failures: Results of all failed attempts
            form_html: Original form HTML for analysis
        """
        print("Analyzing all form submission failures to determine best final approach")

        # Check if we've detected CAPTCHA in previous attempts
        if hasattr(self, 'captcha_detected') and self.captcha_detected:
            print("CAPTCHA was detected in previous attempts - will try JavaScript bypass approach")
            self.use_js_bypass = True
            return

        # Check if we have consistent error messages across attempts
        if hasattr(self, 'form_errors') and self.form_errors:
            print(f"Consistent error messages across attempts: {self.form_errors}")
            # Look for specific error patterns and adjust strategy accordingly

            # Example: If errors mention missing fields, we'll focus on those fields
            missing_field_patterns = ['required', 'missing', 'empty', 'fill', 'complete']
            if any(pattern in error.lower() for error in self.form_errors for pattern in missing_field_patterns):
                print("Errors indicate missing required fields - will focus on filling all possible fields")
                self.fill_all_fields = True

        # If we have required fields from previous analysis, make sure to focus on them
        if hasattr(self, 'required_fields') and self.required_fields:
            print(f"Will focus on filling {len(self.required_fields)} required fields in final attempt")
            # We'll use this information in the _fill_contact_form method

    def _handle_form_errors(self):
        """Handle form errors and attempt recovery

        Returns:
            True if errors were handled successfully, False otherwise
        """
        # Look for error messages
        error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.error, .form-error, .invalid-feedback, .validation-error, .field-error')

        if not error_elements:
            return True

        print(f"Found {len(error_elements)} error messages on the form, attempting recovery")

        # Process each error
        for error in error_elements:
            try:
                error_text = error.text.lower()
                print(f"Error message: '{error_text}'")

                # Find the associated field for this error
                associated_field = self._find_field_for_error(error)

                if not associated_field:
                    print("Could not find field associated with this error")
                    continue

                # Get field attributes for better debugging
                field_id = associated_field.get_attribute('id') or ''
                field_name = associated_field.get_attribute('name') or ''
                field_type = associated_field.get_attribute('type') or ''

                print(f"Found associated field: id='{field_id}', name='{field_name}', type='{field_type}'")

                # Handle specific error types
                if 'email' in error_text:
                    print("Fixing email field error")
                    associated_field.clear()
                    associated_field.send_keys(self.settings.get('your_email', 'contact@example.com'))
                elif 'required' in error_text or 'empty' in error_text or 'fill' in error_text:
                    print("Fixing required field error")
                    field_type = self._identify_field_type(associated_field)
                    self._fill_field_by_type(associated_field, field_type)
                elif 'invalid' in error_text:
                    print("Fixing invalid format error")
                    # Try a different format or value
                    associated_field.clear()
                    if 'phone' in error_text or 'phone' in field_id or 'phone' in field_name:
                        associated_field.send_keys('555-555-5555')
                    elif 'date' in error_text or 'date' in field_id or 'date' in field_name:
                        associated_field.send_keys('01/01/2023')
                    else:
                        associated_field.send_keys('N/A')
                else:
                    # Generic error handling
                    print("Applying generic error fix")
                    associated_field.clear()
                    associated_field.send_keys('Test')
            except Exception as e:
                print(f"Error handling form error: {e}")
                continue

        return True

    def _find_field_for_error(self, error_element):
        """Find the form field associated with an error message

        Args:
            error_element: Error message element

        Returns:
            Associated form field element or None if not found
        """
        try:
            # Method 1: Check if error is inside a form group with the field
            parent = error_element.find_element(By.XPATH, './ancestor::div[contains(@class, "form-group") or contains(@class, "field") or contains(@class, "input-wrapper")]')
            if parent:
                # Look for input, select, or textarea within the same parent
                fields = parent.find_elements(By.CSS_SELECTOR, 'input, select, textarea')
                if fields:
                    return fields[0]

            # Method 2: Check if error has a "for" attribute pointing to field ID
            error_for = error_element.get_attribute('for')
            if error_for:
                field = self.driver.find_element(By.ID, error_for)
                if field:
                    return field

            # Method 3: Check if error is next to a field
            prev_sibling = self.driver.execute_script("""
                return arguments[0].previousElementSibling;
            """, error_element)

            if prev_sibling and prev_sibling.tag_name in ['input', 'select', 'textarea']:
                return prev_sibling

            # Method 4: Look for field with same name as error message
            error_id = error_element.get_attribute('id') or ''
            if error_id and 'error' in error_id:
                field_id = error_id.replace('error', '').replace('-error', '').replace('_error', '')
                if field_id:
                    try:
                        field = self.driver.find_element(By.ID, field_id)
                        return field
                    except:
                        pass

            return None
        except Exception as e:
            print(f"Error finding field for error: {e}")
            return None

    def _fill_field_by_type(self, field, field_type):
        """Fill a field based on its identified type

        Args:
            field: Form field element
            field_type: Type of the field

        Returns:
            True if field was filled successfully, False otherwise
        """
        try:
            if field_type == 'email':
                field.clear()
                field.send_keys(self.settings.get('your_email', 'contact@example.com'))
            elif field_type == 'first_name':
                field.clear()
                field.send_keys(self.settings.get('your_first_name', 'John'))
            elif field_type == 'last_name':
                field.clear()
                field.send_keys(self.settings.get('your_last_name', 'Doe'))
            elif field_type == 'full_name':
                field.clear()
                field.send_keys(self.settings.get('your_name', 'John Doe'))
            elif field_type == 'phone':
                field.clear()
                field.send_keys(self.settings.get('phone', '555-555-5555'))
            elif field_type == 'company':
                field.clear()
                field.send_keys(self.settings.get('your_company', 'My Company'))
            elif field_type == 'message':
                field.clear()
                field.send_keys(self.settings.get('contact_form_template', 'I am interested in learning more about your services.'))
            elif field_type == 'subject':
                field.clear()
                field.send_keys('Inquiry')
            elif field_type == 'address':
                field.clear()
                field.send_keys('123 Main St')
            elif field_type == 'date':
                return self._handle_date_picker(field)
            elif field_type == 'dropdown':
                return self._handle_dropdown(field)
            elif field_type == 'checkbox':
                if not field.is_selected():
                    field.click()
            elif field_type == 'radio':
                if not field.is_selected():
                    field.click()
            else:
                # Unknown field type, try generic text
                field.clear()
                field.send_keys('Test')

            return True
        except Exception as e:
            print(f"Error filling field by type: {e}")
            return False

    def _record_field_training_example(self, field_attributes: Dict[str, Any], field_type: str, success: bool = True) -> None:
        """Record a field training example for machine learning

        Args:
            field_attributes: Dictionary with field attributes
            field_type: The field type
            success: Whether the form submission was successful
        """
        if self.field_classifier and hasattr(self.field_classifier, 'add_training_example'):
            try:
                source = self.driver.current_url if self.driver else None
                self.field_classifier.add_training_example(
                    field_attributes=field_attributes,
                    field_type=field_type,
                    source=source,
                    success=success
                )
                print(f"Recorded training example for field type '{field_type}'")
            except Exception as e:
                print(f"Error recording field training example: {e}")

    def _handle_date_picker(self, date_element):
        """Handle date picker fields intelligently

        Args:
            date_element: Date picker element to handle

        Returns:
            True if date picker was handled successfully, False otherwise
        """
        try:
            # Try direct input first (many date pickers accept text input)
            # Use a date 2 weeks in the future
            future_date = (datetime.now() + timedelta(days=14)).strftime('%m/%d/%Y')
            date_element.clear()
            date_element.send_keys(future_date)
            print(f"Entered future date: {future_date}")

            # Check if a calendar popup appeared and needs to be closed
            try:
                calendar = self.driver.find_element(By.CSS_SELECTOR, '.calendar, .datepicker, .ui-datepicker')
                if calendar.is_displayed():
                    # Try clicking a date in the calendar
                    days = calendar.find_elements(By.CSS_SELECTOR, '.day, .ui-state-default')
                    if days:
                        # Click on a day that's not disabled
                        for day in days:
                            if 'disabled' not in day.get_attribute('class'):
                                day.click()
                                print("Selected date from calendar popup")
                                return True
            except Exception as e:
                print(f"No calendar popup found or error handling it: {e}")

            return True
        except Exception as e:
            print(f"Error handling date picker: {e}")
            return False

    def _identify_field_type(self, element) -> str:
        """Identify the type of form field with advanced heuristics and ML

        Args:
            element: Form field element

        Returns:
            Field type string
        """
        # Extract field attributes
        element_id = element.get_attribute('id') or ''
        element_name = element.get_attribute('name') or ''
        element_class = element.get_attribute('class') or ''
        element_type = element.get_attribute('type') or ''
        element_placeholder = element.get_attribute('placeholder') or ''
        element_tag = element.tag_name or ''

        # Try to find associated label
        element_label = ''
        if element_id:
            try:
                label_elements = self.driver.find_elements(By.CSS_SELECTOR, f'label[for="{element_id}"]')
                if label_elements and len(label_elements) > 0:
                    element_label = label_elements[0].text
            except:
                pass

        # Create field data dictionary for ML model
        field_data = {
            'id': element_id.lower(),
            'name': element_name.lower(),
            'class': element_class.lower(),
            'type': element_type.lower(),
            'placeholder': element_placeholder.lower(),
            'label': element_label.lower(),
            'tag_name': element_tag.lower(),
            'aria-label': element.get_attribute('aria-label') or ''
        }

        # First try machine learning model if available
        if self.field_classifier and self.field_classifier.is_trained:
            try:
                prediction = self.field_classifier.predict(field_data)
                confidence = max(self.field_classifier.predict_proba(field_data).values())

                if confidence > 0.7:
                    print(f"ML identified field as '{prediction}' with {confidence:.2f} confidence")
                    return prediction
                else:
                    print(f"ML prediction confidence too low ({confidence:.2f}), falling back to heuristics")
            except Exception as e:
                print(f"Error using ML for field identification: {e}")

        # Fall back to heuristic-based identification
        # Check for email fields
        if element_type == 'email' or 'email' in element_id or 'email' in element_name or 'email' in element_placeholder or 'email' in element_label:
            return 'email'

        # Check for name fields
        if element_type == 'text':
            # First name
            if any(indicator in text for indicator in ['first', 'firstname', 'first-name', 'first_name', 'fname']
                   for text in [element_id, element_name, element_placeholder, element_label]):
                return 'first_name'

            # Last name
            if any(indicator in text for indicator in ['last', 'lastname', 'last-name', 'last_name', 'lname', 'surname']
                   for text in [element_id, element_name, element_placeholder, element_label]):
                return 'last_name'

            # Full name
            if any(indicator in text for indicator in ['name', 'fullname', 'full-name', 'full_name', 'your-name']
                   for text in [element_id, element_name, element_placeholder, element_label]):
                return 'full_name'

        # Check for phone fields
        if element_type == 'tel' or any(indicator in text for indicator in ['phone', 'tel', 'telephone', 'mobile', 'cell']
                                       for text in [element_id, element_name, element_placeholder, element_label]):
            return 'phone'

        # Check for message/comment fields
        if element_tag == 'textarea' or any(indicator in text for indicator in ['message', 'comment', 'body', 'content', 'inquiry']
                                           for text in [element_id, element_name, element_placeholder, element_label]):
            return 'message'

        # Check for company fields
        if any(indicator in text for indicator in ['company', 'organization', 'business', 'employer']
               for text in [element_id, element_name, element_placeholder, element_label]):
            return 'company'

        # Check for subject fields
        if any(indicator in text for indicator in ['subject', 'topic', 'regarding', 're:']
               for text in [element_id, element_name, element_placeholder, element_label]):
            return 'subject'

        # Check for address fields
        if any(indicator in text for indicator in ['address', 'street', 'location']
               for text in [element_id, element_name, element_placeholder, element_label]):
            return 'address'

        # Check for date fields
        if element_type == 'date' or any(indicator in text for indicator in ['date', 'day', 'calendar']
                                        for text in [element_id, element_name, element_placeholder, element_label]):
            return 'date'

        # Check for time fields
        if element_type == 'time' or any(indicator in text for indicator in ['time', 'hour', 'clock']
                                        for text in [element_id, element_name, element_placeholder, element_label]):
            return 'time'

        # Check for checkbox fields
        if element_type == 'checkbox':
            return 'checkbox'

        # Check for radio fields
        if element_type == 'radio':
            return 'radio'

        # Check for dropdown fields
        if element_tag == 'select':
            return 'dropdown'

        # Check for submit buttons
        if element_type == 'submit' or (element_tag == 'button' and element_type != 'button') or 'submit' in element_id or 'submit' in element_class:
            return 'submit'

        # Default to unknown
        return 'unknown'

    def _find_parent_form(self, element):
        """Find the parent form of an element

        Args:
            element: Element to find parent form for

        Returns:
            Parent form element or None if not found
        """
        try:
            # Method 1: Use XPath to find parent form
            parent_form = element.find_element(By.XPATH, './ancestor::form')
            return parent_form
        except:
            # Method 2: Use JavaScript to find parent form
            try:
                parent_form = self.driver.execute_script("""
                    let element = arguments[0];
                    while (element && element.tagName !== 'FORM') {
                        element = element.parentElement;
                    }
                    return element;
                """, element)
                return parent_form
            except:
                return None

    def _find_contact_form(self, priority: str = 'balanced') -> Optional[Any]:
        """Find contact form on current page with enhanced detection

        Args:
            priority: Form detection priority ('strict', 'balanced', or 'aggressive')

        Returns:
            Contact form element or None if not found
        """
        # Update the processing stage in the status
        self._update_current_status({
            "current_contact_id": self.current_contact_id,
            "processing_stage": "finding_contact_form",
            "last_updated": datetime.now().isoformat()
        })

        # Use advanced form discovery if available
        if self.advanced_form_discovery:
            print("Using advanced form discovery to find contact form")
            form = self.advanced_form_discovery.find_contact_form()
            if form:
                print("Contact form found using advanced form discovery")
                return form
            else:
                print("Advanced form discovery could not find a contact form, falling back to basic methods")

        # Wait for page to fully load with timeout
        print(f"Waiting for page to fully load...")
        try:
            # Set a maximum wait time for page load
            start_time = time.time()
            max_load_time = 20  # Maximum 20 seconds to wait for page to be fully loaded

            # Wait for document ready state with timeout
            wait_time = 0
            while wait_time < max_load_time:
                # Check if page has loaded
                page_state = self.driver.execute_script('return document.readyState;')
                if page_state == 'complete':
                    print(f"Page fully loaded after {wait_time:.1f} seconds")
                    break

                # Sleep for a short interval
                time.sleep(1)
                wait_time = time.time() - start_time

                # Print progress every 5 seconds
                if wait_time % 5 < 1:
                    print(f"Still waiting for page to fully load... ({wait_time:.1f} seconds elapsed)")

            # Check if we timed out
            if wait_time >= max_load_time:
                print(f"⚠️ Page full load timed out after {max_load_time} seconds, but continuing anyway")

            # Additional wait for any JavaScript to initialize
            time.sleep(self.page_load_delay)
            print(f"Page loaded. Looking for contact form with enhanced detection...")

            # Print current URL for debugging
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")

            # Take a screenshot to see what page we're on
            self.driver.save_screenshot("page_before_form_search.png")
            print(f"Screenshot saved to page_before_form_search.png")

        except Exception as e:
            print(f"Warning: Error waiting for page to load: {e}")
            print("Continuing with form search anyway...")

        # First, check if we're already on a contact page
        current_url = self.driver.current_url.lower()
        if 'contact' in current_url:
            print(f"Already on a contact page: {current_url}")

        # Strategy 1: Look for forms with common contact form keywords
        try:
            # Take a screenshot of the page for debugging
            self.driver.save_screenshot("page_before_form_detection.png")

            # Print all forms on the page with their attributes for debugging
            print("Analyzing all forms on the page:")
            all_forms = self.driver.find_elements(By.TAG_NAME, "form")
            for i, form in enumerate(all_forms):
                try:
                    form_id = form.get_attribute('id') or 'no-id'
                    form_class = form.get_attribute('class') or 'no-class'
                    form_action = form.get_attribute('action') or 'no-action'
                    form_method = form.get_attribute('method') or 'no-method'
                    print(f"Form {i+1}/{len(all_forms)}: ID='{form_id}', Class='{form_class}', Action='{form_action}', Method='{form_method}'")

                    # Check if form has input fields
                    inputs = form.find_elements(By.TAG_NAME, "input")
                    textareas = form.find_elements(By.TAG_NAME, "textarea")
                    print(f"  - Contains {len(inputs)} inputs and {len(textareas)} textareas")

                    # Print details of input fields
                    for j, input_field in enumerate(inputs[:5]):  # Limit to first 5 for brevity
                        input_type = input_field.get_attribute('type') or 'no-type'
                        input_name = input_field.get_attribute('name') or 'no-name'
                        input_id = input_field.get_attribute('id') or 'no-id'
                        input_placeholder = input_field.get_attribute('placeholder') or 'no-placeholder'
                        print(f"    Input {j+1}: Type='{input_type}', Name='{input_name}', ID='{input_id}', Placeholder='{input_placeholder}'")
                except Exception as e:
                    print(f"Error analyzing form {i+1}: {e}")

            # Look for forms with contact-related IDs or classes
            strict_selectors = [
                "form[id*='contact' i]",
                "form[class*='contact' i]",
                "div[id*='contact' i] form",
                "div[class*='contact' i] form",
                "section[id*='contact' i] form",
                "section[class*='contact' i] form",
                "#contact form",
                ".contact form",
                "#contactForm",
                ".contactForm",
                "form[id*='form' i]",
                "form[class*='form' i]",
                "form[action*='contact' i]",
                "form[action*='form' i]",
                "form[action*='submit' i]",
                "form[action*='send' i]",
                "form[method='post']",
                "form.wpcf7-form",  # Common WordPress contact form
                "form.wpforms-form",  # WPForms
                "form.gform_wrapper",  # Gravity Forms
                "form.ninja-forms-form",  # Ninja Forms
                "form.elementor-form",  # Elementor forms
                "form.forminator-custom-form",  # Forminator forms
                "form.caldera-grid",  # Caldera forms
                "form.frm_forms",  # Formidable forms
                "form.hubspot-form",  # HubSpot forms
                "form.hs-form",  # Another HubSpot form class
                "form.mktoForm",  # Marketo forms
                "form.pardot-form",  # Pardot forms
                "form.form-horizontal",  # Bootstrap forms
                "form.form-inline",  # Bootstrap inline forms
                "form.contact-form",
                "form.contact_form",
                "form.contactForm",
                "form.contact-us-form",
                "form.inquiry-form",
                "form.get-in-touch",
                "form.reach-out"
            ]

            balanced_selectors = [
                "form:has(input[type='email'])",
                "form:has(textarea)",
                "form:has(input[name*='email' i])",
                "form:has(input[id*='email' i])",
                "form:has(input[placeholder*='email' i])",
                "div.contact",
                "section.contact",
                "div#contact",
                "section#contact",
                "div[id*='contact' i]",
                "div[class*='contact' i]",
                "section[id*='contact' i]",
                "section[class*='contact' i]",
                "div[id*='form' i]",
                "div[class*='form' i]",
                "section[id*='form' i]",
                "section[class*='form' i]",
                ".wpcf7",  # WordPress Contact Form 7 container
                ".wpforms-container",  # WPForms container
                ".gform_wrapper",  # Gravity Forms container
                ".ninja-forms-cont",  # Ninja Forms container
                ".elementor-form-fields-wrapper",  # Elementor form container
                ".forminator-ui",  # Forminator container
                ".caldera-grid",  # Caldera container
                ".frm_form_container",  # Formidable container
                ".hs_cos_wrapper",  # HubSpot container
                ".mktoForm",  # Marketo container
                ".pardot-form",  # Pardot container
                ".contact-form-container",
                ".contact-us-container",
                ".form-container",
                ".form-wrapper"
            ]

            aggressive_selectors = [
                "form",
                "div.footer form",
                "footer form",
                "div[class*='footer' i] form",
                "div[id*='footer' i] form",
                "div[class*='bottom' i] form",
                "div[id*='bottom' i] form",
                "div[class*='form' i]",
                "div[id*='form' i]",
                "div:has(input[type='email'])",
                "div:has(input[name*='email' i])",
                "div:has(input[id*='email' i])",
                "div:has(textarea)",
                "div:has(input[type='text'])",
                "div:has(button[type='submit'])",
                "div:has(input[type='submit'])"
            ]

            # Choose selectors based on priority
            contact_form_selectors = []
            if priority == 'strict':
                contact_form_selectors = strict_selectors
            elif priority == 'balanced':
                contact_form_selectors = strict_selectors + balanced_selectors
            elif priority == 'aggressive':
                contact_form_selectors = strict_selectors + balanced_selectors + aggressive_selectors
            else:  # Default to balanced
                contact_form_selectors = strict_selectors + balanced_selectors

            # Set a timeout for the entire form search process
            form_search_start_time = time.time()
            form_search_timeout = 60  # 60 seconds max for form search

            print(f"Starting contact form search with {len(contact_form_selectors)} selectors (timeout: {form_search_timeout}s)")

            # First, try to find a form
            for selector_index, selector in enumerate(contact_form_selectors):
                # Check if we've exceeded the timeout
                if time.time() - form_search_start_time > form_search_timeout:
                    print(f"⚠️ Form search timed out after {form_search_timeout} seconds. Tried {selector_index}/{len(contact_form_selectors)} selectors.")
                    break

                try:
                    print(f"Trying selector {selector_index+1}/{len(contact_form_selectors)}: {selector}")
                    forms = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if forms:
                        print(f"Found {len(forms)} potential forms with selector: {selector}")

                        # Prioritize forms that have email fields and textareas
                        for form_index, form in enumerate(forms):
                            try:
                                # Check if form is visible and interactable
                                if form.is_displayed():
                                    print(f"Form {form_index+1} is visible")

                                    # Try to find email field and textarea within this form
                                    email_fields = form.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name*='email'], input[id*='email'], input[placeholder*='email']")
                                    textareas = form.find_elements(By.TAG_NAME, "textarea")

                                    if email_fields and textareas:
                                        print(f"✅ Found ideal contact form with selector: {selector}")
                                        print(f"Form has {len(email_fields)} email fields and {len(textareas)} textareas")
                                        # Take a screenshot for debugging
                                        self.driver.save_screenshot("contact_form_found.png")

                                        # Use AI to analyze the form structure
                                        print("Using AI to analyze form structure...")
                                        custom_selectors = self._analyze_form_structure(form)
                                        print(f"AI analysis complete. Found {sum(len(selectors) for selectors in custom_selectors.values())} custom selectors")

                                        # Store the custom selectors in the form element using JavaScript
                                        self.driver.execute_script("""
                                            arguments[0].customSelectors = arguments[1];
                                        """, form, json.dumps(custom_selectors))

                                        return form
                                    else:
                                        print(f"Form has {len(email_fields)} email fields and {len(textareas)} textareas - not ideal")
                                else:
                                    print(f"Form {form_index+1} is not visible")
                            except Exception as e:
                                print(f"Error checking form elements: {e}")
                                continue

                        # If no ideal form found, return the first visible one
                        for form_index, form in enumerate(forms):
                            try:
                                if form.is_displayed():
                                    print(f"✅ Found potential contact form with selector: {selector}")
                                    # Take a screenshot for debugging
                                    self.driver.save_screenshot("contact_form_found.png")
                                    return form
                            except Exception as e:
                                print(f"Error checking if form {form_index+1} is displayed: {e}")
                                continue
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue

            # Strategy 2: Look for contact page links and navigate to them
            # Only if navigate_to_contact_page setting is enabled and we haven't found a form yet
            if self.settings.get('navigate_to_contact_page', True):
                print("Looking for contact page links...")
                contact_link_selectors = [
                    "a[href*='contact']",
                    "a:contains('Contact')",
                    "a:contains('contact')",
                    "a[href*='Contact']",
                    "a.contact",
                    "a#contact",
                    "li.contact a",
                    "nav a[href*='contact']",
                    ".menu a[href*='contact']"
                ]

                # Set a timeout for contact link search
                link_search_start_time = time.time()
                link_search_timeout = 30  # 30 seconds max for link search

                print(f"Starting contact link search with {len(contact_link_selectors)} selectors (timeout: {link_search_timeout}s)")

                for selector_index, selector in enumerate(contact_link_selectors):
                    # Check if we've exceeded the timeout
                    if time.time() - link_search_start_time > link_search_timeout:
                        print(f"⚠️ Contact link search timed out after {link_search_timeout} seconds. Tried {selector_index}/{len(contact_link_selectors)} selectors.")
                        break

                    try:
                        print(f"Trying link selector {selector_index+1}/{len(contact_link_selectors)}: {selector}")

                        # Use JavaScript to find links with text containing 'contact'
                        if 'contains' in selector:
                            text = selector.split("'")[1]
                            links = self.driver.execute_script(f"""
                                return Array.from(document.querySelectorAll('a')).filter(a =>
                                    a.textContent.toLowerCase().includes('{text.lower()}')
                                );
                            """)
                        else:
                            links = self.driver.find_elements(By.CSS_SELECTOR, selector)

                        if links:
                            print(f"Found {len(links)} potential contact links with selector: {selector}")

                            for link_index, link in enumerate(links):
                                # Check if we've exceeded the timeout
                                if time.time() - link_search_start_time > link_search_timeout:
                                    print(f"⚠️ Contact link processing timed out after {link_search_timeout} seconds.")
                                    break

                                try:
                                    if link.is_displayed():
                                        href = link.get_attribute('href')
                                        link_text = link.text.strip()
                                        print(f"Found visible contact link {link_index+1}/{len(links)}: {link_text} -> {href}")

                                        # Don't click if it's an email link
                                        if href and href.startswith('mailto:'):
                                            print("Skipping email link")
                                            continue

                                        # Save current URL to avoid loops
                                        current_url = self.driver.current_url

                                        # Click the link
                                        print(f"Clicking contact link: {link_text}")
                                        link.click()

                                        # Wait for page to load with timeout
                                        page_load_start = time.time()
                                        max_page_load_wait = 10  # 10 seconds max

                                        while time.time() - page_load_start < max_page_load_wait:
                                            # Check if page has loaded
                                            page_state = self.driver.execute_script('return document.readyState;')
                                            if page_state == 'complete':
                                                print(f"Contact page loaded after {time.time() - page_load_start:.1f} seconds")
                                                break
                                            time.sleep(0.5)

                                        # Additional wait based on speed setting
                                        time.sleep(self.page_load_delay)

                                        # Check if URL changed
                                        new_url = self.driver.current_url
                                        if new_url != current_url:
                                            print(f"Successfully navigated to: {new_url}")

                                            # Take a screenshot of the contact page
                                            self.driver.save_screenshot(f"contact_page_{link_index+1}.png")
                                            print(f"Screenshot saved to contact_page_{link_index+1}.png")

                                            # Try to find form on contact page with same priority
                                            print("Looking for contact form on contact page...")
                                            form = self._find_contact_form(priority)
                                            if form:
                                                print("✅ Found contact form on contact page!")
                                                return form
                                            else:
                                                # Go back if no form found
                                                print("No form found on contact page, going back")
                                                self.driver.back()

                                                # Wait for page to load after going back
                                                back_start = time.time()
                                                while time.time() - back_start < 5:  # 5 seconds max
                                                    page_state = self.driver.execute_script('return document.readyState;')
                                                    if page_state == 'complete':
                                                        break
                                                    time.sleep(0.5)

                                                time.sleep(self.page_load_delay)
                                        else:
                                            print(f"URL did not change after clicking contact link")
                                    else:
                                        print(f"Link {link_index+1} is not visible")
                                except Exception as e:
                                    print(f"Error clicking contact link {link_index+1}: {e}")
                                    continue
                        else:
                            print(f"No links found with selector: {selector}")
                    except Exception as e:
                        print(f"Error with link selector {selector}: {e}")
                        continue

            # Strategy 3: Try to find iframe with contact form
            print("Looking for iframes with contact forms...")

            # Set a timeout for iframe search
            iframe_search_start_time = time.time()
            iframe_search_timeout = 30  # 30 seconds max for iframe search

            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    print(f"Found {len(iframes)} iframes, checking each for contact forms (timeout: {iframe_search_timeout}s)")

                    # Save current URL to restore if needed
                    current_url = self.driver.current_url

                    for i, iframe in enumerate(iframes):
                        # Check if we've exceeded the timeout
                        if time.time() - iframe_search_start_time > iframe_search_timeout:
                            print(f"⚠️ Iframe search timed out after {iframe_search_timeout} seconds. Checked {i}/{len(iframes)} iframes.")
                            break

                        try:
                            # Switch to iframe
                            self.driver.switch_to.frame(iframe)
                            print(f"Switched to iframe {i+1}/{len(iframes)}")

                            # Look for forms in iframe
                            iframe_forms = self.driver.find_elements(By.TAG_NAME, "form")
                            if iframe_forms:
                                print(f"Found {len(iframe_forms)} forms in iframe {i+1}")

                                # Check if any forms have email fields and textareas
                                for form_index, form in enumerate(iframe_forms):
                                    try:
                                        # Check if form is visible
                                        if form.is_displayed():
                                            print(f"Form {form_index+1} in iframe {i+1} is visible")

                                            # Try to find email field and textarea within this form
                                            email_fields = form.find_elements(By.CSS_SELECTOR, "input[type='email'], input[name*='email'], input[id*='email'], input[placeholder*='email']")
                                            textareas = form.find_elements(By.TAG_NAME, "textarea")

                                            if email_fields and textareas:
                                                print(f"✅ Found ideal contact form in iframe {i+1}")
                                                # Take a screenshot for debugging
                                                self.driver.save_screenshot(f"iframe_{i+1}_form_{form_index+1}.png")
                                                return form
                                    except Exception as form_error:
                                        print(f"Error checking form {form_index+1} in iframe {i+1}: {form_error}")
                                        continue

                                # If no ideal form found, return the first visible one
                                for form_index, form in enumerate(iframe_forms):
                                    try:
                                        if form.is_displayed():
                                            print(f"✅ Found potential contact form in iframe {i+1}")
                                            # Take a screenshot for debugging
                                            self.driver.save_screenshot(f"iframe_{i+1}_form_{form_index+1}.png")
                                            return form
                                    except Exception as form_error:
                                        print(f"Error checking if form {form_index+1} in iframe {i+1} is displayed: {form_error}")
                                        continue
                            else:
                                print(f"No forms found in iframe {i+1}")

                            # Switch back to main content
                            self.driver.switch_to.default_content()
                        except Exception as e:
                            print(f"Error checking iframe {i+1}: {e}")
                            # Make sure we get back to main content
                            try:
                                self.driver.switch_to.default_content()
                            except:
                                pass
                            continue
                else:
                    print("No iframes found on the page")
            except Exception as e:
                print(f"Error checking iframes: {e}")
                # Make sure we get back to main content
                try:
                    self.driver.switch_to.default_content()
                except:
                    pass

            print("No contact form found with any strategy")
            # Take a screenshot of the page for debugging
            self.driver.save_screenshot("no_contact_form.png")
            return None

        except Exception as e:
            print(f"Error finding contact form: {e}")
            # Take a screenshot for debugging
            self.driver.save_screenshot("error_finding_form.png")
            return None

    def _is_contact_form7(self, form_element) -> bool:
        """Check if the form is a WordPress Contact Form 7 form

        Args:
            form_element: Form element to check

        Returns:
            True if the form is a Contact Form 7 form, False otherwise
        """
        try:
            # Check for common Contact Form 7 indicators
            form_class = form_element.get_attribute('class') or ''
            form_id = form_element.get_attribute('id') or ''
            form_action = form_element.get_attribute('action') or ''

            # Check for wpcf7 class or ID
            if 'wpcf7-form' in form_class or 'wpcf7' in form_id:
                print("✅ Detected WordPress Contact Form 7 form by class/ID")
                return True

            # Check for wpcf7 in the form's parent elements
            parent_has_wpcf7 = self.driver.execute_script("""
                let element = arguments[0];
                let parent = element.parentElement;
                while (parent) {
                    if (parent.className && parent.className.includes('wpcf7')) {
                        return true;
                    }
                    parent = parent.parentElement;
                }
                return false;
            """, form_element)

            if parent_has_wpcf7:
                print("✅ Detected WordPress Contact Form 7 form by parent element")
                return True

            # Check for typical Contact Form 7 field naming patterns
            cf7_field_patterns = ['your-name', 'your-email', 'your-message', 'your-subject', 'your-phone']
            for pattern in cf7_field_patterns:
                fields = form_element.find_elements(By.CSS_SELECTOR, f"[name='{pattern}']")
                if fields:
                    print(f"✅ Detected WordPress Contact Form 7 form by field name pattern: {pattern}")
                    return True

            return False
        except Exception as e:
            print(f"Error checking if form is Contact Form 7: {e}")
            return False

    def _fill_contact_form7(self, form_element, contact_data: Dict[str, Any]) -> tuple[bool, str]:
        """Specialized handler for WordPress Contact Form 7 forms

        Args:
            form_element: Contact Form 7 form element
            contact_data: Contact data

        Returns:
            Tuple of (success, message)
        """
        print("Using specialized Contact Form 7 form handler")

        # Take a screenshot before filling
        self.driver.save_screenshot("before_filling_cf7_form.png")

        # Get user information from settings
        first_name = self.settings.get('your_first_name', '')
        last_name = self.settings.get('your_last_name', '')
        name = (self.settings.get('your_name', '') or
               (f"{first_name} {last_name}" if first_name and last_name else "") or
               "Your Name")
        email = self.settings.get('your_email', '') or "contact@example.com"
        phone = self.settings.get('phone', '') or "555-123-4567"
        company = self.settings.get('your_company', '') or "Your Company"

        # Prepare message
        message = "I'm interested in learning more about your services. Please contact me at your earliest convenience."
        if self.contact_form_template:
            message = self._generate_message(contact_data)

        # Log the data we're using
        print(f"CF7 Form - Using data: Name='{name}', Email='{email}', Phone='{phone}', Company='{company}'")

        # Store the form data in the submission log
        self.submission_log["form_data"] = {
            "name": name,
            "email": email,
            "company": company,
            "phone": phone,
            "message": message
        }

        # Track filled fields
        filled_fields = []
        fields_attempted = []

        # Common Contact Form 7 field names
        cf7_field_mapping = {
            'your-name': name,
            'your-firstname': first_name or name.split()[0] if name and ' ' in name else name,
            'your-lastname': last_name or name.split()[-1] if name and ' ' in name else '',
            'your-email': email,
            'your-phone': phone,
            'your-tel': phone,
            'your-subject': "Inquiry",
            'your-message': message,
            'your-company': company,
            'your-address': "123 Main St",
            'your-city': "New York",
            'your-state': "NY",
            'your-zip': "10001",
            'your-country': "USA",
            'your-website': "example.com"
        }

        # Find and fill all fields
        success = False
        try:
            # Find all input fields and textareas in the form
            input_fields = form_element.find_elements(By.CSS_SELECTOR, "input:not([type='submit']):not([type='button']):not([type='hidden']), textarea, select")

            print(f"Found {len(input_fields)} input fields in Contact Form 7 form")

            for field in input_fields:
                try:
                    field_name = field.get_attribute('name')
                    field_type = field.get_attribute('type')
                    field_tag = field.tag_name

                    if not field_name:
                        continue

                    fields_attempted.append(field_name)
                    print(f"Processing CF7 field: name='{field_name}', type='{field_type}', tag='{field_tag}'")

                    # Check if this is a known CF7 field
                    value = None
                    for cf7_name, cf7_value in cf7_field_mapping.items():
                        if field_name == cf7_name or field_name.startswith(cf7_name):
                            value = cf7_value
                            break

                    # If not a known field, try to determine type
                    if value is None:
                        # Check for common patterns
                        if 'name' in field_name.lower():
                            value = name
                        elif 'email' in field_name.lower():
                            value = email
                        elif 'phone' in field_name.lower() or 'tel' in field_name.lower():
                            value = phone
                        elif 'company' in field_name.lower() or 'business' in field_name.lower():
                            value = company
                        elif 'message' in field_name.lower() or 'comment' in field_name.lower():
                            value = message
                        elif field_tag == 'textarea':
                            value = message
                        elif field_type == 'email':
                            value = email
                        elif field_type == 'tel':
                            value = phone
                        else:
                            # Try to intelligently guess the field type based on field name
                            field_name_lower = field_name.lower()

                            # Check if it might be a name field
                            if any(name_hint in field_name_lower for name_hint in ['name', 'author', 'person', 'who']):
                                print(f"Field '{field_name}' looks like a name field, using name value")
                                value = name
                            # Check if it might be a phone field
                            elif any(phone_hint in field_name_lower for phone_hint in ['phone', 'tel', 'mobile', 'cell']):
                                print(f"Field '{field_name}' looks like a phone field, using phone value")
                                value = phone
                            # Check if it might be an email field
                            elif any(email_hint in field_name_lower for email_hint in ['email', 'mail']):
                                print(f"Field '{field_name}' looks like an email field, using email value")
                                value = email
                            # Check if it might be a company field
                            elif any(company_hint in field_name_lower for company_hint in ['company', 'business', 'organization', 'firm']):
                                print(f"Field '{field_name}' looks like a company field, using company value")
                                value = company
                            # Check if it might be a message field
                            elif any(message_hint in field_name_lower for message_hint in ['message', 'comment', 'feedback', 'inquiry']):
                                print(f"Field '{field_name}' looks like a message field, using message value")
                                value = message
                            else:
                                # For truly unknown fields, use a more reasonable default based on field type
                                if field_tag == 'textarea':
                                    print(f"Unknown textarea field '{field_name}', using message as default")
                                    value = message
                                elif field_type == 'text' or field_type == '':
                                    # For text inputs, try to use name as a reasonable default
                                    print(f"Unknown text field '{field_name}', using name as default")
                                    value = name
                                else:
                                    # Only use N/A as a last resort
                                    print(f"Completely unknown field '{field_name}', using 'N/A' as default")
                                    value = "N/A"

                    # Fill the field based on its type
                    if field_tag == 'select':
                        # For select elements, choose the second option (first is often a placeholder)
                        self.driver.execute_script("""
                            const select = arguments[0];
                            if (select.options.length > 1) {
                                select.selectedIndex = 1;
                                const event = new Event('change', { bubbles: true });
                                select.dispatchEvent(event);
                            } else if (select.options.length > 0) {
                                select.selectedIndex = 0;
                                const event = new Event('change', { bubbles: true });
                                select.dispatchEvent(event);
                            }
                        """, field)
                        print(f"Selected an option from dropdown {field_name}")
                        filled_fields.append({"type": field_name, "value": "Selected option"})
                    elif field_type == 'checkbox':
                        if not field.is_selected():
                            field.click()
                        print(f"Checked checkbox {field_name}")
                        filled_fields.append({"type": field_name, "value": "Checked"})
                    elif field_type == 'radio':
                        if not field.is_selected():
                            field.click()
                        print(f"Selected radio button {field_name}")
                        filled_fields.append({"type": field_name, "value": "Selected"})
                    elif field_type == 'date':
                        today = time.strftime('%Y-%m-%d')
                        self.driver.execute_script("arguments[0].value = arguments[1]", field, today)
                        print(f"Set date field {field_name} to today's date")
                        filled_fields.append({"type": field_name, "value": today})
                    else:
                        # Text input or textarea
                        field.clear()
                        field.send_keys(value)
                        print(f"Filled field {field_name} with '{value}'")
                        filled_fields.append({"type": field_name, "value": value})

                except Exception as e:
                    print(f"Error filling CF7 field {field_name if 'field_name' in locals() else 'unknown'}: {e}")
                    continue

            # Update submission log
            self.submission_log["fields_filled"] = filled_fields
            self.submission_log["fields_attempted"] = fields_attempted

            # Find and click submit button
            submit_buttons = form_element.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], .wpcf7-submit")

            if submit_buttons:
                print(f"Found {len(submit_buttons)} submit buttons in CF7 form")

                # Check if form submission is enabled in settings
                submit_form = self.settings.get('submit_form', True)
                if not submit_form:
                    print("⚠️ Form submission is disabled in settings. Form filled but not submitted.")
                    self.submission_log["form_submitted"] = False
                    self.submission_log["submission_result"] = "Form filled but not submitted (submit_form setting is disabled)"
                    # Take a screenshot of the filled form
                    self.driver.save_screenshot("form_filled_not_submitted_cf7.png")
                    return True, "Form filled successfully but not submitted (submit_form setting is disabled)"

                # Click the first submit button
                try:
                    submit_buttons[0].click()
                    print("Clicked CF7 form submit button")

                    # Wait for form submission
                    time.sleep(3)

                    # Check for success message
                    success_elements = self.driver.find_elements(By.CSS_SELECTOR, ".wpcf7-mail-sent-ok, .wpcf7-response-output:not(.wpcf7-validation-errors)")

                    if success_elements:
                        for element in success_elements:
                            if element.is_displayed():
                                success_text = element.text.strip()
                                print(f"✅ CF7 form submitted successfully: {success_text}")
                                self.submission_log["form_submitted"] = True
                                self.submission_log["submission_result"] = f"Success - {success_text}"
                                return True, f"Form submitted successfully: {success_text}"

                    # Check for validation errors
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".wpcf7-validation-errors, .wpcf7-not-valid-tip")

                    if error_elements:
                        for element in error_elements:
                            if element.is_displayed():
                                error_text = element.text.strip()
                                print(f"❌ CF7 form validation error: {error_text}")
                                self.submission_log["form_submitted"] = False
                                self.submission_log["submission_result"] = f"Failed - Validation error: {error_text}"
                                return False, f"Form validation error: {error_text}"

                    # If no clear success or error message, assume success
                    print("⚠️ No clear CF7 form submission result, assuming success")
                    self.submission_log["form_submitted"] = True
                    self.submission_log["submission_result"] = "Uncertain - No clear submission result"
                    return True, "Form submitted but no clear confirmation"

                except Exception as e:
                    print(f"Error clicking CF7 form submit button: {e}")
                    self.submission_log["form_submitted"] = False
                    self.submission_log["submission_result"] = f"Failed - Error clicking submit button: {str(e)}"
                    return False, f"Error clicking submit button: {str(e)}"
            else:
                print("❌ No submit button found in CF7 form")
                self.submission_log["form_submitted"] = False
                self.submission_log["submission_result"] = "Failed - No submit button found"
                return False, "No submit button found"

        except Exception as e:
            print(f"Error filling Contact Form 7 form: {e}")
            self.submission_log["form_submitted"] = False
            self.submission_log["submission_result"] = f"Failed - Exception: {str(e)}"
            return False, f"Error filling form: {str(e)}"

    def _fill_contact_form(self, contact: Dict[str, Any], strategy: str = "standard", attempt: int = 1) -> tuple[bool, str]:
        """Fill and submit contact form with enhanced intelligence

        Args:
            contact: Contact data
            strategy: Strategy to use ('standard_with_ai', 'aggressive', 'javascript_fallback')
            attempt: Current attempt number

        Returns:
            Tuple of (success, message)
        """
        # Create a submission log dictionary to track what was submitted
        self.submission_log = {
            "contact_id": self.current_contact_id,
            "timestamp": datetime.now().isoformat(),
            "website": self.driver.current_url,
            "fields_filled": [],
            "fields_attempted": [],
            "fields_failed": [],
            "form_submitted": False,
            "submission_result": "Not attempted",
            "form_data": {}
        }

        try:
            # Update the processing stage in the status
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "filling_form",
                "last_updated": datetime.now().isoformat()
            })

            print("Attempting to fill contact form...")
            # Take a screenshot before filling
            self.driver.save_screenshot("before_filling_form.png")

            # Check if this is a WordPress Contact Form 7 form
            form_element = self.driver.find_element(By.TAG_NAME, "form")

            # Check if we have custom selectors from AI analysis
            custom_selectors = None
            try:
                custom_selectors_json = self.driver.execute_script("return arguments[0].customSelectors;", form_element)
                if custom_selectors_json:
                    custom_selectors = json.loads(custom_selectors_json)
                    print(f"Found custom selectors from AI analysis: {custom_selectors}")
            except Exception as e:
                print(f"Error retrieving custom selectors: {e}")

            if self._is_contact_form7(form_element):
                print("Detected WordPress Contact Form 7 form, using specialized handler")
                return self._fill_contact_form7(form_element, contact)

            # Get contact data with fallbacks for different field names
            # Print all contact data for debugging
            print("Available contact data fields:")
            for key, value in contact.items():
                print(f"  {key}: {value}")

            # Use the user's information from settings for filling out contact forms
            # Get first name and last name from settings
            first_name = self.settings.get('your_first_name', '')
            last_name = self.settings.get('your_last_name', '')

            # Use full name from settings or combine first and last name
            name = (self.settings.get('your_name', '') or
                   (f"{first_name} {last_name}" if first_name and last_name else "") or
                   "Your Name")

            # Get email from settings
            settings_email = self.settings.get('your_email', '')
            email = settings_email or "contact@example.com"

            # Get company from settings
            company = self.settings.get('your_company', '') or "Your Company"

            # Get phone from settings
            phone = self.settings.get('phone', '') or "555-123-4567"

            # Log that we're using the user's information from settings
            print(f"Using user's information from settings for contact form:")
            print(f"  Name: {name}")
            print(f"  Email: {email}")
            print(f"  Company: {company}")
            print(f"  Phone: {phone}")

            # Log the data we're using
            print(f"Using contact data: Name='{name}', Email='{email}', Company='{company}', Phone='{phone}'")

            # Store the form data in the submission log
            self.submission_log["form_data"] = {
                "name": name,
                "email": email,
                "company": company,
                "phone": phone
            }

            # Validate email format
            if "@" not in email or "." not in email:
                print(f"Warning: Email '{email}' appears to be invalid. Using settings email or fallback.")
                email = settings_email if settings_email and "@" in settings_email and "." in settings_email else "contact@example.com"
                print(f"Using email: {email}")
                self.submission_log["form_data"]["email"] = email  # Update the log with the corrected email

            # Prepare message using template if available
            message = "I'm interested in learning more about your services. Please contact me at your earliest convenience."
            if self.contact_form_template:
                print(f"Using custom message template: '{self.contact_form_template}'")
                # Use the _generate_message method for consistent template handling
                message = self._generate_message(contact)
                # Log the full message content for debugging
                print(f"Generated message from template: '{message}'")
            else:
                print("No custom message template found, using default message")

            # Store the message in the submission log
            self.submission_log["form_data"]["message"] = message

            print(f"Form data prepared: Name={name}, Company={company}, Message length={len(message)}")
            print(f"Message content: '{message}'")

            # Create a detailed log entry for this form submission attempt
            log_entry = f"""
==========================================================
📝 FORM SUBMISSION ATTEMPT - CONTACT ID: {self.current_contact_id}
==========================================================
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Website: {self.driver.current_url}
👤 Contact: {name}
🏢 Company: {company}
📧 Email: {email}
📞 Phone: {phone}
📝 Message: {message[:100]}{'...' if len(message) > 100 else ''}
🔄 Strategy: {strategy}
🔢 Attempt: {attempt}
==========================================================
"""
            print(log_entry)

            # Also log to the logger if available
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(log_entry)

            # Common field identifiers - expanded with more variations
            # Full name selectors - expanded with more variations
            name_selectors = [
                # Generic name selectors with case insensitivity
                "input[name*='name' i]:not([name*='first' i]):not([name*='last' i]):not([name*='user' i])",
                "input[id*='name' i]:not([id*='first' i]):not([id*='last' i]):not([id*='user' i])",
                "input[placeholder*='name' i]:not([placeholder*='first' i]):not([placeholder*='last' i])",
                "input[class*='name' i]:not([class*='first' i]):not([class*='last' i])",
            ]

            # If using aggressive strategy, add more selectors
            if strategy == "aggressive":
                print("Using expanded selectors for aggressive form filling")
                # Add more aggressive selectors for name fields
                aggressive_name_selectors = [
                    # Try any input that might be a name field
                    "input:not([type='hidden']):not([type='submit']):not([type='checkbox']):not([type='radio'])",
                    "input[type='text']",
                    # Try inputs near labels with name-related text
                    "label:contains('Name'), label:contains('name') + input",
                    "label:contains('Name'), label:contains('name') ~ input",
                    # Try the first visible text input as a fallback
                    "form input[type='text']:first-child",
                    # Try inputs with common name-related attributes
                    "input[name*='contact' i]",
                    "input[id*='contact' i]",
                    "input[name*='author' i]",
                    "input[id*='author' i]",
                    # Try inputs with any name-related class
                    "input[class*='input' i]",
                    "input[class*='field' i]",
                    "input[class*='text' i]",
                    # Try inputs with any name-related aria attributes
                    "input[aria-label*='name' i]",
                    "input[aria-labelledby*='name' i]",
                    "input[aria-describedby*='name' i]",
                ]
                # Add these to the beginning of the selectors list for priority
                name_selectors = aggressive_name_selectors + name_selectors

            # Filter out empty selectors
            name_selectors = [selector for selector in name_selectors if selector and not selector.endswith("''")]

            # First name selectors - expanded with more variations
            first_name_selectors = [
                # Generic first name selectors with case insensitivity
                "input[name*='first' i]",
                "input[id*='first' i]",
                "input[placeholder*='first' i]",
                "input[class*='first' i]",

                # Required field indicators
                "input[required][name*='first' i]",
                "input[required][id*='first' i]",
                "input[required][placeholder*='first' i]",
                "input[aria-required='true'][name*='first' i]",
                "input[aria-required='true'][id*='first' i]",

                # Fields with asterisk in label (common for required fields)
                "input[id$='-first-name']",
                "input[name$='-first-name']",
                "input[id$='_first_name']",
                "input[name$='_first_name']",

                # Common first name field identifiers
                "input[name='f_name']",
                "input[name='fname']",
                "input[id='fname']",
                "input[name='firstname']",
                "input[id='firstname']",
                "input[name='first_name']",
                "input[id='first_name']",
                "input[name='form_fields[first_name]']",
                "input[name='firstName']",
                "input[id='firstName']",
                "input[name='first-name']",
                "input[id='first-name']",
                "input[name='given-name']",
                "input[id='given-name']",
                "input[name='givenName']",
                "input[id='givenName']",
                "input[name='wpforms[fields][0][first]']",

                # Dato CMS form fields (used on floridassmiles.com)
                "input[name='first-name']",
                "input[id='first-name']",
                "input[name='firstName']",
                "input[id='firstName']",
                "input[name='first_name']",
                "input[id='first_name']",

                # Try input fields with first name-related placeholders
                "input[placeholder='First Name']",
                "input[placeholder='First Name*']",
                "input[placeholder='First']",
                "input[placeholder='Given Name']",

                # Try any input with required attribute and first name text
                "input[required][placeholder*='first' i]",

                # Try label-based selectors using JavaScript
                "input#" + self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        if ((label.textContent.toLowerCase().includes('first') ||
                             label.textContent.toLowerCase().includes('given')) &&
                            label.htmlFor) {
                            return label.htmlFor;
                        }
                    }
                    return '';
                """),

                # Try finding inputs with labels containing "First Name"
                self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        const text = label.textContent.trim().toLowerCase();
                        if ((text.includes('first name') || text === 'first name*') && label.htmlFor) {
                            return '#' + label.htmlFor;
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            first_name_selectors = [selector for selector in first_name_selectors if selector and not selector.endswith("''")]

            # Last name selectors - expanded with more variations
            last_name_selectors = [
                # Generic last name selectors with case insensitivity
                "input[name*='last' i]",
                "input[id*='last' i]",
                "input[placeholder*='last' i]",
                "input[class*='last' i]",

                # Required field indicators
                "input[required][name*='last' i]",
                "input[required][id*='last' i]",
                "input[required][placeholder*='last' i]",
                "input[aria-required='true'][name*='last' i]",
                "input[aria-required='true'][id*='last' i]",

                # Fields with asterisk in label (common for required fields)
                "input[id$='-last-name']",
                "input[name$='-last-name']",
                "input[id$='_last_name']",
                "input[name$='_last_name']",

                # Common last name field identifiers
                "input[name='l_name']",
                "input[name='lname']",
                "input[id='lname']",
                "input[name='lastname']",
                "input[id='lastname']",
                "input[name='last_name']",
                "input[id='last_name']",
                "input[name='form_fields[last_name]']",
                "input[name='lastName']",
                "input[id='lastName']",
                "input[name='last-name']",
                "input[id='last-name']",
                "input[name='family-name']",
                "input[id='family-name']",
                "input[name='familyName']",
                "input[id='familyName']",
                "input[name='surname']",
                "input[id='surname']",
                "input[name='wpforms[fields][0][last]']",

                # Dato CMS form fields (used on floridassmiles.com)
                "input[name='last-name']",
                "input[id='last-name']",
                "input[name='lastName']",
                "input[id='lastName']",
                "input[name='last_name']",
                "input[id='last_name']",

                # Try input fields with last name-related placeholders
                "input[placeholder='Last Name']",
                "input[placeholder='Last Name*']",
                "input[placeholder='Last']",
                "input[placeholder='Family Name']",
                "input[placeholder='Surname']",

                # Try any input with required attribute and last name text
                "input[required][placeholder*='last' i]",

                # Try label-based selectors using JavaScript
                "input#" + self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        if ((label.textContent.toLowerCase().includes('last') ||
                             label.textContent.toLowerCase().includes('family') ||
                             label.textContent.toLowerCase().includes('surname')) &&
                            label.htmlFor) {
                            return label.htmlFor;
                        }
                    }
                    return '';
                """),

                # Try finding inputs with labels containing "Last Name"
                self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        const text = label.textContent.trim().toLowerCase();
                        if ((text.includes('last name') || text === 'last name*') && label.htmlFor) {
                            return '#' + label.htmlFor;
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            last_name_selectors = [selector for selector in last_name_selectors if selector and not selector.endswith("''")]

            # Email selectors - expanded with more variations
            email_selectors = [
                # Generic email selectors with case insensitivity
                "input[type='email']",
                "input[name*='email' i]",
                "input[id*='email' i]",
                "input[placeholder*='email' i]",
                "input[class*='email' i]",

                # Required field indicators
                "input[required][type='email']",
                "input[required][name*='email' i]",
                "input[required][id*='email' i]",
                "input[required][placeholder*='email' i]",
                "input[aria-required='true'][type='email']",
                "input[aria-required='true'][name*='email' i]",
                "input[aria-required='true'][id*='email' i]",

                # Fields with asterisk in label (common for required fields)
                "input[id$='-email']",
                "input[name$='-email']",
                "input[id$='_email']",
                "input[name$='_email']",

                # Common email field identifiers
                "input.email",
                "#email",
                "input[name='your-email']",
                "input[name='form_fields[email]']",
                "input[name='e-mail']",
                "input[id='e-mail']",
                "input[name='e_mail']",
                "input[id='e_mail']",
                "input[name='mail']",
                "input[id='mail']",
                "input[name='emailaddress']",
                "input[id='emailaddress']",
                "input[name='email_address']",
                "input[id='email_address']",
                "input[name='email-address']",
                "input[id='email-address']",
                "input[name='emailAddress']",
                "input[id='emailAddress']",
                "input[name='wpforms[fields][1]']",  # Common in WPForms

                # Dato CMS form fields (used on floridassmiles.com)
                "input[name='email']",
                "input[id='email']",
                "input[name='email-address']",
                "input[id='email-address']",

                # Try input fields with email-related placeholders
                "input[placeholder='Email']",
                "input[placeholder='Email*']",
                "input[placeholder='Email Address']",
                "input[placeholder='Email Address*']",
                "input[placeholder='Your Email']",
                "input[placeholder='Your Email*']",
                "input[placeholder='E-mail']",
                "input[placeholder='E-mail*']",

                # Try any input with required attribute and email text
                "input[required][placeholder*='email' i]",

                # Try label-based selectors using JavaScript
                "input#" + self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        if (label.textContent.toLowerCase().includes('email') &&
                            label.htmlFor) {
                            return label.htmlFor;
                        }
                    }
                    return '';
                """),

                # Try finding inputs with labels containing "Email"
                self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        const text = label.textContent.trim().toLowerCase();
                        if ((text.includes('email') || text === 'email*') && label.htmlFor) {
                            return '#' + label.htmlFor;
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            email_selectors = [selector for selector in email_selectors if selector and not selector.endswith("''")]

            # Message selectors - expanded with more variations
            message_selectors = [
                # Generic message selectors with case insensitivity
                "textarea[name*='message' i]",
                "textarea[id*='message' i]",
                "textarea[placeholder*='message' i]",
                "textarea[class*='message' i]",

                # Common message field identifiers
                "textarea.message",
                "#message",
                "textarea[name='your-message']",
                "textarea[name='form_fields[message]']",
                "textarea[name='comment']",
                "textarea[id='comment']",
                "textarea[name='comments']",
                "textarea[id='comments']",
                "textarea[name='content']",
                "textarea[id='content']",
                "textarea[name='description']",
                "textarea[id='description']",
                "textarea[name='inquiry']",
                "textarea[id='inquiry']",
                "textarea[name='wpforms[fields][2]']",  # Common in WPForms

                # Try textarea fields with message-related placeholders
                "textarea[placeholder*='message' i]",
                "textarea[placeholder*='comment' i]",
                "textarea[placeholder*='question' i]",
                "textarea[placeholder*='inquiry' i]",
                "textarea[placeholder*='tell us' i]",
                "textarea[placeholder*='how can we' i]",

                # Try any textarea as a fallback
                "textarea",

                # Some forms use contenteditable divs
                "div[contenteditable='true']",

                # Try label-based selectors using JavaScript
                "textarea#" + self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        if ((label.textContent.toLowerCase().includes('message') ||
                             label.textContent.toLowerCase().includes('comment') ||
                             label.textContent.toLowerCase().includes('inquiry') ||
                             label.textContent.toLowerCase().includes('question')) &&
                            label.htmlFor) {
                            return label.htmlFor;
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            message_selectors = [selector for selector in message_selectors if selector and not selector.endswith("''")]

            # Phone selectors - expanded with more variations
            phone_selectors = [
                # Generic phone selectors with case insensitivity
                "input[type='tel']",
                "input[name*='phone' i]",
                "input[id*='phone' i]",
                "input[placeholder*='phone' i]",
                "input[class*='phone' i]",
                "input[name*='tel' i]",
                "input[id*='tel' i]",

                # Required field indicators
                "input[required][type='tel']",
                "input[required][name*='phone' i]",
                "input[required][id*='phone' i]",
                "input[required][placeholder*='phone' i]",
                "input[aria-required='true'][type='tel']",
                "input[aria-required='true'][name*='phone' i]",
                "input[aria-required='true'][id*='phone' i]",

                # Fields with asterisk in label (common for required fields)
                "input[id$='-phone']",
                "input[name$='-phone']",
                "input[id$='_phone']",
                "input[name$='_phone']",

                # Common phone field identifiers
                "input.phone",
                "#phone",
                "input[name='your-phone']",
                "input[name='form_fields[phone]']",
                "input[name='telephone']",
                "input[id='telephone']",
                "input[name='mobile']",
                "input[id='mobile']",
                "input[name='cell']",
                "input[id='cell']",
                "input[name='phone_number']",
                "input[id='phone_number']",
                "input[name='phoneNumber']",
                "input[id='phoneNumber']",
                "input[name='phone-number']",
                "input[id='phone-number']",
                "input[name='wpforms[fields][3]']",  # Common in WPForms

                # Dato CMS form fields (used on floridassmiles.com)
                "input[name='phone']",
                "input[id='phone']",
                "input[name='phone-number']",
                "input[id='phone-number']",
                "input[name='country-code']",  # For country code dropdown
                "input[id='country-code']",

                # Try input fields with phone-related placeholders
                "input[placeholder='Phone']",
                "input[placeholder='Phone*']",
                "input[placeholder='Phone Number']",
                "input[placeholder='Phone Number*']",
                "input[placeholder='Telephone']",
                "input[placeholder='Telephone*']",
                "input[placeholder='Mobile']",
                "input[placeholder='Mobile*']",

                # Try any input with required attribute and phone text
                "input[required][placeholder*='phone' i]",

                # Try label-based selectors using JavaScript
                "input#" + self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        if ((label.textContent.toLowerCase().includes('phone') ||
                             label.textContent.toLowerCase().includes('tel') ||
                             label.textContent.toLowerCase().includes('mobile') ||
                             label.textContent.toLowerCase().includes('cell')) &&
                            label.htmlFor) {
                            return label.htmlFor;
                        }
                    }
                    return '';
                """),

                # Try finding inputs with labels containing "Phone"
                self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        const text = label.textContent.trim().toLowerCase();
                        if ((text.includes('phone') || text === 'phone*') && label.htmlFor) {
                            return '#' + label.htmlFor;
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            phone_selectors = [selector for selector in phone_selectors if selector and not selector.endswith("''")]

            # Company selectors - expanded with more variations
            company_selectors = [
                # Generic company selectors with case insensitivity
                "input[name*='company' i]",
                "input[id*='company' i]",
                "input[placeholder*='company' i]",
                "input[class*='company' i]",
                "input[name*='organization' i]",
                "input[id*='organization' i]",
                "input[name*='business' i]",
                "input[id*='business' i]",

                # Common company field identifiers
                "input.company",
                "#company",
                "input[name='your-company']",
                "input[name='form_fields[company]']",
                "input[name='company_name']",
                "input[id='company_name']",
                "input[name='companyName']",
                "input[id='companyName']",
                "input[name='company-name']",
                "input[id='company-name']",
                "input[name='organization']",
                "input[id='organization']",
                "input[name='organization_name']",
                "input[id='organization_name']",
                "input[name='business']",
                "input[id='business']",
                "input[name='business_name']",
                "input[id='business_name']",
                "input[name='employer']",
                "input[id='employer']",
                "input[name='wpforms[fields][4]']",  # Common in WPForms

                # Try input fields with company-related placeholders
                "input[placeholder='Company']",
                "input[placeholder='Company Name']",
                "input[placeholder='Organization']",
                "input[placeholder='Business']",

                # Try label-based selectors using JavaScript
                "input#" + self.driver.execute_script("""
                    const labels = Array.from(document.querySelectorAll('label'));
                    for (const label of labels) {
                        if ((label.textContent.toLowerCase().includes('company') ||
                             label.textContent.toLowerCase().includes('organization') ||
                             label.textContent.toLowerCase().includes('business') ||
                             label.textContent.toLowerCase().includes('employer')) &&
                            label.htmlFor) {
                            return label.htmlFor;
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            company_selectors = [selector for selector in company_selectors if selector and not selector.endswith("''")]

            # Submit button selectors - expanded with more variations
            submit_selectors = [
                # Standard HTML form submit elements
                "input[type='submit']",
                "button[type='submit']",

                # Common submit button identifiers
                "button[name*='submit' i]",
                "button[id*='submit' i]",
                "button[class*='submit' i]",
                "input[name*='submit' i]",
                "input[id*='submit' i]",
                "input[class*='submit' i]",

                # Buttons with common submit text
                "button:contains('Submit')",
                "button:contains('Send')",
                "button:contains('Submit Form')",
                "button:contains('Send Message')",
                "button:contains('Contact Us')",
                "button:contains('Get in Touch')",
                "button:contains('Reach Out')",
                "button:contains('Contact')",

                # Input buttons with submit values
                "input[value*='Submit' i]",
                "input[value*='Send' i]",
                "input[value*='Contact' i]",

                # Common CSS classes and IDs
                "button.submit",
                "#submit",
                "button.send",
                "#send",
                "button.btn-submit",
                "button.btn-send",
                "button.contact-submit",
                "button.form-submit",
                "button.submit-button",
                "button.contact-button",
                "button.btn-primary",  # Bootstrap primary button
                "button.btn-contact",

                # Try any button inside a form as a last resort
                "form button:last-child",
                "form input[type='button']:last-child",

                # Try label-based selectors using JavaScript
                "button#" + self.driver.execute_script("""
                    const buttons = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"]'));
                    for (const button of buttons) {
                        if (button.textContent && (
                            button.textContent.toLowerCase().includes('submit') ||
                            button.textContent.toLowerCase().includes('send') ||
                            button.textContent.toLowerCase().includes('contact'))) {
                            return button.id || '';
                        }
                        if (button.value && (
                            button.value.toLowerCase().includes('submit') ||
                            button.value.toLowerCase().includes('send') ||
                            button.value.toLowerCase().includes('contact'))) {
                            return button.id || '';
                        }
                    }
                    return '';
                """)
            ]

            # Filter out empty selectors
            submit_selectors = [selector for selector in submit_selectors if selector and not selector.endswith("''")]

            # Track filled fields for logging
            filled_fields = []

            # Function to safely fill a field
            def fill_field(field_type, selectors, value):
                # Add to attempted fields in submission log
                self.submission_log["fields_attempted"].append(field_type)

                # Skip if value is empty
                if not value:
                    print(f"Skipping {field_type} field because value is empty")
                    self.submission_log["fields_failed"].append(f"{field_type} (empty value)")
                    return False

                # Special handling for name field - log the exact value we're using
                if field_type == "name":
                    print(f"Attempting to fill name field with value: '{value}'")
                    # Log the settings values being used
                    print(f"Using name from settings:")
                    print(f"  your_name: {self.settings.get('your_name', '')}")
                    print(f"  your_first_name: {self.settings.get('your_first_name', '')}")
                    print(f"  your_last_name: {self.settings.get('your_last_name', '')}")

                # Track attempts for better logging
                attempts = 0
                field_details = {}  # Store details about the field for logging

                # Check if we have custom selectors from AI analysis
                if custom_selectors and field_type in custom_selectors and custom_selectors[field_type]:
                    print(f"Using AI-generated selectors for {field_type} field")
                    ai_selectors = custom_selectors[field_type]

                    # Try AI selectors first
                    for selector in ai_selectors:
                        attempts += 1
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                for element in elements:
                                    try:
                                        # Check if element is visible and enabled
                                        if element.is_displayed() and element.is_enabled():
                                            # Get element attributes for better logging
                                            element_id = element.get_attribute('id') or ''
                                            element_name = element.get_attribute('name') or ''
                                            element_class = element.get_attribute('class') or ''
                                            element_type = element.get_attribute('type') or ''
                                            element_placeholder = element.get_attribute('placeholder') or ''

                                            # Store field details for logging
                                            field_details = {
                                                "type": field_type,
                                                "selector": selector,
                                                "id": element_id,
                                                "name": element_name,
                                                "element_type": element_type,
                                                "placeholder": element_placeholder,
                                                "value": value,
                                                "ai_generated": True
                                            }

                                            print(f"Found {field_type} field using AI selector: id='{element_id}', name='{element_name}', type='{element_type}', placeholder='{element_placeholder}'")

                                            # Scroll element into view
                                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                            time.sleep(0.5)  # Wait for scroll

                                            # Clear field if it's an input
                                            if element.tag_name in ['input', 'textarea']:
                                                element.clear()
                                                print(f"Cleared {field_type} field")

                                            # Type more naturally with a delay between characters if in slow mode
                                            if self.browser_speed == 'slow':
                                                print(f"Typing '{value}' character by character in {field_type} field...")
                                                for char in value:
                                                    element.send_keys(char)
                                                    time.sleep(0.1)  # Small delay between characters
                                            else:
                                                print(f"Typing '{value}' in {field_type} field...")
                                                element.send_keys(value)

                                            # Verify the field was filled correctly
                                            if element.tag_name in ['input', 'textarea']:
                                                actual_value = element.get_attribute('value')
                                                if actual_value:
                                                    print(f"Verified {field_type} field contains: '{actual_value}'")
                                                    field_details["actual_value"] = actual_value
                                                else:
                                                    print(f"Warning: {field_type} field appears empty after filling")
                                                    # Try again with JavaScript as a fallback
                                                    self.driver.execute_script(f"arguments[0].value = '{value}';", element)
                                                    print(f"Attempted to fill {field_type} field using JavaScript")

                                                    # Check if JavaScript fill worked
                                                    actual_value = element.get_attribute('value')
                                                    if actual_value:
                                                        print(f"JavaScript fill successful: {field_type} field now contains: '{actual_value}'")
                                                        field_details["actual_value"] = actual_value
                                                        field_details["filled_with"] = "JavaScript"
                                                    else:
                                                        print(f"Warning: {field_type} field still empty after JavaScript fill attempt")
                                                        field_details["filled_with"] = "Failed"

                                            time.sleep(self.action_delay / 2)  # Short delay after filling
                                            print(f"Successfully filled {field_type} field using AI selector: {selector}")

                                            # Add to filled fields in submission log
                                            filled_fields.append(field_type)
                                            self.submission_log["fields_filled"].append(field_details)

                                            # Record training example for machine learning
                                            try:
                                                field_attributes = {
                                                    'id': element_id,
                                                    'name': element_name,
                                                    'class': element_class,
                                                    'type': element_type,
                                                    'placeholder': element_placeholder,
                                                    'tag_name': element.tag_name
                                                }
                                                self._record_field_training_example(field_attributes, field_type, True)
                                            except Exception as e:
                                                print(f"Error recording training example: {e}")

                                            # Take a screenshot of the filled field
                                            try:
                                                self.driver.save_screenshot(f"filled_{field_type}_field_ai.png")
                                            except:
                                                pass

                                            return True
                                    except Exception as e:
                                        print(f"Error filling {field_type} field with AI selector {selector}: {e}")
                                        continue
                        except Exception as e:
                            print(f"Error with {field_type} AI selector {selector}: {e}")
                            continue

                    print(f"AI selectors did not work for {field_type} field, falling back to standard selectors")
                    # If AI selectors didn't work, continue with standard selectors

                for selector in selectors:
                    attempts += 1
                    try:
                        # Handle special case for text containing selectors
                        if 'contains' in selector:
                            text = selector.split("'")[1]
                            elements = self.driver.execute_script(f"""
                                return Array.from(document.querySelectorAll('button')).filter(el =>
                                    el.textContent.toLowerCase().includes('{text.lower()}')
                                );
                            """)
                        else:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                        if elements:
                            for element in elements:
                                try:
                                    # Check if element is visible and enabled
                                    if element.is_displayed() and element.is_enabled():
                                        # Get element attributes for better logging
                                        element_id = element.get_attribute('id') or ''
                                        element_name = element.get_attribute('name') or ''
                                        element_class = element.get_attribute('class') or ''
                                        element_type = element.get_attribute('type') or ''
                                        element_placeholder = element.get_attribute('placeholder') or ''

                                        # Store field details for logging
                                        field_details = {
                                            "type": field_type,
                                            "selector": selector,
                                            "id": element_id,
                                            "name": element_name,
                                            "element_type": element_type,
                                            "placeholder": element_placeholder,
                                            "value": value
                                        }

                                        print(f"Found {field_type} field: id='{element_id}', name='{element_name}', type='{element_type}', placeholder='{element_placeholder}'")

                                        # Scroll element into view
                                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                        time.sleep(0.5)  # Wait for scroll

                                        # Clear field if it's an input
                                        if element.tag_name in ['input', 'textarea']:
                                            element.clear()
                                            print(f"Cleared {field_type} field")

                                        # Type more naturally with a delay between characters if in slow mode
                                        if self.browser_speed == 'slow':
                                            print(f"Typing '{value}' character by character in {field_type} field...")
                                            for char in value:
                                                element.send_keys(char)
                                                time.sleep(0.1)  # Small delay between characters
                                        else:
                                            print(f"Typing '{value}' in {field_type} field...")
                                            element.send_keys(value)

                                        # Verify the field was filled correctly
                                        if element.tag_name in ['input', 'textarea']:
                                            actual_value = element.get_attribute('value')
                                            if actual_value:
                                                print(f"Verified {field_type} field contains: '{actual_value}'")
                                                field_details["actual_value"] = actual_value
                                            else:
                                                print(f"Warning: {field_type} field appears empty after filling")
                                                # Try again with JavaScript as a fallback
                                                self.driver.execute_script(f"arguments[0].value = '{value}';", element)
                                                print(f"Attempted to fill {field_type} field using JavaScript")

                                                # Check if JavaScript fill worked
                                                actual_value = element.get_attribute('value')
                                                if actual_value:
                                                    print(f"JavaScript fill successful: {field_type} field now contains: '{actual_value}'")
                                                    field_details["actual_value"] = actual_value
                                                    field_details["filled_with"] = "JavaScript"
                                                else:
                                                    print(f"Warning: {field_type} field still empty after JavaScript fill attempt")
                                                    field_details["filled_with"] = "Failed"

                                        time.sleep(self.action_delay / 2)  # Short delay after filling
                                        print(f"Successfully filled {field_type} field using selector: {selector}")

                                        # Add to filled fields in submission log
                                        filled_fields.append(field_type)
                                        self.submission_log["fields_filled"].append(field_details)

                                        # Record training example for machine learning
                                        try:
                                            field_attributes = {
                                                'id': element_id,
                                                'name': element_name,
                                                'class': element_class,
                                                'type': element_type,
                                                'placeholder': element_placeholder,
                                                'tag_name': element.tag_name
                                            }
                                            self._record_field_training_example(field_attributes, field_type, True)
                                        except Exception as e:
                                            print(f"Error recording training example: {e}")

                                        # Take a screenshot of the filled field
                                        try:
                                            self.driver.save_screenshot(f"filled_{field_type}_field.png")
                                        except:
                                            pass

                                        return True
                                except Exception as e:
                                    print(f"Error filling {field_type} field with selector {selector}: {e}")
                                    continue
                    except Exception as e:
                        print(f"Error with {field_type} selector {selector}: {e}")
                        continue

                print(f"Could not find or fill {field_type} field after {attempts} selector attempts")
                self.submission_log["fields_failed"].append(f"{field_type} (not found after {attempts} attempts)")
                return False

            # Parse name into first and last name for separate fields
            name_parts = name.split()
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            # Fill form fields
            print("Attempting to fill name fields...")
            # Try full name field first
            name_filled = fill_field("name", name_selectors, name)

            # If full name field not found, try first and last name fields
            first_name_filled = False
            last_name_filled = False

            # Get first name and last name from settings
            settings_first_name = self.settings.get('your_first_name', '')
            settings_last_name = self.settings.get('your_last_name', '')

            if not name_filled and settings_first_name:
                print("Full name field not found, trying first name field with settings first name...")
                print(f"Using first name from settings: '{settings_first_name}'")
                first_name_filled = fill_field("first_name", first_name_selectors, settings_first_name)

                # If first name was filled, try to fill last name too
                if first_name_filled and settings_last_name:
                    print("First name field filled, trying last name field with settings last name...")
                    print(f"Using last name from settings: '{settings_last_name}'")
                    # Fill the last name field and store the result in last_name_filled
                    last_name_filled = fill_field("last_name", last_name_selectors, settings_last_name)
                    # We don't use last_name_filled for name_filled since we only need first name to be filled

                # Consider name filled if at least first name was filled
                name_filled = first_name_filled

            print("Attempting to fill email field...")
            email_filled = fill_field("email", email_selectors, email)

            print("Attempting to fill message field...")
            message_filled = fill_field("message", message_selectors, message)

            print("Attempting to fill phone field...")
            phone_filled = fill_field("phone", phone_selectors, phone)

            print("Attempting to fill company field...")
            company_filled = fill_field("company", company_selectors, company)

            # Handle date and time fields - these are often problematic
            print("Looking for date and time fields...")
            date_time_filled = False

            # Define selectors for date/time fields
            date_time_selectors = [
                'input[type="date"]',
                'input[type="datetime-local"]',
                'input[type="datetime"]',
                'input[type="time"]',
                'input[id*="date"]',
                'input[name*="date"]',
                'input[id*="time"]',
                'input[name*="time"]',
                'input[placeholder*="date"]',
                'input[placeholder*="time"]',
                'input[class*="date"]',
                'input[class*="time"]',
                'input[id*="calendar"]',
                'input[name*="calendar"]',
                'input[placeholder*="calendar"]',
                'input[placeholder*="Date & Time"]',
                'input[placeholder*="Date and Time"]',
                'input[aria-label*="date"]',
                'input[aria-label*="time"]'
            ]

            # Try to find and fill date/time fields
            try:
                for selector in date_time_selectors:
                    try:
                        date_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if date_elements:
                            for element in date_elements:
                                if element.is_displayed() and element.is_enabled():
                                    # Get element attributes for better logging
                                    element_id = element.get_attribute('id') or ''
                                    element_name = element.get_attribute('name') or ''
                                    element_type = element.get_attribute('type') or ''
                                    element_placeholder = element.get_attribute('placeholder') or ''

                                    print(f"Found date/time field: id='{element_id}', name='{element_name}', type='{element_type}', placeholder='{element_placeholder}'")

                                    # Scroll element into view
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                    time.sleep(0.5)  # Wait for scroll

                                    # Clear the field
                                    element.clear()

                                    # Determine what kind of date/time format to use
                                    if element_type == 'date':
                                        # Use YYYY-MM-DD format for date inputs
                                        future_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
                                        element.send_keys(future_date)
                                        print(f"Filled date field with future date: {future_date}")
                                    elif element_type == 'time':
                                        # Use HH:MM format for time inputs
                                        element.send_keys("14:30")
                                        print("Filled time field with 2:30 PM")
                                    elif element_type == 'datetime-local' or element_type == 'datetime':
                                        # Use YYYY-MM-DDThh:mm format for datetime-local inputs
                                        future_datetime = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%dT14:30')
                                        element.send_keys(future_datetime)
                                        print(f"Filled datetime field with future datetime: {future_datetime}")
                                    else:
                                        # For other inputs, try a human-readable format
                                        future_date = (datetime.now() + timedelta(days=3)).strftime('%m/%d/%Y 2:30 PM')
                                        element.send_keys(future_date)
                                        print(f"Filled date/time field with future date and time: {future_date}")

                                    # If JavaScript date pickers are used, also try setting the value directly
                                    try:
                                        future_date_js = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
                                        self.driver.execute_script(f"arguments[0].value = '{future_date_js}';", element)
                                        print(f"Also set date value using JavaScript: {future_date_js}")
                                    except Exception as js_error:
                                        print(f"JavaScript date setting failed: {js_error}")

                                    date_time_filled = True
                                    break

                            if date_time_filled:
                                break
                    except Exception as e:
                        print(f"Error with date/time selector {selector}: {e}")
                        continue

                if not date_time_filled:
                    print("No standard date/time fields found, looking for custom date pickers...")

                    # Try to find date picker elements that might not be standard inputs
                    date_picker_selectors = [
                        '[class*="datepicker"]',
                        '[class*="date-picker"]',
                        '[class*="calendar"]',
                        '[id*="datepicker"]',
                        '[id*="date-picker"]',
                        '[id*="calendar"]',
                        '[aria-label*="Choose a date"]',
                        '[aria-label*="Select a date"]'
                    ]

                    for selector in date_picker_selectors:
                        try:
                            picker_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if picker_elements:
                                for element in picker_elements:
                                    if element.is_displayed():
                                        print(f"Found potential date picker: {selector}")

                                        # Try to click on it to open the picker
                                        element.click()
                                        time.sleep(1)  # Wait for picker to open

                                        # Try to select a date (usually clicking on a day in the current month)
                                        try:
                                            # Look for day elements in the opened calendar
                                            day_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                '.ui-datepicker-calendar td:not(.ui-datepicker-unselectable) a, ' +
                                                '.calendar-day:not(.disabled), ' +
                                                '.datepicker-day:not(.disabled), ' +
                                                '.day:not(.disabled)')

                                            if day_elements:
                                                # Click on a day that's a few days in the future
                                                future_day_index = min(len(day_elements) - 1, 3)
                                                day_elements[future_day_index].click()
                                                print(f"Clicked on a future day in the calendar")
                                                date_time_filled = True
                                                break
                                        except Exception as day_error:
                                            print(f"Error selecting day from calendar: {day_error}")

                                if date_time_filled:
                                    break
                        except Exception as e:
                            print(f"Error with date picker selector {selector}: {e}")
                            continue
            except Exception as date_error:
                print(f"Error handling date/time fields: {date_error}")

            # Take a screenshot after filling
            self.driver.save_screenshot("after_filling_form.png")

            # If we couldn't fill any fields, try a more aggressive approach
            if not (name_filled or email_filled or message_filled or phone_filled or company_filled):
                print("Could not identify any form fields with standard selectors. Trying a more aggressive approach...")

                # Take a screenshot for debugging
                self.driver.save_screenshot("before_aggressive_field_search.png")

                # Try to find ANY input fields on the page, regardless of form
                try:
                    # Find all visible input fields
                    print("Looking for ANY visible input fields on the page...")

                    # Use JavaScript to find all visible input fields, including selects
                    visible_inputs = self.driver.execute_script("""
                        const visibleInputs = [];
                        document.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea, select').forEach(input => {
                            if (input.offsetParent !== null) {  // Check if visible
                                visibleInputs.push({
                                    id: input.id || '',
                                    name: input.name || '',
                                    type: input.type || '',
                                    tag: input.tagName.toLowerCase(),
                                    placeholder: input.placeholder || '',
                                    class: input.className || ''
                                });
                            }
                        });
                        return visibleInputs;
                    """)

                    if visible_inputs:
                        print(f"Found {len(visible_inputs)} visible input fields. Attempting to identify and fill them.")

                        # Try to identify name field
                        if not name_filled:
                            for input_data in visible_inputs:
                                input_id = input_data.get('id', '').lower()
                                input_name = input_data.get('name', '').lower()
                                input_placeholder = input_data.get('placeholder', '').lower()
                                input_class = input_data.get('class', '').lower()

                                # Check if this looks like a name field
                                if ('name' in input_id or 'name' in input_name or 'name' in input_placeholder or
                                    'author' in input_id or 'author' in input_name or
                                    'fullname' in input_id or 'fullname' in input_name or
                                    'full_name' in input_id or 'full_name' in input_name or
                                    'full-name' in input_id or 'full-name' in input_name):

                                    # Skip if it looks like a username field
                                    if ('user' in input_id or 'user' in input_name or 'login' in input_id or 'login' in input_name):
                                        continue

                                    # Try to fill this field
                                    selector = f"#{input_data['id']}" if input_data['id'] else f"[name='{input_data['name']}']"
                                    if not selector or selector == "#" or selector == "[name='']":
                                        continue

                                    try:
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        element.clear()
                                        element.send_keys(name)
                                        print(f"Filled potential name field: {selector} with '{name}'")
                                        name_filled = True
                                        break
                                    except Exception as e:
                                        print(f"Error filling potential name field {selector}: {e}")

                        # Try to identify email field
                        if not email_filled:
                            for input_data in visible_inputs:
                                input_id = input_data.get('id', '').lower()
                                input_name = input_data.get('name', '').lower()
                                input_type = input_data.get('type', '').lower()
                                input_placeholder = input_data.get('placeholder', '').lower()

                                # Check if this looks like an email field
                                if (input_type == 'email' or 'email' in input_id or 'email' in input_name or
                                    'email' in input_placeholder or 'e-mail' in input_id or 'e-mail' in input_name or
                                    'e_mail' in input_id or 'e_mail' in input_name):

                                    # Try to fill this field
                                    selector = f"#{input_data['id']}" if input_data['id'] else f"[name='{input_data['name']}']"
                                    if not selector or selector == "#" or selector == "[name='']":
                                        continue

                                    try:
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        element.clear()
                                        element.send_keys(email)
                                        print(f"Filled potential email field: {selector} with '{email}'")
                                        email_filled = True
                                        break
                                    except Exception as e:
                                        print(f"Error filling potential email field {selector}: {e}")

                        # Try to identify message field
                        if not message_filled:
                            for input_data in visible_inputs:
                                input_id = input_data.get('id', '').lower()
                                input_name = input_data.get('name', '').lower()
                                input_tag = input_data.get('tag', '').lower()
                                input_placeholder = input_data.get('placeholder', '').lower()

                                # Check if this looks like a message field
                                if (input_tag == 'textarea' or 'message' in input_id or 'message' in input_name or
                                    'message' in input_placeholder or 'comment' in input_id or 'comment' in input_name or
                                    'comments' in input_id or 'comments' in input_name or 'inquiry' in input_id or
                                    'inquiry' in input_name or 'description' in input_id or 'description' in input_name):

                                    # Try to fill this field
                                    selector = f"#{input_data['id']}" if input_data['id'] else f"[name='{input_data['name']}']"
                                    if not selector or selector == "#" or selector == "[name='']":
                                        if input_tag == 'textarea':
                                            # For textareas without ID or name, try to use tag selector
                                            selector = "textarea"
                                        else:
                                            continue

                                    try:
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        element.clear()
                                        element.send_keys(message)
                                        print(f"Filled potential message field: {selector} with message")
                                        message_filled = True
                                        break
                                    except Exception as e:
                                        print(f"Error filling potential message field {selector}: {e}")

                        # Try to identify phone field
                        if not phone_filled:
                            for input_data in visible_inputs:
                                input_id = input_data.get('id', '').lower()
                                input_name = input_data.get('name', '').lower()
                                input_type = input_data.get('type', '').lower()
                                input_placeholder = input_data.get('placeholder', '').lower()

                                # Check if this looks like a phone field
                                if (input_type == 'tel' or 'phone' in input_id or 'phone' in input_name or
                                    'phone' in input_placeholder or 'tel' in input_id or 'tel' in input_name or
                                    'telephone' in input_id or 'telephone' in input_name or 'mobile' in input_id or
                                    'mobile' in input_name or 'cell' in input_id or 'cell' in input_name):

                                    # Try to fill this field
                                    selector = f"#{input_data['id']}" if input_data['id'] else f"[name='{input_data['name']}']"
                                    if not selector or selector == "#" or selector == "[name='']":
                                        continue

                                    try:
                                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                        element.clear()
                                        element.send_keys(phone)
                                        print(f"Filled potential phone field: {selector} with '{phone}'")
                                        phone_filled = True
                                        break
                                    except Exception as e:
                                        print(f"Error filling potential phone field {selector}: {e}")

                        # Take a screenshot after aggressive filling
                        self.driver.save_screenshot("after_aggressive_field_search.png")

                        # If we still couldn't fill any fields, try to find alternative contact methods
                        if not (name_filled or email_filled or message_filled or phone_filled or company_filled):
                            print("Could not identify any form fields even with aggressive approach")
                            print("Scanning website for alternative contact methods...")

                            # Take a screenshot for debugging
                            self.driver.save_screenshot("scanning_for_alternative_contacts.png")

                            # Scan for alternative contact methods
                            alternative_contacts = self._scan_for_alternative_contacts()

                            if alternative_contacts:
                                contact_info = "\n".join([f"- {method}: {value}" for method, value in alternative_contacts.items()])
                                print(f"Found alternative contact methods:\n{contact_info}")

                                # Store alternative contacts in the database
                                if hasattr(self, 'current_contact_id') and self.current_contact_id:
                                    self._update_alternative_contacts(self.current_contact_id, alternative_contacts)

                                return False, f"Could not fill form, but found alternative contacts: {contact_info}"
                            else:
                                print("No alternative contact methods found")
                                return False, "Could not identify form fields and no alternative contacts found"
                    else:
                        print("No visible input fields found on the page")
                        print("Scanning website for alternative contact methods...")

                        # Take a screenshot for debugging
                        self.driver.save_screenshot("scanning_for_alternative_contacts.png")

                        # Scan for alternative contact methods
                        alternative_contacts = self._scan_for_alternative_contacts()

                        if alternative_contacts:
                            contact_info = "\n".join([f"- {method}: {value}" for method, value in alternative_contacts.items()])
                            print(f"Found alternative contact methods:\n{contact_info}")

                            # Store alternative contacts in the database
                            if hasattr(self, 'current_contact_id') and self.current_contact_id:
                                self._update_alternative_contacts(self.current_contact_id, alternative_contacts)

                            return False, f"Could not fill form, but found alternative contacts: {contact_info}"
                        else:
                            print("No alternative contact methods found")
                            return False, "No visible input fields found and no alternative contacts found"
                except Exception as e:
                    print(f"Error during aggressive field search: {e}")
                    # If aggressive approach fails, try to find alternative contact methods
                    print("Scanning website for alternative contact methods...")

                    # Take a screenshot for debugging
                    self.driver.save_screenshot("scanning_for_alternative_contacts.png")

                    # Scan for alternative contact methods
                    alternative_contacts = self._scan_for_alternative_contacts()

                    if alternative_contacts:
                        contact_info = "\n".join([f"- {method}: {value}" for method, value in alternative_contacts.items()])
                        print(f"Found alternative contact methods:\n{contact_info}")

                        # Store alternative contacts in the database
                        if hasattr(self, 'current_contact_id') and self.current_contact_id:
                            self._update_alternative_contacts(self.current_contact_id, alternative_contacts)

                        return False, f"Could not fill form, but found alternative contacts: {contact_info}"
                    else:
                        print("No alternative contact methods found")
                        return False, "Could not identify form fields and no alternative contacts found"

            # Log summary of filled fields
            filled_field_types = []
            if name_filled:
                filled_field_types.append("name")
            if email_filled:
                filled_field_types.append("email")
            if message_filled:
                filled_field_types.append("message")
            if phone_filled:
                filled_field_types.append("phone")
            if company_filled:
                filled_field_types.append("company")

            print(f"Successfully filled the following fields: {', '.join(filled_field_types)}")

            # Fill any remaining required fields with default values
            if any(filled_field_types):
                print("Checking for any remaining required fields...")

                # Try to find all required fields that haven't been filled
                try:
                    # Find all required inputs that are empty
                    required_fields = self.driver.execute_script("""
                        const requiredFields = [];
                        // Check for required inputs
                        document.querySelectorAll('input[required], textarea[required], select[required]').forEach(field => {
                            if (!field.value &&
                                field.type !== 'submit' &&
                                field.type !== 'button' &&
                                field.type !== 'hidden' &&
                                field.type !== 'checkbox' &&
                                field.type !== 'radio' &&
                                field.offsetParent !== null) {  // Check if visible
                                requiredFields.push({
                                    id: field.id,
                                    name: field.name,
                                    type: field.type,
                                    tag: field.tagName.toLowerCase(),
                                    placeholder: field.placeholder || ''
                                });
                            }
                        });

                        // Also check for inputs with aria-required="true"
                        document.querySelectorAll('input[aria-required="true"], textarea[aria-required="true"], select[aria-required="true"]').forEach(field => {
                            if (!field.value &&
                                field.type !== 'submit' &&
                                field.type !== 'button' &&
                                field.type !== 'hidden' &&
                                field.type !== 'checkbox' &&
                                field.type !== 'radio' &&
                                field.offsetParent !== null) {  // Check if visible
                                requiredFields.push({
                                    id: field.id,
                                    name: field.name,
                                    type: field.type,
                                    tag: field.tagName.toLowerCase(),
                                    placeholder: field.placeholder || ''
                                });
                            }
                        });

                        return requiredFields;
                    """)

                    if required_fields:
                        print(f"Found {len(required_fields)} unfilled required fields. Attempting to fill them with default values.")

                        for field in required_fields:
                            field_id = field.get('id', '')
                            field_name = field.get('name', '')
                            field_type = field.get('type', '')
                            field_tag = field.get('tag', '')
                            field_placeholder = field.get('placeholder', '')

                            selector = ""
                            if field_id:
                                selector = f"#{field_id}"
                            elif field_name:
                                selector = f"[name='{field_name}']"
                            else:
                                continue

                            print(f"Filling required field: {selector} (type: {field_type}, tag: {field_tag})")

                            try:
                                element = self.driver.find_element(By.CSS_SELECTOR, selector)

                                # Handle different field types
                                if field_tag == 'select':
                                    # For select elements, handle more intelligently
                                    try:
                                        from selenium.webdriver.support.ui import Select
                                        select = Select(element)

                                        # Get all options
                                        options = select.options

                                        # Check if this is a service/interest dropdown (like on floridassmiles.com)
                                        is_service_dropdown = False
                                        if field_id:
                                            if 'service' in field_id.lower() or 'interest' in field_id.lower():
                                                is_service_dropdown = True
                                        if field_name:
                                            if 'service' in field_name.lower() or 'interest' in field_name.lower():
                                                is_service_dropdown = True

                                        if is_service_dropdown:
                                            print(f"Detected service/interest dropdown: {selector}")
                                            # Try to select "Other" option if available
                                            for i, option in enumerate(options):
                                                if option.text.strip().lower() == 'other':
                                                    select.select_by_index(i)
                                                    print(f"Selected 'Other' in service dropdown")
                                                    break
                                            else:
                                                # If no "Other" option, select the second option (first is often a placeholder)
                                                if len(options) > 1:
                                                    select.select_by_index(1)
                                                    print(f"Selected second option in service dropdown")
                                        else:
                                            # For regular dropdowns, choose the second option (first is often a placeholder)
                                            if len(options) > 1:
                                                # Try to find a good option (skip empty or placeholder options)
                                                for i in range(1, len(options)):
                                                    option_text = options[i].text.strip()
                                                    if option_text and option_text.lower() not in ['select', 'choose', 'please select', 'select one']:
                                                        select.select_by_index(i)
                                                        print(f"Selected option '{option_text}' in dropdown: {selector}")
                                                        break
                                                else:
                                                    # If no good option found, select the second option
                                                    select.select_by_index(1)
                                                    print(f"Selected second option in dropdown: {selector}")
                                            elif len(options) > 0:
                                                select.select_by_index(0)
                                                print(f"Selected first option in dropdown: {selector}")
                                    except Exception as select_error:
                                        print(f"Error handling select dropdown: {select_error}")
                                        # Fallback to JavaScript method
                                        self.driver.execute_script("""
                                            const select = arguments[0];
                                            if (select.options.length > 1) {
                                                select.selectedIndex = 1;
                                                const event = new Event('change', { bubbles: true });
                                                select.dispatchEvent(event);
                                            } else if (select.options.length > 0) {
                                                select.selectedIndex = 0;
                                                const event = new Event('change', { bubbles: true });
                                                select.dispatchEvent(event);
                                            }
                                        """, element)
                                        print(f"Used JavaScript fallback to select an option from dropdown {selector}")
                                elif field_type == 'date':
                                    # For date inputs, use today's date
                                    today = time.strftime('%Y-%m-%d')
                                    self.driver.execute_script("arguments[0].value = arguments[1]", element, today)
                                    print(f"Set date field {selector} to today's date")
                                else:
                                    # Try to intelligently guess the field type based on field name and placeholder
                                    field_name_lower = field_name.lower() if field_name else ""
                                    field_placeholder_lower = field_placeholder.lower() if field_placeholder else ""
                                    field_id_lower = field_id.lower() if field_id else ""

                                    # Check if it might be a name field
                                    if any(name_hint in text for name_hint in ['name', 'author', 'person', 'who']
                                          for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        print(f"Field '{field_name}' looks like a name field, using name value")
                                        default_value = self.settings.get('your_name', 'John Doe')
                                    # Check if it might be a phone field
                                    elif any(phone_hint in text for phone_hint in ['phone', 'tel', 'mobile', 'cell']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        print(f"Field '{field_name}' looks like a phone field, using phone value")
                                        default_value = self.settings.get('phone', '555-123-4567')
                                    # Check if it might be an email field
                                    elif any(email_hint in text for email_hint in ['email', 'mail']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        print(f"Field '{field_name}' looks like an email field, using email value")
                                        default_value = self.settings.get('your_email', 'contact@example.com')
                                    # Check if it might be a company field
                                    elif any(company_hint in text for company_hint in ['company', 'business', 'organization', 'firm']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        print(f"Field '{field_name}' looks like a company field, using company value")
                                        default_value = self.settings.get('your_company', 'My Company')
                                    # Check if it might be a zip/postal code field
                                    elif any(keyword in text for keyword in ['zip', 'postal', 'post code']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        default_value = "10001"  # NYC zip code
                                    # Check if it might be a city field
                                    elif any(keyword in text for keyword in ['city', 'town']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        default_value = "New York"
                                    # Check if it might be a state field
                                    elif any(keyword in text for keyword in ['state', 'province']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        default_value = "NY"
                                    # Check if it might be a country field
                                    elif any(keyword in text for keyword in ['country', 'nation']
                                            for text in [field_name_lower, field_id_lower, field_placeholder_lower]):
                                        default_value = "USA"
                                    # For truly unknown fields, use a more reasonable default based on field type
                                    else:
                                        if field_type == 'text' or field_type == '':
                                            # For text inputs, try to use name as a reasonable default
                                            print(f"Unknown text field '{field_name}', using name as default")
                                            default_value = self.settings.get('your_name', 'John Doe')
                                        else:
                                            # Only use N/A as a last resort
                                            print(f"Completely unknown field '{field_name}', using 'N/A' as default")
                                            default_value = "N/A"

                                    element.clear()
                                    element.send_keys(default_value)
                                    print(f"Filled {selector} with '{default_value}'")
                            except Exception as e:
                                print(f"Could not fill required field {selector}: {e}")

                    # Handle checkboxes (often for terms and conditions)
                    try:
                        checkboxes = self.driver.execute_script("""
                            const checkboxes = [];
                            document.querySelectorAll('input[type="checkbox"][required]').forEach(checkbox => {
                                if (!checkbox.checked && checkbox.offsetParent !== null) {
                                    checkboxes.push({
                                        id: checkbox.id,
                                        name: checkbox.name
                                    });
                                }
                            });
                            return checkboxes;
                        """)

                        if checkboxes:
                            print(f"Found {len(checkboxes)} required checkboxes. Checking them.")

                            for checkbox in checkboxes:
                                checkbox_id = checkbox.get('id', '')
                                checkbox_name = checkbox.get('name', '')

                                selector = ""
                                if checkbox_id:
                                    selector = f"#{checkbox_id}"
                                elif checkbox_name:
                                    selector = f"input[type='checkbox'][name='{checkbox_name}']"
                                else:
                                    continue

                                try:
                                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    self.driver.execute_script("arguments[0].click();", element)
                                    print(f"Checked required checkbox: {selector}")
                                except Exception as e:
                                    print(f"Could not check required checkbox {selector}: {e}")
                    except Exception as e:
                        print(f"Error handling checkboxes: {e}")

                except Exception as e:
                    print(f"Error while trying to fill required fields: {e}")

            # Check if we filled the minimum required fields (name and email at minimum)
            if not (name_filled and email_filled):
                print("Warning: Could not fill both name and email fields, which are typically required")
                # We'll still try to submit the form, but log the warning

            # Try to find and click submit button
            print("Looking for submit button...")

            # Update the processing stage in the status
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "submitting_form",
                "last_updated": datetime.now().isoformat()
            })

            # Check if form submission is enabled in settings
            submit_form = self.settings.get('submit_form', True)
            if not submit_form:
                print("⚠️ Form submission is disabled in settings. Form filled but not submitted.")
                self.submission_log["form_submitted"] = False
                self.submission_log["submission_result"] = "Form filled but not submitted (submit_form setting is disabled)"
                # Take a screenshot of the filled form
                self.driver.save_screenshot("form_filled_not_submitted.png")
                return True, "Form filled successfully but not submitted (submit_form setting is disabled)"

            # If this is the JavaScript fallback strategy (third attempt), use a more aggressive approach
            if strategy == "javascript_fallback":
                print("Using JavaScript fallback approach for form submission")

                # Try to directly submit the form using JavaScript
                try:
                    # First try to use the form's submit method
                    print("Attempting to submit form using JavaScript form.submit() method")
                    self.driver.execute_script("arguments[0].submit();", form_element)

                    # Wait for form submission
                    time.sleep(3)

                    # Check if we're still on the same page or if there was a redirect
                    current_url = self.driver.current_url
                    if current_url != self.submission_log["website"]:
                        print(f"✅ Form submission successful - redirected to {current_url}")
                        self.submission_log["form_submitted"] = True
                        self.submission_log["submission_result"] = f"Success - Redirected to {current_url}"
                        return True, f"Form submitted successfully using JavaScript (redirected to {current_url})"

                    # Check for success messages
                    success_messages = self.driver.find_elements(By.CSS_SELECTOR,
                        ".success, .thank-you, .message-sent, .form-success, .alert-success, .wpforms-confirmation-container")

                    if success_messages:
                        for msg in success_messages:
                            if msg.is_displayed():
                                success_text = msg.text.strip()
                                print(f"✅ Form submission successful: {success_text}")
                                self.submission_log["form_submitted"] = True
                                self.submission_log["submission_result"] = f"Success - {success_text}"
                                return True, f"Form submitted successfully using JavaScript: {success_text}"

                    # If no success message, try a more aggressive approach - click all possible submit buttons
                    print("No success confirmation found, trying to click all possible submit buttons")
                    submit_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                        "button[type='submit'], input[type='submit'], button.submit, .submit-button, .btn-submit, .form-submit")

                    if submit_buttons:
                        for button in submit_buttons:
                            try:
                                if button.is_displayed() and button.is_enabled():
                                    print(f"Clicking submit button: {button.get_attribute('outerHTML')[:100]}")
                                    button.click()
                                    time.sleep(2)

                                    # Check for success again
                                    if self.driver.current_url != current_url:
                                        print(f"✅ Form submission successful after clicking button - redirected to {self.driver.current_url}")
                                        self.submission_log["form_submitted"] = True
                                        self.submission_log["submission_result"] = f"Success - Redirected to {self.driver.current_url}"
                                        return True, f"Form submitted successfully after clicking button (redirected to {self.driver.current_url})"
                            except Exception as e:
                                print(f"Error clicking submit button: {e}")
                                continue

                    # If still no success, try to fill hidden fields and submit again
                    print("Trying to fill hidden fields and submit again")
                    hidden_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='hidden']")
                    if hidden_fields:
                        print(f"Found {len(hidden_fields)} hidden fields")
                        for field in hidden_fields:
                            try:
                                field_name = field.get_attribute('name') or ''
                                if field_name and not field.get_attribute('value'):
                                    # Try to set a value for empty hidden fields
                                    self.driver.execute_script("arguments[0].value = 'auto-filled';", field)
                                    print(f"Filled hidden field: {field_name}")
                            except:
                                continue

                        # Try to submit again
                        print("Submitting form again after filling hidden fields")
                        self.driver.execute_script("arguments[0].submit();", form_element)
                        time.sleep(3)

                    # If we get here, we couldn't confirm success but we tried everything
                    print("⚠️ Form may have been submitted but couldn't confirm success")
                    self.submission_log["form_submitted"] = True
                    self.submission_log["submission_result"] = "Uncertain - JavaScript submission attempted but no confirmation"
                    return True, "Form may have been submitted using JavaScript but couldn't confirm success"

                except Exception as js_error:
                    print(f"Error using JavaScript fallback approach: {js_error}")
                    # Continue with normal submission as fallback

            submit_clicked = False

            # Take a screenshot before looking for submit button
            self.driver.save_screenshot("before_submit_button_search.png")

            # First, look for buttons with specific text like "SEND REQUEST" from the screenshot
            custom_submit_texts = [
                "SEND REQUEST",
                "Send Request",
                "send request",
                "Submit Request",
                "Submit Form",
                "Send Message",
                "Submit",
                "Send"
            ]

            # Try to find buttons with these exact texts first
            for submit_text in custom_submit_texts:
                try:
                    print(f"Looking for button with text: '{submit_text}'")

                    # Try different approaches to find the button
                    # 1. XPath with exact text
                    xpath_buttons = self.driver.find_elements(
                        By.XPATH,
                        f"//button[normalize-space(text())='{submit_text}'] | //input[@type='submit' and @value='{submit_text}']"
                    )

                    # 2. JavaScript to find elements containing the text
                    js_buttons = self.driver.execute_script(f"""
                        return Array.from(document.querySelectorAll('button, input[type="submit"], a.button, .btn, [role="button"], .submit, input[type="button"]'))
                            .filter(el => el.textContent.trim() === '{submit_text}' || el.value === '{submit_text}');
                    """)

                    # Combine results
                    buttons = xpath_buttons + js_buttons

                    if buttons:
                        for button in buttons:
                            try:
                                if button.is_displayed() and button.is_enabled():
                                    # Scroll button into view
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                                    time.sleep(1)  # Wait for scroll

                                    # Log button details
                                    button_text = button.text.strip() if hasattr(button, 'text') else "No text"
                                    button_type = button.get_attribute('type') or "No type"
                                    button_class = button.get_attribute('class') or "No class"
                                    button_id = button.get_attribute('id') or "No id"

                                    print(f"Found submit button: Text='{button_text}', Type='{button_type}', Class='{button_class}', ID='{button_id}'")

                                    # Click the button
                                    print(f"Clicking submit button with text: {submit_text}")
                                    print("Waiting 5 seconds before clicking submit button...")
                                    time.sleep(5)  # Add a 5-second delay before clicking

                                    # Try different click methods
                                    try:
                                        # Regular click
                                        button.click()
                                    except Exception as click_error:
                                        print(f"Regular click failed: {click_error}")
                                        try:
                                            # JavaScript click
                                            self.driver.execute_script("arguments[0].click();", button)
                                            print("Used JavaScript click instead")
                                        except Exception as js_click_error:
                                            print(f"JavaScript click also failed: {js_click_error}")
                                            raise

                                    # Wait for form submission with standard delay
                                    time.sleep(3)

                                    # Add a 10-second delay after form submission as requested by user
                                    print(f"Waiting 10 seconds after form submission to observe results...")
                                    for i in range(10, 0, -1):
                                        print(f"⏱️ {i} seconds remaining...")
                                        time.sleep(1)
                                    print(f"✅ 10-second observation period complete")

                                    # Take a screenshot after submission
                                    self.driver.save_screenshot("after_submission.png")

                                    submit_clicked = True
                                    break
                            except Exception as e:
                                print(f"Error clicking submit button with text {submit_text}: {e}")
                                continue

                        if submit_clicked:
                            break
                except Exception as e:
                    print(f"Error searching for button with text {submit_text}: {e}")
                    continue

            # If exact text match didn't work, try the standard selectors
            if not submit_clicked:
                print("Exact text match didn't work, trying standard selectors...")

                for selector in submit_selectors:
                    try:
                        # Handle special case for text containing selectors
                        if 'contains' in selector:
                            text = selector.split("'")[1]
                            buttons = self.driver.execute_script(f"""
                                return Array.from(document.querySelectorAll('button, input[type="submit"], a.button, .btn, [role="button"], .submit, input[type="button"]')).filter(el =>
                                    el.textContent.toLowerCase().includes('{text.lower()}') ||
                                    (el.value && el.value.toLowerCase().includes('{text.lower()}'))
                                );
                            """)
                        else:
                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)

                        if buttons:
                            for button in buttons:
                                try:
                                    if button.is_displayed() and button.is_enabled():
                                        # Scroll button into view
                                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                                        time.sleep(1)  # Wait for scroll

                                        # Click the button
                                        print(f"Clicking submit button with selector: {selector}")
                                        print("Waiting 5 seconds before clicking submit button...")
                                        time.sleep(5)  # Add a 5-second delay before clicking

                                        # Try different click methods
                                        try:
                                            # Regular click
                                            button.click()
                                        except Exception as click_error:
                                            print(f"Regular click failed: {click_error}")
                                            try:
                                                # JavaScript click
                                                self.driver.execute_script("arguments[0].click();", button)
                                                print("Used JavaScript click instead")
                                            except Exception as js_click_error:
                                                print(f"JavaScript click also failed: {js_click_error}")
                                                raise

                                        # Wait for form submission with standard delay
                                        time.sleep(3)

                                        # Add a 10-second delay after form submission as requested by user
                                        print(f"Waiting 10 seconds after form submission to observe results...")
                                        for i in range(10, 0, -1):
                                            print(f"⏱️ {i} seconds remaining...")
                                            time.sleep(1)
                                        print(f"✅ 10-second observation period complete")

                                        # Take a screenshot after submission
                                        self.driver.save_screenshot("after_submission.png")

                                        submit_clicked = True
                                        break
                                except Exception as e:
                                    print(f"Error clicking submit button with selector {selector}: {e}")
                                    continue
                    except Exception as e:
                        print(f"Error with submit selector {selector}: {e}")
                        continue

                    if submit_clicked:
                        break

            # If we couldn't click submit, try to submit the form directly
            if not submit_clicked:
                # Check again if form submission is enabled in settings
                submit_form = self.settings.get('submit_form', True)
                if not submit_form:
                    print("⚠️ Form submission is disabled in settings. Skipping direct form submission.")
                    # We already took a screenshot earlier, so no need to take another one
                    return True, "Form filled successfully but not submitted (submit_form setting is disabled)"

                try:
                    print("Trying to submit form directly...")
                    # Try to find the form element
                    forms = self.driver.find_elements(By.TAG_NAME, "form")
                    if forms:
                        for form in forms:
                            try:
                                # Check if this form contains any of our filled fields
                                if any(field_type in filled_fields for field_type in ["name", "email", "message"]):
                                    print("Submitting form directly")
                                    print("Waiting 5 seconds before direct form submission...")
                                    time.sleep(5)  # Add a 5-second delay before submission
                                    self.driver.execute_script("arguments[0].submit();", form)

                                    # Wait for form submission with standard delay
                                    time.sleep(3)

                                    # Add a 10-second delay after form submission as requested by user
                                    print(f"Waiting 10 seconds after direct form submission to observe results...")
                                    for i in range(10, 0, -1):
                                        print(f"⏱️ {i} seconds remaining...")
                                        time.sleep(1)
                                    print(f"✅ 10-second observation period complete")

                                    # Take a screenshot after submission
                                    self.driver.save_screenshot("after_direct_submission.png")

                                    submit_clicked = True
                                    break
                            except Exception as e:
                                print(f"Error submitting form directly: {e}")
                                continue
                except Exception as e:
                    print(f"Error finding forms for direct submission: {e}")

            # Check for success indicators
            success_indicators = [
                ".success",
                ".thank-you",
                ".thank_you",
                ".thanks",
                ".confirmation",
                "div:contains('Thank you')",
                "div:contains('Message sent')",
                "div:contains('Form submitted')",
                "div:contains('Success')"
            ]

            success_found = False
            for selector in success_indicators:
                try:
                    # Handle special case for text containing selectors
                    if 'contains' in selector:
                        text = selector.split("'")[1]
                        elements = self.driver.execute_script(f"""
                            return Array.from(document.querySelectorAll('div')).filter(el =>
                                el.textContent.toLowerCase().includes('{text.lower()}')
                            );
                        """)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                    if elements and any(el.is_displayed() for el in elements):
                        success_found = True
                        print(f"Found success indicator with selector: {selector}")
                        break
                except Exception as e:
                    print(f"Error checking success indicator {selector}: {e}")
                    continue

            # Determine result
            if submit_clicked:
                if success_found:
                    # Update the processing stage in the status
                    self._update_current_status({
                        "current_contact_id": self.current_contact_id,
                        "processing_stage": "completed",
                        "form_submission_success": True,
                        "last_updated": datetime.now().isoformat()
                    })

                    # Update the status in Supabase
                    if hasattr(self, 'current_contact_id') and self.current_contact_id:
                        self._update_status(self.current_contact_id, "contact_form_submitted", True, "Form submitted successfully with confirmation")

                    # Update submission log
                    self.submission_log["form_submitted"] = True
                    self.submission_log["submission_result"] = "Success - Form submitted with confirmation"

                    # Create a detailed log entry for the form submission result
                    result_log = f"""
==========================================================
✅ FORM SUBMISSION SUCCESSFUL - CONTACT ID: {self.current_contact_id}
==========================================================
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Website: {self.driver.current_url}
👤 Contact: {self.submission_log["form_data"].get("name", "Unknown")}
📧 Email: {self.submission_log["form_data"].get("email", "Unknown")}
📞 Phone: {self.submission_log["form_data"].get("phone", "Unknown")}

Fields successfully filled:
{chr(10).join([f"- {field['type']}: '{field['value']}'" for field in self.submission_log["fields_filled"]])}

Result: Form submitted successfully with confirmation
==========================================================
"""
                    print(result_log)

                    # Also log to the logger if available
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.info(result_log)

                    return True, "Form submitted successfully with confirmation"
                else:
                    # Check for error messages that might indicate failure
                    error_indicators = [
                        ".error",
                        ".form-error",
                        ".alert-danger",
                        ".validation-error",
                        "div:contains('Error')",
                        "div:contains('Failed')",
                        "div:contains('Invalid')",
                        "div:contains('Please try again')",
                        "div:contains('Problem')"
                    ]

                    error_found = False
                    for selector in error_indicators:
                        try:
                            # Handle special case for text containing selectors
                            if 'contains' in selector:
                                text = selector.split("'")[1]
                                elements = self.driver.execute_script(f"""
                                    return Array.from(document.querySelectorAll('div')).filter(el =>
                                        el.textContent.toLowerCase().includes('{text.lower()}')
                                    );
                                """)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

                            if elements and any(el.is_displayed() for el in elements):
                                error_found = True
                                print(f"Found error indicator with selector: {selector}")
                                break
                        except Exception as e:
                            print(f"Error checking error indicator {selector}: {e}")
                            continue

                    if error_found:
                        # Update the processing stage in the status to show error
                        self._update_current_status({
                            "current_contact_id": self.current_contact_id,
                            "processing_stage": "error",
                            "form_submission_success": False,
                            "last_updated": datetime.now().isoformat()
                        })

                        # Update the status in Supabase
                        if hasattr(self, 'current_contact_id') and self.current_contact_id:
                            self._update_status(self.current_contact_id, "contact_form_submitted", False, "Form submission failed - error message detected")

                        # Update submission log
                        self.submission_log["form_submitted"] = False
                        self.submission_log["submission_result"] = "Failed - Error message detected on page"

                        # Add explicit log message for live tracking panel
                        error_message = "Form submission failed - error message detected on page"
                        print(f"Failed to submit form: {error_message}")

                        # Create a detailed log entry for the form submission failure
                        result_log = f"""
==========================================================
❌ FORM SUBMISSION FAILED - CONTACT ID: {self.current_contact_id}
==========================================================
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Website: {self.driver.current_url}
👤 Contact: {self.submission_log["form_data"].get("name", "Unknown")}
📧 Email: {self.submission_log["form_data"].get("email", "Unknown")}
📞 Phone: {self.submission_log["form_data"].get("phone", "Unknown")}

Fields attempted:
{chr(10).join([f"- {field}" for field in self.submission_log["fields_attempted"]])}

Fields successfully filled:
{chr(10).join([f"- {field['type']}: '{field['value']}'" for field in self.submission_log["fields_filled"]]) if self.submission_log["fields_filled"] else "None"}

Fields failed:
{chr(10).join([f"- {field}" for field in self.submission_log["fields_failed"]]) if self.submission_log["fields_failed"] else "None"}

Result: {error_message}
==========================================================
"""
                        print(result_log)

                        # Also log to the logger if available
                        if hasattr(self, 'logger') and self.logger:
                            self.logger.error(result_log)

                        return False, error_message
                    else:
                        # No success confirmation but also no error - mark as uncertain
                        self._update_current_status({
                            "current_contact_id": self.current_contact_id,
                            "processing_stage": "completed",
                            "form_submission_uncertain": True,
                            "last_updated": datetime.now().isoformat()
                        })

                        # Update the status in Supabase with uncertain flag
                        if hasattr(self, 'current_contact_id') and self.current_contact_id:
                            self._update_status(self.current_contact_id, "contact_form_submitted", "uncertain", "Form submitted but no confirmation found")

                        # Update submission log
                        self.submission_log["form_submitted"] = True
                        self.submission_log["submission_result"] = "Uncertain - Form submitted but no confirmation detected"

                        # Create a detailed log entry for the uncertain form submission
                        result_log = f"""
==========================================================
⚠️ FORM SUBMISSION UNCERTAIN - CONTACT ID: {self.current_contact_id}
==========================================================
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Website: {self.driver.current_url}
👤 Contact: {self.submission_log["form_data"].get("name", "Unknown")}
📧 Email: {self.submission_log["form_data"].get("email", "Unknown")}
📞 Phone: {self.submission_log["form_data"].get("phone", "Unknown")}

Fields successfully filled:
{chr(10).join([f"- {field['type']}: '{field['value']}'" for field in self.submission_log["fields_filled"]]) if self.submission_log["fields_filled"] else "None"}

Fields failed:
{chr(10).join([f"- {field}" for field in self.submission_log["fields_failed"]]) if self.submission_log["fields_failed"] else "None"}

Result: Form submitted but no confirmation detected
==========================================================
"""
                        print(result_log)

                        # Also log to the logger if available
                        if hasattr(self, 'logger') and self.logger:
                            self.logger.info(result_log)

                        return True, "Form submitted but no confirmation found - result uncertain"
            else:
                # Update the processing stage in the status with detailed error
                error_message = "Could not find or click submit button"
                self._update_current_status({
                    "current_contact_id": self.current_contact_id,
                    "processing_stage": "error",
                    "form_submission_success": False,
                    "error_message": error_message,
                    "last_updated": datetime.now().isoformat()
                })

                # Update the status in Supabase with detailed error
                if hasattr(self, 'current_contact_id') and self.current_contact_id:
                    self._update_status(self.current_contact_id, "contact_form_submitted", False, error_message)

                # Update submission log
                self.submission_log["form_submitted"] = False
                self.submission_log["submission_result"] = f"Failed - {error_message}"

                # Add explicit log message for live tracking panel
                print(f"Failed to submit form: {error_message}")

                # Create a detailed log entry for the form submission failure
                result_log = f"""
==========================================================
❌ FORM SUBMISSION FAILED - CONTACT ID: {self.current_contact_id}
==========================================================
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Website: {self.driver.current_url}
👤 Contact: {self.submission_log["form_data"].get("name", "Unknown")}
📧 Email: {self.submission_log["form_data"].get("email", "Unknown")}
📞 Phone: {self.submission_log["form_data"].get("phone", "Unknown")}

Fields attempted:
{chr(10).join([f"- {field}" for field in self.submission_log["fields_attempted"]])}

Fields successfully filled:
{chr(10).join([f"- {field['type']}: '{field['value']}'" for field in self.submission_log["fields_filled"]]) if self.submission_log["fields_filled"] else "None"}

Fields failed:
{chr(10).join([f"- {field}" for field in self.submission_log["fields_failed"]]) if self.submission_log["fields_failed"] else "None"}

Result: {error_message}
==========================================================
"""
                print(result_log)

                # Also log to the logger if available
                if hasattr(self, 'logger') and self.logger:
                    self.logger.error(result_log)

                return False, error_message

        except Exception as e:
            print(f"Error filling contact form: {e}")
            # Get detailed error information
            error_message = f"Error filling form: {str(e)}"
            import traceback
            error_details = traceback.format_exc()
            print(f"Error details: {error_details}")

            # Update the processing stage in the status with detailed error
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "error",
                "form_submission_success": False,
                "error_message": error_message,
                "last_updated": datetime.now().isoformat()
            })

            # Update the status in Supabase
            if hasattr(self, 'current_contact_id') and self.current_contact_id:
                self._update_status(self.current_contact_id, "contact_form_submitted", False, error_message)

            # Update submission log
            self.submission_log["form_submitted"] = False
            self.submission_log["submission_result"] = f"Failed - Exception: {error_message}"

            # Add explicit log message for live tracking panel
            print(f"Failed to submit form: {error_message}")

            # Create a detailed log entry for the exception
            result_log = f"""
==========================================================
❌ FORM SUBMISSION EXCEPTION - CONTACT ID: {self.current_contact_id}
==========================================================
🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 Website: {self.driver.current_url}
👤 Contact: {self.submission_log["form_data"].get("name", "Unknown")}
📧 Email: {self.submission_log["form_data"].get("email", "Unknown")}
📞 Phone: {self.submission_log["form_data"].get("phone", "Unknown")}

Exception: {error_message}
Details: {error_details}

Fields attempted:
{chr(10).join([f"- {field}" for field in self.submission_log["fields_attempted"]]) if hasattr(self, 'submission_log') and "fields_attempted" in self.submission_log else "None"}

Fields successfully filled:
{chr(10).join([f"- {field['type']}: '{field['value']}'" for field in self.submission_log["fields_filled"]]) if hasattr(self, 'submission_log') and "fields_filled" in self.submission_log and self.submission_log["fields_filled"] else "None"}

Result: Exception occurred during form submission
==========================================================
"""
            print(result_log)

            # Also log to the logger if available
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(result_log)

            return False, error_message

    def _press_enter_on_last_input(self, form_element):
        """Press Enter on the last input field of a form

        Args:
            form_element: Form element

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all input fields
            inputs = form_element.find_elements(By.CSS_SELECTOR, 'input:not([type="hidden"]):not([type="submit"]):not([type="button"])')
            if not inputs:
                return False

            # Get the last input field
            last_input = inputs[-1]

            # Press Enter
            last_input.send_keys(Keys.ENTER)
            print(f"Pressed Enter on last input field")
            return True
        except Exception as e:
            print(f"Error pressing Enter on last input: {e}")
            return False

    def _verify_submission_success(self):
        """Verify if form submission was successful with multiple methods

        Returns:
            True if submission was successful, False otherwise
        """
        # Method 1: Check for thank you page or success message
        success_indicators = [
            'thank you', 'thanks', 'success', 'received', 'submitted', 'sent', 'message sent',
            'confirmation', 'we\'ll be in touch', 'we will be in touch', 'we will contact you',
            'appreciate your interest', 'got your message', 'form received'
        ]

        page_text = self.driver.page_source.lower()
        if any(indicator in page_text for indicator in success_indicators):
            print("✅ Success indicator found in page text")
            return True

        # Method 2: Check for URL change
        if hasattr(self, 'pre_submission_url') and self.pre_submission_url != self.driver.current_url:
            print("✅ URL changed after submission")
            return True

        # Method 3: Check for form disappearance
        try:
            if hasattr(self, 'current_form') and self.current_form:
                # Try to find the form again
                form_id = self.current_form.get_attribute('id')
                if form_id:
                    try:
                        self.driver.find_element(By.ID, form_id)
                        # Form still exists, check if it's empty
                        inputs = self.current_form.find_elements(By.TAG_NAME, 'input')
                        textareas = self.current_form.find_elements(By.TAG_NAME, 'textarea')

                        # Check if inputs are cleared (might indicate success)
                        all_empty = True
                        for input_field in inputs:
                            if input_field.get_attribute('type') not in ['submit', 'button', 'hidden', 'checkbox', 'radio']:
                                value = input_field.get_attribute('value')
                                if value and value.strip():
                                    all_empty = False
                                    break

                        for textarea in textareas:
                            value = textarea.get_attribute('value')
                            if value and value.strip():
                                all_empty = False
                                break

                        if all_empty:
                            print("✅ Form was cleared after submission")
                            return True
                    except:
                        # Form no longer exists, likely submitted
                        print("✅ Form no longer exists after submission")
                        return True
        except:
            pass

        # Method 4: Check for AJAX success indicators
        try:
            success_elements = self.driver.find_elements(By.CSS_SELECTOR, '.success, .form-success, .message-success, .alert-success, .wpforms-confirmation-container, .wpcf7-mail-sent-ok')
            if success_elements:
                for element in success_elements:
                    if element.is_displayed():
                        print(f"✅ Success element found: {element.get_attribute('class')}")
                        return True
        except:
            pass

        # Method 5: Check for error messages (negative indicator)
        try:
            error_indicators = ['error', 'invalid', 'failed', 'not sent', 'problem']
            error_elements = self.driver.find_elements(By.CSS_SELECTOR, '.error, .form-error, .invalid-feedback, .alert-danger, .wpcf7-not-valid-tip')

            for element in error_elements:
                if element.is_displayed():
                    error_text = element.text.lower()
                    if any(indicator in error_text for indicator in error_indicators):
                        print(f"❌ Error element found: {error_text}")
                        return False
        except:
            pass

        # No clear success indicators
        print("⚠️ No clear success indicators found")
        return False

    def _generate_message(self, contact: Dict[str, Any]) -> str:
        """Generate personalized message based on contact data

        Args:
            contact: Contact data

        Returns:
            Personalized message
        """
        # If custom template is set, use it
        if self.contact_form_template:
            # Start with the template
            message = self.contact_form_template

            # Process newlines in the template (convert \n to actual newlines)
            message = message.replace('\\n', '\n')

            # Print the template after newline processing
            print(f"Template after newline processing: '{message}'")

            # Replace all placeholders with contact data
            # First, handle special placeholders
            message = message.replace("{your_name}", self.your_name)
            message = message.replace("{your_email}", self.settings.get('your_email', ''))
            message = message.replace("{phone}", self.settings.get('phone', ''))

            # Add support for new fields
            message = message.replace("{your_first_name}", self.settings.get('your_first_name', ''))
            message = message.replace("{your_last_name}", self.settings.get('your_last_name', ''))
            message = message.replace("{your_company}", self.settings.get('your_company', ''))

            # Replace {default_message} with a standard message if it exists in the template
            if "{default_message}" in message:
                default_message = "I came across your work and was impressed. I'd love to connect and discuss potential opportunities to collaborate."
                message = message.replace("{default_message}", default_message)

            # Extract first name from full name if available - prioritize listing_name
            full_name = (contact.get("listing_name") or  # Prioritize listing_name from Supabase
                        contact.get("dentist_name_profile") or
                        contact.get("name") or
                        "")

            # Log the name being used for better debugging
            print(f"Using name for message template: '{full_name}'")

            first_name = full_name.split()[0] if full_name else ""
            message = message.replace("{first_name}", first_name)

            # Now dynamically replace any column name from the contact data
            for key, value in contact.items():
                if value:  # Only replace if the value is not empty
                    placeholder = "{" + key + "}"
                    if placeholder in message:
                        message = message.replace(placeholder, str(value))

            # Log which placeholders couldn't be replaced
            import re
            remaining_placeholders = re.findall(r'\{([^}]+)\}', message)
            if remaining_placeholders:
                print(f"Warning: The following placeholders could not be replaced: {', '.join(remaining_placeholders)}")
                print("Available contact fields: " + ", ".join(contact.keys()))

                # Replace remaining placeholders with empty strings
                for placeholder in remaining_placeholders:
                    message = message.replace("{" + placeholder + "}", "")

            return message

        # Otherwise use default template
        # Extract basic info with fallbacks
        company = contact.get("company", "your company")
        full_name = contact.get("name", "")
        first_name = full_name.split()[0] if full_name else ""

        if first_name:
            greeting = f"Hi {first_name},"
        else:
            greeting = "Hello,"

        # Use standard template for message body
        message_body = f"I came across {company} and was impressed by your work. "
        message_body += "I'd love to connect and discuss potential opportunities to collaborate."

        message = f"{greeting}\n\n"
        message += message_body
        message += "\n\nLooking forward to hearing from you,"

        # Use first and last name if available, otherwise use full name
        if self.settings.get('your_first_name') and self.settings.get('your_last_name'):
            message += f"\n{self.settings.get('your_first_name')} {self.settings.get('your_last_name')}"
        else:
            message += f"\n{self.your_name}"

        # Add company if available
        if self.settings.get('your_company'):
            message += f"\n{self.settings.get('your_company')}"

        # Add email and phone if available in settings
        if self.settings.get('your_email'):
            message += f"\n{self.settings.get('your_email')}"
        if self.settings.get('phone'):
            message += f"\n{self.settings.get('phone')}"

        return message

    def _connect_on_linkedin(self, contact: Dict[str, Any]) -> tuple[bool, str]:
        """Find user on LinkedIn and send connection request or message using intelligent LinkedIn integration if available

        Args:
            contact: Contact data

        Returns:
            Tuple of (success, message)
        """
        # Update the processing stage in the status
        self._update_current_status({
            "current_contact_id": self.current_contact_id,
            "processing_stage": "connecting_linkedin",
            "last_updated": datetime.now().isoformat()
        })

        # Use intelligent LinkedIn integration if available
        if self.intelligent_linkedin:
            print("Using intelligent LinkedIn integration for connecting with contact")
            success, message = self.intelligent_linkedin.connect_with_contact(contact)

            if success:
                print(f"Successfully connected with contact on LinkedIn using intelligent integration: {message}")
                return success, message
            else:
                print(f"Failed to connect with contact on LinkedIn using intelligent integration: {message}")
                print("Falling back to standard LinkedIn connection method")
        else:
            print("Intelligent LinkedIn integration not available, using standard method")

        if not self.linkedin_username or not self.linkedin_password:
            # Update the processing stage in the status
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "error",
                "last_updated": datetime.now().isoformat()
            })
            return False, "LinkedIn credentials not configured"

        try:
            # Login to LinkedIn if not already logged in
            if not self.linkedin_logged_in:
                self._login_to_linkedin()

            # Get contact name components
            first_name = contact.get("first_name", "")
            last_name = contact.get("last_name", "")
            full_name = contact.get("name", "")
            listing_name = contact.get("listing_name", "")
            company = contact.get("company", "")
            business_name = contact.get("listing_business_name", "")

            # Extract name from listing_name if available
            extracted_name = ""
            if listing_name:
                # Remove everything after a comma if present
                if "," in listing_name:
                    extracted_name = listing_name.split(",")[0].strip()
                else:
                    extracted_name = listing_name.strip()
                print(f"Extracted name from listing_name: {extracted_name}")

            # Define multiple search strategies to try in order
            search_strategies = []

            # Extract components for search
            company_term = company or business_name or ""

            # Strategy 1: First name + Last name + Company (most specific)
            if first_name and last_name and company_term:
                search_strategies.append({
                    "term": f"{first_name} {last_name} {company_term}",
                    "description": "First name + Last name + Company"
                })

            # Strategy 2: First name + Last name
            if first_name and last_name:
                search_strategies.append({
                    "term": f"{first_name} {last_name}",
                    "description": "First name + Last name"
                })

            # Strategy 3: Extracted name from listing_name + Company
            if extracted_name and company_term:
                search_strategies.append({
                    "term": f"{extracted_name} {company_term}",
                    "description": "Extracted name + Company"
                })

            # Strategy 4: Extracted name only
            if extracted_name:
                search_strategies.append({
                    "term": extracted_name,
                    "description": "Extracted name only"
                })

            # Strategy 5: Full name + Company
            if full_name and company_term:
                search_strategies.append({
                    "term": f"{full_name} {company_term}",
                    "description": "Full name + Company"
                })

            # Strategy 6: Full name only
            if full_name:
                search_strategies.append({
                    "term": full_name,
                    "description": "Full name only"
                })

            # Strategy 7: Listing name + Company
            if listing_name and company_term:
                search_strategies.append({
                    "term": f"{listing_name} {company_term}",
                    "description": "Listing name + Company"
                })

            # Strategy 8: Listing name only
            if listing_name:
                search_strategies.append({
                    "term": listing_name,
                    "description": "Listing name only"
                })

            # Strategy 9: Company only (least specific)
            if company_term:
                search_strategies.append({
                    "term": company_term,
                    "description": "Company only"
                })

            if not search_strategies:
                print("No search strategies available - insufficient contact data")
                return False, "No name or company provided for LinkedIn search"

            print(f"Generated {len(search_strategies)} search strategies")

            # Variables to track best result across all search attempts
            overall_best_result = None
            overall_best_score = 0
            overall_best_name = ""
            overall_best_search_term = ""

            # Try each search strategy until we find a good match
            for strategy_index, strategy in enumerate(search_strategies):
                search_term = strategy["term"]
                description = strategy["description"]

                print(f"\n=== Search Strategy {strategy_index + 1}: {description} ===")
                print(f"Search term: '{search_term}'")

                # Navigate to LinkedIn search
                search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_term}"
                print(f"Navigating to search URL: {search_url}")
                self.driver.get(search_url)
                time.sleep(5)  # Wait longer for search results to load completely

                # Take a screenshot of the search results page for debugging
                screenshot_name = f"linkedin_search_results_{strategy_index + 1}.png"
                self.driver.save_screenshot(screenshot_name)
                print(f"Saved screenshot of search results to {screenshot_name}")

                # Check if we have any search results
                try:
                    no_results = self.driver.find_elements(By.CSS_SELECTOR, ".search-reusables__no-results-message")
                    if no_results and any(elem.is_displayed() for elem in no_results):
                        print(f"No search results found for strategy {strategy_index + 1}")
                        continue  # Try next strategy
                except Exception as no_results_error:
                    print(f"Error checking for no results: {no_results_error}")

                # Get all search results
                try:
                    search_results = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".entity-result__item")))

                    if not search_results:
                        print(f"No search results found for strategy {strategy_index + 1}")
                        continue  # Try next strategy

                    print(f"Found {len(search_results)} search results")

                    # Analyze and score each result to find the best match
                    strategy_best_result = None
                    strategy_best_score = 0
                    strategy_best_name = ""

                    # Store all results for potential visual inspection
                    all_results = []

                    for i, result in enumerate(search_results[:10]):  # Analyze top 10 results
                        try:
                            # Extract name and details from the result
                            name_element = result.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                            result_name = name_element.text.strip()

                            # Try to get subtitle (usually contains company and title)
                            try:
                                subtitle_element = result.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                                result_subtitle = subtitle_element.text.strip()
                            except:
                                result_subtitle = ""

                            # Try to get location
                            try:
                                location_element = result.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                                result_location = location_element.text.strip()
                            except:
                                result_location = ""

                            print(f"Result {i+1}: Name: {result_name}, Details: {result_subtitle}, Location: {result_location}")

                            # Calculate match score
                            score = self._calculate_linkedin_match_score(
                                search_name=search_term,
                                result_name=result_name,
                                result_subtitle=result_subtitle,
                                result_location=result_location,
                                company=company_term,
                                first_name=first_name,
                                last_name=last_name
                            )

                            print(f"Match score for {result_name}: {score}")

                            # Store result for potential visual inspection
                            connect_available = False
                            message_available = False
                            try:
                                # Check if "Connect" button is available
                                connect_buttons = result.find_elements(By.XPATH, ".//button[contains(text(), 'Connect')]")
                                connect_available = len(connect_buttons) > 0

                                # Check if "Message" button is available
                                message_buttons = result.find_elements(By.XPATH, ".//button[contains(text(), 'Message')]")
                                message_available = len(message_buttons) > 0
                            except Exception as button_error:
                                print(f"Error checking buttons: {button_error}")

                            # Store result data
                            all_results.append({
                                "index": i,
                                "element": result,
                                "name": result_name,
                                "subtitle": result_subtitle,
                                "location": result_location,
                                "score": score,
                                "connect_available": connect_available,
                                "message_available": message_available
                            })

                            if score > strategy_best_score:
                                strategy_best_score = score
                                strategy_best_result = result
                                strategy_best_name = result_name

                            # Also update overall best if this is better
                            if score > overall_best_score:
                                overall_best_score = score
                                overall_best_result = result
                                overall_best_name = result_name
                                overall_best_search_term = search_term
                        except Exception as result_error:
                            print(f"Error analyzing search result {i+1}: {result_error}")

                    print(f"Best match for strategy {strategy_index + 1}: {strategy_best_name} with score {strategy_best_score}")

                    # If we found a very good match (score >= 60), we can stop searching
                    if strategy_best_score >= 60:
                        print(f"Found excellent match with score {strategy_best_score}, stopping search")
                        overall_best_result = strategy_best_result
                        overall_best_score = strategy_best_score
                        overall_best_name = strategy_best_name
                        overall_best_search_term = search_term
                        break

                    # If we found a good match (score >= 50) and this is the "first_name last_name" strategy,
                    # we'll keep it but continue searching for potentially better matches
                    elif strategy_best_score >= 50 and description == "First name + Last name":
                        print(f"Found good match with score {strategy_best_score} using first_name + last_name strategy")
                        if strategy_best_score > overall_best_score:
                            overall_best_result = strategy_best_result
                            overall_best_score = strategy_best_score
                            overall_best_name = strategy_best_name
                            overall_best_search_term = search_term

                    # If we didn't find a good match but have results, try the visual inspection approach
                    elif all_results and strategy_best_score < 50:
                        print("\n=== PERFORMING VISUAL INSPECTION OF RESULTS ===")
                        # Use company from contact data if available, otherwise use the company term from search
                        company_info = company if company else company_term
                        better_match = self._visually_inspect_linkedin_results(all_results, first_name, last_name, company_info)
                        if better_match:
                            print(f"Visual inspection found better match: {better_match['name']} with score {better_match['score']}")
                            if better_match['score'] > overall_best_score:
                                overall_best_result = better_match['element']
                                overall_best_score = better_match['score']
                                overall_best_name = better_match['name']
                                overall_best_search_term = search_term

                except Exception as search_error:
                    print(f"Error processing search results for strategy {strategy_index + 1}: {search_error}")
                    continue  # Try next strategy

            # After trying all strategies, use the best result we found
            if overall_best_result and overall_best_score >= 40:  # Minimum threshold for a match
                print(f"\n=== FINAL RESULT ===")
                print(f"Best match across all strategies: {overall_best_name} with score {overall_best_score}")
                print(f"Found using search term: '{overall_best_search_term}'")

                # Navigate back to the search results page where we found the best match
                if search_term != overall_best_search_term:
                    search_url = f"https://www.linkedin.com/search/results/people/?keywords={overall_best_search_term}"
                    print(f"Navigating back to best search results: {search_url}")
                    self.driver.get(search_url)
                    time.sleep(5)

                    # Find the result again
                    search_results = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".entity-result__item")))
                    for result in search_results:
                        try:
                            name_element = result.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                            if name_element.text.strip() == overall_best_name:
                                overall_best_result = result
                                break
                        except:
                            continue

                first_result = overall_best_result
            elif search_strategies:
                # If we didn't find a good match but have search results from the last strategy
                print("\n=== FINAL RESULT ===")
                print("No good match found across all strategies, using first result from last search")

                # Get the first result from the current page
                try:
                    search_results = self.driver.find_elements(By.CSS_SELECTOR, ".entity-result__item")
                    if search_results:
                        first_result = search_results[0]

                        # Get the name for logging
                        try:
                            name_element = first_result.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                            best_name = name_element.text.strip()
                            print(f"Using result: {best_name}")
                        except:
                            best_name = "Unknown"
                            print("Using unknown result")
                    else:
                        print("No search results found in final attempt")
                        return False, "No LinkedIn search results found across all search strategies"
                except Exception as final_error:
                    print(f"Error getting final result: {final_error}")
                    return False, f"Error finding LinkedIn search results: {str(final_error)}"
            else:
                print("No search results found across all strategies")
                return False, "No LinkedIn search results found across all search strategies"

            # Get the name of the person for logging
            try:
                name_element = first_result.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                person_name = name_element.text.strip()
                print(f"Found LinkedIn profile: {person_name}")

                # Get the profile URL for direct visit if needed
                profile_url = name_element.get_attribute("href")
                print(f"Profile URL: {profile_url}")
            except Exception as name_error:
                person_name = "Unknown"
                profile_url = None
                print(f"Could not get person name: {name_error}")

                # First check if we can send a direct message (already connected)
                print("Checking if we can send a direct message (already connected)...")
                message_button = None

                # List of possible selectors for the Message button
                message_button_selectors = [
                    "button.artdeco-button[aria-label*='Message']",
                    "button.artdeco-button[aria-label*='message']",
                    "button[data-control-name='message']",
                    ".message-anywhere-button",
                    "button:contains('Message')"
                ]

                # Try each message button selector
                for selector in message_button_selectors:
                    try:
                        # Use JavaScript to find buttons with text containing 'Message'
                        if 'contains' in selector:
                            text = selector.split("'")[1]
                            buttons = self.driver.execute_script(f"""
                                return Array.from(document.querySelectorAll('button')).filter(button =>
                                    button.textContent.includes('{text}')
                                );
                            """)
                            if buttons:
                                message_button = buttons[0]
                                print(f"Found Message button using JavaScript with text: {text}")
                                break
                        else:
                            buttons = first_result.find_elements(By.CSS_SELECTOR, selector)
                            if buttons:
                                message_button = buttons[0]
                                print(f"Found Message button using selector: {selector}")
                                break
                    except Exception as selector_error:
                        print(f"Error with message selector {selector}: {selector_error}")

                # If we found a Message button, we're already connected - send a direct message
                if message_button:
                    try:
                        print(f"Already connected to {person_name}, sending direct message...")
                        message_button.click()
                        time.sleep(2)

                        # Take a screenshot of the message dialog
                        self.driver.save_screenshot("linkedin_message_dialog.png")

                        # Find the message input field
                        message_input = None
                        message_input_selectors = [
                            "div.msg-form__contenteditable",
                            "div[role='textbox']",
                            "div.msg-form__msg-content-container",
                            "div.msg-form__message-texteditor"
                        ]

                        for selector in message_input_selectors:
                            try:
                                inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                if inputs:
                                    message_input = inputs[0]
                                    print(f"Found message input using selector: {selector}")
                                    break
                            except Exception as input_error:
                                print(f"Error with message input selector {selector}: {input_error}")

                        if message_input:
                            # Generate and enter personalized message
                            personalized_message = self._generate_linkedin_message(contact)
                            print(f"Generated personalized message: {personalized_message}")

                            # Use JavaScript to set the content of the contenteditable div
                            self.driver.execute_script(f"""
                                arguments[0].innerHTML = "{personalized_message.replace('"', '\\"')}";
                                arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            """, message_input)
                            time.sleep(1)

                            # Find and click the Send button
                            send_button = None
                            send_button_selectors = [
                                "button.msg-form__send-button",
                                "button[type='submit']",
                                "button:contains('Send')"
                            ]

                            for selector in send_button_selectors:
                                try:
                                    if 'contains' in selector:
                                        text = selector.split("'")[1]
                                        buttons = self.driver.execute_script(f"""
                                            return Array.from(document.querySelectorAll('button')).filter(button =>
                                                button.textContent.includes('{text}')
                                            );
                                        """)
                                        if buttons:
                                            send_button = buttons[0]
                                            break
                                    else:
                                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                        if buttons:
                                            send_button = buttons[0]
                                            break
                                except Exception as send_button_error:
                                    print(f"Error with send button selector {selector}: {send_button_error}")

                            if send_button:
                                send_button.click()
                                time.sleep(2)
                                self.driver.save_screenshot("linkedin_after_message_sent.png")
                                print(f"Direct message sent to {person_name}")

                                # Update the processing stage in the status
                                self._update_current_status({
                                    "current_contact_id": self.current_contact_id,
                                    "processing_stage": "completed",
                                    "last_updated": datetime.now().isoformat()
                                })

                                # Update the status in Supabase
                                self._update_status(self.current_contact_id, "linkedin_connected", True, f"Direct message sent to {person_name}")
                                self._update_status(self.current_contact_id, "linkedin_message_sent", True, f"Direct message sent to {person_name}")

                                return True, f"Direct message sent to {person_name} on LinkedIn"
                            else:
                                print("Could not find Send button for direct message")
                        else:
                            print("Could not find message input field")
                    except Exception as message_error:
                        print(f"Error sending direct message: {message_error}")
                        traceback.print_exc()

                # If we couldn't send a direct message, try to connect
                print("Looking for Connect button...")
                connect_button = None

                # List of possible selectors for the Connect button
                connect_button_selectors = [
                    "button.artdeco-button[aria-label*='Connect']",
                    "button.artdeco-button[aria-label*='connect']",
                    "button[data-control-name='connect']",
                    ".artdeco-dropdown__item[aria-label*='Connect']",
                    ".pvs-profile-actions button:nth-child(1)",  # First action button
                    ".pvs-profile-actions__action button",  # Any action button
                    "button:contains('Connect')"  # Button with Connect text
                ]

                # Try each selector
                for selector in connect_button_selectors:
                    try:
                        # Use JavaScript to find buttons with text containing 'Connect'
                        if 'contains' in selector:
                            text = selector.split("'")[1]
                            buttons = self.driver.execute_script(f"""
                                return Array.from(document.querySelectorAll('button')).filter(button =>
                                    button.textContent.includes('{text}')
                                );
                            """)
                            if buttons:
                                connect_button = buttons[0]
                                print(f"Found Connect button using JavaScript with text: {text}")
                                break
                        else:
                            buttons = first_result.find_elements(By.CSS_SELECTOR, selector)
                            if buttons:
                                connect_button = buttons[0]
                                print(f"Found Connect button using selector: {selector}")
                                break
                    except Exception as selector_error:
                        print(f"Error with selector {selector}: {selector_error}")

                # If we need to visit the profile directly
                if not connect_button and not message_button and profile_url:
                    print(f"No connect or message button found in search results, visiting profile directly: {profile_url}")
                    self.driver.get(profile_url)
                    time.sleep(3)
                    self.driver.save_screenshot("linkedin_profile_direct.png")

                    # Try to find message or connect buttons on the profile page
                    for selector in message_button_selectors:
                        try:
                            if 'contains' in selector:
                                text = selector.split("'")[1]
                                buttons = self.driver.execute_script(f"""
                                    return Array.from(document.querySelectorAll('button')).filter(button =>
                                        button.textContent.includes('{text}')
                                    );
                                """)
                                if buttons:
                                    message_button = buttons[0]
                                    print(f"Found Message button on profile using JavaScript with text: {text}")
                                    break
                            else:
                                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                if buttons:
                                    message_button = buttons[0]
                                    print(f"Found Message button on profile using selector: {selector}")
                                    break
                        except Exception as selector_error:
                            print(f"Error with message selector on profile {selector}: {selector_error}")

                    # If we found a message button on the profile, use it
                    if message_button:
                        try:
                            print(f"Already connected to {person_name}, sending direct message from profile...")
                            message_button.click()
                            time.sleep(2)
                            self.driver.save_screenshot("linkedin_message_dialog_from_profile.png")

                            # Handle the message dialog (reusing code from above)
                            # Find the message input field
                            message_input = None
                            for selector in message_input_selectors:
                                try:
                                    inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    if inputs:
                                        message_input = inputs[0]
                                        print(f"Found message input on profile using selector: {selector}")
                                        break
                                except Exception as input_error:
                                    print(f"Error with message input selector on profile {selector}: {input_error}")

                            if message_input:
                                # Generate and enter personalized message
                                personalized_message = self._generate_linkedin_message(contact)
                                print(f"Generated personalized message for profile: {personalized_message}")

                                # Use JavaScript to set the content of the contenteditable div
                                self.driver.execute_script(f"""
                                    arguments[0].innerHTML = "{personalized_message.replace('"', '\\"')}";
                                    arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                                """, message_input)
                                time.sleep(1)

                                # Find and click the Send button
                                send_button = None
                                for selector in send_button_selectors:
                                    try:
                                        if 'contains' in selector:
                                            text = selector.split("'")[1]
                                            buttons = self.driver.execute_script(f"""
                                                return Array.from(document.querySelectorAll('button')).filter(button =>
                                                    button.textContent.includes('{text}')
                                                );
                                            """)
                                            if buttons:
                                                send_button = buttons[0]
                                                break
                                        else:
                                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                            if buttons:
                                                send_button = buttons[0]
                                                break
                                    except Exception as send_button_error:
                                        print(f"Error with send button selector on profile {selector}: {send_button_error}")

                                if send_button:
                                    send_button.click()
                                    time.sleep(2)
                                    self.driver.save_screenshot("linkedin_after_message_sent_from_profile.png")
                                    print(f"Direct message sent to {person_name} from profile")

                                    # Update the processing stage in the status
                                    self._update_current_status({
                                        "current_contact_id": self.current_contact_id,
                                        "processing_stage": "completed",
                                        "last_updated": datetime.now().isoformat()
                                    })

                                    # Update the status in Supabase
                                    self._update_status(self.current_contact_id, "linkedin_connected", True, f"Direct message sent to {person_name} from profile")
                                    self._update_status(self.current_contact_id, "linkedin_message_sent", True, f"Direct message sent to {person_name} from profile")

                                    return True, f"Direct message sent to {person_name} on LinkedIn from profile"
                                else:
                                    print("Could not find Send button for direct message on profile")
                            else:
                                print("Could not find message input field on profile")
                        except Exception as message_error:
                            print(f"Error sending direct message from profile: {message_error}")
                            traceback.print_exc()

                    # If we couldn't send a message, try to find connect button on profile
                    if not message_button:
                        for selector in connect_button_selectors:
                            try:
                                if 'contains' in selector:
                                    text = selector.split("'")[1]
                                    buttons = self.driver.execute_script(f"""
                                        return Array.from(document.querySelectorAll('button')).filter(button =>
                                            button.textContent.includes('{text}')
                                        );
                                    """)
                                    if buttons:
                                        connect_button = buttons[0]
                                        print(f"Found Connect button on profile using JavaScript with text: {text}")
                                        break
                                else:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    if buttons:
                                        connect_button = buttons[0]
                                        print(f"Found Connect button on profile using selector: {selector}")
                                        break
                            except Exception as selector_error:
                                print(f"Error with connect selector on profile {selector}: {selector_error}")

                # If we found a Connect button, click it
                if connect_button:
                    try:
                        print("Clicking Connect button...")
                        connect_button.click()
                        time.sleep(2)  # Wait longer for the modal to appear

                        # Take a screenshot after clicking Connect
                        self.driver.save_screenshot("linkedin_after_connect_click.png")
                        print("Saved screenshot after clicking Connect button")

                        # Add personalized note
                        try:
                            print("Looking for 'Add a note' button...")

                            # Try different selectors for the Add a note button
                            add_note_selectors = [
                                "button[aria-label*='Add a note']",
                                "button.artdeco-button[aria-label*='note']",
                                "button.artdeco-modal__confirm-dialog-btn",
                                "button.artdeco-button--secondary",
                                "button:nth-child(1)"  # First button in the modal
                            ]

                            add_note_button = None
                            for selector in add_note_selectors:
                                try:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    for button in buttons:
                                        if "note" in button.text.lower() or "message" in button.text.lower():
                                            add_note_button = button
                                            print(f"Found 'Add a note' button with text: {button.text}")
                                            break
                                    if add_note_button:
                                        break
                                except Exception as note_selector_error:
                                    print(f"Error with note selector {selector}: {note_selector_error}")

                            if add_note_button:
                                add_note_button.click()
                                time.sleep(1)

                                # Take a screenshot after clicking Add a note
                                self.driver.save_screenshot("linkedin_add_note.png")
                                print("Saved screenshot after clicking Add a note button")

                                # Find the message field
                                print("Looking for message field...")
                                message_field = None
                                message_field_selectors = [
                                    "textarea#custom-message",
                                    "textarea.connect-button-send-invite__custom-message",
                                    "textarea[name='message']",
                                    "textarea"
                                ]

                                for selector in message_field_selectors:
                                    try:
                                        fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                        if fields:
                                            message_field = fields[0]
                                            print(f"Found message field using selector: {selector}")
                                            break
                                    except Exception as field_error:
                                        print(f"Error with message field selector {selector}: {field_error}")

                                if message_field:
                                    # Generate and enter personalized message
                                    personalized_message = self._generate_linkedin_message(contact)
                                    print(f"Generated personalized message: {personalized_message}")

                                    message_field.clear()
                                    message_field.send_keys(personalized_message)
                                    time.sleep(1)

                                    # Find and click the Send button
                                    print("Looking for Send button...")
                                    send_button = None
                                    send_button_selectors = [
                                        "button[aria-label*='Send']",
                                        "button[aria-label*='send']",
                                        "button.artdeco-button--primary",
                                        "button.artdeco-modal__confirm-dialog-btn",
                                        "button:nth-child(2)"  # Second button in the modal
                                    ]

                                    for selector in send_button_selectors:
                                        try:
                                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                            for button in buttons:
                                                if "send" in button.text.lower() or "done" in button.text.lower():
                                                    send_button = button
                                                    print(f"Found Send button with text: {button.text}")
                                                    break
                                            if send_button:
                                                break
                                        except Exception as send_button_error:
                                            print(f"Error with send button selector {selector}: {send_button_error}")

                                    if send_button:
                                        send_button.click()
                                        time.sleep(2)

                                        # Take a screenshot after sending
                                        self.driver.save_screenshot("linkedin_after_send.png")
                                        print("Saved screenshot after clicking Send button")

                                        # Update the processing stage in the status
                                        self._update_current_status({
                                            "current_contact_id": self.current_contact_id,
                                            "processing_stage": "completed",
                                            "last_updated": datetime.now().isoformat()
                                        })

                                        # Update the status in Supabase
                                        self._update_status(self.current_contact_id, "linkedin_connected", True, f"Connection request sent to {person_name} with personalized message")

                                        return True, f"LinkedIn connection request sent to {person_name} with personalized message"
                                    else:
                                        print("Could not find Send button")
                                        # Try to find any button that might be the send button
                                        try:
                                            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
                                            for button in buttons:
                                                if "send" in button.text.lower() or "done" in button.text.lower():
                                                    print(f"Found potential Send button with text: {button.text}")
                                                    button.click()
                                                    time.sleep(2)
                                                    self.driver.save_screenshot("linkedin_after_potential_send.png")
                                                    return True, f"LinkedIn connection request possibly sent to {person_name} with personalized message"
                                        except Exception as fallback_send_error:
                                            print(f"Error with fallback send button search: {fallback_send_error}")
                                else:
                                    print("Could not find message field")
                            else:
                                print("Could not find 'Add a note' button, trying to send without note")
                        except Exception as note_error:
                            print(f"Error adding note: {note_error}")
                            traceback.print_exc()

                        # If adding a note fails, just try to send the connection request directly
                        try:
                            print("Looking for Send/Connect button to send without note...")
                            send_button = None
                            send_button_selectors = [
                                "button[aria-label*='Send']",
                                "button[aria-label*='send']",
                                "button.artdeco-button--primary",
                                "button.artdeco-modal__confirm-dialog-btn",
                                "button:nth-child(2)"  # Second button in the modal
                            ]

                            for selector in send_button_selectors:
                                try:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    for button in buttons:
                                        if "send" in button.text.lower() or "connect" in button.text.lower() or "done" in button.text.lower():
                                            send_button = button
                                            print(f"Found Send/Connect button with text: {button.text}")
                                            break
                                    if send_button:
                                        break
                                except Exception as direct_send_error:
                                    print(f"Error with direct send button selector {selector}: {direct_send_error}")

                            if send_button:
                                send_button.click()
                                time.sleep(2)

                                # Take a screenshot after sending
                                self.driver.save_screenshot("linkedin_after_direct_send.png")
                                print("Saved screenshot after clicking Send/Connect button")

                                # Update the processing stage in the status
                                self._update_current_status({
                                    "current_contact_id": self.current_contact_id,
                                    "processing_stage": "completed",
                                    "last_updated": datetime.now().isoformat()
                                })

                                # Update the status in Supabase
                                self._update_status(self.current_contact_id, "linkedin_connected", True, f"Connection request sent to {person_name} without personalized message")

                                return True, f"LinkedIn connection request sent to {person_name} without personalized message"
                            else:
                                print("Could not find Send/Connect button")
                                # Try to find any button that might be the send button
                                try:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
                                    for button in buttons:
                                        if "send" in button.text.lower() or "connect" in button.text.lower() or "done" in button.text.lower():
                                            print(f"Found potential Send/Connect button with text: {button.text}")
                                            button.click()
                                            time.sleep(2)
                                            self.driver.save_screenshot("linkedin_after_potential_direct_send.png")
                                            return True, f"LinkedIn connection request possibly sent to {person_name} without personalized message"
                                except Exception as fallback_direct_send_error:
                                    print(f"Error with fallback direct send button search: {fallback_direct_send_error}")
                        except Exception as direct_send_attempt_error:
                            print(f"Error attempting to send without note: {direct_send_attempt_error}")
                            traceback.print_exc()

                        # If we got here, we couldn't send the connection request
                        self._update_current_status({
                            "current_contact_id": self.current_contact_id,
                            "processing_stage": "error",
                            "last_updated": datetime.now().isoformat()
                        })
                        return False, f"Could not send connection request to {person_name}"
                    except Exception as connect_click_error:
                        print(f"Error clicking Connect button: {connect_click_error}")
                        traceback.print_exc()
                        self.driver.save_screenshot("linkedin_connect_click_error.png")

                        # Update the processing stage in the status
                        self._update_current_status({
                            "current_contact_id": self.current_contact_id,
                            "processing_stage": "error",
                            "last_updated": datetime.now().isoformat()
                        })
                        return False, f"Error clicking Connect button for {person_name}: {str(connect_click_error)}"
                else:
                    print("Connect button not found, checking if already connected or if we need to visit profile")

                    # Check if we need to visit the profile first
                    try:
                        profile_link = first_result.find_element(By.CSS_SELECTOR, ".entity-result__title-text a")
                        profile_url = profile_link.get_attribute("href")
                        print(f"Visiting profile page: {profile_url}")

                        # Visit the profile page
                        self.driver.get(profile_url)
                        time.sleep(3)

                        # Take a screenshot of the profile page
                        self.driver.save_screenshot("linkedin_profile_page.png")
                        print("Saved screenshot of LinkedIn profile page")

                        # Try to find the Connect button on the profile page
                        print("Looking for Connect button on profile page...")
                        profile_connect_button = None

                        # Try to find the More button first (Connect might be in a dropdown)
                        more_button_selectors = [
                            "button.artdeco-dropdown__trigger",
                            "button.pvs-profile-actions__action",
                            "button.artdeco-button[aria-label*='More']"
                        ]

                        for selector in more_button_selectors:
                            try:
                                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for button in buttons:
                                    if "more" in button.text.lower() or "…" in button.text:
                                        print(f"Found More button with text: {button.text}")
                                        button.click()
                                        time.sleep(1)
                                        self.driver.save_screenshot("linkedin_more_dropdown.png")

                                        # Now look for Connect in the dropdown
                                        dropdown_items = self.driver.find_elements(By.CSS_SELECTOR, ".artdeco-dropdown__item")
                                        for item in dropdown_items:
                                            if "connect" in item.text.lower():
                                                print(f"Found Connect option in dropdown: {item.text}")
                                                item.click()
                                                time.sleep(1)
                                                self.driver.save_screenshot("linkedin_after_dropdown_connect.png")

                                                # Now look for the Add a note option
                                                try:
                                                    self._handle_linkedin_connect_modal(contact, person_name)
                                                    # Update the status in Supabase
                                                    self._update_status(self.current_contact_id, "linkedin_connected", True, f"Connection request sent to {person_name} from profile dropdown")

                                                    return True, f"LinkedIn connection request sent to {person_name} from profile page dropdown"
                                                except Exception as modal_error:
                                                    print(f"Error handling connect modal: {modal_error}")
                                                    traceback.print_exc()
                                                    return False, f"Error sending connection from profile dropdown: {str(modal_error)}"
                                        break
                            except Exception as more_button_error:
                                print(f"Error with more button selector {selector}: {more_button_error}")

                        # Try direct Connect button on profile
                        for selector in connect_button_selectors:
                            try:
                                if 'contains' in selector:
                                    text = selector.split("'")[1]
                                    buttons = self.driver.execute_script(f"""
                                        return Array.from(document.querySelectorAll('button')).filter(button =>
                                            button.textContent.includes('{text}')
                                        );
                                    """)
                                    if buttons:
                                        profile_connect_button = buttons[0]
                                        print(f"Found Connect button on profile using JavaScript with text: {text}")
                                        break
                                else:
                                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    if buttons:
                                        profile_connect_button = buttons[0]
                                        print(f"Found Connect button on profile using selector: {selector}")
                                        break
                            except Exception as profile_selector_error:
                                print(f"Error with profile selector {selector}: {profile_selector_error}")

                        if profile_connect_button:
                            profile_connect_button.click()
                            time.sleep(1)
                            self.driver.save_screenshot("linkedin_profile_connect_click.png")

                            try:
                                self._handle_linkedin_connect_modal(contact, person_name)
                                # Update the status in Supabase
                                self._update_status(self.current_contact_id, "linkedin_connected", True, f"Connection request sent to {person_name} from profile page")

                                return True, f"LinkedIn connection request sent to {person_name} from profile page"
                            except Exception as profile_modal_error:
                                print(f"Error handling connect modal from profile: {profile_modal_error}")
                                traceback.print_exc()
                                return False, f"Error sending connection from profile page: {str(profile_modal_error)}"
                        else:
                            # Check if we're already connected
                            try:
                                message_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='Message']")
                                if message_buttons:
                                    print(f"Found Message button - already connected to {person_name}")
                                    self._update_current_status({
                                        "current_contact_id": self.current_contact_id,
                                        "processing_stage": "completed",
                                        "last_updated": datetime.now().isoformat()
                                    })

                                    # Update the status in Supabase
                                    self._update_status(self.current_contact_id, "linkedin_connected", True, f"Already connected to {person_name}")

                                    return True, f"Already connected to {person_name} on LinkedIn"
                            except Exception as message_check_error:
                                print(f"Error checking if already connected: {message_check_error}")
                    except Exception as profile_visit_error:
                        print(f"Error visiting profile: {profile_visit_error}")
                        traceback.print_exc()

                    # Update the processing stage in the status
                    self._update_current_status({
                        "current_contact_id": self.current_contact_id,
                        "processing_stage": "error",
                        "last_updated": datetime.now().isoformat()
                    })
                    return False, f"Connect button not found for {person_name}"

            except Exception as search_error:
                print(f"Error finding search results: {search_error}")
                traceback.print_exc()
                self.driver.save_screenshot("linkedin_search_error.png")

                # Update the processing stage in the status
                self._update_current_status({
                    "current_contact_id": self.current_contact_id,
                    "processing_stage": "error",
                    "last_updated": datetime.now().isoformat()
                })
                return False, f"Error finding LinkedIn search results: {str(search_error)}"

        except Exception as e:
            print(f"Error connecting on LinkedIn: {e}")
            # Update the processing stage in the status
            self._update_current_status({
                "current_contact_id": self.current_contact_id,
                "processing_stage": "error",
                "last_updated": datetime.now().isoformat()
            })
            return False, f"Error connecting on LinkedIn: {str(e)}"

    def _save_cookies(self, domain: str) -> None:
        """Save cookies for a specific domain

        Args:
            domain: Domain to save cookies for (e.g., 'linkedin.com')
        """
        try:
            cookies_file = self.linkedin_cookies_file if 'linkedin' in domain else os.path.join(self.cookies_dir, f"{domain.replace('.', '_')}_cookies.pkl")

            # Get cookies for the domain
            cookies = [cookie for cookie in self.driver.get_cookies() if domain in cookie.get('domain', '')]

            # Save cookies to file
            with open(cookies_file, 'wb') as file:
                pickle.dump(cookies, file)

            print(f"Saved {len(cookies)} cookies for {domain}")
        except Exception as e:
            print(f"Error saving cookies for {domain}: {e}")

    def _load_cookies(self, domain: str) -> bool:
        """Load cookies for a specific domain

        Args:
            domain: Domain to load cookies for (e.g., 'linkedin.com')

        Returns:
            True if cookies were loaded successfully, False otherwise
        """
        try:
            cookies_file = self.linkedin_cookies_file if 'linkedin' in domain else os.path.join(self.cookies_dir, f"{domain.replace('.', '_')}_cookies.pkl")

            # Check if cookies file exists
            if not os.path.exists(cookies_file):
                print(f"No cookies file found for {domain}")
                return False

            # Load cookies from file
            with open(cookies_file, 'rb') as file:
                cookies = pickle.load(file)

            # Add cookies to browser
            for cookie in cookies:
                # Some cookies may cause issues, so we'll try to add each one separately
                try:
                    # Remove problematic keys that might cause issues
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Error adding cookie: {e}")

            print(f"Loaded {len(cookies)} cookies for {domain}")
            return True
        except Exception as e:
            print(f"Error loading cookies for {domain}: {e}")
            return False

    def _check_linkedin_login_status(self) -> bool:
        """Check if we're logged in to LinkedIn

        Returns:
            True if logged in, False otherwise
        """
        try:
            # Take a screenshot before checking login status
            self.driver.save_screenshot("linkedin_check_login_status.png")
            print("Saved screenshot before checking LinkedIn login status")

            # Navigate to LinkedIn homepage
            print("Navigating to LinkedIn feed page to check login status...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)

            # Take a screenshot after navigation
            self.driver.save_screenshot("linkedin_feed_page.png")
            print("Saved screenshot of LinkedIn feed page")

            # Check if we're on the feed page or login page
            current_url = self.driver.current_url
            print(f"Current URL: {current_url}")

            if "feed" in current_url:
                print("On feed page, logged in to LinkedIn")
                return True
            elif "login" in current_url:
                print("On login page, not logged in to LinkedIn")
                return False
            elif "checkpoint" in current_url:
                print("On checkpoint page, may need additional verification")
                return False
            else:
                print("Not on a recognized page, checking for logged-in elements")

                # Try multiple methods to check login status
                logged_in_indicators = [
                    # Method 1: Check for global navigation
                    {
                        "selector": By.ID,
                        "value": "global-nav",
                        "description": "global navigation bar"
                    },
                    # Method 2: Check for profile menu
                    {
                        "selector": By.CSS_SELECTOR,
                        "value": ".profile-rail-card",
                        "description": "profile rail card"
                    },
                    # Method 3: Check for messaging icon
                    {
                        "selector": By.CSS_SELECTOR,
                        "value": "li.global-nav__primary-item a[href='/messaging/']",
                        "description": "messaging icon"
                    },
                    # Method 4: Check for notifications icon
                    {
                        "selector": By.CSS_SELECTOR,
                        "value": "li.global-nav__primary-item a[href='/notifications/']",
                        "description": "notifications icon"
                    },
                    # Method 5: Check for search box
                    {
                        "selector": By.CSS_SELECTOR,
                        "value": "input.search-global-typeahead__input",
                        "description": "search box"
                    }
                ]

                for indicator in logged_in_indicators:
                    try:
                        element = self.driver.find_element(indicator["selector"], indicator["value"])
                        print(f"Found {indicator['description']}, logged in to LinkedIn")
                        return True
                    except Exception as indicator_error:
                        print(f"Could not find {indicator['description']}: {indicator_error}")

                # Check for login button (indicating not logged in)
                try:
                    login_button = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='login'], button[data-litms-control-urn='login-submit']")
                    if login_button:
                        print("Found login button, not logged in to LinkedIn")
                        return False
                except Exception as login_button_error:
                    print(f"Error checking for login button: {login_button_error}")

                # If we get here, we couldn't definitively determine login status
                print("Could not definitively determine LinkedIn login status, assuming not logged in")
                return False
        except Exception as e:
            print(f"Error checking LinkedIn login status: {e}")
            traceback.print_exc()
            return False

    def _login_to_linkedin(self) -> None:
        """Login to LinkedIn using credentials or cookies"""
        try:
            # Take a screenshot before login attempt
            self.driver.save_screenshot("linkedin_before_login.png")
            print("Saved screenshot before LinkedIn login attempt")

            # First try to use cookies
            print("Attempting to use saved LinkedIn cookies...")
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)

            # Try to load cookies
            cookies_loaded = self._load_cookies('linkedin.com')

            if cookies_loaded:
                print("LinkedIn cookies loaded, checking login status...")
                # Check if we're logged in
                self.driver.get("https://www.linkedin.com/feed/")
                time.sleep(3)

                # Take a screenshot after cookie login attempt
                self.driver.save_screenshot("linkedin_after_cookie_login.png")
                print("Saved screenshot after LinkedIn cookie login attempt")

                # Verify login status
                if self._check_linkedin_login_status():
                    print("Successfully logged in to LinkedIn using cookies")
                    self.linkedin_logged_in = True
                    return
                else:
                    print("Cookie login failed, will try with credentials")
            else:
                print("No valid LinkedIn cookies found, will try with credentials")

            # If cookies didn't work, log in with credentials
            print("Logging in to LinkedIn with credentials...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)

            # Take a screenshot of login page
            self.driver.save_screenshot("linkedin_login_page.png")
            print("Saved screenshot of LinkedIn login page")

            # Check if we're already on the feed page (already logged in)
            if "feed" in self.driver.current_url:
                print("Already logged in to LinkedIn")
                self.linkedin_logged_in = True
                return

            # Check if we're on the login page
            if "login" not in self.driver.current_url and "checkpoint" not in self.driver.current_url:
                print(f"Not on LinkedIn login page, current URL: {self.driver.current_url}")
                # Try to navigate to login page again
                self.driver.get("https://www.linkedin.com/login")
                time.sleep(3)

                # Take another screenshot
                self.driver.save_screenshot("linkedin_login_page_retry.png")
                print("Saved screenshot of LinkedIn login page retry")

            # Enter username
            try:
                print("Looking for username field...")
                username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
                username_field.clear()
                print(f"Entering LinkedIn username: {self.linkedin_username[:3]}***")
                username_field.send_keys(self.linkedin_username)
                print("Username entered")
            except Exception as username_error:
                print(f"Error finding username field: {username_error}")
                traceback.print_exc()

                # Try alternative selectors for username field
                try:
                    username_selectors = [
                        "input[name='session_key']",
                        "input[autocomplete='username']",
                        "input[type='email']",
                        "input[type='text']"
                    ]

                    for selector in username_selectors:
                        try:
                            fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if fields:
                                username_field = fields[0]
                                print(f"Found username field using selector: {selector}")
                                username_field.clear()
                                username_field.send_keys(self.linkedin_username)
                                print("Username entered using alternative selector")
                                break
                        except Exception as alt_username_error:
                            print(f"Error with username selector {selector}: {alt_username_error}")
                except Exception as alt_username_attempt_error:
                    print(f"Error attempting alternative username fields: {alt_username_attempt_error}")
                    self.linkedin_logged_in = False
                    return

            # Enter password
            try:
                print("Looking for password field...")
                password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
                password_field.clear()
                print("Entering LinkedIn password: ********")
                password_field.send_keys(self.linkedin_password)
                print("Password entered")
            except Exception as password_error:
                print(f"Error finding password field: {password_error}")
                traceback.print_exc()

                # Try alternative selectors for password field
                try:
                    password_selectors = [
                        "input[name='session_password']",
                        "input[autocomplete='current-password']",
                        "input[type='password']"
                    ]

                    for selector in password_selectors:
                        try:
                            fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if fields:
                                password_field = fields[0]
                                print(f"Found password field using selector: {selector}")
                                password_field.clear()
                                password_field.send_keys(self.linkedin_password)
                                print("Password entered using alternative selector")
                                break
                        except Exception as alt_password_error:
                            print(f"Error with password selector {selector}: {alt_password_error}")
                except Exception as alt_password_attempt_error:
                    print(f"Error attempting alternative password fields: {alt_password_attempt_error}")
                    self.linkedin_logged_in = False
                    return

            # Click login button
            try:
                print("Looking for login button...")
                login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
                print("Found login button, clicking...")
                login_button.click()
                print("Login button clicked")
            except Exception as login_button_error:
                print(f"Error finding login button: {login_button_error}")
                traceback.print_exc()

                # Try alternative selectors for login button
                try:
                    login_button_selectors = [
                        "button.sign-in-form__submit-button",
                        "button.btn__primary--large",
                        "button[aria-label*='Sign in']",
                        "button[data-litms-control-urn='login-submit']",
                        "button.artdeco-button--primary"
                    ]

                    for selector in login_button_selectors:
                        try:
                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if buttons:
                                login_button = buttons[0]
                                print(f"Found login button using selector: {selector}")
                                login_button.click()
                                print("Login button clicked using alternative selector")
                                break
                        except Exception as alt_login_button_error:
                            print(f"Error with login button selector {selector}: {alt_login_button_error}")
                except Exception as alt_login_button_attempt_error:
                    print(f"Error attempting alternative login buttons: {alt_login_button_attempt_error}")
                    self.linkedin_logged_in = False
                    return

            # Wait for login to complete
            print("Waiting for login to complete...")
            time.sleep(5)

            # Take a screenshot after login attempt
            self.driver.save_screenshot("linkedin_after_login.png")
            print("Saved screenshot after LinkedIn login attempt")

            # Check if login was successful
            if "feed" in self.driver.current_url or "checkpoint" in self.driver.current_url or self._check_linkedin_login_status():
                print("Successfully logged in to LinkedIn")
                self.linkedin_logged_in = True

                # Save cookies for future use
                print("Saving LinkedIn cookies for future use...")
                self._save_cookies('linkedin.com')
                print("LinkedIn cookies saved")
            else:
                print(f"Failed to login to LinkedIn, current URL: {self.driver.current_url}")
                self.linkedin_logged_in = False

                # Check for common login issues
                try:
                    # Check for CAPTCHA
                    captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, ".captcha-container, .recaptcha-container")
                    if captcha_elements:
                        print("CAPTCHA detected on LinkedIn login page. Manual login required.")

                    # Check for two-factor authentication
                    twofa_elements = self.driver.find_elements(By.CSS_SELECTOR, ".two-step-verification, .two-factor-auth")
                    if twofa_elements:
                        print("Two-factor authentication detected on LinkedIn. Manual login required.")

                    # Check for incorrect password
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".alert-content, .form__error--password")
                    if error_elements:
                        for error in error_elements:
                            print(f"Login error message: {error.text}")
                except Exception as check_error:
                    print(f"Error checking for login issues: {check_error}")

        except Exception as e:
            print(f"Error logging in to LinkedIn: {e}")
            traceback.print_exc()
            self.linkedin_logged_in = False

    def _handle_linkedin_connect_modal(self, contact: Dict[str, Any], person_name: str) -> bool:
        """Handle the LinkedIn connect modal dialog

        Args:
            contact: Contact data
            person_name: Name of the person to connect with

        Returns:
            True if connection request was sent, False otherwise
        """
        # Take a screenshot of the connect modal
        self.driver.save_screenshot("linkedin_connect_modal.png")
        print("Saved screenshot of LinkedIn connect modal")

        # Look for Add a note button
        try:
            print("Looking for 'Add a note' button in modal...")
            add_note_selectors = [
                "button[aria-label*='Add a note']",
                "button.artdeco-button[aria-label*='note']",
                "button.artdeco-modal__confirm-dialog-btn",
                "button.artdeco-button--secondary",
                "button:nth-child(1)"  # First button in the modal
            ]

            add_note_button = None
            for selector in add_note_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if "note" in button.text.lower() or "message" in button.text.lower():
                            add_note_button = button
                            print(f"Found 'Add a note' button with text: {button.text}")
                            break
                    if add_note_button:
                        break
                except Exception as note_selector_error:
                    print(f"Error with note selector {selector}: {note_selector_error}")

            if add_note_button:
                add_note_button.click()
                time.sleep(1)

                # Take a screenshot after clicking Add a note
                self.driver.save_screenshot("linkedin_modal_add_note.png")
                print("Saved screenshot after clicking Add a note button in modal")

                # Find the message field
                print("Looking for message field in modal...")
                message_field = None
                message_field_selectors = [
                    "textarea#custom-message",
                    "textarea.connect-button-send-invite__custom-message",
                    "textarea[name='message']",
                    "textarea"
                ]

                for selector in message_field_selectors:
                    try:
                        fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if fields:
                            message_field = fields[0]
                            print(f"Found message field in modal using selector: {selector}")
                            break
                    except Exception as field_error:
                        print(f"Error with message field selector {selector}: {field_error}")

                if message_field:
                    # Generate and enter personalized message
                    personalized_message = self._generate_linkedin_message(contact)
                    print(f"Generated personalized message for modal: {personalized_message}")

                    message_field.clear()
                    message_field.send_keys(personalized_message)
                    time.sleep(1)

                    # Find and click the Send button
                    print("Looking for Send button in modal...")
                    send_button = None
                    send_button_selectors = [
                        "button[aria-label*='Send']",
                        "button[aria-label*='send']",
                        "button.artdeco-button--primary",
                        "button.artdeco-modal__confirm-dialog-btn",
                        "button:nth-child(2)"  # Second button in the modal
                    ]

                    for selector in send_button_selectors:
                        try:
                            buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for button in buttons:
                                if "send" in button.text.lower() or "done" in button.text.lower():
                                    send_button = button
                                    print(f"Found Send button in modal with text: {button.text}")
                                    break
                            if send_button:
                                break
                        except Exception as send_button_error:
                            print(f"Error with send button selector {selector}: {send_button_error}")

                    if send_button:
                        send_button.click()
                        time.sleep(2)

                        # Take a screenshot after sending
                        self.driver.save_screenshot("linkedin_modal_after_send.png")
                        print("Saved screenshot after clicking Send button in modal")

                        # Update the processing stage in the status
                        self._update_current_status({
                            "current_contact_id": self.current_contact_id,
                            "processing_stage": "completed",
                            "last_updated": datetime.now().isoformat()
                        })
                        return True
                    else:
                        print("Could not find Send button in modal")
                else:
                    print("Could not find message field in modal")
            else:
                print("Could not find 'Add a note' button in modal, trying to send without note")
        except Exception as modal_note_error:
            print(f"Error adding note in modal: {modal_note_error}")
            traceback.print_exc()

        # If adding a note fails, just try to send the connection request directly
        try:
            print("Looking for Send/Connect button in modal to send without note...")
            send_button = None
            send_button_selectors = [
                "button[aria-label*='Send']",
                "button[aria-label*='send']",
                "button.artdeco-button--primary",
                "button.artdeco-modal__confirm-dialog-btn",
                "button:nth-child(2)"  # Second button in the modal
            ]

            for selector in send_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if "send" in button.text.lower() or "connect" in button.text.lower() or "done" in button.text.lower():
                            send_button = button
                            print(f"Found Send/Connect button in modal with text: {button.text}")
                            break
                    if send_button:
                        break
                except Exception as direct_send_error:
                    print(f"Error with direct send button selector {selector}: {direct_send_error}")

            if send_button:
                send_button.click()
                time.sleep(2)

                # Take a screenshot after sending
                self.driver.save_screenshot("linkedin_modal_after_direct_send.png")
                print("Saved screenshot after clicking Send/Connect button in modal")

                # Update the processing stage in the status
                self._update_current_status({
                    "current_contact_id": self.current_contact_id,
                    "processing_stage": "completed",
                    "last_updated": datetime.now().isoformat()
                })
                return True
            else:
                print("Could not find Send/Connect button in modal")
                # Try to find any button that might be the send button
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
                    for button in buttons:
                        if "send" in button.text.lower() or "connect" in button.text.lower() or "done" in button.text.lower():
                            print(f"Found potential Send/Connect button in modal with text: {button.text}")
                            button.click()
                            time.sleep(2)
                            self.driver.save_screenshot("linkedin_modal_after_potential_direct_send.png")
                            return True
                except Exception as fallback_direct_send_error:
                    print(f"Error with fallback direct send button search in modal: {fallback_direct_send_error}")
        except Exception as direct_send_attempt_error:
            print(f"Error attempting to send without note in modal: {direct_send_attempt_error}")
            traceback.print_exc()

        # If we got here, we couldn't send the connection request
        return False

    def _visually_inspect_linkedin_results(self, results: List[Dict], first_name: str, last_name: str, company: str) -> Dict:
        """Perform a more detailed visual inspection of LinkedIn search results

        This function uses additional heuristics to identify the correct profile when
        the standard scoring algorithm doesn't find a good match.

        Args:
            results: List of search result dictionaries
            first_name: Contact's first name
            last_name: Contact's last name
            company: Contact's company name

        Returns:
            The best match result dictionary or None if no good match found
        """
        print(f"Visually inspecting {len(results)} LinkedIn search results")

        # Sort results by score (highest first)
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)

        # Extract location information from company
        contact_city = ""
        contact_state = ""

        # Try to extract location from company name
        if "," in company:
            location_parts = company.split(",")[-1].strip().split()

            # Common state abbreviations
            state_abbrs = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
                          "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
                          "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
                          "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"]

            # Try to identify state in location parts
            for part in location_parts:
                part = part.strip().upper()
                if part in state_abbrs:
                    contact_state = part
                    # If state is found, assume previous part might be city
                    if location_parts.index(part.strip()) > 0:
                        contact_city = location_parts[location_parts.index(part.strip()) - 1].strip()
                    break

        print(f"Extracted location from company - City: '{contact_city}', State: '{contact_state}'")

        # First, look for exact name matches with first and last name
        exact_name_matches = []
        for result in sorted_results:
            name_parts = result['name'].lower().split()
            if len(name_parts) >= 2:
                if name_parts[0] == first_name.lower() and name_parts[-1] == last_name.lower():
                    exact_name_matches.append(result)
                    print(f"Found exact name match: {result['name']}")

        # If we have exact name matches, prioritize them
        if exact_name_matches:
            # First, check for location and company match within exact name matches
            for result in exact_name_matches:
                location_match = False

                # Check for state match in location
                if contact_state and contact_state.lower() in result['location'].lower():
                    location_match = True
                    print(f"State match found in location: {result['location']}")

                # Check for city match in location
                if contact_city and contact_city.lower() in result['location'].lower():
                    location_match = True
                    print(f"City match found in location: {result['location']}")

                # If we have a location match and company match, this is likely the right person
                if location_match and company.lower() in result['subtitle'].lower():
                    print(f"Found exact name, location, and company match: {result['name']} - {result['subtitle']} - {result['location']}")
                    result['score'] = max(result['score'], 85)  # Ensure very high score
                    return result

                # If we have just a location match
                if location_match:
                    print(f"Found exact name and location match: {result['name']} - {result['location']}")
                    result['score'] = max(result['score'], 75)  # Ensure high score
                    return result

                # If we have just a company match
                if company.lower() in result['subtitle'].lower():
                    print(f"Found exact name and company match: {result['name']} - {result['subtitle']}")
                    result['score'] = max(result['score'], 70)  # Ensure high score
                    return result

            # If no company or location match, return the highest scoring exact name match
            best_exact_match = max(exact_name_matches, key=lambda x: x['score'])
            best_exact_match['score'] = max(best_exact_match['score'], 65)  # Ensure good score
            print(f"Using best exact name match: {best_exact_match['name']} with score {best_exact_match['score']}")
            return best_exact_match

        # If no exact name matches, look for partial matches with location relevance
        location_matches = []
        for result in sorted_results:
            # Check if both first and last name appear in the result name
            name_match = first_name.lower() in result['name'].lower() and last_name.lower() in result['name'].lower()

            # Check for location match
            location_match = False
            if contact_state and contact_state.lower() in result['location'].lower():
                location_match = True
            if contact_city and contact_city.lower() in result['location'].lower():
                location_match = True

            # If we have both name and location match
            if name_match and location_match:
                print(f"Found name and location match: {result['name']} - {result['location']}")
                result['score'] = max(result['score'], 70)  # Ensure high score
                location_matches.append(result)

            # If we have just a location match with partial name
            elif location_match and (first_name.lower() in result['name'].lower() or last_name.lower() in result['name'].lower()):
                print(f"Found partial name and location match: {result['name']} - {result['location']}")
                result['score'] = max(result['score'], 60)  # Ensure good score
                location_matches.append(result)

        # If we found location matches, return the best one
        if location_matches:
            best_location_match = max(location_matches, key=lambda x: x['score'])
            print(f"Using best location match: {best_location_match['name']} with score {best_location_match['score']}")
            return best_location_match

        # If we still don't have a match, check for industry-specific indicators
        industry_keywords = ["dentist", "dental", "healthcare", "medical", "doctor", "physician",
                           "attorney", "lawyer", "legal", "law", "finance", "financial", "advisor",
                           "insurance", "real estate", "realtor", "property", "consultant"]

        for keyword in industry_keywords:
            if company and keyword in company.lower():
                # This is our industry, look for matches with this keyword
                for result in sorted_results:
                    if keyword in result['subtitle'].lower() and (first_name.lower() in result['name'].lower() or last_name.lower() in result['name'].lower()):
                        print(f"Found industry match ({keyword}): {result['name']} - {result['subtitle']}")
                        result['score'] = max(result['score'], 55)  # Ensure decent score
                        return result

        # If we get here, return the highest scoring result if it's above a minimum threshold
        if sorted_results and sorted_results[0]['score'] >= 35:
            print(f"Using highest scoring result: {sorted_results[0]['name']} with score {sorted_results[0]['score']}")
            return sorted_results[0]

        # No good match found
        return None

    def _calculate_linkedin_match_score(self, search_name: str, result_name: str, result_subtitle: str, result_location: str, company: str, first_name: str = "", last_name: str = "") -> int:
        """Calculate a match score between search criteria and LinkedIn search result

        Args:
            search_name: The name used in the search
            result_name: The name from the search result
            result_subtitle: The subtitle from the search result (usually contains company and title)
            result_location: The location from the search result
            company: The company name to match against
            first_name: The contact's first name (if available)
            last_name: The contact's last name (if available)

        Returns:
            Match score (0-100)
        """
        score = 0

        # Clean up search name (remove company if present)
        clean_search_name = search_name
        if company:
            clean_search_name = clean_search_name.replace(company, "").strip()

        # Log the analysis for debugging
        print(f"\n=== ANALYZING MATCH: {result_name} ===")
        print(f"Search name: '{clean_search_name}'")
        print(f"Result name: '{result_name}'")
        print(f"Result subtitle: '{result_subtitle}'")
        print(f"Result location: '{result_location}'")
        print(f"First name: '{first_name}', Last name: '{last_name}'")

        # Name matching (up to 60 points)
        # Exact match
        if clean_search_name.lower() == result_name.lower():
            score += 60
            print(f"Exact name match: +60 points")
        else:
            # Check if all words in search name are in result name
            search_words = clean_search_name.lower().split()
            result_words = result_name.lower().split()

            # Count matching words
            matching_words = sum(1 for word in search_words if any(word in result_word for result_word in result_words))
            word_match_percentage = matching_words / len(search_words) if search_words else 0

            # Add points based on percentage of matching words
            name_match_points = int(50 * word_match_percentage)
            score += name_match_points
            print(f"Name word match: {matching_words}/{len(search_words)} words = {word_match_percentage:.2f} = +{name_match_points} points")

            # Bonus for first name match
            if search_words and result_words and search_words[0] == result_words[0]:
                score += 10
                print(f"First word match: +10 points")

        # Direct first name and last name matching (up to 40 bonus points)
        if first_name and last_name:
            # Check for exact first name match
            if first_name.lower() == result_name.lower().split()[0]:
                score += 20
                print(f"Exact first name match: +20 points")
            # Check for partial first name match
            elif first_name.lower() in result_name.lower():
                score += 10
                print(f"Partial first name match: +10 points")

            # Check for exact last name match
            if len(result_name.split()) > 1 and last_name.lower() == result_name.lower().split()[-1]:
                score += 20
                print(f"Exact last name match: +20 points")
            # Check for partial last name match
            elif last_name.lower() in result_name.lower():
                score += 10
                print(f"Partial last name match: +10 points")

            # Check for middle initial if present in result name
            if len(result_name.split()) > 2 and len(result_name.split()[1]) == 1 or (len(result_name.split()[1]) == 2 and result_name.split()[1].endswith('.')):
                score += 5
                print(f"Middle initial present: +5 points")

        # Company matching (up to 30 points)
        if company and result_subtitle:
            if company.lower() in result_subtitle.lower():
                score += 30
                print(f"Exact company match: +30 points")
            else:
                # Check for partial company name match
                company_words = company.lower().split()
                matching_company_words = sum(1 for word in company_words if word in result_subtitle.lower())
                if matching_company_words > 0:
                    company_match_percentage = matching_company_words / len(company_words)
                    company_points = int(25 * company_match_percentage)
                    score += company_points
                    print(f"Partial company match: {matching_company_words}/{len(company_words)} words = {company_match_percentage:.2f} = +{company_points} points")

                # Check for industry match (if company doesn't match but industry does)
                industry_keywords = ["dentist", "dental", "healthcare", "medical", "doctor", "physician",
                                    "attorney", "lawyer", "legal", "law", "finance", "financial", "advisor",
                                    "insurance", "real estate", "realtor", "property", "consultant",
                                    "accountant", "CPA", "engineer", "architect", "designer"]

                for keyword in industry_keywords:
                    if keyword in company.lower() and keyword in result_subtitle.lower():
                        score += 15
                        print(f"Industry keyword match '{keyword}': +15 points")
                        break

        # Job title matching (up to 15 points)
        job_titles = ["CEO", "founder", "owner", "president", "director", "manager", "specialist",
                     "consultant", "advisor", "dentist", "doctor", "attorney", "lawyer", "agent",
                     "broker", "realtor", "accountant", "engineer", "designer", "developer"]

        for title in job_titles:
            if title.lower() in search_name.lower() and title.lower() in result_subtitle.lower():
                score += 15
                print(f"Job title match '{title}': +15 points")
                break

        # Location matching (up to 25 points)
        if result_location:
            score += 5
            print(f"Location present: +5 points")

            # Extract city and state from contact data
            contact_city = ""
            contact_state = ""

            # Try to extract location from company name or search name
            location_parts = []
            if "," in company:
                location_parts = company.split(",")[-1].strip().split()
            elif "," in search_name:
                location_parts = search_name.split(",")[-1].strip().split()

            # Common state abbreviations and full names
            state_mapping = {
                "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
                "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
                "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
                "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
                "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
                "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
                "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
                "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
                "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
                "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
                "DC": "District of Columbia"
            }

            # Try to identify state in location parts
            for part in location_parts:
                part = part.strip().upper()
                if part in state_mapping:
                    contact_state = part
                    # If state is found, assume previous part might be city
                    if location_parts.index(part.strip()) > 0:
                        contact_city = location_parts[location_parts.index(part.strip()) - 1].strip()
                    break

            print(f"Extracted location - City: '{contact_city}', State: '{contact_state}'")

            # Check for state match (abbreviation or full name)
            if contact_state:
                state_abbr = contact_state
                state_full = state_mapping.get(contact_state, "")

                if state_abbr in result_location or (state_full and state_full.lower() in result_location.lower()):
                    score += 15
                    print(f"State match '{state_abbr}/{state_full}': +15 points")

            # Check for city match
            if contact_city and contact_city.lower() in result_location.lower():
                score += 10
                print(f"City match '{contact_city}': +10 points")

            # If we don't have explicit city/state, try common locations
            if not contact_city and not contact_state:
                # Common locations to check
                location_keywords = ["NY", "New York", "CA", "California", "TX", "Texas", "FL", "Florida",
                                   "IL", "Illinois", "PA", "Pennsylvania", "OH", "Ohio", "GA", "Georgia",
                                   "NC", "North Carolina", "MI", "Michigan", "NJ", "New Jersey"]

                for location in location_keywords:
                    if (location.lower() in search_name.lower() or location.lower() in company.lower()) and location.lower() in result_location.lower():
                        score += 10
                        print(f"Location keyword match '{location}': +10 points")
                        break

        # Penalize very short result names (likely not a person)
        if len(result_name.split()) < 2:
            score -= 20
            print(f"Short name penalty: -20 points")

        # Bonus for results with both first and last name when we have both
        if first_name and last_name and len(result_name.split()) >= 2:
            score += 5
            print(f"Full name bonus: +5 points")

        # Bonus for "Connect" button available (indicates not connected yet)
        if "Connect" in result_subtitle:
            score += 10
            print(f"Connect button available: +10 points")

        # Bonus for exact name format match (e.g., "First M. Last")
        if first_name and last_name:
            name_pattern = f"{first_name} {last_name}"
            if name_pattern.lower() in result_name.lower():
                score += 15
                print(f"Exact name pattern match: +15 points")

            # Check for name with middle initial
            if len(result_name.split()) == 3 and len(result_name.split()[1]) <= 2:
                if result_name.split()[0].lower() == first_name.lower() and result_name.split()[2].lower() == last_name.lower():
                    score += 10
                    print(f"Name with middle initial match: +10 points")

        # Cap score at 100
        final_score = min(score, 100)
        print(f"Final score: {final_score}")
        return final_score

    def _generate_linkedin_message(self, contact: Dict[str, Any]) -> str:
        """Generate personalized LinkedIn connection message

        Args:
            contact: Contact data

        Returns:
            Personalized message
        """
        # If custom template is set, use it
        if self.linkedin_template:
            # Start with the template
            message = self.linkedin_template

            # Replace special placeholders first
            message = message.replace("{your_name}", self.your_name)
            message = message.replace("{your_email}", self.settings.get('your_email', ''))
            message = message.replace("{phone}", self.settings.get('phone', ''))

            # Extract first name from full name if available - prioritize listing_name
            full_name = (contact.get("listing_name") or  # Prioritize listing_name from Supabase
                        contact.get("dentist_name_profile") or
                        contact.get("name") or
                        "")

            # Remove everything after a comma if present
            if full_name and "," in full_name:
                full_name = full_name.split(",")[0].strip()

            # Log the name being used for better debugging
            print(f"Using name for LinkedIn message template: '{full_name}'")

            first_name = full_name.split()[0] if full_name else ""
            message = message.replace("{first_name}", first_name)

            # Now dynamically replace any column name from the contact data
            for key, value in contact.items():
                if value:  # Only replace if the value is not empty
                    placeholder = "{" + key + "}"
                    if placeholder in message:
                        message = message.replace(placeholder, str(value))

            # Log which placeholders couldn't be replaced
            import re
            remaining_placeholders = re.findall(r'\{([^}]+)\}', message)
            if remaining_placeholders:
                print(f"Warning: The following placeholders could not be replaced in LinkedIn message: {', '.join(remaining_placeholders)}")

                # Replace remaining placeholders with empty strings
                for placeholder in remaining_placeholders:
                    message = message.replace("{" + placeholder + "}", "")
        else:
            # Otherwise use default template
            full_name = contact.get("listing_name") or contact.get("name", "")

            # Remove everything after a comma if present
            if full_name and "," in full_name:
                full_name = full_name.split(",")[0].strip()

            first_name = full_name.split()[0] if full_name else ""
            company = contact.get("company", "your company") or contact.get("listing_business_name", "your company")

            message = f"Hi {first_name}, I came across {company} and was impressed by your work. "
            message += f"I'd love to connect and discuss potential opportunities to collaborate. - {self.your_name}"

        # Ensure message is within LinkedIn's character limit (300 characters)
        if len(message) > 300:
            message = message[:297] + "..."
            print(f"LinkedIn message truncated to 300 characters: {message}")

        return message

    def _update_status(self, contact_id: str, status_field: str, success: Union[bool, str], message: str = "") -> None:
        """Update status in Supabase table

        Args:
            contact_id: Contact ID
            status_field: Field to update
            success: Success status (True/False or error message)
            message: Additional message
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot update status.")
            return

        # Special handling for contact_form_found which might not exist
        if status_field == "contact_form_found":
            print(f"Using contact_form_submitted instead of contact_form_found for compatibility")
            # Use contact_form_submitted instead
            status_field = "contact_form_submitted"

            # If we're setting contact_form_found to True, we'll set contact_form_submitted to False
            # This is because if we found a form but didn't submit it, it's a failure
            if success is True:
                # We found a form but didn't submit it yet
                success = None  # Set to pending

            # If message is about finding a form, update it
            if "form found" in message.lower():
                message = f"Form found but not submitted yet: {message}"

        try:
            # If this is a retry operation, use a simplified update approach
            if hasattr(self, 'is_retry') and self.is_retry:
                print(f"RETRY MODE: Using simplified update for contact {contact_id}")

                # In retry mode, we'll just update the main status field and last_updated
                # without checking if columns exist
                try:
                    # Create a minimal update with just the essential fields
                    update_data = {
                        status_field: success,
                        f"{status_field}_message": message
                    }

                    # Add timestamp if it's not contact_form_found (which we've already handled)
                    if status_field != "contact_form_found":
                        from datetime import datetime
                        update_data[f"{status_field}_timestamp"] = datetime.now().isoformat()

                    # Try to update with all fields at once
                    try:
                        self.supabase.table(TABLE_NAME) \
                            .update(update_data) \
                            .eq("id", contact_id) \
                            .execute()
                        print(f"RETRY MODE: Updated status for contact {contact_id}: {status_field} = {success}")
                    except Exception as batch_error:
                        print(f"RETRY MODE: Batch update failed: {batch_error}")
                        print("RETRY MODE: Trying to update one field at a time...")

                        # If batch update fails, try updating just the main status field
                        try:
                            self.supabase.table(TABLE_NAME) \
                                .update({status_field: success}) \
                                .eq("id", contact_id) \
                                .execute()
                            print(f"RETRY MODE: Updated main status field for contact {contact_id}")
                        except Exception as status_error:
                            print(f"RETRY MODE: Failed to update status field: {status_error}")
                            print("RETRY MODE: Continuing with processing anyway")
                except Exception as retry_error:
                    print(f"RETRY MODE: Error in simplified update: {retry_error}")
                    print("RETRY MODE: Continuing with processing anyway")

                # In retry mode, we continue processing even if updates fail
                return

            # Standard mode (not retry) - check columns before updating
            try:
                # Try to get the record to check the structure
                sample = self.supabase.table(TABLE_NAME).select("*").eq("id", contact_id).limit(1).execute()
                if sample.data:
                    columns = list(sample.data[0].keys())

                    # Only update fields that exist in the table
                    update_data = {}

                    # Check if the status field exists
                    if status_field in columns:
                        update_data[status_field] = success
                    else:
                        print(f"Column '{status_field}' does not exist in table {TABLE_NAME}")
                        # Try to create the column
                        if self._check_and_create_column(status_field):
                            update_data[status_field] = success
                            print(f"Created and will update column '{status_field}'")

                    # Check if the message field exists
                    message_field = f"{status_field}_message"
                    if message_field in columns:
                        update_data[message_field] = message
                    else:
                        print(f"Column '{message_field}' does not exist in table {TABLE_NAME}")
                        # Try to create the column
                        if self._check_and_create_column(message_field):
                            update_data[message_field] = message
                            print(f"Created and will update column '{message_field}'")

                    # Check if the timestamp field exists
                    timestamp_field = f"{status_field}_timestamp"
                    if timestamp_field in columns:
                        # Use the current timestamp
                        from datetime import datetime
                        update_data[timestamp_field] = datetime.now().isoformat()
                    else:
                        print(f"Column '{timestamp_field}' does not exist in table {TABLE_NAME}")
                        # Try to create the column
                        if self._check_and_create_column(timestamp_field):
                            from datetime import datetime
                            update_data[timestamp_field] = datetime.now().isoformat()
                            print(f"Created and will update column '{timestamp_field}'")

                    # Always update last_updated if it exists
                    if "last_updated" in columns:
                        update_data["last_updated"] = "now()"

                    # If we have no fields to update, add a generic status field
                    if not update_data and "status" in columns:
                        update_data["status"] = f"{status_field}: {success}"
                        update_data["last_updated"] = "now()"

                    # If we have fields to update, perform the update
                    if update_data:
                        try:
                            self.supabase.table(TABLE_NAME) \
                                .update(update_data) \
                                .eq("id", contact_id) \
                                .execute()
                            print(f"Updated status for contact {contact_id}: {status_field} = {success}")
                        except Exception as update_error:
                            print(f"Error updating status: {update_error}")
                            print("Trying to update one field at a time...")

                            # Try updating one field at a time
                            for field, value in update_data.items():
                                try:
                                    self.supabase.table(TABLE_NAME) \
                                        .update({field: value}) \
                                        .eq("id", contact_id) \
                                        .execute()
                                    print(f"Updated field {field} for contact {contact_id}")
                                except Exception as field_error:
                                    print(f"Error updating field {field}: {field_error}")
                    else:
                        print(f"No matching fields found to update status for contact {contact_id}")
                else:
                    print(f"Contact {contact_id} not found in database")
            except Exception as e:
                print(f"Error checking table structure: {e}")

                # Fallback: try a simple update with just the main fields
                try:
                    update_data = {
                        "last_updated": "now()"
                    }

                    # Only include status_field if it's not contact_form_found
                    if status_field != "contact_form_found":
                        update_data[status_field] = success

                    self.supabase.table(TABLE_NAME) \
                        .update(update_data) \
                        .eq("id", contact_id) \
                        .execute()

                    print(f"Updated status for contact {contact_id} using fallback method")
                except Exception as fallback_error:
                    print(f"Fallback update failed: {fallback_error}")
                    print("Unable to update contact status")

        except Exception as e:
            print(f"Error updating status: {e}")

    def _ensure_enrichment_table_exists(self) -> bool:
        """Ensure the contact_enrichment table exists in Supabase with all required columns

        Returns:
            True if table exists or was created, False otherwise
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot check enrichment table.")
            return False

        try:
            # Check if the enrichment table exists by trying to select from it
            try:
                self.supabase.table("contact_enrichment").select("count", count="exact").limit(1).execute()
                print("Contact enrichment table exists.")

                # Table exists, now check if we need to add new columns
                try:
                    # Add new columns if they don't exist
                    alter_sql = """
                    -- Add address column if it doesn't exist
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                      WHERE table_name='contact_enrichment' AND column_name='address') THEN
                            ALTER TABLE contact_enrichment ADD COLUMN address TEXT DEFAULT '';
                        END IF;

                        -- Add business_hours column if it doesn't exist
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                      WHERE table_name='contact_enrichment' AND column_name='business_hours') THEN
                            ALTER TABLE contact_enrichment ADD COLUMN business_hours TEXT DEFAULT '';
                        END IF;

                        -- Add contact_persons column if it doesn't exist
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                      WHERE table_name='contact_enrichment' AND column_name='contact_persons') THEN
                            ALTER TABLE contact_enrichment ADD COLUMN contact_persons JSONB DEFAULT '[]';
                        END IF;

                        -- Add additional_data column if it doesn't exist
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                                      WHERE table_name='contact_enrichment' AND column_name='additional_data') THEN
                            ALTER TABLE contact_enrichment ADD COLUMN additional_data JSONB DEFAULT '{}';
                        END IF;
                    END $$;
                    """

                    # Execute the SQL to add new columns
                    self.supabase.rpc("exec_sql", {"query": alter_sql}).execute()
                    print("Ensured all required columns exist in contact_enrichment table")
                except Exception as e:
                    print(f"Warning: Could not add new columns to enrichment table: {e}")
                    # Continue anyway, as the base table exists

                return True
            except Exception as e:
                # Table doesn't exist, try to create it
                if "does not exist" in str(e).lower():
                    print("Contact enrichment table does not exist. Creating it...")
                    try:
                        # Use SQL to create the table with all required columns
                        sql = """
                        CREATE TABLE IF NOT EXISTS public.contact_enrichment (
                            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                            contact_id TEXT NOT NULL,
                            source_table TEXT NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                            emails JSONB DEFAULT '[]',
                            phone_numbers JSONB DEFAULT '[]',
                            social_media JSONB DEFAULT '{}',
                            additional_pages JSONB DEFAULT '{}',
                            address TEXT DEFAULT '',
                            business_hours TEXT DEFAULT '',
                            contact_persons JSONB DEFAULT '[]',
                            additional_data JSONB DEFAULT '{}',
                            raw_data JSONB DEFAULT '{}'
                        );
                        """
                        self.supabase.rpc("exec_sql", {"query": sql}).execute()

                        # Create an index on contact_id for faster lookups
                        index_sql = """
                        CREATE INDEX IF NOT EXISTS idx_contact_enrichment_contact_id
                        ON public.contact_enrichment(contact_id);
                        """
                        self.supabase.rpc("exec_sql", {"query": index_sql}).execute()

                        print("Successfully created contact enrichment table with all required columns")
                        return True
                    except Exception as create_error:
                        print(f"Error creating enrichment table: {create_error}")
                        return False
                else:
                    print(f"Error checking enrichment table: {e}")
                    return False
        except Exception as e:
            print(f"Error ensuring enrichment table exists: {e}")
            return False

    def _update_alternative_contacts(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
        """Update alternative contacts in the database

        Args:
            contact_id: Contact ID
            alternative_contacts: Dictionary of alternative contact methods
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot update alternative contacts.")
            return

        # Use the direct method to add columns to the main table
        self._update_enriched_data_columns(contact_id, alternative_contacts)
        print("Data enrichment completed and saved directly to main table with enriched_ prefix")

    def _check_and_create_column(self, column_name: str) -> bool:
        """Check if a column exists in the table and create it if it doesn't

        Args:
            column_name: Name of the column to check/create

        Returns:
            True if column exists or was created, False otherwise
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot check/create column.")
            return False

        # If this is a retry operation, pretend the column exists to bypass checks
        if hasattr(self, 'is_retry') and self.is_retry:
            print(f"RETRY MODE: Bypassing column check for '{column_name}' - assuming it exists")
            return True

        try:
            # First check if the column already exists by trying to select it
            try:
                # Try to get one record to check the structure
                sample = self.supabase.table(TABLE_NAME).select("*").limit(1).execute()
                if sample.data:
                    columns = list(sample.data[0].keys())

                    # Check if the column already exists
                    if column_name.lower() in columns:
                        print(f"Column '{column_name}' already exists in table {TABLE_NAME}")
                        return True

                    # Try using the SQL method if available
                    try:
                        # Use a SQL query to check if the column exists
                        sql = f"""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = '{TABLE_NAME}'
                        AND column_name = '{column_name.lower()}'
                        """

                        response = self.supabase.rpc("exec_sql", {"query": sql}).execute()

                        # If we get data back, the column exists
                        if response.data and len(response.data) > 0:
                            print(f"Column '{column_name}' already exists in table {TABLE_NAME}")
                            return True

                        # Column doesn't exist, try to create it
                        print(f"Column '{column_name}' does not exist in table {TABLE_NAME}. Creating it...")

                        # Determine the appropriate column type based on name
                        column_type = "text"  # Default type
                        if column_name.lower() == "error":
                            column_type = "boolean"
                        elif "timestamp" in column_name.lower():
                            column_type = "timestamptz"
                        elif column_name.lower() == "contact_form_submitted":
                            # Use text type for contact_form_submitted to support "skipped" status
                            column_type = "text"
                        elif "website_visited" == column_name.lower():
                            column_type = "boolean"
                        elif "linkedin_connected" == column_name.lower():
                            column_type = "boolean"

                        # Execute SQL to add the column
                        alter_sql = f"""
                        ALTER TABLE {TABLE_NAME}
                        ADD COLUMN IF NOT EXISTS {column_name.lower()} {column_type}
                        """

                        self.supabase.rpc("exec_sql", {"query": alter_sql}).execute()
                        print(f"Successfully created column '{column_name}' in table {TABLE_NAME}")
                        return True
                    except Exception as sql_error:
                        print(f"SQL method failed: {sql_error}")
                        print("Falling back to alternative method...")

                        # If SQL method fails, we'll try a different approach
                        # We'll create a temporary record with the new column and then delete it
                        try:
                            # Create a unique ID for our temporary record
                            import uuid
                            temp_id = str(uuid.uuid4())

                            # Create a record with the new column
                            temp_data = {"id": temp_id}

                            # Set appropriate value based on column type
                            if column_name.lower() == "error" or column_name.lower() == "contact_form_submitted" or column_name.lower() == "website_visited" or column_name.lower() == "linkedin_connected":
                                temp_data[column_name.lower()] = False
                            elif "timestamp" in column_name.lower():
                                temp_data[column_name.lower()] = datetime.now().isoformat()
                            else:
                                temp_data[column_name.lower()] = "test_value"

                            # Insert the record
                            self.supabase.table(TABLE_NAME).insert(temp_data).execute()
                            print(f"Created temporary record with column '{column_name}'")

                            # Delete the temporary record
                            self.supabase.table(TABLE_NAME).delete().eq("id", temp_id).execute()
                            print(f"Deleted temporary record")

                            return True
                        except Exception as temp_error:
                            print(f"Failed to create column using temporary record method: {temp_error}")

                            # Even if we can't create the column, return True to allow the operation to continue
                            # This prevents the bot from getting stuck when it can't create columns
                            print(f"Assuming column '{column_name}' exists to allow operation to continue")
                            return True
                else:
                    print(f"No data found in {TABLE_NAME} table. Cannot check structure.")
                    # Return True anyway to allow the operation to continue
                    print(f"Assuming column '{column_name}' exists to allow operation to continue")
                    return True
            except Exception as e:
                print(f"Error checking/creating column '{column_name}': {e}")
                # Return True anyway to allow the operation to continue
                print(f"Assuming column '{column_name}' exists to allow operation to continue")
                return True

        except Exception as e:
            print(f"Error in check_and_create_column: {e}")
            # Return True anyway to allow the operation to continue
            print(f"Assuming column '{column_name}' exists to allow operation to continue")
            return True

    def retrain_field_classifier(self) -> bool:
        """Retrain the field classifier with all available training data

        Returns:
            True if model was retrained successfully, False otherwise
        """
        if self.field_classifier and hasattr(self.field_classifier, 'retrain_with_all_data'):
            try:
                return self.field_classifier.retrain_with_all_data()
            except Exception as e:
                print(f"Error retraining field classifier: {e}")
                return False
        return False

    def close(self):
        """Close the browser and clean up resources"""
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
                print("Browser closed")
        except Exception as e:
            print(f"Error closing browser: {e}")

    def _update_enriched_data_columns(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
        """Update the main table with enriched data columns

        This method creates new columns in the main table with the enriched_ prefix
        and stores the data directly in those columns.

        Args:
            contact_id: Contact ID
            alternative_contacts: Dictionary of alternative contact methods
        """
        try:
            print(f"Updating enriched data columns for contact {contact_id}...")

            # Try to get the record to check the structure
            sample = self.supabase.table(TABLE_NAME).select("*").eq("id", contact_id).limit(1).execute()
            if not sample.data:
                print(f"Contact {contact_id} not found in database")
                return

            columns = sample.data[0].keys()

            # Prepare update data
            update_data = {"last_updated": "now()"}


            # Get first name, last name, and niche from the main contact record
            try:
                contact_result = self.supabase.table(TABLE_NAME).select("listing_name, niche").eq("id", contact_id).execute()

                if contact_result.data and len(contact_result.data) > 0:
                    contact = contact_result.data[0]

                    # Extract first and last name from listing_name
                    if contact.get("listing_name"):
                        name_parts = contact.get("listing_name", "").split(" ", 1)
                        first_name = name_parts[0] if len(name_parts) > 0 else ""
                        last_name = name_parts[1] if len(name_parts) > 1 else ""

                        # Add first and last name to enriched data
                        if first_name and self._check_and_create_column("enriched_first_name"):
                            update_data["enriched_first_name"] = first_name

                        if last_name and self._check_and_create_column("enriched_last_name"):
                            update_data["enriched_last_name"] = last_name

                    # Get niche and add to enriched data
                    niche = contact.get("niche", "")
                    if niche and self._check_and_create_column("enriched_niche"):
                        update_data["enriched_niche"] = niche
            except Exception as e:
                print(f"Error getting contact details for enrichment: {e}")

            # Store all alternative contacts in a single JSON field for easy access
            if self._check_and_create_column("enriched_all_contacts"):
                update_data["enriched_all_contacts"] = json.dumps(alternative_contacts)
                print("Added all alternative contacts to enriched_all_contacts JSON field")

            # Process each type of alternative contact
            for method, value in alternative_contacts.items():
                if not value:  # Skip empty values
                    continue

                # Create a valid column name with enriched_ prefix
                column_name = f"enriched_{method.lower().replace(' ', '_').replace('/', '_')}"

                # Check if column exists and create it if needed
                if self._check_and_create_column(column_name):
                    # Add to update data
                    update_data[column_name] = value
                    print(f"Added {method} to update data with column name {column_name}")

                    # For email, phone, and social media, also create a first_value column
                    if method in ['Email', 'Phone', 'LinkedIn', 'Facebook', 'Twitter', 'Instagram']:
                        first_value = value.split(',')[0].strip() if ',' in value else value.strip()
                        first_column_name = f"enriched_{method.lower()}_first"

                        if self._check_and_create_column(first_column_name):
                            update_data[first_column_name] = first_value
                            print(f"Added first {method} value to column {first_column_name}: {first_value}")

            # Set a flag to indicate alternative contacts were found
            if self._check_and_create_column("alternative_contact_found"):
                update_data["alternative_contact_found"] = True
                print("Set alternative_contact_found flag to True")

            # If we have data to update, perform the update
            if len(update_data) > 1:  # More than just last_updated
                try:
                    # Try to update all fields at once
                    self.supabase.table(TABLE_NAME) \
                        .update(update_data) \
                        .eq("id", contact_id) \
                        .execute()
                    print(f"Successfully updated all enriched data columns for contact {contact_id}")
                except Exception as update_error:
                    print(f"Error updating all fields at once: {update_error}")

                    # Try updating one field at a time
                    print("Trying to update one field at a time...")
                    success_count = 0

                    for field, value in update_data.items():
                        if field == "last_updated":
                            continue  # Skip this field as it might cause issues

                        try:
                            single_update = {field: value}
                            self.supabase.table(TABLE_NAME) \
                                .update(single_update) \
                                .eq("id", contact_id) \
                                .execute()
                            print(f"Successfully updated field {field}")
                            success_count += 1
                        except Exception as field_error:
                            print(f"Error updating field {field}: {field_error}")

                    print(f"Updated {success_count} out of {len(update_data)-1} fields individually")
            else:
                print("No data to update for enriched columns")
        except Exception as e:
            print(f"Error updating enriched data columns: {e}")
            # Fallback to the legacy method as last resort
            print("Falling back to legacy method...")
            self._legacy_update_alternative_contacts(contact_id, alternative_contacts)

    def _update_alternative_contacts_fallback(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
        """Fallback method to update alternative contacts in the original table with enhanced data types

        Args:
            contact_id: Contact ID
            alternative_contacts: Dictionary of alternative contact methods
        """
        # Use the new method instead
        print("Using new _update_enriched_data_columns method instead of fallback...")
        self._update_enriched_data_columns(contact_id, alternative_contacts)

    def _legacy_update_alternative_contacts(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
        """Legacy method to update alternative contacts in the original table
        This is the last resort method when all other methods fail

        Args:
            contact_id: Contact ID
            alternative_contacts: Dictionary of alternative contact methods
        """
        try:
            # Try to update with the alternative_contacts field
            try:
                self.supabase.table(TABLE_NAME) \
                    .update({"alternative_contacts": alternative_contacts, "last_updated": "now()"}) \
                    .eq("id", contact_id) \
                    .execute()
                print(f"Updated alternative contacts for contact {contact_id} using legacy method")
            except Exception as e:
                print(f"Legacy update failed: {e}")

                # Last resort: store in message field
                try:
                    # Format the contact info in a readable way
                    contact_info_parts = []

                    # Add email addresses
                    if 'Email' in alternative_contacts and alternative_contacts['Email']:
                        contact_info_parts.append(f"Email: {alternative_contacts['Email']}")

                    # Add phone numbers
                    if 'Phone' in alternative_contacts and alternative_contacts['Phone']:
                        contact_info_parts.append(f"Phone: {alternative_contacts['Phone']}")

                    # Add social media links
                    for platform in ['LinkedIn', 'Facebook', 'Twitter', 'Instagram']:
                        if platform in alternative_contacts and alternative_contacts[platform]:
                            contact_info_parts.append(f"{platform}: {alternative_contacts[platform]}")

                    # Add contact pages
                    if 'Contact Pages' in alternative_contacts and alternative_contacts['Contact Pages']:
                        contact_info_parts.append(f"Contact Pages: {alternative_contacts['Contact Pages']}")

                    # Add about/team pages
                    if 'About/Team Pages' in alternative_contacts and alternative_contacts['About/Team Pages']:
                        contact_info_parts.append(f"About/Team Pages: {alternative_contacts['About/Team Pages']}")

                    # Add address
                    if 'Address' in alternative_contacts and alternative_contacts['Address']:
                        contact_info_parts.append(f"Address: {alternative_contacts['Address']}")

                    # Add business hours
                    if 'Business Hours' in alternative_contacts and alternative_contacts['Business Hours']:
                        contact_info_parts.append(f"Business Hours: {alternative_contacts['Business Hours']}")

                    # Add contact persons
                    if 'Contact Persons' in alternative_contacts and alternative_contacts['Contact Persons']:
                        contact_info_parts.append(f"Contact Persons: {alternative_contacts['Contact Persons']}")

                    # Add any other fields
                    for method, value in alternative_contacts.items():
                        if method not in ['Email', 'Phone', 'LinkedIn', 'Facebook', 'Twitter', 'Instagram',
                                         'Contact Pages', 'About/Team Pages', 'Address', 'Business Hours', 'Contact Persons']:
                            if value:
                                contact_info_parts.append(f"{method}: {value}")

                    # Join all parts with newlines
                    contact_info = "\n".join(contact_info_parts)

                    # Update the message field
                    self.supabase.table(TABLE_NAME) \
                        .update({"contact_form_submitted_message": f"Alternative contacts found:\n{contact_info}"}) \
                        .eq("id", contact_id) \
                        .execute()
                    print(f"Stored alternative contacts in message field for contact {contact_id}")

                    # Also try to set a flag to indicate alternative contacts were found
                    try:
                        self.supabase.table(TABLE_NAME) \
                            .update({"alternative_contact_found": True}) \
                            .eq("id", contact_id) \
                            .execute()
                    except:
                        # Ignore errors here, it's just a nice-to-have
                        pass
                except Exception as e2:
                    print(f"All attempts to store alternative contacts failed: {e2}")
        except Exception as e:
            print(f"Error in legacy update method: {e}")

    def _analyze_form_structure(self, form_element=None) -> Dict[str, List[str]]:
        """
        Analyze the form structure on the current page and generate custom selectors

        Args:
            form_element: Optional form element to analyze. If None, will try to find forms on the page.

        Returns:
            Dict with custom selectors for different field types
        """
        print("🔍 Analyzing form structure with AI...")
        custom_selectors = {
            "name": [],
            "first_name": [],
            "last_name": [],
            "email": [],
            "phone": [],
            "message": [],
            "submit": [],
            "dropdown": []
        }

        try:
            # If no form element provided, try to find forms on the page
            if form_element is None:
                forms = self.driver.find_elements(By.TAG_NAME, "form")
                if not forms:
                    # Try to find div elements that might contain forms
                    forms = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='form' i], div[id*='form' i], div[class*='contact' i], div[id*='contact' i]")

                if not forms:
                    print("No forms found for analysis")
                    return custom_selectors

                # Use the first form for analysis
                form_element = forms[0]

            # Take a screenshot for debugging
            self.driver.save_screenshot("form_analysis.png")

            # Get all input fields, textareas, and selects in the form
            fields = form_element.find_elements(By.CSS_SELECTOR, "input:not([type='hidden']):not([type='submit']):not([type='button']), textarea, select")

            if not fields:
                print("No input fields found in the form")
                return custom_selectors

            print(f"Found {len(fields)} fields to analyze")

            # Analyze each field
            for field in fields:
                field_type = field.get_attribute("type") or ""
                field_id = field.get_attribute("id") or ""
                field_name = field.get_attribute("name") or ""
                field_class = field.get_attribute("class") or ""
                field_placeholder = field.get_attribute("placeholder") or ""
                field_tag = field.tag_name
                field_required = field.get_attribute("required") or field.get_attribute("aria-required") == "true"

                # Try to find associated label
                label_text = ""
                if field_id:
                    try:
                        label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{field_id}']")
                        label_text = label.text.strip()
                    except:
                        # Try to find parent label
                        try:
                            label = field.find_element(By.XPATH, "./ancestor::label")
                            label_text = label.text.strip()
                        except:
                            pass

                print(f"Field analysis: type={field_type}, id={field_id}, name={field_name}, placeholder={field_placeholder}, label={label_text}, required={field_required}")

                # Generate custom selector for this field
                selector = ""
                if field_id:
                    selector = f"#{field_id}"
                elif field_name:
                    selector = f"[name='{field_name}']"
                else:
                    continue

                # Determine field purpose based on attributes and label
                field_purpose = self._determine_field_purpose(
                    field_type, field_id, field_name, field_class,
                    field_placeholder, field_tag, label_text
                )

                if field_purpose and field_purpose in custom_selectors:
                    custom_selectors[field_purpose].append(selector)
                    print(f"Identified {field_purpose} field: {selector}")

            # Look for submit buttons
            submit_buttons = form_element.find_elements(By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button:not([type]), .submit, [class*='submit' i], [id*='submit' i]")
            for button in submit_buttons:
                button_id = button.get_attribute("id") or ""
                button_class = button.get_attribute("class") or ""
                button_text = button.text.strip()

                if button_id:
                    custom_selectors["submit"].append(f"#{button_id}")
                elif button_class:
                    classes = button_class.split()
                    for cls in classes:
                        if cls:
                            custom_selectors["submit"].append(f".{cls}")

                print(f"Found submit button: id={button_id}, class={button_class}, text={button_text}")

            print(f"Form analysis complete. Generated custom selectors: {custom_selectors}")
            return custom_selectors

        except Exception as e:
            print(f"Error analyzing form structure: {e}")
            traceback.print_exc()
            return custom_selectors

    def _determine_field_purpose(self, field_type, field_id, field_name, field_class, field_placeholder, field_tag, label_text):
        """Determine the purpose of a form field based on its attributes"""

        # Convert all text attributes to lowercase for easier matching
        field_id_lower = field_id.lower()
        field_name_lower = field_name.lower()
        field_class_lower = field_class.lower()
        field_placeholder_lower = field_placeholder.lower()
        label_text_lower = label_text.lower()

        # Get any aria-label attribute
        field_aria_label = ""
        try:
            field_aria_label = self.driver.execute_script(
                "return arguments[0].getAttribute('aria-label')",
                self.driver.find_element(By.CSS_SELECTOR, f"#{field_id}" if field_id else f"[name='{field_name}']")
            ) or ""
            field_aria_label = field_aria_label.lower()
        except:
            pass

        # Get any autocomplete attribute
        field_autocomplete = ""
        try:
            field_autocomplete = self.driver.execute_script(
                "return arguments[0].getAttribute('autocomplete')",
                self.driver.find_element(By.CSS_SELECTOR, f"#{field_id}" if field_id else f"[name='{field_name}']")
            ) or ""
            field_autocomplete = field_autocomplete.lower()
        except:
            pass

        # Combine all text attributes for comprehensive matching
        all_field_text = f"{field_id_lower} {field_name_lower} {field_class_lower} {field_placeholder_lower} {label_text_lower} {field_aria_label} {field_autocomplete}"

        print(f"Field purpose analysis - all text: {all_field_text}")

        # Check for email fields
        if field_type == "email" or "email" in all_field_text or field_autocomplete in ["email", "e-mail"]:
            return "email"

        # Check for phone fields
        if field_type == "tel" or any(phone_term in all_field_text for phone_term in ["phone", "tel", "mobile", "cell", "telephone"]) or field_autocomplete in ["tel", "phone", "mobile"]:
            return "phone"

        # Check for message/comment fields
        if field_tag == "textarea" or any(msg_term in all_field_text for msg_term in ["message", "comment", "inquiry", "description", "content", "details", "feedback"]):
            return "message"

        # Check for dropdown/select fields
        if field_tag == "select" or any(select_term in all_field_text for select_term in ["service", "interest", "category", "select", "dropdown", "option", "choose"]):
            return "dropdown"

        # Check for full name fields
        if any(name_term in all_field_text for name_term in ["fullname", "full-name", "full_name", "name", "your name"]) and not any(
                exclude_term in field_id_lower or exclude_term in field_name_lower
                for exclude_term in ["first", "last", "user", "login"]):
            return "name"

        # Check for first name fields
        if any(fname_term in all_field_text for fname_term in ["first", "firstname", "first-name", "first_name", "fname", "given"]) or field_autocomplete in ["given-name", "first-name"]:
            return "first_name"

        # Check for last name fields
        if any(lname_term in all_field_text for lname_term in ["last", "lastname", "last-name", "last_name", "lname", "surname", "family"]) or field_autocomplete in ["family-name", "last-name"]:
            return "last_name"

        # Check for company fields
        if any(company_term in all_field_text for company_term in ["company", "business", "organization", "firm", "employer", "workplace"]) or field_autocomplete in ["organization", "company"]:
            return "company"

        # Check for subject fields
        if any(subject_term in all_field_text for subject_term in ["subject", "topic", "regarding", "re:", "about", "title"]):
            return "subject"

        # Check for address fields
        if any(address_term in all_field_text for address_term in ["address", "street", "line1", "line 1", "address1"]) or field_autocomplete in ["street-address", "address-line1"]:
            return "address"

        # Check for city fields
        if any(city_term in all_field_text for city_term in ["city", "town", "locality"]) or field_autocomplete in ["city", "locality"]:
            return "city"

        # Check for state fields
        if any(state_term in all_field_text for state_term in ["state", "province", "region"]) or field_autocomplete in ["state", "province", "region"]:
            return "state"

        # Check for zip/postal code fields
        if any(zip_term in all_field_text for zip_term in ["zip", "postal", "post code", "postcode"]) or field_autocomplete in ["postal-code", "zip"]:
            return "zip"

        # Check for country fields
        if any(country_term in all_field_text for country_term in ["country", "nation"]) or field_autocomplete in ["country", "country-name"]:
            return "country"

        # Check for date fields
        if field_type == "date" or any(date_term in all_field_text for date_term in ["date", "day", "appointment", "calendar", "schedule"]):
            return "date"

        # Check for time fields
        if field_type == "time" or any(time_term in all_field_text for time_term in ["time", "hour", "clock"]):
            return "time"

        # Check for website/URL fields
        if field_type == "url" or any(url_term in all_field_text for url_term in ["website", "url", "site", "web", "homepage"]) or field_autocomplete in ["url", "website"]:
            return "url"

        # Check for job title/position fields
        if any(job_term in all_field_text for job_term in ["job", "title", "position", "occupation", "role"]) or field_autocomplete in ["job-title", "organization-title"]:
            return "job_title"

        # Check for industry fields
        if any(industry_term in all_field_text for industry_term in ["industry", "sector", "field"]):
            return "industry"

        # Check for budget fields
        if any(budget_term in all_field_text for budget_term in ["budget", "price", "cost", "amount"]):
            return "budget"

        # Check for how did you hear about us fields
        if any(source_term in all_field_text for source_term in ["how did you", "how you heard", "referral", "source", "found us"]):
            return "source"

        # Check for checkbox consent fields
        if field_type == "checkbox" and any(consent_term in all_field_text for consent_term in ["consent", "agree", "accept", "terms", "privacy", "policy", "subscribe", "newsletter"]):
            return "consent"

        return None

    def _scan_for_alternative_contacts(self) -> Dict[str, str]:
        """Scan the website for alternative contact methods with enhanced thoroughness

        This method performs a comprehensive scan of the website to find all possible
        contact information, regardless of whether a contact form was successfully submitted.
        It serves as a data enrichment tool to gather additional contact details.

        Returns:
            Dictionary of contact methods and their values
        """
        alternative_contacts = {}

        try:
            print("Starting enhanced scan for alternative contact methods...")
            # Take a screenshot for debugging
            self.driver.save_screenshot("scanning_for_alternative_contacts_start.png")

            # Get the page source
            page_source = self.driver.page_source
            current_url = self.driver.current_url

            # Store the original URL so we can return to it
            original_url = current_url

            # 1. First, check if we're already on a contact page
            if not any(keyword in current_url.lower() for keyword in ['contact', 'about', 'team']):
                # Try to find and navigate to contact page first for better results
                print("Looking for contact page to navigate to...")
                contact_page_found = False

                # Try to find links with "contact" in them
                contact_elements = self.driver.find_elements(By.XPATH,
                    "//a[contains(translate(text(), 'CONTACT', 'contact'), 'contact') or contains(@href, 'contact')]")

                for element in contact_elements[:1]:  # Just try the first one
                    try:
                        href = element.get_attribute('href')
                        if href and href.startswith('http'):
                            print(f"Navigating to contact page: {href}")
                            self.driver.get(href)
                            time.sleep(2)  # Wait for page to load
                            contact_page_found = True
                            # Update page source after navigation
                            page_source = self.driver.page_source
                            break
                    except Exception as e:
                        print(f"Error navigating to contact page: {e}")
                        continue

                if not contact_page_found:
                    print("No contact page found, scanning current page")

            # 2. Scan for email addresses (enhanced)
            print("Scanning for email addresses...")
            # More comprehensive email pattern
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = set(re.findall(email_pattern, page_source))

            # Also look for obfuscated emails (common anti-scraping technique)
            # Look for elements with data attributes that might contain email parts
            try:
                obfuscated_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    '[data-email], [data-mail], [data-user], [data-domain], [class*="email"], [class*="mail"]')

                for element in obfuscated_elements:
                    # Try to get the actual text which might be the email
                    email_text = element.text
                    if '@' in email_text and '.' in email_text:
                        # Looks like an email
                        emails.add(email_text.strip())
            except Exception as e:
                print(f"Error scanning for obfuscated emails: {e}")

            # Also look for mailto: links which often contain emails
            try:
                mailto_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')
                for link in mailto_links:
                    email = link.get_attribute('href').replace('mailto:', '').split('?')[0]
                    if email and '@' in email:
                        emails.add(email)
            except Exception as e:
                print(f"Error scanning mailto links: {e}")

            # Filter out common false positives and non-business emails
            filtered_emails = []
            for email in emails:
                # Skip emails that are likely not contact emails
                if any(domain in email.lower() for domain in ['example.com', 'yourdomain', 'domain.com']):
                    continue
                # Skip emails that are part of JavaScript or CSS
                if any(code in email for code in ['{', '}', '(', ')', '[', ']', '\\', '/']):
                    continue
                # Basic validation
                if '@' in email and '.' in email.split('@')[1]:
                    filtered_emails.append(email)

            if filtered_emails:
                alternative_contacts['Email'] = ', '.join(filtered_emails[:5])  # Increased limit to 5 emails
                print(f"Found {len(filtered_emails)} email addresses: {alternative_contacts['Email']}")

            # 3. Scan for phone numbers (enhanced)
            print("Scanning for phone numbers...")
            phone_numbers = []

            # Look for tel: links first (more reliable)
            tel_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="tel:"]')
            for link in tel_links:
                phone = link.get_attribute('href').replace('tel:', '')
                if phone and len(phone) > 5:  # Basic validation
                    phone_numbers.append(phone)

            # Look for elements that might contain phone numbers
            try:
                phone_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    '[class*="phone"], [class*="tel"], [class*="contact"], [id*="phone"], [id*="tel"]')

                for element in phone_elements:
                    text = element.text
                    if text:
                        # US/Canada phone pattern
                        phone_matches = re.findall(r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
                        for match in phone_matches:
                            if match and len(match) > 5:
                                phone_numbers.append(match)
            except Exception as e:
                print(f"Error scanning for phone elements: {e}")

            # If still no phone numbers, try pattern matching on the whole page
            if not phone_numbers:
                # US/Canada phone pattern
                phone_pattern = r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
                phones = set(re.findall(phone_pattern, page_source))
                phone_numbers.extend(list(phones)[:5])  # Increased limit to 5 phone numbers

            if phone_numbers:
                alternative_contacts['Phone'] = ', '.join(phone_numbers[:5])
                print(f"Found {len(phone_numbers)} phone numbers: {alternative_contacts['Phone']}")

            # 4. Scan for social media links (enhanced)
            print("Scanning for social media links...")
            social_media = {
                'LinkedIn': r'linkedin\.com/(?:company|in|school)/[^"\'\s<>]+',
                'Facebook': r'facebook\.com/[^"\'\s<>]+',
                'Twitter': r'(?:twitter|x)\.com/[^"\'\s<>]+',
                'Instagram': r'instagram\.com/[^"\'\s<>]+',
            }

            # Also look for social media icons which might not have the domain in the URL
            social_icons = {
                'LinkedIn': ['linkedin', 'li-in'],
                'Facebook': ['facebook', 'fb'],
                'Twitter': ['twitter', 'tweet', 'x-twitter'],
                'Instagram': ['instagram', 'insta', 'ig']
            }

            # First try to find links with the domain patterns
            for platform, pattern in social_media.items():
                matches = set(re.findall(pattern, page_source))
                if matches:
                    # Clean up the URLs
                    cleaned_urls = []
                    for match in matches:
                        # Add https:// if missing
                        if not match.startswith('http'):
                            match = 'https://' + match
                        cleaned_urls.append(match)

                    alternative_contacts[platform] = ', '.join(cleaned_urls[:3])  # Limit to first 3 links

            # Then try to find social media icons
            try:
                for platform, keywords in social_icons.items():
                    if platform in alternative_contacts:
                        continue  # Already found this platform

                    for keyword in keywords:
                        # Look for elements with class or ID containing the social media keyword
                        icon_elements = self.driver.find_elements(By.CSS_SELECTOR,
                            f'a[class*="{keyword}"], a[id*="{keyword}"], i[class*="{keyword}"], span[class*="{keyword}"]')

                        for element in icon_elements:
                            # Try to find the parent <a> tag if this is just an icon
                            if element.tag_name != 'a':
                                try:
                                    parent = element.find_element(By.XPATH, './ancestor::a')
                                    element = parent
                                except:
                                    continue

                            href = element.get_attribute('href')
                            if href and href.startswith('http') and platform not in alternative_contacts:
                                alternative_contacts[platform] = href
                                break
            except Exception as e:
                print(f"Error scanning for social media icons: {e}")

            # 5. Look for "Contact Us" and "About Us" pages (enhanced)
            print("Scanning for additional contact and about pages...")
            contact_links = []
            about_links = []

            # More comprehensive search for contact and about pages
            contact_selectors = [
                "//a[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]",
                "//a[contains(@href, 'contact')]",
                "//a[contains(translate(text(), 'REACH', 'reach'), 'reach us')]",
                "//a[contains(translate(text(), 'GET IN TOUCH', 'get in touch'), 'get in touch')]",
                "//a[contains(@class, 'contact')]",
                "//a[contains(@id, 'contact')]"
            ]

            about_selectors = [
                "//a[contains(translate(text(), 'ABOUT', 'about'), 'about')]",
                "//a[contains(@href, 'about')]",
                "//a[contains(translate(text(), 'TEAM', 'team'), 'team')]",
                "//a[contains(@href, 'team')]",
                "//a[contains(translate(text(), 'STAFF', 'staff'), 'staff')]",
                "//a[contains(@href, 'staff')]",
                "//a[contains(translate(text(), 'PEOPLE', 'people'), 'people')]",
                "//a[contains(@href, 'people')]"
            ]

            # Find contact pages
            for selector in contact_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements[:3]:
                        href = element.get_attribute('href')
                        if href and href.startswith('http') and href not in contact_links:
                            contact_links.append(href)
                except Exception as e:
                    print(f"Error with contact selector {selector}: {e}")

            # Find about/team pages
            for selector in about_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements[:3]:
                        href = element.get_attribute('href')
                        if href and href.startswith('http') and href not in about_links:
                            about_links.append(href)
                except Exception as e:
                    print(f"Error with about selector {selector}: {e}")

            if contact_links:
                alternative_contacts['Contact Pages'] = ', '.join(contact_links[:3])
                print(f"Found {len(contact_links)} contact pages: {alternative_contacts['Contact Pages']}")

            if about_links:
                alternative_contacts['About/Team Pages'] = ', '.join(about_links[:3])
                print(f"Found {len(about_links)} about/team pages: {alternative_contacts['About/Team Pages']}")

            # 6. Try to visit contact and about pages to gather more information
            pages_to_visit = []

            # Add contact pages to visit list
            if alternative_contacts.get('Contact Pages'):
                contact_pages = alternative_contacts['Contact Pages'].split(',')
                pages_to_visit.extend([(page.strip(), 'contact') for page in contact_pages[:2]])  # Limit to first 2

            # Add about/team pages to visit list
            if alternative_contacts.get('About/Team Pages'):
                about_pages = alternative_contacts['About/Team Pages'].split(',')
                pages_to_visit.extend([(page.strip(), 'about') for page in about_pages[:2]])  # Limit to first 2

            # Always visit these pages, even if we already found contact info
            if pages_to_visit:
                print(f"Visiting {len(pages_to_visit)} additional pages for thorough data enrichment...")

                for i, (page_url, page_type) in enumerate(pages_to_visit):
                    print(f"Visiting {page_type} page ({i+1}/{len(pages_to_visit)}): {page_url}")

                    try:
                        self.driver.get(page_url)
                        time.sleep(3)  # Wait for page to load

                        # Take a screenshot of the page
                        self.driver.save_screenshot(f"{page_type}_page_{i+1}.png")

                        # Scan this page for contact information
                        page_info = self._scan_contact_page_directly()

                        if page_info:
                            print(f"Found additional contact information on {page_type} page:")
                            for key, value in page_info.items():
                                print(f"  - {key}: {value}")

                            # Merge the results
                            for key, value in page_info.items():
                                if key not in alternative_contacts or not alternative_contacts[key]:
                                    alternative_contacts[key] = value
                                elif value and value not in alternative_contacts[key]:
                                    # Append new values
                                    alternative_contacts[key] += f", {value}"
                        else:
                            print(f"No additional contact information found on {page_type} page")
                    except Exception as e:
                        print(f"Error visiting {page_type} page: {e}")
            else:
                print("No additional pages found to visit for data enrichment")

            # Return to the original page
            if self.driver.current_url != original_url:
                print(f"Returning to original page: {original_url}")
                self.driver.get(original_url)
                time.sleep(1)

            # Take a final screenshot
            self.driver.save_screenshot("scanning_for_alternative_contacts_end.png")

            # Print summary of what we found
            print(f"Alternative contact scan complete. Found {len(alternative_contacts)} types of contact information.")
            for method, value in alternative_contacts.items():
                print(f"- {method}: {value}")

            return alternative_contacts

        except Exception as e:
            print(f"Error scanning for alternative contacts: {e}")
            traceback.print_exc()
            return {}

    def _analyze_form_structure(self, form_element) -> Dict[str, List[str]]:
        """Analyze a form's structure using AI techniques to generate custom selectors

        Args:
            form_element: The form element to analyze

        Returns:
            Dictionary of field types and their corresponding selectors
        """
        print("Analyzing form structure with AI techniques...")

        # Initialize the result dictionary with empty lists for each field type
        custom_selectors = {
            "name": [],
            "first_name": [],
            "last_name": [],
            "email": [],
            "phone": [],
            "message": [],
            "company": [],
            "submit": []
        }

        try:
            # Get all input, select, and textarea elements in the form
            input_elements = form_element.find_elements(By.CSS_SELECTOR, "input:not([type='hidden']), select, textarea")

            print(f"Found {len(input_elements)} form elements to analyze")

            # Analyze each element to determine its likely field type
            for element in input_elements:
                # Get element attributes
                element_id = element.get_attribute('id') or ''
                element_name = element.get_attribute('name') or ''
                element_class = element.get_attribute('class') or ''
                element_type = element.get_attribute('type') or ''
                element_placeholder = element.get_attribute('placeholder') or ''
                element_tag = element.tag_name

                # Get label text if available
                label_text = self._get_label_for_element(element) or ''

                # Convert attributes to lowercase for easier matching
                element_id_lower = element_id.lower()
                element_name_lower = element_name.lower()
                element_class_lower = element_class.lower()
                element_placeholder_lower = element_placeholder.lower()
                label_text_lower = label_text.lower()

                # Create a CSS selector for this element
                if element_id:
                    selector = f"#{element_id}"
                elif element_name:
                    selector = f"{element_tag}[name='{element_name}']"
                else:
                    # Skip elements without ID or name
                    continue

                # Check for submit buttons
                if element_type == 'submit' or 'submit' in element_class_lower or 'submit' in element_id_lower:
                    custom_selectors['submit'].append(selector)
                    continue

                # Check for email fields
                if (element_type == 'email' or
                    'email' in element_id_lower or
                    'email' in element_name_lower or
                    'email' in element_placeholder_lower or
                    'email' in label_text_lower):
                    custom_selectors['email'].append(selector)
                    continue

                # Check for phone fields
                if (element_type == 'tel' or
                    'phone' in element_id_lower or
                    'phone' in element_name_lower or
                    'phone' in element_placeholder_lower or
                    'tel' in element_id_lower or
                    'tel' in element_name_lower or
                    'phone' in label_text_lower):
                    custom_selectors['phone'].append(selector)
                    continue

                # Check for message/comment fields
                if (element_tag == 'textarea' or
                    'message' in element_id_lower or
                    'message' in element_name_lower or
                    'message' in element_placeholder_lower or
                    'comment' in element_id_lower or
                    'comment' in element_name_lower or
                    'message' in label_text_lower or
                    'comment' in label_text_lower):
                    custom_selectors['message'].append(selector)
                    continue

                # Check for company fields
                if ('company' in element_id_lower or
                    'company' in element_name_lower or
                    'company' in element_placeholder_lower or
                    'organization' in element_id_lower or
                    'organization' in element_name_lower or
                    'company' in label_text_lower or
                    'organization' in label_text_lower):
                    custom_selectors['company'].append(selector)
                    continue

                # Check for first name fields
                if ('first' in element_id_lower or
                    'first' in element_name_lower or
                    'first' in element_placeholder_lower or
                    'fname' in element_id_lower or
                    'fname' in element_name_lower or
                    'first name' in label_text_lower):
                    custom_selectors['first_name'].append(selector)
                    continue

                # Check for last name fields
                if ('last' in element_id_lower or
                    'last' in element_name_lower or
                    'last' in element_placeholder_lower or
                    'lname' in element_id_lower or
                    'lname' in element_name_lower or
                    'last name' in label_text_lower):
                    custom_selectors['last_name'].append(selector)
                    continue

                # Check for full name fields (if not already categorized as first/last)
                if ('name' in element_id_lower or
                    'name' in element_name_lower or
                    'name' in element_placeholder_lower or
                    'name' in label_text_lower):
                    # Skip username fields
                    if ('user' in element_id_lower or
                        'user' in element_name_lower or
                        'user' in element_placeholder_lower or
                        'user' in label_text_lower):
                        continue
                    custom_selectors['name'].append(selector)
                    continue

            # Look for submit buttons outside of input elements (e.g., button tags)
            submit_buttons = form_element.find_elements(By.CSS_SELECTOR, "button[type='submit'], button.submit, button[class*='submit'], button[id*='submit']")
            for button in submit_buttons:
                button_id = button.get_attribute('id') or ''
                if button_id:
                    custom_selectors['submit'].append(f"#{button_id}")
                else:
                    # Create a more complex selector for buttons without ID
                    button_class = button.get_attribute('class') or ''
                    if button_class:
                        custom_selectors['submit'].append(f"button.{button_class.split()[0]}")

            # Print summary of what we found
            total_selectors = sum(len(selectors) for selectors in custom_selectors.values())
            print(f"Form analysis complete. Generated {total_selectors} custom selectors:")
            for field_type, selectors in custom_selectors.items():
                if selectors:
                    print(f"- {field_type}: {len(selectors)} selectors")

            return custom_selectors

        except Exception as e:
            print(f"Error analyzing form structure: {e}")
            traceback.print_exc()
            return custom_selectors

    def _get_label_for_element(self, element) -> Optional[str]:
        """Get the label text for a form element

        Args:
            element: The form element to find a label for

        Returns:
            Label text or None if not found
        """
        try:
            # Try to find label using 'for' attribute
            element_id = element.get_attribute('id')
            if element_id:
                try:
                    label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{element_id}']")
                    return label.text.strip()
                except:
                    pass

            # Try to find label as a parent
            try:
                label = element.find_element(By.XPATH, "./ancestor::label")
                return label.text.strip()
            except:
                pass

            # Try to find label as a sibling
            try:
                label = element.find_element(By.XPATH, "./preceding-sibling::label[1]")
                return label.text.strip()
            except:
                pass

            # Try to find any text element nearby that might be a label
            try:
                parent = element.find_element(By.XPATH, "./parent::*")
                siblings = parent.find_elements(By.XPATH, "./*")
                for sibling in siblings:
                    if sibling.tag_name in ['label', 'span', 'div'] and sibling != element:
                        text = sibling.text.strip()
                        if text and len(text) < 50:  # Basic validation for label text
                            return text
            except:
                pass

            return None
        except Exception as e:
            print(f"Error getting label for element: {e}")
            return None

    def _scan_for_alternative_contacts(self) -> Dict[str, Any]:
        """Scan the current page for alternative contact methods using enhanced data enrichment if available

        Returns:
            Dictionary with alternative contact methods
        """
        # Use enhanced data enrichment if available
        if self.enhanced_data_enrichment:
            print("Using enhanced data enrichment to scan for alternative contact methods")
            enriched_data = self.enhanced_data_enrichment.enrich_contact_data(
                contact_id=self.current_contact_id
            )

            if enriched_data:
                print(f"Enhanced data enrichment found {len(enriched_data)} data points")
                return enriched_data
            else:
                print("Enhanced data enrichment did not find any data, falling back to basic methods")

        # Fall back to the direct scan method
        print("Using direct scan method for alternative contact methods")
        return self._scan_contact_page_directly()

    def _scan_contact_page_directly(self) -> Dict[str, str]:
        """Scan a contact page for contact information with enhanced extraction

        This method performs a comprehensive scan of a specific page to extract
        all possible contact information for data enrichment purposes.

        Returns:
            Dictionary of contact methods and their values
        """
        contact_info = {}

        try:
            # Get the page source and URL
            page_source = self.driver.page_source
            current_url = self.driver.current_url

            print(f"Scanning page for contact information: {current_url}")

            # Take a screenshot for reference
            self.driver.save_screenshot("scanning_page_directly.png")

            # 1. Scan for email addresses (enhanced)
            print("Scanning for email addresses...")
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = set(re.findall(email_pattern, page_source))

            # Also look for mailto: links
            mailto_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')
            for link in mailto_links:
                email = link.get_attribute('href').replace('mailto:', '').split('?')[0]
                if email and '@' in email:
                    emails.add(email)

            # Look for obfuscated emails (common anti-scraping technique)
            try:
                obfuscated_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    '[data-email], [data-mail], [data-user], [data-domain], [class*="email"], [class*="mail"]')

                for element in obfuscated_elements:
                    # Try to get the actual text which might be the email
                    email_text = element.text
                    if '@' in email_text and '.' in email_text:
                        # Looks like an email
                        emails.add(email_text.strip())

                    # Check for data attributes that might contain email parts
                    data_email = element.get_attribute('data-email')
                    data_user = element.get_attribute('data-user')
                    data_domain = element.get_attribute('data-domain')

                    if data_email and '@' in data_email:
                        emails.add(data_email)
                    elif data_user and data_domain:
                        emails.add(f"{data_user}@{data_domain}")
            except Exception as e:
                print(f"Error scanning for obfuscated emails: {e}")

            # Filter emails
            filtered_emails = []
            for email in emails:
                if any(domain in email.lower() for domain in ['example.com', 'yourdomain', 'domain.com']):
                    continue
                if any(code in email for code in ['{', '}', '(', ')', '[', ']', '\\', '/']):
                    continue
                # Basic validation
                if '@' in email and '.' in email.split('@')[1]:
                    filtered_emails.append(email)

            if filtered_emails:
                contact_info['Email'] = ', '.join(filtered_emails[:5])
                print(f"Found {len(filtered_emails)} email addresses")

            # 2. Scan for phone numbers (enhanced)
            print("Scanning for phone numbers...")
            phone_numbers = []

            # Look for tel: links first (more reliable)
            tel_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="tel:"]')
            for link in tel_links:
                phone = link.get_attribute('href').replace('tel:', '')
                if phone and len(phone) > 5:  # Basic validation
                    phone_numbers.append(phone)

            # Look for elements that might contain phone numbers
            try:
                phone_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    '[class*="phone"], [class*="tel"], [class*="contact"], [id*="phone"], [id*="tel"]')

                for element in phone_elements:
                    text = element.text
                    if text:
                        # US/Canada phone pattern
                        phone_matches = re.findall(r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
                        for match in phone_matches:
                            if match and len(match) > 5:
                                phone_numbers.append(match)
            except Exception as e:
                print(f"Error scanning for phone elements: {e}")

            # Pattern matching on the whole page
            if not phone_numbers:
                # US/Canada phone pattern
                phone_pattern = r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
                phones = set(re.findall(phone_pattern, page_source))
                phone_numbers.extend(list(phones)[:5])

            if phone_numbers:
                contact_info['Phone'] = ', '.join(phone_numbers[:5])
                print(f"Found {len(phone_numbers)} phone numbers")

            # 3. Scan for social media links (enhanced)
            print("Scanning for social media links...")
            social_media = {
                'LinkedIn': r'linkedin\.com/(?:company|in|school)/[^"\'\s<>]+',
                'Facebook': r'facebook\.com/[^"\'\s<>]+',
                'Twitter': r'(?:twitter|x)\.com/[^"\'\s<>]+',
                'Instagram': r'instagram\.com/[^"\'\s<>]+',
            }

            # Also look for social media icons which might not have the domain in the URL
            social_icons = {
                'LinkedIn': ['linkedin', 'li-in'],
                'Facebook': ['facebook', 'fb'],
                'Twitter': ['twitter', 'tweet', 'x-twitter'],
                'Instagram': ['instagram', 'insta', 'ig']
            }

            # First try to find links with the domain patterns
            for platform, pattern in social_media.items():
                matches = set(re.findall(pattern, page_source))
                if matches:
                    # Clean up the URLs
                    cleaned_urls = []
                    for match in matches:
                        # Add https:// if missing
                        if not match.startswith('http'):
                            match = 'https://' + match
                        cleaned_urls.append(match)

                    contact_info[platform] = ', '.join(cleaned_urls[:3])

            # Then try to find social media icons
            try:
                for platform, keywords in social_icons.items():
                    if platform in contact_info:
                        continue  # Already found this platform

                    for keyword in keywords:
                        # Look for elements with class or ID containing the social media keyword
                        icon_elements = self.driver.find_elements(By.CSS_SELECTOR,
                            f'a[class*="{keyword}"], a[id*="{keyword}"], i[class*="{keyword}"], span[class*="{keyword}"]')

                        for element in icon_elements:
                            # Try to find the parent <a> tag if this is just an icon
                            if element.tag_name != 'a':
                                try:
                                    parent = element.find_element(By.XPATH, './ancestor::a')
                                    element = parent
                                except:
                                    continue

                            href = element.get_attribute('href')
                            if href and href.startswith('http') and platform not in contact_info:
                                contact_info[platform] = href
                                break
            except Exception as e:
                print(f"Error scanning for social media icons: {e}")

            # 4. Scan for physical address
            print("Scanning for physical address...")
            try:
                # Look for address elements
                address_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    'address, [class*="address"], [id*="address"], [itemprop="address"]')

                if address_elements:
                    for element in address_elements:
                        address_text = element.text.strip()
                        if address_text and len(address_text) > 10:  # Basic validation
                            # Clean up the address text
                            address_text = re.sub(r'\s+', ' ', address_text)
                            contact_info['Address'] = address_text
                            print(f"Found physical address")
                            break
            except Exception as e:
                print(f"Error scanning for address: {e}")

            # 5. Look for business hours
            print("Scanning for business hours...")
            try:
                # Look for hours elements
                hours_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    '[class*="hours"], [id*="hours"], [class*="schedule"], [id*="schedule"], [itemprop="openingHours"]')

                if hours_elements:
                    for element in hours_elements:
                        hours_text = element.text.strip()
                        if hours_text and len(hours_text) > 5:
                            # Check if it contains day names
                            if any(day in hours_text.lower() for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']):
                                contact_info['Business Hours'] = hours_text
                                print(f"Found business hours")
                                break
            except Exception as e:
                print(f"Error scanning for business hours: {e}")

            # 6. Look for contact person names
            print("Scanning for contact person names...")
            try:
                # Look for team/staff elements
                person_elements = self.driver.find_elements(By.CSS_SELECTOR,
                    '[class*="team"], [id*="team"], [class*="staff"], [id*="staff"], [class*="employee"], [class*="member"]')

                person_names = []
                for element in person_elements:
                    # Look for name elements within team/staff sections
                    name_elements = element.find_elements(By.CSS_SELECTOR,
                        '[class*="name"], [id*="name"], h2, h3, h4, strong')

                    for name_el in name_elements:
                        name_text = name_el.text.strip()
                        if name_text and len(name_text) > 3 and len(name_text) < 50:
                            # Basic validation - names usually have spaces and aren't too long
                            if ' ' in name_text and not any(char in name_text for char in ['@', '/', '\\', '|']):
                                person_names.append(name_text)

                if person_names:
                    contact_info['Contact Persons'] = ', '.join(person_names[:5])  # Limit to 5 names
                    print(f"Found {len(person_names)} contact persons")
            except Exception as e:
                print(f"Error scanning for contact persons: {e}")

            # Print summary of what we found
            print(f"Contact page scan complete. Found {len(contact_info)} types of contact information.")

            return contact_info

        except Exception as e:
            print(f"Error scanning contact page directly: {e}")
            traceback.print_exc()
            return {}

    def clear_cookies(self, domain: str = None) -> None:
        """Clear saved cookies

        Args:
            domain: Domain to clear cookies for (e.g., 'linkedin.com'). If None, clear all cookies.
        """
        try:
            if domain:
                cookies_file = self.linkedin_cookies_file if 'linkedin' in domain else os.path.join(self.cookies_dir, f"{domain.replace('.', '_')}_cookies.pkl")
                if os.path.exists(cookies_file):
                    os.remove(cookies_file)
                    print(f"Cleared cookies for {domain}")
                else:
                    print(f"No cookies file found for {domain}")
            else:
                # Clear all cookies
                for file in os.listdir(self.cookies_dir):
                    if file.endswith('.pkl'):
                        os.remove(os.path.join(self.cookies_dir, file))
                print("Cleared all cookies")

            # Also clear browser cookies
            if self.driver:
                self.driver.delete_all_cookies()
                print("Cleared browser cookies")
        except Exception as e:
            print(f"Error clearing cookies: {e}")

    def close(self) -> None:
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            print("WebDriver closed.")

if __name__ == "__main__":
    bot = ContactBot(headless=False)
    try:
        # Example: Process contacts from Supabase
        bot.process_contacts_from_supabase(limit=5)

        # Example: Process contacts from CSV
        # bot.process_csv("contacts.csv")
    finally:
        bot.close()
