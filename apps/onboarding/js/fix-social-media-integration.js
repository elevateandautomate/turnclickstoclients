/**
 * Social Media Integration Fix Script
 * Fixes errors with undefined functions and enhances functionality
 */

console.log('Social Media Integration Fix Script loaded');

// Make sure these functions are defined before the page tries to use them
window.showExistingAssetsFlow = function() {
  console.log('showExistingAssetsFlow called');
  
  // Show the existing assets flow content
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (existingAssetsFlow) {
    existingAssetsFlow.style.display = 'block';
  }
  
  // Hide the setup guide
  const setupGuide = document.getElementById('setup-guide');
  if (setupGuide) {
    setupGuide.style.display = 'none';
  }
  
  // Add enhanced UI elements
  setTimeout(() => {
    console.log('Adding enhanced UI to existing assets flow');
    enhanceExistingAssetsFlow();
  }, 100);
};

window.showSetupGuide = function() {
  console.log('showSetupGuide called');
  
  // Show the setup guide content
  const setupGuide = document.getElementById('setup-guide');
  if (setupGuide) {
    setupGuide.style.display = 'block';
  }
  
  // Hide the existing assets flow
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (existingAssetsFlow) {
    existingAssetsFlow.style.display = 'none';
  }
  
  // Add enhanced UI elements
  setTimeout(() => {
    console.log('Adding enhanced UI to setup guide');
    enhanceSetupGuide();
  }, 100);
};

// Helper function to enhance the existing assets flow
function enhanceExistingAssetsFlow() {
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (!existingAssetsFlow) return;
  
  // Find Facebook connect button and enhance it
  const connectButton = existingAssetsFlow.querySelector('button[onclick="connectFacebookManager()"]');
  if (connectButton) {
    console.log('Found Facebook connect button');
    
    // Make sure we have a notification area
    if (!document.getElementById('facebook-notification-area')) {
      const notificationArea = document.createElement('div');
      notificationArea.id = 'facebook-notification-area';
      notificationArea.className = 'mt-4 p-4 bg-blue-50 rounded-lg';
      notificationArea.style.display = 'none';
      existingAssetsFlow.appendChild(notificationArea);
    }
  }
}

// Helper function to enhance the setup guide
function enhanceSetupGuide() {
  const setupGuide = document.getElementById('setup-guide');
  if (!setupGuide) return;
  
  // Find Ad Account creation button
  const createAdAccountBtn = setupGuide.querySelector('button[onclick="openAdAccountCreation()"]');
  if (createAdAccountBtn) {
    console.log('Found Ad Account creation button');
    
    // Make sure we have a notification area
    if (!document.getElementById('facebook-notification-area')) {
      const notificationArea = document.createElement('div');
      notificationArea.id = 'facebook-notification-area';
      notificationArea.className = 'mt-4 p-4 bg-blue-50 rounded-lg';
      notificationArea.style.display = 'none';
      setupGuide.appendChild(notificationArea);
    }
  }
}

// Override social media connection functions
window.connectFacebookManager = function() {
  console.log('connectFacebookManager called');
  
  // Open Facebook Business Manager in a new tab
  window.open('https://business.facebook.com/overview', '_blank');
  
  // Display success message
  const notificationArea = document.getElementById('facebook-notification-area');
  if (notificationArea) {
    notificationArea.innerHTML = `
      <div class="flex items-center text-green-700">
        <i class="fas fa-check-circle mr-2"></i>
        <span>Facebook Business Manager opened in a new tab. When you've connected, click the button below.</span>
      </div>
      <button id="confirm-facebook-btn" class="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        I've Connected My Facebook Account
      </button>
    `;
    notificationArea.style.display = 'block';
    
    // Add event listener to confirmation button
    const confirmButton = document.getElementById('confirm-facebook-btn');
    if (confirmButton) {
      confirmButton.addEventListener('click', confirmFacebookConnection);
    }
  }
};

window.openAdAccountCreation = function() {
  console.log('openAdAccountCreation called');
  
  // Open Ad Account creation page in a new tab
  window.open('https://business.facebook.com/settings/ad-accounts', '_blank');
  
  // Display success message
  const notificationArea = document.getElementById('facebook-notification-area');
  if (notificationArea) {
    notificationArea.innerHTML = `
      <div class="flex items-center text-green-700">
        <i class="fas fa-check-circle mr-2"></i>
        <span>Ad Account creation page opened in a new tab. When you've set up your ad account, click the button below.</span>
      </div>
      <button id="confirm-ad-account-btn" class="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        I've Set Up My Ad Account
      </button>
    `;
    notificationArea.style.display = 'block';
    
    // Add event listener to confirmation button
    const confirmButton = document.getElementById('confirm-ad-account-btn');
    if (confirmButton) {
      confirmButton.addEventListener('click', confirmAdAccountSetup);
    }
  }
};

