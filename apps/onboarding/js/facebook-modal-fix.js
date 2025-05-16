/**
 * FACEBOOK MODAL VISIBILITY FIX
 * 
 * This script ensures the Facebook integration modal appears correctly
 * by forcibly overriding display settings and z-index to ensure visibility.
 */

console.log('[FB-MODAL-FIX] Loading Facebook modal visibility fix...');

// Store original functions if they exist
const originalConnectFacebookAssets = window.connectFacebookAssets || function() {};

// Override the connectFacebookAssets function to ensure the modal is visible
window.connectFacebookAssets = function() {
  console.log('[FB-MODAL-FIX] Enhanced connectFacebookAssets called');
  
  // Call the original function first
  originalConnectFacebookAssets();
  
  // Then ensure the modal is created if it doesn't exist
  setTimeout(function() {
    let modal = document.getElementById('facebook-connection-modal');
    
    if (!modal) {
      console.log('[FB-MODAL-FIX] Modal not found, creating it');
      
      // Create modal container
      modal = document.createElement('div');
      modal.id = 'facebook-connection-modal';
      modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50';
      modal.style.zIndex = '9999';
      modal.style.display = 'block';
      
      // Create modal content
      const modalContent = document.createElement('div');
      modalContent.className = 'relative top-10 mx-auto p-5 border w-3/4 max-w-4xl shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto';
      
      // Create header
      const header = document.createElement('div');
      header.className = 'sticky top-0 bg-white z-10 pb-4 border-b mb-4';
      header.innerHTML = `
        <div class="flex justify-between items-center">
          <h3 class="text-xl font-bold text-gray-800">Connect Your Social Media Accounts</h3>
          <button onclick="closeConnectionModal()" class="text-gray-400 hover:text-gray-500">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-100">
          <p class="text-sm text-yellow-800">
            <i class="fas fa-shield-alt mr-2"></i>
            Your account security is our priority. We only request necessary permissions to manage your campaigns effectively. Most questions can be answered by following the steps provided. If you still need assistance, <a href="#" onclick="showHelpModal(event)" class="text-blue-700 hover:underline">request help</a>.
          </p>
        </div>
      `;
      
      // Create content area
      const contentArea = document.createElement('div');
      contentArea.id = 'facebook-connection-content';
      contentArea.className = 'space-y-6';
      contentArea.innerHTML = `
        <div class="text-center mb-4">
          <i class="fab fa-facebook text-[#1877F2] fa-3x mb-3"></i>
          <h4 class="text-xl font-bold text-gray-800">Connect Your Social Media Accounts</h4>
          <p>Follow these steps to connect your Facebook ad accounts, pages, and Instagram profiles.</p>
        </div>
        
        <div class="px-2">
          <h5 class="font-medium text-gray-800 mt-4 mb-3">Do you have existing Meta business assets?</h5>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer" onclick="showExistingBusinessFlow()">
              <div class="flex items-center mb-2">
                <i class="fas fa-check-circle text-green-600 mr-2"></i>
                <h5 class="font-medium text-gray-800">Yes, I have existing assets</h5>
              </div>
              <p class="text-sm text-gray-600">I already have a Meta Business Manager, ad account, and business page set up.</p>
            </div>
            <div class="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer" onclick="showNewBusinessFlow()">
              <div class="flex items-center mb-2">
                <i class="fas fa-plus-circle text-blue-600 mr-2"></i>
                <h5 class="font-medium text-gray-800">No, I need to set them up</h5>
              </div>
              <p class="text-sm text-gray-600">I need help creating my Meta Business Manager, ad account, and business page.</p>
            </div>
          </div>
          
          <div class="mt-6 text-center">
            <button class="py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" onclick="closeConnectionModal()">Cancel</button>
          </div>
        </div>
      `;
      
      // Assemble modal
      modalContent.appendChild(header);
      modalContent.appendChild(contentArea);
      modal.appendChild(modalContent);
      document.body.appendChild(modal);
      
      // Define helper functions if they don't exist
      if (typeof window.closeConnectionModal !== 'function') {
        window.closeConnectionModal = function() {
          console.log('[FB-MODAL-FIX] Closing connection modal');
          const modal = document.getElementById('facebook-connection-modal');
          if (modal) {
            modal.style.display = 'none';
          }
        };
      }
      
      if (typeof window.showExistingBusinessFlow !== 'function') {
        window.showExistingBusinessFlow = function() {
          console.log('[FB-MODAL-FIX] Showing existing business flow');
          const contentArea = document.getElementById('facebook-connection-content');
          if (contentArea) {
            contentArea.innerHTML = `
              <div class="text-center mb-3">
                <h4 class="text-xl font-bold text-gray-800">Connect Your Business Manager</h4>
                <p class="text-gray-600">Follow these steps to connect your existing Business Manager</p>
              </div>
              
              <div class="steps-container space-y-6">
                <div class="step-item pb-3 border-bottom">
                  <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">1</span> Go to Business Settings</h5>
                  <p class="text-gray-600 mb-3">Open your Facebook Business Manager settings by clicking the button below:</p>
                  <a href="https://business.facebook.com/settings" target="_blank" class="block w-full py-2 px-4 bg-blue-600 text-white text-center rounded hover:bg-blue-700">
                    <i class="fas fa-external-link-alt mr-2"></i>Open Business Settings
                  </a>
                </div>
                
                <div class="step-item pb-3 border-bottom">
                  <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">2</span> Add a Partner</h5>
                  <p class="text-gray-600">From the left menu, select <strong>Partners</strong> > <strong>Add</strong> > <strong>Add a Partner</strong></p>
                  <p class="text-gray-600">Enter our Business ID: <strong class="text-blue-600">1234567890</strong></p>
                </div>
                
                <div class="step-item">
                  <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">3</span> Confirm Connection</h5>
                  <p class="text-gray-600 mb-3">After you've completed these steps, click the button below to confirm:</p>
                  <button class="block w-full py-2 px-4 bg-green-600 text-white text-center rounded hover:bg-green-700" onclick="confirmManualConnection()">
                    <i class="fas fa-check mr-2"></i>I've Connected My Assets
                  </button>
                </div>
              </div>
              
              <div class="text-center mt-6 space-x-2">
                <button class="py-2 px-4 border border-blue-600 text-blue-600 rounded hover:bg-blue-50" onclick="connectFacebookAssets()">
                  <i class="fas fa-arrow-left mr-2"></i>Back
                </button>
                <button class="py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" onclick="closeConnectionModal()">Cancel</button>
              </div>
            `;
          }
        };
      }
      
      if (typeof window.showNewBusinessFlow !== 'function') {
        window.showNewBusinessFlow = function() {
          console.log('[FB-MODAL-FIX] Showing new business flow');
          const contentArea = document.getElementById('facebook-connection-content');
          if (contentArea) {
            contentArea.innerHTML = `
              <div class="text-center mb-3">
                <h4 class="text-xl font-bold text-gray-800">Create a Business Manager</h4>
                <p class="text-gray-600">Follow these steps to create a Business Manager and connect with us</p>
              </div>
              
              <div class="steps-container space-y-6">
                <div class="step-item pb-3 border-bottom">
                  <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">1</span> Create Business Manager</h5>
                  <p class="text-gray-600 mb-3">Create a new Facebook Business Manager by clicking the button below:</p>
                  <a href="https://business.facebook.com/overview" target="_blank" class="block w-full py-2 px-4 bg-blue-600 text-white text-center rounded hover:bg-blue-700">
                    <i class="fas fa-external-link-alt mr-2"></i>Create Business Manager
                  </a>
                </div>
                
                <div class="step-item">
                  <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">2</span> Confirm Connection</h5>
                  <p class="text-gray-600 mb-3">After you've completed these steps, click the button below to confirm:</p>
                  <button class="block w-full py-2 px-4 bg-green-600 text-white text-center rounded hover:bg-green-700" onclick="confirmManualConnection()">
                    <i class="fas fa-check mr-2"></i>I've Connected My Assets
                  </button>
                </div>
              </div>
              
              <div class="text-center mt-6 space-x-2">
                <button class="py-2 px-4 border border-blue-600 text-blue-600 rounded hover:bg-blue-50" onclick="connectFacebookAssets()">
                  <i class="fas fa-arrow-left mr-2"></i>Back
                </button>
                <button class="py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" onclick="closeConnectionModal()">Cancel</button>
              </div>
            `;
          }
        };
      }
      
      if (typeof window.confirmManualConnection !== 'function') {
        window.confirmManualConnection = function() {
          console.log('[FB-MODAL-FIX] Confirming manual connection');
          const contentArea = document.getElementById('facebook-connection-content');
          if (contentArea) {
            contentArea.innerHTML = `
              <div class="text-center">
                <div class="mb-4 text-green-600">
                  <i class="fas fa-check-circle fa-4x"></i>
                </div>
                <h4 class="text-xl font-bold text-gray-800">Thank You!</h4>
                <p class="text-gray-600">We've recorded that you've connected your Facebook assets.</p>
                <p class="text-gray-600">Our team will verify the connection within 1 business day and reach out if we need anything else.</p>
                <div class="mt-6">
                  <button type="button" class="py-2 px-6 bg-green-600 text-white text-center rounded hover:bg-green-700" onclick="completeOnboarding()">Continue</button>
                </div>
              </div>
            `;
          }
          
          // Update onboarding status if possible
          try {
            if (typeof updateOnboardingProgress === 'function') {
              updateOnboardingProgress('social-card', 'Completed');
            }
          } catch(e) {
            console.error('[FB-MODAL-FIX] Error updating onboarding status:', e);
          }
        };
      }
      
      if (typeof window.completeOnboarding !== 'function') {
        window.completeOnboarding = function() {
          console.log('[FB-MODAL-FIX] Completing onboarding');
          closeConnectionModal();
        };
      }
    } else {
      console.log('[FB-MODAL-FIX] Modal found, ensuring visibility');
      
      // Ensure the modal is visible
      modal.style.zIndex = '9999';
      modal.style.display = 'block';
      
      // Make sure Font Awesome is loaded for icons
      if (!document.querySelector('link[href*="fontawesome"]')) {
        const fontAwesomeLink = document.createElement('link');
        fontAwesomeLink.rel = 'stylesheet';
        fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(fontAwesomeLink);
      }
    }
  }, 100);
};

