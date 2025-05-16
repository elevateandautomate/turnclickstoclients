/**
 * Facebook Integration - Onboarding Integration
 * This script provides integration with the existing onboarding workflow
 */

console.log('Facebook Integration - Onboarding Integration loaded');

document.addEventListener('DOMContentLoaded', function() {
  // Define the missing functions that are being called in onclick attributes
  if (typeof window.showExistingAssetsFlow !== 'function') {
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
      
      showEnhancedUIInExistingAssetsFlow();
    };
  }
  
  if (typeof window.showSetupGuide !== 'function') {
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
      
      showEnhancedSetupGuide();
    };
  }
  
  // Map the social modal buttons when the DOM is loaded
  const yesOption = document.querySelector('[onclick*="showExistingAssetsFlow"]');
  const noOption = document.querySelector('[onclick*="showSetupGuide"]');
  
  console.log('Original connectFacebookManager function exists:', typeof window.connectFacebookManager === 'function');
  console.log('Original openAdAccountCreation function exists:', typeof window.openAdAccountCreation === 'function');
  console.log('Original confirmSocialConnections function exists:', typeof window.confirmSocialConnections === 'function');
  
  // Add enhanced UI to existing assets flow
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (existingAssetsFlow) {
    console.log('Added enhanced UI to existing-assets-flow');
  }
  
  // Check if the Yes/No options exist
  const hasYesOption = yesOption !== null;
  const hasNoOption = noOption !== null;
  console.log('Found existing Meta business assets options:', hasYesOption, hasNoOption);
  
  // If options exist, enhance them with our event handlers
  if (yesOption) {
    yesOption.addEventListener('click', function() {
      console.log('Yes option clicked');
      // Ensure the original onclick still works (it will be called by the browser)
      setTimeout(showEnhancedUIInExistingAssetsFlow, 100);
    });
  }
  
  if (noOption) {
    noOption.addEventListener('click', function() {
      console.log('No option clicked');
      // Ensure the original onclick still works (it will be called by the browser)
      setTimeout(showEnhancedSetupGuide, 100);
    });
  }
  
  // Find and enhance Facebook connect button
  enhanceFacebookButtons();
});

// Override or create Facebook connection functions if they don't exist
if (typeof window.connectFacebookManager !== 'function') {
  window.connectFacebookManager = function() {
    console.log('connectFacebookManager called - custom implementation');
    window.open('https://business.facebook.com/overview', '_blank');
    
    // Show success message
    displaySuccessMessage('Facebook Business Manager opened in a new tab');
    
    // Show confirmation section
    showConnectConfirmation();
  };
}

if (typeof window.openAdAccountCreation !== 'function') {
  window.openAdAccountCreation = function() {
    console.log('openAdAccountCreation called - custom implementation');
    window.open('https://business.facebook.com/settings/ad-accounts', '_blank');
    
    // Show success message
    displaySuccessMessage('Ad Account Creation page opened in a new tab');
    
    // Show confirmation section
    showAdAccountConfirmation();
  };
}

