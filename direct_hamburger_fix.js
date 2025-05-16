// Direct hamburger fix - to be included at the end of the body
document.addEventListener('DOMContentLoaded', function() {
    // Direct fix for hamburger menu
    var hamburger = document.querySelector('.hamburger');
    var mainNav = document.getElementById('main-nav');
    
    if (hamburger && mainNav) {
        // Replace the hamburger button with a new one that has the onclick attribute
        var newHamburger = hamburger.cloneNode(true);
        newHamburger.setAttribute('onclick', "this.classList.toggle('active'); document.getElementById('main-nav').classList.toggle('open'); return false;");
        hamburger.parentNode.replaceChild(newHamburger, hamburger);
        
        // Also add the event listener
        newHamburger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.toggle('active');
            mainNav.classList.toggle('open');
            return false;
        });
        
        console.log('Hamburger button replaced with direct onclick version');
    }
});
