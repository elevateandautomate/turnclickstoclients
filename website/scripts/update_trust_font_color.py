#!/usr/bin/env python3
"""
Script to update the font color of the trust mechanism section to black.
"""

import os
import re
import glob
import time

# Base directory
BASE_DIR = r"C:\Users\Eleva\Desktop\todo\contactlead\quiz-applications"

def update_file(file_path):
    """Update a single file's trust mechanism font color."""
    print(f"Updating file: {file_path}")
    
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Make a backup of the original file
    backup_path = file_path + ".color.bak"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Update the trust mechanism section font color
    
    # 1. Update the heading color
    content = re.sub(
        r'<h3 style="color: #2c3e50; font-size: 1.4em; margin-bottom: 20px;">',
        r'<h3 style="color: #000000; font-size: 1.4em; margin-bottom: 20px;">',
        content
    )
    
    # 2. Update the subheading color
    content = re.sub(
        r'<h4 style="color: #2c3e50; font-size: 1.2em; margin: 20px 0 15px;">',
        r'<h4 style="color: #000000; font-size: 1.2em; margin: 20px 0 15px;">',
        content
    )
    
    # 3. Update the paragraph text color (if not already black)
    content = re.sub(
        r'<p style="font-size: 1.1em; line-height: 1.6;">',
        r'<p style="font-size: 1.1em; line-height: 1.6; color: #000000;">',
        content
    )
    
    # 4. Update the list item text color
    content = re.sub(
        r'<li style="margin-bottom: 12px; padding-left: 25px; position: relative;">',
        r'<li style="margin-bottom: 12px; padding-left: 25px; position: relative; color: #000000;">',
        content
    )
    
    # Write the updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully updated font color in: {file_path}")

def main():
    """Main function to process files."""
    # Get all HTML files
    files = glob.glob(os.path.join(BASE_DIR, '*', '*', '*.html'))
    
    # Update each file
    for file in files:
        update_file(file)
        # Add a small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    print(f"Updated font color in {len(files)} files")

if __name__ == "__main__":
    main()
