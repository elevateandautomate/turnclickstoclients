// Direct A2P Dropdown Fix
(function() {
  console.log("A2P Fix Direct script loaded V2");
  const LISTENER_ATTACHED_ATTR = 'data-a2p-listener-attached';

  function fixA2PButton() {
    // Try finding the specific button first
    const button = document.getElementById('learn-more-btn');

    // If found and listener not yet attached
    if (button && !button.hasAttribute(LISTENER_ATTACHED_ATTR)) {
      console.log("A2P Button found by ID:", button);

      const content = document.getElementById('learn-more-content');

      if (content) {
        console.log("A2P content found:", content);

        // Add click event listener directly
        button.addEventListener('click', function(e) {
          e.preventDefault(); // Prevent default button action
          console.log("A2P Button clicked!");

          // Toggle content visibility using the hidden class
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

        // Mark the button as having the listener attached
        button.setAttribute(LISTENER_ATTACHED_ATTR, 'true');
        console.log("A2P Button event listener attached.");

      } else {
        console.warn("A2P content (#learn-more-content) not found when button was found.");
      }
    } else if (button && button.hasAttribute(LISTENER_ATTACHED_ATTR)) {
      // console.log("A2P Button already has listener attached."); // Optional: uncomment for debugging
    } else {
       console.log("A2P Button (#learn-more-btn) not found yet.");
    }
  }

  // Define global toggleLearnMore function
  window.toggleLearnMore = function() {
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
      console.log("Content toggled, hidden:", content.classList.contains('hidden'));
    }
  };

  // Run fix function attempt when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixA2PButton);
  } else {
    // DOM is already loaded, try running immediately
    fixA2PButton();
    // Also run after a short delay in case of timing issues
    setTimeout(fixA2PButton, 150);
  }

  // Set up a MutationObserver to watch for the button being added later
  // Only run the fix if the specific button node is added or its attributes change
  const observer = new MutationObserver(function(mutationsList) {
    for(const mutation of mutationsList) {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(node => {
                // Check if the added node *is* the button or *contains* the button
                if (node.nodeType === 1) { // Check if it's an element node
                   if (node.id === 'learn-more-btn' || node.querySelector('#learn-more-btn')) {
                      console.log('MutationObserver: learn-more-btn potentially added.');
                      fixA2PButton();
                   }
                }
            });
        } else if (mutation.type === 'attributes') {
            // If attributes change on the button itself (less likely needed but safe)
            if (mutation.target.id === 'learn-more-btn') {
                console.log('MutationObserver: learn-more-btn attributes changed.');
                fixA2PButton();
            }
        }
    }
  });

  // Observe the body for additions/changes
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true, // Also observe attribute changes, just in case
    attributeFilter: ['id'] // Focus on ID changes which might be relevant
  });

})(); 