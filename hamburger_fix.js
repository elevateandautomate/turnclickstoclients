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
