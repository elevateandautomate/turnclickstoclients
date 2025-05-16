document.addEventListener('DOMContentLoaded', function() {
    // Handle hamburger menu toggle
    const hamburger = document.querySelector('.hamburger');
    const mainNav = document.getElementById('main-nav');
    
    if (hamburger && mainNav) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            mainNav.classList.toggle('open');
        });
    }
    
    // Fix for dropdown menu disappearing
    const dropdownParents = document.querySelectorAll('.dropdown-parent');
    
    dropdownParents.forEach(function(parent) {
        const link = parent.querySelector('a');
        const dropdown = parent.querySelector('.dropdown-menu');
        
        if (link && dropdown) {
            // Add click event for mobile
            link.addEventListener('click', function(e) {
                if (window.innerWidth <= 900) {
                    e.preventDefault();
                    parent.classList.toggle('open');
                }
            });
            
            // Fix for dropdown disappearing on desktop
            let timeoutId;
            
            // When mouse enters the dropdown parent
            parent.addEventListener('mouseenter', function() {
                clearTimeout(timeoutId);
                dropdownParents.forEach(p => {
                    if (p !== parent) p.classList.remove('active');
                });
                parent.classList.add('active');
            });
            
            // When mouse leaves the dropdown parent
            parent.addEventListener('mouseleave', function() {
                timeoutId = setTimeout(function() {
                    parent.classList.remove('active');
                }, 300); // Delay before hiding
            });
            
            // When mouse enters the dropdown menu
            dropdown.addEventListener('mouseenter', function() {
                clearTimeout(timeoutId);
            });
            
            // When mouse leaves the dropdown menu
            dropdown.addEventListener('mouseleave', function() {
                timeoutId = setTimeout(function() {
                    parent.classList.remove('active');
                }, 300); // Delay before hiding
            });
        }
    });
    
    // Fix for GET STARTED button color
    const ctaButtons = document.querySelectorAll('.cta-button, .nav-cta, [href="quiz-start.html"], .get-started');
    ctaButtons.forEach(function(button) {
        button.style.color = 'white';
    });
});
