/**
 * Main JavaScript for Contact Bot
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh dashboard if processing is in progress
    if (document.getElementById('refreshBtn')) {
        checkProcessingStatus();
    }
    
    // File input validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            validateFileInput(this);
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

/**
 * Check if processing is in progress and refresh if needed
 */
function checkProcessingStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            if (data.is_processing) {
                // If processing, refresh the page every 10 seconds
                setTimeout(function() {
                    location.reload();
                }, 10000);
            }
        })
        .catch(error => console.error('Error checking processing status:', error));
}

/**
 * Validate file input
 * @param {HTMLInputElement} input - File input element
 */
function validateFileInput(input) {
    const file = input.files[0];
    const fileError = document.getElementById('fileError');
    
    if (fileError) {
        fileError.textContent = '';
    }
    
    if (file) {
        // Check file extension
        const fileName = file.name;
        const fileExt = fileName.split('.').pop().toLowerCase();
        
        if (fileExt !== 'csv') {
            if (fileError) {
                fileError.textContent = 'Please upload a CSV file.';
            }
            input.value = '';
            return false;
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            if (fileError) {
                fileError.textContent = 'File size exceeds 5MB limit.';
            }
            input.value = '';
            return false;
        }
    }
    
    return true;
}

/**
 * Retry processing a contact
 * @param {string} contactId - Contact ID
 */
function retryContact(contactId) {
    fetch(`/api/retry/${contactId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Contact queued for retry. The page will refresh shortly.');
                setTimeout(function() {
                    location.reload();
                }, 2000);
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => console.error('Error retrying contact:', error));
}

/**
 * Format status for display
 * @param {boolean|null} status - Status value
 * @returns {string} Formatted status text
 */
function formatStatus(status) {
    if (status === true) return 'Success';
    if (status === false) return 'Failed';
    return 'Pending';
}
