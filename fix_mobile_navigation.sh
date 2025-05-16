#!/bin/bash

echo "Fixing mobile navigation menu issues site-wide..."

# Find all HTML files in the project
HTML_FILES=$(find . -name "*.html" -not -path "*/\.*")
HTML_COUNT=$(echo "$HTML_FILES" | wc -l)

echo "Found $HTML_COUNT HTML files to update."

# 1. Add improved hamburger menu CSS to all HTML files
echo "1. Adding improved hamburger menu CSS to all HTML files..."
for file in $HTML_FILES; do
  # Determine the relative path based on the file's location
  DEPTH=$(echo "$file" | tr -cd "/" | wc -c)
  REL_PATH=""
  for ((i=1; i<$DEPTH; i++)); do
    REL_PATH="../$REL_PATH"
  done
  
  # Remove old hamburger fix CSS if present
  sed -i '/hamburger_fix.css/d' "$file"
  sed -i '/hamburger_clickable_fix.css/d' "$file"
  
  # Add improved hamburger fix CSS if not already present
  if ! grep -q "improved_hamburger_fix.css" "$file"; then
    sed -i "s|</head>|    <link rel=\"stylesheet\" href=\"${REL_PATH}improved_hamburger_fix.css\">\n</head>|" "$file"
    echo "  Added improved_hamburger_fix.css to $file"
  fi
done

# 2. Add improved hamburger menu JavaScript to all HTML files
echo "2. Adding improved hamburger menu JavaScript to all HTML files..."
for file in $HTML_FILES; do
  # Determine the relative path based on the file's location
  DEPTH=$(echo "$file" | tr -cd "/" | wc -c)
  REL_PATH=""
  for ((i=1; i<$DEPTH; i++)); do
    REL_PATH="../$REL_PATH"
  done
  
  # Remove old hamburger fix JS if present
  sed -i '/hamburger_fix.js/d' "$file"
  
  # Add improved hamburger fix JS if not already present
  if ! grep -q "improved_hamburger_fix.js" "$file"; then
    sed -i "s|</body>|    <script src=\"${REL_PATH}improved_hamburger_fix.js\"></script>\n</body>|" "$file"
    echo "  Added improved_hamburger_fix.js to $file"
  fi
done

# 3. Fix the "Get Started" button in mobile navigation
echo "3. Fixing 'Get Started' button in mobile navigation..."
for file in $HTML_FILES; do
  # Find and add class to Get Started button in navigation
  if grep -q "Get Started" "$file" && grep -q "navbar-nav" "$file"; then
    # Add mobile-centered-btn class to Get Started button
    sed -i 's/\(class="[^"]*\)get-started-btn\([^"]*"\)/\1get-started-btn mobile-centered-btn\2/g' "$file"
    echo "  Fixed Get Started button in $file"
  fi
done

# 4. Fix dropdown functionality for "Clients We Serve"
echo "4. Fixing dropdown functionality for 'Clients We Serve'..."
for file in $HTML_FILES; do
  # Find and fix Clients We Serve dropdown
  if grep -q "Clients We Serve" "$file" && grep -q "dropdown" "$file"; then
    # Ensure dropdown has proper attributes
    sed -i 's/\(class="[^"]*\)dropdown\([^"]*"\)/\1dropdown nav-item\2/g' "$file"
    sed -i 's/\(class="[^"]*\)dropdown-toggle\([^"]*"\)/\1dropdown-toggle nav-link\2/g' "$file"
    
    # Ensure dropdown menu has proper classes
    sed -i 's/\(class="[^"]*\)dropdown-menu\([^"]*"\)/\1dropdown-menu dropdown-menu-mobile\2/g' "$file"
    
    echo "  Fixed Clients We Serve dropdown in $file"
  fi
done

echo "All mobile navigation fixes have been applied to $HTML_COUNT HTML files."
echo "The hamburger menu should now work consistently across all pages."
echo "The Get Started button should be centered in the mobile menu."
echo "The Clients We Serve dropdown should now work properly in mobile view."
