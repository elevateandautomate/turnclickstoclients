#!/usr/bin/env python3
import os
import argparse
import logging
import json
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# Import local modules
import config
from db import save_job, save_application, get_jobs, update_job_status, export_jobs_to_csv, export_applications_to_csv
from scrapers import LinkedInScraper, IndeedScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "job_scraper.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("JobScraper")

# Ensure logs directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"), exist_ok=True)

def scrape_jobs(args):
    """Scrape jobs from the specified job boards."""
    scrapers = []
    
    # Initialize scrapers based on arguments
    if args.linkedin or args.all:
        linkedin_scraper = LinkedInScraper(
            email=config.EMAIL if args.login else None,
            password=config.PASSWORD if args.login else None,
            headless=not args.visible
        )
        scrapers.append(linkedin_scraper)
    
    if args.indeed or args.all:
        indeed_scraper = IndeedScraper(headless=not args.visible)
        scrapers.append(indeed_scraper)
    
    # Determine search parameters
    search_terms = args.search_terms if args.search_terms else config.DEFAULT_SEARCH_TERMS
    locations = args.locations if args.locations else config.DEFAULT_LOCATIONS
    experience_levels = args.experience_levels if args.experience_levels else config.DEFAULT_EXPERIENCE_LEVELS
    
    all_jobs = []
    for scraper in scrapers:
        try:
            logger.info(f"Starting scraper for {scraper.job_board_name}")
            
            jobs = scraper.scrape_and_save(
                search_terms=search_terms,
                locations=locations,
                experience_levels=experience_levels,
                save_callback=save_job if args.save else None
            )
            
            all_jobs.extend(jobs)
            logger.info(f"Found {len(jobs)} jobs from {scraper.job_board_name}")
            
        except Exception as e:
            logger.error(f"Error with {scraper.job_board_name} scraper: {e}")
        finally:
            scraper.close()
    
    # Export to CSV if requested
    if args.export:
        export_jobs_to_csv(config.JOBS_CSV_PATH)
        logger.info(f"Exported jobs to {config.JOBS_CSV_PATH}")
    
    logger.info(f"Scraped a total of {len(all_jobs)} jobs")
    return all_jobs

def apply_to_jobs(args):
    """Apply to jobs based on filtering criteria."""
    # Get jobs to apply to
    df = get_jobs(status="new")
    
    if len(df) == 0:
        logger.info("No new jobs to apply to")
        return
    
    # Filter jobs by keywords if specified
    if args.keywords:
        keyword_pattern = '|'.join(args.keywords)
        df = df[df['keywords'].str.contains(keyword_pattern, case=False, na=False)]
    
    # Filter jobs by excludes if specified
    if args.exclude:
        exclude_pattern = '|'.join(args.exclude)
        df = df[~df['title'].str.contains(exclude_pattern, case=False, na=False) & 
                ~df['description'].str.contains(exclude_pattern, case=False, na=False)]
    
    # Limit the number of applications if specified
    if args.limit and args.limit < len(df):
        df = df.head(args.limit)
    
    logger.info(f"Applying to {len(df)} jobs")
    
    # Initialize scrapers based on job board
    linkedin_jobs = df[df['job_board'] == 'linkedin']
    indeed_jobs = df[df['job_board'] == 'indeed']
    
    # Apply to LinkedIn jobs
    if not linkedin_jobs.empty:
        linkedin_scraper = LinkedInScraper(
            email=config.EMAIL,
            password=config.PASSWORD,
            headless=not args.visible
        )
        
        try:
            # Log in first to avoid doing it for each job
            linkedin_scraper._login()
            
            for _, job in tqdm(linkedin_jobs.iterrows(), total=len(linkedin_jobs), desc="Applying to LinkedIn jobs"):
                try:
                    success = linkedin_scraper.apply_to_job(job['url'])
                    if success:
                        save_application(job['id'], "Applied automatically")
                        logger.info(f"Successfully applied to {job['title']} at {job['company']}")
                    else:
                        update_job_status(job['id'], "failed", "Failed to apply automatically")
                        logger.warning(f"Failed to apply to {job['title']} at {job['company']}")
                except Exception as e:
                    logger.error(f"Error applying to LinkedIn job {job['id']}: {e}")
                    update_job_status(job['id'], "error", f"Error: {str(e)}")
        finally:
            linkedin_scraper.close()
    
    # Apply to Indeed jobs
    if not indeed_jobs.empty:
        indeed_scraper = IndeedScraper(headless=not args.visible)
        
        try:
            for _, job in tqdm(indeed_jobs.iterrows(), total=len(indeed_jobs), desc="Applying to Indeed jobs"):
                try:
                    success = indeed_scraper.apply_to_job(job['url'])
                    if success:
                        save_application(job['id'], "Applied automatically")
                        logger.info(f"Successfully applied to {job['title']} at {job['company']}")
                    else:
                        update_job_status(job['id'], "failed", "Failed to apply automatically")
                        logger.warning(f"Failed to apply to {job['title']} at {job['company']}")
                except Exception as e:
                    logger.error(f"Error applying to Indeed job {job['id']}: {e}")
                    update_job_status(job['id'], "error", f"Error: {str(e)}")
        finally:
            indeed_scraper.close()
    
    # Export applications to CSV if requested
    if args.export:
        export_applications_to_csv(config.APPLICATIONS_CSV_PATH)
        logger.info(f"Exported applications to {config.APPLICATIONS_CSV_PATH}")

