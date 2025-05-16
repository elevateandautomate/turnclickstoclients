"""
Enhanced data enrichment module for extracting additional contact information from websites
"""

import re
import time
import json
import traceback
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class EnhancedDataEnrichment:
    """Enhanced data enrichment for extracting additional contact information from websites"""
    
    def __init__(self, driver, supabase_client=None, settings=None, logger=None):
        """Initialize the enhanced data enrichment
        
        Args:
            driver: Selenium WebDriver instance
            supabase_client: Supabase client for storing enriched data
            settings: Dictionary of settings
            logger: Logger instance
        """
        self.driver = driver
        self.supabase = supabase_client
        self.settings = settings or {}
        self.logger = logger
        self.enrichment_log = {
            "website": "",
            "data_extracted": {},
            "extraction_methods": [],
            "timestamp": ""
        }
        
        # Define patterns for data extraction
        self.patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'phone': r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}',
            'address': r'\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Ave|Street|St|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Way|Place|Pl|Terrace|Ter|Circle|Cir|Highway|Hwy|Route|Rt)[,\s]+[A-Za-z\s]+,\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?',
            'business_hours': r'(?:hours|open)[\s\:]+([^<]+)',
            'social_media': {
                'facebook': r'facebook\.com/([^/"\']+)',
                'twitter': r'twitter\.com/([^/"\']+)',
                'linkedin': r'linkedin\.com/(?:company|in)/([^/"\']+)',
                'instagram': r'instagram\.com/([^/"\']+)',
                'youtube': r'youtube\.com/(?:user|channel)/([^/"\']+)',
                'pinterest': r'pinterest\.com/([^/"\']+)',
                'tiktok': r'tiktok\.com/@([^/"\']+)'
            }
        }
    
    def enrich_contact_data(self, contact_id: str) -> Dict[str, Any]:
        """Extract additional contact information from the current website
        
        Args:
            contact_id: Contact ID for updating the database
            
        Returns:
            Dictionary with enriched data
        """
        self.enrichment_log["website"] = self.driver.current_url
        self.enrichment_log["data_extracted"] = {}
        self.enrichment_log["extraction_methods"] = []
        
        enriched_data = {}
        
        # Extract data using different methods
        try:
            # Method 1: Extract from page source
            source_data = self._extract_from_page_source()
            if source_data:
                enriched_data.update(source_data)
                self.enrichment_log["extraction_methods"].append("page_source")
            
            # Method 2: Extract from contact/about pages
            page_data = self._extract_from_contact_pages()
            if page_data:
                enriched_data.update(page_data)
                self.enrichment_log["extraction_methods"].append("contact_pages")
            
            # Method 3: Extract from structured data
            structured_data = self._extract_from_structured_data()
            if structured_data:
                enriched_data.update(structured_data)
                self.enrichment_log["extraction_methods"].append("structured_data")
            
            # Method 4: Extract from footer
            footer_data = self._extract_from_footer()
            if footer_data:
                enriched_data.update(footer_data)
                self.enrichment_log["extraction_methods"].append("footer")
            
            # Method 5: Extract team/staff information
            team_data = self._extract_team_information()
            if team_data:
                enriched_data.update(team_data)
                self.enrichment_log["extraction_methods"].append("team_info")
            
            # Add prefix to all keys
            prefixed_data = {}
            for key, value in enriched_data.items():
                prefixed_data[f"enriched_{key}"] = value
            
            # Update the enrichment log
            self.enrichment_log["data_extracted"] = prefixed_data
            
            # Save enriched data to database if contact_id is provided
            if contact_id and self.supabase:
                self._save_enriched_data_to_database(contact_id, prefixed_data)
            
            return prefixed_data
        except Exception as e:
            print(f"Error enriching contact data: {e}")
            traceback.print_exc()
            return {}
    
    def _extract_from_page_source(self) -> Dict[str, Any]:
        """Extract contact information from the page source
        
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        
        try:
            # Get page source
            page_source = self.driver.page_source
            
            # Extract email addresses
            emails = re.findall(self.patterns['email'], page_source)
            if emails:
                # Filter out common false positives
                filtered_emails = [email for email in emails if not any(domain in email for domain in ['example.com', 'yourdomain.com', 'domain.com'])]
                if filtered_emails:
                    extracted_data['email'] = filtered_emails[0]  # Use the first email found
                    
                    # If there are multiple emails, store them as well
                    if len(filtered_emails) > 1:
                        extracted_data['additional_emails'] = filtered_emails[1:]
            
            # Extract phone numbers
            phones = re.findall(self.patterns['phone'], page_source)
            if phones:
                # Clean up phone numbers
                cleaned_phones = []
                for phone in phones:
                    # Remove non-digit characters for comparison
                    digits_only = re.sub(r'\D', '', phone)
                    if len(digits_only) >= 7 and digits_only not in [re.sub(r'\D', '', p) for p in cleaned_phones]:
                        cleaned_phones.append(phone)
                
                if cleaned_phones:
                    extracted_data['phone'] = cleaned_phones[0]  # Use the first phone found
                    
                    # If there are multiple phones, store them as well
                    if len(cleaned_phones) > 1:
                        extracted_data['additional_phones'] = cleaned_phones[1:]
            
            # Extract address
            addresses = re.findall(self.patterns['address'], page_source)
            if addresses:
                extracted_data['address'] = addresses[0]
            
            # Extract business hours
            hours_match = re.search(self.patterns['business_hours'], page_source, re.IGNORECASE)
            if hours_match:
                extracted_data['business_hours'] = hours_match.group(1).strip()
            
            # Extract social media profiles
            for platform, pattern in self.patterns['social_media'].items():
                matches = re.findall(pattern, page_source)
                if matches:
                    extracted_data[f'social_{platform}'] = matches[0]
        except Exception as e:
            print(f"Error extracting from page source: {e}")
            traceback.print_exc()
        
        return extracted_data
    
    def _extract_from_contact_pages(self) -> Dict[str, Any]:
        """Extract contact information from contact/about pages
        
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        original_url = self.driver.current_url
        
        try:
            # Parse the base URL
            parsed_url = urlparse(original_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Common contact page paths
            contact_paths = [
                '/contact',
                '/contact-us',
                '/about',
                '/about-us'
            ]
            
            for path in contact_paths:
                try:
                    contact_url = base_url + path
                    print(f"Checking {path} page for contact information...")
                    
                    # Navigate to the contact page
                    self.driver.get(contact_url)
                    time.sleep(3)  # Wait for page to load
                    
                    # Check if page loaded successfully (not 404)
                    if "404" in self.driver.title or "not found" in self.driver.title.lower():
                        print(f"Path {path} returned 404, skipping")
                        continue
                    
                    # Extract contact information from this page
                    page_data = self._extract_from_page_source()
                    
                    # Merge with existing data
                    for key, value in page_data.items():
                        if key not in extracted_data:
                            extracted_data[key] = value
                except:
                    continue
        except Exception as e:
            print(f"Error extracting from contact pages: {e}")
            traceback.print_exc()
        
        # Return to original URL
        try:
            self.driver.get(original_url)
            time.sleep(2)
        except:
            pass
        
        return extracted_data
    
    def _extract_from_structured_data(self) -> Dict[str, Any]:
        """Extract contact information from structured data (JSON-LD, microdata)
        
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        
        try:
            # Extract JSON-LD data
            json_ld_scripts = self.driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            
            for script in json_ld_scripts:
                try:
                    script_content = script.get_attribute('innerHTML')
                    json_data = json.loads(script_content)
                    
                    # Handle both single objects and arrays
                    if isinstance(json_data, list):
                        items = json_data
                    else:
                        items = [json_data]
                    
                    for item in items:
                        # Look for Organization or LocalBusiness data
                        if '@type' in item and item['@type'] in ['Organization', 'LocalBusiness', 'Store', 'Restaurant', 'Hotel']:
                            # Extract email
                            if 'email' in item and not extracted_data.get('email'):
                                extracted_data['email'] = item['email']
                            
                            # Extract phone
                            if 'telephone' in item and not extracted_data.get('phone'):
                                extracted_data['phone'] = item['telephone']
                            
                            # Extract address
                            if 'address' in item and not extracted_data.get('address'):
                                address_obj = item['address']
                                if isinstance(address_obj, dict):
                                    address_parts = []
                                    
                                    if 'streetAddress' in address_obj:
                                        address_parts.append(address_obj['streetAddress'])
                                    
                                    if 'addressLocality' in address_obj:
                                        address_parts.append(address_obj['addressLocality'])
                                    
                                    if 'addressRegion' in address_obj:
                                        address_parts.append(address_obj['addressRegion'])
                                    
                                    if 'postalCode' in address_obj:
                                        address_parts.append(address_obj['postalCode'])
                                    
                                    if address_parts:
                                        extracted_data['address'] = ', '.join(address_parts)
                            
                            # Extract business hours
                            if 'openingHours' in item and not extracted_data.get('business_hours'):
                                if isinstance(item['openingHours'], list):
                                    extracted_data['business_hours'] = '; '.join(item['openingHours'])
                                else:
                                    extracted_data['business_hours'] = item['openingHours']
                            
                            # Extract social media
                            if 'sameAs' in item:
                                same_as = item['sameAs']
                                if isinstance(same_as, list):
                                    for url in same_as:
                                        for platform, pattern in self.patterns['social_media'].items():
                                            if platform in url.lower():
                                                matches = re.findall(pattern, url)
                                                if matches and not extracted_data.get(f'social_{platform}'):
                                                    extracted_data[f'social_{platform}'] = matches[0]
                except:
                    continue
        except Exception as e:
            print(f"Error extracting from structured data: {e}")
            traceback.print_exc()
        
        return extracted_data
    
    def _extract_from_footer(self) -> Dict[str, Any]:
        """Extract contact information from the page footer
        
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        
        try:
            # Find footer element
            footer_selectors = ['footer', '.footer', '#footer', '[role="contentinfo"]']
            
            for selector in footer_selectors:
                try:
                    footer_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for footer in footer_elements:
                        # Extract text from footer
                        footer_text = footer.text
                        
                        # Extract email addresses
                        emails = re.findall(self.patterns['email'], footer_text)
                        if emails and not extracted_data.get('email'):
                            # Filter out common false positives
                            filtered_emails = [email for email in emails if not any(domain in email for domain in ['example.com', 'yourdomain.com', 'domain.com'])]
                            if filtered_emails:
                                extracted_data['email'] = filtered_emails[0]
                        
                        # Extract phone numbers
                        phones = re.findall(self.patterns['phone'], footer_text)
                        if phones and not extracted_data.get('phone'):
                            # Clean up phone numbers
                            cleaned_phones = []
                            for phone in phones:
                                # Remove non-digit characters for comparison
                                digits_only = re.sub(r'\D', '', phone)
                                if len(digits_only) >= 7 and digits_only not in [re.sub(r'\D', '', p) for p in cleaned_phones]:
                                    cleaned_phones.append(phone)
                            
                            if cleaned_phones:
                                extracted_data['phone'] = cleaned_phones[0]
                        
                        # Extract address
                        addresses = re.findall(self.patterns['address'], footer_text)
                        if addresses and not extracted_data.get('address'):
                            extracted_data['address'] = addresses[0]
                        
                        # Extract business hours
                        hours_match = re.search(self.patterns['business_hours'], footer_text, re.IGNORECASE)
                        if hours_match and not extracted_data.get('business_hours'):
                            extracted_data['business_hours'] = hours_match.group(1).strip()
                        
                        # Extract social media links
                        social_links = footer.find_elements(By.TAG_NAME, 'a')
                        for link in social_links:
                            href = link.get_attribute('href')
                            if href:
                                for platform, pattern in self.patterns['social_media'].items():
                                    if platform in href.lower() and not extracted_data.get(f'social_{platform}'):
                                        matches = re.findall(pattern, href)
                                        if matches:
                                            extracted_data[f'social_{platform}'] = matches[0]
                except:
                    continue
        except Exception as e:
            print(f"Error extracting from footer: {e}")
            traceback.print_exc()
        
        return extracted_data
    
    def _extract_team_information(self) -> Dict[str, Any]:
        """Extract team/staff information from the website
        
        Returns:
            Dictionary with extracted data
        """
        extracted_data = {}
        
        try:
            # Look for team/staff sections
            team_selectors = [
                '.team', '#team', '.staff', '#staff', '.our-team', '#our-team',
                '.team-members', '#team-members', '.employees', '#employees',
                '.people', '#people', '.about-us', '#about-us', '.about', '#about',
                '[data-section="team"]', '[data-section="staff"]'
            ]
            
            for selector in team_selectors:
                try:
                    team_sections = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for section in team_sections:
                        team_members = []
                        
                        # Look for team member elements
                        member_elements = section.find_elements(By.CSS_SELECTOR, '.member, .team-member, .staff-member, .person, .employee, .profile')
                        
                        if not member_elements:
                            # Try to find team members by looking for name/title patterns
                            member_elements = section.find_elements(By.CSS_SELECTOR, 'div, li, article')
                        
                        for member in member_elements:
                            member_info = {}
                            
                            # Extract name
                            name_elements = member.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6, .name, .title')
                            if name_elements:
                                member_info['name'] = name_elements[0].text.strip()
                            
                            # Extract role/position
                            role_elements = member.find_elements(By.CSS_SELECTOR, '.role, .position, .job-title, .designation, p')
                            if role_elements:
                                for role_el in role_elements:
                                    role_text = role_el.text.strip()
                                    if role_text and role_text != member_info.get('name', ''):
                                        member_info['role'] = role_text
                                        break
                            
                            # Extract contact information
                            member_text = member.text
                            
                            # Extract email
                            emails = re.findall(self.patterns['email'], member_text)
                            if emails:
                                filtered_emails = [email for email in emails if not any(domain in email for domain in ['example.com', 'yourdomain.com', 'domain.com'])]
                                if filtered_emails:
                                    member_info['email'] = filtered_emails[0]
                            
                            # Extract phone
                            phones = re.findall(self.patterns['phone'], member_text)
                            if phones:
                                member_info['phone'] = phones[0]
                            
                            # Add to team members if we have at least a name
                            if 'name' in member_info:
                                team_members.append(member_info)
                        
                        if team_members:
                            # Format team members as a string
                            team_str = []
                            for member in team_members:
                                member_str = member.get('name', '')
                                
                                if 'role' in member:
                                    member_str += f" - {member['role']}"
                                
                                if 'email' in member:
                                    member_str += f" ({member['email']})"
                                
                                if 'phone' in member:
                                    member_str += f" {member['phone']}"
                                
                                team_str.append(member_str)
                            
                            extracted_data['team'] = '; '.join(team_str)
                            break  # Stop after finding one team section
                except:
                    continue
        except Exception as e:
            print(f"Error extracting team information: {e}")
            traceback.print_exc()
        
        return extracted_data
    
    def _save_enriched_data_to_database(self, contact_id: str, enriched_data: Dict[str, Any]) -> bool:
        """Save enriched data to the database
        
        Args:
            contact_id: Contact ID
            enriched_data: Dictionary with enriched data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.supabase:
                print("Supabase client not initialized. Cannot save enriched data.")
                return False
            
            # Get the table name from settings or use default
            table_name = self.settings.get('table_name', 'core_data')
            
            # Update the contact record with enriched data
            self.supabase.table(table_name).update(enriched_data).eq('id', contact_id).execute()
            
            print(f"Saved enriched data to database for contact {contact_id}")
            return True
        except Exception as e:
            print(f"Error saving enriched data to database: {e}")
            traceback.print_exc()
            return False
