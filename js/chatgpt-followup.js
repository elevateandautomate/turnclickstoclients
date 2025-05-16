/**
 * ChatGPT-powered Follow-up System
 *
 * This file contains functions to generate personalized follow-up messages
 * using ChatGPT for leads who have viewed offers but not converted.
 */

// Configuration - Use the same API key as the offer generation
let followupApiKey = ''; // Will be populated from openai-integration.js
let followupDemoMode = true;

/**
 * Initialize the ChatGPT follow-up system
 */
function initChatGPTFollowup() {
    // Try to get the API key and demo mode from openai-integration.js
    if (window.openaiIntegration && window.openaiIntegration.getConfig) {
        const config = window.openaiIntegration.getConfig();
        if (config) {
            followupApiKey = config.apiKey || '';
            followupDemoMode = config.demoMode || true;
            console.log('ChatGPT follow-up using configuration from openai-integration.js');
        }
    }
}

/**
 * Generate a personalized follow-up sequence for a lead
 *
 * @param {Object} applicationData - The application data for the lead
 * @param {Object} offerData - The offer data that was presented to the lead
 * @param {Object} interactionData - Data about how the lead interacted with the offer
 * @returns {Promise<Array>} - Array of follow-up messages
 */
async function generateFollowupSequence(applicationData, offerData, interactionData) {
    try {
        console.log('Generating follow-up sequence for lead:', applicationData.id);

        // If in demo mode, return pre-generated follow-ups
        if (followupDemoMode || !followupApiKey) {
            console.log('Using pre-generated demo follow-ups (no API call)');
            return getDemoFollowups(applicationData, offerData);
        }

        // Prepare the system message with context
        const systemMessage = `You are an expert follow-up specialist for TurnClicksToClients.com.

        You're creating a sequence of 3 follow-up messages for a business owner who viewed our offer but hasn't booked a call yet.

        Business details:
        - Name: ${applicationData.businessName}
        - Type: ${applicationData.businessType}
        - Current clients: ${applicationData.currentClients}/month
        - Desired clients: ${applicationData.desiredClients}/month
        - Marketing challenges: ${applicationData.marketingChallenges}
        - Goals: ${applicationData.goals}

        Offer they viewed:
        - Headline: ${offerData.headline}
        - Main benefit: Getting more high-value clients without wasting time on marketing
        - Price: $2,500/month (Accelerate Plan)

        Interaction data:
        - Time spent on page: ${interactionData.timeOnPage || '3 minutes'}
        - Sections viewed: ${interactionData.sectionsViewed || 'headline, problem, solution, pricing'}
        - Clicked CTA: ${interactionData.clickedCTA ? 'Yes' : 'No'}

        Create 3 follow-up messages:
        1. A same-day follow-up (send 2 hours after viewing)
        2. A next-day follow-up (send 24 hours after viewing)
        3. A 3-day follow-up (send 3 days after viewing)

        Each message should:
        - Be personalized to their business type and challenges
        - Address a different objection or concern they might have
        - Include a clear call-to-action to book a call
        - Be written in a conversational, non-pushy tone
        - Be formatted for email (with subject line and body)

        Return the messages as a JSON array with each message having 'subject' and 'body' properties.`;

        // Make the API request
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${followupApiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    { role: 'system', content: systemMessage },
                    { role: 'user', content: 'Please generate a personalized 3-part follow-up sequence for this lead.' }
                ],
                temperature: 0.7,
                max_tokens: 1000
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const content = data.choices[0].message.content.trim();

        // Parse the JSON response
        try {
            // Try to parse the response as JSON
            const followups = JSON.parse(content);
            return followups;
        } catch (parseError) {
            console.error('Error parsing follow-up sequence JSON:', parseError);

            // Try to extract JSON from the text response
            const jsonMatch = content.match(/\[[\s\S]*\]/);
            if (jsonMatch) {
                try {
                    const followups = JSON.parse(jsonMatch[0]);
                    return followups;
                } catch (extractError) {
                    console.error('Error extracting JSON from response:', extractError);
                }
            }

            // Fall back to demo follow-ups
            return getDemoFollowups(applicationData, offerData);
        }
    } catch (error) {
        console.error('Error generating follow-up sequence:', error);
        return getDemoFollowups(applicationData, offerData);
    }
}

/**
 * Generate a personalized response to an inquiry
 *
 * @param {Object} applicationData - The application data for the lead
 * @param {Object} offerData - The offer data that was presented to the lead
 * @param {string} inquiry - The inquiry text from the lead
 * @returns {Promise<string>} - The personalized response
 */
async function generateInquiryResponse(applicationData, offerData, inquiry) {
    try {
        console.log('Generating response to inquiry from lead:', applicationData.id);

        // If in demo mode, return a pre-generated response
        if (followupDemoMode || !followupApiKey) {
            console.log('Using pre-generated demo response (no API call)');
            return getDemoInquiryResponse(applicationData, inquiry);
        }

        // Prepare the system message with context
        const systemMessage = `You are a helpful sales representative for TurnClicksToClients.com.

        You're responding to an inquiry from a business owner who viewed our offer.

        Business details:
        - Name: ${applicationData.businessName}
        - Type: ${applicationData.businessType}
        - Current clients: ${applicationData.currentClients}/month
        - Desired clients: ${applicationData.desiredClients}/month
        - Marketing challenges: ${applicationData.marketingChallenges}
        - Goals: ${applicationData.goals}

        Offer they viewed:
        - Headline: ${offerData.headline}
        - Main benefit: Getting more high-value clients without wasting time on marketing
        - Price: $2,500/month (Accelerate Plan)

        Your response should:
        - Be personalized to their business type and challenges
        - Directly answer their question or address their concern
        - Include relevant information about our service
        - End with a clear next step or call-to-action
        - Be written in a helpful, conversational tone
        - Be concise (150-200 words maximum)`;

        // Make the API request
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${followupApiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    { role: 'system', content: systemMessage },
                    { role: 'user', content: inquiry }
                ],
                temperature: 0.7,
                max_tokens: 300
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        return data.choices[0].message.content.trim();
    } catch (error) {
        console.error('Error generating inquiry response:', error);
        return getDemoInquiryResponse(applicationData, inquiry);
    }
}

