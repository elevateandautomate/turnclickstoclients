#!/usr/bin/env python3
"""
Script to test tracking functionality and split test distribution.
This script simulates user journeys and verifies tracking in Supabase.
"""

import os
import sys
import time
import random
import requests
import argparse
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64'

# Base URL for the website (update with your actual domain when deployed)
BASE_URL = 'http://localhost'  # Change to your actual domain when deployed

# Available niches for testing
NICHES = [
    'cosmetic-dentistry',
    'child-care',
    'pmu-artists',
    'weight-loss-clinics',
    'high-end-chiropractors',
    'sleep-apnea',
    'hearing-aid-audiology',
    'dme-clinics',
    'non-surgical-body-contouring'
]

# Buckets for testing
BUCKETS = ['foundation', 'growth', 'scaling', 'clients', 'patients', 'practice', 'operations', 'enrollment', 'future', 'studio', 'referrals']

# Variants for testing
VARIANTS = ['a-solution', 'b-problem', 'c-most-aware']

def initialize_supabase() -> Client:
    """Initialize Supabase client."""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Successfully connected to Supabase")
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

def test_page_access(url, description):
    """Test accessing a page and print the result."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ Successfully accessed {description}: {url}")
            return True
        else:
            print(f"❌ Failed to access {description}: {url} (Status code: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error accessing {description}: {url} - {e}")
        return False

def verify_tracking_events(supabase, event_type, expected_count=1):
    """Verify tracking events in Supabase."""
    try:
        # Query the last minute of events
        one_minute_ago = time.time() - 60
        iso_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(one_minute_ago))
        
        response = supabase.table('tctc_user_flow') \
            .select('*') \
            .filter('action_type', 'eq', event_type) \
            .filter('timestamp', 'gt', iso_time) \
            .execute()
        
        events = response.data
        
        if len(events) >= expected_count:
            print(f"✅ Found {len(events)} '{event_type}' events in Supabase")
            return True
        else:
            print(f"❌ Expected at least {expected_count} '{event_type}' events, but found {len(events)}")
            return False
    except Exception as e:
        print(f"❌ Error verifying tracking events: {e}")
        return False

def test_split_distribution(niche, bucket, variant, iterations=10):
    """Test the distribution of split test variations."""
    print(f"\n🔍 Testing split test distribution for {niche}/{bucket}/{variant}")
    
    splits = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for i in range(iterations):
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
        try:
            response = requests.get(url, allow_redirects=False)
            if response.status_code == 302:
                # Extract split from Location header
                location = response.headers.get('Location', '')
                if 'split=' in location:
                    split = location.split('split=')[1].split('&')[0]
                    splits[int(split)] += 1
                else:
                    splits[0] += 1
            else:
                # If no redirect, assume it's the main page (split=0)
                splits[0] += 1
        except Exception as e:
            print(f"❌ Error in iteration {i+1}: {e}")
    
    print(f"📊 Split test distribution after {iterations} iterations:")
    for split, count in splits.items():
        if split > 0:  # Only show actual split variations
            percentage = (count / iterations) * 100
            print(f"  - Split {split}: {count} ({percentage:.1f}%)")
    
    # Check if distribution is roughly even (within 20% of expected)
    expected = iterations / 3  # Should be evenly distributed among 3 splits
    is_balanced = all(abs(count - expected) <= (expected * 0.2) for split, count in splits.items() if split > 0)
    
    if is_balanced:
        print("✅ Split test distribution is balanced")
    else:
        print("⚠️ Split test distribution appears unbalanced")

def test_user_journey(niche=None):
    """Test a complete user journey with tracking verification."""
    if niche is None:
        niche = random.choice(NICHES)
    
    # Find valid bucket for this niche
    valid_buckets = []
    for bucket in BUCKETS:
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}"
        try:
            response = requests.head(url)
            if response.status_code != 404:
                valid_buckets.append(bucket)
        except:
            pass
    
    if not valid_buckets:
        print(f"❌ No valid buckets found for niche: {niche}")
        return False
    
    bucket = random.choice(valid_buckets)
    variant = random.choice(VARIANTS)
    
    print(f"\n🧪 Testing user journey for {niche}/{bucket}/{variant}")
    
    # 1. Access quiz page
    quiz_url = f"{BASE_URL}/niches/{niche}-quiz.html?source=test&track_source=testing"
    if not test_page_access(quiz_url, "quiz page"):
        return False
    
    # 2. Access results page
    results_url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html?firstName=Test&lastName=User&businessName=TestBusiness&score=75"
    if not test_page_access(results_url, "results page"):
        return False
    
    # 3. Access application page
    application_url = f"{BASE_URL}/universal-application-form.html?niche={niche}&bucket={bucket}&variant={variant}&split=0&source_page={bucket}-variant-{variant}"
    if not test_page_access(application_url, "application page"):
        return False
    
    print("✅ Successfully completed user journey test")
    return True

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Test tracking and split testing functionality')
    parser.add_argument('--niche', choices=NICHES, help='Specific niche to test')
    parser.add_argument('--verify-tracking', action='store_true', help='Verify tracking events in Supabase')
    parser.add_argument('--test-splits', action='store_true', help='Test split test distribution')
    parser.add_argument('--iterations', type=int, default=10, help='Number of iterations for split testing')
    args = parser.parse_args()
    
    print("🚀 Starting tracking and split testing verification")
    
    # Initialize Supabase if needed
    supabase = None
    if args.verify_tracking:
        supabase = initialize_supabase()
    
    # Test user journey
    if args.niche:
        test_user_journey(args.niche)
    else:
        # Test a random niche
        test_user_journey()
    
    # Test split distribution if requested
    if args.test_splits:
        niche = args.niche or random.choice(NICHES)
        # Find valid bucket for this niche
        valid_buckets = []
        for bucket in BUCKETS:
            url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}"
            try:
                response = requests.head(url)
                if response.status_code != 404:
                    valid_buckets.append(bucket)
            except:
                pass
        
        if valid_buckets:
            bucket = valid_buckets[0]
            variant = 'a-solution'  # Use solution variant for testing
            test_split_distribution(niche, bucket, variant, args.iterations)
    
    # Verify tracking events if requested
    if args.verify_tracking and supabase:
        print("\n🔍 Verifying tracking events in Supabase")
        verify_tracking_events(supabase, 'page_view')
        verify_tracking_events(supabase, 'application_click')
    
    print("\n✅ Testing completed")

if __name__ == "__main__":
    main()
