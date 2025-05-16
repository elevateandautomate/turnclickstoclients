#!/usr/bin/env python3
"""
Script to fix the quiz paths in the full_system_test.py file.
This script will update the NICHES variable to use the correct file names.
"""

import re

# The correct file names for the quiz pages
CORRECT_NICHES = {
    'cosmetic-dentistry': 'cosmetic-dentistry',
    'child-care': 'child-care-centers',
    'pmu-artists': 'pmu-artists',
    'sleep-apnea': 'sleep-apnea-snoring-clinics',
    'hearing-aid-audiology': 'hearing-aid-audiology-clinics',
    'dme-clinics': 'dme-clinics',
    'non-surgical-body-contouring': 'non-surgical-body-contouring'
}

def fix_quiz_paths():
    """Fix the quiz paths in the full_system_test.py file."""
    # Read the file
    with open('full_system_test.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the NICHES variable
    niches_pattern = r'NICHES = \[\s*([^\]]+)\]'
    niches_match = re.search(niches_pattern, content, re.DOTALL)
    
    if niches_match:
        niches_str = niches_match.group(1)
        
        # Replace each niche with the correct file name
        for old_niche, new_niche in CORRECT_NICHES.items():
            niches_str = niches_str.replace(f"'{old_niche}'", f"'{new_niche}'")
        
        # Update the NICHES variable
        new_niches = f"NICHES = [\n{niches_str}]"
        content = content.replace(niches_match.group(0), new_niches)
        
        # Write the updated content back to the file
        with open('full_system_test.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully updated the NICHES variable in full_system_test.py")
    else:
        print("❌ Could not find the NICHES variable in full_system_test.py")

if __name__ == "__main__":
    fix_quiz_paths()
