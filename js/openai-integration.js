/**
 * OpenAI Integration for Automatic Offer Creation
 *
 * This file contains functions to generate coaching offers using OpenAI's API.
 */

// OpenAI API configuration
// This key should be kept private in a production environment
// Consider using environment variables or a secure backend
const OPENAI_API_KEY = ''; // Empty for demo purposes
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
const OPENAI_MODEL = 'gpt-3.5-turbo'; // You can also use 'gpt-4' if you have access

// Flag to determine if we're in demo mode
const DEMO_MODE = true;

/**
 * Sleep for a specified number of milliseconds
 *
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Generate an offer using OpenAI
 *
 * @param {string} niche - The business niche (e.g., "cosmetic-dentists", "pmu-artists")
 * @param {string} targetAudience - The target audience (e.g., "quiz_completed", "high_score")
 * @param {Object} quizData - Sample quiz data to inform the AI (optional)
 * @param {Object} applicationData - Application answers to inform the AI (optional)
 * @param {number} retryCount - Number of retries attempted (default: 0)
 * @param {number} maxRetries - Maximum number of retries (default: 3)
 * @returns {Promise<Object>} - The generated offer data
 */
async function generateOffer(niche, targetAudience, quizData = null, applicationData = null, retryCount = 0, maxRetries = 3) {
    try {
        console.log(`Generating offer for ${niche}, targeting ${targetAudience}...`);

        // If in demo mode, return a pre-generated offer
        if (DEMO_MODE || !OPENAI_API_KEY) {
            console.log('Using pre-generated demo offer (no API call)');
            return getDemoOffer(niche, targetAudience, applicationData);
        }

        // Add delay between requests to avoid rate limiting
        if (retryCount > 0) {
            const delayMs = retryCount * 2000; // Increase delay with each retry
            console.log(`Retry attempt ${retryCount}. Waiting ${delayMs/1000} seconds before retrying...`);
            await sleep(delayMs);
        }

        // Format the niche for better readability
        const formattedNiche = niche.split('-').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');

        // Format the target audience for better readability
        let formattedAudience = targetAudience;
        if (targetAudience === 'quiz_completed') formattedAudience = 'people who completed your quiz';
        if (targetAudience === 'high_score') formattedAudience = 'people who scored high on your quiz';
        if (targetAudience === 'returning') formattedAudience = 'returning visitors';
        if (targetAudience === 'application_completed') formattedAudience = 'people who completed your application';

        // Create a detailed prompt for the AI in the style of Eugene Schwartz and Russell Brunson
        let prompt = `
            Create a compelling offer for TurnClicksToClients.com to present to a ${formattedNiche} business owner, written in the persuasive style of Eugene Schwartz and Russell Brunson.

            IMPORTANT: This offer is FROM TurnClicksToClients.com TO the ${formattedNiche} business owner. It is NOT an offer from the ${formattedNiche} business to their end customers.

            TurnClicksToClients.com specializes in helping care-driven service businesses fill their calendars with high-value clients.
            We handle the entire client acquisition process including lead generation, follow-up, and appointment booking.

            Our pricing structure includes:
            - Growth Plan: $1,500/month ($50/day) - Core lead generation system with up to $50/day ad spend
            - Accelerate Plan: $2,500/month ($83/day) - Advanced lead generation with up to $100/day ad spend
            - Fast Track Plan: $3,500/month ($117/day) - All-inclusive system with $100+/day ad spend

            The offer should speak DIRECTLY TO THE BUSINESS OWNER about how TurnClicksToClients.com can help them get more clients. Do NOT create an offer for the business owner to show to their customers.

            Create a COMPLETE offer page in the exact style of Russell Brunson and Eugene Schwartz. Include ALL these elements:

            Format the response as JSON with the following fields:
            - name: A name for this offer (for internal reference)
            - headline: A powerful, emotionally-charged headline that speaks directly to the prospect's deepest desires or fears (max 15 words)
            - subheadline: A compelling subheadline that elaborates on the headline (15-20 words)
            - opening_hook: An attention-grabbing opening hook that creates curiosity (30-50 words)
            - problem_agitation: A vivid description of the pain points and challenges the business owner faces (100-150 words)
            - solution_introduction: Introduction of your solution as the answer to their problems (50-80 words)
            - bullet_points: An array of 5-7 powerful bullet points highlighting key benefits (each 10-15 words)
            - social_proof: A brief section on results achieved for similar businesses (50-80 words)
            - offer_details: A detailed breakdown of what's included in your service (100-150 words)
            - price_justification: Text explaining the value and ROI of your service (50-80 words)
            - guarantee: A risk-reversal guarantee statement (30-50 words)
            - scarcity: Text creating urgency and scarcity (30-50 words)
            - cta_text: An irresistible call to action text for the booking button (5-7 words)
            - cta_subtext: Small text below the CTA button to reduce friction (15-25 words)

            The offer should:
            - Use Eugene Schwartz's 5 levels of awareness (Unaware, Problem-Aware, Solution-Aware, Product-Aware, Most Aware)
            - Incorporate Russell Brunson's "Perfect Webinar" elements (The Big Promise, The Big Domino, False Beliefs, Opportunity Switch, Stack)
            - Create a sense of scarcity and urgency (e.g., "limited spots available this week")
            - Use powerful emotional triggers and future-pacing
            - Focus on transformation, not just features
            - Include a risk-reversal element (e.g., "no obligation consultation")
            - Be specific to the ${formattedNiche} industry and address the needs of ${formattedAudience}

            Remember to use these copywriting techniques:
            - Identify a big, emotionally-charged problem
            - Agitate that problem with vivid description
            - Present a unique solution with a clear mechanism
            - Use future pacing to help them imagine the transformation
            - Create urgency and scarcity to drive immediate action
            - Reverse risk to make saying "yes" the only logical choice
        `;

        // Add niche-specific guidance based on the business type
        if (niche === 'cosmetic-dentists') {
            prompt += `\n\nFor Cosmetic Dentist Business Owners:
            - BIG PROMISE: "Fill Your Chair With High-Value Smile Makeover Patients Without Wasting Time On Marketing"
            - BIG DOMINO: "If I can make you believe that consistent patient acquisition doesn't require endless hours managing ads and following up with leads..."
            - FALSE BELIEF to overcome: "I need to handle all my marketing myself to get quality patients"
            - OPPORTUNITY SWITCH: From "Marketing is a necessary evil that takes time away from patients" to "Marketing can be completely handled for you while you focus on patients"
            - STACK: Client Attraction Engine + Conversion Crew + 24/7 lead response + booking directly into your calendar
            - FUTURE PACING: Have them imagine their schedule filled with ideal patients while they focus solely on providing care
            - SCARCITY: Only ONE cosmetic dentist per city, just 3 spots available`;
        } else if (niche === 'pmu-artists') {
            prompt += `\n\nFor PMU Artist Business Owners:
            - BIG PROMISE: "Book Your Calendar Solid With Premium PMU Clients Without The Instagram Hustle"
            - BIG DOMINO: "If I can make you believe that you can attract high-paying clients without spending hours on social media..."
            - FALSE BELIEF to overcome: "I need to constantly create content and manage DMs to get bookings"
            - OPPORTUNITY SWITCH: From "Social media marketing is the only way to get PMU clients" to "Automated systems can bring you clients while you focus on your art"
            - STACK: Client Attraction Engine + Conversion Crew + 24/7 lead response + booking directly into your calendar
            - FUTURE PACING: Have them imagine their schedule filled with ideal clients while they focus solely on their artistry
            - SCARCITY: Only ONE PMU artist per city, just 3 spots available`;
        }

        // Add application data context if available
        if (applicationData) {
            prompt += `\n\nHere is application data to help inform the offer:`;

            // Add business information
            if (applicationData.businessName) {
                prompt += `\nBusiness Name: ${applicationData.businessName}`;
            }

            if (applicationData.businessType) {
                prompt += `\nBusiness Type: ${applicationData.businessType}`;
            }

            if (applicationData.currentClients) {
                prompt += `\nCurrent Monthly Clients: ${applicationData.currentClients}`;
            }

            if (applicationData.desiredClients) {
                prompt += `\nDesired Monthly Clients: ${applicationData.desiredClients}`;
            }

            if (applicationData.clientValue) {
                prompt += `\nAverage Client Value: $${applicationData.clientValue}`;
            }

            if (applicationData.marketingChallenges) {
                prompt += `\nMarketing Challenges: ${applicationData.marketingChallenges}`;
            }

            if (applicationData.goals) {
                prompt += `\nBusiness Goals: ${applicationData.goals}`;
            }

            // Add personalization note
            prompt += `\n\nMake sure the offer speaks directly to this business's specific situation, challenges, and goals.`;
        }

        // Add quiz data context if available
        if (quizData && quizData.length > 0) {
            prompt += `\n\nHere is some sample quiz data to help inform the offer:`;

            // Add a summary of quiz data
            const commonScores = quizData.reduce((acc, submission) => {
                const score = submission.total_score || 0;
                acc[score] = (acc[score] || 0) + 1;
                return acc;
            }, {});

            prompt += `\nTypical quiz scores: ${JSON.stringify(commonScores)}`;

            // Add common outcomes if available
            const outcomes = quizData
                .filter(s => s.primary_outcome_hint)
                .map(s => s.primary_outcome_hint);

            if (outcomes.length > 0) {
                prompt += `\nCommon quiz outcomes: ${outcomes.join(', ')}`;
            }
        }

        // Make the API request to OpenAI
        const response = await fetch(OPENAI_API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${OPENAI_API_KEY}`
            },
            body: JSON.stringify({
                model: OPENAI_MODEL,
                messages: [
                    {
                        role: "system",
                        content: "You are an expert copywriter specializing in creating high-converting offers in the style of Eugene Schwartz and Russell Brunson. You always respond with valid JSON."
                    },
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                temperature: 0.7,
                max_tokens: 1000
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('OpenAI API error response:', errorText);
            throw new Error(`OpenAI API error: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();
        console.log('OpenAI API response:', data);

        if (!data.choices || data.choices.length === 0) {
            throw new Error('No response from OpenAI API');
        }

        const generatedText = data.choices[0].message.content;

        // Extract the JSON from the response
        // The AI might include markdown formatting, so we need to extract just the JSON part
        const jsonMatch = generatedText.match(/```json\n([\s\S]*?)\n```/) ||
                         generatedText.match(/```\n([\s\S]*?)\n```/) ||
                         generatedText.match(/{[\s\S]*?}/);

        let offerData;
        if (jsonMatch) {
            offerData = JSON.parse(jsonMatch[0].replace(/```json\n|```\n|```/g, ''));
        } else {
            // If no JSON formatting, try to parse the whole response
            offerData = JSON.parse(generatedText);
        }

        // Add metadata
        offerData.niche = niche;
        offerData.target_audience = targetAudience;
        offerData.is_auto_generated = true;
        offerData.generated_by_ai = true;
        offerData.ai_provider = 'openai';
        offerData.created_at = new Date().toISOString();
        offerData.updated_at = new Date().toISOString();

        console.log('Successfully generated offer:', offerData.name);
        return offerData;
    } catch (error) {
        console.error('Error generating offer:', error);

        // Check if this is a rate limit error and we haven't exceeded max retries
        if (error.message && error.message.includes('429') && retryCount < maxRetries) {
            console.log(`Rate limit exceeded. Will retry (${retryCount + 1}/${maxRetries})...`);

            // Retry with incremented retry count
            return generateOffer(niche, targetAudience, quizData, applicationData, retryCount + 1, maxRetries);
        }

        return null;
    }
}

/**
 * Generate a personalized offer for the post-application offer page
 *
 * @param {Object} applicationData - The user's application data
 * @param {Object} quizData - The user's quiz data
 * @returns {Promise<Object>} - The generated offer data
 */
async function generatePostApplicationOffer(applicationData, quizData) {
    try {
        console.log('Generating personalized post-application offer with OpenAI...');

        // Extract niche from application data or quiz data
        let niche = applicationData.businessType ||
                   (quizData && quizData.niche) ||
                   'general';

        // Map business type to our niche format if needed
        const nicheMap = {
            'Cosmetic Dentist': 'cosmetic-dentists',
            'PMU Artist': 'pmu-artists',
            'Weight Loss Clinic': 'weight-loss-clinics',
            'Chiropractor': 'high-end-chiropractors',
            'Child Care Center': 'child-care-centers',
            'Body Contouring': 'non-surgical-body-contouring',
            'Sleep Clinic': 'sleep-apnea-snoring-clinics',
            'Audiology Clinic': 'hearing-aid-audiology-clinics',
            'DME Clinic': 'dme-clinics'
        };

        if (nicheMap[niche]) {
            niche = nicheMap[niche];
        }

        // Generate a personalized offer
        const offer = await generateOffer(
            niche,
            'application_completed',
            quizData ? [quizData] : null,
            applicationData
        );

        if (offer) {
            // Add application-specific fields
            offer.is_personalized = true;
            offer.application_id = applicationData.id || null;
            offer.quiz_id = quizData ? quizData.id : null;

            return offer;
        } else {
            throw new Error('Failed to generate post-application offer');
        }
    } catch (error) {
        console.error('Error generating post-application offer:', error);
        return null;
    }
}

/**
 * Get a pre-generated demo offer for testing purposes
 *
 * @param {string} niche - The business niche
 * @param {string} targetAudience - The target audience
 * @param {Object} applicationData - Application data to personalize the offer
 * @returns {Object} - A pre-generated offer
 */
function getDemoOffer(niche, targetAudience, applicationData) {
    const businessName = applicationData?.businessName || 'Your Business';
    const desiredClients = applicationData?.desiredClients || '30';
    const clientValue = applicationData?.clientValue || '5000';

    // Create a demo offer based on the niche
    let offer = {
        name: `Demo Offer for ${niche}`,
        headline: "Fill Your Calendar With Premium Clients Without The Marketing Headaches",
        subheadline: `Discover how we're helping ${niche.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')} book 15-30 new high-value clients every month on autopilot`,
        opening_hook: `${businessName}, what if you could attract ${desiredClients} qualified, high-value clients every month while focusing solely on what you do best?`,
        problem_agitation: `Most businesses in your industry are stuck in an endless cycle of marketing frustration. You're spending thousands on ads that don't convert, wasting hours creating content nobody sees, and missing leads because you can't respond fast enough. Meanwhile, your competitors are stealing the clients you deserve, and your calendar has more gaps than you'd like to admit. The worst part? Every hour spent on marketing is an hour away from serving clients and growing your practice.`,
        solution_introduction: `That's why we created the Client Attraction Engine—a complete done-for-you system that handles every aspect of your client acquisition. No more wasted ad spend, no more missed leads, no more marketing headaches. Just a steady stream of qualified, high-value clients booking directly into your calendar.`,
        bullet_points: [
            "Expertly crafted ads that target your ideal clients with laser precision",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to book",
            "Direct calendar integration so appointments are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One client per city exclusivity—we'll never work with your local competitors"
        ],
        social_proof: `We've already helped dozens of businesses just like yours transform their client acquisition. On average, our clients see a 43% increase in booked appointments within the first 60 days, with some seeing results in as little as 2 weeks. Many have been able to completely eliminate their marketing team or agency, saving thousands while getting better results.`,
        offer_details: `Our Accelerate Plan ($83/day) includes everything you need to fill your calendar with high-value clients: Our proprietary Client Attraction Engine that creates high-converting ads specifically for your industry, our professional Conversion Crew who responds to every lead within 5 minutes (24/7), our proven follow-up system that nurtures leads until they're ready to book, and direct integration with your calendar so appointments are booked automatically.`,
        price_justification: `Consider this: If just ONE new client is worth $${clientValue} to your business, and our system brings you 15-30 new clients every month, that's a potential return of $${Number(clientValue) * 15}-$${Number(clientValue) * 30} monthly from an investment of just $2,500. That's a ${Math.round((Number(clientValue) * 15) / 2500)}-${Math.round((Number(clientValue) * 30) / 2500)}x return on your investment.`,
        guarantee: `If you don't see real, qualified appointments booked on your calendar and measurable growth within the first 30 days, you pay absolutely nothing for our service fee. That's performance, guaranteed.`,
        scarcity: `IMPORTANT: We can only partner with ONE business in your industry per city. Right now, we have just 3 spots available for our Accelerate Plan. Claim your city before your competitor does!`,
        cta_text: 'Claim Your City Now',
        cta_subtext: 'No obligation, 30-day performance guarantee',
        niche: niche,
        target_audience: targetAudience,
        is_auto_generated: true,
        generated_by_ai: true,
        ai_provider: 'openai-demo',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
    };

    // Customize for specific niches
    if (niche === 'cosmetic-dentists' || applicationData?.businessType === 'Cosmetic Dentist') {
        offer.headline = "Fill Your Chair With High-Value Smile Makeover Patients Without Wasting Time On Marketing";
        offer.subheadline = "Discover how we're helping cosmetic dentists book 15-30 new smile makeover patients every month without the marketing headaches";
        offer.opening_hook = `${businessName}, what if you could attract ${desiredClients} qualified, high-value smile makeover patients every month on autopilot while focusing solely on transforming smiles?`;
        offer.problem_agitation = "Most cosmetic dental practices are stuck in an endless cycle of marketing frustration. You're spending thousands on ads that don't convert, wasting hours managing social media that nobody sees, and missing leads because you can't respond fast enough. Meanwhile, your competitors are stealing the patients you deserve, and your chair has more empty time than you'd like to admit.";
        offer.bullet_points = [
            "Expertly crafted dental ads that target patients seeking cosmetic procedures",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to book",
            "Direct calendar integration so consultations are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One cosmetic dentist per city exclusivity—we'll never work with your local competitors"
        ];
    } else if (niche === 'pmu-artists' || applicationData?.businessType === 'PMU Artist') {
        offer.headline = "Book Your Calendar Solid With Premium PMU Clients Without The Instagram Hustle";
        offer.subheadline = "Discover how we're helping PMU artists book 15-30 new high-paying clients every month without spending hours on social media";
        offer.opening_hook = `${businessName}, what if you could attract ${desiredClients} qualified, high-paying PMU clients every month without the exhausting social media hustle?`;
        offer.problem_agitation = "Most PMU artists are trapped in an endless cycle of content creation and DM management. You're spending hours creating the perfect posts, responding to inquiries at all hours, and still missing potential clients because you can't keep up. Meanwhile, your competitors with bigger followings are stealing the clients you deserve.";
        offer.bullet_points = [
            "Expertly crafted ads that target clients seeking premium PMU services",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to book",
            "Direct calendar integration so appointments are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One PMU artist per city exclusivity—we'll never work with your local competitors"
        ];
    }

    return offer;
}

/**
 * Get the configuration for other modules to use
 *
 * @returns {Object} Configuration object with API key and demo mode
 */
function getConfig() {
    return {
        apiKey: OPENAI_API_KEY,
        demoMode: DEMO_MODE
    };
}

// Export the functions for use in other files
window.openaiIntegration = {
    generateOffer,
    generatePostApplicationOffer,
    getConfig
};
