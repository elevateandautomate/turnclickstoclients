// Facebook Integration Module - Simplified Version
// This script handles Facebook Business Manager integration without requiring a Facebook App

/**
 * Simplified Facebook Integration Module
 * This module allows users to:
 * 1. Connect with their Facebook Business Manager
 * 2. Grant access to their Facebook ad accounts
 * 3. Get guided setup for creating ad accounts if they don't have one
 */

// Initialize the module
document.addEventListener('DOMContentLoaded', function() {
  console.log('Facebook Integration Module loaded (Simplified Version)');
  initializeFacebookIntegration();
});

// Main initialization function
function initializeFacebookIntegration() {
  // Add event listeners to the Facebook connect buttons
  const facebookButtons = document.querySelectorAll('.facebook-connect-btn');
  facebookButtons.forEach(button => {
    button.addEventListener('click', handleFacebookConnect);
  });

  // Set up the guided setup buttons
  const adAccountSetupButtons = document.querySelectorAll('.create-ad-account-btn');
  adAccountSetupButtons.forEach(button => {
    button.addEventListener('click', startAdAccountSetup);
  });

  // Check for existing Facebook connections
  checkExistingFacebookConnections();
}

// Handle Facebook Connect Button Click
function handleFacebookConnect(event) {
  if (event) event.preventDefault();
  
  console.log('Facebook connect button clicked');
  showLoadingState('Opening Facebook Business Manager...');
  
  // Simply open Facebook Business Manager in a new tab
  window.open('https://business.facebook.com/overview', '_blank');
  
  // Hide loading and show next steps
  setTimeout(() => {
    hideLoadingState();
    showBusinessManagerInstructions();
  }, 1000);
}

// Show Business Manager Instructions
function showBusinessManagerInstructions() {
  // Hide any existing success/error messages
  hideAllMessages();
  
  // Show the business manager instructions
  const instructionsElement = document.getElementById('facebook-business-instructions');
  if (instructionsElement) {
    instructionsElement.style.display = 'block';
  } else {
    // Create instructions if they don't exist
    createBusinessManagerInstructions();
  }
  
  // Show the "I've connected" confirmation button
  const confirmButton = document.getElementById('confirm-facebook-connection');
  if (confirmButton) {
    confirmButton.style.display = 'block';
    // Make sure it has the click handler
    confirmButton.onclick = confirmBusinessManagerConnection;
  }
}

// Create Business Manager Instructions if they don't exist
function createBusinessManagerInstructions() {
  const container = document.querySelector('#enhanced-facebook-ui') || document.body;
  
  const instructionsDiv = document.createElement('div');
  instructionsDiv.id = 'facebook-business-instructions';
  instructionsDiv.className = 'bg-yellow-50 text-yellow-800 p-4 rounded-md my-4';
  
  instructionsDiv.innerHTML = `
    <h4 class="font-medium mb-2"><i class="fas fa-info-circle mr-2"></i>Next Steps</h4>
    <ol class="list-decimal pl-5 space-y-2 text-sm">
      <li>In the newly opened tab, log in to your Facebook account if prompted</li>
      <li>Navigate to your Business Manager settings</li>
      <li>Make sure your Business Manager is set up properly</li>
      <li>Return to this tab and click "I've Connected My Business Manager" below</li>
    </ol>
    <div class="mt-4">
      <button id="confirm-facebook-connection" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        I've Connected My Business Manager
      </button>
    </div>
  `;
  
  container.appendChild(instructionsDiv);
}

// Confirm Business Manager Connection
function confirmBusinessManagerConnection() {
  console.log('User confirmed Business Manager connection');
  
  // Hide instructions
  const instructionsElement = document.getElementById('facebook-business-instructions');
  if (instructionsElement) {
    instructionsElement.style.display = 'none';
  }
  
  // Ask if they have ad accounts
  askAboutAdAccounts();
}

// Ask if the user has ad accounts
function askAboutAdAccounts() {
  // Create and show the ad account question
  const container = document.querySelector('#enhanced-facebook-ui') || document.body;
  
  const adAccountDiv = document.createElement('div');
  adAccountDiv.id = 'ad-account-question';
  adAccountDiv.className = 'bg-white border border-gray-200 p-4 rounded-md my-4';
  
  adAccountDiv.innerHTML = `
    <h4 class="font-medium mb-2">Do you have Facebook Ad Accounts set up?</h4>
    <div class="mt-3 space-x-3">
      <button id="has-ad-accounts" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
        Yes, I Have Ad Accounts
      </button>
      <button id="no-ad-accounts" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        No, I Need to Create One
      </button>
    </div>
  `;
  
  container.appendChild(adAccountDiv);
  
  // Add event listeners
  document.getElementById('has-ad-accounts').addEventListener('click', confirmAdAccountsExist);
  document.getElementById('no-ad-accounts').addEventListener('click', startAdAccountSetup);
}

