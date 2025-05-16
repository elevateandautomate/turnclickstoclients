/**
 * Offer A/B Testing System
 * 
 * This script handles A/B testing for the offer page.
 * It randomly assigns visitors to different variations and tracks conversions.
 */

// Configuration
const OFFER_VARIATIONS = {
    'original': {
        name: 'Original',
        headline: 'JOIN OUR PARTNERSHIP & ACTIVATE YOUR SYSTEM',
        subheadline: 'Right now, you stand at the crossroads that separates the leaders from the followers in your industry.',
        ctaText: 'JOIN OUR PARTNERSHIP FOR JUST $997',
        ctaColor: '#28a745', // Green
    },
    'variation-b': {
        name: 'Variation B',
        headline: 'SECURE YOUR EXCLUSIVE PARTNERSHIP TODAY',
        subheadline: 'Only one business per city can access our proven client attraction system. Will it be you or your competitor?',
        ctaText: 'ACTIVATE YOUR PARTNERSHIP NOW - $997',
        ctaColor: '#0056b3', // Blue
    },
    'variation-c': {
        name: 'Variation C',
        headline: 'CLAIM YOUR $997 PARTNERSHIP ACTIVATION',
        subheadline: 'Join the elite group of business owners who are dominating their local markets with our proven system.',
        ctaText: 'YES! I WANT EXCLUSIVE PARTNERSHIP RIGHTS',
        ctaColor: '#d9534f', // Red
    }
};

// Initialize on document load
document.addEventListener('DOMContentLoaded', function() {
    initializeOfferABTesting();
});

/**
 * Initialize the offer A/B testing system
 */
function initializeOfferABTesting() {
    // Check if we're on the offer page
    if (!document.querySelector('.final-cta')) {
        return;
    }
    
    // Check for admin mode (for testing variations)
    const urlParams = new URLSearchParams(window.location.search);
    const adminMode = urlParams.get('admin_mode') === 'true';
    
    // Get or assign variation
    let variation = urlParams.get('variation');
    
    if (!variation || !OFFER_VARIATIONS[variation]) {
        // If no valid variation specified in URL, get from localStorage or assign randomly
        variation = localStorage.getItem('offerVariation');
        
        // If no variation in localStorage or invalid, assign randomly
        if (!variation || !OFFER_VARIATIONS[variation]) {
            const variationKeys = Object.keys(OFFER_VARIATIONS);
            const randomIndex = Math.floor(Math.random() * variationKeys.length);
            variation = variationKeys[randomIndex];
            localStorage.setItem('offerVariation', variation);
        }
    } else {
        // If variation specified in URL, save to localStorage
        localStorage.setItem('offerVariation', variation);
    }
    
    // Apply the variation
    applyVariation(variation);
    
    // Track page view
    trackEvent('view', variation);
    
    // Add variation controls for admin mode
    if (adminMode) {
        addVariationControls(variation);
    }
    
    // Add click tracking to CTA buttons
    addConversionTracking();
}

/**
 * Apply the selected variation to the page
 * 
 * @param {string} variationKey - The key of the variation to apply
 */
function applyVariation(variationKey) {
    const variation = OFFER_VARIATIONS[variationKey];
    
    if (!variation) {
        console.error('Invalid variation:', variationKey);
        return;
    }
    
    // Update headline
    const headlineElement = document.querySelector('.final-cta h2');
    if (headlineElement) {
        headlineElement.textContent = variation.headline;
    }
    
    // Update subheadline
    const subheadlineElement = document.querySelector('.final-cta > div > p:first-of-type');
    if (subheadlineElement) {
        subheadlineElement.textContent = variation.subheadline;
    }
    
    // Update CTA button text
    const ctaButton = document.querySelector('.final-cta .cta-button');
    if (ctaButton) {
        ctaButton.textContent = variation.ctaText;
        ctaButton.style.backgroundColor = variation.ctaColor;
        
        // Update the URL to include the variation for tracking
        const currentHref = ctaButton.getAttribute('href');
        const url = new URL(currentHref, window.location.origin);
        url.searchParams.set('variation', variationKey);
        ctaButton.setAttribute('href', url.pathname + url.search);
    }
    
    // Add a badge for admin mode
    const urlParams = new URLSearchParams(window.location.search);
    const adminMode = urlParams.get('admin_mode') === 'true';
    
    if (adminMode) {
        const badge = document.createElement('div');
        badge.style.position = 'fixed';
        badge.style.top = '10px';
        badge.style.right = '10px';
        badge.style.backgroundColor = '#333';
        badge.style.color = '#fff';
        badge.style.padding = '5px 10px';
        badge.style.borderRadius = '3px';
        badge.style.zIndex = '9999';
        badge.textContent = `Viewing: ${variation.name}`;
        document.body.appendChild(badge);
    }
}

