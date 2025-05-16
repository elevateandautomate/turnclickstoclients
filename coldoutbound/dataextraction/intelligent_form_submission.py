"""
Intelligent form submission module with adaptive retry strategies
"""

import time
import re
import traceback
from typing import Dict, List, Any, Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException

class IntelligentFormSubmission:
    """Intelligent form submission with adaptive retry strategies"""
    
    def __init__(self, driver, field_classifier, settings=None, logger=None):
        """Initialize the intelligent form submission
        
        Args:
            driver: Selenium WebDriver instance
            field_classifier: Form field classifier instance
            settings: Dictionary of settings
            logger: Logger instance
        """
        self.driver = driver
        self.field_classifier = field_classifier
        self.settings = settings or {}
        self.logger = logger
        self.submission_log = {
            "website": "",
            "form_data": {},
            "fields_filled": [],
            "form_submitted": False,
            "submission_result": "",
            "timestamp": "",
            "retry_attempts": 0,
            "error_messages": []
        }
    
    def fill_form_with_retries(self, form_element, contact_data: Dict[str, Any], max_attempts: int = 3) -> Tuple[bool, str]:
        """Fill a form with intelligent retry logic
        
        Args:
            form_element: Form element to fill
            contact_data: Contact data to use for filling
            max_attempts: Maximum number of retry attempts
            
        Returns:
            Tuple of (success, message)
        """
        self.submission_log["website"] = self.driver.current_url
        self.submission_log["form_data"] = contact_data
        self.submission_log["retry_attempts"] = 0
        
        # First attempt - standard approach
        success, message = self._standard_form_fill(form_element, contact_data)
        if success:
            self.submission_log["form_submitted"] = True
            self.submission_log["submission_result"] = message
            return success, message
        
        self.submission_log["retry_attempts"] += 1
        self.submission_log["error_messages"].append(message)
        
        # If first attempt failed, analyze the page for error messages
        error_messages = self._extract_form_error_messages()
        if error_messages:
            print(f"Found form error messages: {error_messages}")
            self.submission_log["error_messages"].extend(error_messages)
        
        # Second attempt - analyze failure and adapt
        if self.submission_log["retry_attempts"] < max_attempts:
            print(f"Retry attempt {self.submission_log['retry_attempts']} of {max_attempts}")
            
            # Modify contact data based on error messages
            modified_contact = self._adapt_contact_data(contact_data, error_messages)
            
            # Try with modified data
            success, message = self._standard_form_fill(form_element, modified_contact)
            if success:
                self.submission_log["form_submitted"] = True
                self.submission_log["submission_result"] = f"Success on retry {self.submission_log['retry_attempts']}: {message}"
                return success, self.submission_log["submission_result"]
            
            self.submission_log["retry_attempts"] += 1
            self.submission_log["error_messages"].append(message)
        
        # Third attempt - try alternative form filling strategy
        if self.submission_log["retry_attempts"] < max_attempts:
            print(f"Retry attempt {self.submission_log['retry_attempts']} of {max_attempts} using JavaScript injection")
            
            # Try JavaScript injection approach
            success, message = self._fill_form_with_javascript(form_element, contact_data)
            if success:
                self.submission_log["form_submitted"] = True
                self.submission_log["submission_result"] = f"Success with JavaScript injection on retry {self.submission_log['retry_attempts']}: {message}"
                return success, self.submission_log["submission_result"]
            
            self.submission_log["retry_attempts"] += 1
            self.submission_log["error_messages"].append(message)
        
        # All attempts failed
        self.submission_log["form_submitted"] = False
        self.submission_log["submission_result"] = f"Failed after {max_attempts} attempts: {'; '.join(self.submission_log['error_messages'])}"
        return False, self.submission_log["submission_result"]
    
    def _standard_form_fill(self, form_element, contact_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Standard form filling approach
        
        Args:
            form_element: Form element to fill
            contact_data: Contact data to use for filling
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Extract form fields
            form_fields = self._extract_form_fields(form_element)
            
            # Fill each field
            filled_fields = []
            for field in form_fields:
                field_type = self._identify_field_type(field)
                if self._fill_field_by_type(field, field_type, contact_data):
                    filled_fields.append(f"{field_type}: {field.get_attribute('name') or field.get_attribute('id')}")
            
            self.submission_log["fields_filled"] = filled_fields
            
            # Submit the form if enabled in settings
            if self.settings.get('submit_form', True):
                submit_button = self._find_submit_button(form_element)
                if submit_button:
                    # Scroll to the submit button
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                    time.sleep(1)  # Wait for scroll
                    
                    # Click the submit button
                    submit_button.click()
                    
                    # Wait for form submission to complete
                    time.sleep(3)
                    
                    return True, "Form submitted successfully"
                else:
                    return False, "Submit button not found"
            else:
                return True, "Form filled successfully but not submitted (submit_form setting is disabled)"
        except Exception as e:
            print(f"Error in standard form fill: {e}")
            traceback.print_exc()
            return False, f"Error filling form: {str(e)}"
    
    def _extract_form_error_messages(self) -> List[str]:
        """Extract error messages from the form
        
        Returns:
            List of error messages
        """
        error_messages = []
        
        # Common error message selectors
        error_selectors = [
            ".error", ".form-error", ".alert-danger", ".validation-error",
            "[role='alert']", ".invalid-feedback", ".help-block",
            ".error-message", ".form-error-message", ".form-message-error"
        ]
        
        # Try each selector
        for selector in error_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.text.strip():
                        error_messages.append(element.text.strip())
            except:
                continue
        
        # Look for elements with error-related classes
        try:
            elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'invalid')]")
            for element in elements:
                if element.is_displayed() and element.text.strip() and element.text.strip() not in error_messages:
                    error_messages.append(element.text.strip())
        except:
            pass
        
        return error_messages
    
    def _adapt_contact_data(self, contact_data: Dict[str, Any], error_messages: List[str]) -> Dict[str, Any]:
        """Adapt contact data based on error messages
        
        Args:
            contact_data: Original contact data
            error_messages: List of error messages
            
        Returns:
            Modified contact data
        """
        modified_data = contact_data.copy()
        
        for error in error_messages:
            error_lower = error.lower()
            
            # Email-related errors
            if any(term in error_lower for term in ['email', 'e-mail', '@']):
                modified_data['email'] = self.settings.get('your_email', 'contact@example.com')
                print(f"Modified email to {modified_data['email']} based on error: {error}")
            
            # Phone-related errors
            elif any(term in error_lower for term in ['phone', 'telephone', 'mobile']):
                modified_data['phone'] = '555-555-5555'
                print(f"Modified phone to {modified_data['phone']} based on error: {error}")
            
            # Name-related errors
            elif any(term in error_lower for term in ['name', 'firstname', 'lastname']):
                if 'first' in error_lower:
                    modified_data['first_name'] = 'John'
                    print(f"Modified first name to {modified_data['first_name']} based on error: {error}")
                elif 'last' in error_lower:
                    modified_data['last_name'] = 'Doe'
                    print(f"Modified last name to {modified_data['last_name']} based on error: {error}")
                else:
                    modified_data['name'] = 'John Doe'
                    print(f"Modified name to {modified_data['name']} based on error: {error}")
            
            # Message-related errors
            elif any(term in error_lower for term in ['message', 'comment', 'inquiry']):
                modified_data['message'] = 'I am interested in learning more about your services. Please contact me at your earliest convenience.'
                print(f"Modified message based on error: {error}")
            
            # Required field errors
            elif any(term in error_lower for term in ['required', 'mandatory', 'fill', 'empty']):
                # Generic handling for required fields
                print(f"Will ensure all fields are filled based on error: {error}")
        
        return modified_data
    
    def _fill_form_with_javascript(self, form_element, contact_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Fill form using JavaScript injection to bypass validation
        
        Args:
            form_element: Form element to fill
            contact_data: Contact data to use for filling
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Get form ID or create a unique identifier
            form_id = form_element.get_attribute('id')
            if not form_id:
                form_id = f"form_{int(time.time())}"
                self.driver.execute_script(f"arguments[0].id = '{form_id}';", form_element)
            
            # Extract form fields
            form_fields = self._extract_form_fields(form_element)
            
            # Prepare JavaScript to fill all fields
            js_fill_script = """
            (function() {
                const form = document.getElementById('%s');
                const fields = form.querySelectorAll('input, textarea, select');
                
                fields.forEach(field => {
                    // Skip hidden and submit fields
                    if (field.type === 'hidden' || field.type === 'submit' || field.type === 'button') {
                        return;
                    }
                    
                    // Fill based on field type
                    if (field.type === 'text' || field.type === 'email' || field.type === 'tel' || field.type === 'textarea') {
                        // Text inputs
                        const name = field.name.toLowerCase();
                        let value = '';
                        
                        if (name.includes('email')) {
                            value = '%s';
                        } else if (name.includes('phone') || name.includes('tel')) {
                            value = '%s';
                        } else if (name.includes('first') && name.includes('name')) {
                            value = '%s';
                        } else if (name.includes('last') && name.includes('name')) {
                            value = '%s';
                        } else if (name.includes('name')) {
                            value = '%s';
                        } else if (name.includes('message') || name.includes('comment')) {
                            value = '%s';
                        } else if (name.includes('company')) {
                            value = '%s';
                        } else {
                            value = 'Test';
                        }
                        
                        field.value = value;
                        
                        // Trigger events
                        field.dispatchEvent(new Event('input', { bubbles: true }));
                        field.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (field.type === 'checkbox') {
                        // Check checkboxes
                        field.checked = true;
                        field.dispatchEvent(new Event('change', { bubbles: true }));
                    } else if (field.type === 'radio') {
                        // Select first radio in each group
                        const name = field.name;
                        const radios = form.querySelectorAll(`input[type="radio"][name="${name}"]`);
                        if (radios.length > 0 && !radios[0].checked) {
                            radios[0].checked = true;
                            radios[0].dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    } else if (field.tagName === 'SELECT') {
                        // Select first non-empty option
                        if (field.options.length > 1) {
                            field.selectedIndex = 1;
                        } else if (field.options.length > 0) {
                            field.selectedIndex = 0;
                        }
                        field.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
                
                return true;
            })();
            """ % (
                form_id,
                contact_data.get('email', 'contact@example.com'),
                contact_data.get('phone', '555-555-5555'),
                contact_data.get('first_name', 'John'),
                contact_data.get('last_name', 'Doe'),
                contact_data.get('name', 'John Doe'),
                contact_data.get('message', 'I am interested in learning more about your services.'),
                contact_data.get('company', 'Company')
            )
            
            # Execute the JavaScript
            result = self.driver.execute_script(js_fill_script)
            
            if result:
                # Find and click submit button
                if self.settings.get('submit_form', True):
                    submit_button = self._find_submit_button(form_element)
                    if submit_button:
                        # Try JavaScript click to bypass any validation
                        self.driver.execute_script("arguments[0].click();", submit_button)
                        time.sleep(3)  # Wait for submission
                        
                        return True, "Form submitted using JavaScript injection"
                    else:
                        # Try to submit the form directly
                        self.driver.execute_script(f"document.getElementById('{form_id}').submit();")
                        time.sleep(3)  # Wait for submission
                        
                        return True, "Form submitted directly using JavaScript"
                else:
                    return True, "Form filled using JavaScript but not submitted (submit_form setting is disabled)"
            else:
                return False, "JavaScript form filling failed"
        except Exception as e:
            print(f"Error in JavaScript form fill: {e}")
            traceback.print_exc()
            return False, f"Error filling form with JavaScript: {str(e)}"
    
    def _extract_form_fields(self, form_element) -> List:
        """Extract all fields from a form
        
        Args:
            form_element: Form element
            
        Returns:
            List of form field elements
        """
        fields = []
        
        # Get all input elements
        input_elements = form_element.find_elements(By.TAG_NAME, 'input')
        for input_el in input_elements:
            input_type = input_el.get_attribute('type')
            if input_type not in ['hidden', 'submit', 'button', 'image']:
                fields.append(input_el)
        
        # Get all textarea elements
        textarea_elements = form_element.find_elements(By.TAG_NAME, 'textarea')
        fields.extend(textarea_elements)
        
        # Get all select elements
        select_elements = form_element.find_elements(By.TAG_NAME, 'select')
        fields.extend(select_elements)
        
        return fields
    
    def _identify_field_type(self, field_element) -> str:
        """Identify the type of a form field
        
        Args:
            field_element: Form field element
            
        Returns:
            Field type string
        """
        # Extract field attributes
        field_data = {
            'id': field_element.get_attribute('id'),
            'name': field_element.get_attribute('name'),
            'class': field_element.get_attribute('class'),
            'type': field_element.get_attribute('type'),
            'placeholder': field_element.get_attribute('placeholder'),
            'aria-label': field_element.get_attribute('aria-label'),
            'tag_name': field_element.tag_name.lower(),
            'form_url': self.driver.current_url
        }
        
        # Try to find associated label
        label_for = None
        if field_data['id']:
            try:
                label_elements = self.driver.find_elements(By.CSS_SELECTOR, f"label[for='{field_data['id']}']")
                if label_elements and len(label_elements) > 0:
                    label_for = label_elements[0].text
            except:
                pass
        
        field_data['label'] = label_for
        
        # Use the field classifier if available
        if self.field_classifier and hasattr(self.field_classifier, 'predict'):
            try:
                prediction = self.field_classifier.predict(field_data)
                return prediction
            except Exception as e:
                print(f"Error using field classifier: {e}")
        
        # Fallback to basic heuristics
        return self._identify_field_type_heuristic(field_data)
    
    def _identify_field_type_heuristic(self, field_data: Dict[str, Any]) -> str:
        """Identify field type using heuristics
        
        Args:
            field_data: Field data dictionary
            
        Returns:
            Field type string
        """
        # Extract field attributes
        field_id = (field_data.get('id') or '').lower()
        field_name = (field_data.get('name') or '').lower()
        field_class = (field_data.get('class') or '').lower()
        field_type = (field_data.get('type') or '').lower()
        field_placeholder = (field_data.get('placeholder') or '').lower()
        field_label = (field_data.get('label') or '').lower()
        field_aria_label = (field_data.get('aria-label') or '').lower()
        field_tag = field_data.get('tag_name', '').lower()
        
        # Check for email fields
        if field_type == 'email' or 'email' in field_id or 'email' in field_name or 'email' in field_placeholder or 'email' in field_label or 'email' in field_aria_label:
            return 'email'
        
        # Check for phone fields
        if field_type == 'tel' or 'phone' in field_id or 'phone' in field_name or 'phone' in field_placeholder or 'phone' in field_label or 'phone' in field_aria_label or 'tel' in field_id or 'tel' in field_name:
            return 'phone'
        
        # Check for name fields
        if 'name' in field_id or 'name' in field_name or 'name' in field_placeholder or 'name' in field_label or 'name' in field_aria_label:
            if 'first' in field_id or 'first' in field_name or 'first' in field_placeholder or 'first' in field_label or 'first' in field_aria_label:
                return 'first_name'
            elif 'last' in field_id or 'last' in field_name or 'last' in field_placeholder or 'last' in field_label or 'last' in field_aria_label:
                return 'last_name'
            else:
                return 'full_name'
        
        # Check for message fields
        if field_tag == 'textarea' or 'message' in field_id or 'message' in field_name or 'message' in field_placeholder or 'message' in field_label or 'message' in field_aria_label or 'comment' in field_id or 'comment' in field_name:
            return 'message'
        
        # Check for company fields
        if 'company' in field_id or 'company' in field_name or 'company' in field_placeholder or 'company' in field_label or 'company' in field_aria_label or 'organization' in field_id or 'organization' in field_name:
            return 'company'
        
        # Check for subject fields
        if 'subject' in field_id or 'subject' in field_name or 'subject' in field_placeholder or 'subject' in field_label or 'subject' in field_aria_label or 'topic' in field_id or 'topic' in field_name:
            return 'subject'
        
        # Check for checkbox fields
        if field_type == 'checkbox':
            return 'checkbox'
        
        # Check for radio fields
        if field_type == 'radio':
            return 'radio'
        
        # Check for dropdown fields
        if field_tag == 'select':
            return 'dropdown'
        
        # Default to unknown
        return 'unknown'
    
    def _fill_field_by_type(self, field, field_type: str, contact_data: Dict[str, Any]) -> bool:
        """Fill a field based on its type
        
        Args:
            field: Field element
            field_type: Field type
            contact_data: Contact data
            
        Returns:
            True if field was filled successfully, False otherwise
        """
        try:
            # Get field values from contact data or settings
            name = contact_data.get('name') or self.settings.get('your_name', 'John Doe')
            first_name = contact_data.get('first_name') or (name.split()[0] if ' ' in name else name)
            last_name = contact_data.get('last_name') or (name.split()[-1] if ' ' in name else '')
            email = contact_data.get('email') or self.settings.get('your_email', 'contact@example.com')
            phone = contact_data.get('phone') or self.settings.get('your_phone', '555-555-5555')
            company = contact_data.get('company') or self.settings.get('your_company', 'Company')
            message = contact_data.get('message') or self.settings.get('contact_form_template', 'I am interested in learning more about your services.')
            
            # Fill based on field type
            if field_type == 'email':
                field.clear()
                field.send_keys(email)
            elif field_type == 'phone':
                field.clear()
                field.send_keys(phone)
            elif field_type == 'first_name':
                field.clear()
                field.send_keys(first_name)
            elif field_type == 'last_name':
                field.clear()
                field.send_keys(last_name)
            elif field_type == 'full_name':
                field.clear()
                field.send_keys(name)
            elif field_type == 'company':
                field.clear()
                field.send_keys(company)
            elif field_type == 'message':
                field.clear()
                field.send_keys(message)
            elif field_type == 'subject':
                field.clear()
                field.send_keys('Inquiry')
            elif field_type == 'checkbox':
                if not field.is_selected():
                    field.click()
            elif field_type == 'radio':
                if not field.is_selected():
                    field.click()
            elif field_type == 'dropdown':
                # Handle dropdown
                try:
                    # Try to select the second option (first is often a placeholder)
                    options = field.find_elements(By.TAG_NAME, 'option')
                    if len(options) > 1:
                        options[1].click()
                    elif len(options) > 0:
                        options[0].click()
                except:
                    # Fallback to JavaScript
                    self.driver.execute_script("""
                        const select = arguments[0];
                        if (select.options.length > 1) {
                            select.selectedIndex = 1;
                            select.dispatchEvent(new Event('change', { bubbles: true }));
                        } else if (select.options.length > 0) {
                            select.selectedIndex = 0;
                            select.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    """, field)
            else:
                # Unknown field type, try generic text
                field.clear()
                field.send_keys('Test')
            
            return True
        except Exception as e:
            print(f"Error filling field by type: {e}")
            return False
    
    def _find_submit_button(self, form_element) -> Optional:
        """Find the submit button for a form
        
        Args:
            form_element: Form element
            
        Returns:
            Submit button element or None if not found
        """
        # Try to find submit button by type
        submit_buttons = form_element.find_elements(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
        if submit_buttons and len(submit_buttons) > 0:
            return submit_buttons[0]
        
        # Try to find button elements with submit-like text
        buttons = form_element.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            button_text = button.text.lower()
            if any(term in button_text for term in ['submit', 'send', 'contact', 'message', 'continue']):
                return button
        
        # Try to find input elements with submit-like value
        inputs = form_element.find_elements(By.TAG_NAME, "input")
        for input_el in inputs:
            input_value = (input_el.get_attribute('value') or '').lower()
            if any(term in input_value for term in ['submit', 'send', 'contact', 'message', 'continue']):
                return input_el
        
        # Try to find any button or input that looks like a submit button
        elements = form_element.find_elements(By.CSS_SELECTOR, "button, input[type='button'], input[type='image'], a.button, .btn, .submit, .submit-button")
        for element in elements:
            element_text = element.text.lower()
            element_class = (element.get_attribute('class') or '').lower()
            
            if any(term in element_text for term in ['submit', 'send', 'contact', 'message', 'continue']):
                return element
            
            if any(term in element_class for term in ['submit', 'send', 'contact', 'btn-primary']):
                return element
        
        # No submit button found
        return None
