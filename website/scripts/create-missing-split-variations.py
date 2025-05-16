#!/usr/bin/env python3
"""
Script to create missing split test variations for all main variant pages.
This script will:
1. Find all main variant pages (e.g., foundation-variant-a-solution.html)
2. Check if split test variations exist (e.g., foundation-variant-a-solution-split1.html)
3. Create missing split test variations by copying the main variant page
"""

import os
import re
import glob
import shutil

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

def create_split_variations(page_path):
    """Create split test variations for a main variant page."""
    # Get the directory and filename
    directory = os.path.dirname(page_path)
    filename = os.path.basename(page_path)

    # Get the base name without extension
    base_name = os.path.splitext(filename)[0]

    # Create split test variations
    created_count = 0
    for split in range(1, 4):
        split_filename = f"{base_name}-split{split}.html"
        split_path = os.path.join(directory, split_filename)

        # Check if the split test variation already exists
        if os.path.exists(split_path):
            print(f"  ⚠️ Split test variation {split} already exists: {split_path}")
            continue

        # Copy the main variant page to create the split test variation
        shutil.copy2(page_path, split_path)

        # Update the split parameter in the file
        with open(split_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update the split parameter in the JavaScript code
        content = re.sub(r"split: urlParams\.get\('split'\) \|\| '0'", f"split: urlParams.get('split') || '{split}'", content)

        # Update the application button link to include the split parameter
        content = content.replace('split=0', f'split={split}')

        # Write the updated content back to the file
        with open(split_path, 'w', encoding='utf-8') as f:
            f.write(content)

        created_count += 1
        print(f"  ✅ Created split test variation {split}: {split_path}")

    return created_count

def main():
    """Main function."""
    print("Finding main variant pages...")
    main_variant_pages = find_main_variant_pages()
    print(f"Found {len(main_variant_pages)} main variant pages")

    # Create split test variations for each page
    total_created = 0
    for page_path in main_variant_pages:
        print(f"Processing {page_path}...")
        try:
            created_count = create_split_variations(page_path)
            total_created += created_count
        except Exception as e:
            print(f"  ❌ Error processing {page_path}: {e}")

    print(f"\nSummary: Created {total_created} split test variations")

if __name__ == "__main__":
    main()
