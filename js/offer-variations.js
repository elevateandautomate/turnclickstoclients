/**
 * Offer Variations Generator
 *
 * This file contains functions to generate multiple variations of offers
 * using ChatGPT for split testing purposes.
 */

// Configuration - Use the same API key as the offer generation
let offerVariationsApiKey = ''; // Will be populated from openai-integration.js
let offerVariationsDemoMode = true;

// Variation types
const VARIATION_TYPES = {
    HEADLINE: 'headline',
    HOOK: 'hook',
    PROBLEM: 'problem',
    SOLUTION: 'solution',
    BULLETS: 'bullets',
    SCARCITY: 'scarcity',
    CTA: 'cta'
};

/**
 * Initialize the offer variations module
 */
function initOfferVariations() {
    // Try to get the API key and demo mode from openai-integration.js
    if (window.openaiIntegration && window.openaiIntegration.getConfig) {
        const config = window.openaiIntegration.getConfig();
        if (config) {
            offerVariationsApiKey = config.apiKey || '';
            offerVariationsDemoMode = config.demoMode || true;
            console.log('Offer variations using configuration from openai-integration.js');
        }
    }
}

/**
 * Generate variations of an offer for split testing
 *
 * @param {Object} baseOffer - The base offer to create variations from
 * @param {Array} variationTypes - Array of elements to vary (headline, hook, etc.)
 * @param {number} numVariations - Number of variations to generate
 * @returns {Promise<Array>} - Array of offer variations
 */
async function generateOfferVariations(baseOffer, variationTypes = [VARIATION_TYPES.HEADLINE], numVariations = 2) {
    try {
        console.log(`Generating ${numVariations} offer variations with changes to: ${variationTypes.join(', ')}`);

        // If in demo mode, return pre-generated variations
        if (offerVariationsDemoMode || !offerVariationsApiKey) {
            console.log('Using pre-generated demo variations (no API call)');
            return getDemoVariations(baseOffer, variationTypes, numVariations);
        }

        // Prepare the variations array
        const variations = [];

        // For each variation
        for (let i = 0; i < numVariations; i++) {
            // Create a copy of the base offer
            const variation = { ...baseOffer, is_variation: true, variation_id: i + 1 };

            // For each variation type
            for (const type of variationTypes) {
                // Generate a variation for this element
                const newValue = await generateVariation(baseOffer, type);

                // Update the variation with the new value
                switch (type) {
                    case VARIATION_TYPES.HEADLINE:
                        variation.headline = newValue;
                        break;
                    case VARIATION_TYPES.HOOK:
                        variation.opening_hook = newValue;
                        break;
                    case VARIATION_TYPES.PROBLEM:
                        variation.problem_agitation = newValue;
                        break;
                    case VARIATION_TYPES.SOLUTION:
                        variation.solution_introduction = newValue;
                        break;
                    case VARIATION_TYPES.BULLETS:
                        variation.bullet_points = newValue;
                        break;
                    case VARIATION_TYPES.SCARCITY:
                        variation.scarcity = newValue;
                        break;
                    case VARIATION_TYPES.CTA:
                        variation.cta_text = newValue;
                        break;
                }
            }

            // Add the variation to the array
            variations.push(variation);
        }

        return variations;
    } catch (error) {
        console.error('Error generating offer variations:', error);
        return [];
    }
}

/**
 * Generate a variation for a specific element of an offer
 *
 * @param {Object} baseOffer - The base offer
 * @param {string} type - The type of element to vary
 * @returns {Promise<string|Array>} - The new value for the element
 */
