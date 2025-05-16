// Persistent fix for GET STARTED button text color
document.addEventListener('DOMContentLoaded', function() {
    // Initial fix
    fixGetStartedButton();
    
    // Set up a recurring check to ensure the button stays white
    setInterval(fixGetStartedButton, 100); // Check every 100ms
});

function fixGetStartedButton() {
    // Target all possible GET STARTED button selectors
    var buttons = document.querySelectorAll('.cta-button, .nav-cta, a[href="quiz-start.html"], .get-started, [class*="cta"], [class*="get-started"]');
    
    buttons.forEach(function(button) {
        // Force white color with !important
        button.setAttribute('style', button.getAttribute('style') + '; color: white !important;');
        
        // Also set the color property directly
        button.style.setProperty('color', 'white', 'important');
    });
    
    // Specifically target the navigation GET STARTED button
    var navCta = document.querySelector('nav a.cta-button.nav-cta');
    if (navCta) {
        navCta.setAttribute('style', navCta.getAttribute('style') + '; color: white !important;');
        navCta.style.setProperty('color', 'white', 'important');
    }
}
