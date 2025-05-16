#!/bin/bash

# Find all HTML files
find . -name "*.html" -not -path "*/\.*" | while read -r file; do
  # Remove the Pricing link from the header navigation
  sed -i '/href=".*#pricing">Pricing<\/a><\/li>/d' "$file"
  sed -i '/href=".*\/services\/pricing.html">Pricing<\/a><\/li>/d' "$file"
done

echo "Pricing links removed from header navigation in all HTML files."
