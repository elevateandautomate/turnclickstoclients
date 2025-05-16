#!/usr/bin/env python3
"""
Script to test split test variations for all niches.
This script verifies that all split test variations are accessible and correctly configured.
"""

import os
import sys
import requests
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

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

def test_page_exists(url):
    """Test if a page exists and return the status code."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return 0

def test_split_variation(niche, bucket, variant, split):
    """Test a specific split test variation."""
    if split == 0:
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
    else:
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}-split{split}.html"
    
    status_code = test_page_exists(url)
    
    if status_code == 200:
        return True, url, "OK"
    elif status_code == 302:
        return True, url, "Redirect"
    else:
        return False, url, f"Status: {status_code}"

def verify_split_content(niche, bucket, variant):
    """Verify that split variations have different content."""
    results = {}
    content_hashes = {}
    
    # Check main variant and all splits
    for split in range(4):  # 0 = main, 1-3 = splits
        if split == 0:
            url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
        else:
            url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}-split{split}.html"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                # Get content hash to compare
                soup = BeautifulSoup(response.text, 'html.parser')
                # Remove script tags which might contain dynamic content
                for script in soup.find_all('script'):
                    script.decompose()
                
                # Get main content area
                main_content = soup.find('main')
                if main_content:
                    content_hash = hash(main_content.get_text())
                    content_hashes[split] = content_hash
                    results[split] = "Content verified"
                else:
                    results[split] = "No main content found"
            else:
                results[split] = f"Status: {response.status_code}"
        except Exception as e:
            results[split] = f"Error: {e}"
    
    # Check if content is different across splits
    unique_hashes = len(set(content_hashes.values()))
    if len(content_hashes) > 1 and unique_hashes == len(content_hashes):
        return True, results, "All split variations have unique content"
    elif len(content_hashes) > 1:
        return False, results, f"Some split variations have identical content ({unique_hashes} unique out of {len(content_hashes)})"
    else:
        return False, results, "Could not verify split content differences"

def verify_tracking_code(niche, bucket, variant, split=0):
    """Verify that the page contains Supabase tracking code."""
    if split == 0:
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
    else:
        url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}-split{split}.html"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Check for Supabase tracking code
            if 'supabase' in response.text.lower() and 'tctc_user_flow' in response.text:
                # Check for split parameter in tracking code
                if f'page_split: window.userParams.split' in response.text or f"page_split: '{split}'" in response.text:
                    return True, "Tracking code with split parameter verified"
                else:
                    return False, "Tracking code found but missing split parameter"
            else:
                return False, "No Supabase tracking code found"
        else:
            return False, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {e}"

def test_niche_bucket_variant(niche, bucket, variant):
    """Test all split variations for a specific niche/bucket/variant combination."""
    print(f"\n🧪 Testing {niche}/{bucket}/{variant}")
    
    # Test main variant
    main_exists, main_url, main_status = test_split_variation(niche, bucket, variant, 0)
    if main_exists:
        print(f"✅ Main variant exists: {main_url} ({main_status})")
    else:
        print(f"❌ Main variant missing: {main_url} ({main_status})")
        return False
    
    # Test split variations
    split_results = []
    for split in range(1, 4):
        exists, url, status = test_split_variation(niche, bucket, variant, split)
        split_results.append((split, exists, url, status))
    
    all_splits_exist = all(exists for _, exists, _, _ in split_results)
    
    if all_splits_exist:
        print("✅ All split variations exist:")
        for split, _, url, status in split_results:
            print(f"  - Split {split}: {url} ({status})")
    else:
        print("⚠️ Some split variations are missing:")
        for split, exists, url, status in split_results:
            status_icon = "✅" if exists else "❌"
            print(f"  {status_icon} Split {split}: {url} ({status})")
    
    # Verify content differences
    content_different, content_results, content_message = verify_split_content(niche, bucket, variant)
    if content_different:
        print(f"✅ {content_message}")
    else:
        print(f"⚠️ {content_message}")
    
    # Verify tracking code
    tracking_ok, tracking_message = verify_tracking_code(niche, bucket, variant)
    if tracking_ok:
        print(f"✅ {tracking_message}")
    else:
        print(f"⚠️ {tracking_message}")
    
    return all_splits_exist and content_different and tracking_ok

def find_valid_combinations():
    """Find all valid niche/bucket/variant combinations."""
    valid_combinations = []
    
    for niche in NICHES:
        for bucket in BUCKETS:
            for variant in VARIANTS:
                url = f"{BASE_URL}/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html"
                status_code = test_page_exists(url)
                if status_code in [200, 302]:
                    valid_combinations.append((niche, bucket, variant))
    
    return valid_combinations

def main():
    """Main function to run tests."""
    print("🚀 Starting split test variation verification")
    
    # Find valid combinations
    print("🔍 Finding valid niche/bucket/variant combinations...")
    valid_combinations = find_valid_combinations()
    print(f"✅ Found {len(valid_combinations)} valid combinations")
    
    # Test each combination
    results = {}
    for niche, bucket, variant in valid_combinations:
        key = f"{niche}/{bucket}/{variant}"
        results[key] = test_niche_bucket_variant(niche, bucket, variant)
    
    # Summary
    print("\n📊 Test Summary:")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed < total:
        print("\n⚠️ Failed combinations:")
        for key, result in results.items():
            if not result:
                print(f"  - {key}")
    
    print("\n✅ Testing completed")

if __name__ == "__main__":
    main()
