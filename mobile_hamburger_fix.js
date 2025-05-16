// Mobile hamburger menu fix
(function() {
    // Function to create and insert hamburger menu if it doesn't exist
    function ensureHamburgerExists() {
        // Check if hamburger already exists
        var existingHamburger = document.querySelector('.hamburger');
        
        // If hamburger doesn't exist, create it
        if (!existingHamburger) {
            console.log('Hamburger menu not found - creating one');
            
            // Find the navigation container
            var nav = document.querySelector('nav[aria-label="Main Navigation"]');
            
            if (nav) {
                // Create hamburger button
                var hamburger = document.createElement('button');
                hamburger.className = 'hamburger';
                hamburger.setAttribute('aria-label', 'Open navigation');
                hamburger.setAttribute('aria-expanded', 'false');
                hamburger.setAttribute('aria-controls', 'main-nav');
                
                // Create hamburger icon spans
                for (var i = 0; i < 3; i++) {
                    var span = document.createElement('span');
                    hamburger.appendChild(span);
                }
                
                // Add click event
                hamburger.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    this.classList.toggle('active');
                    var mainNav = document.getElementById('main-nav');
                    if (mainNav) {
                        mainNav.classList.toggle('open');
                    }
                    return false;
                };
                
                // Insert hamburger at the beginning of nav
                nav.insertBefore(hamburger, nav.firstChild);
                console.log('Hamburger menu created and inserted');
            } else {
                console.error('Navigation container not found');
            }
        } else {
            console.log('Hamburger menu already exists');
        }
    }
    
    // Run immediately
    ensureHamburgerExists();
    
    // Also run after DOM is loaded
    document.addEventListener('DOMContentLoaded', ensureHamburgerExists);
    
    // And after window load
    window.addEventListener('load', ensureHamburgerExists);
    
    // Also run periodically to ensure it's always there
    setInterval(ensureHamburgerExists, 1000);
})();
