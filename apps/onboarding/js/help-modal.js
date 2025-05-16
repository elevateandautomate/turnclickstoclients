// Simple inline help modal
(function() {
    // Show modal function
    async function showHelpModal(event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        console.log('[Help Modal] Showing help modal...');
        
        // Create a brand new modal using Tailwind classes
        const html = `
          <div id="help-request-modal" class="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center">
            <div class="bg-white rounded-lg shadow-xl w-full max-w-md mx-auto">
              <div class="flex justify-between items-center bg-blue-600 p-4 rounded-t-lg">
                <h3 class="text-xl font-semibold text-white">Request Assistance</h3>
                <button onclick="window.closeHelpModal()" class="text-white hover:text-gray-200 text-2xl">&times;</button>
              </div>
              <div class="p-6">
                <div class="mb-4 bg-blue-50 p-4 rounded-lg flex items-start">
                  <span class="text-blue-500 mr-2">ⓘ</span>
                  <p class="text-sm text-gray-700">Our team typically replies in 1-2 hours during business hours (10am-5pm Monday - Friday).</p>
                </div>
                <form id="help-request-form" onsubmit="submitHelpRequest(event)">
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label for="help-first-name" class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                      <input type="text" id="help-first-name" name="firstName" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="Your First Name">
                    </div>
                    <div>
                      <label for="help-last-name" class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                      <input type="text" id="help-last-name" name="lastName" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="Your Last Name">
                    </div>
                  </div>
                  <div class="mb-4">
                    <label for="help-email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input type="email" id="help-email" name="email" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="your.email@example.com">
                  </div>
                  <div class="mb-4">
                    <label for="help-phone" class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <input type="tel" id="help-phone" name="phone" class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="Your phone number">
                  </div>
                  <div class="mb-4">
                    <label for="help-message" class="block text-sm font-medium text-gray-700 mb-1">What do you need help with?</label>
                    <p class="text-xs text-gray-500 mb-2">Please provide a detailed summary of your question or issue so we can assist you effectively.</p>
                    <textarea id="help-message" name="message" rows="4" required class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" placeholder="Please describe the issue with specific details..."></textarea>
                  </div>
                  <div id="help-modal-error" class="text-red-600 text-sm mb-3 hidden"></div>
                  <div class="flex justify-end space-x-3">
                    <button type="button" onclick="window.closeHelpModal()" class="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">Cancel</button>
                    <button id="help-submit-btn" type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-wait">Submit Request</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        `;
        
        // Remove any existing modal
        const existingModal = document.getElementById('help-request-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add to document body
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        document.body.appendChild(tempDiv.firstElementChild);
        
        // Try to pre-fill user data if available
        try {
            if (window.supabaseClient) {
                const { data } = await window.supabaseClient.auth.getUser();
                if (data && data.user) {
                    const emailInput = document.getElementById('help-email');
                    if (emailInput) {
                        emailInput.value = data.user.email || '';
                    }

                    // Try to get user profile data
                    const { data: profileData } = await window.supabaseClient
                        .from('new_client_onboarding')
                        .select('first_name, last_name, phone, business_name')
                        .eq('user_id', data.user.id)
                        .maybeSingle();

                    if (profileData) {
                        const firstNameInput = document.getElementById('help-first-name');
                        const lastNameInput = document.getElementById('help-last-name');
                        const phoneInput = document.getElementById('help-phone');

                        if (firstNameInput && profileData.first_name) {
                            firstNameInput.value = profileData.first_name;
                        }

                        if (lastNameInput && profileData.last_name) {
                            lastNameInput.value = profileData.last_name;
                        }
                        
                        if (phoneInput && profileData.phone) {
                            phoneInput.value = profileData.phone;
                        }
                    }
                }
            }
        } catch (error) {
            console.error('[Help Modal] Error pre-filling user data:', error);
        }
        
        console.log('[Help Modal] Modal created and displayed');
    }
    
    // Hide modal function
    function closeHelpModal() {
        console.log('[Help Modal] Closing...');
        const modal = document.getElementById('help-request-modal');
        if (modal) {
            modal.remove(); // Remove the dynamically created modal
        }
    }
    
    // Expose functions to global scope
    window.showHelpModal = showHelpModal;
    window.closeHelpModal = closeHelpModal;
    window.submitHelpRequest = submitHelpRequest;
    
    // Helper function to capitalize first letter of a string
    function capitalizeFirstLetter(string) {
        if (!string) return '';
        return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
    }
    
    // Handle form submission
    async function submitHelpRequest(event) {
        event.preventDefault();
        console.log('[Help Modal] Submit initiated...');

        const firstName = document.getElementById('help-first-name').value.trim();
        const lastName = document.getElementById('help-last-name').value.trim();
        const email = document.getElementById('help-email').value.trim();
        const phone = document.getElementById('help-phone')?.value.trim() || '';
        const message = document.getElementById('help-message').value.trim();
        const errorDiv = document.getElementById('help-modal-error');
        const submitButton = document.getElementById('help-submit-btn');

        if (!firstName || !lastName || !email || !message) {
            errorDiv.textContent = 'Please fill out all required fields.';
            errorDiv.classList.remove('hidden');
            return;
        }
        
        errorDiv.classList.add('hidden');
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Sending...';

        // Capitalize first letter of names
        const formattedFirstName = capitalizeFirstLetter(firstName);
        const formattedLastName = capitalizeFirstLetter(lastName);
        
        // Get business name if available
        let businessName = 'Unknown Business';
        try {
            if (window.supabaseClient) {
                const { data: { user } } = await window.supabaseClient.auth.getUser();
                if (user) {
                    const { data: onboardingData } = await window.supabaseClient
                        .from('new_client_onboarding')
                        .select('business_name')
                        .eq('user_id', user.id)
                        .maybeSingle();
                    
                    if (onboardingData && onboardingData.business_name) {
                        businessName = onboardingData.business_name;
                    }
                }
            }
        } catch (error) {
            console.error('[Help Modal] Error getting business name:', error);
        }

        const formattedMessage = `
Help Request from ${formattedFirstName} ${formattedLastName}
Business: ${businessName}
Email: ${email}
Phone: ${phone || 'Not provided'}

Message:
${message}

--------------------------------------
        `.trim();

        try {
            const response = await fetch('https://onboardinghelp.onrender.com/send-slack-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    channel_id: 'C08Q1SK91MG',
                    message: formattedMessage
                })
            });

            if (!response.ok) {
                const resData = await response.json();
                throw new Error(resData.error || 'Failed to send message');
            }

            alert('Your help request has been received. Our team will get back to you soon, please continue with onboarding steps!');
            closeHelpModal();
        } catch (error) {
            console.error('[Help Modal] Error submitting help request:', error);
            errorDiv.textContent = 'Something went wrong. Please try again later.';
            errorDiv.classList.remove('hidden');
            submitButton.disabled = false;
            submitButton.innerHTML = 'Submit Request';
        }
    }
    
    // Initialize event listeners and expose help modal trigger to global scope
    function init() {
        // Set up event listeners only after the DOM is fully loaded
        document.addEventListener('DOMContentLoaded', () => {
            // Override requestSetupHelp if it exists
            if (typeof window.requestSetupHelp === 'function') {
                console.log('[Help Modal] Overriding window.requestSetupHelp to show modal.');
                // Keep the original function name but change its behavior
                window.requestSetupHelp = showHelpModal;
            } else {
                // Define it if it doesn't exist
                window.requestSetupHelp = showHelpModal;
            }

            // Find all "Request Assistance" and "Help" buttons and attach the handler
            const helpButtons = Array.from(document.querySelectorAll('button, a')).filter(el => {
                const text = el.textContent.toLowerCase();
                return text.includes('request assistance') || 
                       text.includes('help') ||
                       text.includes('support') ||
                       text.includes('instant message');
            });
            
            helpButtons.forEach(button => {
                button.addEventListener('click', showHelpModal);
                console.log('[Help Modal] Attached help modal to:', button.textContent);
            });
        });
    }

    // Run initialization
    init();
})(); 