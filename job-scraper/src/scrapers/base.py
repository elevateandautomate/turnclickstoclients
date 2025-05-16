import logging
import os
import requests
import time
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import random
from datetime import datetime
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../logs/scraper.log"),
        logging.StreamHandler()
    ]
)

# Ensure log directory exists
os.makedirs("../logs", exist_ok=True)

logger = logging.getLogger("JobScraper")

class BaseScraper(ABC):
    """Base class for all job board scrapers."""
    
    def __init__(self, job_board_name, base_url, headers=None):
        self.job_board_name = job_board_name
        self.base_url = base_url
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    @abstractmethod
    def search_jobs(self, search_term, location, experience_level=None, num_results=100):
        """
        Search for jobs with the given parameters
        
        Args:
            search_term (str): Job title or keywords
            location (str): Job location
            experience_level (str, optional): Experience level
            num_results (int, optional): Number of results to fetch
            
        Returns:
            list: List of job data dictionaries
        """
        pass
    
    @abstractmethod
    def extract_job_details(self, job_url):
        """
        Extract detailed information about a job listing
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            dict: Dictionary containing job details
        """
        pass
    
    @abstractmethod
    def apply_to_job(self, job_url):
        """
        Apply to a job
        
        Args:
            job_url (str): URL of the job listing
            
        Returns:
            bool: True if application was successful, False otherwise
        """
        pass
    
    def _make_request(self, url, method="GET", data=None, params=None, retries=3, backoff_factor=0.3):
        """
        Make an HTTP request with retries and backoff
        
        Args:
            url (str): URL to request
            method (str, optional): HTTP method
            data (dict, optional): Form data for POST requests
            params (dict, optional): Query parameters
            retries (int, optional): Number of retries
            backoff_factor (float, optional): Backoff factor for retries
            
        Returns:
            requests.Response: Response object
        """
        for attempt in range(retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(url, params=params, timeout=30)
                else:
                    response = self.session.post(url, data=data, params=params, timeout=30)
                
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed: {e}")
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed after {retries} attempts")
                    raise
    
    def _parse_html(self, html):
        """Parse HTML string into BeautifulSoup object"""
        return BeautifulSoup(html, 'html.parser')
    
    def _random_delay(self, min_seconds=1, max_seconds=5):
        """Add a random delay to avoid detection"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        
    def _normalize_job_data(self, job_data):
        """
        Normalize job data to a standard format
        
        Args:
            job_data (dict): Raw job data
            
        Returns:
            dict: Normalized job data
        """
        # Add job board name and scrape date
        job_data['job_board'] = self.job_board_name
        job_data['date_scraped'] = datetime.now().isoformat()
        
        # Ensure all expected fields are present
        required_fields = [
            'job_id', 'title', 'company', 'location', 'description',
            'url', 'salary', 'date_posted'
        ]
        
        for field in required_fields:
            if field not in job_data:
                job_data[field] = ""
                
        return job_data
        
    def scrape_and_save(self, search_terms, locations, experience_levels=None, save_callback=None):
        """
        Scrape jobs for multiple search terms and locations and save them
        
        Args:
            search_terms (list): List of job titles or keywords
            locations (list): List of job locations
            experience_levels (list, optional): List of experience levels
            save_callback (callable, optional): Function to save job data
            
        Returns:
            list: List of all scraped job data
        """
        if not experience_levels:
            experience_levels = [None]
            
        all_jobs = []
        
        for search_term in search_terms:
            for location in locations:
                for experience_level in experience_levels:
                    logger.info(f"Searching for {search_term} in {location} with experience level {experience_level}")
                    
                    try:
                        jobs = self.search_jobs(search_term, location, experience_level)
                        logger.info(f"Found {len(jobs)} jobs")
                        
                        # Process each job
                        for job in tqdm(jobs, desc=f"Processing {search_term} in {location}"):
                            try:
                                # Get detailed job information
                                detailed_job = self.extract_job_details(job['url'])
                                normalized_job = self._normalize_job_data({**job, **detailed_job})
                                
                                # Save job data if callback provided
                                if save_callback:
                                    save_callback(normalized_job)
                                
                                all_jobs.append(normalized_job)
                                
                                # Add random delay to avoid detection
                                self._random_delay()
                                
                            except Exception as e:
                                logger.error(f"Error processing job {job.get('url', 'unknown')}: {e}")
                                continue
                    
                    except Exception as e:
                        logger.error(f"Error searching for {search_term} in {location}: {e}")
                        continue
        
        return all_jobs 