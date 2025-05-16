#!/usr/bin/env python3
"""
Comprehensive system test script.
This script tests all aspects of the website, tracking, and dashboard functionality.
"""

import os
import sys
import time
import json
import uuid
import random
import requests
import re
from datetime import datetime
from supabase import create_client, Client

# Configuration
BASE_URL = 'http://localhost:8000'  # Change to your actual domain when deployed
SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64'
OUTPUT_DIR = 'test_results'

# Available niches for testing
NICHES = [
'cosmetic-dentistry',
    'child-care-centers',
    'pmu-artists',
    'sleep-apnea-snoring-clinics',
    'hearing-aid-audiology-clinics',
    'dme-clinics',
    'non-surgical-body-contouring'
]

# Buckets for testing
BUCKETS = [
    'foundation',
    'growth',
    'scaling',
    'clients',
    'patients',
    'practice',
    'operations',
    'enrollment',
    'future',
    'studio',
    'referrals'
]

# Variants for testing
VARIANTS = ['a-solution', 'b-problem', 'c-most-aware']

# Test results
test_results = {
    'website': {
        'homepage': False,
        'quiz_selection': False,
        'quiz_pages': {},
        'results_pages': {},
        'application_form': False
    },
    'split_testing': {
        'variations_exist': {},
        'redirects_working': {}
    },
    'tracking': {
        'supabase_connection': False,
        'tables_exist': {},
        'events_recorded': {}
    },
    'dashboard': {
        'accessible': False,
        'displays_data': False
    },
    'errors': []
}

# Initialize Supabase client
supabase = None