// Confirm Facebook connection
function confirmFacebookConnection() {
  console.log('Facebook connection confirmed');
  
  // Create or update connected accounts section
  let connectedAccountsSection = document.getElementById('connected-accounts-section');
  if (!connectedAccountsSection) {
    connectedAccountsSection = document.createElement('div');
    connectedAccountsSection.id = 'connected-accounts-section';
    connectedAccountsSection.className = 'mt-6 p-4 bg-white rounded-lg border';
    connectedAccountsSection.innerHTML = `
      <h3 class="text-lg font-semibold mb-3">Connected Accounts</h3>
      <div id="connected-accounts-list" class="space-y-2"></div>
    `;
    
    const notificationArea = document.getElementById('facebook-notification-area');
    if (notificationArea) {
      notificationArea.parentNode.insertBefore(connectedAccountsSection, notificationArea);
    } else {
      const existingAssetsFlow = document.getElementById('existing-assets-flow');
      if (existingAssetsFlow) {
        existingAssetsFlow.appendChild(connectedAccountsSection);
      }
    }
  }
  
  // Add Facebook account to connected accounts
  const connectedAccountsList = document.getElementById('connected-accounts-list');
  if (connectedAccountsList) {
    // Check if Facebook is already in the list
    if (!connectedAccountsList.querySelector('[data-account="facebook"]')) {
      const accountItem = document.createElement('div');
      accountItem.className = 'flex items-center justify-between p-3 bg-blue-50 rounded-lg';
      accountItem.setAttribute('data-account', 'facebook');
      accountItem.innerHTML = `
        <div class="flex items-center">
          <i class="fab fa-facebook text-[#1877F2] text-xl mr-3"></i>
          <span class="font-medium">Facebook Business Manager</span>
        </div>
        <span class="text-green-600 flex items-center text-sm">
          <i class="fas fa-check-circle mr-1"></i> Connected
        </span>
      `;
      connectedAccountsList.appendChild(accountItem);
    }
  }
  
  // Update notification area
  const notificationArea = document.getElementById('facebook-notification-area');
  if (notificationArea) {
    notificationArea.innerHTML = `
      <div class="flex items-center text-green-700">
        <i class="fas fa-check-circle mr-2"></i>
        <span>Facebook Business Manager successfully connected!</span>
      </div>
    `;
  }
  
  // Show confirm social connections button
  const confirmSocialBtn = document.querySelector('button[onclick="confirmSocialConnections()"]');
  if (confirmSocialBtn) {
    confirmSocialBtn.parentNode.style.display = 'block';
  }
}

// Confirm Ad Account setup
function confirmAdAccountSetup() {
  console.log('Ad Account setup confirmed');
  
  // Create or update connected accounts section
  let connectedAccountsSection = document.getElementById('connected-accounts-section');
  if (!connectedAccountsSection) {
    connectedAccountsSection = document.createElement('div');
    connectedAccountsSection.id = 'connected-accounts-section';
    connectedAccountsSection.className = 'mt-6 p-4 bg-white rounded-lg border';
    connectedAccountsSection.innerHTML = `
      <h3 class="text-lg font-semibold mb-3">Connected Accounts</h3>
      <div id="connected-accounts-list" class="space-y-2"></div>
    `;
    
    const notificationArea = document.getElementById('facebook-notification-area');
    if (notificationArea) {
      notificationArea.parentNode.insertBefore(connectedAccountsSection, notificationArea);
    } else {
      const setupGuide = document.getElementById('setup-guide');
      if (setupGuide) {
        setupGuide.appendChild(connectedAccountsSection);
      }
    }
  }
  
  // Add Ad Account to connected accounts
  const connectedAccountsList = document.getElementById('connected-accounts-list');
  if (connectedAccountsList) {
    // Check if Ad Account is already in the list
    if (!connectedAccountsList.querySelector('[data-account="ad-account"]')) {
      const accountItem = document.createElement('div');
      accountItem.className = 'flex items-center justify-between p-3 bg-blue-50 rounded-lg';
      accountItem.setAttribute('data-account', 'ad-account');
      accountItem.innerHTML = `
        <div class="flex items-center">
          <i class="fas fa-ad text-[#1877F2] text-xl mr-3"></i>
          <span class="font-medium">Facebook Ad Account</span>
        </div>
        <span class="text-green-600 flex items-center text-sm">
          <i class="fas fa-check-circle mr-1"></i> Connected
        </span>
      `;
      connectedAccountsList.appendChild(accountItem);
    }
  }
  
  // Update notification area
  const notificationArea = document.getElementById('facebook-notification-area');
  if (notificationArea) {
    notificationArea.innerHTML = `
      <div class="flex items-center text-green-700">
        <i class="fas fa-check-circle mr-2"></i>
        <span>Facebook Ad Account successfully set up!</span>
      </div>
    `;
  }
  
  // Show confirm social connections button
  const confirmSocialBtn = document.querySelector('button[onclick="confirmSocialConnections()"]');
  if (confirmSocialBtn) {
    confirmSocialBtn.parentNode.style.display = 'block';
  }
}

// Override confirmSocialConnections to update database
if (typeof window.confirmSocialConnections !== 'function') {
  window.confirmSocialConnections = async function() {
    console.log('confirmSocialConnections called');
    
    try {
      // Check if we have connected accounts
      const connectedAccounts = document.querySelectorAll('#connected-accounts-list > div');
      if (connectedAccounts.length === 0) {
        alert('Please connect at least one social media account first.');
        return;
      }
      
      // Update database if Supabase is available
      if (window.supabaseClient) {
        // Get current user
        const { data: { user } } = await window.supabaseClient.auth.getUser();
        
        if (user) {
          // Update the onboarding status
          const { error } = await window.supabaseClient
            .from('new_client_onboarding')
            .upsert({
              user_id: user.id,
              social_status: 'Completed'
            });
            
          if (error) {
            console.error('Error updating social status:', error);
            alert('There was an error saving your social media setup. Please try again.');
            return;
          }
        }
      }
      
      // Update UI if possible
      if (typeof updateStepUICard === 'function') {
        updateStepUICard('social-card', 'social-card-status', 'Completed');
      }
      
      // Close the modal
      const socialModal = document.getElementById('social-modal');
      if (socialModal) {
        socialModal.style.display = 'none';
      }
      
      alert('Social media setup completed successfully!');
    } catch (error) {
      console.error('Error in confirmSocialConnections:', error);
      alert('There was an error saving your social media setup. Please try again.');
    }
  };
} 