// Enhanced User Journey Tracking Script
document.addEventListener('DOMContentLoaded', function() {
    // Initialize or retrieve user session ID
    if (!localStorage.getItem('tctc_session_id')) {
        const sessionId = generateUUID();
        localStorage.setItem('tctc_session_id', sessionId);
    }

    // Initialize or retrieve user ID
    if (!localStorage.getItem('tctc_user_id')) {
        const userId = generateUUID();
        localStorage.setItem('tctc_user_id', userId);
    }

    // Initialize flow hash if it doesn't exist (for backward compatibility)
    if (!localStorage.getItem('flow_hash')) {
        const flowHash = generateUUID();
        localStorage.setItem('flow_hash', flowHash);
    }

    // Store UTM parameters and referrer info
    storeTrafficSourceData();

    // Track page view
    trackPageView();

    // Setup event tracking
    setupEventTracking();
});

// Generate UUID for user/session identification
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Store traffic source data
function storeTrafficSourceData() {
    const params = new URLSearchParams(window.location.search);

    // Store UTM parameters (only if not already stored or if new values provided)
    if (!localStorage.getItem('traffic_source') || params.get('utm_source') || params.get('source')) {
        localStorage.setItem('traffic_source', params.get('utm_source') || params.get('source') || document.referrer || 'direct');
    }

    if (!localStorage.getItem('utm_medium') || params.get('utm_medium')) {
        localStorage.setItem('utm_medium', params.get('utm_medium') || '');
    }

    if (!localStorage.getItem('utm_campaign') || params.get('utm_campaign')) {
        localStorage.setItem('utm_campaign', params.get('utm_campaign') || '');
    }

    if (!localStorage.getItem('landing_page')) {
        localStorage.setItem('landing_page', window.location.href);
        localStorage.setItem('entry_point', 'landing_page');
    }

    // Store user data from URL parameters if available
    if (params.get('firstName')) {
        localStorage.setItem('user_first_name', params.get('firstName'));
    }
    if (params.get('lastName')) {
        localStorage.setItem('user_last_name', params.get('lastName'));
    }
    if (params.get('businessName')) {
        localStorage.setItem('user_business_name', params.get('businessName'));
    }
    if (params.get('email')) {
        localStorage.setItem('user_email', params.get('email'));
    }
    if (params.get('track_source')) {
        localStorage.setItem('track_source', params.get('track_source'));
    }
}

// Track page view
function trackPageView() {
    const params = new URLSearchParams(window.location.search);
    const path = window.location.pathname;

    // Determine page type
    let pageType = 'other';
    if (path.includes('index.html') || path === '/' || path.endsWith('/')) {
        pageType = 'home';
    } else if (path.includes('-quiz.html')) {
        pageType = 'quiz';
    } else if (path.includes('-variant-')) {
        pageType = 'quiz_result';
    } else if (path.includes('universal-application-form.html')) {
        pageType = 'application';
    } else if (path.includes('niches/')) {
        pageType = 'niche';
    }

    // Extract niche, bucket, and variant from URL
    const { niche, bucket, variant } = extractPageContext(path, params);

    // Track the page view
    trackEvent('page_view', {
        page_url: window.location.href,
        page_title: document.title,
        page_type: pageType,
        niche: niche,
        bucket: bucket,
        variant: variant,
        referrer: document.referrer,
        time_on_page_start: new Date().toISOString()
    });

    // Add tracking parameters to all links
    setTimeout(addTrackingToLinks, 500);
}

// Extract page context (niche, bucket, variant)
function extractPageContext(path, params) {
    let niche = '';
    let bucket = '';
    let variant = '';

    // Extract niche
    if (params.get('niche')) {
        niche = params.get('niche');
    } else if (path.includes('/quiz-applications/')) {
        const pathParts = path.split('/');
        const nicheIndex = pathParts.findIndex(part => part === 'quiz-applications');
        if (nicheIndex >= 0 && pathParts.length > nicheIndex + 1) {
            niche = pathParts[nicheIndex + 1];
        }
    } else if (path.includes('niches/')) {
        const match = path.match(/niches\/([^-/]+)/);
        if (match && match[1]) {
            niche = match[1];
        }
    }

    // Extract bucket
    if (params.get('bucket')) {
        bucket = params.get('bucket');
    } else if (path.includes('variant-')) {
        const pathParts = path.split('/');
        const bucketPartIndex = pathParts.findIndex(part => part.includes('variant-'));
        if (bucketPartIndex > 0) {
            bucket = pathParts[bucketPartIndex - 1];
        }
    }

    // Extract variant
    if (params.get('variant')) {
        variant = params.get('variant');
    } else if (path.includes('variant-')) {
        const match = path.match(/variant-([a-c]-[^.]+)/i);
        if (match && match[1]) {
            variant = match[1];
        }
    }

    return { niche, bucket, variant };
}

