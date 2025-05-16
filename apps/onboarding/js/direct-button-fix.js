/**
 * DIRECT BUTTON FIX
 * This script directly replaces the onclick handlers on the buttons
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log("DIRECT BUTTON FIX: Script loaded, waiting for social modal buttons...");
  
  // Keep checking for the buttons until we find them
  let checkInterval = setInterval(function() {
    // Look for the specific buttons in the social modal
    const socialModal = document.getElementById('social-modal');
    if (!socialModal) {
      console.log("DIRECT BUTTON FIX: Social modal not found yet, waiting...");
      return;
    }
    
    // Try different ways to find the buttons
    const yesButton = findYesButton();
    const noButton = findNoButton();
    
    if (yesButton || noButton) {
      console.log("DIRECT BUTTON FIX: Found buttons, applying fix!");
      
      if (yesButton) {
        console.log("DIRECT BUTTON FIX: Replacing Yes button handler");
        // Remove the onclick attribute
        yesButton.removeAttribute('onclick');
        
        // Add our own click handler
        yesButton.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log("DIRECT BUTTON FIX: Yes button clicked!");
          
          // Find the elements directly
          const existingAssetsFlow = findElement('existing-assets-flow') || 
                                    findElementByText('existing assets') ||
                                    document.querySelector('.assets-flow');
                                    
          const setupGuide = findElement('setup-guide') || 
                           findElementByText('setup guide') ||
                           document.querySelector('.setup-guide');
          
          if (existingAssetsFlow) {
            console.log("DIRECT BUTTON FIX: Showing existing assets flow");
            existingAssetsFlow.style.display = 'block';
            existingAssetsFlow.style.visibility = 'visible';
            existingAssetsFlow.style.opacity = '1';
            existingAssetsFlow.classList.remove('hidden');
          } else {
            console.warn("DIRECT BUTTON FIX: Could not find existing assets flow element");
          }
          
          if (setupGuide) {
            console.log("DIRECT BUTTON FIX: Hiding setup guide");
            setupGuide.style.display = 'none';
            setupGuide.style.visibility = 'hidden';
            setupGuide.style.opacity = '0';
            setupGuide.classList.add('hidden');
          } else {
            console.warn("DIRECT BUTTON FIX: Could not find setup guide element");
          }
          
          // Force redraw
          document.body.style.zoom = '99.9%';
          setTimeout(function() {
            document.body.style.zoom = '100%';
          }, 10);
          
          return false;
        });
      }
      
      if (noButton) {
        console.log("DIRECT BUTTON FIX: Replacing No button handler");
        // Remove the onclick attribute
        noButton.removeAttribute('onclick');
        
        // Add our own click handler
        noButton.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log("DIRECT BUTTON FIX: No button clicked!");
          
          // Find the elements directly
          const setupGuide = findElement('setup-guide') || 
                           findElementByText('setup guide') ||
                           document.querySelector('.setup-guide');
                           
          const existingAssetsFlow = findElement('existing-assets-flow') || 
                                    findElementByText('existing assets') ||
                                    document.querySelector('.assets-flow');
          
          if (setupGuide) {
            console.log("DIRECT BUTTON FIX: Showing setup guide");
            setupGuide.style.display = 'block';
            setupGuide.style.visibility = 'visible';
            setupGuide.style.opacity = '1';
            setupGuide.classList.remove('hidden');
          } else {
            console.warn("DIRECT BUTTON FIX: Could not find setup guide element");
          }
          
          if (existingAssetsFlow) {
            console.log("DIRECT BUTTON FIX: Hiding existing assets flow");
            existingAssetsFlow.style.display = 'none';
            existingAssetsFlow.style.visibility = 'hidden';
            existingAssetsFlow.style.opacity = '0';
            existingAssetsFlow.classList.add('hidden');
          } else {
            console.warn("DIRECT BUTTON FIX: Could not find existing assets flow element");
          }
          
          // Force redraw
          document.body.style.zoom = '99.9%';
          setTimeout(function() {
            document.body.style.zoom = '100%';
          }, 10);
          
          return false;
        });
      }
      
      // Stop checking once we've found the buttons
      clearInterval(checkInterval);
      console.log("DIRECT BUTTON FIX: Direct button fix applied successfully!");
    }
  }, 500);  // Check every 500ms
  
  // Helper function to find the Yes button
  function findYesButton() {
    const possibleButtons = [
      document.querySelector('[onclick*="showExistingAssetsFlow"]'),
      document.querySelector('div[onclick*="Assets"]'),
      Array.from(document.querySelectorAll('div')).find(el => 
        el.textContent.includes('Yes') && el.textContent.includes('existing assets')
      ),
      document.querySelector('.social-modal-yes-button')
    ];
    
    return possibleButtons.find(btn => btn !== null);
  }
  
  // Helper function to find the No button
  function findNoButton() {
    const possibleButtons = [
      document.querySelector('[onclick*="showSetupGuide"]'),
      document.querySelector('div[onclick*="Guide"]'),
      Array.from(document.querySelectorAll('div')).find(el => 
        el.textContent.includes('No') && el.textContent.includes('set them up')
      ),
      document.querySelector('.social-modal-no-button')
    ];
    
    return possibleButtons.find(btn => btn !== null);
  }
  
  // Helper function to find an element by ID
  function findElement(id) {
    return document.getElementById(id);
  }
  
  // Helper function to find an element by contained text
  function findElementByText(text) {
    const elements = Array.from(document.querySelectorAll('div, section, article'));
    return elements.find(el => 
      el.textContent.toLowerCase().includes(text.toLowerCase())
    );
  }
});

// Also check immediately in case DOM is already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  console.log("DIRECT BUTTON FIX: DOM already loaded, executing immediately");
  const event = new Event('DOMContentLoaded');
  document.dispatchEvent(event);
} 