if (typeof window.confirmSocialConnections !== 'function') {
  window.confirmSocialConnections = async function() {
    console.log('confirmSocialConnections called - custom implementation');
    
    try {
      // Check if we have connected accounts visualization
      const connectedAccounts = document.querySelectorAll('.connected-account-item');
      
      if (connectedAccounts.length === 0) {
        alert('Please connect at least one social media account first');
        return;
      }
      
      // Update the database
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

// Find and enhance Facebook buttons
function enhanceFacebookButtons() {
  // Find Facebook connect button by text
  const fbButtons = Array.from(document.querySelectorAll('button')).filter(
    button => button.textContent.includes('Connect') && 
             button.closest('.bg-white.p-6.rounded-lg') &&
             button.closest('.bg-white.p-6.rounded-lg').textContent.includes('Facebook')
  );
  
  if (fbButtons.length > 0) {
    fbButtons.forEach(button => {
      button.classList.add('facebook-connect-btn');
    });
  }
  
  // Find Ad Account creation button
  const adAccountButtons = Array.from(document.querySelectorAll('button')).filter(
    button => button.getAttribute('onclick') === 'openAdAccountCreation()'
  );
  
  if (adAccountButtons.length > 0) {
    adAccountButtons.forEach(button => {
      button.classList.add('create-ad-account-btn');
    });
  }
}

// Add enhanced UI to the existing assets flow
function showEnhancedUIInExistingAssetsFlow() {
  console.log('Showing enhanced UI in existing assets flow');
  
  const existingAssetsFlow = document.getElementById('existing-assets-flow');
  if (!existingAssetsFlow) return;
  
  // Create connected accounts section if it doesn't exist
  if (!document.getElementById('connected-accounts-section')) {
    const connectedAccountsSection = document.createElement('div');
    connectedAccountsSection.id = 'connected-accounts-section';
    connectedAccountsSection.className = 'mt-6 p-4 bg-blue-50 rounded-lg';
    connectedAccountsSection.innerHTML = `
      <h3 class="text-lg font-semibold mb-3">Connected Accounts</h3>
      <div id="connected-accounts-list" class="space-y-2"></div>
    `;
    
    existingAssetsFlow.appendChild(connectedAccountsSection);
  }
  
  // Create notification area if it doesn't exist
  if (!document.getElementById('facebook-notification-area')) {
    const notificationArea = document.createElement('div');
    notificationArea.id = 'facebook-notification-area';
    notificationArea.className = 'mt-4';
    notificationArea.style.display = 'none';
    
    existingAssetsFlow.appendChild(notificationArea);
  }
}

// Show enhanced setup guide
function showEnhancedSetupGuide() {
  console.log('Showing enhanced setup guide');
  
  const setupGuide = document.getElementById('setup-guide');
  if (!setupGuide) return;
  
  // Find Create Ad Account button
  const createAdAccountBtn = setupGuide.querySelector('button[onclick="openAdAccountCreation()"]');
  if (createAdAccountBtn) {
    console.log('Found Create Ad Account button in setup guide');
  }
}

// Display success message
function displaySuccessMessage(message) {
  // Find or create notification area
  let notificationArea = document.getElementById('facebook-notification-area');
  
  if (!notificationArea) {
    notificationArea = document.createElement('div');
    notificationArea.id = 'facebook-notification-area';
    notificationArea.className = 'mt-4';
    
    const existingAssetsFlow = document.getElementById('existing-assets-flow');
    if (existingAssetsFlow) {
      existingAssetsFlow.appendChild(notificationArea);
    } else {
      const setupGuide = document.getElementById('setup-guide');
      if (setupGuide) {
        setupGuide.appendChild(notificationArea);
      } else {
        const socialModal = document.getElementById('social-modal');
        if (socialModal) {
          socialModal.querySelector('.space-y-6').appendChild(notificationArea);
        }
      }
    }
  }
  
  // Set notification content
  notificationArea.innerHTML = `
    <div class="bg-green-50 text-green-700 p-3 rounded-md flex items-center">
      <div class="mr-3">
        <i class="fas fa-check-circle"></i>
      </div>
      <div>${message}</div>
    </div>
  `;
  
  notificationArea.style.display = 'block';
}

// Show confirmation section for Facebook connection
function showConnectConfirmation() {
  let confirmationSection = document.getElementById('facebook-confirmation-section');
  
  if (!confirmationSection) {
    confirmationSection = document.createElement('div');
    confirmationSection.id = 'facebook-confirmation-section';
    confirmationSection.className = 'mt-4 p-4 bg-blue-50 rounded-lg';
    
    confirmationSection.innerHTML = `
      <p class="mb-2">After you've connected your Facebook Business Manager, confirm below:</p>
      <button id="confirm-facebook-connection" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        I've Connected My Facebook Account
      </button>
    `;
    
    const notificationArea = document.getElementById('facebook-notification-area');
    if (notificationArea) {
      notificationArea.parentNode.insertBefore(confirmationSection, notificationArea.nextSibling);
    } else {
      const existingAssetsFlow = document.getElementById('existing-assets-flow');
      if (existingAssetsFlow) {
        existingAssetsFlow.appendChild(confirmationSection);
      }
    }
    
    // Add event listener to the confirmation button
    const confirmButton = document.getElementById('confirm-facebook-connection');
    if (confirmButton) {
      confirmButton.addEventListener('click', function() {
        confirmFacebookConnection();
      });
    }
  }
  
  confirmationSection.style.display = 'block';
}

// Show confirmation section for Ad Account
function showAdAccountConfirmation() {
  let confirmationSection = document.getElementById('ad-account-confirmation-section');
  
  if (!confirmationSection) {
    confirmationSection = document.createElement('div');
    confirmationSection.id = 'ad-account-confirmation-section';
    confirmationSection.className = 'mt-4 p-4 bg-blue-50 rounded-lg';
    
    confirmationSection.innerHTML = `
      <p class="mb-2">After you've set up your Ad Account, confirm below:</p>
      <button id="confirm-ad-account" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        I've Set Up My Ad Account
      </button>
    `;
    
    const notificationArea = document.getElementById('facebook-notification-area');
    if (notificationArea) {
      notificationArea.parentNode.insertBefore(confirmationSection, notificationArea.nextSibling);
    } else {
      const setupGuide = document.getElementById('setup-guide');
      if (setupGuide) {
        setupGuide.appendChild(confirmationSection);
      }
    }
    
    // Add event listener to the confirmation button
    const confirmButton = document.getElementById('confirm-ad-account');
    if (confirmButton) {
      confirmButton.addEventListener('click', function() {
        confirmAdAccountSetup();
      });
    }
  }
  
  confirmationSection.style.display = 'block';
}

// Confirm Facebook connection
function confirmFacebookConnection() {
  // Hide confirmation section
  const confirmationSection = document.getElementById('facebook-confirmation-section');
  if (confirmationSection) {
    confirmationSection.style.display = 'none';
  }
  
  // Update connected accounts list
  addConnectedAccount('Facebook Business Manager', 'facebook');
  
  // Show success message
  displaySuccessMessage('Facebook Business Manager successfully connected!');
  
  // Show the final confirmation button
  const confirmSocialBtn = document.getElementById('confirm-social-btn');
  if (confirmSocialBtn) {
    confirmSocialBtn.style.display = 'block';
  }
}

// Confirm Ad Account setup
function confirmAdAccountSetup() {
  // Hide confirmation section
  const confirmationSection = document.getElementById('ad-account-confirmation-section');
  if (confirmationSection) {
    confirmationSection.style.display = 'none';
  }
  
  // Update connected accounts list
  addConnectedAccount('Facebook Ad Account', 'ad-account');
  
  // Show success message
  displaySuccessMessage('Ad Account successfully set up!');
  
  // Show the final confirmation button
  const confirmSocialBtn = document.getElementById('confirm-social-btn');
  if (confirmSocialBtn) {
    confirmSocialBtn.style.display = 'block';
  }
}

// Add connected account to the list
function addConnectedAccount(name, type) {
  let connectedAccountsList = document.getElementById('connected-accounts-list');
  
  if (!connectedAccountsList) {
    // Create connected accounts section
    const connectedAccountsSection = document.createElement('div');
    connectedAccountsSection.id = 'connected-accounts-section';
    connectedAccountsSection.className = 'mt-6 p-4 bg-blue-50 rounded-lg';
    connectedAccountsSection.innerHTML = `
      <h3 class="text-lg font-semibold mb-3">Connected Accounts</h3>
      <div id="connected-accounts-list" class="space-y-2"></div>
    `;
    
    const socialModal = document.getElementById('social-modal');
    if (!socialModal) return;
    
    const existingAssetsFlow = document.getElementById('existing-assets-flow');
    if (existingAssetsFlow) {
      existingAssetsFlow.appendChild(connectedAccountsSection);
    } else {
      const setupGuide = document.getElementById('setup-guide');
      if (setupGuide) {
        setupGuide.appendChild(connectedAccountsSection);
      } else {
        socialModal.querySelector('.space-y-6').appendChild(connectedAccountsSection);
      }
    }
    
    connectedAccountsList = document.getElementById('connected-accounts-list');
  }
  
  // Check if this account is already in the list
  const existingAccount = document.querySelector(`[data-account-type="${type}"]`);
  if (existingAccount) return;
  
  // Create account item
  const accountItem = document.createElement('div');
  accountItem.className = 'flex items-center justify-between p-3 bg-white rounded-lg shadow-sm connected-account-item';
  accountItem.setAttribute('data-account-type', type);
  
  let icon = 'fa-facebook';
  let color = 'text-[#1877F2]';
  
  if (type === 'ad-account') {
    icon = 'fa-ad';
  } else if (type === 'instagram') {
    icon = 'fa-instagram';
    color = 'text-[#E4405F]';
  }
  
  accountItem.innerHTML = `
    <div class="flex items-center">
      <i class="fab ${icon} ${color} text-xl mr-3"></i>
      <span class="font-medium">${name}</span>
    </div>
    <span class="text-green-600 flex items-center text-sm">
      <i class="fas fa-check-circle mr-1"></i> Connected
    </span>
  `;
  
  connectedAccountsList.appendChild(accountItem);
  document.getElementById('connected-accounts-section').style.display = 'block';
}

// Export functions to be used in other scripts
window.fbIntegration = {
  showEnhancedUIInExistingAssetsFlow,
  showEnhancedSetupGuide,
  displaySuccessMessage,
  showConnectConfirmation,
  showAdAccountConfirmation,
  confirmFacebookConnection,
  confirmAdAccountSetup,
  addConnectedAccount
}; 