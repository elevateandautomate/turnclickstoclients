#!/usr/bin/env python3
"""
Script to fix the results paths in the full_system_test.py file.
This script will update the test to use the correct directory names for the results pages.
"""

import re

# The correct directory names for the results pages
DIRECTORY_MAPPING = {
    'child-care-centers': 'child-care',
    'sleep-apnea-snoring-clinics': 'sleep-apnea',
    'hearing-aid-audiology-clinics': 'hearing-aid-audiology'
}

def fix_results_paths():
    """Fix the results paths in the full_system_test.py file."""
    # Read the file
    with open('full_system_test.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a mapping function for the results URL
    def replace_results_url(match):
        niche = match.group(1)
        rest = match.group(2)
        
        # Replace the niche with the correct directory name
        if niche in DIRECTORY_MAPPING:
            niche = DIRECTORY_MAPPING[niche]
        
        return f'"{BASE_URL}/quiz-applications/{niche}{rest}'
    
    # Find and replace the results URL pattern
    pattern = r'"http://localhost:8000/quiz-applications/([^/]+)/(.*?)"'
    content = re.sub(pattern, replace_results_url, content)
    
    # Write the updated content back to the file
    with open('full_system_test.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Successfully updated the results paths in full_system_test.py")

# Add the BASE_URL constant
BASE_URL = 'http://localhost:8000'

if __name__ == "__main__":
    fix_results_paths()
