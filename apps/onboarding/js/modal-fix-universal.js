/**
 * Universal Modal Fix Script
 * This script handles closing modals by targeting all possible close button elements,
 * regardless of class names or structure.
 */
document.addEventListener('DOMContentLoaded', function() {
  console.log('📊 Universal Modal Fix: Initializing...');

  // Find all visible modals in the document
  function findVisibleModals() {
    // Look for elements that appear to be modals based on various indicators
    const possibleModals = Array.from(document.querySelectorAll('.modal, [class*="modal"], [id*="modal"], .fixed.inset-0'));
    return possibleModals.filter(modal => {
      const style = window.getComputedStyle(modal);
      return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
    });
  }

  // Close a specific modal
  function closeModalElement(element) {
    if (!element) return;
    
    console.log('🔒 Universal Modal Fix: Closing modal', element.id || element.className);
    
    // Try different methods to close the modal
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
      try {
        const bsModal = bootstrap.Modal.getInstance(element);
        if (bsModal) {
          bsModal.hide();
          return;
        }
      } catch (e) {
        console.log('Bootstrap method failed:', e);
      }
    }
    
    // Try direct DOM methods
    element.style.display = 'none';
    element.classList.remove('show', 'modal-open');
    
    // If there's a backdrop, remove it
    const backdrop = document.querySelector('.modal-backdrop');
    if (backdrop) backdrop.remove();
    
    // Remove modal-open class from body
    document.body.classList.remove('modal-open');
    
    // Dispatch a custom event that other scripts might listen for
    element.dispatchEvent(new CustomEvent('modalClosed', { bubbles: true }));
  }

  // Find all potential close buttons
  function attachCloseHandlers() {
    // Target any element that might be a close button
    const closeSelectors = [
      // Common close button selectors
      'button.close', '.btn-close', '[data-dismiss="modal"]', '.close',
      // X symbol buttons
      'button:has(i.fa-times)', 'button:has(i.fas.fa-times)', 'button:has(span:contains("×"))',
      // Any button with onclick containing closeModal
      'button[onclick*="closeModal"]',
      // Font awesome close icons
      'i.fa-times', 'i.fas.fa-times',
      // Any element with "close" in the ID
      '[id*="close"]'
    ];
    
    // Create a single selector from the array
    const allCloseSelectors = closeSelectors.join(', ');
    
    // Find and process all potential close buttons
    document.querySelectorAll(allCloseSelectors).forEach(closeBtn => {
      console.log('🔍 Universal Modal Fix: Found close button', closeBtn.outerHTML.slice(0, 50) + '...');
      
      // Remove any existing handler by cloning and replacing
      const newBtn = closeBtn.cloneNode(true);
      closeBtn.parentNode?.replaceChild(newBtn, closeBtn);
      
      // Add our event handler
      newBtn.addEventListener('click', function(e) {
        // Stop default action and event bubbling
        e.preventDefault();
        e.stopPropagation();
        
        // Find the modal this button belongs to
        const modal = this.closest('.modal, [class*="modal"], [id*="modal"], .fixed.inset-0');
        
        if (modal) {
          closeModalElement(modal);
        } else {
          // If we can't find the modal by DOM traversal, check for an ID in the onclick
          const onclickAttr = this.getAttribute('onclick');
          if (onclickAttr && onclickAttr.includes('closeModal')) {
            // Extract modal ID from the onclick attribute
            const match = onclickAttr.match(/closeModal\(['"](.*?)['"]\)/);
            if (match && match[1]) {
              const modalId = match[1];
              const targetModal = document.getElementById(modalId);
              if (targetModal) {
                closeModalElement(targetModal);
              }
            }
          } else {
            // Last resort: try to find any visible modal and close it
            const visibleModals = findVisibleModals();
            visibleModals.forEach(closeModalElement);
          }
        }
      });
    });
  }

  // Handle Escape key press to close modals
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      const visibleModals = findVisibleModals();
      visibleModals.forEach(closeModalElement);
    }
  });

  // Initial setup
  attachCloseHandlers();
  
  // Monitor DOM changes to handle dynamically added close buttons
  const observer = new MutationObserver(function(mutations) {
    let shouldCheck = false;
    
    mutations.forEach(function(mutation) {
      if (mutation.addedNodes.length > 0 || 
          mutation.type === 'attributes' && 
          (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
        shouldCheck = true;
      }
    });
    
    if (shouldCheck) {
      console.log('🔄 Universal Modal Fix: DOM changed, checking for new close buttons');
      attachCloseHandlers();
    }
  });
  
  // Start observing the body and all its descendants
  observer.observe(document.body, { 
    childList: true, 
    subtree: true,
    attributes: true,
    attributeFilter: ['class', 'style']
  });
  
  console.log('✅ Universal Modal Fix: Successfully initialized');
});

// Enhance closeModal function if it exists
if (typeof closeModal === 'function') {
  const originalCloseModal = closeModal;
  window.closeModal = function(modalId) {
    console.log('🔒 Universal Modal Fix: closeModal called for', modalId);
    try {
      originalCloseModal(modalId);
    } catch (e) {
      console.error('Original closeModal failed:', e);
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.style.display = 'none';
      }
    }
  };
} 