/**
 * SOCIAL MEDIA INTEGRATION DEBUG FIX
 * 
 * This script fixes issues with the social media integration modal
 * by ensuring all required functions are properly defined and working.
 */

console.log('[SOCIAL-FIX] Loading social media integration fix...');

// Check if openModal function exists and patch it if needed
if (!window.openModal) {
  console.log('[SOCIAL-FIX] No openModal function found, creating one');
  window.openModal = function(modalId) {
    console.log(`[SOCIAL-FIX] openModal called for ${modalId}`);
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = 'block';
    } else {
      console.error(`[SOCIAL-FIX] Modal with ID ${modalId} not found`);
    }
  };
}

// Ensure showSocialModal is defined properly
window.showSocialModal = function() {
  console.log('[SOCIAL-FIX] showSocialModal called');
  
  // Check if our direct integration is loaded
  if (typeof connectFacebookAssets === 'function') {
    console.log('[SOCIAL-FIX] Using Facebook direct integration');
    connectFacebookAssets();
    return;
  }
  
  // Fallback to original behavior
  console.log('[SOCIAL-FIX] Falling back to original modal behavior');
  openModal('social-modal');
};

// Ensure the facebook-seamless-integration.js script is loaded
function ensureScriptLoaded(scriptSrc, callback) {
  // Check if script is already loaded
  const existingScript = document.querySelector(`script[src="${scriptSrc}"]`);
  if (existingScript) {
    console.log(`[SOCIAL-FIX] Script ${scriptSrc} is already loaded`);
    if (callback) callback();
    return;
  }
  
  // Load the script
  console.log(`[SOCIAL-FIX] Loading script: ${scriptSrc}`);
  const script = document.createElement('script');
  script.src = scriptSrc;
  script.onload = function() {
    console.log(`[SOCIAL-FIX] Script ${scriptSrc} loaded successfully`);
    if (callback) callback();
  };
  script.onerror = function() {
    console.error(`[SOCIAL-FIX] Failed to load script: ${scriptSrc}`);
  };
  document.body.appendChild(script);
}

// Ensure Font Awesome is loaded for icons
function ensureFontAwesomeLoaded() {
  if (!document.querySelector('link[href*="fontawesome"]')) {
    console.log('[SOCIAL-FIX] Loading Font Awesome');
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(link);
  }
}

// Debug console
document.addEventListener('DOMContentLoaded', function() {
  console.log('[SOCIAL-FIX] DOM loaded. Checking social integration elements...');
  
  // Check for the connect button
  const connectButtons = document.querySelectorAll('button[onclick*="showSocialModal"]');
  console.log(`[SOCIAL-FIX] Found ${connectButtons.length} social media connect buttons`);
  
  // Check for the social modal
  const socialModal = document.getElementById('social-modal');
  if (socialModal) {
    console.log('[SOCIAL-FIX] Social modal found in the DOM');
  } else {
    console.error('[SOCIAL-FIX] Social modal not found in the DOM');
  }
  
  // Add direct event listeners to the buttons
  connectButtons.forEach((button, index) => {
    console.log(`[SOCIAL-FIX] Adding direct event listener to button ${index + 1}`);
    
    // Remove the onclick attribute but store its value
    const originalOnclick = button.getAttribute('onclick');
    button.removeAttribute('onclick');
    
    // Add a direct event listener
    button.addEventListener('click', function(e) {
      e.preventDefault();
      console.log(`[SOCIAL-FIX] Social connect button ${index + 1} clicked`);
      console.log(`[SOCIAL-FIX] Original onclick was: ${originalOnclick}`);
      
      if (typeof connectFacebookAssets === 'function') {
        console.log('[SOCIAL-FIX] Calling connectFacebookAssets() directly');
        connectFacebookAssets();
      } else {
        console.log('[SOCIAL-FIX] connectFacebookAssets not found, attempting to load integration script');
        ensureScriptLoaded('facebook-seamless-integration.js', function() {
          if (typeof connectFacebookAssets === 'function') {
            connectFacebookAssets();
          } else {
            console.error('[SOCIAL-FIX] connectFacebookAssets still not defined after loading script');
            // Fall back to original behavior
            if (typeof showSocialModal === 'function') {
              showSocialModal();
            } else if (typeof openModal === 'function') {
              openModal('social-modal');
            }
          }
        });
      }
    });
  });
  
  // Ensure Font Awesome is loaded
  ensureFontAwesomeLoaded();
  
  // Ensure Facebook integration script is loaded
  ensureScriptLoaded('facebook-seamless-integration.js');
  
  console.log('[SOCIAL-FIX] Social media integration fix initialization complete');
});

// Override closeModal function if it exists
const originalCloseModal = window.closeModal || function() {};
window.closeModal = function(modalId) {
  console.log(`[SOCIAL-FIX] closeModal called for ${modalId}`);
  
  // Call original function
  originalCloseModal(modalId);
  
  // Additionally, check for our custom modal
  if (modalId === 'social-modal') {
    const fbModal = document.getElementById('facebook-connection-modal');
    if (fbModal) {
      fbModal.style.display = 'none';
    }
  }
};

// Export functions for debugging
window.socialFixDebug = {
  ensureScriptLoaded,
  ensureFontAwesomeLoaded,
  checkElements: function() {
    const connectButtons = document.querySelectorAll('button[onclick*="showSocialModal"]');
    const socialModal = document.getElementById('social-modal');
    const fbModal = document.getElementById('facebook-connection-modal');
    
    return {
      connectButtons: connectButtons.length,
      socialModalExists: !!socialModal,
      fbModalExists: !!fbModal,
      connectFacebookAssetsExists: typeof connectFacebookAssets === 'function',
      showSocialModalExists: typeof showSocialModal === 'function',
      openModalExists: typeof openModal === 'function'
    };
  }
};

console.log('[SOCIAL-FIX] Social media fix script loaded successfully'); 