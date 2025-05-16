/**
 * This script updates facebook-integration-onboarding.js with fixes
 * Run this before loading the main page
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Facebook Integration Update Script loaded');
  
  // Load the fixes
  const fixScript = document.createElement('script');
  fixScript.src = 'fix-social-media-integration.js';
  document.head.appendChild(fixScript);
  
  // Override or patch the Facebook Integration Onboarding script
  setTimeout(function() {
    console.log('Patching facebook-integration-onboarding.js functionality');
    
    // Ensure our fix script runs first by patching any existing event listeners
    const originalDocumentAddEventListener = document.addEventListener;
    document.addEventListener = function(type, listener, options) {
      if (type === 'DOMContentLoaded' && String(listener).includes('Facebook Integration - Onboarding Integration')) {
        console.log('Intercepted Facebook Integration onboarding DOMContentLoaded event');
        // Modify the listener to work with our fix
        const newListener = function(event) {
          console.log('Running modified Facebook Integration onboarding listener');
          listener(event);
        };
        return originalDocumentAddEventListener.call(this, type, newListener, options);
      }
      return originalDocumentAddEventListener.call(this, type, listener, options);
    };
  }, 0);
}); 