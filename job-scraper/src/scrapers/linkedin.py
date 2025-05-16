import logging
import re
from urllib.parse import urlencode
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from .base import BaseScraper

logger = logging.getLogger("LinkedInScraper")

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn jobs."""
    
    def __init__(self, email=None, password=None, headless=True):
        super().__init__("linkedin", "https://www.linkedin.com/jobs/search")
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.logged_in = False
    
    def _initialize_driver(self):
        """Initialize and configure the web driver."""
        if self.driver:
            return
            
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        
        # Add user agent to avoid detection
        options.add_argument(f"user-agent={self.headers['User-Agent']}")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(10)
    
    def _login(self):
        """Log in to LinkedIn if credentials are provided."""
        if not self.email or not self.password or self.logged_in:
            return False
            
        try:
            self._initialize_driver()
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(self.email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(3)
            
            # Check if login was successful
            if "feed" in self.driver.current_url:
                self.logged_in = True
                logger.info("Successfully logged in to LinkedIn")
                return True
            else:
                logger.warning("Failed to log in to LinkedIn")
                return False
                
        except Exception as e:
            logger.error(f"Error logging in to LinkedIn: {e}")
            return False
    
    def search_jobs(self, search_term, location, experience_level=None, num_results=100):
        """
        Search for jobs on LinkedIn.
        
        Args:
            search_term (str): Job title or keywords
            location (str): Job location
            experience_level (str, optional): Experience level (entry, mid, senior)
            num_results (int, optional): Maximum number of results to return
            
        Returns:
            list: List of job data dictionaries
        """
        self._initialize_driver()
        self._login()  # Try to log in if credentials are provided
        
        # Construct search URL
        params = {
            "keywords": search_term,
            "location": location,
            "f_AL": "true",  # Easy Apply filter
            "sortBy": "R",   # Sort by relevance
        }
        
        # Add experience level filter if provided
        if experience_level:
            exp_filter = None
            if experience_level.lower() == "entry":
                exp_filter = "1"  # Internship or Entry level
            elif experience_level.lower() == "mid":
                exp_filter = "2"  # Mid-Senior level
            elif experience_level.lower() == "senior":
                exp_filter = "3"  # Director or Executive
                
            if exp_filter:
                params["f_E"] = exp_filter
        
        search_url = f"{self.base_url}?{urlencode(params)}"
        logger.info(f"Searching LinkedIn jobs: {search_url}")
        
        self.driver.get(search_url)
        time.sleep(3)  # Wait for page to load
        
        jobs = []
        job_cards = []
        last_height = 0
        
        # Scroll and collect job cards until we have enough or can't find more
        while len(job_cards) < num_results:
            # Find all job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            if len(job_cards) >= num_results:
                break
                
            # Scroll down to load more results
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if we've reached the end of results
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Try clicking the "See more jobs" button if it exists
                try:
                    see_more_button = self.driver.find_element(By.CSS_SELECTOR, ".infinite-scroller__show-more-button")
                    see_more_button.click()
                    time.sleep(2)
                except NoSuchElementException:
                    break  # No more results
            
            last_height = new_height
        
        # Process job cards (take up to num_results)
        for card in job_cards[:num_results]:
            try:
                job_id = card.get_attribute("data-id") or ""
                job_title_element = card.find_element(By.CSS_SELECTOR, "h3.base-search-card__title")
                job_title = job_title_element.text.strip()
                
                company_element = card.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle")
                company = company_element.text.strip()
                
                location_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                job_location = location_element.text.strip()
                
                job_link_element = card.find_element(By.CSS_SELECTOR, ".base-card__full-link")
                job_url = job_link_element.get_attribute("href")
                
                # Try to get the date posted
                try:
                    date_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
                    date_posted = date_element.get_attribute("datetime") or ""
                except NoSuchElementException:
                    date_posted = ""
                
                job_data = {
                    "job_id": job_id,
                    "title": job_title,
                    "company": company,
                    "location": job_location,
                    "url": job_url,
                    "date_posted": date_posted,
                    "description": "",
                    "salary": ""
                }
                
                jobs.append(job_data)
                
            except Exception as e:
                logger.error(f"Error extracting job data from card: {e}")
                continue
                
        logger.info(f"Found {len(jobs)} LinkedIn jobs for '{search_term}' in '{location}'")
        return jobs
    
    def extract_job_details(self, job_url):
        """
        Extract detailed information about a LinkedIn job listing.
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            dict: Dictionary containing job details
        """
        self._initialize_driver()
        
        logger.info(f"Extracting job details from {job_url}")
        
        try:
            self.driver.get(job_url)
            time.sleep(2)  # Wait for page to load
            
            # Extract job description
            description_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".show-more-less-html__markup"))
            )
            description = description_element.get_attribute("innerHTML")
            
            # Try to extract salary information
            salary = ""
            try:
                salary_element = self.driver.find_element(By.CSS_SELECTOR, ".compensation__salary")
                salary = salary_element.text.strip()
            except NoSuchElementException:
                # Try alternative selectors for salary
                try:
                    criteria_elements = self.driver.find_elements(By.CSS_SELECTOR, ".description__job-criteria-item")
                    for element in criteria_elements:
                        label = element.find_element(By.CSS_SELECTOR, ".description__job-criteria-subheader").text.strip()
                        if "salary" in label.lower() or "compensation" in label.lower():
                            salary = element.find_element(By.CSS_SELECTOR, ".description__job-criteria-text").text.strip()
                            break
                except NoSuchElementException:
                    pass
            
            # Try to extract keywords from job description
            keywords = self._extract_keywords(description)
            
            return {
                "description": description,
                "salary": salary,
                "keywords": ", ".join(keywords)
            }
            
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return {
                "description": "",
                "salary": "",
                "keywords": ""
            }
    
    def apply_to_job(self, job_url):
        """
        Apply to a job on LinkedIn.
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            bool: True if application was successful, False otherwise
        """
        if not self.logged_in:
            success = self._login()
            if not success:
                logger.error("Must be logged in to apply for jobs")
                return False
        
        self._initialize_driver()
        
        try:
            logger.info(f"Applying to job: {job_url}")
            self.driver.get(job_url)
            time.sleep(2)
            
            # Click the "Easy Apply" button
            try:
                apply_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".jobs-apply-button"))
                )
                apply_button.click()
                
                # Wait for the application form to appear
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-easy-apply-content"))
                )
                
                # Handle application steps
                completed = False
                while not completed:
                    # Check if we're on the final step
                    try:
                        review_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Review your application']")
                        review_button.click()
                        time.sleep(1)
                        
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Submit application']"))
                        )
                        submit_button.click()
                        time.sleep(2)
                        completed = True
                        
                    except NoSuchElementException:
                        # Not on the final step, look for the "Next" button
                        try:
                            next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
                            next_button.click()
                            time.sleep(2)
                        except NoSuchElementException:
                            # If we can't find the next button, try looking for form fields to fill out
                            self._fill_application_form()
                            
                            # After filling, try to find the next button again
                            try:
                                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']")
                                next_button.click()
                                time.sleep(2)
                            except NoSuchElementException:
                                logger.warning("Could not find next button or form fields to fill out")
                                return False
            
                logger.info("Successfully applied to job")
                return True
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"Could not find Easy Apply button: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False
    
    def _fill_application_form(self):
        """Fill out form fields in the application."""
        try:
            # Look for input fields
            input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input.artdeco-text-input--input")
            for field in input_fields:
                field_id = field.get_attribute("id")
                
                # Skip if field already has a value
                if field.get_attribute("value"):
                    continue
                
                # Fill phone number fields
                if "phone" in field_id.lower():
                    field.send_keys("5555555555")  # Placeholder phone number
                
                # Fill in years of experience fields
                if "years" in field_id.lower() and "experience" in field_id.lower():
                    field.send_keys("3")
                
            # Look for select/dropdown elements
            select_elements = self.driver.find_elements(By.CSS_SELECTOR, "select.artdeco-select__input")
            for select in select_elements:
                # Skip if already selected
                if select.get_attribute("value"):
                    continue
                
                # Select the first non-empty option
                options = select.find_elements(By.CSS_SELECTOR, "option")
                for option in options[1:]:  # Skip first option which is usually a placeholder
                    if option.get_attribute("value"):
                        option.click()
                        break
            
            # Look for checkboxes
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            for checkbox in checkboxes:
                # Check any "I agree" or "I authorize" checkboxes
                checkbox_id = checkbox.get_attribute("id") or ""
                label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                label_text = label.text.lower()
                
                if ("agree" in label_text or "authorize" in label_text) and not checkbox.is_selected():
                    checkbox.click()
            
            # Look for radio buttons
            radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            if radio_buttons:
                # Group radio buttons by name
                radio_groups = {}
                for radio in radio_buttons:
                    name = radio.get_attribute("name")
                    if name:
                        if name not in radio_groups:
                            radio_groups[name] = []
                        radio_groups[name].append(radio)
                
                # For each group, select the first button or the "Yes" option if available
                for name, radios in radio_groups.items():
                    selected = False
                    
                    # First try to find a "Yes" option
                    for radio in radios:
                        radio_id = radio.get_attribute("id") or ""
                        try:
                            label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                            label_text = label.text.lower()
                            
                            if label_text == "yes" and not radio.is_selected():
                                radio.click()
                                selected = True
                                break
                        except NoSuchElementException:
                            pass
                    
                    # If no "Yes" option was found, select the first radio button
                    if not selected and radios:
                        if not radios[0].is_selected():
                            radios[0].click()
            
            return True
            
        except Exception as e:
            logger.error(f"Error filling application form: {e}")
            return False
    
    def _extract_keywords(self, description):
        """Extract keywords from job description."""
        # Common tech skills and keywords
        tech_keywords = [
            "python", "java", "javascript", "typescript", "c\\+\\+", "c#", "ruby", "php", "swift",
            "react", "angular", "vue", "node", "express", "django", "flask", "spring", "asp\\.net",
            "html", "css", "sql", "nosql", "mongodb", "mysql", "postgresql", "oracle", "redis",
            "aws", "azure", "gcp", "cloud", "docker", "kubernetes", "ci/cd", "git", "github",
            "rest", "api", "microservices", "agile", "scrum", "jira", "tdd", "devops",
            "machine learning", "ai", "data science", "big data", "hadoop", "spark", "tableau"
        ]
        
        # Create a regex pattern for finding these keywords
        pattern = r'\b(' + '|'.join(tech_keywords) + r')\b'
        
        # Find all matches
        matches = re.findall(pattern, description.lower())
        
        # Return unique keywords
        return list(set(matches))
    
    def close(self):
        """Close the web driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.logged_in = False 