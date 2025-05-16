/**
 * Split Test Redirect Script
 *
 * This script handles redirecting users to split test variations of results pages.
 * It should be included in all main variant pages (e.g., foundation-variant-a-solution.html)
 * to randomly distribute users to split test variations.
 */

// Add a global debug flag
const DEBUG_SPLIT_TEST = true;

// Helper function for logging
function debugLog(message) {
    if (DEBUG_SPLIT_TEST) {
        console.log(`[SPLIT TEST] ${message}`);
    }
}

// Add a global alert for testing
function debugAlert(message) {
    if (DEBUG_SPLIT_TEST) {
        alert(`[SPLIT TEST] ${message}`);
    }
}

// Execute immediately, don't wait for DOMContentLoaded
(function() {
    try {
        debugLog('Split test redirect script loaded');
        debugAlert('Split test redirect script loaded');

        // Check if this is a main variant page (not already a split test variation)
        const currentPath = window.location.pathname;
        debugLog(`Current path: ${currentPath}`);

        const isSplitVariation = currentPath.includes('-split');
        debugLog(`Is split variation: ${isSplitVariation}`);

        // Only redirect if this is a main variant page
        if (!isSplitVariation) {
            debugLog('This is a main variant page, checking for redirect');

            // Get URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const split = urlParams.get('split');
            debugLog(`Current split parameter: ${split}`);

            // Only redirect if split parameter is not already set or is set to 0
            if (!split || split === '0') {
                debugLog('Split parameter not set or is 0, proceeding with redirect');

                // Randomly select a split test variation (1, 2, or 3)
                const splitVariation = Math.floor(Math.random() * 3) + 1;
                debugLog(`Selected split variation: ${splitVariation}`);

                // Construct the new URL for the split test variation
                const newPath = currentPath.replace('.html', `-split${splitVariation}.html`);
                debugLog(`New path: ${newPath}`);

                // Add or update the split parameter in the query string
                urlParams.set('split', splitVariation.toString());
                const newSearch = urlParams.toString();
                debugLog(`New query string: ${newSearch}`);

                // Construct the full URL
                const newUrl = newPath + (newSearch ? `?${newSearch}` : '');
                debugLog(`Full redirect URL: ${newUrl}`);

                // Skip the fetch check and directly redirect
                // This avoids potential CORS issues when running locally
                debugLog(`Redirecting to split test variation: ${newUrl}`);
                debugAlert(`Redirecting to split test variation: ${newUrl}`);

                // Add a small delay to ensure logs are visible
                setTimeout(function() {
                    try {
                        window.location.href = newUrl;
                        debugLog('Redirect initiated');
                    } catch (e) {
                        debugLog(`Error during redirect: ${e.message}`);
                        debugAlert(`Error during redirect: ${e.message}`);
                    }
                }, 1000);
            } else {
                debugLog(`Split parameter already set to ${split}, not redirecting`);
            }
        } else {
            debugLog('This is already a split variation, not redirecting');
        }
    } catch (e) {
        debugLog(`Error in split test script: ${e.message}`);
        debugAlert(`Error in split test script: ${e.message}`);
    }
})();
