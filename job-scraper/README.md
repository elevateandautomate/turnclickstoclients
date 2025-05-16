# Job Scraper and Auto-Applicator

A Python-based tool for scraping job listings from multiple job boards and automatically applying to them in bulk.

## Features

- Scrape job listings from LinkedIn and Indeed
- Save job listings to a local SQLite database
- Apply to jobs automatically or semi-automatically
- Filter jobs by keywords, location, experience level, etc.
- Export job listings and applications to CSV

## Prerequisites

- Python 3.7+
- Chrome browser (for Selenium-based scrapers)
- Resume and cover letter in PDF format

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd job-scraper
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup command to create the initial configuration files:
```bash
python src/main.py setup
```

4. Edit the `.env` file to add your credentials and file paths:
```
USER_EMAIL=your_email@example.com
USER_PASSWORD=your_password
RESUME_PATH=/path/to/your/resume.pdf
COVER_LETTER_PATH=/path/to/your/coverletter.pdf
```

## Usage

### Scraping Jobs

Scrape jobs from all supported job boards:
```bash
python src/main.py scrape --all --save --export
```

Scrape jobs with specific search terms and locations:
```bash
python src/main.py scrape --linkedin --search-terms "python developer" "software engineer" --locations "remote" "new york" --save
```

Scrape with visible browser for debugging:
```bash
python src/main.py scrape --all --visible --save
```

### Applying to Jobs

Apply to all new jobs in the database:
```bash
python src/main.py apply --export
```

Apply to jobs with specific keywords:
```bash
python src/main.py apply --keywords python django --limit 10
```

Apply to jobs excluding certain keywords:
```bash
python src/main.py apply --exclude "senior" "lead" "manager" --limit 5
```

### Viewing and Filtering Jobs

View a summary of all jobs in the database:
```bash
python src/main.py view
```

View detailed information about specific jobs:
```bash
python src/main.py view --keywords python --output detail
```

View jobs with specific filters and export them:
```bash
python src/main.py view --status new --job-board linkedin --keywords python react --export
```

## Command Options

### Scrape Command

```
python src/main.py scrape [options]
```

Options:
- `--linkedin`: Scrape LinkedIn jobs
- `--indeed`: Scrape Indeed jobs
- `--all`: Scrape all supported job boards
- `--search-terms [terms]`: Job titles or keywords to search for
- `--locations [locations]`: Locations to search in
- `--experience-levels [levels]`: Experience levels to filter by (entry, mid, senior)
- `--login`: Log in to job boards (required for applying)
- `--visible`: Show browser windows (for debugging)
- `--save`: Save scraped jobs to database
- `--export`: Export jobs to CSV

### Apply Command

```
python src/main.py apply [options]
```

Options:
- `--keywords [keywords]`: Only apply to jobs with these keywords
- `--exclude [keywords]`: Exclude jobs with these keywords
- `--limit [number]`: Maximum number of jobs to apply to
- `--visible`: Show browser windows (for debugging)
- `--export`: Export applications to CSV

### View Command

```
python src/main.py view [options]
```

Options:
- `--status [status]`: Filter by job status (new, applied, rejected, interviewing, offer, all)
- `--job-board [board]`: Filter by job board (linkedin, indeed, all)
- `--keywords [keywords]`: Filter jobs by keywords
- `--exclude [keywords]`: Exclude jobs with these keywords
- `--output [format]`: Output format (count, summary, detail)
- `--export`: Export filtered jobs to CSV
- `--export-path [path]`: Path for exported CSV file

## Customizing Scrapers

The scraper modules can be customized to support additional job boards or modify the behavior of existing scrapers. See the documentation in the `src/scrapers` directory for more information.

## Data Storage

Job data is stored in a SQLite database located at `data/jobs.db`. The database schema includes tables for jobs and applications, allowing you to track your job search progress.

## Logs

Logs are stored in the `logs` directory. Check these logs for debugging information or to troubleshoot issues with the scrapers or application process.

## Disclaimer

This tool is for educational purposes only. Use it responsibly and in accordance with the terms of service of the job boards you are scraping. The authors are not responsible for any violations of terms of service or any consequences resulting from the use of this tool. 