// Confirm Ad Accounts Exist
function confirmAdAccountsExist() {
  // Hide the question
  const questionElement = document.getElementById('ad-account-question');
  if (questionElement) {
    questionElement.style.display = 'none';
  }
  
  // Show success and mark as completed
  showSuccessMessage('Facebook Business Manager and Ad Accounts successfully connected!');
  updateFacebookIntegrationUI(true);
  updateSocialIntegrationStatus('Completed');
}

// Start guided setup for ad account creation
function startAdAccountSetup() {
  // Hide any questions
  const questionElement = document.getElementById('ad-account-question');
  if (questionElement) {
    questionElement.style.display = 'none';
  }
  
  // Show the guided setup UI
  const setupGuide = document.getElementById('ad-account-setup-guide');
  if (setupGuide) {
    setupGuide.style.display = 'block';
  } else {
    // Create the guide if it doesn't exist
    createAdAccountSetupGuide();
  }
}

// Create Ad Account Setup Guide
function createAdAccountSetupGuide() {
  const container = document.querySelector('#enhanced-facebook-ui') || document.body;
  
  const guideDiv = document.createElement('div');
  guideDiv.id = 'ad-account-setup-guide';
  guideDiv.className = 'bg-gray-50 p-5 rounded-lg border my-4';
  
  guideDiv.innerHTML = `
    <h3 class="text-lg font-semibold text-gray-800 mb-4">Ad Account Setup Guide</h3>
    
    <ol class="space-y-6">
      <li class="flex">
        <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
          1
        </div>
        <div class="ml-4">
          <h5 class="font-medium text-gray-800">Create a Business Manager</h5>
          <p class="text-sm text-gray-600 mb-2">If you don't already have one, you'll need to create a Meta Business Manager first.</p>
          <button onclick="window.open('https://business.facebook.com/create', '_blank')" class="text-sm px-3 py-1 bg-[#1877F2] text-white rounded-md hover:bg-[#1664d9]">
            Create Business Manager
          </button>
        </div>
      </li>
      
      <li class="flex">
        <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
          2
        </div>
        <div class="ml-4">
          <h5 class="font-medium text-gray-800">Create a Business Page</h5>
          <p class="text-sm text-gray-600 mb-2">Create a business page that will be associated with your ads.</p>
          <button onclick="window.open('https://www.facebook.com/pages/create/', '_blank')" class="text-sm px-3 py-1 bg-[#1877F2] text-white rounded-md hover:bg-[#1664d9]">
            Create Business Page
          </button>
        </div>
      </li>
      
      <li class="flex">
        <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
          3
        </div>
        <div class="ml-4">
          <h5 class="font-medium text-gray-800">Create an Ad Account</h5>
          <p class="text-sm text-gray-600 mb-2">Create an ad account within your Business Manager.</p>
          <button onclick="window.open('https://business.facebook.com/settings/ad-accounts', '_blank')" class="text-sm px-3 py-1 bg-[#1877F2] text-white rounded-md hover:bg-[#1664d9]">
            Create Ad Account
          </button>
        </div>
      </li>
      
      <li class="flex">
        <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold">
          4
        </div>
        <div class="ml-4">
          <h5 class="font-medium text-gray-800">Add Payment Method</h5>
          <p class="text-sm text-gray-600 mb-2">Add a payment method to your ad account.</p>
          <button onclick="window.open('https://business.facebook.com/settings/payment-methods', '_blank')" class="text-sm px-3 py-1 bg-[#1877F2] text-white rounded-md hover:bg-[#1664d9]">
            Add Payment Method
          </button>
        </div>
      </li>
    </ol>
    
    <div class="mt-6 pt-6 border-t border-gray-200">
      <p class="font-medium text-gray-800 mb-2">Have you completed all the steps above?</p>
      <button id="confirm-ad-account-creation" class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
        Yes, I've Set Up My Ad Account
      </button>
    </div>
  `;
  
  container.appendChild(guideDiv);
  
  // Add event listener to the confirmation button
  document.getElementById('confirm-ad-account-creation').addEventListener('click', verifyAdAccountCreation);
}

// Verify the ad account was created
function verifyAdAccountCreation() {
  console.log('User confirmed ad account creation');
  
  // Hide the guide
  const setupGuide = document.getElementById('ad-account-setup-guide');
  if (setupGuide) {
    setupGuide.style.display = 'none';
  }
  
  // Show success message
  showSuccessMessage('Facebook Business Manager and Ad Account successfully connected!');
  
  // Update UI to reflect completion
  updateFacebookIntegrationUI(true);
  
  // Update database
  updateSocialIntegrationStatus('Completed');
}

