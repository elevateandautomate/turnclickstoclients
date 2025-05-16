// Supabase Client for Dashboard
// Check if we have a shared client from the parent page
let supabaseClient;

if (window.tctcSupabaseClient) {
    // Use the shared client
    supabaseClient = window.tctcSupabaseClient;
    console.log('Dashboard: Using shared Supabase client');
} else {
    // Initialize a new client if shared client is not available
    const SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co';
    const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64';
    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    console.log('Dashboard: Created new Supabase client');
}

// Date range utilities
function getDateRange(rangeType) {
    const now = new Date();
    const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);
    let startDate;

    switch (rangeType) {
        case 'today':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
            break;
        case 'yesterday':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 0, 0, 0);
            endDate.setDate(endDate.getDate() - 1);
            break;
        case '7days':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6, 0, 0, 0);
            break;
        case '30days':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 29, 0, 0, 0);
            break;
        default:
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6, 0, 0, 0);
    }

    return {
        startDate: startDate.toISOString(),
        endDate: endDate.toISOString()
    };
}

// Data fetching functions
async function fetchPageViews(dateRange) {
    const { startDate, endDate } = getDateRange(dateRange);

    try {
        const { data, error } = await supabaseClient
            .from('tctc_user_behavior')
            .select('*')
            .eq('event_type', 'page_view')
            .gte('timestamp', startDate)
            .lte('timestamp', endDate);

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error fetching page views:', error);
        return [];
    }
}

async function fetchQuizStarts(dateRange) {
    const { startDate, endDate } = getDateRange(dateRange);

    try {
        const { data, error } = await supabaseClient
            .from('tctc_user_behavior')
            .select('*')
            .eq('event_type', 'quiz_started')
            .gte('timestamp', startDate)
            .lte('timestamp', endDate);

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error fetching quiz starts:', error);
        return [];
    }
}

async function fetchQuizCompletions(dateRange) {
    const { startDate, endDate } = getDateRange(dateRange);

    try {
        const { data, error } = await supabaseClient
            .from('tctc_user_behavior')
            .select('*')
            .eq('event_type', 'quiz_completed')
            .gte('timestamp', startDate)
            .lte('timestamp', endDate);

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error fetching quiz completions:', error);
        return [];
    }
}

async function fetchApplications(dateRange) {
    const { startDate, endDate } = getDateRange(dateRange);

    try {
        const { data, error } = await supabaseClient
            .from('tctc_user_behavior')
            .select('*')
            .eq('event_type', 'form_submitted')
            .eq('page_type', 'application')
            .gte('timestamp', startDate)
            .lte('timestamp', endDate);

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error fetching applications:', error);
        return [];
    }
}

async function fetchUserJourneys(dateRange, filters = {}) {
    const { startDate, endDate } = getDateRange(dateRange);

    try {
        let query = supabaseClient
            .from('tctc_user_behavior')
            .select('*')
            .gte('timestamp', startDate)
            .lte('timestamp', endDate)
            .order('timestamp', { ascending: true });

        // Apply filters
        if (filters.niche && filters.niche !== 'all') {
            query = query.eq('niche', filters.niche);
        }

        if (filters.source && filters.source !== 'all') {
            query = query.eq('traffic_source', filters.source);
        }

        if (filters.userId) {
            query = query.eq('user_id', filters.userId);
        }

        const { data, error } = await query;

        if (error) throw error;

        // Group by user_id
        const journeys = {};
        data.forEach(event => {
            if (!journeys[event.user_id]) {
                journeys[event.user_id] = [];
            }
            journeys[event.user_id].push(event);
        });

        return journeys;
    } catch (error) {
        console.error('Error fetching user journeys:', error);
        return {};
    }
}

async function fetchQuizAnalytics(dateRange, filters = {}) {
    const { startDate, endDate } = getDateRange(dateRange);

    try {
        // Fetch quiz submissions
        let query = supabaseClient
            .from('tctc_quiz_submission')
            .select('*')
            .gte('submitted_at', startDate)
            .lte('submitted_at', endDate);

        // Apply filters
        if (filters.niche && filters.niche !== 'all') {
            query = query.eq('niche', filters.niche);
        }

        if (filters.source && filters.source !== 'all') {
            query = query.eq('source', filters.source);
        }

        const { data, error } = await query;

        if (error) throw error;
        return data;
    } catch (error) {
        console.error('Error fetching quiz analytics:', error);
        return [];
    }
}

// Export functions
window.dashboardAPI = {
    fetchPageViews,
    fetchQuizStarts,
    fetchQuizCompletions,
    fetchApplications,
    fetchUserJourneys,
    fetchQuizAnalytics,
    getDateRange
};
