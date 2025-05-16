// Dashboard Main JavaScript
console.log('Dashboard.js loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing dashboard...');
    console.log('Supabase client available:', !!window.tctcSupabaseClient);
    console.log('Dashboard API available:', !!window.dashboardAPI);

    // Check if the dashboard API is available
    if (!window.dashboardAPI) {
        console.error('Dashboard API not available. Make sure supabase-client.js is loaded correctly.');
        document.getElementById('total-visitors').textContent = 'API Error';
        document.getElementById('quiz-starts').textContent = 'API Error';
        document.getElementById('quiz-completions').textContent = 'API Error';
        document.getElementById('applications').textContent = 'API Error';
        return;
    }

    // Initialize dashboard
    initializeDashboard();

    // Set up navigation
    setupNavigation();

    // Set up date range picker
    setupDateRangePicker();

    // Set up filters
    setupFilters();
});

// Initialize dashboard with default view
async function initializeDashboard() {
    console.log('Initializing dashboard...');
    const dateRange = document.getElementById('date-range').value;
    console.log('Date range:', dateRange);
    console.log('Supabase client available in initializeDashboard:', !!window.tctcSupabaseClient);
    console.log('Dashboard API available in initializeDashboard:', !!window.dashboardAPI);

    // Check if dashboardAPI is available
    if (!window.dashboardAPI) {
        console.error('Dashboard API is not available. Make sure dashboard-api.js is loaded correctly.');
        document.getElementById('total-visitors').textContent = 'Error';
        document.getElementById('quiz-starts').textContent = 'Error';
        document.getElementById('quiz-completions').textContent = 'Error';
        document.getElementById('applications').textContent = 'Error';
        return;
    }

    try {
        // Show loading state
        document.getElementById('total-visitors').textContent = 'Loading...';
        document.getElementById('quiz-starts').textContent = 'Loading...';
        document.getElementById('quiz-completions').textContent = 'Loading...';
        document.getElementById('applications').textContent = 'Loading...';

        console.log('Starting to fetch data...');

        // Fetch data
        let pageViews = [];
        let quizStarts = [];
        let quizCompletions = [];
        let applications = [];
        let quizSubmissions = [];

        try {
            console.log('About to fetch page views...');
            pageViews = await window.dashboardAPI.fetchPageViews(dateRange);
            console.log(`Fetched ${pageViews.length} page views`);
            if (pageViews.length > 0) {
                console.log('First page view:', pageViews[0]);
            }
        } catch (e) {
            console.error('Error fetching page views:', e);
            console.error('Error stack:', e.stack);
            pageViews = [];
        }

        try {
            console.log('About to fetch quiz starts...');
            quizStarts = await window.dashboardAPI.fetchQuizStarts(dateRange);
            console.log(`Fetched ${quizStarts.length} quiz starts`);
            if (quizStarts.length > 0) {
                console.log('First quiz start:', quizStarts[0]);
            }
        } catch (e) {
            console.error('Error fetching quiz starts:', e);
            console.error('Error stack:', e.stack);
            quizStarts = [];
        }

        try {
            console.log('About to fetch quiz completions...');
            quizCompletions = await window.dashboardAPI.fetchQuizCompletions(dateRange);
            console.log(`Fetched ${quizCompletions.length} quiz completions`);
            if (quizCompletions.length > 0) {
                console.log('First quiz completion:', quizCompletions[0]);
            }
        } catch (e) {
            console.error('Error fetching quiz completions:', e);
            console.error('Error stack:', e.stack);
            quizCompletions = [];
        }

        try {
            console.log('About to fetch quiz submissions...');
            quizSubmissions = await window.dashboardAPI.fetchQuizSubmissions(dateRange);
            console.log(`Fetched ${quizSubmissions.length} quiz submissions`);
            if (quizSubmissions.length > 0) {
                console.log('First quiz submission:', quizSubmissions[0]);
            }
        } catch (e) {
            console.error('Error fetching quiz submissions:', e);
            console.error('Error stack:', e.stack);
            quizSubmissions = [];
        }

        // Update metrics - with direct DOM manipulation for debugging
        try {
            if (Array.isArray(pageViews)) {
                const count = countUniqueUsers(pageViews);
                console.log(`Updating total-visitors element with count: ${count}`);
                const element = document.getElementById('total-visitors');
                if (element) {
                    element.textContent = count;
                } else {
                    console.error('Element with ID "total-visitors" not found');
                }
            } else {
                console.error('Cannot update total-visitors element: pageViews is not an array');
                const element = document.getElementById('total-visitors');
                if (element) {
                    element.textContent = '0';
                }
            }
        } catch (e) {
            console.error('Error updating total-visitors:', e);
        }

        try {
            if (Array.isArray(quizStarts)) {
                const count = countUniqueUsers(quizStarts);
                console.log(`Updating quiz-starts element with count: ${count}`);
                const element = document.getElementById('quiz-starts');
                if (element) {
                    element.textContent = count;
                } else {
                    console.error('Element with ID "quiz-starts" not found');
                }
            } else {
                console.error('Cannot update quiz-starts element: quizStarts is not an array');
                const element = document.getElementById('quiz-starts');
                if (element) {
                    element.textContent = '0';
                }
            }
        } catch (e) {
            console.error('Error updating quiz-starts:', e);
        }

        try {
            if (Array.isArray(quizCompletions)) {
                const count = countUniqueUsers(quizCompletions);
                console.log(`Updating quiz-completions element with count: ${count}`);
                const element = document.getElementById('quiz-completions');
                if (element) {
                    element.textContent = count;
                } else {
                    console.error('Element with ID "quiz-completions" not found');
                }
            } else {
                console.error('Cannot update quiz-completions element: quizCompletions is not an array');
                const element = document.getElementById('quiz-completions');
                if (element) {
                    element.textContent = '0';
                }
            }
        } catch (e) {
            console.error('Error updating quiz-completions:', e);
        }

        try {
            if (Array.isArray(quizSubmissions)) {
                const count = quizSubmissions.length;
                console.log(`Updating applications element with count: ${count}`);
                const element = document.getElementById('applications');
                if (element) {
                    element.textContent = count;
                } else {
                    console.error('Element with ID "applications" not found');
                }
            } else {
                console.error('Cannot update applications element: quizSubmissions is not an array');
                const element = document.getElementById('applications');
                if (element) {
                    element.textContent = '0';
                }
            }
        } catch (e) {
            console.error('Error updating applications:', e);
        }

        // Render charts
        try {
            renderTrafficSourceChart(pageViews);
        } catch (e) {
            console.error('Error rendering traffic source chart:', e);
        }

        try {
            renderNicheConversionChart(quizStarts, quizCompletions);
        } catch (e) {
            console.error('Error rendering niche conversion chart:', e);
        }

        // Combine all data for timeline chart
        try {
            const allData = [...pageViews, ...quizStarts, ...quizCompletions, ...applications];
            renderActivityTimelineChart(allData);
        } catch (e) {
            console.error('Error rendering activity timeline chart:', e);
        }

        // Fetch user journeys for flow analysis
        try {
            const journeys = await window.dashboardAPI.fetchUserJourneys(dateRange);
            renderDropoutChart(journeys);
        } catch (e) {
            console.error('Error rendering dropout chart:', e);
            renderDropoutChart({});
        }

    } catch (error) {
        console.error('Error initializing dashboard:', error);
        // Update metrics with zeros instead of showing an alert
        document.getElementById('total-visitors').textContent = '0';
        document.getElementById('quiz-starts').textContent = '0';
        document.getElementById('quiz-completions').textContent = '0';
        document.getElementById('applications').textContent = '0';
    }
}