/**
 * Get pre-generated demo follow-ups for testing
 *
 * @param {Object} applicationData - The application data for the lead
 * @param {Object} offerData - The offer data that was presented to the lead
 * @returns {Array} - Array of follow-up messages
 */
function getDemoFollowups(applicationData, offerData) {
    const businessName = applicationData.businessName || 'your business';
    const businessType = applicationData.businessType || 'your business';

    return [
        {
            subject: `Quick question about ${businessName}`,
            body: `Hi there,

I noticed you were checking out our client acquisition system for ${businessType.toLowerCase()} businesses earlier today.

I'm curious - what's the biggest challenge you're currently facing with getting new clients?

If you have 15 minutes, I'd love to show you exactly how we're helping other ${businessType.toLowerCase()} businesses book 15-30 new high-value clients every month without the marketing headaches.

You can book a quick call here: [BOOKING_LINK]

No pressure at all - just want to make sure you have all the information you need.

Best,
Alex
TurnClicksToClients.com`
        },
        {
            subject: `${businessName}: A quick idea for you`,
            body: `Hi again,

I was thinking about ${businessName} and had a quick idea I wanted to share.

One of our clients in the ${businessType.toLowerCase()} space was struggling with similar challenges to what you mentioned in your application. They were [SPECIFIC_CHALLENGE] and wanted to [SPECIFIC_GOAL].

Within 30 days of implementing our Client Attraction Engine, they saw a 43% increase in booked appointments and were able to be much more selective about which clients they took on.

I'd be happy to walk you through exactly how we did this and how we could apply the same approach to ${businessName}.

Here's my calendar link if you'd like to chat: [BOOKING_LINK]

Regards,
Alex
TurnClicksToClients.com`
        },
        {
            subject: `Last chance: Exclusive spot for ${businessName}`,
            body: `Hello,

Just wanted to let you know that we're currently finalizing our client roster for this quarter, and we only have space for one more ${businessType.toLowerCase()} business in your area.

Given your application and the goals you shared for ${businessName}, I believe we could help you [SPECIFIC_GOAL] within the next 60-90 days.

Remember, our service comes with a performance guarantee - if you don't see real, qualified appointments booked on your calendar within the first 30 days, you pay absolutely nothing.

If you're still interested, you can secure your spot here: [BOOKING_LINK]

If not, no problem at all! I appreciate your time and wish you all the best.

Best regards,
Alex
TurnClicksToClients.com`
        }
    ];
}

/**
 * Get a pre-generated demo inquiry response for testing
 *
 * @param {Object} applicationData - The application data for the lead
 * @param {string} inquiry - The inquiry text from the lead
 * @returns {string} - The personalized response
 */
function getDemoInquiryResponse(applicationData, inquiry) {
    const businessName = applicationData.businessName || 'your business';
    const businessType = applicationData.businessType || 'your business';

    // Check for common questions and return appropriate responses
    const lowerInquiry = inquiry.toLowerCase();

    if (lowerInquiry.includes('price') || lowerInquiry.includes('cost') || lowerInquiry.includes('how much')) {
        return `Hi there,

Thanks for asking about our pricing for ${businessName}. Our Accelerate Plan is $2,500/month and includes everything you need to fill your calendar with high-value clients:

1. Our proprietary Client Attraction Engine that creates high-converting ads specifically for ${businessType.toLowerCase()} businesses
2. Our professional Conversion Crew who responds to every lead within 5 minutes (24/7)
3. Our proven follow-up system that nurtures leads until they're ready to book
4. Direct integration with your calendar so appointments are booked automatically

Plus, you'll get weekly performance reports and monthly strategy calls to continuously optimize your results.

And remember, we offer a performance guarantee - if you don't see real, qualified appointments booked on your calendar within the first 30 days, you pay absolutely nothing.

Would you like to schedule a quick call to discuss how this would work specifically for ${businessName}?

Best,
Alex`;
    } else if (lowerInquiry.includes('guarantee') || lowerInquiry.includes('refund')) {
        return `Hi there,

Yes, we absolutely offer a performance guarantee for ${businessName}. Here's how it works:

If you don't see real, qualified appointments booked on your calendar and measurable growth within the first 30 days, you pay absolutely nothing for our service fee.

We can offer this guarantee because our system has been proven to work across dozens of ${businessType.toLowerCase()} businesses, and we're confident we can deliver results for you too.

Would you like to schedule a quick call to discuss the specific results we expect to achieve for ${businessName}?

Best,
Alex`;
    } else {
        return `Hi there,

Thanks for reaching out about ${businessName}. I appreciate your question.

Based on what you've shared about your goals and challenges, I believe our Client Attraction Engine would be a great fit for your ${businessType.toLowerCase()} business.

We specialize in helping businesses like yours get more high-value clients without the marketing headaches. Our clients typically see a 40-50% increase in booked appointments within 60 days.

I'd love to discuss this in more detail and answer any other questions you might have. Would you be available for a quick 15-minute call this week?

You can book a time that works for you here: [BOOKING_LINK]

Looking forward to chatting!

Best,
Alex`;
    }
}

// Initialize when the script loads
initChatGPTFollowup();

// Export the functions for use in other files
window.chatgptFollowup = {
    generateFollowupSequence,
    generateInquiryResponse
};
