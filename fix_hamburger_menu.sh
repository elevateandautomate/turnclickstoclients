#!/bin/bash

# Fix the hamburger menu in the index.html file
sed -i 's|<button class="hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="main-nav" style="display:none;">|<button class="hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="main-nav">|g' index.html

# Fix the hamburger menu in the website/index.html file
sed -i 's|<button class="hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="main-nav" style="display:none;">|<button class="hamburger" aria-label="Open navigation" aria-expanded="false" aria-controls="main-nav">|g' website/index.html

# Fix the JavaScript for the hamburger menu in the index.html file
sed -i 's|hamburger.style.display = '\''block'\'';|// hamburger is now visible by default in mobile view|g' index.html

# Fix the JavaScript for the hamburger menu in the website/index.html file
sed -i 's|hamburger.style.display = '\''block'\'';|// hamburger is now visible by default in mobile view|g' website/index.html

# Create a new CSS file for the hamburger menu fixes
cat > hamburger_fix.css << 'CSSEOF'
/* Hamburger Menu Fixes */
@media (max-width: 900px) {
    .hamburger {
        display: block !important;
        position: absolute;
        top: 1rem;
        right: 1rem;
        cursor: pointer;
        z-index: 1002;
        background: none;
        border: none;
        padding: 10px;
    }

    .hamburger span {
        display: block;
        width: 25px;
        height: 3px;
        background-color: #333;
        margin: 5px 0;
        transition: all 0.3s ease-in-out;
    }

    /* Animation for hamburger to X */
    .hamburger[aria-expanded="true"] span:nth-child(1) {
        transform: rotate(45deg) translate(5px, 5px);
    }

    .hamburger[aria-expanded="true"] span:nth-child(2) {
        opacity: 0;
    }

    .hamburger[aria-expanded="true"] span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -7px);
    }

    #main-nav {
        display: none;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.97);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 0.75rem 0;
        z-index: 1001;
    }

    #main-nav.open {
        display: flex !important;
    }

    #main-nav li {
        margin-left: 0;
        text-align: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #eee;
    }

    #main-nav li a {
        display: block;
        padding: 0.5rem 1rem;
    }

    /* Hide hamburger on desktop */
    @media (min-width: 901px) {
        .hamburger {
            display: none !important;
        }
    }
}
CSSEOF

# Copy the hamburger fix CSS to all directories
cp hamburger_fix.css website/
cp hamburger_fix.css apps/
cp hamburger_fix.css coldoutbound/

# Add the hamburger fix CSS to the index.html file
sed -i '/<link rel="stylesheet" href="\/mobile_optimization.css">/a \    <link rel="stylesheet" href="hamburger_fix.css">' index.html

# Add the hamburger fix CSS to the website/index.html file
sed -i '/<link rel="stylesheet" href="\/mobile_optimization.css">/a \    <link rel="stylesheet" href="hamburger_fix.css">' website/index.html

# Add the hamburger fix CSS to all niche pages
find niches -name "*.html" -exec sed -i '/<link rel="stylesheet" href="..\/mobile_optimization.css">/a \    <link rel="stylesheet" href="../hamburger_fix.css">' {} \;

# Add the hamburger fix CSS to all website/niche pages
find website/niches -name "*.html" -exec sed -i '/<link rel="stylesheet" href="..\/..\/mobile_optimization.css">/a \    <link rel="stylesheet" href="../../hamburger_fix.css">' {} \;

# Add the hamburger fix CSS to the onboarding portal
sed -i '/<link rel="stylesheet" href="..\/..\/mobile_optimization.css">/a \    <link rel="stylesheet" href="../../hamburger_fix.css">' apps/onboarding/index.html

# Add the hamburger fix CSS to the dashboard
sed -i '/<link rel="stylesheet" href="..\/..\/..\/mobile_optimization.css">/a \    <link rel="stylesheet" href="../../../hamburger_fix.css">' apps/dashboard/agencydashboard/index.html

echo "Hamburger menu fixed in all pages."
