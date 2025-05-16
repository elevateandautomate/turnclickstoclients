/**
 * Post-Application Offer Generator
 *
 * This file handles generating personalized offers after a user completes an application.
 * It integrates with the quiz results and application answers to create tailored offers.
 */

// Global variables
let applicationData = null;
let quizData = null;
let generatedOffer = null;
let offerVariations = [];
let currentVariationIndex = 0;

// User behavior tracking
let userBehavior = {
    pageLoadTime: new Date(),
    timeOnPage: 0,
    sectionsViewed: [],
    clickedCTA: false,
    scrollDepth: 0,
    lastActivity: new Date()
};

/**
 * Initialize the post-application offer page
 */
async function initPostApplicationOffer() {
    try {
        // Show loading state
        showLoadingState();

        // Get application and quiz data from URL parameters or localStorage
        await loadUserData();

        // Generate a personalized offer
        await generatePersonalizedOffer();

        // Display the offer
        displayOffer();

        // Set up event listeners
        setupEventListeners();

        // Add a small delay before hiding the loading state to ensure everything is ready
        setTimeout(() => {
            // Hide loading state
            hideLoadingState();
        }, 500);
    } catch (error) {
        console.error('Error initializing post-application offer:', error);
        showErrorState(error);
    }
}

/**
 * Load user data from URL parameters or localStorage
 */
async function loadUserData() {
    try {
        // Get application ID and quiz ID from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const applicationId = urlParams.get('application_id');
        const quizId = urlParams.get('quiz_id');

        if (!applicationId || applicationId === '123') {
            console.log('Using demo data for testing');
            // Use demo data for testing
            applicationData = {
                id: 'demo123',
                businessName: 'Smile Perfect Dental',
                businessType: 'Cosmetic Dentist',
                currentClients: '15',
                desiredClients: '30',
                clientValue: '5000',
                marketingChallenges: 'Spending too much time on marketing instead of patients',
                goals: 'Book more high-value smile makeover patients'
            };

            quizData = {
                id: 'quiz123',
                niche: 'cosmetic-dentists',
                total_score: 85,
                primary_outcome_hint: 'ready_to_scale'
            };

            // Skip Supabase fetch for demo data
            return;
        }

        try {
            // Fetch application data from Supabase
            const fetchedData = await fetchFromSupabase('tctc_applications', `?id=eq.${applicationId}`);

            if (!fetchedData || fetchedData.length === 0) {
                console.warn('Application not found, using demo data');
                // Use demo data if application not found
                applicationData = {
                    id: applicationId,
                    businessName: 'Smile Perfect Dental',
                    businessType: 'Cosmetic Dentist',
                    currentClients: '15',
                    desiredClients: '30',
                    clientValue: '2500',
                    marketingChallenges: 'Inconsistent lead flow, high ad costs, and difficulty converting leads to appointments',
                    goals: 'Double monthly new patients and reduce marketing costs'
                };
            } else {
                applicationData = fetchedData[0];
            }
        } catch (error) {
            console.error('Error fetching application data:', error);
            // Use demo data if there's an error
            applicationData = {
                id: applicationId || 'demo123',
                businessName: 'Smile Perfect Dental',
                businessType: 'Cosmetic Dentist',
                currentClients: '15',
                desiredClients: '30',
                clientValue: '2500',
                marketingChallenges: 'Inconsistent lead flow, high ad costs, and difficulty converting leads to appointments',
                goals: 'Double monthly new patients and reduce marketing costs'
            };
        }

        // If we fetched data from Supabase, it's already set above
        // No need to do anything here

        // If quiz ID is provided, fetch quiz data
        if (quizId) {
            quizData = await fetchFromSupabase('tctc_quiz_submission', `?id=eq.${quizId}`);

            if (quizData && quizData.length > 0) {
                quizData = quizData[0];
            }
        }

        console.log('Loaded user data:', { applicationData, quizData });
    } catch (error) {
        console.error('Error loading user data:', error);
        throw error;
    }
}

/**
 * Generate a personalized offer based on application and quiz data
 */
