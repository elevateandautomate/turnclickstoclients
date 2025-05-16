import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path(r"C:\Users\Eleva\Desktop\todo\contactlead")

# Tracking script reference to add
TRACKING_SCRIPT = '<script src="/tracking.js"></script>'

# Count successful updates
updated_files = 0
error_files = 0

# Process all HTML files
for html_file in BASE_DIR.glob('**/*.html'):
    try:
        # Read file content
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if tracking script is already added
        if '/tracking.js' in content:
            print(f"Skipping {html_file} - tracking script already added")
            continue
        
        # Find </head> tag
        head_match = re.search(r'</head>', content, re.IGNORECASE)
        
        if head_match:
            # Insert tracking script before </head>
            insert_pos = head_match.start()
            new_content = content[:insert_pos] + f"\n    {TRACKING_SCRIPT}\n  " + content[insert_pos:]
            
            # Write updated content back to file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Updated {html_file}")
            updated_files += 1
        else:
            # For files without a head tag, try adding before the first script
            script_match = re.search(r'<script', content, re.IGNORECASE)
            if script_match:
                insert_pos = script_match.start()
                new_content = content[:insert_pos] + f"{TRACKING_SCRIPT}\n" + content[insert_pos:]
                
                # Write updated content back to file
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Updated {html_file} (added before first script)")
                updated_files += 1
            else:
                print(f"Could not update {html_file} - no </head> or <script> tags found")
                error_files += 1
    
    except Exception as e:
        print(f"Error processing {html_file}: {str(e)}")
        error_files += 1

print(f"\nSummary:")
print(f"  - {updated_files} HTML files updated")
print(f"  - {error_files} files had errors")
print("\nDone!") 