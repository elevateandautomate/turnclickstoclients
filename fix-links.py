import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(r"C:\Users\Eleva\Desktop\todo\contactlead")
NICHES_DIR = BASE_DIR / "niches"

# Pattern to match absolute file paths
FILE_PATH_PATTERN = r'href="file:///C:/Users/Eleva/Desktop/todo/contactlead/([^"]+)"'

# Count successful updates
updated_files = 0
total_replacements = 0

# Process all HTML files in the niches directory
for html_file in NICHES_DIR.glob('*.html'):
    try:
        # Read file content
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all instances of absolute file paths
        matches = re.findall(FILE_PATH_PATTERN, content)
        
        if matches:
            # Replace absolute paths with relative paths
            new_content = re.sub(
                FILE_PATH_PATTERN,
                lambda m: f'href="../{m.group(1)}"',
                content
            )
            
            # Count replacements
            replacements = len(matches)
            total_replacements += replacements
            
            # Write updated content back to file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Updated {html_file.name} - {replacements} links fixed")
            updated_files += 1
        else:
            print(f"No absolute paths found in {html_file.name}")
    
    except Exception as e:
        print(f"Error processing {html_file.name}: {str(e)}")

print(f"\nSummary:")
print(f"  - {updated_files} HTML files updated")
print(f"  - {total_replacements} absolute paths replaced with relative paths")
print("\nDone!") 