async function generatePersonalizedOffer() {
    try {
        // Check if we already have a generated offer for this application
        const existingOffers = await fetchFromSupabase('tctc_offers',
            `?application_id=eq.${applicationData.id}&is_personalized=eq.true`);

        if (existingOffers && existingOffers.length > 0) {
            // Use existing offer
            generatedOffer = existingOffers[0];
            console.log('Using existing personalized offer:', generatedOffer);

            // Generate variations of the existing offer
            await generateOfferVariationsForTesting(generatedOffer);
            return;
        }

        console.log('Attempting to generate offer with OpenAI...');

        // Generate new offer with OpenAI
        if (window.openaiIntegration && window.openaiIntegration.generatePostApplicationOffer) {
            try {
                // Show a message that we're generating with AI
                const loadingElement = document.getElementById('offer-loading');
                if (loadingElement) {
                    const loadingText = loadingElement.querySelector('p');
                    if (loadingText) {
                        loadingText.textContent = 'Generating your personalized offer with AI...';
                    }
                }

                generatedOffer = await window.openaiIntegration.generatePostApplicationOffer(applicationData, quizData);

                if (generatedOffer) {
                    console.log('Successfully generated new personalized offer with OpenAI:', generatedOffer);

                    // Generate variations of the new offer
                    await generateOfferVariationsForTesting(generatedOffer);
                    return;
                } else {
                    console.warn('OpenAI returned null offer, falling back to default');
                    throw new Error('OpenAI returned null offer');
                }
            } catch (openaiError) {
                console.error('Error with OpenAI API:', openaiError);
                throw openaiError; // Re-throw to be caught by the outer catch
            }
        } else {
            console.warn('OpenAI integration not available, falling back to default offer');
            throw new Error('OpenAI integration not available');
        }

    } catch (error) {
        console.error('Error generating personalized offer:', error);

        // Fall back to a default offer if generation fails
        generatedOffer = createDefaultOffer();

        // Generate variations of the default offer
        await generateOfferVariationsForTesting(generatedOffer);
    }
}

/**
 * Generate variations of the offer for split testing
 *
 * @param {Object} baseOffer - The base offer to create variations from
 */
async function generateOfferVariationsForTesting(baseOffer) {
    try {
        // Check if we have the offer variations module
        if (typeof window.offerVariations !== 'undefined') {
            console.log('Generating offer variations for testing...');

            // Define which elements to vary
            const variationTypes = [
                window.offerVariations.VARIATION_TYPES.HEADLINE,
                window.offerVariations.VARIATION_TYPES.HOOK,
                window.offerVariations.VARIATION_TYPES.CTA
            ];

            // Generate 2 variations
            offerVariations = await window.offerVariations.generateOfferVariations(
                baseOffer,
                variationTypes,
                2
            );

            console.log(`Generated ${offerVariations.length} offer variations:`, offerVariations);

            // Add the original offer as the first variation
            offerVariations.unshift({
                ...baseOffer,
                is_variation: false,
                variation_id: 0
            });

            // Set up variation testing controls
            setupVariationControls();
        } else {
            console.warn('Offer variations module not available');

            // Create a simple variation for testing
            offerVariations = [
                {
                    ...baseOffer,
                    is_variation: false,
                    variation_id: 0
                },
                {
                    ...baseOffer,
                    headline: "Stop Wasting Time on Marketing: Fill Your Calendar With Premium Clients Now",
                    opening_hook: "What if your calendar was consistently booked with ideal clients while you focused exclusively on delivering exceptional service?",
                    cta_text: "Book My Strategy Call",
                    is_variation: true,
                    variation_id: 1
                }
            ];

            // Set up variation testing controls
            setupVariationControls();
        }
    } catch (error) {
        console.error('Error generating offer variations:', error);
    }
}

/**
 * Set up controls for testing offer variations
 * These controls are only shown in admin/testing mode
 */
function setupVariationControls() {
    // Check if we're in admin/testing mode
    const urlParams = new URLSearchParams(window.location.search);
    const isAdminMode = urlParams.get('admin_mode') === 'true';

    // Only show controls in admin mode
    if (!isAdminMode) {
        console.log('Variation controls hidden (not in admin mode)');

        // Still set up automatic variation testing
        setupAutomaticVariationTesting();
        return;
    }

    // Create variation controls if they don't exist
    if (!document.getElementById('variation-controls')) {
        const controlsContainer = document.createElement('div');
        controlsContainer.id = 'variation-controls';
        controlsContainer.className = 'variation-controls';
        controlsContainer.innerHTML = `
            <div class="variation-controls-inner">
                <span>Testing Variations: </span>
                <button id="prev-variation" class="variation-button">&lt; Prev</button>
                <span id="variation-indicator">Original</span>
                <button id="next-variation" class="variation-button">Next &gt;</button>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .variation-controls {
                position: fixed;
                bottom: 20px;
                left: 20px;
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
            }

            .variation-controls-inner {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .variation-button {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                cursor: pointer;
            }

            #variation-indicator {
                min-width: 80px;
                text-align: center;
                font-weight: bold;
            }
        `;

        // Add to document
        document.head.appendChild(style);
        document.body.appendChild(controlsContainer);

        // Set up event listeners
        const prevButton = document.getElementById('prev-variation');
        const nextButton = document.getElementById('next-variation');

        if (prevButton && nextButton) {
            prevButton.addEventListener('click', showPreviousVariation);
            nextButton.addEventListener('click', showNextVariation);
        }

        // Update the variation indicator
        updateVariationIndicator();
    }
}