// Add tracking parameters to all links
function addTrackingToLinks() {
    const allLinks = document.querySelectorAll('a');
    allLinks.forEach(link => {
        try {
            if (link.href && link.href.includes(window.location.hostname) && !link.href.includes('#')) {
                const url = new URL(link.href);

                // Don't modify links that already have tracking parameters
                if (!url.searchParams.has('flow_hash')) {
                    // Add tracking parameters
                    url.searchParams.append('flow_hash', localStorage.getItem('flow_hash') || '');
                    url.searchParams.append('session_id', localStorage.getItem('tctc_session_id') || '');
                    url.searchParams.append('user_id', localStorage.getItem('tctc_user_id') || '');

                    if (localStorage.getItem('traffic_source')) {
                        url.searchParams.append('source', localStorage.getItem('traffic_source'));
                    }

                    if (localStorage.getItem('utm_medium')) {
                        url.searchParams.append('utm_medium', localStorage.getItem('utm_medium'));
                    }

                    if (localStorage.getItem('utm_campaign')) {
                        url.searchParams.append('utm_campaign', localStorage.getItem('utm_campaign'));
                    }

                    // Add niche if available
                    const path = window.location.pathname;
                    const params = new URLSearchParams(window.location.search);
                    const { niche } = extractPageContext(path, params);
                    if (niche) {
                        url.searchParams.append('niche', niche);
                    }

                    link.href = url.toString();

                    // Add click tracking
                    link.addEventListener('click', function(e) {
                        trackEvent('link_click', {
                            link_url: this.href,
                            link_text: this.textContent.trim(),
                            destination_page: this.href
                        });
                    });
                }
            }
        } catch (e) {
            console.error('Error adding tracking to link:', e);
        }
    });
}

// Setup event tracking for various interactions
function setupEventTracking() {
    // Track quiz interactions
    setupQuizTracking();

    // Track form interactions
    setupFormTracking();

    // Track scroll depth
    setupScrollTracking();

    // Track time on page
    setupTimeTracking();

    // Track clicks on buttons and interactive elements
    setupClickTracking();
}

// Track quiz interactions
function setupQuizTracking() {
    // Track quiz start
    const startQuizBtn = document.getElementById('start-quiz-btn');
    if (startQuizBtn) {
        startQuizBtn.addEventListener('click', function() {
            trackEvent('quiz_started', {
                action: 'start_quiz',
                quiz_type: document.title || 'Unknown Quiz'
            });
        });
    }

    // Track question answers
    const quizAnswersDiv = document.getElementById('quiz-answers');
    if (quizAnswersDiv) {
        quizAnswersDiv.addEventListener('click', function(e) {
            if (e.target.classList.contains('answer-btn')) {
                const questionText = document.querySelector('#quiz-question h2')?.textContent || 'Unknown Question';
                const answerText = e.target.textContent;
                const currentQuestionIndex = window.currentQuestionIndex || 0;

                trackEvent('quiz_answer_selected', {
                    question: questionText,
                    answer: answerText,
                    question_index: currentQuestionIndex,
                    time_to_answer: calculateTimeOnQuestion()
                });

                // Reset question timer for next question
                window.questionStartTime = new Date();
            }
        });
    }

    // Track form submission
    const leadCaptureForm = document.querySelector('#lead-capture-form form');
    if (leadCaptureForm) {
        leadCaptureForm.addEventListener('submit', function() {
            trackEvent('quiz_completed', {
                action: 'submit_lead_form',
                quiz_type: document.title || 'Unknown Quiz'
            });
        });
    }

    // Set initial question timer
    window.questionStartTime = new Date();
}

// Calculate time spent on current question
function calculateTimeOnQuestion() {
    if (!window.questionStartTime) {
        return 0;
    }

    const now = new Date();
    const timeSpent = now - window.questionStartTime;
    return Math.round(timeSpent / 1000); // Convert to seconds
}

