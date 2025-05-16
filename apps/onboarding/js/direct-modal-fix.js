/**
 * Direct Modal Close Fix
 * This script directly targets each modal and its close button
 */

console.log("[DIRECT-MODAL-FIX] Initializing direct modal close fix...");

// Wait for the DOM to be fully loaded
window.addEventListener("load", function() {
  console.log("[DIRECT-MODAL-FIX] Window loaded, applying direct modal fixes");
  
  // Define the modals and their close button selectors
  const modalConfigs = [
    { id: "guide-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "verification-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "authorization-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "slack-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "domain-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "a2p-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "social-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "help-modal", selector: ".modal-header button, .modal-header .close, .modal-header span" },
    { id: "signatureModal", selector: ".modal-header button, .modal-header .close, .modal-header span" }
  ];
  
  // Process each modal
  modalConfigs.forEach(config => {
    const modal = document.getElementById(config.id);
    if (!modal) {
      console.log(`[DIRECT-MODAL-FIX] Modal not found: ${config.id}`);
      return;
    }
    
    console.log(`[DIRECT-MODAL-FIX] Processing modal: ${config.id}`);
    
    // Find the close button using the selector
    const closeButtons = modal.querySelectorAll(config.selector);
    console.log(`[DIRECT-MODAL-FIX] Found ${closeButtons.length} close buttons for ${config.id}`);
    
    if (closeButtons.length === 0) {
      console.log(`[DIRECT-MODAL-FIX] No close buttons found for ${config.id}, creating one`);
      
      // Create a close button if none exists
      const modalHeader = modal.querySelector(".modal-header, .modal-content > div:first-child");
      if (modalHeader) {
        const closeButton = document.createElement("button");
        closeButton.type = "button";
        closeButton.className = "direct-modal-fix-close";
        closeButton.innerHTML = "&times;";
        closeButton.style.position = "absolute";
        closeButton.style.right = "10px";
        closeButton.style.top = "10px";
        closeButton.style.fontSize = "24px";
        closeButton.style.fontWeight = "bold";
        closeButton.style.border = "none";
        closeButton.style.background = "transparent";
        closeButton.style.cursor = "pointer";
        closeButton.style.zIndex = "9999";
        
        modalHeader.style.position = "relative";
        modalHeader.appendChild(closeButton);
        
        // Add click handler to the new close button
        closeButton.addEventListener("click", function(event) {
          console.log(`[DIRECT-MODAL-FIX] Close button clicked for ${config.id}`);
          event.preventDefault();
          event.stopPropagation();
          closeModal(config.id);
          return false;
        });
      }
    } else {
      // Add click handlers to all found close buttons
      closeButtons.forEach(button => {
        // Remove existing click listeners to avoid duplicates
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Add new click listener
        newButton.addEventListener("click", function(event) {
          console.log(`[DIRECT-MODAL-FIX] Close button clicked for ${config.id}`);
          event.preventDefault();
          event.stopPropagation();
          closeModal(config.id);
          return false;
        });
      });
    }
    
    // Also add a click handler to close when clicking outside the modal content
    modal.addEventListener("click", function(event) {
      if (event.target === modal) {
        console.log(`[DIRECT-MODAL-FIX] Modal background clicked for ${config.id}`);
        closeModal(config.id);
      }
    });
    
    // Add a direct close method to the modal
    modal.closeModal = function() {
      console.log(`[DIRECT-MODAL-FIX] Direct close method called for ${config.id}`);
      closeModal(config.id);
    };
  });
  
  // Override the closeModal function to ensure it works correctly
  const originalCloseModal = window.closeModal;
  window.closeModal = function(modalId) {
    console.log(`[DIRECT-MODAL-FIX] closeModal called for ${modalId}`);
    
    // Get the modal
    const modal = document.getElementById(modalId);
    if (!modal) {
      console.log(`[DIRECT-MODAL-FIX] Modal not found: ${modalId}`);
      return;
    }
    
    // Hide the modal
    modal.style.display = "none";
    
    // Call the original closeModal function if it exists
    if (originalCloseModal && typeof originalCloseModal === "function") {
      try {
        originalCloseModal(modalId);
      } catch (error) {
        console.log(`[DIRECT-MODAL-FIX] Error calling original closeModal: ${error}`);
      }
    }
    
    console.log(`[DIRECT-MODAL-FIX] Modal ${modalId} closed successfully`);
  };
  
  // Add keyboard support to close modals with Escape key
  document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
      // Find any visible modal
      const visibleModal = document.querySelector(".modal[style*=\"display: block\"], [role=\"dialog\"][style*=\"display: block\"]");
      if (visibleModal && visibleModal.id) {
        console.log(`[DIRECT-MODAL-FIX] Escape key pressed, closing modal: ${visibleModal.id}`);
        closeModal(visibleModal.id);
      }
    }
  });
});

console.log("[DIRECT-MODAL-FIX] Direct modal close fix initialized");