/**
 * Set up automatic variation testing for real users
 * This randomly selects a variation to show to the user
 */
function setupAutomaticVariationTesting() {
    if (offerVariations.length <= 1) return;

    // Get user ID or generate one if not available
    let userId = localStorage.getItem('user_id');
    if (!userId) {
        userId = 'user_' + Math.random().toString(36).substring(2, 15);
        localStorage.setItem('user_id', userId);
    }

    // Determine which variation to show based on user ID
    // This ensures the same user always sees the same variation
    const variationIndex = Math.abs(hashCode(userId)) % offerVariations.length;

    // Show the selected variation
    currentVariationIndex = variationIndex;
    showCurrentVariation();

    console.log(`Automatic variation testing: showing variation ${variationIndex} to user ${userId}`);
}

/**
 * Simple string hash function for consistent variation selection
 */
function hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
}

/**
 * Show the previous offer variation
 */
function showPreviousVariation() {
    if (offerVariations.length === 0) return;

    currentVariationIndex = (currentVariationIndex - 1 + offerVariations.length) % offerVariations.length;
    showCurrentVariation();
}

/**
 * Show the next offer variation
 */
function showNextVariation() {
    if (offerVariations.length === 0) return;

    currentVariationIndex = (currentVariationIndex + 1) % offerVariations.length;
    showCurrentVariation();
}

/**
 * Show the current variation
 */
function showCurrentVariation() {
    if (offerVariations.length === 0 || !offerVariations[currentVariationIndex]) return;

    // Get the current variation
    const variation = offerVariations[currentVariationIndex];

    // Display the variation
    displayOffer(variation);

    // Update the variation indicator
    updateVariationIndicator();

    // Track the variation view
    trackVariationView(variation);
}

/**
 * Update the variation indicator
 */
function updateVariationIndicator() {
    const indicator = document.getElementById('variation-indicator');
    if (!indicator) return;

    if (offerVariations.length === 0) {
        indicator.textContent = 'No Variations';
        return;
    }

    if (currentVariationIndex === 0) {
        indicator.textContent = 'Original';
    } else {
        indicator.textContent = `Variation ${currentVariationIndex}`;
    }
}

/**
 * Track a variation view in Supabase
 */
