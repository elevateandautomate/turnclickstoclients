/**
 * FACEBOOK DIRECT INTEGRATION
 * 
 * This script implements a direct Facebook integration flow without requiring a Facebook App.
 * It uses direct links to Facebook Business Manager and guides users through manual connection steps.
 */

// Configuration - REPLACE THIS VALUE WITH YOUR ACTUAL BUSINESS MANAGER ID
const FB_CONFIG = {
  businessManagerId: '1234567890', // Your Business Manager ID
  businessName: 'Your Company Name' // Your company name
};

// Don't override the existing showSocialModal function directly, 
// instead patch openModal to handle the social-modal case
const originalOpenModal = window.openModal || function() {};
window.openModal = function(modalId, ...args) {
  console.log(`openModal called with ${modalId}`);
  
  // If this is the social modal, use our custom implementation
  if (modalId === 'social-modal') {
    console.log("Intercepted social-modal open, showing new integration UI");
    connectFacebookAssets();
    return false;
  }
  
  // Otherwise, call the original function
  return originalOpenModal(modalId, ...args);
};

// Main entry point - call this when user clicks the connect button
function connectFacebookAssets() {
  console.log("Starting Facebook assets connection flow...");
  
  // Create and show the modal with instructions
  createConnectionModal();
  showConnectionModal();
  
  // Show the initial instructions screen
  showInstructionsScreen();
}

// Show instructions for connecting Facebook assets
function showInstructionsScreen() {
  updateConnectionModal(`
    <div class="text-center mb-4">
      <i class="fab fa-facebook text-[#1877F2] fa-3x mb-3"></i>
      <h4 class="text-xl font-bold text-gray-800">Connect Your Social Media Accounts</h4>
      <p>Follow these steps to connect your Facebook ad accounts, pages, and Instagram profiles.</p>
    </div>
    
    <div class="px-2">
      <div class="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-100">
        <p class="text-sm text-yellow-800">
          <i class="fas fa-info-circle mr-2"></i>
          Please read through the instructions carefully before proceeding. Most questions can be answered by following the steps provided.
        </p>
      </div>
      
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
      
      <div class="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-100">
        <p class="text-sm text-yellow-800">
          <i class="fas fa-shield-alt mr-2"></i>
          Your account security is our priority. We only request necessary permissions to manage your campaigns effectively.
        </p>
      </div>
      
      <div class="mt-6 text-center">
        <button class="py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" onclick="cancelFacebookConnection()">Cancel</button>
      </div>
    </div>
  `);
}

// Show instructions for users with existing Business Manager
function showExistingBusinessFlow() {
  updateConnectionModal(`
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
        <p class="text-gray-600">Enter our Business ID: <strong class="text-blue-600">${FB_CONFIG.businessManagerId}</strong></p>
        <div class="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-100">
          <p class="text-sm text-blue-800">
            <i class="fas fa-lightbulb mr-2"></i>
            You may need to scroll down in the Partners section to find the Add option.
          </p>
        </div>
      </div>
      
      <div class="step-item pb-3 border-bottom">
        <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">3</span> Select Assets to Share</h5>
        <p class="text-gray-600">Select the assets you want to share with us:</p>
        <ul class="list-disc pl-5 text-gray-600">
          <li><strong>Ad Accounts</strong>: Select all accounts we should manage</li>
          <li><strong>Pages</strong>: Select business pages for your ads</li>
          <li><strong>Instagram Accounts</strong>: Select connected Instagram accounts</li>
        </ul>
        <p class="text-gray-600">Set permission level to <strong>Ad Account Advertiser</strong> for each asset</p>
      </div>
      
      <div class="step-item">
        <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">4</span> Confirm Connection</h5>
        <p class="text-gray-600 mb-3">After you've completed these steps, click the button below to confirm:</p>
        <button class="block w-full py-2 px-4 bg-green-600 text-white text-center rounded hover:bg-green-700" onclick="confirmManualConnection()">
          <i class="fas fa-check mr-2"></i>I've Connected My Assets
        </button>
      </div>
    </div>
    
    <div class="text-center mt-6 space-x-2">
      <button class="py-2 px-4 border border-blue-600 text-blue-600 rounded hover:bg-blue-50" onclick="showInstructionsScreen()">
        <i class="fas fa-arrow-left mr-2"></i>Back
      </button>
      <button class="py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" onclick="cancelFacebookConnection()">Cancel</button>
    </div>
  `);
}

