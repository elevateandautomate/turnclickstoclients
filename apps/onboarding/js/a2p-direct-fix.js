// A2P Direct Fix
// This script provides a direct solution for opening the A2P modal and fixing navigation
(function() {
  console.log("[A2P-Direct-Fix] Script loaded");

  // Function to directly handle the Next button click without validation
  function handleNextButtonClick(stepNumber) {
    console.log(`[A2P-Direct-Fix] Handling Next button click for step ${stepNumber}`);

    try {
      // Get the current step element
      const currentStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
      if (!currentStep) {
        console.error(`[A2P-Direct-Fix] Step ${stepNumber} not found`);
        return;
      }

      // Get the next step element
      const nextStep = document.querySelector(`.form-step[data-step="${stepNumber + 1}"]`);
      if (!nextStep) {
        console.error(`[A2P-Direct-Fix] Next step ${stepNumber + 1} not found`);
        return;
      }

      // Hide current step
      currentStep.style.display = 'none';

      // Show next step
      nextStep.style.display = 'block';
      console.log(`[A2P-Direct-Fix] Moved from step ${stepNumber} to step ${stepNumber + 1}`);
    } catch (error) {
      console.error('[A2P-Direct-Fix] Error handling Next button click:', error);
    }
  }

  // Function to directly handle the Back button click
  function handleBackButtonClick(stepNumber) {
    console.log(`[A2P-Direct-Fix] Handling Back button click for step ${stepNumber}`);

    try {
      // Get the current step element
      const currentStep = document.querySelector(`.form-step[data-step="${stepNumber}"]`);
      if (!currentStep) {
        console.error(`[A2P-Direct-Fix] Step ${stepNumber} not found`);
        return;
      }

      // Get the previous step element
      const prevStep = document.querySelector(`.form-step[data-step="${stepNumber - 1}"]`);
      if (!prevStep) {
        console.error(`[A2P-Direct-Fix] Previous step ${stepNumber - 1} not found`);
        return;
      }

      // Hide current step
      currentStep.style.display = 'none';

      // Show previous step
      prevStep.style.display = 'block';
      console.log(`[A2P-Direct-Fix] Moved from step ${stepNumber} to step ${stepNumber - 1}`);
    } catch (error) {
      console.error('[A2P-Direct-Fix] Error handling Back button click:', error);
    }
  }

  // Function to fix the A2P form buttons
  function fixA2PFormButtons() {
    console.log('[A2P-Direct-Fix] Fixing A2P form buttons');

    try {
      // Get the A2P modal
      const a2pModal = document.getElementById('a2p-modal');
      if (!a2pModal) {
        console.error('[A2P-Direct-Fix] A2P modal not found');
        return;
      }

      // Fix Step 1 Next button
      const step1NextButton = a2pModal.querySelector('.form-step[data-step="1"] button.btn-next');
      if (step1NextButton) {
        console.log('[A2P-Direct-Fix] Found Step 1 Next button');

        // Remove any existing event listeners and onclick attribute
        step1NextButton.removeAttribute('onclick');
        const newStep1NextButton = step1NextButton.cloneNode(true);
        step1NextButton.parentNode.replaceChild(newStep1NextButton, step1NextButton);

        // Add direct event listener
        newStep1NextButton.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log('[A2P-Direct-Fix] Step 1 Next button clicked');
          handleNextButtonClick(1);
        });
      }

      // Fix Step 2 Back button
      const step2BackButton = a2pModal.querySelector('.form-step[data-step="2"] button:first-child');
      if (step2BackButton) {
        console.log('[A2P-Direct-Fix] Found Step 2 Back button');

        // Remove any existing event listeners and onclick attribute
        step2BackButton.removeAttribute('onclick');
        const newStep2BackButton = step2BackButton.cloneNode(true);
        step2BackButton.parentNode.replaceChild(newStep2BackButton, step2BackButton);

        // Add direct event listener
        newStep2BackButton.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log('[A2P-Direct-Fix] Step 2 Back button clicked');
          handleBackButtonClick(2);
        });
      }

      // Fix Step 2 Next button
      const step2NextButton = a2pModal.querySelector('.form-step[data-step="2"] button:last-child');
      if (step2NextButton) {
        console.log('[A2P-Direct-Fix] Found Step 2 Next button');

        // Remove any existing event listeners and onclick attribute
        step2NextButton.removeAttribute('onclick');
        const newStep2NextButton = step2NextButton.cloneNode(true);
        step2NextButton.parentNode.replaceChild(newStep2NextButton, step2NextButton);

        // Add direct event listener
        newStep2NextButton.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log('[A2P-Direct-Fix] Step 2 Next button clicked');
          handleNextButtonClick(2);
        });
      }

      // Fix Step 3 Back button
      const step3BackButton = a2pModal.querySelector('.form-step[data-step="3"] button:first-child');
      if (step3BackButton) {
        console.log('[A2P-Direct-Fix] Found Step 3 Back button');

        // Remove any existing event listeners and onclick attribute
        step3BackButton.removeAttribute('onclick');
        const newStep3BackButton = step3BackButton.cloneNode(true);
        step3BackButton.parentNode.replaceChild(newStep3BackButton, step3BackButton);

        // Add direct event listener
        newStep3BackButton.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          console.log('[A2P-Direct-Fix] Step 3 Back button clicked');
          handleBackButtonClick(3);
        });
      }

      console.log('[A2P-Direct-Fix] A2P form buttons fixed');
    } catch (error) {
      console.error('[A2P-Direct-Fix] Error fixing A2P form buttons:', error);
    }
  }

  // Create a direct button that will always work
  function createDirectButton() {
    console.log("[A2P-Direct-Fix] Creating direct button");

    // Create a floating button container
    const buttonContainer = document.createElement('div');
    buttonContainer.id = 'a2p-direct-buttons';
    buttonContainer.style.position = 'fixed';
    buttonContainer.style.bottom = '20px';
    buttonContainer.style.right = '20px';
    buttonContainer.style.zIndex = '10000';
    buttonContainer.style.display = 'flex';
    buttonContainer.style.flexDirection = 'column';
    buttonContainer.style.gap = '10px';

    // Create the emergency button
    const emergencyButton = document.createElement('button');
    emergencyButton.id = 'a2p-emergency-button';
    emergencyButton.innerHTML = '⚠️ EMERGENCY: Open A2P Form';
    emergencyButton.style.padding = '15px 20px';
    emergencyButton.style.backgroundColor = '#FF4500';
    emergencyButton.style.color = 'white';
    emergencyButton.style.border = 'none';
    emergencyButton.style.borderRadius = '8px';
    emergencyButton.style.fontWeight = 'bold';
    emergencyButton.style.cursor = 'pointer';
    emergencyButton.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    emergencyButton.style.display = 'flex';
    emergencyButton.style.alignItems = 'center';
    emergencyButton.style.justifyContent = 'center';
    emergencyButton.style.fontSize = '16px';

    // Create the standard button
    const standardButton = document.createElement('button');
    standardButton.id = 'a2p-standard-button';
    standardButton.innerHTML = '📝 Open A2P Registration';
    standardButton.style.padding = '15px 20px';
    standardButton.style.backgroundColor = '#4CAF50';
    standardButton.style.color = 'white';
    standardButton.style.border = 'none';
    standardButton.style.borderRadius = '8px';
    standardButton.style.fontWeight = 'bold';
    standardButton.style.cursor = 'pointer';
    standardButton.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
    standardButton.style.display = 'flex';
    standardButton.style.alignItems = 'center';
    standardButton.style.justifyContent = 'center';
    standardButton.style.fontSize = '16px';

    // Add click handlers
    emergencyButton.addEventListener('click', openA2PModalDirect);
    standardButton.addEventListener('click', openA2PModalDirect);

    // Add to the container
    buttonContainer.appendChild(emergencyButton);
    buttonContainer.appendChild(standardButton);

    // Add to the page
    document.body.appendChild(buttonContainer);
    console.log("[A2P-Direct-Fix] Direct buttons added to page");
  }

  // Function to directly open the A2P modal
  function openA2PModalDirect() {
    console.log("[A2P-Direct-Fix] Opening A2P modal directly");

    try {
      // Get the A2P modal
      const a2pModal = document.getElementById('a2p-modal');

      if (!a2pModal) {
        console.error("[A2P-Direct-Fix] A2P modal not found");
        alert("Error: A2P modal not found. Please refresh the page and try again.");
        return;
      }

      console.log("[A2P-Direct-Fix] Found A2P modal, setting display to flex");

      // Show the modal
      a2pModal.style.display = 'flex';
      a2pModal.style.position = 'fixed';
      a2pModal.style.inset = '0';
      a2pModal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
      a2pModal.style.zIndex = '9999';
      a2pModal.style.alignItems = 'center';
      a2pModal.style.justifyContent = 'center';
      a2pModal.style.padding = '20px';

      // Fix the modal content
      const modalContent = a2pModal.querySelector('.relative');
      if (modalContent) {
        modalContent.style.maxHeight = '85vh';
        modalContent.style.overflowY = 'auto';
        modalContent.style.backgroundColor = 'white';
        modalContent.style.borderRadius = '8px';
        modalContent.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        modalContent.style.width = '95%';
        modalContent.style.maxWidth = '800px';
        modalContent.style.margin = '0 auto';
        modalContent.style.position = 'relative';
      }

      // Fix the form steps
      const formSteps = a2pModal.querySelectorAll('.form-step');
      formSteps.forEach((step, index) => {
        // Hide all steps except the first one
        if (index === 0) {
          step.style.display = 'block';
        } else {
          step.style.display = 'none';
        }

        // Fix step styling
        step.style.maxHeight = 'none';
        step.style.overflow = 'visible';
        step.style.paddingBottom = '60px';
      });

      // Override the closeModal function to make sure it works
      if (typeof window.closeModal !== 'function') {
        window.closeModal = function(modalId) {
          console.log("[A2P-Direct-Fix] Closing modal with ID:", modalId);
          const modal = document.getElementById(modalId);
          if (modal) {
            console.log("[A2P-Direct-Fix] Modal found, setting display to none");
            modal.style.display = 'none';
          } else {
            console.error("[A2P-Direct-Fix] Modal element not found:", modalId);
          }
        };
      }

      // Fix the form buttons
      setTimeout(function() {
        fixA2PFormButtons();
      }, 500);

      console.log("[A2P-Direct-Fix] A2P modal opened successfully");
    } catch (error) {
      console.error("[A2P-Direct-Fix] Error opening A2P modal:", error);
      alert("Error opening A2P form. Please try again.");
    }
  }

  // Function to observe the A2P modal for changes
  function observeA2PModal() {
    console.log('[A2P-Direct-Fix] Setting up observer for A2P modal');

    try {
      // Get the A2P modal
      const a2pModal = document.getElementById('a2p-modal');
      if (!a2pModal) {
        console.error('[A2P-Direct-Fix] A2P modal not found');
        return;
      }

      // Create a MutationObserver to watch for changes to the modal's style attribute
      const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
          if (mutation.attributeName === 'style') {
            const display = a2pModal.style.display;
            if (display === 'block' || display === 'flex') {
              console.log('[A2P-Direct-Fix] A2P modal is now visible, fixing buttons');
              fixA2PFormButtons();
            }
          }
        });
      });

      // Start observing the modal
      observer.observe(a2pModal, { attributes: true });

      console.log('[A2P-Direct-Fix] Observer set up for A2P modal');
    } catch (error) {
      console.error('[A2P-Direct-Fix] Error setting up observer:', error);
    }
  }

  // Run when the DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      createDirectButton();
      observeA2PModal();
    });
  } else {
    // DOM is already loaded, run immediately
    createDirectButton();
    observeA2PModal();
  }

  // Also run after a short delay to ensure it works
  setTimeout(function() {
    createDirectButton();
    observeA2PModal();

    // Also fix the buttons immediately in case the modal is already visible
    const a2pModal = document.getElementById('a2p-modal');
    if (a2pModal && (a2pModal.style.display === 'block' || a2pModal.style.display === 'flex')) {
      console.log('[A2P-Direct-Fix] A2P modal is already visible, fixing buttons');
      fixA2PFormButtons();
    }
  }, 1000);

  // Add a keyboard shortcut (Ctrl+Shift+A) to open the A2P modal
  document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.shiftKey && event.key === 'A') {
      console.log("[A2P-Direct-Fix] Keyboard shortcut triggered");
      openA2PModalDirect();
    }
  });

  // Expose the function globally
  window.openA2PModalDirect = openA2PModalDirect;

  console.log("[A2P-Direct-Fix] Script initialization complete");
})();
