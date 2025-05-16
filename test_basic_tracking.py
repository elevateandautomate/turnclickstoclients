#!/usr/bin/env python3
"""
Basic script to test tracking functionality.
This script verifies that pages are accessible and tracking is working.
"""

import requests
import time
import random

# Base URL for the website (update with your actual domain when deployed)
BASE_URL = 'http://localhost:8000'  # Change to your actual domain when deployed

# Available niches for testing
NICHES = [
    'cosmetic-dentistry',
    'child-care',
    'pmu-artists',
    'sleep-apnea',
    'hearing-aid-audiology',
    'dme-clinics',
    'non-surgical-body-contouring'
]

def test_page_access(url, description):
    """Test accessing a page and print the result."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Successfully accessed {description}: {url}")
            return True
        else:
            print(f"❌ Failed to access {description}: {url} (Status code: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error accessing {description}: {url} - {e}")
        return False

def test_user_journey(niche):
    """Test a complete user journey."""
    print(f"\n🧪 Testing user journey for niche: {niche}")

    # 1. Access homepage
    homepage_url = f"{BASE_URL}/index.html"
    if not test_page_access(homepage_url, "homepage"):
        return False

    # 2. Access quiz page
    quiz_url = f"{BASE_URL}/niches/{niche}-quiz.html"
    if not test_page_access(quiz_url, "quiz page"):
        return False

    # 3. Try to find a valid results page
    # Common buckets to try
    buckets = ['foundation', 'growth', 'scaling', 'patients', 'clients']
    variants = ['a-solution', 'b-problem', 'c-most-aware']

    results_found = False
    for bucket in buckets:
        for variant in variants:
            results_url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
            if test_page_access(results_url, f"results page ({bucket}/{variant})"):
                results_found = True

                # 4. Access application page
                application_url = f"{BASE_URL}/universal-application-form.html?niche={niche}&bucket={bucket}&variant={variant}"
                test_page_access(application_url, "application page")

                # Only need to find one valid results page
                break

        if results_found:
            break

    if not results_found:
        print(f"❌ Could not find a valid results page for niche: {niche}")
        return False

    print(f"✅ Successfully completed user journey test for niche: {niche}")
    return True

def test_split_distribution(niche, bucket, variant, iterations=5):
    """Test the distribution of split test variations."""
    print(f"\n🔍 Testing split test distribution for {niche}/{bucket}/{variant}")

    splits = {0: 0, 1: 0, 2: 0, 3: 0}

    # First, check if split variations exist
    print("Checking for split test variations:")
    for split in range(1, 4):
        split_url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}-split{split}.html"
        try:
            response = requests.head(split_url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ Split {split} exists: {split_url}")
            else:
                print(f"  ❌ Split {split} not found: {split_url} (Status code: {response.status_code})")
        except Exception as e:
            print(f"  ❌ Error checking split {split}: {e}")

    # Now test the distribution
    print("\nTesting split distribution:")
    for i in range(iterations):
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html?test={i}"
        try:
            response = requests.get(url, allow_redirects=False, timeout=10)
            if response.status_code == 302:
                # Extract split from Location header
                location = response.headers.get('Location', '')
                print(f"  Iteration {i+1}: Redirect to {location}")
                if 'split=' in location:
                    split = location.split('split=')[1].split('&')[0]
                    splits[int(split)] += 1
                else:
                    splits[0] += 1
            else:
                # If no redirect, assume it's the main page (split=0)
                print(f"  Iteration {i+1}: No redirect (Status code: {response.status_code})")
                splits[0] += 1
        except Exception as e:
            print(f"  ❌ Error in iteration {i+1}: {e}")

    print(f"\n📊 Split test distribution after {iterations} iterations:")
    for split, count in splits.items():
        percentage = (count / iterations) * 100
        print(f"  - Split {split}: {count} ({percentage:.1f}%)")

    return True

def main():
    """Main function to run tests."""
    print("🚀 Starting basic tracking and accessibility test")

    # Test homepage
    print("\n🧪 Testing homepage access")
    test_page_access(f"{BASE_URL}/index.html", "homepage")

    # Test quiz selection page
    print("\n🧪 Testing quiz selection page access")
    test_page_access(f"{BASE_URL}/quiz-start.html", "quiz selection page")

    # Test user journey for each niche
    successful_niches = []
    for niche in NICHES:
        if test_user_journey(niche):
            successful_niches.append(niche)

    # Test split distribution for a successful niche
    if successful_niches:
        niche = successful_niches[0]
        # Try to find a valid bucket/variant combination
        buckets = ['foundation', 'growth', 'scaling', 'patients', 'clients']
        variants = ['a-solution', 'b-problem', 'c-most-aware']

        for bucket in buckets:
            for variant in variants:
                url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200 or response.status_code == 302:
                        test_split_distribution(niche, bucket, variant)
                        break
                except:
                    pass
            else:
                continue
            break

    print("\n✅ Testing completed")
    print(f"Successfully tested user journeys for {len(successful_niches)}/{len(NICHES)} niches")
    print("Successful niches:", ", ".join(successful_niches))

if __name__ == "__main__":
    main()
