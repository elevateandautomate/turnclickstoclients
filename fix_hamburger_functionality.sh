#!/bin/bash

# Create a new JavaScript file for the hamburger menu fix
cat > hamburger_fix.js << 'JSEOF'
// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the hamburger button and navigation menu
    const hamburger = document.querySelector('.hamburger');
    const navUl = document.querySelector('#main-nav');
    
    if (hamburger && navUl) {
        // Function to close all dropdowns
        function closeAllDropdowns() {
            document.querySelectorAll('.dropdown-parent').forEach(li => li.classList.remove('open'));
        }
        
        // Add click event listener to hamburger button
        hamburger.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default behavior
            const open = navUl.classList.toggle('open');
            hamburger.setAttribute('aria-expanded', open);
            if (!open) closeAllDropdowns();
            
            // Log for debugging
            console.log('Hamburger clicked, nav is now: ' + (open ? 'open' : 'closed'));
        });
        
        // Dropdowns for mobile
        navUl.querySelectorAll('.dropdown-parent > a').forEach(link => {
            link.addEventListener('click', function(e) {
                if (window.innerWidth <= 900) {
                    e.preventDefault();
                    const parent = this.parentElement;
                    
                    // Close all other dropdowns
                    document.querySelectorAll('.dropdown-parent').forEach(li => {
                        if (li !== parent) li.classList.remove('open');
                    });
                    
                    // Toggle this dropdown
                    parent.classList.toggle('open');
                }
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!hamburger.contains(e.target) && !navUl.contains(e.target) && navUl.classList.contains('open')) {
                navUl.classList.remove('open');
                hamburger.setAttribute('aria-expanded', false);
                closeAllDropdowns();
            }
        });
    } else {
        console.error('Hamburger menu or navigation not found');
    }
});
JSEOF

# Copy the hamburger fix JS to all directories
cp hamburger_fix.js website/
cp hamburger_fix.js apps/
cp hamburger_fix.js coldoutbound/

# Add the hamburger fix JS to the index.html file
sed -i '/<\/body>/i \    <script src="hamburger_fix.js"></script>' index.html

# Add the hamburger fix JS to the website/index.html file
sed -i '/<\/body>/i \    <script src="hamburger_fix.js"></script>' website/index.html

# Add the hamburger fix JS to all niche pages
find niches -name "*.html" -exec sed -i '/<\/body>/i \    <script src="../hamburger_fix.js"></script>' {} \;

# Add the hamburger fix JS to all website/niche pages
find website/niches -name "*.html" -exec sed -i '/<\/body>/i \    <script src="../../hamburger_fix.js"></script>' {} \;

# Add the hamburger fix JS to the onboarding portal
sed -i '/<\/body>/i \    <script src="../../hamburger_fix.js"></script>' apps/onboarding/index.html

# Add the hamburger fix JS to the dashboard
sed -i '/<\/body>/i \    <script src="../../../hamburger_fix.js"></script>' apps/dashboard/agencydashboard/index.html

# Update the CSS to ensure the hamburger button is clickable
cat > hamburger_clickable_fix.css << 'CSSEOF'
/* Ensure hamburger button is clickable */
@media (max-width: 900px) {
    .hamburger {
        cursor: pointer !important;
        z-index: 1002 !important;
        position: absolute !important;
        top: 1rem !important;
        right: 1rem !important;
        background: none !important;
        border: none !important;
        padding: 10px !important;
        outline: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }
    
    /* Make the spans larger for better touch targets */
    .hamburger span {
        display: block !important;
        width: 30px !important;
        height: 4px !important;
        background-color: #333 !important;
        margin: 6px 0 !important;
        transition: all 0.3s ease-in-out !important;
    }
    
    /* Ensure the navigation menu appears correctly */
    #main-nav.open {
        display: flex !important;
        opacity: 1 !important;
        visibility: visible !important;
        transform: translateY(0) !important;
    }
}
CSSEOF

# Copy the hamburger clickable fix CSS to all directories
cp hamburger_clickable_fix.css website/
cp hamburger_clickable_fix.css apps/
cp hamburger_clickable_fix.css coldoutbound/

# Add the hamburger clickable fix CSS to the index.html file
sed -i '/<link rel="stylesheet" href="chat_widget_improvements.css">/a \    <link rel="stylesheet" href="hamburger_clickable_fix.css">' index.html

# Add the hamburger clickable fix CSS to the website/index.html file
sed -i '/<link rel="stylesheet" href="chat_widget_improvements.css">/a \    <link rel="stylesheet" href="hamburger_clickable_fix.css">' website/index.html

# Add the hamburger clickable fix CSS to all niche pages
find niches -name "*.html" -exec sed -i '/<link rel="stylesheet" href="..\/chat_widget_improvements.css">/a \    <link rel="stylesheet" href="../hamburger_clickable_fix.css">' {} \;

# Add the hamburger clickable fix CSS to all website/niche pages
find website/niches -name "*.html" -exec sed -i '/<link rel="stylesheet" href="..\/..\/chat_widget_improvements.css">/a \    <link rel="stylesheet" href="../../hamburger_clickable_fix.css">' {} \;

# Add the hamburger clickable fix CSS to the onboarding portal
sed -i '/<link rel="stylesheet" href="..\/..\/chat_widget_improvements.css">/a \    <link rel="stylesheet" href="../../hamburger_clickable_fix.css">' apps/onboarding/index.html

# Add the hamburger clickable fix CSS to the dashboard
sed -i '/<link rel="stylesheet" href="..\/..\/..\/chat_widget_improvements.css">/a \    <link rel="stylesheet" href="../../../hamburger_clickable_fix.css">' apps/dashboard/agencydashboard/index.html

echo "Hamburger menu functionality fixed."