/**
 * Add variation controls for admin mode
 * 
 * @param {string} currentVariation - The current variation key
 */
function addVariationControls(currentVariation) {
    const controls = document.createElement('div');
    controls.style.position = 'fixed';
    controls.style.bottom = '10px';
    controls.style.right = '10px';
    controls.style.backgroundColor = '#333';
    controls.style.color = '#fff';
    controls.style.padding = '10px';
    controls.style.borderRadius = '5px';
    controls.style.zIndex = '9999';
    controls.innerHTML = '<strong>Test Variations:</strong><br>';
    
    Object.keys(OFFER_VARIATIONS).forEach(key => {
        const button = document.createElement('button');
        button.textContent = OFFER_VARIATIONS[key].name;
        button.style.margin = '5px';
        button.style.padding = '5px 10px';
        button.style.cursor = 'pointer';
        
        if (key === currentVariation) {
            button.style.backgroundColor = '#4a90e2';
            button.style.color = '#fff';
        }
        
        button.addEventListener('click', () => {
            const url = new URL(window.location.href);
            url.searchParams.set('variation', key);
            url.searchParams.set('admin_mode', 'true');
            window.location.href = url.toString();
        });
        
        controls.appendChild(button);
    });
    
    document.body.appendChild(controls);
}

/**
 * Add conversion tracking to CTA buttons
 */
function addConversionTracking() {
    const ctaButtons = document.querySelectorAll('.cta-button');
    
    ctaButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const variation = localStorage.getItem('offerVariation') || 'original';
            trackEvent('conversion', variation);
        });
    });
}

/**
 * Track an event (view or conversion)
 * 
 * @param {string} eventType - The type of event ('view' or 'conversion')
 * @param {string} variation - The variation key
 */
function trackEvent(eventType, variation) {
    // Get existing tracking data from localStorage
    let trackingData = JSON.parse(localStorage.getItem('offerTrackingData') || '{}');
    
    // Initialize variation data if it doesn't exist
    if (!trackingData[variation]) {
        trackingData[variation] = {
            views: 0,
            conversions: 0
        };
    }
    
    // Increment the appropriate counter
    if (eventType === 'view') {
        trackingData[variation].views++;
    } else if (eventType === 'conversion') {
        trackingData[variation].conversions++;
    }
    
    // Save updated tracking data
    localStorage.setItem('offerTrackingData', JSON.stringify(trackingData));
    
    // If Supabase is available, send the event there
    if (typeof supabase !== 'undefined') {
        try {
            const eventData = {
                event_type: eventType,
                variation: variation,
                page: window.location.pathname,
                timestamp: new Date().toISOString()
            };
            
            // Send to Supabase (assuming you have a tracking table)
            supabase.from('tracking_events').insert([eventData])
                .then(response => {
                    if (response.error) {
                        console.error('Error tracking event:', response.error);
                    }
                });
        } catch (error) {
            console.error('Error sending tracking data to Supabase:', error);
        }
    }
}

/**
 * Get tracking statistics for all variations
 * 
 * @returns {Object} Statistics for all variations
 */
function getTrackingStats() {
    const trackingData = JSON.parse(localStorage.getItem('offerTrackingData') || '{}');
    const stats = {};
    
    Object.keys(trackingData).forEach(variation => {
        const data = trackingData[variation];
        const conversionRate = data.views > 0 ? (data.conversions / data.views) * 100 : 0;
        
        stats[variation] = {
            views: data.views,
            conversions: data.conversions,
            conversionRate: conversionRate.toFixed(2) + '%'
        };
    });
    
    return stats;
}

// Export functions for external use
window.offerABTesting = {
    getTrackingStats,
    applyVariation,
    OFFER_VARIATIONS
};
