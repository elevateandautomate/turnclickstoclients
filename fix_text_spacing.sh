#!/bin/bash

echo "Creating text spacing CSS..."
cat > text_spacing.css << 'CSSEOF'
/* Text Spacing Improvements */
p {
  margin-bottom: 1.2em !important;
  line-height: 1.6 !important;
}

h1, h2, h3, h4, h5, h6 {
  margin-top: 1.5em !important;
  margin-bottom: 0.8em !important;
  line-height: 1.3 !important;
}

ul, ol {
  margin-bottom: 1.2em !important;
  padding-left: 2em !important;
}

li {
  margin-bottom: 0.5em !important;
}

.section-content p:last-child,
.card-body p:last-child,
.content-block p:last-child {
  margin-bottom: 0 !important;
}

/* Improve readability on mobile */
@media (max-width: 768px) {
  p, li {
    font-size: 16px !important;
    line-height: 1.5 !important;
  }
  
  h1 {
    font-size: 28px !important;
    line-height: 1.2 !important;
  }
  
  h2 {
    font-size: 24px !important;
    line-height: 1.2 !important;
  }
  
  h3 {
    font-size: 20px !important;
    line-height: 1.2 !important;
  }
  
  /* Add more space between paragraphs on mobile */
  p {
    margin-bottom: 1.4em !important;
  }
  
  /* Ensure proper text wrapping */
  * {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
  }
}

/* Fix for long text without spaces */
.content-area p,
.content-area li,
.content-area div {
  word-break: break-word !important;
  max-width: 100% !important;
}

/* Ensure proper paragraph breaks */
p + p {
  margin-top: 0 !important;
}

/* Improve blockquote spacing */
blockquote {
  margin: 1.5em 0 !important;
  padding: 1em 1.5em !important;
  border-left: 4px solid #e0e0e0 !important;
  background-color: #f9f9f9 !important;
}

blockquote p {
  font-style: italic !important;
}

/* Fix for quiz pages */
.quiz-question p {
  margin-bottom: 1em !important;
}

.quiz-options label {
  margin-bottom: 0.8em !important;
  display: block !important;
}
CSSEOF

echo "Created text_spacing.css"

# Copy the text spacing CSS to all directories
cp text_spacing.css website/ 2>/dev/null || echo "Could not copy to website/"
mkdir -p apps
cp text_spacing.css apps/ 2>/dev/null || echo "Could not copy to apps/"
mkdir -p coldoutbound
cp text_spacing.css coldoutbound/ 2>/dev/null || echo "Could not copy to coldoutbound/"

echo "Copied text_spacing.css to directories"

# Find all HTML files
echo "Finding all HTML files..."
HTML_FILES=$(find . -name "*.html" -not -path "*/\.*")
HTML_COUNT=$(echo "$HTML_FILES" | wc -l)
echo "Found $HTML_COUNT HTML files"

# Add text spacing CSS to all HTML files
echo "Adding text spacing CSS to HTML files..."
for file in $HTML_FILES; do
  echo "Processing $file"
  # Determine the relative path based on the file's location
  DEPTH=$(echo "$file" | tr -cd "/" | wc -c)
  REL_PATH=""
  for ((i=1; i<$DEPTH; i++)); do
    REL_PATH="../$REL_PATH"
  done
  
  # Add text_spacing.css if not already present
  if ! grep -q "text_spacing.css" "$file"; then
    sed -i "s|</head>|    <link rel=\"stylesheet\" href=\"${REL_PATH}text_spacing.css\">\n</head>|" "$file"
    echo "  Added text_spacing.css to $file"
  fi
  
  # Fix paragraph structure
  sed -i "s|<br><br>|</p><p>|g" "$file"
  sed -i "s|<br /><br />|</p><p>|g" "$file"
  sed -i "s|<br/><br/>|</p><p>|g" "$file"
  sed -i "s|</li><li>|</li>\n    <li>|g" "$file"
  
  echo "  Fixed paragraph structure in $file"
done

echo "All text spacing improvements have been applied."
