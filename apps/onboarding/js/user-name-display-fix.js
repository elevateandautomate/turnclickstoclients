// User Name Display Fix
// This script fixes the user name display to show the first name with first letter capitalized

(function() {
  console.log('[User Name Display Fix] Script loaded');

  // Function to update the user name display
  async function updateUserNameDisplayFixed() {
    console.log('[User Name Display Fix] Updating user name display');

    try {
      // Get the current user
      const { data: { user } } = await window.supabase.auth.getUser();

      if (!user) {
        console.log('[User Name Display Fix] No user logged in');
        return;
      }

      console.log('[User Name Display Fix] User data:', user);

      // Get the user name element
      const userNameElement = document.getElementById('user-name');

      if (!userNameElement) {
        console.error('[User Name Display Fix] User name element not found');
        return;
      }

      // Try to get the first name from user metadata
      let firstName = '';

      if (user.user_metadata && user.user_metadata.first_name) {
        // Get first name from user metadata
        firstName = user.user_metadata.first_name;
        console.log('[User Name Display Fix] Found first name in user metadata:', firstName);
      } else {
        // If first name is not in metadata, try to get it from the new_client_onboarding table
        try {
          const { data: onboardingData, error } = await window.supabase
            .from('new_client_onboarding')
            .select('first_name')
            .eq('user_id', user.id)
            .maybeSingle();

          if (error) {
            console.error('[User Name Display Fix] Error fetching onboarding data:', error);
          } else if (onboardingData && onboardingData.first_name) {
            firstName = onboardingData.first_name;
            console.log('[User Name Display Fix] Found first name in onboarding table:', firstName);
          } else {
            // If not in onboarding table, try the profiles table
            const { data: profile, error: profileError } = await window.supabase
              .from('profiles')
              .select('first_name')
              .eq('id', user.id)
              .single();

            if (profileError) {
              console.error('[User Name Display Fix] Error fetching profile:', profileError);
            } else if (profile && profile.first_name) {
              firstName = profile.first_name;
              console.log('[User Name Display Fix] Found first name in profiles table:', firstName);
            }
          }
        } catch (err) {
          console.error('[User Name Display Fix] Exception fetching profile:', err);
        }
      }

      // If we still don't have a first name, use the email prefix
      if (!firstName && user.email) {
        firstName = user.email.split('@')[0].split('.')[0];
        console.log('[User Name Display Fix] Using email prefix as first name:', firstName);
      }

      // Capitalize the first letter of the first name
      if (firstName) {
        firstName = firstName.charAt(0).toUpperCase() + firstName.slice(1);
        console.log('[User Name Display Fix] Capitalized first name:', firstName);
      }

      // Update the user name element with "Hello Firstname" format
      userNameElement.textContent = `Hello ${firstName || 'User'}!`;
      console.log('[User Name Display Fix] Updated user name display to:', userNameElement.textContent);

    } catch (err) {
      console.error('[User Name Display Fix] Exception updating user name display:', err);
    }
  }

  // Define the original function if it doesn't exist yet
  if (typeof window.updateUserNameDisplay !== 'function') {
    window.updateUserNameDisplay = function() {
      console.log('[Original updateUserNameDisplay] Placeholder function called, will be replaced');
    };
  }

  // Override the existing updateUserNameDisplay function
  window.updateUserNameDisplay = updateUserNameDisplayFixed;

  // Call the function immediately if the user is already logged in
  if (window.currentUserEmail) {
    console.log('[User Name Display Fix] User already logged in, updating name display');
    updateUserNameDisplayFixed();
  }

  // Add event listener for auth state changes to update the name display
  window.supabase?.auth?.onAuthStateChange((event, session) => {
    if (event === 'SIGNED_IN' || event === 'USER_UPDATED') {
      console.log('[User Name Display Fix] Auth state changed, updating name display');
      setTimeout(updateUserNameDisplayFixed, 500); // Small delay to ensure DOM is ready
    }
  });

  // Also run on DOMContentLoaded to ensure it runs after page load
  document.addEventListener('DOMContentLoaded', () => {
    console.log('[User Name Display Fix] DOM loaded, checking if update needed');
    if (window.currentUserEmail) {
      updateUserNameDisplayFixed();
    }
  });

  console.log('[User Name Display Fix] Setup complete');
})();
