// Login Form Direct Fix
// This script completely replaces the login form handler with a direct implementation

(function() {
  console.log('[Login Form Direct Fix] Script loaded');

  // Function to completely replace the login form handler
  function replaceLoginFormHandler() {
    console.log('[Login Form Direct Fix] Replacing login form handler');

    // Find the login form
    const loginForm = document.getElementById('login-form');
    if (!loginForm) {
      console.error('[Login Form Direct Fix] Login form not found');
      return;
    }

    // Add a visual indicator that our fix is active
    const submitButton = loginForm.querySelector('button[type="submit"]');
    if (submitButton) {
      // Add a small green dot to the button
      const indicator = document.createElement('span');
      indicator.style.display = 'inline-block';
      indicator.style.width = '8px';
      indicator.style.height = '8px';
      indicator.style.backgroundColor = '#10B981'; // Green color
      indicator.style.borderRadius = '50%';
      indicator.style.marginLeft = '8px';

      submitButton.appendChild(indicator);

      // Also add a tooltip
      submitButton.title = 'Enhanced login enabled';

      console.log('[Login Form Direct Fix] Added visual indicator to login button');
    }

    // Remove all existing event listeners from the form
    const newForm = loginForm.cloneNode(true);
    loginForm.parentNode.replaceChild(newForm, loginForm);

    console.log('[Login Form Direct Fix] Cloned login form to remove existing event listeners');

    // Add our new event listener
    newForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      console.log('[Login Form Direct Fix] Login form submitted');

      // Show loading state
      const submitButton = newForm.querySelector('button[type="submit"]');
      const originalButtonText = submitButton ? submitButton.textContent : 'Login';
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';
      }

      // Clear any previous error messages
      let errorElement = document.getElementById('login-error');

      // If error element doesn't exist, create one
      if (!errorElement) {
        console.log('[Login Form Direct Fix] Creating login error element');
        errorElement = document.createElement('div');
        errorElement.id = 'login-error';
        errorElement.className = 'text-red-600 mt-4 text-sm w-full text-center';

        // Insert after the form
        newForm.parentNode.insertBefore(errorElement, newForm.nextSibling);
      }

      // Clear any existing error message
      errorElement.textContent = '';

      // Get input values
      const emailInput = document.getElementById('login-email');
      const passwordInput = document.getElementById('login-password');

      if (!emailInput || !passwordInput) {
        console.error('[Login Form Direct Fix] Email or password input not found');
        showError('Email or password field not found. Please refresh the page and try again.');
        resetButton();
        return;
      }

      const email = emailInput.value.trim();
      const password = passwordInput.value;

      // Validate inputs
      if (!email || !password) {
        showError('Please enter both email and password');
        resetButton();
        return;
      }

      console.log('[Login Form Direct Fix] Attempting login with email:', email);
      console.log('[Login Form Direct Fix] Password length:', password.length);

      try {
        // Check if Supabase is available
        if (!window.supabase) {
          console.error('[Login Form Direct Fix] Supabase client not found');
          showError('Supabase client not found. Please refresh the page and try again.');
          resetButton();
          return;
        }

        // Attempt to sign in directly with Supabase
        console.log('[Login Form Direct Fix] Calling supabase.auth.signInWithPassword');
        const { data, error } = await window.supabase.auth.signInWithPassword({
          email: email,
          password: password
        });

        if (error) {
          console.error('[Login Form Direct Fix] Error during login:', error);
          showError(error.message || 'Login failed. Please check your credentials.');
          resetButton();
          return;
        }

        console.log('[Login Form Direct Fix] Login successful!', data);

        // Show success message
        if (errorElement) {
          errorElement.style.color = '#10B981'; // Green color
          errorElement.textContent = 'Login successful! Redirecting...';
        }

        // Show dashboard
        const loginSection = document.getElementById('login-section');
        const dashboardSection = document.getElementById('dashboard-section');

        if (loginSection) loginSection.style.display = 'none';
        if (dashboardSection) dashboardSection.style.display = 'block';

        // Set current user email
        if (data.user) {
          window.currentUserEmail = data.user.email;
          console.log('[Login Form Direct Fix] Set currentUserEmail to:', window.currentUserEmail);

          // Update user name display if the function exists
          if (typeof updateUserNameDisplay === 'function') {
            updateUserNameDisplay();
          }

          // Load onboarding status if the function exists
          if (typeof loadAndApplyOnboardingStatus === 'function') {
            loadAndApplyOnboardingStatus();
          }
        }
      } catch (err) {
        console.error('[Login Form Direct Fix] Exception during login:', err);
        showError('An unexpected error occurred. Please try again.');
        resetButton();
      }

      // Helper function to reset button state
      function resetButton() {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = originalButtonText;
        }
      }

      // Helper function to show error message
      function showError(message) {
        if (errorElement) {
          errorElement.style.color = '#DC2626'; // Red color
          errorElement.textContent = message;
        } else {
          // Fallback to alert if somehow the error element is not available
          alert(message);
        }
      }
    });

    console.log('[Login Form Direct Fix] New login form handler added');

    // Also update the Test Direct Login button to use our direct login approach
    const testDirectLoginButton = document.getElementById('test-direct-login');
    if (testDirectLoginButton) {
      testDirectLoginButton.addEventListener('click', async function() {
        console.log('[Login Form Direct Fix] Test Direct Login button clicked');

        const emailInput = document.getElementById('login-email');
        const passwordInput = document.getElementById('login-password');

        if (!emailInput || !passwordInput) {
          alert('Email or password field not found');
          return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email || !password) {
          alert('Please enter both email and password');
          return;
        }

        // Trigger the form submission
        const submitButton = newForm.querySelector('button[type="submit"]');
        if (submitButton) {
          submitButton.click();
        } else {
          // If we can't find the submit button, just call the handler directly
          newForm.dispatchEvent(new Event('submit'));
        }
      });
    }
  }

  // Wait for the page to fully load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', replaceLoginFormHandler);
  } else {
    replaceLoginFormHandler();
  }
})();