// Show instructions for users who need to create a Business Manager
function showNewBusinessFlow() {
  updateConnectionModal(`
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
        <p class="text-sm text-gray-500 mt-2">You'll need to provide your business name and details.</p>
      </div>
      
      <div class="step-item pb-3 border-bottom">
        <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">2</span> Create an Ad Account</h5>
        <p class="text-gray-600">After creating your Business Manager:</p>
        <ol class="list-decimal pl-5 text-gray-600">
          <li>Go to <strong>Business Settings</strong></li>
          <li>Select <strong>Accounts</strong> > <strong>Ad Accounts</strong></li>
          <li>Click <strong>Add</strong> > <strong>Create a New Ad Account</strong></li>
        </ol>
        <a href="https://business.facebook.com/settings/ad-accounts" target="_blank" class="block w-full py-2 px-4 mt-3 border border-blue-600 text-blue-600 text-center rounded hover:bg-blue-50">
          <i class="fas fa-plus-circle mr-2"></i>Create Ad Account
        </a>
      </div>
      
      <div class="step-item pb-3 border-bottom">
        <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">3</span> Add a Partner</h5>
        <p class="text-gray-600">Now that your Business Manager is set up:</p>
        <ol class="list-decimal pl-5 text-gray-600">
          <li>Go to <strong>Business Settings</strong></li>
          <li>Select <strong>Partners</strong> from the left menu</li>
          <li>Click <strong>Add</strong> > <strong>Add a Partner</strong></li>
          <li>Enter our Business ID: <strong class="text-blue-600">${FB_CONFIG.businessManagerId}</strong></li>
          <li>Select your ad account and set permission level to <strong>Ad Account Advertiser</strong></li>
        </ol>
        <a href="https://business.facebook.com/settings/partners" target="_blank" class="block w-full py-2 px-4 mt-3 border border-blue-600 text-blue-600 text-center rounded hover:bg-blue-50">
          <i class="fas fa-user-plus mr-2"></i>Add Partner
        </a>
      </div>
      
      <div class="step-item">
        <h5 class="font-medium text-gray-800"><span class="inline-block w-6 h-6 text-center rounded-full bg-blue-600 text-white mr-2">4</span> Confirm Connection</h5>
        <p class="text-gray-600 mb-3">After you've completed these steps, click the button below to confirm:</p>
        <button class="block w-full py-2 px-4 bg-green-600 text-white text-center rounded hover:bg-green-700" onclick="confirmManualConnection()">
          <i class="fas fa-check mr-2"></i>I've Connected My Assets
        </button>
      </div>
    </div>
    
    <div class="text-center mt-6 space-x-2">
      <button class="py-2 px-4 border border-blue-600 text-blue-600 rounded hover:bg-blue-50" onclick="showInstructionsScreen()">
        <i class="fas fa-arrow-left mr-2"></i>Back
      </button>
      <button class="py-2 px-4 bg-gray-200 text-gray-700 rounded hover:bg-gray-300" onclick="cancelFacebookConnection()">Cancel</button>
    </div>
  `);
}

// Confirm the manual connection process
function confirmManualConnection() {
  updateConnectionModal(`
    <div class="text-center">
      <div class="mb-4 text-green-600">
        <i class="fas fa-check-circle fa-4x"></i>
      </div>
      <h4 class="text-xl font-bold text-gray-800">Thank You!</h4>
      <p class="text-gray-600">We've recorded that you've connected your Facebook assets.</p>
      <p class="text-gray-600">Our team will verify the connection within 1 business day and reach out if we need anything else.</p>
      <div class="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
        <p class="text-sm text-blue-800">
          <i class="fas fa-info-circle mr-2"></i>
          <strong>Important:</strong> If you don't see our business request in your Business Manager, please double-check that you entered our Business ID correctly: <strong>${FB_CONFIG.businessManagerId}</strong>
        </p>
      </div>
      <div class="mt-6">
        <button type="button" class="py-2 px-6 bg-green-600 text-white text-center rounded hover:bg-green-700" onclick="completeOnboarding()">Continue</button>
      </div>
    </div>
  `);
  
  // Update onboarding status
  try {
    updateOnboardingStatus('social-card', 'Completed');
  } catch(e) {
    console.error("Error updating onboarding status:", e);
  }

  // Also close the original modal if it exists
  try {
    if (typeof closeModal === 'function') {
      setTimeout(function() {
        closeModal('social-modal');
      }, 500);
    }
  } catch(e) {
    console.error("Error closing original modal:", e);
  }
}

