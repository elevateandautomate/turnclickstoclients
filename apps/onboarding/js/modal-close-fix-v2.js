/**
 * Modal Close Fix v2
 * This script fixes issues with the X buttons not closing modals
 * Specifically targeting the structure of the onboarding portal modals
 */

console.log("[MODAL-CLOSE-FIX-V2] Initializing modal close button fix...");

// Wait for the DOM to be fully loaded
window.addEventListener("load", function() {
  console.log("[MODAL-CLOSE-FIX-V2] Window loaded, setting up close button handlers");
  
  // Find all elements that might be close buttons
  const closeButtons = document.querySelectorAll("button, span, div, i, a");
  const closeButtonCandidates = Array.from(closeButtons).filter(el => {
    // Check if the element contains an X or close icon
    const text = el.textContent.trim().toLowerCase();
    const classes = el.className.toLowerCase();
    const hasX = text === "x" || text === "×" || text === "close";
    const hasCloseClass = classes.includes("close") || classes.includes("x") || classes.includes("times");
    const hasCloseIcon = el.innerHTML.includes("fa-times") || el.innerHTML.includes("fa-close") || el.innerHTML.includes("&times;");
    
    return hasX || hasCloseClass || hasCloseIcon;
  });
  
  console.log(`[MODAL-CLOSE-FIX-V2] Found ${closeButtonCandidates.length} potential close buttons`);
  
  // Add click event listeners to all potential close buttons
  closeButtonCandidates.forEach(button => {
    // Find the parent modal
    let modal = button;
    let depth = 0;
    const maxDepth = 10; // Prevent infinite loops
    
    // Traverse up the DOM to find the modal
    while (modal && depth < maxDepth) {
      if (modal.classList && (
          modal.classList.contains("modal") || 
          modal.id && modal.id.includes("modal") ||
          modal.getAttribute("role") === "dialog"
        )) {
        break;
      }
      modal = modal.parentElement;
      depth++;
    }
    
    if (modal && modal.id) {
      console.log(`[MODAL-CLOSE-FIX-V2] Found close button for modal: ${modal.id}`);
      
      // Add click event listener
      button.addEventListener("click", function(event) {
        console.log(`[MODAL-CLOSE-FIX-V2] Close button clicked for modal: ${modal.id}`);
        event.preventDefault();
        event.stopPropagation();
        closeModal(modal.id);
        return false;
      });
    }
  });
  
  // Also directly target specific modals we know exist
  const knownModals = [
    "guide-modal", 
    "verification-modal", 
    "authorization-modal", 
    "slack-modal", 
    "domain-modal", 
    "a2p-modal", 
    "social-modal",
    "help-modal",
    "signatureModal"
  ];
  
  knownModals.forEach(modalId => {
    const modal = document.getElementById(modalId);
    if (modal) {
      console.log(`[MODAL-CLOSE-FIX-V2] Processing known modal: ${modalId}`);
      
      // Find all potential close elements in this modal
      const closeElements = modal.querySelectorAll(".close, .modal-close, .close-button, [aria-label=\"Close\"], button:first-child");
      
      closeElements.forEach(closeEl => {
        console.log(`[MODAL-CLOSE-FIX-V2] Adding click handler to close element in ${modalId}`);
        
        closeEl.addEventListener("click", function(event) {
          console.log(`[MODAL-CLOSE-FIX-V2] Close element clicked for modal: ${modalId}`);
          event.preventDefault();
          event.stopPropagation();
          closeModal(modalId);
          return false;
        });
      });
      
      // Add keyboard event listener to close on Escape key
      document.addEventListener("keydown", function(event) {
        if (event.key === "Escape" && modal.style.display === "block") {
          console.log(`[MODAL-CLOSE-FIX-V2] Escape key pressed, closing modal: ${modalId}`);
          closeModal(modalId);
        }
      });
    }
  });
  
  // Add a global click handler for any element with data-dismiss="modal"
  document.addEventListener("click", function(event) {
    const target = event.target;
    if (target.getAttribute("data-dismiss") === "modal") {
      console.log("[MODAL-CLOSE-FIX-V2] Clicked element with data-dismiss=modal");
      
      // Find the parent modal
      let modal = target.closest(".modal");
      if (modal && modal.id) {
        console.log(`[MODAL-CLOSE-FIX-V2] Closing modal: ${modal.id}`);
        closeModal(modal.id);
      }
    }
  });
});

console.log("[MODAL-CLOSE-FIX-V2] Modal close button fix initialized");