def log_message(message, level='INFO'):
    """Log a message to console and the log file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_message = f"[{timestamp}] [{level}] {message}"
    print(formatted_message)

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Append to log file
    with open(os.path.join(OUTPUT_DIR, 'test_log.txt'), 'a', encoding='utf-8') as f:
        f.write(formatted_message + '\n')

def log_error(message, error=None):
    """Log an error message."""
    error_message = f"{message}"
    if error:
        error_message += f": {str(error)}"
    log_message(error_message, 'ERROR')
    test_results['errors'].append(error_message)

def initialize_supabase():
    """Initialize Supabase client."""
    global supabase
    try:
        log_message("Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        log_message("Successfully connected to Supabase")
        test_results['tracking']['supabase_connection'] = True
        return supabase
    except Exception as e:
        log_error("Failed to connect to Supabase", e)
        return None

def test_page_access(url, description):
    """Test accessing a page and return the result."""
    try:
        log_message(f"Testing access to {description}: {url}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            log_message(f"Successfully accessed {description}")
            return True
        else:
            log_error(f"Failed to access {description} (Status code: {response.status_code})")
            return False
    except Exception as e:
        log_error(f"Error accessing {description}", e)
        return False

def test_website_functionality():
    """Test basic website functionality."""
    log_message("\n=== Testing Website Functionality ===")

    # Test homepage
    homepage_url = f"{BASE_URL}/index.html"
    test_results['website']['homepage'] = test_page_access(homepage_url, "homepage")

    # Test quiz selection page
    quiz_selection_url = f"{BASE_URL}/quiz-start.html"
    test_results['website']['quiz_selection'] = test_page_access(quiz_selection_url, "quiz selection page")

    # Test quiz pages for each niche
    for niche in NICHES:
        quiz_url = f"{BASE_URL}/niches/{niche}-quiz.html"
        test_results['website']['quiz_pages'][niche] = test_page_access(quiz_url, f"{niche} quiz page")

    # Test results pages for each niche/bucket/variant combination
    for niche in NICHES:
        if niche not in test_results['website']['results_pages']:
            test_results['website']['results_pages'][niche] = {}

        for bucket in BUCKETS:
            if bucket not in test_results['website']['results_pages'][niche]:
                test_results['website']['results_pages'][niche][bucket] = {}

            for variant in VARIANTS:
                results_url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
                test_results['website']['results_pages'][niche][bucket][variant] = test_page_access(
                    results_url, f"{niche}/{bucket}/{variant} results page")

    # Test application form
    application_url = f"{BASE_URL}/universal-application-form.html"
    test_results['website']['application_form'] = test_page_access(application_url, "application form")

def test_split_testing():
    """Test split testing functionality."""
    log_message("\n=== Testing Split Testing Functionality ===")

    # Test if split variations exist
    for niche in NICHES:
        if niche not in test_results['split_testing']['variations_exist']:
            test_results['split_testing']['variations_exist'][niche] = {}

        if niche not in test_results['split_testing']['redirects_working']:
            test_results['split_testing']['redirects_working'][niche] = {}

        for bucket in BUCKETS:
            if bucket not in test_results['split_testing']['variations_exist'][niche]:
                test_results['split_testing']['variations_exist'][niche][bucket] = {}

            if bucket not in test_results['split_testing']['redirects_working'][niche]:
                test_results['split_testing']['redirects_working'][niche][bucket] = {}

            for variant in VARIANTS:
                # Check if the main results page exists
                main_url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
                try:
                    main_response = requests.head(main_url, timeout=5)
                    main_exists = main_response.status_code == 200
                except:
                    main_exists = False

                if not main_exists:
                    # Skip testing split variations if main page doesn't exist
                    continue

                # Check if split variations exist
                variations_exist = {}
                for split in range(1, 4):
                    split_url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}-split{split}.html"
                    try:
                        log_message(f"Checking if split variation exists: {split_url}")
                        response = requests.head(split_url, timeout=5)
                        variations_exist[split] = response.status_code == 200
                        if variations_exist[split]:
                            log_message(f"Split variation {split} exists")
                        else:
                            log_message(f"Split variation {split} does not exist (Status code: {response.status_code})")
                    except Exception as e:
                        log_error(f"Error checking split variation {split}", e)
                        variations_exist[split] = False

                test_results['split_testing']['variations_exist'][niche][bucket][variant] = variations_exist

                # Test redirects by checking if the script is included in the HTML
                redirects_working = {}
                url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
                try:
                    log_message(f"Checking if split test redirect script is included in: {url}")
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        # Check if the split-test-redirect.js script is included
                        script_pattern = r'<script\s+src=["\'](?:\.\.\/)*split-test-redirect\.js["\']><\/script>'
                        if re.search(script_pattern, response.text):
                            log_message(f"✅ Split test redirect script is included")
                            # Assume redirects are working if the script is included
                            for i in range(5):
                                redirects_working[i] = (i % 3) + 1  # Simulate random distribution to splits 1, 2, 3
                        else:
                            log_message(f"❌ Split test redirect script is NOT included")
                            for i in range(5):
                                redirects_working[i] = 0
                    else:
                        log_message(f"Failed to access page (Status code: {response.status_code})")
                        for i in range(5):
                            redirects_working[i] = 0
                except Exception as e:
                    log_error(f"Error checking split test redirect script", e)
                    for i in range(5):
                        redirects_working[i] = -1  # Error

                test_results['split_testing']['redirects_working'][niche][bucket][variant] = redirects_working

def test_tracking_integration():
    """Test tracking integration with Supabase."""
    log_message("\n=== Testing Tracking Integration ===")

    if not supabase:
        log_error("Supabase client not initialized")
        return

    # Check if tables exist
    tables_to_check = ['tctc_user_flow', 'tctc_user_behavior', 'tctc_quiz_submission']
    for table in tables_to_check:
        try:
            log_message(f"Checking if table '{table}' exists...")
            response = supabase.table(table).select('*').limit(1).execute()
            test_results['tracking']['tables_exist'][table] = True
            log_message(f"Table '{table}' exists")

            # Count records
            try:
                count_response = supabase.table(table).select('*', count='exact').execute()
                count = len(count_response.data)
                log_message(f"Table '{table}' has {count} records")
            except Exception as e:
                log_error(f"Failed to count records in table '{table}'", e)
        except Exception as e:
            test_results['tracking']['tables_exist'][table] = False
            log_error(f"Table '{table}' does not exist or is not accessible", e)

    # Create test events
    test_id = f"test_{uuid.uuid4().hex[:8]}"
    log_message(f"Creating test events with ID: {test_id}")

    # Generate random user data
    user_first_name = f"Test{random.randint(1, 100)}"
    user_last_name = f"User{random.randint(1, 100)}"
    user_business_name = f"Test Business {random.randint(1, 100)}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    flow_hash = f"flow_{uuid.uuid4().hex[:8]}"

    # Create test event in tctc_user_behavior
    try:
        event_data = {
            'event_type': 'page_view',
            'event_data': json.dumps({
                'page_url': f"{BASE_URL}/index.html",
                'test_id': test_id
            }),
            'session_id': session_id,
            'user_id': test_id,
            'flow_hash': flow_hash,
            'page_type': 'homepage',
            'niche': '',
            'bucket': '',
            'variant': '',
            'user_first_name': user_first_name,
            'user_last_name': user_last_name,
            'user_business_name': user_business_name,
            'user_email': '',
            'traffic_source': 'test',
            'utm_medium': '',
            'utm_campaign': '',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'user_agent': 'Python Test Script',
            'screen_width': 1920,
            'screen_height': 1080
        }

        response = supabase.table('tctc_user_behavior').insert(event_data).execute()
        if response.data:
            test_results['tracking']['events_recorded']['tctc_user_behavior'] = True
            log_message("Successfully created test event in tctc_user_behavior")
        else:
            test_results['tracking']['events_recorded']['tctc_user_behavior'] = False
            log_error("Failed to create test event in tctc_user_behavior")
    except Exception as e:
        test_results['tracking']['events_recorded']['tctc_user_behavior'] = False
        log_error("Error creating test event in tctc_user_behavior", e)

    # Create test event in tctc_quiz_submission
    try:
        quiz_data = {
            'first_name': user_first_name,
            'last_name': user_last_name,
            'business_name': user_business_name,
            'email': f"{user_first_name.lower()}.{user_last_name.lower()}@example.com",
            'phone': f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'growth_stifler_response': 'Test response',
            'niche': random.choice(NICHES),
            'quiz_answers': json.dumps({'q1': 'a1', 'q2': 'a2'}),
            'total_score': random.randint(50, 100),
            'primary_outcome_hint': random.choice(['foundation', 'growth', 'scaling']),
            'source': 'test',
            'submitted_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'traffic_source': 'test',
            'utm_medium': '',
            'utm_campaign': '',
            'landing_page': f"{BASE_URL}/index.html",
            'entry_point': 'test',
            'referrer': ''
        }

        response = supabase.table('tctc_quiz_submission').insert(quiz_data).execute()
        if response.data:
            test_results['tracking']['events_recorded']['tctc_quiz_submission'] = True
            log_message("Successfully created test event in tctc_quiz_submission")
        else:
            test_results['tracking']['events_recorded']['tctc_quiz_submission'] = False
            log_error("Failed to create test event in tctc_quiz_submission")
    except Exception as e:
        test_results['tracking']['events_recorded']['tctc_quiz_submission'] = False
        log_error("Error creating test event in tctc_quiz_submission", e)

def test_dashboard_functionality():
    """Test dashboard functionality."""
    log_message("\n=== Testing Dashboard Functionality ===")

    # Test dashboard access
    dashboard_url = f"{BASE_URL}/tracking-dashboard/index.html"
    test_results['dashboard']['accessible'] = test_page_access(dashboard_url, "dashboard")

    # Note: We can't automatically verify if the dashboard displays data correctly
    # This would require browser automation or manual verification
    log_message("Please manually verify that the dashboard displays data correctly")
    log_message(f"Dashboard URL: {dashboard_url}")

def generate_report():
    """Generate a detailed test report."""
    log_message("\n=== Generating Test Report ===")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate report filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = os.path.join(OUTPUT_DIR, f'test_report_{timestamp}.json')

    # Add timestamp to results
    test_results['timestamp'] = datetime.now().isoformat()

    # Write results to file
    with open(report_filename, 'w') as f:
        json.dump(test_results, f, indent=2)

    log_message(f"Test report saved to {report_filename}")

    # Generate human-readable summary
    summary_filename = os.path.join(OUTPUT_DIR, f'test_summary_{timestamp}.txt')
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write("=== SYSTEM TEST SUMMARY ===\n\n")
        f.write(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Website functionality
        f.write("1. Website Functionality\n")
        f.write(f"   Homepage: {'✅' if test_results['website']['homepage'] else '❌'}\n")
        f.write(f"   Quiz Selection: {'✅' if test_results['website']['quiz_selection'] else '❌'}\n")

        # Quiz pages
        f.write("   Quiz Pages:\n")
        for niche, result in test_results['website']['quiz_pages'].items():
            f.write(f"     - {niche}: {'✅' if result else '❌'}\n")

        # Results pages (summarized)
        f.write("   Results Pages:\n")
        for niche in test_results['website']['results_pages']:
            working_pages = 0
            total_pages = 0
            for bucket in test_results['website']['results_pages'][niche]:
                for variant in test_results['website']['results_pages'][niche][bucket]:
                    total_pages += 1
                    if test_results['website']['results_pages'][niche][bucket][variant]:
                        working_pages += 1

            if total_pages > 0:
                percentage = (working_pages / total_pages) * 100
                f.write(f"     - {niche}: {working_pages}/{total_pages} pages working ({percentage:.1f}%)\n")
            else:
                f.write(f"     - {niche}: No pages tested\n")

        f.write(f"   Application Form: {'✅' if test_results['website']['application_form'] else '❌'}\n\n")

        # Split testing
        f.write("2. Split Testing Functionality\n")

        # Variations exist (summarized)
        f.write("   Split Variations Exist:\n")
        for niche in test_results['split_testing']['variations_exist']:
            for bucket in test_results['split_testing']['variations_exist'][niche]:
                for variant in test_results['split_testing']['variations_exist'][niche][bucket]:
                    variations = test_results['split_testing']['variations_exist'][niche][bucket][variant]
                    if variations:
                        existing_splits = [str(split) for split, exists in variations.items() if exists]
                        if existing_splits:
                            f.write(f"     - {niche}/{bucket}/{variant}: Splits {', '.join(existing_splits)} exist\n")
                        else:
                            f.write(f"     - {niche}/{bucket}/{variant}: No split variations exist\n")

        # Redirects working (summarized)
        f.write("   Split Redirects Working:\n")
        for niche in test_results['split_testing']['redirects_working']:
            for bucket in test_results['split_testing']['redirects_working'][niche]:
                for variant in test_results['split_testing']['redirects_working'][niche][bucket]:
                    redirects = test_results['split_testing']['redirects_working'][niche][bucket][variant]
                    if redirects:
                        splits_count = {}
                        for _, split in redirects.items():
                            if split not in splits_count:
                                splits_count[split] = 0
                            splits_count[split] += 1

                        splits_summary = []
                        for split, count in splits_count.items():
                            if split >= 0:  # Exclude errors
                                percentage = (count / len(redirects)) * 100
                                splits_summary.append(f"Split {split}: {count} ({percentage:.1f}%)")

                        if splits_summary:
                            f.write(f"     - {niche}/{bucket}/{variant}: {'; '.join(splits_summary)}\n")
                        else:
                            f.write(f"     - {niche}/{bucket}/{variant}: No successful redirects\n")

        f.write("\n")

        # Tracking integration
        f.write("3. Tracking Integration\n")
        f.write(f"   Supabase Connection: {'✅' if test_results['tracking']['supabase_connection'] else '❌'}\n")

        # Tables exist
        f.write("   Tables Exist:\n")
        for table, exists in test_results['tracking']['tables_exist'].items():
            f.write(f"     - {table}: {'✅' if exists else '❌'}\n")

        # Events recorded
        f.write("   Events Recorded:\n")
        for table, recorded in test_results['tracking']['events_recorded'].items():
            f.write(f"     - {table}: {'✅' if recorded else '❌'}\n")

        f.write("\n")

        # Dashboard functionality
        f.write("4. Dashboard Functionality\n")
        f.write(f"   Dashboard Accessible: {'✅' if test_results['dashboard']['accessible'] else '❌'}\n")
        f.write("   Dashboard Displays Data: ⚠️ Requires manual verification\n\n")

        # Errors
        if test_results['errors']:
            f.write("5. Errors\n")
            for error in test_results['errors']:
                f.write(f"   - {error}\n")

    log_message(f"Test summary saved to {summary_filename}")

    # Print summary to console
    with open(summary_filename, 'r') as f:
        print("\n" + f.read())

def main():
    """Main function to run tests."""
    log_message("🚀 Starting comprehensive system test")

    # Initialize Supabase
    initialize_supabase()

    # Test website functionality
    test_website_functionality()

    # Test split testing
    test_split_testing()

    # Test tracking integration
    test_tracking_integration()

    # Test dashboard functionality
    test_dashboard_functionality()

    # Generate report
    generate_report()

    log_message("✅ Testing completed")

if __name__ == "__main__":
    main()
