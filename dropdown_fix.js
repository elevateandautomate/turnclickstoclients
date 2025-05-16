// Immediate fix for dropdown menu
document.addEventListener('DOMContentLoaded', function() {
    // Fix for dropdown menu
    const dropdownParent = document.querySelector('.dropdown-parent');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (dropdownParent && dropdownMenu) {
        // Make dropdown stay visible on hover
        dropdownParent.addEventListener('mouseenter', function() {
            dropdownMenu.style.display = 'block';
        });
        
        dropdownMenu.addEventListener('mouseenter', function() {
            this.style.display = 'block';
        });
        
        // Add a delay before hiding
        dropdownParent.addEventListener('mouseleave', function() {
            setTimeout(function() {
                if (!dropdownMenu.matches(':hover')) {
                    dropdownMenu.style.display = 'none';
                }
            }, 500);
        });
        
        dropdownMenu.addEventListener('mouseleave', function() {
            setTimeout(function() {
                if (!dropdownParent.matches(':hover')) {
                    dropdownMenu.style.display = 'none';
                }
            }, 500);
        });
    }
    
    // Fix for GET STARTED button
    const ctaButtons = document.querySelectorAll('.cta-button, .nav-cta, [href="quiz-start.html"]');
    ctaButtons.forEach(function(button) {
        button.style.color = 'white';
    });
});