// Track form interactions
function setupFormTracking() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        // Track form field focus
        const formFields = form.querySelectorAll('input, textarea, select');
        formFields.forEach(field => {
            field.addEventListener('focus', function() {
                trackEvent('form_field_focus', {
                    field_name: this.name,
                    field_type: this.type,
                    form_id: form.id || 'unknown_form'
                });
            });

            // Track field completion
            field.addEventListener('blur', function() {
                if (this.value.trim() !== '') {
                    trackEvent('form_field_completed', {
                        field_name: this.name,
                        field_type: this.type,
                        form_id: form.id || 'unknown_form',
                        is_valid: this.checkValidity()
                    });
                }
            });
        });

        // Track form submission
        form.addEventListener('submit', function(e) {
            // Add tracking data as hidden fields
            if (!this.querySelector('input[name="flow_hash"]')) {
                const fields = [
                    { name: 'flow_hash', value: localStorage.getItem('flow_hash') || '' },
                    { name: 'session_id', value: localStorage.getItem('tctc_session_id') || '' },
                    { name: 'user_id', value: localStorage.getItem('tctc_user_id') || '' },
                    { name: 'traffic_source', value: localStorage.getItem('traffic_source') || 'direct' },
                    { name: 'utm_medium', value: localStorage.getItem('utm_medium') || '' },
                    { name: 'utm_campaign', value: localStorage.getItem('utm_campaign') || '' },
                    { name: 'landing_page', value: localStorage.getItem('landing_page') || '' },
                    { name: 'entry_point', value: localStorage.getItem('entry_point') || '' }
                ];

                fields.forEach(field => {
                    const input = document.createElement('input');
                    input.type = 'hidden';
                    input.name = field.name;
                    input.value = field.value;
                    this.appendChild(input);
                });
            }

            trackEvent('form_submitted', {
                form_id: this.id || 'unknown_form',
                form_action: this.action,
                form_fields: Array.from(this.elements)
                    .filter(el => el.name && !el.name.startsWith('flow_') && el.type !== 'submit')
                    .map(el => el.name)
            });
        });
    });
}

// Track scroll depth
function setupScrollTracking() {
    let maxScrollDepth = 0;
    let scrollDepthMarkers = [25, 50, 75, 90, 100];
    let reachedMarkers = [];

    window.addEventListener('scroll', function() {
        // Calculate scroll depth as percentage
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrollDepth = Math.round((scrollTop / scrollHeight) * 100);

        // Update max scroll depth
        if (scrollDepth > maxScrollDepth) {
            maxScrollDepth = scrollDepth;

            // Check if we've hit any markers
            scrollDepthMarkers.forEach(marker => {
                if (scrollDepth >= marker && !reachedMarkers.includes(marker)) {
                    reachedMarkers.push(marker);
                    trackEvent('scroll_depth', {
                        depth_percentage: marker,
                        page_url: window.location.href,
                        page_title: document.title
                    });
                }
            });
        }
    });

    // Track max scroll depth when user leaves page
    window.addEventListener('beforeunload', function() {
        trackEvent('max_scroll_depth', {
            depth_percentage: maxScrollDepth,
            page_url: window.location.href,
            page_title: document.title
        });
    });
}

// Track time on page
function setupTimeTracking() {
    const startTime = new Date();
    let timeOnPageTracked = false;

    // Track time intervals
    const intervals = [10, 30, 60, 120, 300]; // seconds
    intervals.forEach(interval => {
        setTimeout(() => {
            trackEvent('time_on_page', {
                seconds: interval,
                page_url: window.location.href,
                page_title: document.title
            });
        }, interval * 1000);
    });

    // Track total time on page when leaving
    window.addEventListener('beforeunload', function() {
        if (!timeOnPageTracked) {
            const endTime = new Date();
            const timeSpent = Math.round((endTime - startTime) / 1000); // seconds

            trackEvent('page_exit', {
                time_on_page: timeSpent,
                page_url: window.location.href,
                page_title: document.title,
                exit_to: document.activeElement.href || null
            });

            timeOnPageTracked = true;
        }
    });
}