// Count unique users in data
function countUniqueUsers(data) {
    const uniqueUsers = new Set();
    data.forEach(item => {
        // Create a composite key from user_first_name, user_last_name, and user_email
        const userId = `${item.user_first_name || ''}_${item.user_last_name || ''}_${item.user_email || ''}`.toLowerCase();
        if (userId && userId !== '__') {
            uniqueUsers.add(userId);
        }
    });
    return uniqueUsers.size;
}

// Set up navigation between dashboard sections
function setupNavigation() {
    console.log('Setting up navigation...');
    const navLinks = document.querySelectorAll('nav a');
    const sections = document.querySelectorAll('.dashboard-section');

    console.log(`Found ${navLinks.length} navigation links and ${sections.length} dashboard sections`);

    // Log the navigation links and sections for debugging
    navLinks.forEach((link, index) => {
        console.log(`Nav link ${index}: href="${link.getAttribute('href')}", text="${link.textContent}"`);
    });

    sections.forEach((section, index) => {
        console.log(`Section ${index}: id="${section.id}", class="${section.className}"`);
    });

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log(`Navigation link clicked: ${this.getAttribute('href')}`);
            e.preventDefault();

            // Get target section ID from href
            const targetId = this.getAttribute('href').substring(1);
            console.log(`Target section ID: ${targetId}`);

            // Hide all sections
            sections.forEach(section => {
                section.classList.remove('active');
                console.log(`Removed 'active' class from section ${section.id}`);
            });

            // Show target section if it exists
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                console.log(`Added 'active' class to section ${targetId}`);
            } else {
                console.warn(`Section with ID "${targetId}" not found in the DOM.`);
                // Show the overview section as fallback
                const overviewSection = document.getElementById('overview');
                if (overviewSection) {
                    overviewSection.classList.add('active');
                    console.log(`Added 'active' class to overview section as fallback`);
                } else {
                    console.error(`Overview section not found in the DOM.`);
                }
            }

            // Update active nav link
            navLinks.forEach(navLink => {
                navLink.classList.remove('active');
                console.log(`Removed 'active' class from nav link ${navLink.getAttribute('href')}`);
            });
            this.classList.add('active');
            console.log(`Added 'active' class to clicked nav link ${this.getAttribute('href')}`);
        });
    });
}