async function trackVariationView(variation) {
    try {
        if (!variation || !variation.variation_id) return;

        const viewData = {
            offer_id: generatedOffer.id || 'demo123',
            application_id: applicationData.id,
            variation_id: variation.variation_id,
            viewed_at: new Date().toISOString()
        };

        // Only try to save to Supabase if we're not in demo mode
        if (applicationData.id !== 'demo123') {
            try {
                const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offer_variation_views`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_KEY,
                        'Authorization': `Bearer ${SUPABASE_KEY}`
                    },
                    body: JSON.stringify(viewData)
                });

                if (!response.ok) {
                    console.warn(`Supabase returned status ${response.status}. This is expected in demo mode.`);
                } else {
                    console.log('Tracked variation view in Supabase:', viewData);
                }
            } catch (supabaseError) {
                console.warn('Could not track variation view in Supabase (expected in demo mode):', supabaseError);
            }
        }

        // Log the view data regardless
        console.log('Variation view data:', viewData);
    } catch (error) {
        console.error('Error processing variation view:', error);
    }
}

/**
 * Create a default offer if generation fails
 */
function createDefaultOffer() {
    const businessType = applicationData.businessType || 'your business';
    const businessName = applicationData.businessName || 'your business';
    const currentClients = applicationData.currentClients || '10-15';
    const desiredClients = applicationData.desiredClients || '30+';

    // Create different offers based on business type
    let offer = {
        name: `Default Offer for ${businessType}`,
        headline: `Fill Your ${businessType} Calendar With High-Value Clients Without Wasting Time On Marketing`,
        subheadline: `Discover how we're helping ${businessType} owners book 15-30 new high-value clients every month without the marketing headaches`,
        opening_hook: `${businessName}, what if you could attract ${desiredClients} qualified, high-value patients every month on autopilot while focusing solely on what you do best?`,
        problem_agitation: `Most ${businessType.toLowerCase()} practices are stuck in an endless cycle of marketing frustration. You're spending thousands on ads that don't convert, wasting hours creating content nobody sees, and missing leads because you can't respond fast enough. Meanwhile, your competitors are stealing the clients you deserve, and your calendar has more gaps than you'd like to admit. The worst part? Every hour spent on marketing is an hour away from serving clients and growing your practice. This approach isn't just inefficient—it's actively holding your business back from the growth you know is possible.`,
        solution_introduction: `That's why we created the Client Attraction Engine—a complete done-for-you system that handles every aspect of your client acquisition. No more wasted ad spend, no more missed leads, no more marketing headaches. Just a steady stream of qualified, high-value clients booking directly into your calendar.`,
        bullet_points: [
            "Expertly crafted ads that target your ideal clients with laser precision",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to book",
            "Direct calendar integration so appointments are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One client per city exclusivity—we'll never work with your local competitors"
        ],
        social_proof: `We've already helped 37 ${businessType.toLowerCase()} practices transform their businesses with our system. On average, our clients see a 43% increase in booked appointments within the first 60 days, with some seeing results in as little as 2 weeks. Many have been able to completely eliminate their marketing team or agency, saving thousands while getting better results.`,
        offer_details: `Our Accelerate Plan ($83/day) includes everything you need to fill your calendar with high-value clients: Our proprietary Client Attraction Engine that creates high-converting ads specifically for ${businessType.toLowerCase()} practices, our professional Conversion Crew who responds to every lead within 5 minutes (24/7), our proven follow-up system that nurtures leads until they're ready to book, and direct integration with your calendar so appointments are booked automatically. Plus, you'll get weekly performance reports and monthly strategy calls to continuously optimize your results.`,
        price_justification: `Consider this: If just ONE new client is worth $${clientValue || '2,500'} to your practice, and our system brings you 15-30 new clients every month, that's a potential return of $${(clientValue || 2500) * 15}-$${(clientValue || 2500) * 30} monthly from an investment of just $2,500. That's a 15-30x return on your investment—something most investments can't touch.`,
        guarantee: `If you don't see real, qualified appointments booked on your calendar and measurable growth within the first 30 days, you pay absolutely nothing for our service fee. That's performance, guaranteed.`,
        scarcity: `IMPORTANT: We can only partner with ONE ${businessType.toLowerCase()} per city. Right now, we have just 3 spots available for our Accelerate Plan. Claim your city before your competitor does!`,
        cta_text: 'Claim Your City Now',
        cta_subtext: 'No obligation, 30-day performance guarantee',
        is_personalized: true,
        is_default: true,
        generated_by_ai: false,
        application_id: applicationData.id,
        quiz_id: quizData ? quizData.id : null,
        created_at: new Date().toISOString()
    };

    // Customize based on business type
    if (businessType === 'Cosmetic Dentist') {
        offer.headline = "Fill Your Chair With High-Value Smile Makeover Patients Without Wasting Time On Marketing";
        offer.subheadline = "Discover how we're helping cosmetic dentists book 15-30 new smile makeover patients every month without the marketing headaches";
        offer.opening_hook = `${businessName}, what if you could attract ${desiredClients} qualified, high-value smile makeover patients every month on autopilot while focusing solely on transforming smiles?`;
        offer.problem_agitation = "Most cosmetic dental practices are stuck in an endless cycle of marketing frustration. You're spending thousands on ads that don't convert, wasting hours managing social media that nobody sees, and missing leads because you can't respond fast enough. Meanwhile, your competitors are stealing the patients you deserve, and your chair has more empty time than you'd like to admit. The worst part? Every hour spent on marketing is an hour away from performing smile transformations and growing your practice. This approach isn't just inefficient—it's actively holding your practice back from the growth you know is possible.";
        offer.solution_introduction = "That's why we created the Client Attraction Engine for cosmetic dentists—a complete done-for-you system that handles every aspect of your patient acquisition. No more wasted ad spend, no more missed leads, no more marketing headaches. Just a steady stream of qualified, high-value patients seeking smile makeovers, veneers, and full reconstructions booking directly into your calendar.";
        offer.bullet_points = [
            "Expertly crafted dental ads that target patients seeking cosmetic procedures",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to book",
            "Direct calendar integration so consultations are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One cosmetic dentist per city exclusivity—we'll never work with your local competitors"
        ];
        offer.social_proof = "We've already helped 37 cosmetic dental practices transform their businesses with our system. On average, our dental clients see a 43% increase in booked consultations within the first 60 days, with some seeing results in as little as 2 weeks. Many have been able to completely eliminate their marketing team or agency, saving thousands while getting better results.";
        offer.offer_details = "Our Accelerate Plan ($83/day) includes everything you need to fill your chair with high-value patients: Our proprietary Client Attraction Engine that creates high-converting ads specifically for cosmetic dental procedures, our professional Conversion Crew who responds to every lead within 5 minutes (24/7), our proven follow-up system that nurtures leads until they're ready to book, and direct integration with your calendar so consultations are booked automatically. Plus, you'll get weekly performance reports and monthly strategy calls to continuously optimize your results.";
        offer.price_justification = `Consider this: If just ONE new smile makeover patient is worth $${clientValue || '5,000'} to your practice, and our system brings you 15-30 new patients every month, that's a potential return of $${(clientValue || 5000) * 15}-$${(clientValue || 5000) * 30} monthly from an investment of just $2,500. That's a 30-60x return on your investment—something most investments can't touch.`;
        offer.scarcity = "IMPORTANT: We can only partner with ONE cosmetic dentist per city. Right now, we have just 3 spots available for our Accelerate Plan. Claim your city before your competitor does!";
    } else if (businessType === 'PMU Artist') {
        offer.headline = "Book Your Calendar Solid With Premium PMU Clients Without The Instagram Hustle";
        offer.subheadline = "Discover how we're helping PMU artists book 15-30 new high-paying clients every month without spending hours on social media";
        offer.opening_hook = `${businessName}, what if you could attract ${desiredClients} qualified, high-paying PMU clients every month without the exhausting social media hustle?`;
        offer.problem_agitation = "Most PMU artists are trapped in an endless cycle of content creation and DM management. You're spending hours creating the perfect posts, responding to inquiries at all hours, and still missing potential clients because you can't keep up. Meanwhile, your competitors with bigger followings are stealing the clients you deserve, and your calendar has more gaps than you'd like to admit. The worst part? Every hour spent on Instagram is an hour away from doing what you love—creating beautiful brows, lips, and liner for your clients. This approach isn't just exhausting—it's actively holding your business back from the growth you know is possible.";
        offer.solution_introduction = "That's why we created the Client Attraction Engine for PMU artists—a complete done-for-you system that handles every aspect of your client acquisition. No more content creation burnout, no more missed DMs, no more social media anxiety. Just a steady stream of qualified, high-paying clients booking directly into your calendar.";
        offer.bullet_points = [
            "Expertly crafted ads that target clients seeking premium PMU services",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to book",
            "Direct calendar integration so appointments are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One PMU artist per city exclusivity—we'll never work with your local competitors"
        ];
        offer.social_proof = "We've already helped 29 PMU artists transform their businesses with our system. On average, our PMU clients see a 51% increase in booked appointments within the first 60 days, with some seeing results in as little as 2 weeks. Many have been able to completely eliminate their social media marketing stress, saving countless hours while getting better results.";
        offer.offer_details = "Our Accelerate Plan ($83/day) includes everything you need to fill your calendar with high-paying clients: Our proprietary Client Attraction Engine that creates high-converting ads specifically for PMU services, our professional Conversion Crew who responds to every lead within 5 minutes (24/7), our proven follow-up system that nurtures leads until they're ready to book, and direct integration with your calendar so appointments are booked automatically. Plus, you'll get weekly performance reports and monthly strategy calls to continuously optimize your results.";
        offer.price_justification = `Consider this: If just ONE new PMU client is worth $${clientValue || '800'} to your business, and our system brings you 15-30 new clients every month, that's a potential return of $${(clientValue || 800) * 15}-$${(clientValue || 800) * 30} monthly from an investment of just $2,500. That's a 5-10x return on your investment—something most investments can't touch.`;
        offer.scarcity = "IMPORTANT: We can only partner with ONE PMU artist per city. Right now, we have just 3 spots available for our Accelerate Plan. Claim your city before your competitor does!";
    } else if (businessType === 'Weight Loss Clinic') {
        offer.headline = "Fill Your Weight Loss Clinic With Committed Clients Without Expensive Ad Campaigns";
        offer.subheadline = "Discover how we're helping weight loss clinics book 15-30 new committed clients every month without wasting thousands on ineffective marketing";
        offer.opening_hook = `${businessName}, what if you could attract ${desiredClients} motivated, ready-to-commit weight loss clients every month without the massive ad spend and constant content creation?`;
        offer.problem_agitation = "Most weight loss clinics are trapped in an expensive cycle of marketing frustration. You're spending thousands on ads that don't convert, wasting hours creating before-and-after content, and missing leads because you can't respond fast enough. Meanwhile, your competitors are stealing the clients you deserve, and your appointment book has more gaps than you'd like to admit. The worst part? Every dollar wasted on ineffective marketing is money that could be invested in better equipment, staff training, or facility improvements. This approach isn't just expensive—it's actively holding your clinic back from the growth you know is possible.";
        offer.solution_introduction = "That's why we created the Client Attraction Engine for weight loss clinics—a complete done-for-you system that handles every aspect of your client acquisition. No more wasted ad spend, no more missed leads, no more marketing headaches. Just a steady stream of motivated, ready-to-commit clients booking directly into your calendar.";
        offer.bullet_points = [
            "Expertly crafted ads that target people serious about weight loss results",
            "24/7 lead response within 5 minutes by our professional Conversion Crew",
            "Automated follow-up sequences that nurture leads until they're ready to commit",
            "Direct calendar integration so consultations are booked without your involvement",
            "Comprehensive analytics dashboard showing your exact ROI on every marketing dollar",
            "One weight loss clinic per city exclusivity—we'll never work with your local competitors"
        ];
        offer.social_proof = "We've already helped 31 weight loss clinics transform their businesses with our system. On average, our clients see a 47% increase in booked consultations within the first 60 days, with some seeing results in as little as 2 weeks. Many have been able to completely eliminate their marketing team or agency, saving thousands while getting better results.";
        offer.offer_details = "Our Accelerate Plan ($83/day) includes everything you need to fill your clinic with committed clients: Our proprietary Client Attraction Engine that creates high-converting ads specifically for weight loss services, our professional Conversion Crew who responds to every lead within 5 minutes (24/7), our proven follow-up system that nurtures leads until they're ready to book, and direct integration with your calendar so consultations are booked automatically. Plus, you'll get weekly performance reports and monthly strategy calls to continuously optimize your results.";
        offer.price_justification = `Consider this: If just ONE new weight loss client is worth $${clientValue || '3,000'} to your clinic, and our system brings you 15-30 new clients every month, that's a potential return of $${(clientValue || 3000) * 15}-$${(clientValue || 3000) * 30} monthly from an investment of just $2,500. That's a 18-36x return on your investment—something most investments can't touch.`;
        offer.scarcity = "IMPORTANT: We can only partner with ONE weight loss clinic per city. Right now, we have just 3 spots available for our Accelerate Plan. Claim your city before your competitor does!";
    }

    return offer;
}

/**
 * Display the generated offer on the page
 *
 * @param {Object} offerToDisplay - The offer to display (defaults to generatedOffer)
 */
function displayOffer(offerToDisplay = null) {
    try {
        // Use the provided offer or fall back to the generated offer
        const offer = offerToDisplay || generatedOffer;

        if (!offer) {
            console.error('No offer to display');
            return;
        }

        // Helper function to update element text if it exists
        function updateElement(id, text) {
            const element = document.getElementById(id);
            if (element && text) {
                element.innerHTML = text.replace(/\n/g, '<br>');
            }
        }

        // Update headline
        updateElement('offer-headline', offer.headline);

        // Update subheadline if available
        updateElement('offer-subheadline', offer.subheadline);

        // Update opening hook if available
        updateElement('offer-opening-hook', offer.opening_hook);

        // Update problem agitation if available
        updateElement('offer-problem-agitation', offer.problem_agitation);

        // Update solution introduction if available
        updateElement('offer-solution-introduction', offer.solution_introduction);

        // Update bullet points if available
        if (offer.bullet_points && Array.isArray(offer.bullet_points)) {
            const bulletPointsList = document.getElementById('offer-bullet-points');
            if (bulletPointsList) {
                bulletPointsList.innerHTML = '';
                offer.bullet_points.forEach(point => {
                    const li = document.createElement('li');
                    li.innerHTML = point;
                    li.style.marginBottom = '0.5rem';
                    bulletPointsList.appendChild(li);
                });
            }
        }

        // Update social proof if available
        updateElement('offer-social-proof', offer.social_proof);

        // Update offer details if available
        updateElement('offer-details', offer.offer_details);

        // Update price justification if available
        updateElement('offer-price-justification', offer.price_justification);

        // Update guarantee if available
        updateElement('offer-guarantee', offer.guarantee || 'If you don\'t see real, qualified appointments booked on your calendar and measurable growth within the first 30 days, you pay absolutely nothing for our service fee. That\'s performance, guaranteed.');

        // Update scarcity if available
        updateElement('offer-scarcity-text', offer.scarcity);

        // Update CTA button
        const ctaButton = document.getElementById('offer-cta-button');
        if (ctaButton && offer.cta_text) {
            ctaButton.textContent = offer.cta_text;
        }

        // Update CTA subtext if available
        updateElement('offer-cta-subtext', offer.cta_subtext);

        // Personalize with business name if available
        if (applicationData.businessName) {
            const businessNameElements = document.querySelectorAll('.business-name-placeholder');
            businessNameElements.forEach(element => {
                element.textContent = applicationData.businessName;
            });
        }

        // Check if we're in admin/testing mode
        const urlParams = new URLSearchParams(window.location.search);
        const isAdminMode = urlParams.get('admin_mode') === 'true';

        // Add variation indicator if this is a variation and we're in admin mode
        if (offer.is_variation && isAdminMode) {
            // Add a small badge to indicate this is a variation
            const variationBadge = document.getElementById('variation-badge') || document.createElement('div');
            variationBadge.id = 'variation-badge';
            variationBadge.className = 'variation-badge';
            variationBadge.textContent = `Variation ${offer.variation_id}`;
            variationBadge.style.position = 'fixed';
            variationBadge.style.top = '10px';
            variationBadge.style.right = '10px';
            variationBadge.style.backgroundColor = '#4a90e2';
            variationBadge.style.color = 'white';
            variationBadge.style.padding = '5px 10px';
            variationBadge.style.borderRadius = '3px';
            variationBadge.style.fontSize = '12px';
            variationBadge.style.zIndex = '1000';

            if (!document.getElementById('variation-badge')) {
                document.body.appendChild(variationBadge);
            }
        } else {
            // Remove the variation badge if this is the original or not in admin mode
            const variationBadge = document.getElementById('variation-badge');
            if (variationBadge) {
                variationBadge.remove();
            }
        }

    } catch (error) {
        console.error('Error displaying offer:', error);
    }
}

/**
 * Set up event listeners for the offer page
 */
function setupEventListeners() {
    // CTA button click
    const ctaButton = document.getElementById('offer-cta-button');
    if (ctaButton) {
        ctaButton.addEventListener('click', function() {
            // Track click
            trackOfferClick();

            // Update user behavior
            userBehavior.clickedCTA = true;
            userBehavior.lastActivity = new Date();

            // Save behavior before leaving page
            saveUserBehavior();

            // Redirect to booking page or show booking modal
            window.location.href = 'booking.html?application_id=' + applicationData.id;
        });
    }

    // Set up scroll tracking
    window.addEventListener('scroll', throttle(trackScrollDepth, 500));

    // Set up section visibility tracking
    window.addEventListener('scroll', throttle(trackSectionViews, 1000));

    // Set up user activity tracking
    ['mousemove', 'keydown', 'click', 'touchstart'].forEach(eventType => {
        window.addEventListener(eventType, function() {
            userBehavior.lastActivity = new Date();
        });
    });

    // Set up page exit tracking
    window.addEventListener('beforeunload', function() {
        // Calculate time on page
        userBehavior.timeOnPage = Math.round((new Date() - userBehavior.pageLoadTime) / 1000);

        // Save behavior before leaving page
        saveUserBehavior();

        // Generate follow-up sequence if needed
        if (!userBehavior.clickedCTA && userBehavior.timeOnPage > 30) {
            generateFollowupForLead();
        }
    });
}

/**
 * Track which sections of the offer the user has viewed
 */
function trackSectionViews() {
    // Define the sections to track
    const sections = [
        { id: 'offer-headline', name: 'headline' },
        { id: 'offer-opening-hook', name: 'hook' },
        { id: 'offer-problem-agitation', name: 'problem' },
        { id: 'offer-solution-introduction', name: 'solution' },
        { id: 'offer-bullet-points', name: 'bullets' },
        { id: 'offer-social-proof', name: 'social_proof' },
        { id: 'offer-details', name: 'details' },
        { id: 'offer-price-justification', name: 'pricing' },
        { id: 'offer-guarantee', name: 'guarantee' },
        { id: 'offer-scarcity-text', name: 'scarcity' },
        { id: 'offer-cta-button', name: 'cta' }
    ];

    // Check each section
    sections.forEach(section => {
        const element = document.getElementById(section.id);
        if (element && isElementInViewport(element)) {
            // Add to sections viewed if not already there
            if (!userBehavior.sectionsViewed.includes(section.name)) {
                userBehavior.sectionsViewed.push(section.name);
                console.log(`User viewed section: ${section.name}`);
            }
        }
    });
}

/**
 * Track the user's scroll depth
 */
function trackScrollDepth() {
    // Calculate scroll depth as percentage
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrollDepth = Math.round((scrollTop / scrollHeight) * 100);

    // Update if it's deeper than before
    if (scrollDepth > userBehavior.scrollDepth) {
        userBehavior.scrollDepth = scrollDepth;
    }
}

/**
 * Save user behavior to Supabase
 */
async function saveUserBehavior() {
    try {
        // Calculate time on page
        userBehavior.timeOnPage = Math.round((new Date() - userBehavior.pageLoadTime) / 1000);

        const behaviorData = {
            application_id: applicationData.id,
            offer_id: generatedOffer.id || 'demo123',
            time_on_page: userBehavior.timeOnPage,
            sections_viewed: userBehavior.sectionsViewed,
            clicked_cta: userBehavior.clickedCTA,
            scroll_depth: userBehavior.scrollDepth,
            variation_id: offerVariations.length > 0 ? offerVariations[currentVariationIndex].variation_id : 0,
            recorded_at: new Date().toISOString()
        };

        // Only try to save to Supabase if we're not in demo mode
        if (applicationData.id !== 'demo123') {
            try {
                const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_user_behavior`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_KEY,
                        'Authorization': `Bearer ${SUPABASE_KEY}`
                    },
                    body: JSON.stringify(behaviorData)
                });

                if (!response.ok) {
                    console.warn(`Supabase returned status ${response.status}. This is expected in demo mode.`);
                } else {
                    console.log('Saved user behavior to Supabase:', behaviorData);
                }
            } catch (supabaseError) {
                console.warn('Could not save to Supabase (expected in demo mode):', supabaseError);
            }
        }

        // Log the behavior data regardless
        console.log('User behavior data:', behaviorData);
    } catch (error) {
        console.error('Error processing user behavior:', error);
    }
}

/**
 * Generate follow-up sequence for a lead who didn't convert
 */
async function generateFollowupForLead() {
    try {
        // Only generate follow-ups if we have the ChatGPT follow-up module
        if (window.chatgptFollowup && window.chatgptFollowup.generateFollowupSequence) {
            console.log('Generating follow-up sequence for lead who didn\'t convert');

            // Generate the follow-up sequence
            const followups = await window.chatgptFollowup.generateFollowupSequence(
                applicationData,
                generatedOffer,
                userBehavior
            );

            // Save the follow-ups to Supabase
            if (followups && followups.length > 0) {
                const followupData = {
                    application_id: applicationData.id,
                    offer_id: generatedOffer.id || 'demo123',
                    followup_sequence: followups,
                    user_behavior: userBehavior,
                    created_at: new Date().toISOString()
                };

                // Only try to save to Supabase if we're not in demo mode
                if (applicationData.id !== 'demo123') {
                    try {
                        const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_followup_sequences`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'apikey': SUPABASE_KEY,
                                'Authorization': `Bearer ${SUPABASE_KEY}`
                            },
                            body: JSON.stringify(followupData)
                        });

                        if (!response.ok) {
                            console.warn(`Supabase returned status ${response.status}. This is expected in demo mode.`);
                        } else {
                            console.log('Saved follow-up sequence to Supabase:', followupData);
                        }
                    } catch (supabaseError) {
                        console.warn('Could not save follow-up to Supabase (expected in demo mode):', supabaseError);
                    }
                }

                // Log the follow-up data regardless
                console.log('Generated follow-up sequence:', followups);
            }
        }
    } catch (error) {
        console.error('Error generating follow-up sequence:', error);
    }
}

