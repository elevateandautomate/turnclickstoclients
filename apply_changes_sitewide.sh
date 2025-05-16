#!/bin/bash

echo "Applying all changes site-wide to every HTML file..."

# Find all HTML files in the project
HTML_FILES=$(find . -name "*.html" -not -path "*/\.*")
HTML_COUNT=$(echo "$HTML_FILES" | wc -l)

echo "Found $HTML_COUNT HTML files to update."

# 1. Update mobile optimization CSS links
echo "1. Ensuring mobile optimization CSS is linked in all HTML files..."
for file in $HTML_FILES; do
  if ! grep -q "mobile_optimization.css" "$file"; then
    # Determine the relative path based on the file's location
    DEPTH=$(echo "$file" | tr -cd '/' | wc -c)
    REL_PATH=""
    for ((i=1; i<$DEPTH; i++)); do
      REL_PATH="../$REL_PATH"
    done
    
    # Add the mobile optimization CSS link before the closing head tag
    sed -i "s|</head>|    <link rel=\"stylesheet\" href=\"${REL_PATH}mobile_optimization.css\">\n</head>|" "$file"
    echo "  Added mobile_optimization.css to $file"
  fi
done

# 2. Update hamburger menu CSS and JS links
echo "2. Ensuring hamburger menu fixes are applied to all HTML files..."
for file in $HTML_FILES; do
  # Determine the relative path based on the file's location
  DEPTH=$(echo "$file" | tr -cd '/' | wc -c)
  REL_PATH=""
  for ((i=1; i<$DEPTH; i++)); do
    REL_PATH="../$REL_PATH"
  done
  
  # Add hamburger_fix.css if not already present
  if ! grep -q "hamburger_fix.css" "$file"; then
    sed -i "s|</head>|    <link rel=\"stylesheet\" href=\"${REL_PATH}hamburger_fix.css\">\n</head>|" "$file"
    echo "  Added hamburger_fix.css to $file"
  fi
  
  # Add hamburger_clickable_fix.css if not already present
  if ! grep -q "hamburger_clickable_fix.css" "$file"; then
    sed -i "s|</head>|    <link rel=\"stylesheet\" href=\"${REL_PATH}hamburger_clickable_fix.css\">\n</head>|" "$file"
    echo "  Added hamburger_clickable_fix.css to $file"
  fi
  
  # Add hamburger_fix.js if not already present
  if ! grep -q "hamburger_fix.js" "$file"; then
    sed -i "s|</body>|    <script src=\"${REL_PATH}hamburger_fix.js\"></script>\n</body>|" "$file"
    echo "  Added hamburger_fix.js to $file"
  fi
done

# 3. Update chat widget CSS links
echo "3. Ensuring chat widget improvements are applied to all HTML files..."
for file in $HTML_FILES; do
  # Determine the relative path based on the file's location
  DEPTH=$(echo "$file" | tr -cd '/' | wc -c)
  REL_PATH=""
  for ((i=1; i<$DEPTH; i++)); do
    REL_PATH="../$REL_PATH"
  done
  
  # Add chat_widget_improvements.css if not already present
  if ! grep -q "chat_widget_improvements.css" "$file"; then
    sed -i "s|</head>|    <link rel=\"stylesheet\" href=\"${REL_PATH}chat_widget_improvements.css\">\n</head>|" "$file"
    echo "  Added chat_widget_improvements.css to $file"
  fi
done

# 4. Update chat button HTML
echo "4. Updating chat button HTML in all files that have it..."
for file in $HTML_FILES; do
  if grep -q "id=\"chat-widget-button\"" "$file"; then
    # Create a temporary file with the new chat button HTML
    cat > temp_chat_button.html << 'HTMLEOF'
    <div id="chat-widget-button">
        <span><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg></span> Chat
    </div>
HTMLEOF

    # Replace the old chat button with the new one
    awk '
    /id="chat-widget-button"/ {
      getline; getline;
      system("cat temp_chat_button.html");
      next;
    }
    /id="chat-widget-button"/ { p=1 }
    p && /^    <\/div>/ { p=0; next }
    !p { print }
    ' "$file" > "$file.new" && mv "$file.new" "$file"
    
    echo "  Updated chat button in $file"
  fi
done

# Clean up
rm -f temp_chat_button.html

# 5. Update "3 min" to "30 seconds" in all files
echo "5. Updating '3 min' to '30 seconds' in all files..."
find . -name "*.html" -exec sed -i 's|in 3 Mins|in 30 seconds|g' {} \;
find . -name "*.html" -exec sed -i 's|in 3 mins|in 30 seconds|g' {} \;
find . -name "*.html" -exec sed -i 's|in 3min|in 30 seconds|g' {} \;
find . -name "*.html" -exec sed -i 's|in 3-min|in 30 seconds|g' {} \;
echo "  Updated time references in all HTML files"

# 6. Remove field explanations from all quiz pages
echo "6. Removing field explanations from all quiz pages..."
find . -name "*-quiz.html" -exec sed -i '/<p class="field-explanation">We'\''re asking/d' {} \;
echo "  Removed field explanations from all quiz pages"

# 7. Fix absolute paths to quiz-start.html
echo "7. Fixing absolute paths to quiz-start.html..."
find . -name "*.html" -exec sed -i 's|file:///C:/Users/Eleva/Desktop/todo/contactlead/quiz-start.html|quiz-start.html|g' {} \;
echo "  Fixed absolute paths to quiz-start.html"

# 8. Fix absolute paths to universal-application-form.html
echo "8. Fixing absolute paths to universal-application-form.html..."
find . -name "*.html" -exec sed -i 's|file:///C:/Users/Eleva/Desktop/todo/contactlead/universal-application-form.html|universal-application-form.html|g' {} \;
echo "  Fixed absolute paths to universal-application-form.html"

# 9. Fix copyright text in onboarding portal
echo "9. Fixing copyright text in onboarding portal..."
sed -i 's|&copy; 2024 The Connector Group. All rights reserved.copy; 2024 TurnClicksToClients.com. All rights reserved.|&copy; 2024 TurnClicksToClients.com. All rights reserved.|g' apps/onboarding/index.html
echo "  Fixed copyright text in onboarding portal"

echo "All changes have been applied site-wide to every HTML file."
echo "Total files updated: $HTML_COUNT"