// Set up date range picker
function setupDateRangePicker() {
    const dateRangePicker = document.getElementById('date-range');

    dateRangePicker.addEventListener('change', function() {
        // Reload dashboard with new date range
        initializeDashboard();
    });
}

// Set up filters
function setupFilters() {
    const nicheFilter = document.getElementById('flow-niche-filter');
    const sourceFilter = document.getElementById('flow-source-filter');

    if (!nicheFilter || !sourceFilter) {
        console.warn('Filter elements not found in the DOM');
        return;
    }

    // Populate filters with dynamic options
    populateFilters();

    // Add event listeners
    nicheFilter.addEventListener('change', applyFilters);
    sourceFilter.addEventListener('change', applyFilters);
}

// Populate filters with options from data
async function populateFilters() {
    if (!window.dashboardAPI) {
        console.error('Dashboard API not available for populating filters');
        return;
    }

    try {
        // Fetch all data for the last 30 days
        let pageViews = [];
        try {
            pageViews = await window.dashboardAPI.fetchPageViews('30days');
        } catch (e) {
            console.error('Error fetching page views for filters:', e);
            pageViews = [];
        }

        // Extract unique niches
        const niches = new Set();
        pageViews.forEach(item => {
            if (item.niche && item.niche.trim() !== '') {
                niches.add(item.niche);
            }
        });

        // Extract unique sources
        const sources = new Set();
        pageViews.forEach(item => {
            if (item.original_source && item.original_source.trim() !== '') {
                sources.add(item.original_source);
            } else if (item.track_source && item.track_source.trim() !== '') {
                sources.add(item.track_source);
            }
        });

        // Populate niche filter
        const nicheFilter = document.getElementById('flow-niche-filter');
        if (nicheFilter) {
            niches.forEach(niche => {
                const option = document.createElement('option');
                option.value = niche;
                option.textContent = formatNicheName(niche);
                nicheFilter.appendChild(option);
            });
        }

        // Populate source filter
        const sourceFilter = document.getElementById('flow-source-filter');
        if (sourceFilter) {
            sources.forEach(source => {
                const option = document.createElement('option');
                option.value = source;
                option.textContent = formatSourceName(source);
                sourceFilter.appendChild(option);
            });
        }

    } catch (error) {
        console.error('Error populating filters:', error);
    }
}

// Format niche name for display
function formatNicheName(niche) {
    return niche
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Format source name for display
function formatSourceName(source) {
    return source.charAt(0).toUpperCase() + source.slice(1);
}

// Apply filters to user flow analysis
async function applyFilters() {
    if (!window.dashboardAPI) {
        console.error('Dashboard API not available for applying filters');
        return;
    }

    const dateRangeElement = document.getElementById('date-range');
    const nicheFilterElement = document.getElementById('flow-niche-filter');
    const sourceFilterElement = document.getElementById('flow-source-filter');

    if (!dateRangeElement || !nicheFilterElement || !sourceFilterElement) {
        console.error('Filter elements not found');
        return;
    }

    const dateRange = dateRangeElement.value;
    const nicheFilter = nicheFilterElement.value;
    const sourceFilter = sourceFilterElement.value;

    try {
        // Fetch filtered user journeys
        const filters = {
            niche: nicheFilter,
            source: sourceFilter
        };

        const journeys = await window.dashboardAPI.fetchUserJourneys(dateRange, filters);
        renderDropoutChart(journeys);

    } catch (error) {
        console.error('Error applying filters:', error);
        // Render empty chart to avoid showing stale data
        renderDropoutChart({});
    }
}
