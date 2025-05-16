#!/bin/bash

# Find all HTML files
find . -name "*.html" -not -path "*/\.*" | while read -r file; do
  # Check if the file already has the mobile optimization CSS
  if ! grep -q "mobile_optimization.css" "$file"; then
    echo "Adding mobile optimization CSS to $file"
    
    # Check if the file has a head section
    if grep -q "</head>" "$file"; then
      # Add the mobile optimization CSS link before the closing head tag
      sed -i 's|</head>|    <link rel="stylesheet" href="/mobile_optimization.css">\n</head>|' "$file"
    fi
  fi
done

echo "Mobile optimization CSS added to all missing HTML files."
