// Domain Search Fix - Addressing Modal Close Button Issues
document.addEventListener('DOMContentLoaded', function() {
  // Debug logging
  console.log("[domain-search-fix] Initializing domain search fix script");
  
  // Fix for domain search modal close buttons
  function fixDomainSearchModalCloseButtons() {
    // Select all close buttons within domain search modals
    const closeButtons = document.querySelectorAll('.domain-search-modal .close-button, .domain-search-modal .btn-close, .domain-search-modal [data-dismiss="modal"]');
    
    closeButtons.forEach(button => {
      // Remove existing event listeners by cloning the button
      const newButton = button.cloneNode(true);
      button.parentNode.replaceChild(newButton, button);
      
      // Add new event listener
      newButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log("[domain-search-fix] Close button clicked");
        
        // Find the modal container
        const modal = this.closest('.modal, .domain-search-modal');
        if (modal) {
          console.log("[domain-search-fix] Found modal to close:", modal.id || modal.className);
          
          // Hide the modal
          if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
              bsModal.hide();
            }
          } else {
            // Fallback for non-Bootstrap modals
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.classList.remove('modal-open');
            
            // Remove modal backdrop if exists
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
              backdrop.parentNode.removeChild(backdrop);
            }
          }
        }
      });
    });
    
    console.log("[domain-search-fix] Fixed", closeButtons.length, "close buttons");
  }
  
  // Run immediately
  fixDomainSearchModalCloseButtons();
  
  // Also observe DOM changes to handle dynamically added modals
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.addedNodes.length) {
        fixDomainSearchModalCloseButtons();
      }
    });
  });
  
  observer.observe(document.body, { childList: true, subtree: true });
  
  // Ensure that 'X' close buttons also work
  document.body.addEventListener('click', function(e) {
    if (e.target.textContent === '×' || e.target.innerHTML === '&times;' || 
        e.target.classList.contains('close') || e.target.classList.contains('btn-close')) {
      console.log("[domain-search-fix] Global handler caught close button click");
      const modal = e.target.closest('.modal, .domain-search-modal');
      if (modal) {
        e.preventDefault();
        e.stopPropagation();
        
        // Hide the modal
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
          const bsModal = bootstrap.Modal.getInstance(modal);
          if (bsModal) {
            bsModal.hide();
          }
        } else {
          // Fallback for non-Bootstrap modals
          modal.style.display = 'none';
          modal.classList.remove('show');
          document.body.classList.remove('modal-open');
          
          // Remove modal backdrop if exists
          const backdrop = document.querySelector('.modal-backdrop');
          if (backdrop) {
            backdrop.parentNode.removeChild(backdrop);
          }
        }
      }
    }
  });
});
