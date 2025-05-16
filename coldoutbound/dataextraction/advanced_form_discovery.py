"""
Advanced form discovery module for finding contact forms on websites
"""

import time
import re
import traceback
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AdvancedFormDiscovery:
    """Advanced form discovery for finding contact forms on websites"""
    
    def __init__(self, driver, settings=None, logger=None):
        """Initialize the advanced form discovery
        
        Args:
            driver: Selenium WebDriver instance
            settings: Dictionary of settings
            logger: Logger instance
        """
        self.driver = driver
        self.settings = settings or {}
        self.logger = logger
        self.discovery_log = {
            "website": "",
            "contact_pages_found": [],
            "forms_found": [],
            "navigation_steps": [],
            "form_found": False,
            "form_location": "",
            "timestamp": ""
        }
    
    def find_contact_form(self, max_depth: int = 2) -> Optional:
        """Find a contact form on the current website with advanced discovery
        
        Args:
            max_depth: Maximum navigation depth
            
        Returns:
            Form element or None if not found
        """
        self.discovery_log["website"] = self.driver.current_url
        self.discovery_log["navigation_steps"] = []
        
        # First, try to find a form on the current page
        print("Looking for contact form on current page...")
        form = self._find_form_on_current_page()
        if form:
            self.discovery_log["form_found"] = True
            self.discovery_log["form_location"] = self.driver.current_url
            self.discovery_log["forms_found"].append({
                "url": self.driver.current_url,
                "location": "current_page"
            })
            return form
        
        # If no form found, try to find contact pages
        print("No form found on current page, looking for contact page links...")
        contact_links = self._find_contact_page_links()
        
        # Try each contact link
        original_url = self.driver.current_url
        for link in contact_links:
            try:
                link_url = link["url"]
                link_text = link["text"]
                
                print(f"Navigating to potential contact page: {link_url} ({link_text})")
                self.discovery_log["navigation_steps"].append(f"Navigating to {link_url} ({link_text})")
                self.discovery_log["contact_pages_found"].append(link)
                
                # Navigate to the contact page
                self.driver.get(link_url)
                time.sleep(3)  # Wait for page to load
                
                # Try to find a form on this page
                form = self._find_form_on_current_page()
                if form:
                    self.discovery_log["form_found"] = True
                    self.discovery_log["form_location"] = self.driver.current_url
                    self.discovery_log["forms_found"].append({
                        "url": self.driver.current_url,
                        "location": "contact_page"
                    })
                    return form
            except Exception as e:
                print(f"Error navigating to contact page: {e}")
                traceback.print_exc()
                # Continue with next link
        
        # If still no form found, try multi-step discovery
        if max_depth > 1:
            print("No form found on contact pages, trying multi-step discovery...")
            form = self._multi_step_form_discovery()
            if form:
                return form
        
        # If still no form found, try common contact page paths
        print("Trying common contact page paths...")
        form = self._try_common_contact_paths()
        if form:
            return form
        
        # If still no form found, check for forms in iframes
        print("Checking for forms in iframes...")
        form = self._check_forms_in_iframes()
        if form:
            return form
        
        # If still no form found, try to find and click contact buttons
        print("Looking for contact buttons or popups...")
        form = self._find_and_click_contact_buttons()
        if form:
            return form
        
        # Return to original URL if no form found
        try:
            self.driver.get(original_url)
            time.sleep(2)
        except:
            pass
        
        print("No contact form found after exhaustive search")
        return None
    
    def _find_form_on_current_page(self) -> Optional:
        """Find a contact form on the current page
        
        Returns:
            Form element or None if not found
        """
        # Try different form selectors
        form_selectors = [
            "form[action*='contact']",
            "form[id*='contact']",
            "form[class*='contact']",
            "form[name*='contact']",
            ".contact-form",
            "#contact-form",
            "form:not([action*='search']):not([action*='login']):not([action*='register'])",
            "form"
        ]
        
        for selector in form_selectors:
            try:
                forms = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for form in forms:
                    # Check if this looks like a contact form
                    if self._is_likely_contact_form(form):
                        print(f"Found potential contact form with selector: {selector}")
                        return form
            except:
                continue
        
        # Try to find forms with contact-related fields
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            for form in forms:
                if self._is_likely_contact_form(form):
                    print("Found potential contact form by analyzing fields")
                    return form
        except:
            pass
        
        return None
    
    def _is_likely_contact_form(self, form_element) -> bool:
        """Check if a form is likely to be a contact form
        
        Args:
            form_element: Form element to check
            
        Returns:
            True if the form is likely a contact form, False otherwise
        """
        try:
            # Check form attributes
            form_id = (form_element.get_attribute('id') or '').lower()
            form_class = (form_element.get_attribute('class') or '').lower()
            form_action = (form_element.get_attribute('action') or '').lower()
            
            # Check if form attributes contain contact-related terms
            if any(term in form_id for term in ['contact', 'inquiry', 'message', 'feedback']):
                return True
            
            if any(term in form_class for term in ['contact', 'inquiry', 'message', 'feedback']):
                return True
            
            if any(term in form_action for term in ['contact', 'inquiry', 'message', 'feedback']):
                return True
            
            # Check for contact-related fields
            input_elements = form_element.find_elements(By.TAG_NAME, 'input')
            textarea_elements = form_element.find_elements(By.TAG_NAME, 'textarea')
            
            # Count contact-related fields
            contact_field_count = 0
            
            # Check input elements
            for input_el in input_elements:
                input_type = input_el.get_attribute('type')
                input_id = (input_el.get_attribute('id') or '').lower()
                input_name = (input_el.get_attribute('name') or '').lower()
                input_placeholder = (input_el.get_attribute('placeholder') or '').lower()
                
                # Skip hidden and submit fields
                if input_type in ['hidden', 'submit', 'button', 'image']:
                    continue
                
                # Check for email fields
                if input_type == 'email' or 'email' in input_id or 'email' in input_name or 'email' in input_placeholder:
                    contact_field_count += 1
                
                # Check for name fields
                if 'name' in input_id or 'name' in input_name or 'name' in input_placeholder:
                    contact_field_count += 1
                
                # Check for phone fields
                if input_type == 'tel' or 'phone' in input_id or 'phone' in input_name or 'phone' in input_placeholder:
                    contact_field_count += 1
            
            # Check textarea elements (likely message fields)
            if textarea_elements and len(textarea_elements) > 0:
                contact_field_count += 1
            
            # If we found at least 2 contact-related fields, it's likely a contact form
            if contact_field_count >= 2:
                return True
            
            # Check for submit button with contact-related text
            submit_buttons = form_element.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit'], button")
            for button in submit_buttons:
                button_text = button.text.lower()
                button_value = (button.get_attribute('value') or '').lower()
                
                if any(term in button_text or term in button_value for term in ['contact', 'send', 'submit', 'message']):
                    contact_field_count += 1
            
            return contact_field_count >= 2
        except:
            return False
    
    def _find_contact_page_links(self) -> List[Dict[str, str]]:
        """Find links to contact pages
        
        Returns:
            List of dictionaries with contact page URLs and text
        """
        contact_links = []
        
        # Get the base URL
        base_url = self.driver.current_url
        
        # Find all links
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        
        for link in links:
            try:
                link_text = link.text.strip().lower()
                link_href = link.get_attribute('href')
                
                # Skip empty or javascript links
                if not link_href or link_href.startswith('javascript:') or link_href == '#':
                    continue
                
                # Check if link text contains contact-related terms
                if any(term in link_text for term in ['contact', 'get in touch', 'reach us', 'talk to us']):
                    # Make sure the URL is absolute
                    absolute_url = urljoin(base_url, link_href)
                    
                    # Add to contact links if not already added
                    if absolute_url not in [l['url'] for l in contact_links]:
                        contact_links.append({
                            'url': absolute_url,
                            'text': link.text.strip()
                        })
            except:
                continue
        
        return contact_links
    
    def _multi_step_form_discovery(self) -> Optional:
        """Try multi-step discovery to find contact forms
        
        Returns:
            Form element or None if not found
        """
        # Store original URL
        original_url = self.driver.current_url
        
        try:
            # First, look for navigation menus
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 'nav, .nav, .menu, .navigation, header, .header')
            
            for nav in nav_elements:
                try:
                    # Find links in navigation
                    links = nav.find_elements(By.TAG_NAME, 'a')
                    
                    for link in links:
                        link_text = link.text.strip().lower()
                        
                        # Check for about/services pages that might have contact info
                        if any(term in link_text for term in ['about', 'services', 'company', 'who we are']):
                            try:
                                # Get link URL
                                link_href = link.get_attribute('href')
                                if not link_href or link_href.startswith('javascript:') or link_href == '#':
                                    continue
                                
                                # Navigate to the page
                                print(f"Exploring {link_text} page for contact information...")
                                self.discovery_log["navigation_steps"].append(f"Exploring {link_text} page")
                                
                                self.driver.get(link_href)
                                time.sleep(3)  # Wait for page to load
                                
                                # Look for contact forms or links on this page
                                form = self._find_form_on_current_page()
                                if form:
                                    self.discovery_log["form_found"] = True
                                    self.discovery_log["form_location"] = self.driver.current_url
                                    self.discovery_log["forms_found"].append({
                                        "url": self.driver.current_url,
                                        "location": f"multi_step_{link_text}"
                                    })
                                    return form
                                
                                # Look for contact links on this page
                                contact_links = self._find_contact_page_links()
                                if contact_links:
                                    for contact_link in contact_links:
                                        try:
                                            print(f"Following contact link from {link_text} page: {contact_link['text']}")
                                            self.discovery_log["navigation_steps"].append(f"Following contact link from {link_text} page: {contact_link['text']}")
                                            
                                            self.driver.get(contact_link['url'])
                                            time.sleep(3)  # Wait for page to load
                                            
                                            form = self._find_form_on_current_page()
                                            if form:
                                                self.discovery_log["form_found"] = True
                                                self.discovery_log["form_location"] = self.driver.current_url
                                                self.discovery_log["forms_found"].append({
                                                    "url": self.driver.current_url,
                                                    "location": f"multi_step_{link_text}_contact"
                                                })
                                                return form
                                        except:
                                            continue
                            except:
                                continue
                except:
                    continue
        except Exception as e:
            print(f"Error in multi-step discovery: {e}")
            traceback.print_exc()
        
        # Return to original URL if no form found
        try:
            self.driver.get(original_url)
            time.sleep(2)
        except:
            pass
        
        return None
    
    def _try_common_contact_paths(self) -> Optional:
        """Try common contact page paths
        
        Returns:
            Form element or None if not found
        """
        # Store original URL
        original_url = self.driver.current_url
        
        # Parse the base URL
        parsed_url = urlparse(original_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Common contact page paths
        contact_paths = [
            '/contact',
            '/contact-us',
            '/get-in-touch',
            '/reach-us',
            '/connect',
            '/about/contact',
            '/about-us/contact',
            '/support',
            '/help',
            '/inquiry',
            '/contactus',
            '/contact.html',
            '/contact.php',
            '/contactus.html',
            '/contactus.php'
        ]
        
        for path in contact_paths:
            try:
                contact_url = base_url + path
                print(f"Trying common contact path: {contact_url}")
                self.discovery_log["navigation_steps"].append(f"Trying common contact path: {path}")
                
                self.driver.get(contact_url)
                time.sleep(3)  # Wait for page to load
                
                # Check if page loaded successfully (not 404)
                if "404" in self.driver.title or "not found" in self.driver.title.lower():
                    print(f"Path {path} returned 404, skipping")
                    continue
                
                # Try to find a form on this page
                form = self._find_form_on_current_page()
                if form:
                    self.discovery_log["form_found"] = True
                    self.discovery_log["form_location"] = self.driver.current_url
                    self.discovery_log["forms_found"].append({
                        "url": self.driver.current_url,
                        "location": f"common_path_{path}"
                    })
                    return form
            except Exception as e:
                print(f"Error trying contact path {path}: {e}")
                # Continue with next path
        
        # Return to original URL if no form found
        try:
            self.driver.get(original_url)
            time.sleep(2)
        except:
            pass
        
        return None
    
    def _check_forms_in_iframes(self) -> Optional:
        """Check for forms in iframes
        
        Returns:
            Form element or None if not found
        """
        try:
            # Find all iframes
            iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
            
            # Store current window handle
            main_window = self.driver.current_window_handle
            
            for i, iframe in enumerate(iframes):
                try:
                    print(f"Checking iframe {i+1} of {len(iframes)}")
                    self.discovery_log["navigation_steps"].append(f"Checking iframe {i+1}")
                    
                    # Switch to iframe
                    self.driver.switch_to.frame(iframe)
                    
                    # Try to find a form in this iframe
                    form = self._find_form_on_current_page()
                    if form:
                        self.discovery_log["form_found"] = True
                        self.discovery_log["form_location"] = f"iframe_{i+1}"
                        self.discovery_log["forms_found"].append({
                            "url": self.driver.current_url,
                            "location": f"iframe_{i+1}"
                        })
                        return form
                    
                    # Switch back to main content
                    self.driver.switch_to.default_content()
                except:
                    # Switch back to main content in case of error
                    self.driver.switch_to.default_content()
                    continue
            
            # Make sure we're back in the main content
            self.driver.switch_to.default_content()
        except Exception as e:
            print(f"Error checking iframes: {e}")
            traceback.print_exc()
            
            # Make sure we're back in the main content
            try:
                self.driver.switch_to.default_content()
            except:
                pass
        
        return None
    
    def _find_and_click_contact_buttons(self) -> Optional:
        """Find and click buttons that might reveal contact forms
        
        Returns:
            Form element or None if not found
        """
        try:
            # Find elements that might be contact buttons
            contact_buttons = self.driver.find_elements(By.XPATH, 
                "//a[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]|" +
                "//button[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]|" +
                "//div[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]|" +
                "//span[contains(translate(text(), 'CONTACT', 'contact'), 'contact')]|" +
                "//a[contains(@class, 'contact')]|" +
                "//button[contains(@class, 'contact')]|" +
                "//div[contains(@class, 'contact')]|" +
                "//a[contains(@id, 'contact')]|" +
                "//button[contains(@id, 'contact')]|" +
                "//div[contains(@id, 'contact')]"
            )
            
            for i, button in enumerate(contact_buttons):
                try:
                    # Skip if not visible
                    if not button.is_displayed():
                        continue
                    
                    button_text = button.text.strip()
                    print(f"Clicking potential contact button: {button_text}")
                    self.discovery_log["navigation_steps"].append(f"Clicking contact button: {button_text}")
                    
                    # Scroll to the button
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                    time.sleep(1)  # Wait for scroll
                    
                    # Click the button
                    button.click()
                    time.sleep(3)  # Wait for any animations or popups
                    
                    # Check if a form appeared
                    form = self._find_form_on_current_page()
                    if form:
                        self.discovery_log["form_found"] = True
                        self.discovery_log["form_location"] = f"after_button_click_{i+1}"
                        self.discovery_log["forms_found"].append({
                            "url": self.driver.current_url,
                            "location": f"after_button_click_{button_text}"
                        })
                        return form
                except:
                    continue
        except Exception as e:
            print(f"Error finding and clicking contact buttons: {e}")
            traceback.print_exc()
        
        return None
