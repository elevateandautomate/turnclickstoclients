// A2P Card Click Fix
(function() {
  console.log("[A2P-Card-Click-Fix] Script loaded");
  
  // Function to fix the A2P form when the A2P card is clicked
  function fixA2PCardClick() {
    console.log("[A2P-Card-Click-Fix] Setting up A2P card click handler");
    
    // Find the A2P card
    const a2pCard = document.getElementById('a2p-card');
    if (a2pCard) {
      console.log("[A2P-Card-Click-Fix] Found A2P card");
      
      // Add click event listener
      a2pCard.addEventListener('click', function(e) {
        console.log("[A2P-Card-Click-Fix] A2P card clicked");
        
        // Wait for the modal to open
        setTimeout(function() {
          console.log("[A2P-Card-Click-Fix] Applying fixes after card click");
          
          // Find the A2P form
          const a2pForm = document.getElementById('a2p-form');
          if (a2pForm) {
            console.log("[A2P-Card-Click-Fix] Found A2P form");
            
            // Remove action and method attributes
            a2pForm.removeAttribute('action');
            a2pForm.removeAttribute('method');
            
            // Add onsubmit attribute
            a2pForm.setAttribute('onsubmit', 'event.preventDefault(); return false;');
            
            // Add direct event listener
            a2pForm.addEventListener('submit', function(e) {
              e.preventDefault();
              e.stopPropagation();
              console.log("[A2P-Card-Click-Fix] Form submission prevented");
              return false;
            });
            
            // Replace all Next buttons
            const nextButtons = a2pForm.querySelectorAll('.btn-next');
            nextButtons.forEach((button, index) => {
              console.log(`[A2P-Card-Click-Fix] Processing Next button #${index + 1}`);
              
              // Create a new button
              const newButton = document.createElement('button');
              newButton.type = 'button';
              newButton.className = button.className;
              newButton.innerHTML = button.innerHTML;
              
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
                console.log(`[A2P-Card-Click-Fix] Found step number: ${stepNumber}`);
                
                // Add direct click handler
                newButton.addEventListener('click', function(e) {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log(`[A2P-Card-Click-Fix] Next button clicked for step ${stepNumber}`);
                  
                  // Find the current step
                  const currentStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
                  if (!currentStep) {
                    console.error(`[A2P-Card-Click-Fix] Current step ${stepNumber} not found`);
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
                  
                  // Show next step
                  const nextStep = document.querySelector(`.form-step[data-step="${stepNumber + 1}"]`);
                  if (nextStep) {
                    nextStep.style.display = 'block';
                    
                    // If showing review step, populate review data
                    if (stepNumber + 1 === 3) {
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
                    }
                  } else {
                    console.error(`[A2P-Card-Click-Fix] Next step ${stepNumber + 1} not found`);
                  }
                });
                
                // Replace the old button with the new one
                button.parentNode.replaceChild(newButton, button);
              }
            });
            
            // Replace all Back buttons
            const backButtons = a2pForm.querySelectorAll('.btn-prev');
            backButtons.forEach((button, index) => {
              console.log(`[A2P-Card-Click-Fix] Processing Back button #${index + 1}`);
              
              // Create a new button
              const newButton = document.createElement('button');
              newButton.type = 'button';
              newButton.className = button.className;
              newButton.innerHTML = button.innerHTML;
              
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
                console.log(`[A2P-Card-Click-Fix] Found step number: ${stepNumber}`);
                
                // Add direct click handler
                newButton.addEventListener('click', function(e) {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log(`[A2P-Card-Click-Fix] Back button clicked for step ${stepNumber}`);
                  
                  // Find the current step
                  const currentStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
                  if (!currentStep) {
                    console.error(`[A2P-Card-Click-Fix] Current step ${stepNumber} not found`);
                    return;
                  }
                  
                  // Hide current step
                  currentStep.style.display = 'none';
                  
                  // Show previous step
                  const prevStep = document.querySelector(`.form-step[data-step="${stepNumber - 1}"]`);
                  if (prevStep) {
                    prevStep.style.display = 'block';
                  } else {
                    console.error(`[A2P-Card-Click-Fix] Previous step ${stepNumber - 1} not found`);
                  }
                });
                
                // Replace the old button with the new one
                button.parentNode.replaceChild(newButton, button);
              }
            });
            
            // Replace all Submit buttons
            const submitButtons = a2pForm.querySelectorAll('.btn-submit');
            submitButtons.forEach((button, index) => {
              console.log(`[A2P-Card-Click-Fix] Processing Submit button #${index + 1}`);
              
              // Create a new button
              const newButton = document.createElement('button');
              newButton.type = 'button';
              newButton.className = button.className;
              newButton.innerHTML = button.innerHTML;
              
              // Add direct click handler
              newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("[A2P-Card-Click-Fix] Submit button clicked");
                
                // Check if checkbox is checked
                const checkbox = document.getElementById('confirmDetails');
                if (!checkbox || !checkbox.checked) {
                  alert('Please confirm that your details are correct before submitting.');
                  return;
                }
                
                // Disable submit button
                this.disabled = true;
                this.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Submitting...';
                
                // Call the original submit function if it exists
                if (typeof submitA2PForm === 'function') {
                  submitA2PForm();
                } else {
                  console.error("[A2P-Card-Click-Fix] submitA2PForm function not found");
                  
                  // Re-enable button
                  this.disabled = false;
                  this.innerHTML = 'Submit Registration';
                }
              });
              
              // Replace the old button with the new one
              button.parentNode.replaceChild(newButton, button);
            });
          }
        }, 500); // Wait 500ms for the modal to open
      });
    }
  }
  
  // Run the fix when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixA2PCardClick);
  } else {
    // DOM is already loaded, run immediately
    fixA2PCardClick();
  }
  
  console.log("[A2P-Card-Click-Fix] Script initialization complete");
})();
