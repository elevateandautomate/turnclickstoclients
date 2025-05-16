// A2P Button Fix - Comprehensive Solution
(function() {
  console.log("[A2P-Button-Fix] Script loaded");

  // Function to fix the "Learn More About A2P" buttons
  function fixLearnMoreButtons() {
    console.log("[A2P-Button-Fix] Attempting to fix Learn More buttons");

    // Fix the first Learn More button
    fixLearnMoreButtonById('learn-more-btn', 'learn-more-content');

    // Fix the second Learn More button
    fixLearnMoreButtonById('learn-more-btn-2', 'learn-more-content-2');
  }

  // Helper function to fix a specific Learn More button by ID
  function fixLearnMoreButtonById(buttonId, contentId) {
    console.log(`[A2P-Button-Fix] Attempting to fix button with ID: ${buttonId}`);

    // Try finding the specific button
    const button = document.getElementById(buttonId);

    if (button) {
      console.log(`[A2P-Button-Fix] Button found: ${buttonId}`);

      const content = document.getElementById(contentId);

      if (content) {
        console.log(`[A2P-Button-Fix] Content found: ${contentId}`);

        // Remove any existing click event listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);

        // Add new click event listener
        newButton.addEventListener('click', function(e) {
          e.preventDefault();
          console.log(`[A2P-Button-Fix] Button clicked: ${buttonId}`);

          // Toggle content visibility
          if (content.classList.contains('hidden')) {
            content.classList.remove('hidden');
            // Find and rotate chevron if it exists
            const icon = this.querySelector('i.fa-chevron-down');
            if (icon) {
              icon.classList.remove('fa-chevron-down');
              icon.classList.add('fa-chevron-up');
            }
          } else {
            content.classList.add('hidden');
            // Find and rotate chevron if it exists
            const icon = this.querySelector('i.fa-chevron-up');
            if (icon) {
              icon.classList.remove('fa-chevron-up');
              icon.classList.add('fa-chevron-down');
            }
          }
        });

        console.log(`[A2P-Button-Fix] Event listener attached to: ${buttonId}`);
      } else {
        console.warn(`[A2P-Button-Fix] Content not found: ${contentId}`);
      }
    } else {
      console.warn(`[A2P-Button-Fix] Button not found: ${buttonId}`);
    }
  }

  // Function to fix the "Submit Registration" button
  function fixSubmitButton() {
    console.log("[A2P-Button-Fix] Attempting to fix Submit Registration button");

    // Find the submit button
    const submitButton = document.querySelector('.btn-submit');

    if (submitButton) {
      console.log("[A2P-Button-Fix] Submit button found:", submitButton);

      // Remove any existing click event listeners
      const newSubmitButton = submitButton.cloneNode(true);
      submitButton.parentNode.replaceChild(newSubmitButton, submitButton);

      // Add new click event listener
      newSubmitButton.addEventListener('click', function(e) {
        e.preventDefault();
        console.log("[A2P-Button-Fix] Submit button clicked");

        // Call the handleA2PSubmitClick function
        if (typeof handleA2PSubmitClick === 'function') {
          console.log("[A2P-Button-Fix] Calling handleA2PSubmitClick function");
          handleA2PSubmitClick();
        } else {
          console.error("[A2P-Button-Fix] handleA2PSubmitClick function not found");

          // Fallback: Try to call submitA2PForm directly
          if (typeof submitA2PForm === 'function') {
            console.log("[A2P-Button-Fix] Calling submitA2PForm function directly");
            submitA2PForm();
          } else {
            console.error("[A2P-Button-Fix] submitA2PForm function not found");
            alert("Error: Could not submit the form. Please contact support.");
          }
        }
      });

      console.log("[A2P-Button-Fix] Submit button event listener attached");
    } else {
      console.warn("[A2P-Button-Fix] Submit button not found");
    }
  }

  // Define global toggleLearnMore function
  window.toggleLearnMore = function() {
    console.log("[A2P-Button-Fix] Global toggleLearnMore function called");

    const content = document.getElementById('learn-more-content');
    const button = document.getElementById('learn-more-btn');

    if (content) {
      if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        // Find and rotate chevron if it exists
        if (button) {
          const icon = button.querySelector('i.fa-chevron-down');
          if (icon) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
          }
        }
      } else {
        content.classList.add('hidden');
        // Find and rotate chevron if it exists
        if (button) {
          const icon = button.querySelector('i.fa-chevron-up');
          if (icon) {
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
          }
        }
      }
      console.log("[A2P-Button-Fix] Content toggled, hidden:", content.classList.contains('hidden'));
    }
  };

  // Define global toggleLearnMore2 function for the second button
  window.toggleLearnMore2 = function() {
    console.log("[A2P-Button-Fix] Global toggleLearnMore2 function called");

    const content = document.getElementById('learn-more-content-2');
    const button = document.getElementById('learn-more-btn-2');

    if (content) {
      if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        // Find and rotate chevron if it exists
        if (button) {
          const icon = button.querySelector('i.fa-chevron-down');
          if (icon) {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
          }
        }
      } else {
        content.classList.add('hidden');
        // Find and rotate chevron if it exists
        if (button) {
          const icon = button.querySelector('i.fa-chevron-up');
          if (icon) {
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
          }
        }
      }
      console.log("[A2P-Button-Fix] Content 2 toggled, hidden:", content.classList.contains('hidden'));
    }
  };

  // Function to fix all A2P buttons
  function fixAllA2PButtons() {
    console.log("[A2P-Button-Fix] Fixing all A2P buttons");
    fixLearnMoreButtons();
    fixSubmitButton();
  }

  // Run fix function when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixAllA2PButtons);
  } else {
    // DOM is already loaded, try running immediately
    fixAllA2PButtons();
    // Also run after a short delay in case of timing issues
    setTimeout(fixAllA2PButtons, 500);
  }

  // Set up a MutationObserver to watch for the buttons being added later
  const observer = new MutationObserver(function(mutationsList) {
    for (const mutation of mutationsList) {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach(node => {
          // Check if the added node contains any of our target buttons
          if (node.nodeType === 1) { // Check if it's an element node
            if (node.id === 'learn-more-btn' ||
                node.id === 'learn-more-btn-2' ||
                node.querySelector('#learn-more-btn') ||
                node.querySelector('#learn-more-btn-2') ||
                node.classList.contains('btn-submit') ||
                node.querySelector('.btn-submit')) {
              console.log('[A2P-Button-Fix] MutationObserver: Potential A2P button added');
              fixAllA2PButtons();
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

  // Also run the fix when the A2P modal is opened
  const originalShowA2PModal = window.showA2PModal;
  window.showA2PModal = function() {
    console.log("[A2P-Button-Fix] showA2PModal called");

    // Call the original function
    if (typeof originalShowA2PModal === 'function') {
      originalShowA2PModal();
    } else {
      console.warn("[A2P-Button-Fix] Original showA2PModal function not found");

      // Fallback: Try to open the modal directly
      const modal = document.getElementById('a2p-modal');
      if (modal) {
        modal.style.display = 'block';
      }
    }

    // Fix the buttons after a short delay
    setTimeout(fixAllA2PButtons, 500);
  };

  console.log("[A2P-Button-Fix] Script initialization complete");
})();
