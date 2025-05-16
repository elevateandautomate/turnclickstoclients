// Tabbed Dashboard JavaScript
console.log('Tabbed dashboard.js loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing tabbed dashboard...');
    
    // Initialize tabs
    initTabs();
    
    // Initialize dashboard data
    initializeDashboard();
    
    // Set up date range picker
    setupDateRangePicker();
});

// Initialize tab functionality
function initTabs() {
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log(`Found ${tabLinks.length} tab links and ${tabContents.length} tab contents`);
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function() {
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
}

// Update metrics with error state
function updateMetricsWithError() {
    document.getElementById('total-visitors').textContent = 'Error';
    document.getElementById('quiz-starts').textContent = 'Error';
    document.getElementById('quiz-completions').textContent = 'Error';
    document.getElementById('applications').textContent = 'Error';
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
