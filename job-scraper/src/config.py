import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Job search parameters
DEFAULT_SEARCH_TERMS = ["Marketing Director", "Chief Marketing Officer", "VP of Marketing", 
                        "Marketing Executive", "Head of Marketing", "Senior Marketing Manager", 
                        "Marketing Leader", "Brand Director", "Digital Marketing Director", 
                        "Marketing Strategy", "Executive Marketing"]
DEFAULT_LOCATIONS = ["remote", "florida", "new york", "washington dc", "atlanta", "virginia", "texas"]
DEFAULT_EXPERIENCE_LEVELS = ["mid", "senior"]

# Job board URLs
JOB_BOARDS = {
    "linkedin": "https://www.linkedin.com/jobs/search",
    "indeed": "https://www.indeed.com/jobs",
    "glassdoor": "https://www.glassdoor.com/Job",
    "monster": "https://www.monster.com/jobs/search"
}

# User credentials (stored in .env file)
EMAIL = os.getenv("USER_EMAIL", "")
PASSWORD = os.getenv("USER_PASSWORD", "")

# Resume and cover letter file paths
RESUME_PATH = os.getenv("RESUME_PATH", "../Aaron_Price_Full_Resume.pdf")
COVER_LETTER_PATH = os.getenv("COVER_LETTER_PATH", "../Aaron_Price_Cover_Letter.pdf")

# Database settings for storing job listings and application status
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobs.db")

# Scraping settings
REQUEST_TIMEOUT = 30  # seconds
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Set to True to use headless mode for browser automation
HEADLESS_MODE = True

# Output files
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
JOBS_CSV_PATH = os.path.join(OUTPUT_DIR, "jobs.csv")
APPLICATIONS_CSV_PATH = os.path.join(OUTPUT_DIR, "applications.csv")

# Create data directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True) 