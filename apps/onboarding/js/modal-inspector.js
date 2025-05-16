/**
 * MODAL STRUCTURE INSPECTOR
 * This script inspects the social modal and outputs its structure to the console
 */

(function() {
  console.log("INSPECTOR: Modal inspector script loaded");

  // Function to inspect the modal when it's visible
  function inspectModal() {
    console.log("----- MODAL INSPECTION START -----");
    
    // Find the social modal
    const socialModal = document.getElementById('social-modal');
    if (!socialModal) {
      console.error("INSPECTOR: Social modal not found!");
      return;
    }
    
    console.log("INSPECTOR: Found social modal:", socialModal);
    console.log("INSPECTOR: Modal display style:", socialModal.style.display);
    console.log("INSPECTOR: Modal visibility:", socialModal.style.visibility);
    console.log("INSPECTOR: Modal classes:", socialModal.className);
    
    // Get the HTML structure
    console.log("INSPECTOR: Modal HTML structure:");
    console.log(socialModal.outerHTML);
    
    // Find the buttons
    const allDivsInModal = socialModal.querySelectorAll('div');
    console.log("INSPECTOR: Total divs in modal:", allDivsInModal.length);
    
    const possibleYesButtons = Array.from(allDivsInModal).filter(div => 
      div.textContent.includes('Yes') || 
      div.textContent.includes('existing assets') ||
      (div.onclick && div.onclick.toString().includes('Existing'))
    );
    
    const possibleNoButtons = Array.from(allDivsInModal).filter(div => 
      div.textContent.includes('No') || 
      div.textContent.includes('set them up') ||
      (div.onclick && div.onclick.toString().includes('Guide'))
    );
    
    console.log("INSPECTOR: Possible Yes buttons found:", possibleYesButtons.length);
    possibleYesButtons.forEach((btn, i) => {
      console.log(`INSPECTOR: Yes button candidate ${i}:`, {
        text: btn.textContent.trim(),
        onclick: btn.getAttribute('onclick'),
        id: btn.id,
        classes: btn.className
      });
    });
    
    console.log("INSPECTOR: Possible No buttons found:", possibleNoButtons.length);
    possibleNoButtons.forEach((btn, i) => {
      console.log(`INSPECTOR: No button candidate ${i}:`, {
        text: btn.textContent.trim(),
        onclick: btn.getAttribute('onclick'),
        id: btn.id,
        classes: btn.className
      });
    });
    
    // Find possible content divs
    const possibleContentDivs = Array.from(allDivsInModal).filter(div => 
      div.id === 'existing-assets-flow' || 
      div.id === 'setup-guide' ||
      div.className.includes('assets') ||
      div.className.includes('guide') ||
      div.style.display === 'none'
    );
    
    console.log("INSPECTOR: Possible content divs found:", possibleContentDivs.length);
    possibleContentDivs.forEach((div, i) => {
      console.log(`INSPECTOR: Content div candidate ${i}:`, {
        id: div.id,
        classes: div.className,
        display: div.style.display,
        visibility: div.style.visibility,
        children: div.children.length
      });
    });

    // Create a direct DOM explorer function
    window.exploreModalDOM = function() {
      const modal = document.getElementById('social-modal');
      console.log("INSPECTOR: Full modal DOM explorer:", modal);
      
      // Search for buttons with specific text
      const allElements = document.querySelectorAll('*');
      const yesButton = Array.from(allElements).find(el => 
        el.textContent.trim() === 'Yes, I have existing assets'
      );
      const noButton = Array.from(allElements).find(el => 
        el.textContent.trim() === 'No, I need to set them up'
      );
      
      console.log("INSPECTOR: Direct yes button search:", yesButton);
      console.log("INSPECTOR: Direct no button search:", noButton);
      
      // Return object for further inspection
      return {
        modal,
        yesButton,
        noButton,
        allDivsInModal: allDivsInModal,
        possibleYesButtons,
        possibleNoButtons,
        possibleContentDivs
      };
    };
    
    console.log("INSPECTOR: Created global explorer function. Call window.exploreModalDOM() to explore further.");
    console.log("----- MODAL INSPECTION END -----");
  }
  
  // Monitor for modal opening
  function setupInspector() {
    // Check every second if the modal is visible
    const checkInterval = setInterval(function() {
      const socialModal = document.getElementById('social-modal');
      if (socialModal && (socialModal.style.display === 'block' || socialModal.style.display === 'flex')) {
        console.log("INSPECTOR: Social modal is now visible, inspecting...");
        inspectModal();
        clearInterval(checkInterval);
        
        // Create a fix function to be called manually
        window.fixModalButtons = function() {
          console.log("INSPECTOR: Applying direct fix to modal buttons");
          
          // Find the buttons based on text content
          const allElements = document.querySelectorAll('*');
          const yesButton = Array.from(allElements).find(el => 
            el.textContent.trim() === 'Yes, I have existing assets'
          );
          const noButton = Array.from(allElements).find(el => 
            el.textContent.trim() === 'No, I need to set them up'
          );
          
          if (yesButton) {
            yesButton.removeAttribute('onclick');
            yesButton.addEventListener('click', function() {
              console.log("INSPECTOR: Yes button clicked via direct fix");
              const modal = document.getElementById('social-modal');
              const allDivs = modal.querySelectorAll('div');
              
              // Look for content divs
              const allDivsArray = Array.from(allDivs);
              
              // Find assets flow by size and position
              const largerDivs = allDivsArray.filter(div => div.offsetWidth > 200 && div.offsetHeight > 100);
              
              if (largerDivs.length >= 2) {
                console.log("INSPECTOR: Found larger content divs:", largerDivs);
                largerDivs[0].style.display = 'block';
                largerDivs[1].style.display = 'none';
              }
            });
            console.log("INSPECTOR: Fixed yes button:", yesButton);
          }
          
          if (noButton) {
            noButton.removeAttribute('onclick');
            noButton.addEventListener('click', function() {
              console.log("INSPECTOR: No button clicked via direct fix");
              const modal = document.getElementById('social-modal');
              const allDivs = modal.querySelectorAll('div');
              
              // Look for content divs
              const allDivsArray = Array.from(allDivs);
              
              // Find setup guide by size and position
              const largerDivs = allDivsArray.filter(div => div.offsetWidth > 200 && div.offsetHeight > 100);
              
              if (largerDivs.length >= 2) {
                console.log("INSPECTOR: Found larger content divs:", largerDivs);
                largerDivs[0].style.display = 'none';
                largerDivs[1].style.display = 'block';
              }
            });
            console.log("INSPECTOR: Fixed no button:", noButton);
          }
          
          console.log("INSPECTOR: Applied direct fix to buttons. Try clicking them now.");
        };
        
        console.log("INSPECTOR: Created global fix function. Call window.fixModalButtons() to apply a direct fix.");
      }
    }, 1000);
  }
  
  // Set up the inspector once the DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupInspector);
  } else {
    setupInspector();
  }
})(); 