// Track clicks on buttons and interactive elements
function setupClickTracking() {
    document.addEventListener('click', function(e) {
        // Track button clicks
        if (e.target.tagName === 'BUTTON' ||
            (e.target.tagName === 'A' && e.target.classList.contains('btn')) ||
            e.target.type === 'submit') {

            trackEvent('button_click', {
                button_text: e.target.textContent.trim(),
                button_id: e.target.id || null,
                button_classes: Array.from(e.target.classList).join(' '),
                page_location: getElementPath(e.target)
            });
        }

        // Track clicks on interactive elements
        if (e.target.hasAttribute('data-track-click') ||
            e.target.closest('[data-track-click]')) {

            const trackElement = e.target.hasAttribute('data-track-click') ?
                e.target : e.target.closest('[data-track-click]');

            trackEvent('tracked_element_click', {
                element_type: trackElement.tagName.toLowerCase(),
                element_id: trackElement.id || null,
                element_text: trackElement.textContent.trim().substring(0, 100),
                tracking_id: trackElement.getAttribute('data-track-click'),
                page_location: getElementPath(trackElement)
            });
        }
    });
}

// Get element path for better context
function getElementPath(element) {
    let path = [];
    let currentElement = element;

    while (currentElement && currentElement !== document.body) {
        let identifier = currentElement.tagName.toLowerCase();

        if (currentElement.id) {
            identifier += `#${currentElement.id}`;
        } else if (currentElement.className) {
            const classes = Array.from(currentElement.classList).join('.');
            if (classes) {
                identifier += `.${classes}`;
            }
        }

        path.unshift(identifier);
        currentElement = currentElement.parentElement;
    }

    return path.join(' > ');
}

// Core tracking function to send events to Supabase
function trackEvent(eventType, eventData) {
    // Get basic tracking data
    const sessionId = localStorage.getItem('tctc_session_id');
    const userId = localStorage.getItem('tctc_user_id');
    const flowHash = localStorage.getItem('flow_hash');

    // Get URL parameters
    const params = new URLSearchParams(window.location.search);

    // Determine page context
    const path = window.location.pathname;
    const pageType = determinePageType(path);
    const { niche, bucket, variant } = extractPageContext(path, params);

    // Combine all data
    const trackingData = {
        event_type: eventType,
        event_data: eventData,
        session_id: sessionId,
        user_id: userId,
        flow_hash: flowHash,
        page_type: pageType,
        niche: niche,
        bucket: bucket,
        variant: variant,
        user_first_name: params.get('firstName') || localStorage.getItem('user_first_name') || '',
        user_last_name: params.get('lastName') || localStorage.getItem('user_last_name') || '',
        user_business_name: params.get('businessName') || localStorage.getItem('user_business_name') || '',
        user_email: params.get('email') || localStorage.getItem('user_email') || '',
        traffic_source: localStorage.getItem('traffic_source') || 'direct',
        utm_medium: localStorage.getItem('utm_medium') || '',
        utm_campaign: localStorage.getItem('utm_campaign') || '',
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        screen_width: window.innerWidth,
        screen_height: window.innerHeight
    };

    // Send to Supabase
    sendToSupabase('tctc_user_behavior', trackingData);
}

// Determine page type
function determinePageType(path) {
    let pageType = 'other';

    if (path.includes('index.html') || path === '/' || path.endsWith('/')) {
        pageType = 'home';
    } else if (path.includes('-quiz.html')) {
        pageType = 'quiz';
    } else if (path.includes('-variant-')) {
        pageType = 'quiz_result';
    } else if (path.includes('universal-application-form.html')) {
        pageType = 'application';
    } else if (path.includes('niches/')) {
        pageType = 'niche';
    }

    return pageType;
}

// Send data to Supabase
function sendToSupabase(table, data) {
    // Use the shared Supabase client if available
    const supabaseClient = window.tctcSupabaseClient;

    console.log('Attempting to send data to Supabase table:', table);
    console.log('Data to send:', data);
    console.log('Supabase client available:', !!supabaseClient);

    if (!supabaseClient) {
        console.error('Shared Supabase client not available');
        return;
    }

    try {
        console.log(`Sending ${data.event_type} to Supabase table ${table}...`);
        supabaseClient.from(table).insert([data])
            .then(result => {
                if (result.error) {
                    console.error(`Error tracking ${data.event_type}:`, result.error);
                    console.error('Error details:', result.error.message);
                    console.error('Error code:', result.error.code);
                } else {
                    console.log(`${data.event_type} tracked successfully:`, result.data);
                }
            })
            .catch(error => {
                console.error(`Error tracking ${data.event_type}:`, error);
                console.error('Error message:', error.message);
                console.error('Error stack:', error.stack);
            });
    } catch (e) {
        console.error(`Exception during ${data.event_type} tracking:`, e);
        console.error('Exception message:', e.message);
        console.error('Exception stack:', e.stack);
    }
}
