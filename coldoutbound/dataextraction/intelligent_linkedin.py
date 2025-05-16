"""
Intelligent LinkedIn integration with advanced matching and messaging
"""

import time
import re
import json
import traceback
import random
from typing import Dict, List, Any, Tuple, Optional
from urllib.parse import quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException

# Import fuzzy matching library if available
try:
    from fuzzywuzzy import fuzz
    FUZZY_MATCHING_AVAILABLE = True
except ImportError:
    FUZZY_MATCHING_AVAILABLE = False
    print("FuzzyWuzzy library not available. Install with: pip install fuzzywuzzy python-Levenshtein")

class IntelligentLinkedIn:
    """Intelligent LinkedIn integration with advanced matching and messaging"""
    
    def __init__(self, driver, settings=None, logger=None):
        """Initialize the intelligent LinkedIn integration
        
        Args:
            driver: Selenium WebDriver instance
            settings: Dictionary of settings
            logger: Logger instance
        """
        self.driver = driver
        self.settings = settings or {}
        self.logger = logger
        self.linkedin_logged_in = False
        self.linkedin_log = {
            "contact": {},
            "search_query": "",
            "profiles_found": [],
            "best_match": None,
            "best_match_score": 0,
            "action_taken": "",
            "result": "",
            "timestamp": ""
        }
    
    def connect_with_contact(self, contact: Dict[str, Any]) -> Tuple[bool, str]:
        """Connect with a contact on LinkedIn using intelligent matching
        
        Args:
            contact: Contact data dictionary
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Extract contact information
            contact_name = contact.get('name', '')
            company_name = contact.get('company', '')
            location = ''
            
            # Try to extract location from various fields
            if contact.get('city') and contact.get('state'):
                location = f"{contact['city']}, {contact['state']}"
            elif contact.get('city'):
                location = contact['city']
            elif contact.get('state'):
                location = contact['state']
            elif contact.get('location'):
                location = contact['location']
            elif contact.get('listing_actual_location'):
                # Extract from format 'Location: City, State'
                location_match = re.match(r'Location:\s*(.*)', contact.get('listing_actual_location', ''))
                if location_match:
                    location = location_match.group(1)
            
            # Update LinkedIn log
            self.linkedin_log["contact"] = {
                "name": contact_name,
                "company": company_name,
                "location": location
            }
            
            # Check if we have enough information to search
            if not contact_name:
                return False, "Contact name is required for LinkedIn search"
            
            # Navigate to LinkedIn
            print(f"Navigating to LinkedIn to connect with {contact_name}")
            self.driver.get('https://www.linkedin.com/')
            time.sleep(3)  # Wait for page to load
            
            # Check if already logged in
            if not self._is_linkedin_logged_in():
                login_success = self._login_to_linkedin()
                if not login_success:
                    return False, "Failed to log in to LinkedIn"
            
            # Search for the contact
            search_result = self._search_for_contact(contact_name, company_name, location)
            if not search_result:
                return False, "No matching LinkedIn profiles found"
            
            # Try to message or connect
            profile_url, profile_name, match_score = search_result
            
            # Navigate to the profile
            print(f"Navigating to LinkedIn profile: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(5)  # Wait for profile to load
            
            # First try to send a message (only works if already connected)
            message_result = self._try_send_message(contact)
            if message_result[0]:
                self.linkedin_log["action_taken"] = "message_sent"
                self.linkedin_log["result"] = message_result[1]
                return message_result
            
            # If messaging fails, try to connect
            connect_result = self._try_connect(contact)
            if connect_result[0]:
                self.linkedin_log["action_taken"] = "connection_sent"
                self.linkedin_log["result"] = connect_result[1]
                return connect_result
            
            # If both fail, return the connect result (which contains the error)
            self.linkedin_log["action_taken"] = "failed"
            self.linkedin_log["result"] = connect_result[1]
            return connect_result
        except Exception as e:
            error_msg = f"Error connecting with contact on LinkedIn: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            self.linkedin_log["action_taken"] = "error"
            self.linkedin_log["result"] = error_msg
            
            return False, error_msg
    
    def _is_linkedin_logged_in(self) -> bool:
        """Check if already logged in to LinkedIn
        
        Returns:
            True if logged in, False otherwise
        """
        try:
            # Check for elements that indicate logged-in state
            logged_in_indicators = [
                "//div[contains(@class, 'nav-settings__member-dropdown-trigger')]",
                "//img[contains(@class, 'global-nav__me-photo')]",
                "//li[contains(@class, 'global-nav__primary-item--profile')]"
            ]
            
            for indicator in logged_in_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, indicator)
                    if elements and len(elements) > 0 and elements[0].is_displayed():
                        print("Already logged in to LinkedIn")
                        self.linkedin_logged_in = True
                        return True
                except:
                    continue
            
            print("Not logged in to LinkedIn")
            self.linkedin_logged_in = False
            return False
        except Exception as e:
            print(f"Error checking LinkedIn login status: {e}")
            return False
    
    def _login_to_linkedin(self) -> bool:
        """Log in to LinkedIn
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get LinkedIn credentials from settings
            linkedin_email = self.settings.get('linkedin_email')
            linkedin_password = self.settings.get('linkedin_password')
            
            if not linkedin_email or not linkedin_password:
                print("LinkedIn credentials not provided in settings")
                return False
            
            # Check if we're on the login page, if not navigate to it
            if "login" not in self.driver.current_url.lower():
                self.driver.get('https://www.linkedin.com/login')
                time.sleep(3)  # Wait for page to load
            
            # Find login form elements
            username_input = self.driver.find_element(By.ID, 'username')
            password_input = self.driver.find_element(By.ID, 'password')
            
            # Clear and fill the inputs
            username_input.clear()
            username_input.send_keys(linkedin_email)
            
            password_input.clear()
            password_input.send_keys(linkedin_password)
            
            # Submit the form
            password_input.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if self._is_linkedin_logged_in():
                print("Successfully logged in to LinkedIn")
                return True
            else:
                print("Failed to log in to LinkedIn")
                return False
        except Exception as e:
            print(f"Error logging in to LinkedIn: {e}")
            traceback.print_exc()
            return False
    
    def _search_for_contact(self, name: str, company: str = "", location: str = "") -> Optional[Tuple[str, str, float]]:
        """Search for a contact on LinkedIn with intelligent matching
        
        Args:
            name: Contact name
            company: Company name
            location: Location
            
        Returns:
            Tuple of (profile_url, profile_name, match_score) or None if no match found
        """
        try:
            # Build search query
            search_query = name
            if company:
                search_query += f" {company}"
            
            self.linkedin_log["search_query"] = search_query
            
            # Navigate to search page
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote_plus(search_query)}"
            print(f"Searching LinkedIn for: {search_query}")
            self.driver.get(search_url)
            time.sleep(5)  # Wait for search results to load
            
            # Find search results
            search_results = self.driver.find_elements(By.CSS_SELECTOR, ".reusable-search__result-container")
            
            if not search_results:
                print("No search results found")
                return None
            
            print(f"Found {len(search_results)} search results")
            
            # Process each result to find the best match
            best_match = None
            best_match_score = 0
            best_match_name = ""
            
            profiles_found = []
            
            for result in search_results:
                try:
                    # Extract profile information
                    profile_link = result.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                    profile_url = profile_link.get_attribute("href").split("?")[0]  # Remove query parameters
                    
                    # Extract name
                    name_element = result.find_element(By.CSS_SELECTOR, ".entity-result__title-text a span span")
                    profile_name = name_element.text.strip()
                    
                    # Extract subtitle (usually position and company)
                    subtitle_element = result.find_element(By.CSS_SELECTOR, ".entity-result__primary-subtitle")
                    profile_subtitle = subtitle_element.text.strip()
                    
                    # Extract location
                    location_element = result.find_element(By.CSS_SELECTOR, ".entity-result__secondary-subtitle")
                    profile_location = location_element.text.strip()
                    
                    # Calculate match score
                    match_score = self._calculate_match_score(name, company, location, profile_name, profile_subtitle, profile_location)
                    
                    # Add to profiles found
                    profiles_found.append({
                        "name": profile_name,
                        "subtitle": profile_subtitle,
                        "location": profile_location,
                        "url": profile_url,
                        "match_score": match_score
                    })
                    
                    print(f"Profile: {profile_name} | {profile_subtitle} | {profile_location} | Score: {match_score}")
                    
                    # Update best match if this is better
                    if match_score > best_match_score:
                        best_match = profile_url
                        best_match_score = match_score
                        best_match_name = profile_name
                except Exception as e:
                    print(f"Error processing search result: {e}")
                    continue
            
            # Update LinkedIn log
            self.linkedin_log["profiles_found"] = profiles_found
            
            # Check if we found a good match
            if best_match and best_match_score >= 70:  # Threshold for a good match
                print(f"Best match: {best_match_name} with score {best_match_score}")
                
                self.linkedin_log["best_match"] = best_match
                self.linkedin_log["best_match_score"] = best_match_score
                
                return best_match, best_match_name, best_match_score
            else:
                print(f"No good match found. Best score was {best_match_score}")
                return None
        except Exception as e:
            print(f"Error searching for contact on LinkedIn: {e}")
            traceback.print_exc()
            return None
    
    def _calculate_match_score(self, search_name: str, search_company: str, search_location: str, 
                              profile_name: str, profile_subtitle: str, profile_location: str) -> float:
        """Calculate match score between search criteria and profile
        
        Args:
            search_name: Name from search
            search_company: Company from search
            search_location: Location from search
            profile_name: Name from profile
            profile_subtitle: Subtitle from profile (usually position and company)
            profile_location: Location from profile
            
        Returns:
            Match score (0-100)
        """
        # Initialize weights and scores
        name_weight = 0.6
        company_weight = 0.3
        location_weight = 0.1
        
        name_score = 0
        company_score = 0
        location_score = 0
        
        # Calculate name score
        if FUZZY_MATCHING_AVAILABLE:
            # Use fuzzy matching for better name comparison
            name_score = fuzz.token_sort_ratio(search_name.lower(), profile_name.lower())
        else:
            # Simple matching if fuzzy matching not available
            search_name_lower = search_name.lower()
            profile_name_lower = profile_name.lower()
            
            # Check if all search name tokens are in profile name
            search_tokens = search_name_lower.split()
            profile_tokens = profile_name_lower.split()
            
            matches = 0
            for token in search_tokens:
                if token in profile_tokens or any(token in p_token for p_token in profile_tokens):
                    matches += 1
            
            name_score = (matches / len(search_tokens)) * 100 if search_tokens else 0
        
        # Calculate company score
        if search_company:
            if FUZZY_MATCHING_AVAILABLE:
                company_score = fuzz.partial_ratio(search_company.lower(), profile_subtitle.lower())
            else:
                if search_company.lower() in profile_subtitle.lower():
                    company_score = 100
                else:
                    # Check for partial matches
                    search_company_tokens = search_company.lower().split()
                    matches = 0
                    for token in search_company_tokens:
                        if token in profile_subtitle.lower():
                            matches += 1
                    
                    company_score = (matches / len(search_company_tokens)) * 100 if search_company_tokens else 0
        else:
            # If no company provided, don't factor it in
            company_weight = 0
            name_weight = 0.7
            location_weight = 0.3
        
        # Calculate location score
        if search_location:
            if FUZZY_MATCHING_AVAILABLE:
                location_score = fuzz.partial_ratio(search_location.lower(), profile_location.lower())
            else:
                if search_location.lower() in profile_location.lower():
                    location_score = 100
                else:
                    # Check for partial matches
                    search_location_tokens = search_location.lower().split()
                    matches = 0
                    for token in search_location_tokens:
                        if token in profile_location.lower():
                            matches += 1
                    
                    location_score = (matches / len(search_location_tokens)) * 100 if search_location_tokens else 0
        else:
            # If no location provided, don't factor it in
            location_weight = 0
            name_weight = 0.7
            company_weight = 0.3
        
        # Normalize weights
        total_weight = name_weight + company_weight + location_weight
        name_weight /= total_weight
        company_weight /= total_weight
        location_weight /= total_weight
        
        # Calculate final score
        final_score = (name_score * name_weight) + (company_score * company_weight) + (location_score * location_weight)
        
        return final_score
    
    def _try_send_message(self, contact: Dict[str, Any]) -> Tuple[bool, str]:
        """Try to send a message to the contact
        
        Args:
            contact: Contact data
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Look for message button
            message_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.message-anywhere-button, button.pv-s-profile-actions--message, button[aria-label*='Message']")
            
            if not message_buttons:
                return False, "Message button not found (not connected or not available)"
            
            # Click the message button
            message_buttons[0].click()
            time.sleep(3)  # Wait for message dialog to open
            
            # Find message input
            message_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                "div.msg-form__contenteditable, div[role='textbox'], div.msg-form__message-texteditor")
            
            if not message_inputs:
                return False, "Message input not found"
            
            # Generate personalized message
            message_text = self._generate_personalized_message(contact)
            
            # Type the message
            message_input = message_inputs[0]
            message_input.click()
            time.sleep(1)
            
            # Clear any existing text
            message_input.clear()
            
            # Send the message in chunks to avoid issues
            for chunk in [message_text[i:i+50] for i in range(0, len(message_text), 50)]:
                message_input.send_keys(chunk)
                time.sleep(0.5)
            
            time.sleep(1)  # Wait after typing
            
            # Find and click send button
            send_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.msg-form__send-button, button[aria-label='Send']")
            
            if not send_buttons:
                return False, "Send button not found"
            
            send_buttons[0].click()
            time.sleep(3)  # Wait for message to send
            
            return True, "Successfully sent LinkedIn message"
        except Exception as e:
            print(f"Error sending LinkedIn message: {e}")
            traceback.print_exc()
            return False, f"Error sending message: {str(e)}"
    
    def _try_connect(self, contact: Dict[str, Any]) -> Tuple[bool, str]:
        """Try to send a connection request
        
        Args:
            contact: Contact data
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Look for connect button
            connect_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button.pv-s-profile-actions--connect, button[aria-label*='Connect']")
            
            if not connect_buttons:
                # Try to find the "More" button and click it to reveal connect option
                more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button.pv-s-profile-actions--overflow, button[aria-label='More']")
                
                if more_buttons:
                    more_buttons[0].click()
                    time.sleep(2)  # Wait for dropdown
                    
                    # Look for connect option in dropdown
                    connect_options = self.driver.find_elements(By.CSS_SELECTOR, 
                        "div[aria-label='Connect']")
                    
                    if connect_options:
                        connect_options[0].click()
                        time.sleep(2)  # Wait for connect dialog
                    else:
                        return False, "Connect option not found in dropdown"
                else:
                    return False, "Connect button not found (may already be connected or pending)"
            else:
                # Click the connect button
                connect_buttons[0].click()
                time.sleep(2)  # Wait for connect dialog
            
            # Look for "Add a note" button
            add_note_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[aria-label='Add a note']")
            
            if add_note_buttons:
                add_note_buttons[0].click()
                time.sleep(2)  # Wait for note dialog
                
                # Find note input
                note_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                    "textarea#custom-message, textarea[name='message']")
                
                if note_inputs:
                    # Generate personalized connection note
                    note_text = self._generate_personalized_connection_note(contact)
                    
                    # Type the note
                    note_input = note_inputs[0]
                    note_input.clear()
                    note_input.send_keys(note_text)
                    time.sleep(1)  # Wait after typing
            
            # Find and click send/connect button
            send_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[aria-label='Send now'], button[aria-label='Send invitation']")
            
            if not send_buttons:
                return False, "Send invitation button not found"
            
            send_buttons[0].click()
            time.sleep(3)  # Wait for invitation to send
            
            return True, "Successfully sent LinkedIn connection request"
        except Exception as e:
            print(f"Error sending LinkedIn connection request: {e}")
            traceback.print_exc()
            return False, f"Error sending connection request: {str(e)}"
    
    def _generate_personalized_message(self, contact: Dict[str, Any]) -> str:
        """Generate a personalized message for the contact
        
        Args:
            contact: Contact data
            
        Returns:
            Personalized message text
        """
        # Get message template from settings
        message_template = self.settings.get('linkedin_message_template', 
            "Hi {first_name}, I recently visited your website and wanted to connect. "
            "I'd love to learn more about your business and see if there might be ways we could collaborate. "
            "Looking forward to connecting!")
        
        # Extract contact information
        contact_name = contact.get('name', '')
        first_name = contact.get('first_name', '')
        
        if not first_name and contact_name and ' ' in contact_name:
            first_name = contact_name.split()[0]
        elif not first_name:
            first_name = contact_name
        
        # Replace template variables
        message = message_template.replace('{first_name}', first_name)
        message = message.replace('{name}', contact_name)
        
        for key, value in contact.items():
            if isinstance(value, str):
                message = message.replace(f'{{{key}}}', value)
        
        return message
    
    def _generate_personalized_connection_note(self, contact: Dict[str, Any]) -> str:
        """Generate a personalized connection note
        
        Args:
            contact: Contact data
            
        Returns:
            Personalized connection note text
        """
        # Get connection note template from settings
        note_template = self.settings.get('linkedin_connection_note', 
            "Hi {first_name}, I came across your profile and would like to connect. "
            "Looking forward to networking with you!")
        
        # Extract contact information
        contact_name = contact.get('name', '')
        first_name = contact.get('first_name', '')
        
        if not first_name and contact_name and ' ' in contact_name:
            first_name = contact_name.split()[0]
        elif not first_name:
            first_name = contact_name
        
        # Replace template variables
        note = note_template.replace('{first_name}', first_name)
        note = note.replace('{name}', contact_name)
        
        for key, value in contact.items():
            if isinstance(value, str):
                note = note.replace(f'{{{key}}}', value)
        
        # LinkedIn has a character limit for connection notes
        max_length = 300
        if len(note) > max_length:
            note = note[:max_length-3] + "..."
        
        return note
