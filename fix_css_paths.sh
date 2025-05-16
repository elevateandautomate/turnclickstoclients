#!/bin/bash

# Fix the CSS path for the onboarding portal
sed -i 's|href="/mobile_optimization.css"|href="../../mobile_optimization.css"|g' apps/onboarding/index.html
sed -i 's|href="/mobile_optimization.css"|href="../../../mobile_optimization.css"|g' apps/onboarding/js/welcomeguide.html

# Fix the CSS path for the dashboard
sed -i 's|href="/mobile_optimization.css"|href="../../../mobile_optimization.css"|g' apps/dashboard/agencydashboard/index.html

# Fix the CSS path for the website directory
find ./website -name "*.html" -not -path "*/\.*" | xargs sed -i 's|href="/mobile_optimization.css"|href="../mobile_optimization.css"|g'

# Fix the CSS path for the niches directory
find ./niches -name "*.html" -not -path "*/\.*" | xargs sed -i 's|href="/mobile_optimization.css"|href="../mobile_optimization.css"|g'

# Fix the CSS path for the website/niches directory
find ./website/niches -name "*.html" -not -path "*/\.*" | xargs sed -i 's|href="../mobile_optimization.css"|href="../../mobile_optimization.css"|g'

echo "CSS paths fixed for all HTML files."