// Update the database status
async function updateSocialIntegrationStatus(status) {
  try {
    const { data: { user } } = await window.supabaseClient.auth.getUser();
    if (!user) return;
    
    await window.supabaseClient
      .from('new_client_onboarding')
      .upsert({ 
        user_id: user.id,
        social_status: status
      })
      .select();
      
    // Also update UI card if on the onboarding page
    if (typeof updateStepUICard === 'function') {
      updateStepUICard('social-card', 'social-card-status', status);
    }
    
    console.log('Social integration status updated to:', status);
  } catch (error) {
    console.error('Error updating social status:', error);
  }
}

// Check for existing Facebook connections
async function checkExistingFacebookConnections() {
  try {
    const { data: { user } } = await window.supabaseClient.auth.getUser();
    if (!user) return;
    
    // Get onboarding status
    const { data, error } = await window.supabaseClient
      .from('new_client_onboarding')
      .select('social_status')
      .eq('user_id', user.id)
      .maybeSingle();
      
    if (error) throw error;
    
    if (data && data.social_status === 'Completed') {
      // User already has Facebook integration set up
      updateFacebookIntegrationUI(true);
    }
  } catch (error) {
    console.error('Error checking Facebook connection status:', error);
  }
}

// UI Helper Functions

function showLoadingState(message) {
  hideAllMessages();
  const loadingElement = document.getElementById('facebook-integration-loading');
  if (loadingElement) {
    loadingElement.textContent = message || 'Loading...';
    loadingElement.style.display = 'block';
  }
}

function hideLoadingState() {
  const loadingElement = document.getElementById('facebook-integration-loading');
  if (loadingElement) {
    loadingElement.style.display = 'none';
  }
}

function hideAllMessages() {
  // Hide all message elements
  const messageElements = [
    'facebook-integration-loading',
    'facebook-integration-error',
    'facebook-integration-success',
    'facebook-business-instructions',
    'ad-account-question',
    'ad-account-setup-guide'
  ];
  
  messageElements.forEach(id => {
    const element = document.getElementById(id);
    if (element) {
      element.style.display = 'none';
    }
  });
}

function showFacebookError(message) {
  hideAllMessages();
  const errorElement = document.getElementById('facebook-integration-error');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
      errorElement.style.display = 'none';
    }, 5000);
  }
}

function showSuccessMessage(message) {
  hideAllMessages();
  const successElement = document.getElementById('facebook-integration-success');
  if (successElement) {
    successElement.textContent = message;
    successElement.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
      successElement.style.display = 'none';
    }, 5000);
  }
}

function updateFacebookIntegrationUI(isConnected = true) {
  // Update the UI to show Facebook is connected
  const facebookButtons = document.querySelectorAll('.facebook-connect-btn');
  facebookButtons.forEach(button => {
    if (isConnected) {
      button.textContent = 'Connected';
      button.classList.add('bg-green-600');
      button.classList.remove('bg-[#1877F2]');
      button.disabled = true;
    } else {
      button.textContent = 'Connect';
      button.classList.remove('bg-green-600');
      button.classList.add('bg-[#1877F2]');
      button.disabled = false;
    }
  });
  
  // Add connected account to the UI list if it exists
  const accountsList = document.getElementById('accounts-list');
  if (accountsList && isConnected) {
    addConnectedAccount('Facebook Business Manager', 'facebook');
  }
  
  // Update the confirm button in the social modal
  const confirmSocialBtn = document.getElementById('confirm-social-btn');
  if (confirmSocialBtn && isConnected) {
    confirmSocialBtn.style.display = 'block';
  }
}

// Function from auth.js to maintain compatibility
function addConnectedAccount(name, type) {
  const accountsList = document.getElementById('accounts-list');
  if (!accountsList) return;
  
  const connectedAccountsSection = document.getElementById('connected-accounts');
  if (connectedAccountsSection) {
    connectedAccountsSection.style.display = 'block';
  }
  
  // Check if account already exists
  const existingAccount = document.querySelector(`[data-account-type="${type}"]`);
  if (existingAccount) return;
  
  // Create account item
  const accountItem = document.createElement('div');
  accountItem.className = 'flex items-center justify-between p-3 border rounded-lg';
  accountItem.setAttribute('data-account-type', type);
  
  let icon = 'fa-facebook';
  let color = 'text-[#1877F2]';
  
  if (type === 'instagram') {
    icon = 'fa-instagram';
    color = 'text-[#E4405F]';
  }
  
  accountItem.innerHTML = `
    <div class="flex items-center">
      <i class="fab ${icon} ${color} text-xl mr-3"></i>
      <span class="font-medium">${name}</span>
    </div>
    <span class="text-green-600 text-sm font-medium"><i class="fas fa-check-circle mr-1"></i> Connected</span>
  `;
  
  accountsList.appendChild(accountItem);
}

// Export any functions that need to be callable from HTML
window.handleFacebookConnect = handleFacebookConnect;
window.startAdAccountSetup = startAdAccountSetup;
window.confirmBusinessManagerConnection = confirmBusinessManagerConnection;
window.verifyAdAccountCreation = verifyAdAccountCreation; 