// Attach a click handler to all social connect buttons
document.addEventListener('DOMContentLoaded', function() {
  console.log('[FB-MODAL-FIX] DOM loaded, setting up button handlers');
  
  // Find all social buttons
  const socialButtons = document.querySelectorAll('button[onclick*="showSocialModal"]');
  socialButtons.forEach(function(button, index) {
    console.log(`[FB-MODAL-FIX] Found social button ${index + 1}, adding enhanced click handler`);
    
    // Add a direct click handler
    button.addEventListener('click', function(e) {
      console.log('[FB-MODAL-FIX] Social button clicked, showing Facebook integration');
      
      // Prevent default action
      e.preventDefault();
      e.stopPropagation();
      
      // Call our enhanced connectFacebookAssets
      connectFacebookAssets();
      
      return false;
    });
  });
  
  // Additionally, check if the modal should be shown immediately (common fix for cases where click was already handled)
  setTimeout(function() {
    // If the original modal is open but our enhanced one is not
    const socialModal = document.getElementById('social-modal');
    const facebookModal = document.getElementById('facebook-connection-modal');
    
    if (socialModal && window.getComputedStyle(socialModal).display !== 'none' && (!facebookModal || window.getComputedStyle(facebookModal).display === 'none')) {
      console.log('[FB-MODAL-FIX] Found open social modal, showing Facebook integration');
      connectFacebookAssets();
    }
  }, 500);
});

// Force-run if we're already loaded after DOM is ready
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  console.log('[FB-MODAL-FIX] Document already loaded, running setup immediately');
  
  const socialButtons = document.querySelectorAll('button[onclick*="showSocialModal"]');
  console.log(`[FB-MODAL-FIX] Found ${socialButtons.length} social buttons`);
  
  socialButtons.forEach(function(button, index) {
    console.log(`[FB-MODAL-FIX] Setting up button ${index + 1}`);
    
    button.addEventListener('click', function(e) {
      console.log('[FB-MODAL-FIX] Social button clicked, showing Facebook integration');
      e.preventDefault();
      e.stopPropagation();
      connectFacebookAssets();
      return false;
    });
  });
}

console.log('[FB-MODAL-FIX] Facebook modal visibility fix loaded'); 