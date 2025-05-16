/**
 * LOGOUT HANDLER (Simplified)
 * 
 * This script ensures users are redirected to the login page after logout
 * primarily using the Supabase auth state change listener.
 */

console.log('[LOGOUT v2] Logout handler script loaded');

// --- Primary Logout Trigger: Supabase Auth State Change --- 
document.addEventListener('DOMContentLoaded', function() {
  console.log('[LOGOUT v2] Setting up auth state change listener');
  
  // Check if Supabase client is available
  if (window.supabaseClient && window.supabaseClient.auth) {
    window.supabaseClient.auth.onAuthStateChange((event, session) => {
      console.log('[LOGOUT v2] Auth state changed:', event);
      
      if (event === 'SIGNED_OUT') {
        console.log('[LOGOUT v2] User signed out via Supabase event, redirecting...');
        redirectToLoginPage();
      }
    });
    console.log('[LOGOUT v2] Supabase auth state listener attached');
  } else {
    console.warn('[LOGOUT v2] Supabase client or auth module not found. Cannot listen for SIGNED_OUT event.');
  }
  
  // --- Backup Logout Trigger: Enhance Existing Function --- 
  // Try to enhance the existing handleLogout function if it exists
  if (typeof window.handleLogout === 'function') {
    console.log('[LOGOUT v2] Found existing handleLogout function, enhancing it...');
    const originalHandleLogout = window.handleLogout;
    
    window.handleLogout = async function(...args) {
      console.log('[LOGOUT v2] Enhanced handleLogout called');
      let originalFunctionError = false;
      try {
        // Call the original function
        await originalHandleLogout.apply(this, args);
        console.log('[LOGOUT v2] Original handleLogout completed.');
      } catch (error) {
        console.error('[LOGOUT v2] Error executing original handleLogout:', error);
        originalFunctionError = true;
      }
      
      // Force redirect, especially if the original function failed or didn't redirect
      console.log('[LOGOUT v2] Ensuring redirect after handleLogout call...');
      redirectToLoginPage(); 
    };
    console.log('[LOGOUT v2] handleLogout function enhanced.');
  } else {
    console.log('[LOGOUT v2] window.handleLogout function not found. Relying on button clicks.');
  }

  // --- Fallback Logout Trigger: Direct Button Listener --- 
  // Add listeners to buttons as a final fallback
  const logoutButtons = document.querySelectorAll('#logout-button, button[onclick*="signOut"], a[onclick*="signOut"]');
  logoutButtons.forEach(button => {
    console.log('[LOGOUT v2] Adding fallback listener to logout button:', button.id || 'No ID');
    button.addEventListener('click', function(e) {
      console.log('[LOGOUT v2] Fallback logout button listener triggered.');
      // Don't prevent default here, let Supabase signOut trigger the state change
      // Add a small delay before forcing redirect, in case Supabase event is slow
      setTimeout(redirectToLoginPage, 1500); 
    });
  });
});

// --- Redirect Function --- 
function redirectToLoginPage() {
  // Prevent multiple redirects
  if (window.location.pathname === '/' || window.location.pathname === '/index.html' || window.location.pathname === '/login.html') {
    console.log('[LOGOUT v2] Already on login/root page, redirect aborted.');
    return;
  }
  
  console.log('[LOGOUT v2] Redirecting to login page (/)...');
  // Use a short timeout to allow other cleanup tasks
  setTimeout(() => {
      window.location.href = '/'; 
  }, 100); 
}

console.log('[LOGOUT v2] Logout handler ready'); 