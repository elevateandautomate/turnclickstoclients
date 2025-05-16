#!/usr/bin/env python3
"""
Script to update quiz result pages with towards language instead of away language.
This script transforms the belief shifting framework sections to use more positive,
goal-oriented language that emphasizes achievement rather than avoidance.
"""

import os
import re
import sys
import glob
import time
import random

# Base directory
BASE_DIR = r"C:\Users\Eleva\Desktop\todo\contactlead\quiz-applications"

# Define market types (towards vs away)
TOWARDS_MARKETS = [
    'cosmetic-dentistry',
    'high-end-chiropractors',
    'hearing-aid-audiology',
    'dme-clinics',
    'sleep-apnea'
]

AWAY_MARKETS = [
    'child-care',
    'pmu-artists',
    'weight-loss-clinics',
    'non-surgical-body-contouring'
]

# Language transformation patterns
# Format: (away_pattern, towards_replacement)
HEADING_TRANSFORMATIONS = [
    (r"What's Possible \(That You're Missing Out On\)", "What's Possible When You Implement This System"),
    (r"What's Possible With This Solution \(That You're Missing Out On\)", "What's Possible When You Implement This Solution"),
    (r"What's Possible When You Solve This Problem \(That You're Missing Out On\)", "What's Possible When You Implement This Solution"),
    (r"The Gap Between You and These", "Your Path to Joining These"),
    (r"Ready to Stop Missing Out on the Success", "Ready to Create the Success"),
    (r"What You're Currently Missing Out On", "What You'll Soon Be Achieving"),
    (r"Stop Missing Out", "Start Succeeding")
]

CONTENT_TRANSFORMATIONS = [
    # Missing out -> achieving
    (r"you're missing the proven system", "you can implement the proven system"),
    (r"missing out on", "ready to achieve"),
    (r"Every day you wait is another day of missed", "Every day with this system means more"),
    (r"falling further behind", "making steady progress toward your goals"),
    
    # Problem focus -> solution focus
    (r"The difference between your current situation and these success stories", 
     "The path to joining these success stories"),
    (r"The real difference is that these successful .+ have implemented", 
     "Your opportunity is to implement"),
    
    # Negative -> positive framing
    (r"They're not more .+ than you\. They're not .+ than you\.", 
     "You have all the talent and dedication needed."),
    (r"the exact system you're currently missing", "the exact system now available to you"),
    
    # Away -> towards for CTAs
    (r"Apply Now to Stop Missing Out", "Apply Now to Start Succeeding"),
    (r"Don't let another day go by watching others succeed", 
     "Take the first step toward the success you deserve"),
    
    # Lack focus -> achievement focus
    (r"While you're struggling with", "You're ready to transform"),
    (r"As you worry about", "As you prepare for"),
    (r"Rather than stressing about", "By confidently managing"),
]

def determine_market_type(niche):
    """Determine if a niche is primarily towards or away focused."""
    if niche in TOWARDS_MARKETS:
        return "towards"
    elif niche in AWAY_MARKETS:
        return "away"
    else:
        # Default to balanced approach for unknown niches
        return "balanced"

def transform_language(content, market_type, variant):
    """Transform away language to towards language based on market type."""
    # Make a copy of the original content
    transformed = content
    
    # Determine the towards/away ratio based on market type and variant
    towards_ratio = 0.5  # Default balanced approach
    
    if market_type == "towards":
        towards_ratio = 0.8  # 80% towards language for towards markets
    elif market_type == "away":
        towards_ratio = 0.3  # 30% towards language for away markets
        
    # Adjust ratio based on variant
    if "solution" in variant:
        towards_ratio += 0.1  # Solution-aware can handle more towards language
    elif "problem" in variant:
        towards_ratio -= 0.1  # Problem-aware needs more away language
    
    # Apply heading transformations (always apply these)
    for away, towards in HEADING_TRANSFORMATIONS:
        transformed = re.sub(away, towards, transformed)
    
    # Apply content transformations based on the towards ratio
    for away, towards in CONTENT_TRANSFORMATIONS:
        # Only apply some transformations based on the towards ratio
        if random.random() < towards_ratio:
            transformed = re.sub(away, towards, transformed)
    
    return transformed

def update_file(file_path):
    """Update a single file with towards language."""
    print(f"Updating file: {file_path}")
    
    # Extract niche from file path
    path_parts = file_path.split(os.sep)
    niche_dir = path_parts[-3]  # Assuming structure is quiz-applications/niche/bucket/file.html
    
    # Extract variant from filename
    filename = os.path.basename(file_path)
    variant_match = re.search(r'variant-([abc]-\w+)', filename)
    variant = variant_match.group(1) if variant_match else "unknown"
    
    print(f"Processing niche: {niche_dir}, variant: {variant}")
    
    # Determine market type
    market_type = determine_market_type(niche_dir)
    print(f"Market type: {market_type}")
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Make a backup of the original file
    backup_path = file_path + ".bak"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Transform the language
    transformed_content = transform_language(content, market_type, variant)
    
    # Only write if changes were made
    if transformed_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(transformed_content)
        print(f"Successfully updated: {file_path}")
    else:
        print(f"No changes needed for: {file_path}")
        # Remove backup if no changes
        os.remove(backup_path)

def main():
    """Main function to process files."""
    # Check command line arguments
    if len(sys.argv) > 1:
        niche = sys.argv[1]
        bucket = sys.argv[2] if len(sys.argv) > 2 else '*'
        variant = sys.argv[3] if len(sys.argv) > 3 else '*'
        
        # Process specific files
        pattern = os.path.join(BASE_DIR, niche, bucket, f"*{variant}*.html")
        files = glob.glob(pattern)
    else:
        # Process all files
        files = glob.glob(os.path.join(BASE_DIR, '*', '*', '*.html'))
    
    # Update each file
    for file in files:
        update_file(file)
        # Add a small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    print(f"Updated {len(files)} files")

if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    main()
