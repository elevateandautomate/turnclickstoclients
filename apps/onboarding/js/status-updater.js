// Function to update the status of a step to "In Progress"
async function updateToInProgress(cardId, statusId) {
    // Get the status element
    const statusElement = document.getElementById(statusId);
    if (statusElement) {
        // Remove existing classes
        statusElement.className = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium in-progress-status';

        // Clear existing content
        statusElement.innerHTML = '';

        // Add orange dot
        const orangeDot = document.createElement('span');
        orangeDot.className = 'h-2 w-2 mr-1 rounded-full bg-orange-500';
        statusElement.appendChild(orangeDot);

        // Add text
        statusElement.appendChild(document.createTextNode('In Progress'));

        // Update the card class
        const cardElement = document.getElementById(cardId);
        if (cardElement) {
            cardElement.classList.remove('not-started');
            cardElement.classList.add('in-progress');
        }

        // Save the status to Supabase
        await saveStatusToSupabase(cardId, 'In Progress');
    }
}

// Function to save the status to Supabase
async function saveStatusToSupabase(cardId, status) {
    try {
        // Make sure we have Supabase client
        if (!window.supabaseClient) {
            console.error('Supabase client not found');
            return;
        }

        // Get current user
        const { data: { user } } = await window.supabaseClient.auth.getUser();
        if (!user) {
            console.error('No user found, cannot save status');
            return;
        }

        // Map card ID to database column
        const columnMapping = {
            'guide-card': 'guide_status',
            'verification-card': 'verification_status',
            'authorization-card': 'authorization_status',
            'slack-card': 'slack_status',
            'domain-card': 'domain_status',
            'a2p-card': 'a2p_status',
            'social-card': 'social_status'
        };

        const column = columnMapping[cardId];
        if (!column) {
            console.error('Unknown card ID:', cardId);
            return;
        }

        // First, check if a record already exists for this user
        const { data: existingRecord, error: fetchError } = await window.supabaseClient
            .from('new_client_onboarding')
            .select('*')
            .eq('user_id', user.id)
            .maybeSingle();

        if (fetchError) {
            console.error('Error checking for existing record:', fetchError);
            return;
        }

        // Create update object with all necessary fields
        let updateData = {
            user_id: user.id,
            [column]: status,
            updated_at: new Date().toISOString()
        };

        // If this is a new record, initialize all status fields to 'Not Started'
        if (!existingRecord) {
            console.log('Creating new onboarding record for user');
            // Initialize all status columns to 'Not Started'
            Object.values(columnMapping).forEach(col => {
                if (col !== column) { // Skip the current column being updated
                    updateData[col] = 'Not Started';
                }
            });
        }

        console.log('Saving status to Supabase:', updateData);

        // Update the database using upsert with onConflict option
        const { error } = await window.supabaseClient
            .from('new_client_onboarding')
            .upsert(updateData, { onConflict: 'user_id' });

        if (error) {
            console.error('Error saving status to Supabase:', error);
        } else {
            console.log('Status saved successfully to Supabase');
        }
    } catch (err) {
        console.error('Exception saving status to Supabase:', err);
    }
}

// Function to handle Getting Started Guide button click
async function handleGuideClick() {
    await updateToInProgress('guide-card', 'guide-status');
    showGuideModal();
}

// Function to handle A2P Registration button click
async function handleA2PClick() {
    try {
        console.log('A2P button clicked, updating status');

        // Get the status element directly
        const statusElement = document.getElementById('a2p-form-status');
        if (statusElement) {
            console.log('Found a2p-form-status element');

            // Check if status is already "In Progress" or "Completed"
            const currentStatus = statusElement.textContent.trim();
            if (currentStatus.includes('In Progress') || currentStatus.includes('Completed')) {
                console.log('Status is already:', currentStatus);
            } else {
                console.log('Updating status to In Progress');
                await updateToInProgress('a2p-card', 'a2p-form-status');
            }
        } else {
            console.error('Could not find a2p-form-status element');
        }

        // Show the modal
        if (typeof window.showA2PModal === 'function') {
            window.showA2PModal();
        } else {
            console.error('showA2PModal function not found');
            alert('Error: Could not open A2P form. Please refresh the page and try again.');
        }
    } catch (error) {
        console.error('Error in handleA2PClick:', error);

        // Still try to show the modal even if there's an error
        if (typeof window.showA2PModal === 'function') {
            window.showA2PModal();
        }
    }
}

// Function to handle Social Media Setup button click
async function handleSocialClick() {
    await updateToInProgress('social-card', 'social-card-status');
    showSocialModal();
}

// Add CSS for in-progress status
function addInProgressCSS() {
    // Create a style element
    const style = document.createElement('style');
    style.textContent = `
        .in-progress-status {
            background-color: #FFEDD5 !important; /* Light orange background */
            color: #EA580C !important; /* Orange text */
        }

        .step-card.in-progress {
            border-color: #F97316 !important; /* Orange border */
            background-color: #FFF7ED !important; /* Very light orange background */
        }
    `;
    document.head.appendChild(style);
}

// Add event listeners to buttons when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for in-progress status
    addInProgressCSS();

    // Find all buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        // Getting Started Guide button
        if (button.textContent.includes('Read Guide')) {
            // Remove existing onclick attribute
            button.removeAttribute('onclick');
            // Add new event listener
            button.addEventListener('click', handleGuideClick);
            console.log('Added event listener to Getting Started Guide button');
        }

        // A2P Registration button
        if (button.textContent.includes('Start Registration')) {
            // Remove existing onclick attribute
            button.removeAttribute('onclick');
            // Add new event listener
            button.addEventListener('click', handleA2PClick);
            console.log('Added event listener to A2P Registration button');
        }

        // Social Media Setup button
        if (button.textContent.includes('Connect Accounts')) {
            // Remove existing onclick attribute
            button.removeAttribute('onclick');
            // Add new event listener
            button.addEventListener('click', handleSocialClick);
            console.log('Added event listener to Social Media Setup button');
        }
    });
});
