// Clear the verification signature pad
function clearVerificationSignature() {
    console.log('Clearing verification signature pad');
    const canvas = document.getElementById('verification-signature-pad');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

// Check if the verification signature pad has content
function hasVerificationSignature() {
    const canvas = document.getElementById('verification-signature-pad');
    if (!canvas) {
        return false;
    }
    
    const ctx = canvas.getContext('2d');
    const pixelData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    
    // Check if any pixel has alpha > 0 (meaning something was drawn)
    for (let i = 3; i < pixelData.length; i += 4) {
        if (pixelData[i] > 0) {
            return true;
        }
    }
    
    return false;
}

// Handle verification form submission
function submitVerificationForm() {
    console.log('Submitting verification form');
    try {
        // Validate form fields
        const firstName = document.getElementById('first-name')?.value;
        const lastName = document.getElementById('last-name')?.value;
        const businessName = document.getElementById('business-name')?.value;
        
        // Check required fields
        if (!firstName || !lastName || !businessName) {
            alert('Please fill in all required fields.');
            return false;
        }
        
        // Check agreement checkbox
        const agreementCheckbox = document.getElementById('agreementCheck');
        if (agreementCheckbox && !agreementCheckbox.checked) {
            alert('Please agree to the terms and conditions.');
            return false;
        }
        
        // Validate signature
        if (!hasVerificationSignature()) {
            alert('Please sign the agreement before submitting.');
            return false;
        }
        
        // Save signature data
        const canvas = document.getElementById('verification-signature-pad');
        if (canvas) {
            const signatureData = canvas.toDataURL();
            const signatureField = document.getElementById('signature_data');
            if (signatureField) {
                signatureField.value = signatureData;
            }
        }
        
        // If everything is valid, submit the form
        alert('Verification form submitted successfully!');
        // Close the modal
        closeModal('verification-modal');
        
        // Update UI if needed
        updateOnboardingProgress('verification', 'Completed');
        
        return true;
    } catch (error) {
        console.error('Error in submitVerificationForm:', error);
        alert('An error occurred while submitting the form. Please try again.');
        return false;
    }
}

// Initialize verification signature pad
function initializeVerificationSignature() {
    console.log('Initializing verification signature pad');
    try {
        const canvas = document.getElementById('verification-signature-pad');
        if (!canvas) {
            console.error('Verification signature pad canvas not found');
            return;
        }
        
        // Clone the canvas to remove any previous event listeners
        const oldCanvas = canvas;
        const freshCanvas = oldCanvas.cloneNode(true);
        oldCanvas.parentNode.replaceChild(freshCanvas, oldCanvas);
        
        // Set up new context
        const freshCtx = freshCanvas.getContext('2d');
        freshCtx.lineWidth = 2;
        freshCtx.lineCap = 'round';
        freshCtx.lineJoin = 'round';
        freshCtx.strokeStyle = '#000';
        
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        
        // Define mousedown handler
        const handleMouseDown = function(e) {
            isDrawing = true;
            const rect = freshCanvas.getBoundingClientRect();
            lastX = e.clientX - rect.left;
            lastY = e.clientY - rect.top;
        };
        
        // Define mousemove handler
        const handleMouseMove = function(e) {
            if (!isDrawing) return;
            const rect = freshCanvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            freshCtx.beginPath();
            freshCtx.moveTo(lastX, lastY);
            freshCtx.lineTo(x, y);
            freshCtx.stroke();
            
            lastX = x;
            lastY = y;
        };
        
        // Define mouseup handler
        const handleMouseUp = function() {
            isDrawing = false;
        };
        
        // Define touch handlers
        const handleTouchStart = function(e) {
            e.preventDefault();
            const rect = freshCanvas.getBoundingClientRect();
            const touch = e.touches[0];
            lastX = touch.clientX - rect.left;
            lastY = touch.clientY - rect.top;
            isDrawing = true;
        };
        
        const handleTouchMove = function(e) {
            e.preventDefault();
            if (!isDrawing) return;
            
            const rect = freshCanvas.getBoundingClientRect();
            const touch = e.touches[0];
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;
            
            freshCtx.beginPath();
            freshCtx.moveTo(lastX, lastY);
            freshCtx.lineTo(x, y);
            freshCtx.stroke();
            
            lastX = x;
            lastY = y;
        };
        
        const handleTouchEnd = function(e) {
            e.preventDefault();
            isDrawing = false;
        };
        
        // Add event listeners
        freshCanvas.addEventListener('mousedown', handleMouseDown);
        freshCanvas.addEventListener('mousemove', handleMouseMove);
        freshCanvas.addEventListener('mouseup', handleMouseUp);
        freshCanvas.addEventListener('mouseleave', handleMouseUp);
        
        freshCanvas.addEventListener('touchstart', handleTouchStart);
        freshCanvas.addEventListener('touchmove', handleTouchMove);
        freshCanvas.addEventListener('touchend', handleTouchEnd);
        
        // Draw a test line to confirm it's working
        freshCtx.beginPath();
        freshCtx.moveTo(50, 50);
        freshCtx.lineTo(60, 60);
        freshCtx.stroke();
        
        console.log('Verification signature pad initialized');
    } catch (error) {
        console.error('Error initializing verification signature pad:', error);
    }
} 