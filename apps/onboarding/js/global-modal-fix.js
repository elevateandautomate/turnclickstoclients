// Global Modal Fix for X Close Buttons
(function() {
  console.log('🔍 Global Modal Fix: Loading...');
  
  // Execute when DOM is ready
  function initModalFix() {
    console.log('🚀 Global Modal Fix: Initializing');
    
    // Function to handle closing a modal
    function closeModalElement(element) {
      if (!element) return;
      
      // Find the closest modal/dialog container
      const modal = element.closest('.modal') || 
                   element.closest('[role="dialog"]') || 
                   element.closest('[aria-modal="true"]') ||
                   element.closest('.modal-container');
      
      if (modal) {
        console.log('Global Modal Fix: Closing modal:', modal.id || 'unnamed modal');
        
        // Try multiple closing methods
        if (typeof window.closeModal === 'function' && modal.id) {
          // Try existing closeModal function first
          window.closeModal(modal.id);
        } else {
          // Fallback to direct style manipulation
          modal.style.display = 'none';
        }
      }
    }
    
    // Special handle for X close buttons
    function handleXButtons() {
      // Find all elements that are likely X buttons
      const closeButtons = document.querySelectorAll('button.close, span.close, .modal-close, [aria-label="Close"], .close-modal');
      
      console.log(`Global Modal Fix: Found ${closeButtons.length} close buttons`);
      
      closeButtons.forEach(button => {
        // Skip if already handled
        if (button.dataset.fixApplied) return;
        
        button.dataset.fixApplied = 'true';
        button.addEventListener('click', function(e) {
          console.log('Global Modal Fix: Close button clicked');
          e.preventDefault();
          e.stopPropagation();
          closeModalElement(this);
        });
      });
      
      // Special case for elements containing × character (common for close buttons)
      document.querySelectorAll('button, span').forEach(element => {
        if (element.textContent.trim() === '×' && !element.dataset.fixApplied) {
          console.log('Global Modal Fix: Found × button');
          element.dataset.fixApplied = 'true';
          element.addEventListener('click', function(e) {
            console.log('Global Modal Fix: × close button clicked');
            e.preventDefault();
            e.stopPropagation();
            closeModalElement(this);
          });
        }
      });
    }
    
    // Apply fixes immediately
    handleXButtons();
    
    // Global click handler as fallback
    document.addEventListener('click', function(e) {
      // Check for close buttons that might not have direct handlers
      if ((e.target.classList.contains('close') || 
           e.target.classList.contains('modal-close') || 
           e.target.classList.contains('close-modal') ||
           e.target.getAttribute('aria-label') === 'Close' ||
           e.target.textContent.trim() === '×') && 
          !e.target.dataset.clickHandled) {
        
        console.log('Global Modal Fix: Caught close click via global handler');
        e.target.dataset.clickHandled = 'true';
        e.preventDefault();
        e.stopPropagation();
        
        setTimeout(() => {
          delete e.target.dataset.clickHandled;
        }, 100);
        
        closeModalElement(e.target);
      }
    }, true); // Use capture phase to intercept early
    
    // ESC key handling
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        const visibleModals = document.querySelectorAll('.modal:not(.hidden), [role="dialog"]:not(.hidden)');
        if (visibleModals.length > 0) {
          console.log('Global Modal Fix: ESC key closing modal');
          closeModalElement(visibleModals[visibleModals.length - 1]);
        }
      }
    });
    
    // Observer for dynamically added content
    const observer = new MutationObserver(function(mutations) {
      let shouldCheckButtons = false;
      
      mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length > 0) {
          shouldCheckButtons = true;
        }
      });
      
      if (shouldCheckButtons) {
        console.log('Global Modal Fix: DOM changed, checking for new close buttons');
        handleXButtons();
      }
    });
    
    // Start observing
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
    
    console.log('✅ Global Modal Fix: Successfully applied');
  }
  
  // Run immediately if DOM is already loaded
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initModalFix();
  } else {
    // Otherwise wait for DOM to load
    document.addEventListener('DOMContentLoaded', initModalFix);
  }
  
  // Also run on load as a fallback
  window.addEventListener('load', initModalFix);
})(); 