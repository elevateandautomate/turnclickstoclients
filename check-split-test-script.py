#!/usr/bin/env python3
"""
Script to check if the split test redirect script is correctly included in all main variant pages.
This script will:
1. Find all main variant pages (e.g., foundation-variant-a-solution.html)
2. Check if the split-test-redirect.js script is correctly included
"""

import os
import re
import glob

# Path to the quiz applications directory
QUIZ_APPLICATIONS_DIR = 'quiz-applications'

def find_main_variant_pages():
    """Find all main variant pages (not split test variations)."""
    main_variant_pages = []
    
    # Walk through all directories in quiz-applications
    for root, dirs, files in os.walk(QUIZ_APPLICATIONS_DIR):
        for file in files:
            # Check if the file is an HTML file
            if file.endswith('.html'):
                # Check if the file is a main variant page (not a split test variation)
                if '-variant-' in file and not '-split' in file:
                    main_variant_pages.append(os.path.join(root, file))
    
    return main_variant_pages

def check_script_inclusion(page_path):
    """Check if the split-test-redirect.js script is correctly included in the page."""
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the script is included
    script_pattern = r'<script\s+src=["\'](?:\.\.\/)*split-test-redirect\.js["\']><\/script>'
    if re.search(script_pattern, content):
        return True
    else:
        return False

def main():
    """Main function."""
    print("Finding main variant pages...")
    main_variant_pages = find_main_variant_pages()
    print(f"Found {len(main_variant_pages)} main variant pages")
    
    # Check script inclusion in each page
    included_count = 0
    missing_count = 0
    for page_path in main_variant_pages:
        print(f"Checking {page_path}...")
        if check_script_inclusion(page_path):
            included_count += 1
            print(f"  ✅ Script is included")
        else:
            missing_count += 1
            print(f"  ❌ Script is missing")
    
    print(f"\nSummary: Script is included in {included_count} out of {len(main_variant_pages)} pages")
    print(f"Script is missing in {missing_count} pages")

if __name__ == "__main__":
    main()
