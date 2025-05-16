// Sidebar Dashboard JavaScript
console.log('Sidebar dashboard.js loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing sidebar dashboard...');
    
    // Initialize tabs
    initTabs();
    
    // Initialize dashboard data
    initializeDashboard();
    
    // Set up date range picker
    setupDateRangePicker();
});

// Initialize tab functionality
function initTabs() {
    const tabLinks = document.querySelectorAll('.sidebar-nav-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log(`Found ${tabLinks.length} tab links and ${tabContents.length} tab contents`);
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.getAttribute('data-tab');
            console.log(`Tab clicked: ${tabId}`);
            
            // Remove active class from all tabs and contents
            tabLinks.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to current tab and content
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// Initialize dashboard with default view
async function initializeDashboard() {
    console.log('Initializing dashboard data...');
    
    if (!window.dashboardAPI) {
        console.error('Dashboard API not available. Make sure dashboard-api.js is loaded correctly.');
        updateMetricsWithError();
        return;
    }
    
    const dateRange = document.getElementById('date-range').value;
    console.log('Date range:', dateRange);
    
    try {
        // Show loading state
        updateMetricsWithLoading();
        
        // Fetch data
        let pageViews = [];
        let quizStarts = [];
        let quizCompletions = [];
        let quizSubmissions = [];
        
        try {
            pageViews = await window.dashboardAPI.fetchPageViews(dateRange);
            console.log(`Fetched ${pageViews.length} page views`);
        } catch (e) {
            console.error('Error fetching page views:', e);
            pageViews = [];
        }
        
        try {
            quizStarts = await window.dashboardAPI.fetchQuizStarts(dateRange);
            console.log(`Fetched ${quizStarts.length} quiz starts`);
        } catch (e) {
            console.error('Error fetching quiz starts:', e);
            quizStarts = [];
        }
        
        try {
            quizCompletions = await window.dashboardAPI.fetchQuizCompletions(dateRange);
            console.log(`Fetched ${quizCompletions.length} quiz completions`);
        } catch (e) {
            console.error('Error fetching quiz completions:', e);
            quizCompletions = [];
        }
        
        try {
            quizSubmissions = await window.dashboardAPI.fetchQuizSubmissions(dateRange);
            console.log(`Fetched ${quizSubmissions.length} quiz submissions`);
        } catch (e) {
            console.error('Error fetching quiz submissions:', e);
            quizSubmissions = [];
        }
        
        // Update metrics
        updateMetrics(pageViews, quizStarts, quizCompletions, quizSubmissions);
        
        // Update pipeline
        updatePipeline(pageViews, quizStarts, quizCompletions, quizSubmissions);
        
        // Render charts
        try {
            if (typeof renderTrafficSourceChart === 'function') {
                renderTrafficSourceChart(pageViews);
            } else {
                console.error('renderTrafficSourceChart function not available');
            }
        } catch (e) {
            console.error('Error rendering traffic source chart:', e);
        }
        
        try {
            if (typeof renderNicheConversionChart === 'function') {
                renderNicheConversionChart(quizStarts, quizCompletions);
            } else {
                console.error('renderNicheConversionChart function not available');
            }
        } catch (e) {
            console.error('Error rendering niche conversion chart:', e);
        }
        
        try {
            if (typeof renderActivityTimelineChart === 'function') {
                const allData = [...pageViews, ...quizStarts, ...quizCompletions, ...quizSubmissions];
                renderActivityTimelineChart(allData);
            } else {
                console.error('renderActivityTimelineChart function not available');
            }
        } catch (e) {
            console.error('Error rendering activity timeline chart:', e);
        }
        
        try {
            if (typeof renderPipelineConversionChart === 'function') {
                renderPipelineConversionChart(pageViews, quizStarts, quizCompletions, quizSubmissions);
            } else {
                console.error('renderPipelineConversionChart function not available');
            }
        } catch (e) {
            console.error('Error rendering pipeline conversion chart:', e);
        }
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        updateMetricsWithError();
    }
}

// Update metrics with loading state
function updateMetricsWithLoading() {
    document.getElementById('total-visitors').textContent = 'Loading...';
    document.getElementById('quiz-starts').textContent = 'Loading...';
    document.getElementById('quiz-completions').textContent = 'Loading...';
    document.getElementById('applications').textContent = 'Loading...';
    
    // Pipeline metrics
    document.getElementById('pipeline-visitors').textContent = 'Loading...';
    document.getElementById('pipeline-quiz-takers').textContent = 'Loading...';
    document.getElementById('pipeline-applicants').textContent = 'Loading...';
    document.getElementById('pipeline-qualified').textContent = 'Loading...';
    document.getElementById('pipeline-customers').textContent = 'Loading...';
    
    document.getElementById('pipeline-quiz-percentage').textContent = 'Loading...';
    document.getElementById('pipeline-applicants-percentage').textContent = 'Loading...';
    document.getElementById('pipeline-qualified-percentage').textContent = 'Loading...';
    document.getElementById('pipeline-customers-percentage').textContent = 'Loading...';
}

// Update metrics with error state
function updateMetricsWithError() {
    document.getElementById('total-visitors').textContent = 'Error';
    document.getElementById('quiz-starts').textContent = 'Error';
    document.getElementById('quiz-completions').textContent = 'Error';
    document.getElementById('applications').textContent = 'Error';
    
    // Pipeline metrics
    document.getElementById('pipeline-visitors').textContent = 'Error';
    document.getElementById('pipeline-quiz-takers').textContent = 'Error';
    document.getElementById('pipeline-applicants').textContent = 'Error';
    document.getElementById('pipeline-qualified').textContent = 'Error';
    document.getElementById('pipeline-customers').textContent = 'Error';
    
    document.getElementById('pipeline-quiz-percentage').textContent = 'Error';
    document.getElementById('pipeline-applicants-percentage').textContent = 'Error';
    document.getElementById('pipeline-qualified-percentage').textContent = 'Error';
    document.getElementById('pipeline-customers-percentage').textContent = 'Error';
}

// Update metrics with data
function updateMetrics(pageViews, quizStarts, quizCompletions, quizSubmissions) {
    try {
        const totalVisitors = countUniqueUsers(pageViews);
        document.getElementById('total-visitors').textContent = totalVisitors;
    } catch (e) {
        console.error('Error updating total visitors:', e);
        document.getElementById('total-visitors').textContent = '0';
    }
    
    try {
        const quizStartsCount = countUniqueUsers(quizStarts);
        document.getElementById('quiz-starts').textContent = quizStartsCount;
    } catch (e) {
        console.error('Error updating quiz starts:', e);
        document.getElementById('quiz-starts').textContent = '0';
    }
    
    try {
        const quizCompletionsCount = countUniqueUsers(quizCompletions);
        document.getElementById('quiz-completions').textContent = quizCompletionsCount;
    } catch (e) {
        console.error('Error updating quiz completions:', e);
        document.getElementById('quiz-completions').textContent = '0';
    }
    
    try {
        const applicationsCount = quizSubmissions.length;
        document.getElementById('applications').textContent = applicationsCount;
    } catch (e) {
        console.error('Error updating applications:', e);
        document.getElementById('applications').textContent = '0';
    }
}

// Update pipeline metrics
function updatePipeline(pageViews, quizStarts, quizCompletions, quizSubmissions) {
    try {
        // For this example, we'll use some assumptions for qualified leads and customers
        // In a real implementation, you would fetch this data from your CRM or sales database
        const visitorCount = countUniqueUsers(pageViews);
        const quizTakerCount = countUniqueUsers(quizStarts);
        const applicantCount = countUniqueUsers(quizSubmissions);
        
        // Assuming 30% of applicants become qualified leads and 20% of qualified leads become customers
        const qualifiedLeadCount = Math.round(applicantCount * 0.3);
        const customerCount = Math.round(qualifiedLeadCount * 0.2);
        
        // Update counts
        document.getElementById('pipeline-visitors').textContent = visitorCount;
        document.getElementById('pipeline-quiz-takers').textContent = quizTakerCount;
        document.getElementById('pipeline-applicants').textContent = applicantCount;
        document.getElementById('pipeline-qualified').textContent = qualifiedLeadCount;
        document.getElementById('pipeline-customers').textContent = customerCount;
        
        // Update percentages
        if (visitorCount > 0) {
            document.getElementById('pipeline-quiz-percentage').textContent = 
                Math.round((quizTakerCount / visitorCount) * 100) + '%';
            document.getElementById('pipeline-applicants-percentage').textContent = 
                Math.round((applicantCount / visitorCount) * 100) + '%';
            document.getElementById('pipeline-qualified-percentage').textContent = 
                Math.round((qualifiedLeadCount / visitorCount) * 100) + '%';
            document.getElementById('pipeline-customers-percentage').textContent = 
                Math.round((customerCount / visitorCount) * 100) + '%';
        } else {
            document.getElementById('pipeline-quiz-percentage').textContent = '0%';
            document.getElementById('pipeline-applicants-percentage').textContent = '0%';
            document.getElementById('pipeline-qualified-percentage').textContent = '0%';
            document.getElementById('pipeline-customers-percentage').textContent = '0%';
        }
    } catch (e) {
        console.error('Error updating pipeline metrics:', e);
    }
}

// Count unique users in data
function countUniqueUsers(data) {
    if (!Array.isArray(data)) {
        console.error('Data is not an array:', data);
        return 0;
    }
    
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

// Set up date range picker
function setupDateRangePicker() {
    const dateRangePicker = document.getElementById('date-range');
    
    dateRangePicker.addEventListener('change', function() {
        // Reload dashboard with new date range
        initializeDashboard();
    });
}