// Continue with the onboarding process
function completeOnboarding() {
  closeConnectionModal();
  
  // Redirect or update UI as needed
  console.log("Facebook integration complete, continuing with onboarding...");
  
  // If there's a next step function in your onboarding, call it here
  try {
    if (typeof continueToNextOnboardingStep === 'function') {
      continueToNextOnboardingStep('social');
    }
  } catch(e) {
    console.error("Error continuing onboarding:", e);
  }

  // Also close the original modal if it exists
  try {
    if (typeof closeModal === 'function') {
      closeModal('social-modal');
    }
  } catch(e) {
    console.error("Error closing original modal:", e);
  }
}

// Cancel the connection process
function cancelFacebookConnection() {
  console.log("Cancelling Facebook connection...");
  closeConnectionModal();
  
  // Also close the original modal if it exists
  try {
    if (typeof closeModal === 'function') {
      closeModal('social-modal');
    }
  } catch(e) {
    console.error("Error closing original modal:", e);
  }
}

// Create the connection modal in the DOM
function createConnectionModal() {
  // Check if modal already exists
  if (document.getElementById('facebook-connection-modal')) {
    return;
  }
  
  const modalHtml = `
    <div id="facebook-connection-modal" class="fixed inset-0 bg-gray-600 bg-opacity-50" style="z-index: 1000;">
      <div class="relative top-10 mx-auto p-5 border w-3/4 max-w-4xl shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white z-10 pb-4 border-b mb-4">
          <div class="flex justify-between items-center">
            <h3 class="text-xl font-bold text-gray-800">Connect Your Social Media Accounts</h3>
            <button onclick="cancelFacebookConnection()" class="text-gray-400 hover:text-gray-500">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <!-- Social Media Modal Help Section -->
          <div class="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-100">
            <p class="text-sm text-yellow-800">
              <i class="fas fa-info-circle mr-2"></i>
              Please read through the instructions carefully before proceeding. Most questions can be answered by following the steps provided.
            </p>
          </div>
        </div>
        <div id="facebook-connection-content" class="space-y-6">
          <!-- Content will be dynamically updated -->
          <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p class="mt-3 text-gray-600">Loading instructions...</p>
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to DOM
  const modalContainer = document.createElement('div');
  modalContainer.innerHTML = modalHtml;
  document.body.appendChild(modalContainer.firstChild);
}

// Show the connection modal
function showConnectionModal() {
  const modal = document.getElementById('facebook-connection-modal');
  if (modal) {
    modal.style.display = 'block';
  }
}

// Close the connection modal
function closeConnectionModal() {
  const modal = document.getElementById('facebook-connection-modal');
  if (modal) {
    modal.style.display = 'none';
    
    // Optional: remove from DOM completely
    //modal.parentNode.removeChild(modal);
  }
}

// Update the connection modal content
function updateConnectionModal(htmlContent) {
  const contentElement = document.getElementById('facebook-connection-content');
  if (contentElement) {
    contentElement.innerHTML = htmlContent;
  }
}

// Add a function to update the onboarding status UI
function updateOnboardingStatus(cardId, status) {
  console.log(`Updating ${cardId} status to ${status}`);
  
  // This should match your existing updateOnboardingUI function
  try {
    if (typeof updateUI === 'function') {
      updateUI(cardId, status);
    } else if (typeof updateOnboardingProgress === 'function') {
      // Try the function from workingonboarding.html
      updateOnboardingProgress(cardId, status);
    }
  } catch(e) {
    console.error("Error updating UI:", e);
  }
}

// Expose the main function globally
window.connectFacebookAssets = connectFacebookAssets;

// Initialization
document.addEventListener('DOMContentLoaded', function() {
  console.log("Facebook Direct Integration script loaded - patching openModal function");
  
  // Check if we need to add Font Awesome (if not already available)
  if (!document.querySelector('link[href*="fontawesome"]')) {
    const fontAwesomeLink = document.createElement('link');
    fontAwesomeLink.rel = 'stylesheet';
    fontAwesomeLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    document.head.appendChild(fontAwesomeLink);
  }
}); 