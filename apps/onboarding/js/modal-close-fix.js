/**
 * Modal Close Fix
 * This script fixes issues with the X buttons not closing modals
 */

console.log("[MODAL-CLOSE-FIX] Initializing modal close button fix...");

document.addEventListener("DOMContentLoaded", function() {
  console.log("[MODAL-CLOSE-FIX] DOM loaded, setting up close button handlers");
  
  // Find all modal close buttons (X buttons)
  const closeButtons = document.querySelectorAll(".modal-close, .close-button, .close-modal, [data-close=\"modal\"]");
  
  console.log(`[MODAL-CLOSE-FIX] Found ${closeButtons.length} close buttons`);
  
  // Add click event listeners to all close buttons
  closeButtons.forEach(button => {
    console.log("[MODAL-CLOSE-FIX] Processing button:", button);
    
    // Get the parent modal
    const modal = button.closest(".modal");
    
    if (modal) {
      const modalId = modal.id;
      console.log(`[MODAL-CLOSE-FIX] Button is in modal: ${modalId}`);
      
      // Add new click listener
      button.addEventListener("click", function(event) {
        event.preventDefault();
        console.log(`[MODAL-CLOSE-FIX] Close button clicked for modal: ${modalId}`);
        closeModal(modalId);
      });
      
      console.log(`[MODAL-CLOSE-FIX] Added click handler to close button for modal: ${modalId}`);
    }
  });
  
  // Also add click handlers to modal backgrounds for closing when clicking outside
  const modals = document.querySelectorAll(".modal");
  
  modals.forEach(modal => {
    // Only add the event to the modal background, not the content
    modal.addEventListener("click", function(event) {
      // Check if the click was directly on the modal (background) and not on its children
      if (event.target === modal) {
        console.log(`[MODAL-CLOSE-FIX] Modal background clicked: ${modal.id}`);
        closeModal(modal.id);
      }
    });
  });
  
  // Make sure the closeModal function exists
  if (!window.closeModal) {
    console.log("[MODAL-CLOSE-FIX] Creating closeModal function");
    
    window.closeModal = function(modalId) {
      console.log(`[MODAL-CLOSE-FIX] Closing modal: ${modalId}`);
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.style.display = "none";
        console.log(`[MODAL-CLOSE-FIX] Modal ${modalId} closed`);
      } else {
        console.error(`[MODAL-CLOSE-FIX] Modal ${modalId} not found`);
      }
    };
  }
});

console.log("[MODAL-CLOSE-FIX] Modal close button fix initialized");
