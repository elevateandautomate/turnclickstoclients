// Hamburger menu functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get hamburger button and navigation menu
    const hamburger = document.querySelector('.hamburger');
    const mainNav = document.getElementById('main-nav');
    
    if (hamburger && mainNav) {
        // Add click event listener to hamburger button
        hamburger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle active class on hamburger
            hamburger.classList.toggle('active');
            
            // Toggle open class on main navigation
            mainNav.classList.toggle('open');
            
            console.log('Hamburger clicked - Menu toggled');
        });
        
        console.log('Hamburger menu initialized');
    } else {
        console.error('Hamburger menu or main navigation not found');
        if (!hamburger) console.error('Hamburger button not found');
        if (!mainNav) console.error('Main navigation not found');
    }
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (mainNav.classList.contains('open') && 
            !mainNav.contains(e.target) && 
            !hamburger.contains(e.target)) {
            mainNav.classList.remove('open');
            hamburger.classList.remove('active');
        }
    });
});

// Backup initialization - run after a short delay
setTimeout(function() {
    const hamburger = document.querySelector('.hamburger');
    const mainNav = document.getElementById('main-nav');
    
    if (hamburger && mainNav) {
        hamburger.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            hamburger.classList.toggle('active');
            mainNav.classList.toggle('open');
            console.log('Hamburger clicked (backup handler)');
        };
        
        console.log('Hamburger menu backup initialization complete');
    }
}, 1000);
