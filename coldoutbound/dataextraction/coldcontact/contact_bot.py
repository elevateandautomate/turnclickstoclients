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
import traceback
from typing import Dict, List, Optional, Union, Any

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

# Supabase
from supabase import create_client, Client

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"  # Using the core_data table (renamed from dentist)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MSEDGEDRIVER_LOG_PATH = os.path.join(BASE_DIR, 'msedgedriver.log')

# LinkedIn credentials - should be stored securely in production
LINKEDIN_USERNAME = ""  # Fill in your LinkedIn username
LINKEDIN_PASSWORD = ""  # Fill in your LinkedIn password

class ContactBot:
    """Bot for automating contact form filling and LinkedIn outreach"""

    def __init__(self, headless: bool = False):
        """Initialize the bot

        Args:
            headless: Whether to run the browser in headless mode
        """
        self.supabase = self._init_supabase()
        self.driver = self._init_webdriver(headless)
        self.wait = WebDriverWait(self.driver, 10)
        self.linkedin_logged_in = False

    def _init_supabase(self) -> Optional[Client]:
        """Initialize Supabase client

        Returns:
            Supabase client or None if initialization fails
        """
        try:
            if SUPABASE_URL and SUPABASE_KEY:
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
                print("Successfully initialized Supabase client.")
                return supabase
            else:
                print("CRITICAL: Supabase URL or Key is missing.")
                return None
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            return None

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

    def process_contacts_from_supabase(self, limit: int = 10, filter_status: str = 'all', keep_browser_open: bool = False, resume: bool = True) -> None:
        """Process contacts from Supabase table

        Args:
            limit: Maximum number of contacts to process
            filter_status: Filter contacts by status ('all', 'pending', 'failed')
            keep_browser_open: Whether to keep the browser open after processing
            resume: Whether to resume from the last processed contact
        """
        if not self.supabase:
            print("Supabase client not initialized. Cannot process contacts.")
            return

        try:
            # Start building the query
            query = self.supabase.table(TABLE_NAME).select("*")

            # Apply filter based on filter_status
            if filter_status == 'pending':
                query = query.is_("contact_form_submitted", None)
            elif filter_status == 'failed':
                query = query.eq("contact_form_submitted", False)

            # Apply limit
            query = query.limit(limit)

            # Execute the query
            response = query.execute()

            contacts = response.data
            print(f"Found {len(contacts)} contacts to process from table {TABLE_NAME}.")

            # Process all contacts in the batch
            for i, contact in enumerate(contacts):
                print(f"Processing contact {i+1} of {len(contacts)}")
                self._process_single_contact(contact)

                # Only pause between contacts if we have more to process
                if i < len(contacts) - 1:
                    print("Waiting 2 seconds before processing next contact...")
                    time.sleep(2)

            # Only keep the browser open after all contacts are processed
            if keep_browser_open and not self.headless:
                print("All contacts processed. Keeping browser open for inspection")
                for i in range(60, 0, -1):
                    print(f"\rBrowser will close in {i} seconds...", end="")
                    time.sleep(1)

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

    def _process_single_contact(self, contact: Dict[str, Any]) -> None:
        """Process a single contact

        Args:
            contact: Contact data from Supabase
        """
        contact_id = contact.get("id")
        website_url = contact.get("website_url")

        if not website_url:
            self._update_status(contact_id, "website_visited", False, "No website URL provided")
            return

        try:
            # Visit website
            print(f"Visiting website: {website_url}")
            self.driver.get(website_url)
            time.sleep(2)  # Allow page to load
            self._update_status(contact_id, "website_visited", True)

            # Find contact form
            contact_form = self._find_contact_form()
            if not contact_form:
                self._update_status(contact_id, "contact_form_found", False, "Contact form not found")
                return

            self._update_status(contact_id, "contact_form_found", True)

            # Fill contact form
            success, message = self._fill_contact_form(contact)
            self._update_status(contact_id, "contact_form_submitted", success, message)

            # Connect on LinkedIn
            if contact.get("linkedin_url") or contact.get("name"):
                linkedin_success, linkedin_message = self._connect_on_linkedin(contact)
                self._update_status(contact_id, "linkedin_connected", linkedin_success, linkedin_message)

        except Exception as e:
            print(f"Error processing contact {contact.get('name', 'Unknown')}: {e}")
            traceback.print_exc()
            self._update_status(contact_id, "error", str(e))

    def _find_contact_form(self) -> Optional[Any]:
        """Find contact form on current page

        Returns:
            Contact form element or None if not found
        """
        # Strategy 1: Look for forms with common contact form keywords
        try:
            # Look for forms with contact-related IDs or classes
            contact_form_selectors = [
                "form[id*='contact']",
                "form[class*='contact']",
                "div[id*='contact'] form",
                "div[class*='contact'] form",
                "section[id*='contact'] form",
                "section[class*='contact'] form",
                # More generic form selectors
                "form:has(input[type='email'])",
                "form:has(textarea)",
                "form"
            ]

            for selector in contact_form_selectors:
                try:
                    forms = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if forms:
                        # Prioritize forms that have email fields and textareas
                        for form in forms:
                            if (form.find_elements(By.CSS_SELECTOR, "input[type='email']") and
                                form.find_elements(By.TAG_NAME, "textarea")):
                                print(f"Found contact form with selector: {selector}")
                                return form

                        # If no ideal form found, return the first one
                        print(f"Found potential contact form with selector: {selector}")
                        return forms[0]
                except:
                    continue

            # Strategy 2: Look for contact page links and navigate to them
            contact_link_selectors = [
                "a[href*='contact']",
                "a[text()*='Contact']",
                "a[text()*='contact']"
            ]

            for selector in contact_link_selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if links:
                        print(f"Found contact page link: {links[0].get_attribute('href')}")
                        links[0].click()
                        time.sleep(2)  # Wait for page to load

                        # Try to find form on contact page
                        return self._find_contact_form()
                except:
                    continue

            return None

        except Exception as e:
            print(f"Error finding contact form: {e}")
            return None

    def _fill_contact_form(self, contact: Dict[str, Any]) -> tuple[bool, str]:
        """Fill and submit contact form

        Args:
            contact: Contact data

        Returns:
            Tuple of (success, message)
        """
        try:
            # Common field identifiers
            name_selectors = [
                "input[name*='name']",
                "input[id*='name']",
                "input[placeholder*='name' i]",
                "input[class*='name']"
            ]

            email_selectors = [
                "input[type='email']",
                "input[name*='email']",
                "input[id*='email']",
                "input[placeholder*='email' i]",
                "input[class*='email']"
            ]

            message_selectors = [
                "textarea",
                "textarea[name*='message']",
                "textarea[id*='message']",
                "textarea[placeholder*='message' i]",
                "textarea[class*='message']"
            ]

            # Try to fill name field
            name_field = None
            for selector in name_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if fields:
                        name_field = fields[0]
                        break
                except:
                    continue

            if name_field:
                name_field.clear()
                name_field.send_keys(contact.get("name", ""))
                print("Filled name field")

            # Try to fill email field
            email_field = None
            for selector in email_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if fields:
                        email_field = fields[0]
                        break
                except:
                    continue

            if email_field:
                email_field.clear()
                email_field.send_keys(contact.get("email", ""))
                print("Filled email field")

            # Try to fill message field
            message_field = None
            for selector in message_selectors:
                try:
                    fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if fields:
                        message_field = fields[0]
                        break
                except:
                    continue

            if message_field:
                message_field.clear()
                message_field.send_keys(self._generate_message(contact))
                print("Filled message field")

            # If we couldn't fill any fields, return failure
            if not (name_field or email_field or message_field):
                return False, "Could not identify form fields"

            # For now, we'll just return success without actually submitting
            # In a real implementation, you would uncomment the submit code

            # # Try to find and click submit button
            # submit_selectors = [
            #     "button[type='submit']",
            #     "input[type='submit']",
            #     "button:contains('Send')",
            #     "button:contains('Submit')",
            #     "button:contains('Contact')",
            #     "button"
            # ]
            #
            # for selector in submit_selectors:
            #     try:
            #         buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
            #         if buttons:
            #             buttons[0].click()
            #             time.sleep(2)  # Wait for submission
            #             print("Clicked submit button")
            #             return True, "Form submitted successfully"
            #     except:
            #         continue

            return True, "Form fields identified and filled (submission disabled for testing)"

        except Exception as e:
            print(f"Error filling contact form: {e}")
            return False, f"Error filling form: {str(e)}"

    def _generate_message(self, contact: Dict[str, Any]) -> str:
        """Generate personalized message based on contact data

        Args:
            contact: Contact data

        Returns:
            Personalized message
        """
        # Use contact data to personalize message
        company = contact.get("company", "your company")
        name = contact.get("name", "").split()[0] if contact.get("name") else ""

        if name:
            greeting = f"Hi {name},"
        else:
            greeting = "Hello,"

        message = f"{greeting}\n\n"
        message += f"I came across {company} and was impressed by your work. "
        message += "I'd love to connect and discuss potential opportunities to collaborate.\n\n"
        message += "Looking forward to hearing from you,\n"
        message += "Your Name"  # Replace with your actual name

        return message

    def _connect_on_linkedin(self, contact: Dict[str, Any]) -> tuple[bool, str]:
        """Find user on LinkedIn and send connection request

        Args:
            contact: Contact data

        Returns:
            Tuple of (success, message)
        """
        if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
            return False, "LinkedIn credentials not configured"

        try:
            # Login to LinkedIn if not already logged in
            if not self.linkedin_logged_in:
                self._login_to_linkedin()

            # Search for user
            search_term = contact.get("name", "")
            if contact.get("company"):
                search_term += f" {contact.get('company')}"

            if not search_term:
                return False, "No name or company provided for LinkedIn search"

            # Navigate to LinkedIn search
            self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={search_term}")
            time.sleep(3)  # Wait for search results

            # Find first result
            try:
                first_result = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".entity-result__item")))

                # Check if "Connect" button exists
                connect_buttons = first_result.find_elements(By.CSS_SELECTOR, "button:contains('Connect')")
                if connect_buttons:
                    # Click Connect button
                    connect_buttons[0].click()
                    time.sleep(1)

                    # Add personalized note
                    try:
                        add_note_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button:contains('Add a note')")))
                        add_note_button.click()
                        time.sleep(1)

                        # Enter personalized message
                        message_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea#custom-message")))
                        message_field.clear()
                        message_field.send_keys(self._generate_linkedin_message(contact))

                        # Send invitation
                        send_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button:contains('Send')")))
                        send_button.click()
                        time.sleep(1)

                        return True, "LinkedIn connection request sent with personalized message"
                    except:
                        # If adding a note fails, just send the connection request
                        send_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button:contains('Send')")))
                        send_button.click()
                        time.sleep(1)

                        return True, "LinkedIn connection request sent without personalized message"
                else:
                    return False, "Connect button not found for this user"

            except:
                return False, "No search results found on LinkedIn"

        except Exception as e:
            print(f"Error connecting on LinkedIn: {e}")
            return False, f"Error connecting on LinkedIn: {str(e)}"

    def _login_to_linkedin(self) -> None:
        """Login to LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)

            # Enter username
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            username_field.clear()
            username_field.send_keys(LINKEDIN_USERNAME)

            # Enter password
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_field.clear()
            password_field.send_keys(LINKEDIN_PASSWORD)

            # Click login button
            login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_button.click()

            # Wait for login to complete
            time.sleep(5)

            # Check if login was successful
            if "feed" in self.driver.current_url or "checkpoint" in self.driver.current_url:
                print("Successfully logged in to LinkedIn")
                self.linkedin_logged_in = True
            else:
                print("Failed to login to LinkedIn")
                self.linkedin_logged_in = False

        except Exception as e:
            print(f"Error logging in to LinkedIn: {e}")
            self.linkedin_logged_in = False

    def _generate_linkedin_message(self, contact: Dict[str, Any]) -> str:
        """Generate personalized LinkedIn connection message

        Args:
            contact: Contact data

        Returns:
            Personalized message
        """
        name = contact.get("name", "").split()[0] if contact.get("name") else ""
        company = contact.get("company", "your company")

        message = f"Hi {name}, I came across {company} and was impressed by your work. "
        message += "I'd love to connect and discuss potential opportunities to collaborate."

        # Ensure message is within LinkedIn's character limit (300 characters)
        if len(message) > 300:
            message = message[:297] + "..."

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

        try:
            update_data = {
                status_field: success,
                f"{status_field}_message": message,
                f"{status_field}_timestamp": "now()"
            }

            self.supabase.table(TABLE_NAME) \
                .update(update_data) \
                .eq("id", contact_id) \
                .execute()

            print(f"Updated status for contact {contact_id}: {status_field} = {success}")

        except Exception as e:
            print(f"Error updating status: {e}")

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