/**
 * Check if an element is in the viewport
 */
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Throttle a function to prevent too many calls
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Track offer click in Supabase
 */
async function trackOfferClick() {
    try {
        const clickData = {
            offer_id: generatedOffer.id || 'demo123',
            application_id: applicationData.id,
            quiz_id: quizData ? quizData.id : null,
            clicked_at: new Date().toISOString()
        };

        // Only try to save to Supabase if we're not in demo mode
        if (applicationData.id !== 'demo123') {
            try {
                const response = await fetch(`${SUPABASE_URL}/rest/v1/tctc_offer_clicks`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'apikey': SUPABASE_KEY,
                        'Authorization': `Bearer ${SUPABASE_KEY}`
                    },
                    body: JSON.stringify(clickData)
                });

                if (!response.ok) {
                    console.warn(`Supabase returned status ${response.status}. This is expected in demo mode.`);
                } else {
                    console.log('Tracked offer click in Supabase:', clickData);
                }
            } catch (supabaseError) {
                console.warn('Could not track click in Supabase (expected in demo mode):', supabaseError);
            }
        }

        // Log the click data regardless
        console.log('Offer click data:', clickData);
    } catch (error) {
        console.error('Error processing offer click:', error);
    }
}

/**
 * Show loading state
 */
function showLoadingState() {
    const loadingElement = document.getElementById('offer-loading');
    const contentElement = document.getElementById('offer-content');

    if (loadingElement) {
        loadingElement.style.display = 'flex';
    }

    if (contentElement) {
        contentElement.style.display = 'none';
    }
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const loadingElement = document.getElementById('offer-loading');
    const contentElement = document.getElementById('offer-content');
    const errorElement = document.getElementById('offer-error');

    if (loadingElement) {
        loadingElement.style.display = 'none';
    }

    if (errorElement) {
        errorElement.style.display = 'none';
    }

    if (contentElement) {
        // Force display block and ensure it's visible
        contentElement.style.display = 'block';
        contentElement.style.opacity = '1';
        contentElement.style.visibility = 'visible';

        // Force a reflow to ensure the browser applies the changes
        void contentElement.offsetWidth;

        console.log('Content element should now be visible');
    }
}

/**
 * Show error state
 */
function showErrorState(error) {
    const errorElement = document.getElementById('offer-error');
    const loadingElement = document.getElementById('offer-loading');
    const contentElement = document.getElementById('offer-content');

    if (errorElement) {
        errorElement.style.display = 'block';
        errorElement.querySelector('.error-message').textContent = error.message || 'An error occurred';
    }

    if (loadingElement) {
        loadingElement.style.display = 'none';
    }

    if (contentElement) {
        contentElement.style.display = 'none';
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', initPostApplicationOffer);
