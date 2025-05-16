// A2P Form Fix - Consolidated Solution
(function() {
  console.log("[A2P-Form-Fix] Script loaded");
  
  // Main function to fix the A2P form
  function fixA2PForm() {
    console.log("[A2P-Form-Fix] Applying fixes to A2P form");
    
    // 1. Fix the form submission
    fixFormSubmission();
    
    // 2. Fix the navigation buttons
    fixNavigationButtons();
    
    // 3. Fix the submit button
    fixSubmitButton();
    
    console.log("[A2P-Form-Fix] All fixes applied");
  }
  
  // Function to fix form submission
  function fixFormSubmission() {
    console.log("[A2P-Form-Fix] Fixing form submission");
    
    // Find the A2P form
    const a2pForm = document.getElementById('a2p-form');
    if (a2pForm) {
      // Remove any existing event listeners
      const newForm = a2pForm.cloneNode(true);
      a2pForm.parentNode.replaceChild(newForm, a2pForm);
      
      // Add new submit event listener
      newForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log("[A2P-Form-Fix] Form submission prevented");
        return false;
      });
      
      console.log("[A2P-Form-Fix] Form submission fixed");
    } else {
      console.warn("[A2P-Form-Fix] A2P form not found");
    }
  }
  
  // Function to fix navigation buttons
  function fixNavigationButtons() {
    console.log("[A2P-Form-Fix] Fixing navigation buttons");
    
    // Fix Next buttons
    document.querySelectorAll('.btn-next').forEach((button, index) => {
      // Get the step number from the onclick attribute
      const onclickAttr = button.getAttribute('onclick');
      let stepNumber = null;
      
      if (onclickAttr && onclickAttr.includes('validateAndNext')) {
        const match = onclickAttr.match(/validateAndNext\((\d+)\)/);
        if (match && match[1]) {
          stepNumber = parseInt(match[1], 10);
        }
      }
      
      if (stepNumber !== null) {
        // Remove any existing event listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add new click event listener
        newButton.addEventListener('click', function(e) {
          e.preventDefault();
          console.log(`[A2P-Form-Fix] Next button clicked for step ${stepNumber}`);
          
          // Handle next step
          handleNextStep(stepNumber);
        });
      }
    });
    
    // Fix Back buttons
    document.querySelectorAll('.btn-prev').forEach((button, index) => {
      // Get the step number from the onclick attribute
      const onclickAttr = button.getAttribute('onclick');
      let stepNumber = null;
      
      if (onclickAttr && onclickAttr.includes('prevStep')) {
        const match = onclickAttr.match(/prevStep\((\d+)\)/);
        if (match && match[1]) {
          stepNumber = parseInt(match[1], 10);
        }
      }
      
      if (stepNumber !== null) {
        // Remove any existing event listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add new click event listener
        newButton.addEventListener('click', function(e) {
          e.preventDefault();
          console.log(`[A2P-Form-Fix] Back button clicked for step ${stepNumber}`);
          
          // Handle previous step
          handlePrevStep(stepNumber);
        });
      }
    });
    
    console.log("[A2P-Form-Fix] Navigation buttons fixed");
  }
  
  // Function to fix submit button
  function fixSubmitButton() {
    console.log("[A2P-Form-Fix] Fixing submit button");
    
    // Find all Submit buttons
    document.querySelectorAll('.btn-submit').forEach((button, index) => {
      // Remove any existing event listeners
      const newButton = button.cloneNode(true);
      button.parentNode.replaceChild(newButton, button);
      
      // Add new click event listener
      newButton.addEventListener('click', function(e) {
        e.preventDefault();
        console.log("[A2P-Form-Fix] Submit button clicked");
        
        // Handle form submission
        handleSubmit(this);
      });
    });
    
    console.log("[A2P-Form-Fix] Submit button fixed");
  }
  
  // Function to handle next step
  function handleNextStep(step) {
    console.log(`[A2P-Form-Fix] Handling next step for step ${step}`);
    
    try {
      // Find the current step
      const currentStep = document.querySelector(`.form-step[data-step="${step}"]`);
      if (!currentStep) {
        console.error(`[A2P-Form-Fix] Current step ${step} not found`);
        return;
      }
      
      // Validate required fields
      const requiredFields = currentStep.querySelectorAll('[required]');
      let isValid = true;
      let firstInvalidField = null;
      
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          field.classList.add('border-red-500');
          if (!firstInvalidField) {
            firstInvalidField = field;
          }
        } else {
          field.classList.remove('border-red-500');
        }
      });
      
      if (!isValid) {
        alert('Please fill in all required fields for this step.');
        if (firstInvalidField) {
          firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
          if (firstInvalidField.focus) {
            setTimeout(() => firstInvalidField.focus(), 500);
          }
        }
        return;
      }
      
      // Hide current step
      currentStep.style.display = 'none';
      currentStep.classList.remove('active');
      
      // Show next step
      const nextStep = document.querySelector(`.form-step[data-step="${step + 1}"]`);
      if (nextStep) {
        nextStep.style.display = 'block';
        nextStep.classList.add('active');
        
        // If showing review step, populate review data
        if (step + 1 === 3) {
          populateReviewData();
        }
      } else {
        console.error(`[A2P-Form-Fix] Next step ${step + 1} not found`);
      }
    } catch (error) {
      console.error('[A2P-Form-Fix] Error handling next step:', error);
    }
  }
  
  // Function to handle previous step
  function handlePrevStep(step) {
    console.log(`[A2P-Form-Fix] Handling previous step for step ${step}`);
    
    try {
      // Find the current step
      const currentStep = document.querySelector(`.form-step[data-step="${step}"]`);
      if (!currentStep) {
        console.error(`[A2P-Form-Fix] Current step ${step} not found`);
        return;
      }
      
      // Hide current step
      currentStep.style.display = 'none';
      currentStep.classList.remove('active');
      
      // Show previous step
      const prevStep = document.querySelector(`.form-step[data-step="${step - 1}"]`);
      if (prevStep) {
        prevStep.style.display = 'block';
        prevStep.classList.add('active');
      } else {
        console.error(`[A2P-Form-Fix] Previous step ${step - 1} not found`);
      }
    } catch (error) {
      console.error('[A2P-Form-Fix] Error handling previous step:', error);
    }
  }
  
  // Function to populate review data
  function populateReviewData() {
    console.log('[A2P-Form-Fix] Populating review data');
    
    try {
      // Get values from form fields
      const fullName = document.getElementById('fullName')?.value || '';
      const email = document.getElementById('email')?.value || '';
      const phone = document.getElementById('phone')?.value || '';
      const ein = document.getElementById('ein')?.value || '';
      const businessName = document.getElementById('businessName')?.value || '';
      const businessAddress = document.getElementById('businessAddress')?.value || '';
      const businessCity = document.getElementById('businessCity')?.value || '';
      const businessState = document.getElementById('businessState')?.value || '';
      const businessZip = document.getElementById('businessZip')?.value || '';
      const cp575UploadInput = document.getElementById('cp575-upload');
      const cp575File = cp575UploadInput?.files[0]?.name || 'Not Uploaded';
      
      // Populate review fields
      if (document.getElementById('reviewFullName')) document.getElementById('reviewFullName').textContent = fullName;
      if (document.getElementById('reviewEmail')) document.getElementById('reviewEmail').textContent = email;
      if (document.getElementById('reviewPhone')) document.getElementById('reviewPhone').textContent = phone;
      if (document.getElementById('reviewEin')) document.getElementById('reviewEin').textContent = ein;
      if (document.getElementById('reviewBusinessName')) document.getElementById('reviewBusinessName').textContent = businessName;
      if (document.getElementById('reviewBusinessAddress')) document.getElementById('reviewBusinessAddress').textContent = businessAddress;
      if (document.getElementById('reviewBusinessCity')) document.getElementById('reviewBusinessCity').textContent = businessCity;
      if (document.getElementById('reviewBusinessState')) document.getElementById('reviewBusinessState').textContent = businessState;
      if (document.getElementById('reviewBusinessZip')) document.getElementById('reviewBusinessZip').textContent = businessZip;
      if (document.getElementById('reviewCP575')) document.getElementById('reviewCP575').textContent = cp575File;
    } catch (error) {
      console.error('[A2P-Form-Fix] Error populating review data:', error);
    }
  }
  
  // Function to handle form submission
  function handleSubmit(submitButton) {
    console.log('[A2P-Form-Fix] Handling form submission');
    
    try {
      // Check if checkbox is checked
      const checkbox = document.getElementById('confirmDetails');
      if (!checkbox || !checkbox.checked) {
        alert('Please confirm that your details are correct before submitting.');
        return;
      }
      
      // Disable submit button
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Submitting...';
      }
      
      // Collect form data
      const formData = {
        fullName: document.getElementById('fullName')?.value || '',
        email: document.getElementById('email')?.value || '',
        phone: document.getElementById('phone')?.value || '',
        ein: document.getElementById('ein')?.value || '',
        businessName: document.getElementById('businessName')?.value || '',
        businessAddress: document.getElementById('businessAddress')?.value || '',
        businessCity: document.getElementById('businessCity')?.value || '',
        businessState: document.getElementById('businessState')?.value || '',
        businessZip: document.getElementById('businessZip')?.value || ''
      };
      
      console.log('[A2P-Form-Fix] Form data:', formData);
      
      // Update Supabase with the A2P status
      updateA2PStatus('Completed')
        .then(() => {
          // Show success message
          alert('A2P registration submitted successfully!');
          
          // Close the modal
          closeModal('a2p-modal');
          
          // Update the A2P card status
          updateStepUICard('a2p-card', 'a2p-form-status', 'Completed');
        })
        .catch(error => {
          console.error('[A2P-Form-Fix] Error updating A2P status:', error);
          alert('There was an error submitting your registration. Please try again.');
          
          // Re-enable button
          if (submitButton) {
            submitButton.disabled = false;
            submitButton.innerHTML = 'Submit Registration';
          }
        });
    } catch (error) {
      console.error('[A2P-Form-Fix] Error handling form submission:', error);
      
      // Re-enable button
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = 'Submit Registration';
      }
    }
  }
  
  // Function to update A2P status in Supabase
  async function updateA2PStatus(status) {
    console.log(`[A2P-Form-Fix] Updating A2P status to: ${status}`);
    
    try {
      const { data: { user } } = await window.supabase.auth.getUser();
      if (!user) {
        throw new Error('User not logged in');
      }
      
      const { error } = await window.supabase
        .from('new_client_onboarding')
        .update({
          a2p_status: status,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', user.id);
      
      if (error) {
        throw error;
      }
      
      console.log('[A2P-Form-Fix] A2P status updated successfully');
    } catch (error) {
      console.error('[A2P-Form-Fix] Error updating A2P status:', error);
      throw error;
    }
  }
  
  // Run the fix when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixA2PForm);
  } else {
    // DOM is already loaded, run immediately
    fixA2PForm();
    
    // Also run after a short delay in case of timing issues
    setTimeout(fixA2PForm, 500);
  }
  
  // Set up a MutationObserver to watch for changes
  const observer = new MutationObserver(function(mutationsList) {
    for (const mutation of mutationsList) {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach(node => {
          // Check if the added node contains any A2P elements
          if (node.nodeType === 1) { // Check if it's an element node
            if (node.id === 'a2p-form' || 
                node.id === 'a2p-modal' ||
                node.querySelector('#a2p-form') ||
                node.querySelector('#a2p-modal') ||
                node.querySelector('.btn-next') ||
                node.querySelector('.btn-prev') ||
                node.querySelector('.btn-submit')) {
              console.log('[A2P-Form-Fix] MutationObserver: A2P element added');
              fixA2PForm();
            }
          }
        });
      }
    }
  });
  
  // Observe the body for additions/changes
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: false
  });
  
  console.log("[A2P-Form-Fix] Script initialization complete");
})();
