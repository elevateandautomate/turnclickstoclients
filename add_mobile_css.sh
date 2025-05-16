#!/bin/bash

# Find all HTML files
find . -name "*.html" -not -path "*/\.*" | while read -r file; do
  # Skip files in certain directories
  if [[ "$file" == *"/apps/"* ]] || [[ "$file" == *"/test_results/"* ]]; then
    continue
  fi
  
  # Check if the file has a head section
  if grep -q "</head>" "$file"; then
    # Add the mobile optimization CSS link before the closing head tag
    sed -i 's|</head>|    <link rel="stylesheet" href="/mobile_optimization.css">\n</head>|' "$file"
  fi
done

echo "Mobile optimization CSS added to all HTML files."
