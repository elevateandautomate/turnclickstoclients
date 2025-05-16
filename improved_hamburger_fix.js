// Improved Hamburger Menu Fix JavaScript

document.addEventListener('DOMContentLoaded', function() {
  // Fix for hamburger menu toggle
  const hamburgerToggle = document.querySelector('.navbar-toggler');
  const navbarCollapse = document.querySelector('.navbar-collapse');
  
  if (hamburgerToggle && navbarCollapse) {
    // Ensure the toggle button works
    hamburgerToggle.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      // Toggle the 'show' class on navbar-collapse
      navbarCollapse.classList.toggle('show');
      
      // Toggle aria-expanded attribute
      const expanded = hamburgerToggle.getAttribute('aria-expanded') === 'true' || false;
      hamburgerToggle.setAttribute('aria-expanded', !expanded);
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
      if (!navbarCollapse.contains(e.target) && !hamburgerToggle.contains(e.target)) {
        navbarCollapse.classList.remove('show');
        hamburgerToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }
  
  // Fix for dropdown toggles in mobile navigation
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
  
  dropdownToggles.forEach(function(toggle) {
    toggle.addEventListener('click', function(e) {
      // Only handle dropdown toggle on mobile
      if (window.innerWidth < 992) {
        e.preventDefault();
        e.stopPropagation();
        
        // Get the parent dropdown element
        const dropdown = toggle.closest('.dropdown');
        
        // Get the dropdown menu
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        
        // Toggle the 'show' class on dropdown and dropdown-menu
        dropdown.classList.toggle('show');
        if (dropdownMenu) {
          dropdownMenu.classList.toggle('show');
        }
        
        // Close other open dropdowns
        document.querySelectorAll('.dropdown.show').forEach(function(openDropdown) {
          if (openDropdown !== dropdown) {
            openDropdown.classList.remove('show');
            const openDropdownMenu = openDropdown.querySelector('.dropdown-menu');
            if (openDropdownMenu) {
              openDropdownMenu.classList.remove('show');
            }
          }
        });
      }
    });
  });
  
  // Fix for "Get Started" button in mobile navigation
  const getStartedBtn = document.querySelector('.navbar-nav .get-started-btn, .navbar-nav .btn-primary');
  if (getStartedBtn) {
    // Add classes to ensure proper styling
    getStartedBtn.classList.add('mobile-centered-btn');
  }
  
  // Handle window resize to reset menu state
  window.addEventListener('resize', function() {
    if (window.innerWidth >= 992) {
      // Reset mobile menu when switching to desktop view
      if (navbarCollapse && navbarCollapse.classList.contains('show')) {
        navbarCollapse.classList.remove('show');
        if (hamburgerToggle) {
          hamburgerToggle.setAttribute('aria-expanded', 'false');
        }
      }
      
      // Reset dropdowns
      document.querySelectorAll('.dropdown.show, .dropdown-menu.show').forEach(function(el) {
        el.classList.remove('show');
      });
    }
  });
  
  // Fix for any existing Bootstrap initialization
  if (typeof bootstrap !== 'undefined') {
    // Initialize any Bootstrap components if needed
    const dropdowns = document.querySelectorAll('.dropdown-toggle');
    dropdowns.forEach(function(dropdown) {
      new bootstrap.Dropdown(dropdown);
    });
  }
});
