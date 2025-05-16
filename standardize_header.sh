#!/bin/bash

# Find all HTML files
find . -name "*.html" -not -path "*/\.*" | while read -r file; do
  # Skip files in the apps directory
  if [[ "$file" == *"/apps/"* ]]; then
    continue
  fi
  
  # Check if the file has a header section
  if grep -q "<header" "$file"; then
    # Replace the navigation structure with the standardized version
    sed -i '/<header/,/<\/header>/c\
    <header>\
        <nav aria-label="Main Navigation">\
            <div class="logo"><a href="index.html" style="color: inherit; text-decoration: none;">TurnClicksToClients.com</a></div>\
            <button class="hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="main-nav" style="display:none;">\
                <span></span>\
                <span></span>\
                <span></span>\
            </button>\
            <ul id="main-nav">\
                <li style="margin-right: 8px;"><a href="index.html">Home</a></li>\
                <li style="margin-right: 8px;"><a href="about.html">About Us</a></li>\
                <li class="dropdown-parent" style="margin-right: 8px;">\
                    <a href="#ideal-clients">Clients We Serve <span class="dropdown-arrow">▼</span></a>\
                    <ul class="dropdown-menu">\
                        <li><a href="niches/child-care-centers.html">Child Care Centers</a></li>\
                        <li><a href="niches/cosmetic-dentists.html">Cosmetic Dentists</a></li>\
                        <li><a href="niches/pmu-artists.html">PMU Artists</a></li>\
                        <li><a href="niches/non-surgical-body-contouring.html">Non-Surgical Body Contouring</a></li>\
                        <li><a href="niches/weight-loss-clinics.html">Weight Loss Clinics</a></li>\
                        <li><a href="niches/high-end-chiropractors.html">High-End Chiropractors</a></li>\
                        <li><a href="niches/sleep-apnea-snoring-clinics.html">Sleep Apnea & Snoring Clinics</a></li>\
                        <li><a href="niches/hearing-aid-audiology-clinics.html">Hearing Aid & Audiology</a></li>\
                        <li><a href="niches/dme-clinics.html">DME Clinics</a></li>\
                    </ul>\
                </li>\
                <li style="margin-right: 8px;"><a href="index.html#core-offer">Our Offer</a></li>\
                <li style="margin-right: 8px;"><a href="index.html#guarantee">Guarantee</a></li>\
                <li><a href="index.html#cta-contact" class="cta-button nav-cta">Get Started</a></li>\
            </ul>\
        </nav>\
    </header>' "$file"
    
    # Fix paths for niche pages
    if [[ "$file" == *"/niches/"* ]]; then
      sed -i 's|href="index.html"|href="../index.html"|g' "$file"
      sed -i 's|href="about.html"|href="../about.html"|g' "$file"
      sed -i 's|href="#ideal-clients"|href="../index.html#ideal-clients"|g' "$file"
      sed -i 's|href="index.html#core-offer"|href="../index.html#core-offer"|g' "$file"
      sed -i 's|href="index.html#guarantee"|href="../index.html#guarantee"|g' "$file"
      sed -i 's|href="index.html#cta-contact"|href="../index.html#cta-contact"|g' "$file"
      sed -i 's|href="niches/|href="|g' "$file"
    fi
  fi
done

echo "Header navigation standardized across all HTML files."
