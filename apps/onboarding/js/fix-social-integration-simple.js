/**
 * SOCIAL INTEGRATION - SIMPLE FIX
 * This script enhances the existing social integration functionality
 * without trying to replace the existing handlers
 */

console.log("SIMPLE FIX: Social integration simple fix loaded");

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  console.log("SIMPLE FIX: DOM loaded, setting up enhancements");
  
  // Set up a MutationObserver to detect when the social modal is shown
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
        const socialModal = document.getElementById('social-modal');
        if (socialModal && socialModal.style.display === 'block') {
          console.log("SIMPLE FIX: Social modal opened, enhancing functionality");
          enhanceSocialModal();
        }
      }
    });
  });
  
  // Start observing the social modal if it exists
  const socialModal = document.getElementById('social-modal');
  if (socialModal) {
    observer.observe(socialModal, { attributes: true });
    console.log("SIMPLE FIX: Observer set up for social modal");
    
    // If the modal is already open, enhance it immediately
    if (socialModal.style.display === 'block') {
      console.log("SIMPLE FIX: Social modal already open, enhancing now");
      enhanceSocialModal();
    }
  }
  
  // Function to enhance the social modal functionality
  function enhanceSocialModal() {
    console.log("SIMPLE FIX: Enhancing social modal");
    
    // Make sure the original functions are defined
    window.showExistingAssetsFlow = window.showExistingAssetsFlow || function() {
      console.log("SIMPLE FIX: Using fallback showExistingAssetsFlow");
      const existingAssetsFlow = document.getElementById('existing-assets-flow');
      const setupGuide = document.getElementById('setup-guide');
      
      if (existingAssetsFlow) existingAssetsFlow.style.display = 'block';
      if (setupGuide) setupGuide.style.display = 'none';
    };
    
    window.showSetupGuide = window.showSetupGuide || function() {
      console.log("SIMPLE FIX: Using fallback showSetupGuide");
      const existingAssetsFlow = document.getElementById('existing-assets-flow');
      const setupGuide = document.getElementById('setup-guide');
      
      if (existingAssetsFlow) existingAssetsFlow.style.display = 'none';
      if (setupGuide) setupGuide.style.display = 'block';
    };
    
    // Find the Yes button
    const yesOptionDiv = document.querySelector('div.p-4.border.rounded-lg.hover\\:bg-gray-50.cursor-pointer[onclick*="showExistingAssetsFlow"]');
    if (yesOptionDiv) {
      console.log("SIMPLE FIX: Found Yes button, enhancing");
      
      // Preserve the original onclick but add our own functionality
      const originalOnclick = yesOptionDiv.getAttribute('onclick');
      yesOptionDiv.setAttribute('onclick', '');
      
      yesOptionDiv.addEventListener('click', function(e) {
        console.log("SIMPLE FIX: Yes button clicked, executing original function and our enhancement");
        
        // Call the original function
        if (window.showExistingAssetsFlow) {
          window.showExistingAssetsFlow();
        }
        
        // Add our own enhancement
        const existingAssetsFlow = document.getElementById('existing-assets-flow');
        if (existingAssetsFlow) {
          console.log("SIMPLE FIX: Ensuring existing assets flow is visible");
          existingAssetsFlow.style.display = 'block';
          existingAssetsFlow.style.visibility = 'visible';
          existingAssetsFlow.classList.remove('hidden');
          
          // Force redraw
          existingAssetsFlow.style.opacity = '0.99';
          setTimeout(function() {
            existingAssetsFlow.style.opacity = '1';
          }, 10);
        }
      });
    } else {
      console.log("SIMPLE FIX: Yes button not found");
    }
    
    // Find the No button
    const noOptionDiv = document.querySelector('div.p-4.border.rounded-lg.hover\\:bg-gray-50.cursor-pointer[onclick*="showSetupGuide"]');
    if (noOptionDiv) {
      console.log("SIMPLE FIX: Found No button, enhancing");
      
      // Preserve the original onclick but add our own functionality
      const originalOnclick = noOptionDiv.getAttribute('onclick');
      noOptionDiv.setAttribute('onclick', '');
      
      noOptionDiv.addEventListener('click', function(e) {
        console.log("SIMPLE FIX: No button clicked, executing original function and our enhancement");
        
        // Call the original function
        if (window.showSetupGuide) {
          window.showSetupGuide();
        }
        
        // Add our own enhancement
        const setupGuide = document.getElementById('setup-guide');
        if (setupGuide) {
          console.log("SIMPLE FIX: Ensuring setup guide is visible");
          setupGuide.style.display = 'block';
          setupGuide.style.visibility = 'visible';
          setupGuide.classList.remove('hidden');
          
          // Force redraw
          setupGuide.style.opacity = '0.99';
          setTimeout(function() {
            setupGuide.style.opacity = '1';
          }, 10);
        }
      });
    } else {
      console.log("SIMPLE FIX: No button not found");
    }
    
    // Create global debug functions
    window.debugExistingAssets = function() {
      console.log("SIMPLE FIX: Debug - Showing existing assets flow");
      const existingAssetsFlow = document.getElementById('existing-assets-flow');
      const setupGuide = document.getElementById('setup-guide');
      
      if (existingAssetsFlow) {
        console.log("SIMPLE FIX: Found existing assets flow:", existingAssetsFlow);
        existingAssetsFlow.style.display = 'block';
        existingAssetsFlow.style.visibility = 'visible';
        existingAssetsFlow.classList.remove('hidden');
      } else {
        console.log("SIMPLE FIX: Existing assets flow not found");
      }
      
      if (setupGuide) {
        console.log("SIMPLE FIX: Found setup guide:", setupGuide);
        setupGuide.style.display = 'none';
      }
    };
    
    window.debugSetupGuide = function() {
      console.log("SIMPLE FIX: Debug - Showing setup guide");
      const existingAssetsFlow = document.getElementById('existing-assets-flow');
      const setupGuide = document.getElementById('setup-guide');
      
      if (setupGuide) {
        console.log("SIMPLE FIX: Found setup guide:", setupGuide);
        setupGuide.style.display = 'block';
        setupGuide.style.visibility = 'visible';
        setupGuide.classList.remove('hidden');
      } else {
        console.log("SIMPLE FIX: Setup guide not found");
      }
      
      if (existingAssetsFlow) {
        console.log("SIMPLE FIX: Found existing assets flow:", existingAssetsFlow);
        existingAssetsFlow.style.display = 'none';
      }
    };
    
    console.log("SIMPLE FIX: Social modal enhancement complete. Debug functions added: window.debugExistingAssets() and window.debugSetupGuide()");
  }
});

// Check if DOM is already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  console.log("SIMPLE FIX: DOM already loaded, triggering DOMContentLoaded event");
  const event = new Event('DOMContentLoaded');
  document.dispatchEvent(event);
} 