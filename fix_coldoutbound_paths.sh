#!/bin/bash

# Fix the CSS path for the coldoutbound directory
find ./coldoutbound -name "*.html" -not -path "*/\.*" | xargs sed -i 's|href="/mobile_optimization.css"|href="../../mobile_optimization.css"|g'

echo "CSS paths fixed for coldoutbound HTML files."