def view_jobs(args):
    """View and filter jobs."""
    df = get_jobs(status=args.status, job_board=args.job_board)
    
    if len(df) == 0:
        print("No jobs found matching criteria")
        return
    
    # Filter by keywords
    if args.keywords:
        keyword_pattern = '|'.join(args.keywords)
        df = df[df['keywords'].str.contains(keyword_pattern, case=False, na=False) | 
                df['title'].str.contains(keyword_pattern, case=False, na=False) | 
                df['description'].str.contains(keyword_pattern, case=False, na=False)]
    
    # Filter by exclude terms
    if args.exclude:
        exclude_pattern = '|'.join(args.exclude)
        df = df[~df['title'].str.contains(exclude_pattern, case=False, na=False) & 
                ~df['description'].str.contains(exclude_pattern, case=False, na=False)]
    
    # Display results
    if args.output == "count":
        print(f"Found {len(df)} jobs")
    elif args.output == "summary":
        print(f"Found {len(df)} jobs:")
        for _, job in df.iterrows():
            print(f"{job['id']}: {job['title']} at {job['company']} ({job['location']}) - {job['url']}")
    elif args.output == "detail":
        for _, job in df.iterrows():
            print(f"\nID: {job['id']}")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"URL: {job['url']}")
            print(f"Salary: {job['salary']}")
            print(f"Date Posted: {job['date_posted']}")
            print(f"Status: {job['status']}")
            print(f"Keywords: {job['keywords']}")
            print("-" * 50)
    
    # Export to CSV if requested
    if args.export:
        file_path = args.export_path if args.export_path else config.JOBS_CSV_PATH
        df.to_csv(file_path, index=False)
        print(f"Exported {len(df)} jobs to {file_path}")

def create_dotenv():
    """Create a .env file if it doesn't exist."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("""# Job Scraper Configuration
# Enter your credentials and paths below

# User credentials for logging into job boards
USER_EMAIL=your_email@example.com
USER_PASSWORD=your_password

# Paths to resume and cover letter files
RESUME_PATH=path/to/your/resume.pdf
COVER_LETTER_PATH=path/to/your/coverletter.pdf
""")
        logger.info(f"Created .env file at {env_path}")
        print(f"Created .env file at {env_path}. Please edit it to add your credentials.")
    else:
        logger.info(".env file already exists")

def main():
    parser = argparse.ArgumentParser(description="Job Scraper and Auto-Applicator")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up the job scraper")
    
    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape jobs from job boards")
    scrape_parser.add_argument("--linkedin", action="store_true", help="Scrape LinkedIn jobs")
    scrape_parser.add_argument("--indeed", action="store_true", help="Scrape Indeed jobs")
    scrape_parser.add_argument("--all", action="store_true", help="Scrape all supported job boards")
    scrape_parser.add_argument("--search-terms", nargs="+", help="Job titles or keywords to search for")
    scrape_parser.add_argument("--locations", nargs="+", help="Locations to search in")
    scrape_parser.add_argument("--experience-levels", nargs="+", 
                             choices=["entry", "mid", "senior"], 
                             help="Experience levels to filter by")
    scrape_parser.add_argument("--login", action="store_true", help="Log in to job boards")
    scrape_parser.add_argument("--visible", action="store_true", help="Show browser windows")
    scrape_parser.add_argument("--save", action="store_true", help="Save scraped jobs to database")
    scrape_parser.add_argument("--export", action="store_true", help="Export jobs to CSV")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply to jobs")
    apply_parser.add_argument("--keywords", nargs="+", help="Only apply to jobs with these keywords")
    apply_parser.add_argument("--exclude", nargs="+", help="Exclude jobs with these keywords")
    apply_parser.add_argument("--limit", type=int, help="Maximum number of jobs to apply to")
    apply_parser.add_argument("--visible", action="store_true", help="Show browser windows")
    apply_parser.add_argument("--export", action="store_true", help="Export applications to CSV")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View and filter jobs")
    view_parser.add_argument("--status", choices=["new", "applied", "rejected", "interviewing", "offer", "all"], 
                           default="all", help="Filter by job status")
    view_parser.add_argument("--job-board", choices=["linkedin", "indeed", "all"], 
                           default="all", help="Filter by job board")
    view_parser.add_argument("--keywords", nargs="+", help="Filter jobs by keywords")
    view_parser.add_argument("--exclude", nargs="+", help="Exclude jobs with these keywords")
    view_parser.add_argument("--output", choices=["count", "summary", "detail"], 
                           default="summary", help="Output format")
    view_parser.add_argument("--export", action="store_true", help="Export filtered jobs to CSV")
    view_parser.add_argument("--export-path", help="Path for exported CSV file")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        create_dotenv()
    elif args.command == "scrape":
        if not (args.linkedin or args.indeed or args.all):
            args.all = True  # Default to all job boards if none specified
        scrape_jobs(args)
    elif args.command == "apply":
        apply_to_jobs(args)
    elif args.command == "view":
        view_jobs(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 