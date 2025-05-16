#!/usr/bin/env python3
"""
Script to add split test redirect code to all main variant pages.
This script will:
1. Find all main variant pages (e.g., foundation-variant-a-solution.html)
2. Add the split test redirect script to each page
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

def add_split_test_redirect(page_path):
    """Add split test redirect script to a page."""
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the script is already included
    if '<script src="/split-test-redirect.js"></script>' in content:
        print(f"Split test redirect script already included in {page_path}")
        return False
    
    # Add the script before the closing </head> tag
    new_content = content.replace('</head>', '    <script src="/split-test-redirect.js"></script>\n  </head>')
    
    # Write the updated content back to the file
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    """Main function."""
    print("Finding main variant pages...")
    main_variant_pages = find_main_variant_pages()
    print(f"Found {len(main_variant_pages)} main variant pages")
    
    # Add split test redirect script to each page
    updated_count = 0
    for page_path in main_variant_pages:
        print(f"Processing {page_path}...")
        if add_split_test_redirect(page_path):
            updated_count += 1
            print(f"  ✅ Added split test redirect script")
        else:
            print(f"  ⚠️ No changes made")
    
    print(f"\nSummary: Added split test redirect script to {updated_count} out of {len(main_variant_pages)} pages")

if __name__ == "__main__":
    main()