async function generateVariation(baseOffer, type) {
    try {
        // Get the current value
        let currentValue;
        switch (type) {
            case VARIATION_TYPES.HEADLINE:
                currentValue = baseOffer.headline;
                break;
            case VARIATION_TYPES.HOOK:
                currentValue = baseOffer.opening_hook;
                break;
            case VARIATION_TYPES.PROBLEM:
                currentValue = baseOffer.problem_agitation;
                break;
            case VARIATION_TYPES.SOLUTION:
                currentValue = baseOffer.solution_introduction;
                break;
            case VARIATION_TYPES.BULLETS:
                currentValue = baseOffer.bullet_points;
                break;
            case VARIATION_TYPES.SCARCITY:
                currentValue = baseOffer.scarcity;
                break;
            case VARIATION_TYPES.CTA:
                currentValue = baseOffer.cta_text;
                break;
        }

        // Prepare the prompt
        let prompt = `You are an expert copywriter specializing in creating high-converting offers in the style of Eugene Schwartz and Russell Brunson.

        I have an offer with the following ${type}:

        ${JSON.stringify(currentValue)}

        Please create a new variation of this ${type} that:
        1. Maintains the same core message and intent
        2. Uses different wording and structure
        3. Potentially tests a different angle or emotional trigger
        4. Follows the Eugene Schwartz and Russell Brunson copywriting principles
        5. Is optimized for conversion

        The offer is for a service that helps ${baseOffer.niche.replace(/-/g, ' ')} get more clients through digital marketing.`;

        // Add specific instructions based on the type
        switch (type) {
            case VARIATION_TYPES.HEADLINE:
                prompt += `\n\nFor the headline, create something powerful and emotionally charged that speaks directly to the prospect's deepest desires or fears. Keep it under 15 words.`;
                break;
            case VARIATION_TYPES.HOOK:
                prompt += `\n\nFor the opening hook, create something that immediately grabs attention and creates curiosity. It should be 30-50 words.`;
                break;
            case VARIATION_TYPES.PROBLEM:
                prompt += `\n\nFor the problem agitation, vividly describe the pain points and challenges the business owner faces. It should be 100-150 words.`;
                break;
            case VARIATION_TYPES.SOLUTION:
                prompt += `\n\nFor the solution introduction, present the solution as the answer to their problems. It should be 50-80 words.`;
                break;
            case VARIATION_TYPES.BULLETS:
                prompt += `\n\nFor the bullet points, create 5-7 powerful points highlighting key benefits. Each should be 10-15 words.`;
                break;
            case VARIATION_TYPES.SCARCITY:
                prompt += `\n\nFor the scarcity element, create text that creates urgency and scarcity. It should be 30-50 words.`;
                break;
            case VARIATION_TYPES.CTA:
                prompt += `\n\nFor the call to action, create an irresistible button text. It should be 3-7 words.`;
                break;
        }

        // Make the API request
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${offerVariationsApiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    { role: 'system', content: 'You are an expert copywriter specializing in creating high-converting offers in the style of Eugene Schwartz and Russell Brunson.' },
                    { role: 'user', content: prompt }
                ],
                temperature: 0.8,
                max_tokens: 500
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        let newValue = data.choices[0].message.content.trim();

        // Process the response based on the type
        if (type === VARIATION_TYPES.BULLETS) {
            // Extract bullet points as an array
            const bulletRegex = /[-*•]\s*(.+?)(?=\n[-*•]|\n\n|$)/gs;
            const matches = [...newValue.matchAll(bulletRegex)];
            newValue = matches.map(match => match[1].trim());

            // If no matches, split by newlines
            if (newValue.length === 0) {
                newValue = newValue.split('\n').map(line => line.trim()).filter(line => line);
            }

            // If still no matches, use the whole text as one bullet
            if (newValue.length === 0) {
                newValue = [newValue];
            }
        }

        return newValue;
    } catch (error) {
        console.error(`Error generating ${type} variation:`, error);
        return null;
    }
}

/**
 * Get pre-generated demo variations for testing
 *
 * @param {Object} baseOffer - The base offer
 * @param {Array} variationTypes - Array of elements to vary
 * @param {number} numVariations - Number of variations to generate
 * @returns {Array} - Array of offer variations
 */
function getDemoVariations(baseOffer, variationTypes, numVariations) {
    const variations = [];

    // Demo variations for headlines
    const headlineVariations = [
        "Stop Wasting Time on Marketing: Fill Your Calendar With Premium Clients Now",
        "Transform Your Practice: High-Value Clients Without Marketing Headaches",
        "Eliminate Marketing Stress: Book More Premium Clients Automatically",
        "Double Your Client Value Without Doubling Your Marketing Time"
    ];

    // Demo variations for hooks
    const hookVariations = [
        "What if your calendar was consistently booked with ideal clients while you focused exclusively on delivering exceptional service?",
        "Imagine never having to worry about where your next client is coming from, all while spending zero time on marketing.",
        "What would change in your business if you could delegate your entire client acquisition process to experts who guarantee results?"
    ];

    // Demo variations for CTAs
    const ctaVariations = [
        "Book My Strategy Call",
        "Reserve My City Now",
        "Get Started Today",
        "Claim My Spot"
    ];

    // Create variations
    for (let i = 0; i < numVariations; i++) {
        // Create a copy of the base offer
        const variation = { ...baseOffer, is_variation: true, variation_id: i + 1 };

        // For each variation type
        for (const type of variationTypes) {
            // Update the variation with a demo value
            switch (type) {
                case VARIATION_TYPES.HEADLINE:
                    variation.headline = headlineVariations[i % headlineVariations.length];
                    break;
                case VARIATION_TYPES.HOOK:
                    variation.opening_hook = hookVariations[i % hookVariations.length];
                    break;
                case VARIATION_TYPES.CTA:
                    variation.cta_text = ctaVariations[i % ctaVariations.length];
                    break;
                // For other types, just append "Variation #X" to the original
                default:
                    const originalValue = baseOffer[type];
                    if (typeof originalValue === 'string') {
                        variation[type] = `${originalValue} (Variation #${i + 1})`;
                    }
            }
        }

        // Add the variation to the array
        variations.push(variation);
    }

    return variations;
}

// Initialize when the script loads
initOfferVariations();

// Export the functions for use in other files
window.offerVariations = {
    generateOfferVariations,
    VARIATION_TYPES
};
