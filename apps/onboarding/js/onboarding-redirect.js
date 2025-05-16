// Script to handle "Continue to Onboarding" button redirection
document.addEventListener('DOMContentLoaded', function() {
  // Find all "Continue to Onboarding" buttons by text content
  function setupContinueButtons() {
    // Look for buttons that might be the "Continue to Onboarding" button
    const allButtons = document.querySelectorAll('button, a.button, .btn, a.btn, [class*="btn"]');
    
    allButtons.forEach(button => {
      // Check if the button text includes "Continue to Onboarding" or similar phrases
      const buttonText = button.textContent.toLowerCase().trim();
      if (buttonText.includes('continue to onboarding') || 
          buttonText.includes('go to onboarding') ||
          buttonText.includes('start onboarding') ||
          (buttonText.includes('continue') && buttonText.includes('onboarding'))) {
        
        console.log('Found "Continue to Onboarding" button:', button);
        
        // Remove any existing click handlers by cloning the node
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add our click handler
        newButton.addEventListener('click', function(e) {
          e.preventDefault();
          
          console.log('Continue to Onboarding clicked - redirecting to onboarding steps');
          
          // Redirect to the onboarding steps page
          // If we're already on the main page, we just need to show the correct section
          const dashboardSection = document.getElementById('dashboard-section');
          if (dashboardSection) {
            // Hide all sections
            document.querySelectorAll('.main-section').forEach(section => {
              section.style.display = 'none';
            });
            
            // Show dashboard section
            dashboardSection.style.display = 'block';
            
            // Look for onboarding steps container or sections within dashboard
            const onboardingSteps = document.querySelector('.onboarding-steps, .steps-container, #onboarding-steps');
            if (onboardingSteps) {
              onboardingSteps.style.display = 'block';
              
              // If there's an onboarding card or container, show it
              const onboardingCards = document.querySelectorAll('.onboarding-card, .step-card');
              onboardingCards.forEach(card => {
                card.style.display = 'block';
              });
            }
            
            // Scroll to the onboarding section
            window.scrollTo({
              top: 0,
              behavior: 'smooth'
            });
          } else {
            // If we're on a different page, redirect to the main page with onboarding section
            window.location.href = 'workingonboarding.html';
          }
        });
      }
    });
  }
  
  // Initial setup
  setupContinueButtons();
  
  // Also run setup when content changes (for dynamically loaded buttons)
  const observer = new MutationObserver(function(mutations) {
    setupContinueButtons();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
}); 