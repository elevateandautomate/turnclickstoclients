// Simple Mobile Navigation Fix

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the hamburger button and navigation menu
    var hamburger = document.querySelector('.hamburger');
    var mainNav = document.getElementById('main-nav');
    
    // Add click event to hamburger button
    if (hamburger && mainNav) {
        hamburger.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Toggle the open class on the navigation menu
            mainNav.classList.toggle('open');
            
            // Update aria-expanded attribute
            var isExpanded = mainNav.classList.contains('open');
            hamburger.setAttribute('aria-expanded', isExpanded);
        });
        
        // Close navigation when clicking on a link
        var navLinks = mainNav.querySelectorAll('a');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                // Only close on mobile
                if (window.innerWidth <= 900) {
                    mainNav.classList.remove('open');
                    hamburger.setAttribute('aria-expanded', 'false');
                }
            });
        });
        
        // Handle dropdown menus on mobile
        var dropdownParents = document.querySelectorAll('.dropdown-parent');
        dropdownParents.forEach(function(parent) {
            var link = parent.querySelector('a');
            
            link.addEventListener('click', function(e) {
                // Only handle on mobile
                if (window.innerWidth <= 900) {
                    e.preventDefault();
                    
                    // Toggle the open class on the parent
                    parent.classList.toggle('open');
                    
                    // Close other dropdowns
                    dropdownParents.forEach(function(otherParent) {
                        if (otherParent !== parent) {
                            otherParent.classList.remove('open');
                        }
                    });
                }
            });
        });
    }
});
