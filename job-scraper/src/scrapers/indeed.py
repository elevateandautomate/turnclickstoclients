import logging
import re
from urllib.parse import urlencode
import time
import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .base import BaseScraper

logger = logging.getLogger("IndeedScraper")

class IndeedScraper(BaseScraper):
    """Scraper for Indeed jobs."""
    
    def __init__(self, headless=True):
        super().__init__("indeed", "https://www.indeed.com/jobs")
        self.headless = headless
        self.browser = None
        self.page = None
    
    def _initialize_browser(self):
        """Initialize and configure the Playwright browser."""
        if self.browser:
            return
            
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page(
            user_agent=self.headers["User-Agent"],
            viewport={"width": 1920, "height": 1080}
        )
        
        # Set a longer timeout for navigation
        self.page.set_default_timeout(60000)
        
        # Add some additional configurations to make the bot less detectable
        self.page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        """)
    
    def search_jobs(self, search_term, location, experience_level=None, num_results=100):
        """
        Search for jobs on Indeed.
        
        Args:
            search_term (str): Job title or keywords
            location (str): Job location
            experience_level (str, optional): Experience level (entry, mid, senior)
            num_results (int, optional): Maximum number of results to return
            
        Returns:
            list: List of job data dictionaries
        """
        self._initialize_browser()
        
        # Construct search URL
        params = {
            "q": search_term,
            "l": location,
            "sort": "date",  # Sort by date
        }
        
        # Add experience level filter if provided
        if experience_level:
            exp_filter = None
            if experience_level.lower() == "entry":
                exp_filter = "ENTRY_LEVEL"
            elif experience_level.lower() == "mid":
                exp_filter = "MID_LEVEL"
            elif experience_level.lower() == "senior":
                exp_filter = "SENIOR_LEVEL"
                
            if exp_filter:
                params["explvl"] = exp_filter
        
        search_url = f"{self.base_url}?{urlencode(params)}"
        logger.info(f"Searching Indeed jobs: {search_url}")
        
        self.page.goto(search_url)
        time.sleep(3)  # Wait for page to load
        
        # Handle any popups or consent dialogs
        self._dismiss_popups()
        
        jobs = []
        pages_scraped = 0
        max_pages = max(1, (num_results // 15) + 1)  # Each page has ~15 results
        
        while len(jobs) < num_results and pages_scraped < max_pages:
            # Wait for job cards to load
            self.page.wait_for_selector('div[data-testid="job-card"]', timeout=10000)
            
            # Extract job data from current page
            page_content = self.page.content()
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find all job cards
            job_cards = soup.select('div[data-testid="job-card"]')
            
            for card in job_cards:
                if len(jobs) >= num_results:
                    break
                    
                try:
                    # Extract job ID
                    job_id = card.get('id', '').replace('job_', '')
                    
                    # Extract job title
                    title_element = card.select_one('h2.jobTitle span[title]')
                    job_title = title_element.get('title') if title_element else "Unknown Title"
                    
                    # Extract company name
                    company_element = card.select_one('span.companyName')
                    company = company_element.text.strip() if company_element else "Unknown Company"
                    
                    # Extract location
                    location_element = card.select_one('div.companyLocation')
                    job_location = location_element.text.strip() if location_element else ""
                    
                    # Extract URL
                    url_element = card.select_one('a.jcs-JobTitle')
                    job_url = f"https://www.indeed.com{url_element.get('href')}" if url_element else ""
                    
                    # Extract salary if available
                    salary_element = card.select_one('div.salary-snippet')
                    salary = salary_element.text.strip() if salary_element else ""
                    
                    # Extract date posted
                    date_element = card.select_one('span.date')
                    date_posted = date_element.text.strip() if date_element else ""
                    
                    job_data = {
                        "job_id": job_id,
                        "title": job_title,
                        "company": company,
                        "location": job_location,
                        "url": job_url,
                        "date_posted": date_posted,
                        "salary": salary,
                        "description": ""
                    }
                    
                    jobs.append(job_data)
                    
                except Exception as e:
                    logger.error(f"Error extracting job data from card: {e}")
                    continue
            
            # Click the next page button if available
            try:
                next_button = self.page.query_selector('a[data-testid="pagination-page-next"]')
                if next_button:
                    next_button.click()
                    time.sleep(3)  # Wait for next page to load
                    pages_scraped += 1
                    self._dismiss_popups()
                else:
                    break  # No more pages
            except Exception as e:
                logger.error(f"Error navigating to next page: {e}")
                break
                
        logger.info(f"Found {len(jobs)} Indeed jobs for '{search_term}' in '{location}'")
        return jobs[:num_results]
    
    def extract_job_details(self, job_url):
        """
        Extract detailed information about an Indeed job listing.
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            dict: Dictionary containing job details
        """
        self._initialize_browser()
        
        logger.info(f"Extracting job details from {job_url}")
        
        try:
            self.page.goto(job_url)
            time.sleep(2)  # Wait for page to load
            self._dismiss_popups()
            
            # Wait for job description to load
            self.page.wait_for_selector('div#jobDescriptionText', timeout=10000)
            
            # Extract job description
            description_element = self.page.query_selector('div#jobDescriptionText')
            description = description_element.inner_html() if description_element else ""
            
            # Extract additional information
            # Try to extract salary information again (might be more detailed on the job page)
            salary = ""
            salary_element = self.page.query_selector('.jobsearch-JobMetadataHeader-item')
            if salary_element:
                salary_text = salary_element.inner_text()
                if "$" in salary_text or "£" in salary_text or "€" in salary_text:
                    salary = salary_text.strip()
            
            # Extract keywords from job description
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
        Apply to a job on Indeed.
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            bool: True if application was successful, False otherwise
        """
        self._initialize_browser()
        
        try:
            logger.info(f"Applying to job: {job_url}")
            self.page.goto(job_url)
            time.sleep(2)
            self._dismiss_popups()
            
            # Look for the "Apply Now" button
            apply_button = self.page.query_selector('button[id="indeedApplyButton"], a.jobsearch-DesktopStickyContainer-applyButton-newDesign')
            
            if not apply_button:
                logger.warning("Could not find Apply button")
                return False
            
            apply_button.click()
            time.sleep(3)
            
            # Check if we're redirected to an external site
            current_url = self.page.url
            if "indeed.com/jobs" not in current_url and "indeed.com/apply" not in current_url:
                logger.info("Redirected to external application site")
                return False  # External application not supported yet
            
            # Handle Indeed's application form
            # This is simplified and may need to be expanded based on actual form fields
            try:
                # Check if we need to enter resume
                resume_upload = self.page.query_selector('input[type="file"][name="resume"]')
                if resume_upload:
                    # Upload resume
                    logger.info("Resume upload required")
                    return False  # Resume upload not implemented yet
                
                # Fill out form fields
                form_fields = self.page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"], textarea')
                
                for field in form_fields:
                    field_id = field.get_attribute('id') or ''
                    
                    # Fill appropriate values based on field identifiers
                    if "email" in field_id.lower():
                        field.fill("example@example.com")  # Use actual email from config
                    elif "phone" in field_id.lower():
                        field.fill("5555555555")
                    elif "name" in field_id.lower():
                        if "first" in field_id.lower():
                            field.fill("John")  # Use actual name from config
                        elif "last" in field_id.lower():
                            field.fill("Doe")  # Use actual name from config
                
                # Click continue/submit buttons
                continue_button = self.page.query_selector('button[type="submit"]')
                if continue_button:
                    continue_button.click()
                    time.sleep(2)
                
                # Application may involve multiple steps, but this is a simplified version
                logger.info("Applied to job (simplified process)")
                return True
                
            except Exception as e:
                logger.error(f"Error during application process: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False
    
    def _dismiss_popups(self):
        """Dismiss common popups and modals."""
        try:
            # Close cookie consent
            cookie_button = self.page.query_selector('#onetrust-accept-btn-handler')
            if cookie_button:
                cookie_button.click()
                time.sleep(1)
            
            # Close job alerts popup
            close_alert = self.page.query_selector('button[aria-label="close job alert"]')
            if close_alert:
                close_alert.click()
                time.sleep(1)
            
            # Close any modal dialogs
            modal_close = self.page.query_selector('button.icl-Modal-close')
            if modal_close:
                modal_close.click()
                time.sleep(1)
                
        except Exception as e:
            logger.warning(f"Error dismissing popups: {e}")
    
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
        """Close the browser."""
        if self.browser:
            self.browser.close()
            self.browser = None 