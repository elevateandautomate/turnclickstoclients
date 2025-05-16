#!/usr/bin/env python3
"""
Script to check if all HTML files have the trust mechanism section.
"""

import os
import glob

# Base directory
BASE_DIR = r"C:\Users\Eleva\Desktop\todo\contactlead\quiz-applications"

def main():
    """Check all HTML files for trust mechanism section."""
    # Get all HTML files
    all_files = glob.glob(os.path.join(BASE_DIR, '*', '*', '*.html'))
    
    # Count files with trust mechanism
    files_with_trust = 0
    files_without_trust = []
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'trust-mechanism-container' in content:
                    files_with_trust += 1
                else:
                    files_without_trust.append(file_path)
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
                if 'trust-mechanism-container' in content:
                    files_with_trust += 1
                else:
                    files_without_trust.append(file_path)
    
    # Print results
    print(f"Total HTML files: {len(all_files)}")
    print(f"Files with trust mechanism: {files_with_trust}")
    print(f"Files missing trust mechanism: {len(files_without_trust)}")
    
    # Print files without trust mechanism if any
    if files_without_trust:
        print("\nFiles missing trust mechanism:")
        for file_path in files_without_trust:
            print(f"  - {file_path}")

if __name__ == "__main__":
    main()
