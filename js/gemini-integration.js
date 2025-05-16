/**
 * Gemini AI Integration for Automatic Offer Creation
 *
 * This file contains functions to generate coaching offers using Google's Gemini AI.
 */

// Store the API key from Google AI Studio
const GEMINI_API_KEY = 'AIzaSyAp8ZjZ_M-l14UUMvcGyI5IXTQW4FRIaO4';
// Updated API URL to use the correct endpoint
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent';

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
 * Generate a coaching offer using Google Gemini AI with retry logic
 *
 * @param {string} niche - The coaching niche (e.g., "health-coach", "business-coach")
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

        // Add delay between requests to avoid rate limiting
        if (retryCount > 0) {
            const delayMs = retryCount * 5000; // Increase delay with each retry
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

        // Create a detailed prompt for the AI in the style of Eugene Schwartz and Russell Brunson
        let prompt = `
            Create a compelling post-quiz offer for a ${formattedNiche} business to show to ${formattedAudience}, written in the persuasive style of Eugene Schwartz and Russell Brunson.

            This offer will be shown after someone completes a quiz about their needs related to ${formattedNiche} services.
            The goal is to convert the quiz taker into a booked appointment or consultation for the ${formattedNiche} business.

            TurnClicksToClients.com specializes in helping care-driven service businesses fill their calendars with high-value clients.
            We handle the entire client acquisition process including lead generation, follow-up, and appointment booking.

            Our pricing structure includes:
            - Growth Plan: $1,500/month ($50/day) - Core lead generation system with up to $50/day ad spend
            - Accelerate Plan: $2,500/month ($83/day) - Advanced lead generation with up to $100/day ad spend
            - Fast Track Plan: $3,500/month ($117/day) - All-inclusive system with $100+/day ad spend

            Format the response as JSON with the following fields:
            - name: A name for this offer (for internal reference)
            - headline: A powerful, emotionally-charged headline that speaks directly to the prospect's deepest desires or fears (max 12 words)
            - description: A persuasive description using Eugene Schwartz's 5-stage awareness framework and Russell Brunson's "Perfect Webinar" structure (100-150 words)
            - cta_text: An irresistible call to action text for the booking button (5-7 words)

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

        // Add niche-specific guidance based on the business type with Eugene Schwartz and Russell Brunson elements
        if (niche === 'cosmetic-dentists') {
            prompt += `\n\nFor Cosmetic Dentists:
            - BIG PROMISE: "Transform your smile and your life in just one visit"
            - BIG DOMINO: "If I can make you believe that a beautiful smile is the key to confidence and success in both personal and professional life..."
            - FALSE BELIEF to overcome: "Cosmetic dentistry is painful, expensive, and takes too long to see results"
            - OPPORTUNITY SWITCH: From "Cosmetic dentistry is a luxury" to "A perfect smile is an essential investment in your future"
            - STACK: Free smile assessment + digital smile preview + same-day consultation + flexible payment options
            - FUTURE PACING: Have them imagine walking into important meetings with complete confidence, smiling without hesitation in photos
            - SCARCITY: Limited appointments for new patients this month`;
        } else if (niche === 'pmu-artists') {
            prompt += `\n\nFor PMU Artists:
            - BIG PROMISE: "Wake up beautiful every day with perfect brows, lips, or liner"
            - BIG DOMINO: "If I can make you believe that permanent makeup will save you hours every week and boost your confidence instantly..."
            - FALSE BELIEF to overcome: "Permanent makeup looks unnatural and the procedure is painful"
            - OPPORTUNITY SWITCH: From "PMU is a vanity expense" to "PMU is a life-changing time and confidence investment"
            - STACK: Free color matching + consultation with master artist + before/after portfolio review + touch-up guarantee
            - FUTURE PACING: Have them imagine waking up with perfect makeup, swimming/working out without worrying about smudges
            - SCARCITY: Limited spots with master artist this month`;
        } else if (niche === 'weight-loss-clinics') {
            prompt += `\n\nFor Weight Loss Clinics:
            - BIG PROMISE: "Lose weight permanently without extreme diets or endless exercise"
            - BIG DOMINO: "If I can make you believe that your metabolism can be reset with the right scientific approach..."
            - FALSE BELIEF to overcome: "I've tried everything and nothing works for my body type"
            - OPPORTUNITY SWITCH: From "Weight loss is about willpower" to "Weight loss is about having the right metabolic system and support"
            - STACK: Free body composition analysis + metabolic assessment + personalized plan + ongoing support
            - FUTURE PACING: Have them imagine shopping for clothes they love, having energy all day, receiving compliments
            - SCARCITY: Only accepting 5 new clients this month for personalized program`;
        } else if (niche === 'high-end-chiropractors') {
            prompt += `\n\nFor High-End Chiropractors:
            - BIG PROMISE: "Live pain-free without drugs or surgery"
            - BIG DOMINO: "If I can make you believe that your pain isn't just 'something you have to live with'..."
            - FALSE BELIEF to overcome: "Chiropractic care is temporary relief at best"
            - OPPORTUNITY SWITCH: From "Pain management" to "Structural correction and optimal function"
            - STACK: Comprehensive assessment + digital posture analysis + personalized treatment plan + wellness resources
            - FUTURE PACING: Have them imagine waking up without pain, returning to activities they love, playing with kids/grandkids
            - SCARCITY: Limited new patient slots this week for comprehensive assessments`;
        } else if (niche === 'child-care-centers') {
            prompt += `\n\nFor Child Care Centers:
            - BIG PROMISE: "Give your child the perfect start while advancing your career"
            - BIG DOMINO: "If I can make you believe that the right childcare environment actually accelerates your child's development..."
            - FALSE BELIEF to overcome: "My child will miss out on important development if I'm not home full-time"
            - OPPORTUNITY SWITCH: From "Childcare as a necessary evil" to "Educational advantage and social development opportunity"
            - STACK: Center tour + curriculum review + security demonstration + free trial day + priority enrollment
            - FUTURE PACING: Have them imagine their child thriving, learning, making friends while they succeed professionally
            - SCARCITY: Limited spots available in specific age groups`;
        } else if (niche === 'non-surgical-body-contouring') {
            prompt += `\n\nFor Non-Surgical Body Contouring:
            - BIG PROMISE: "Sculpt your dream body without surgery, pain, or downtime"
            - BIG DOMINO: "If I can make you believe that targeted fat reduction is possible without invasive procedures..."
            - FALSE BELIEF to overcome: "The only way to change my body shape is surgery or extreme dieting"
            - OPPORTUNITY SWITCH: From "Body contouring as vanity" to "Body contouring as confidence and self-care"
            - STACK: Body assessment + treatment demonstration + customized plan + before/after portfolio + first session discount
            - FUTURE PACING: Have them imagine wearing clothes they've avoided, feeling confident at the beach, loving their reflection
            - SCARCITY: Limited introductory packages available at special pricing`;
        } else if (niche === 'sleep-apnea-snoring-clinics') {
            prompt += `\n\nFor Sleep Apnea & Snoring Clinics:
            - BIG PROMISE: "Sleep soundly tonight and wake up with energy you haven't felt in years"
            - BIG DOMINO: "If I can make you believe that your fatigue, brain fog, and health issues are directly linked to your breathing during sleep..."
            - FALSE BELIEF to overcome: "Snoring is just annoying, not dangerous" or "CPAP is the only solution"
            - OPPORTUNITY SWITCH: From "Sleep treatment as optional" to "Sleep optimization as essential for health and longevity"
            - STACK: Sleep assessment + home testing kit + treatment options review + partner relief plan + insurance verification
            - FUTURE PACING: Have them imagine waking refreshed, having all-day energy, and their partner thanking them
            - SCARCITY: Limited sleep specialist appointments available this month`;
        } else if (niche === 'hearing-aid-audiology-clinics') {
            prompt += `\n\nFor Hearing Aid & Audiology Clinics:
            - BIG PROMISE: "Reconnect with loved ones and rediscover sounds you've been missing"
            - BIG DOMINO: "If I can make you believe that modern hearing technology is nearly invisible and can selectively enhance only what you want to hear..."
            - FALSE BELIEF to overcome: "Hearing aids are bulky, uncomfortable, and make everything too loud"
            - OPPORTUNITY SWITCH: From "Hearing aids as a sign of aging" to "Hearing technology as a connection to life"
            - STACK: Comprehensive hearing assessment + invisible technology demonstration + real-world sound simulation + risk-free trial
            - FUTURE PACING: Have them imagine effortless conversations in restaurants, hearing grandchildren's voices clearly, enjoying music again
            - SCARCITY: Limited appointments with master audiologist this month`;
        } else if (niche === 'dme-clinics') {
            prompt += `\n\nFor DME Clinics:
            - BIG PROMISE: "Regain your independence and mobility without hassle or confusion"
            - BIG DOMINO: "If I can make you believe that the right equipment, properly fitted, can transform your daily life..."
            - FALSE BELIEF to overcome: "Medical equipment is complicated, expensive, and hard to get approved"
            - OPPORTUNITY SWITCH: From "DME as last resort" to "DME as life-enhancing technology"
            - STACK: Needs assessment + insurance verification + in-home setup + training session + ongoing support
            - FUTURE PACING: Have them imagine moving freely through their home, going out confidently, maintaining independence
            - SCARCITY: Limited in-home assessment appointments available this week`;
        }

        // Add quiz data context if available
        if (quizData && quizData.length > 0) {
            prompt += `\n\nHere is some sample quiz data from users in this niche to help inform the offer:`;

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

        // Make the API request to Gemini with updated format
        const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: prompt
                    }]
                }],
                generationConfig: {
                    temperature: 0.7,
                    topK: 40,
                    topP: 0.95,
                    maxOutputTokens: 2048,
                }
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Gemini API error response:', errorText);
            throw new Error(`Gemini API error: ${response.status} ${response.statusText} - ${errorText}`);
        }

        const data = await response.json();
        console.log('Gemini API response:', data);

        if (!data.candidates || data.candidates.length === 0) {
            if (data.error) {
                throw new Error(`Gemini API error: ${data.error.message || JSON.stringify(data.error)}`);
            } else {
                throw new Error('No response from Gemini API');
            }
        }

        const generatedText = data.candidates[0].content.parts[0].text;

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
        offerData.created_at = new Date().toISOString();
        offerData.updated_at = new Date().toISOString();

        console.log('Successfully generated offer:', offerData.name);
        return offerData;
    } catch (error) {
        console.error('Error generating offer:', error);

        // Check if this is a rate limit error (429) and we haven't exceeded max retries
        if (error.message && error.message.includes('429') && retryCount < maxRetries) {
            console.log(`Rate limit exceeded. Will retry (${retryCount + 1}/${maxRetries})...`);

            // Extract retry delay from error message if available
            let retryDelay = 60000; // Default to 60 seconds
            try {
                const retryDelayMatch = error.message.match(/retryDelay": "(\d+)s"/);
                if (retryDelayMatch && retryDelayMatch[1]) {
                    retryDelay = parseInt(retryDelayMatch[1]) * 1000 + 5000; // Convert to ms and add 5 seconds buffer
                }
            } catch (e) {
                console.warn('Could not parse retry delay, using default', e);
            }

            console.log(`Waiting ${retryDelay/1000} seconds before retry...`);

            // Retry with incremented retry count
            return generateOffer(niche, targetAudience, quizData, retryCount + 1, maxRetries);
        }

        // If it's not a rate limit error or we've exceeded retries, return null
        return null;
    }
}

/**
 * Create multiple offers for different niches and audience segments with rate limiting
 *
 * @param {Array} niches - Array of niche strings
 * @param {Array} audiences - Array of target audience strings
 * @returns {Promise<Array>} - Array of generated offers
 */
async function generateMultipleOffers(niches, audiences) {
    const generatedOffers = [];

    // Process one niche at a time with delays between them
    for (const niche of niches) {
        // Process one audience at a time with delays between them
        for (const audience of audiences) {
            try {
                // Add a delay between requests to avoid rate limiting
                if (generatedOffers.length > 0) {
                    const delayMs = 10000; // 10 seconds between requests
                    console.log(`Waiting ${delayMs/1000} seconds before generating next offer...`);
                    await sleep(delayMs);
                }

                const offer = await generateOffer(niche, audience);
                if (offer) {
                    generatedOffers.push(offer);

                    // Save each offer as it's generated rather than waiting for all
                    try {
                        await saveOfferToSupabase(offer);
                        console.log(`Saved offer "${offer.name}" to Supabase`);
                    } catch (saveError) {
                        console.error('Error saving offer to Supabase:', saveError);
                    }
                }
            } catch (error) {
                console.error(`Failed to generate offer for ${niche}, ${audience}:`, error);
            }
        }
    }

    return generatedOffers;
}

/**
 * Save a generated offer to Supabase
 *
 * @param {Object} offer - The offer data to save
 * @returns {Promise<boolean>} - Whether the save was successful
 */
async function saveOfferToSupabase(offer) {
    try {
        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'apikey': SUPABASE_KEY,
                'Authorization': `Bearer ${SUPABASE_KEY}`
            },
            body: JSON.stringify(offer)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        console.log(`Saved offer "${offer.name}" to Supabase`);
        return true;
    } catch (error) {
        console.error('Error saving offer to Supabase:', error);
        return false;
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
        console.log('Generating personalized post-application offer...');

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

            // Save to Supabase
            await saveOfferToSupabase(offer);

            return offer;
        } else {
            throw new Error('Failed to generate post-application offer');
        }
    } catch (error) {
        console.error('Error generating post-application offer:', error);
        return null;
    }
}

// Export the functions for use in other files
window.geminiIntegration = {
    generateOffer,
    generateMultipleOffers,
    saveOfferToSupabase,
    generatePostApplicationOffer
};
