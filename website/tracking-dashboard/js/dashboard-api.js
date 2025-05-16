// Dashboard API for TurnClicksToClients
// This file provides the API for fetching data from Supabase for the dashboard

// Debug logging
console.log('Dashboard API loading...');

// Use the Supabase URL and key from the shared client
// These variables are already defined in supabase-client.js
// const SUPABASE_URL is already defined
// Using SUPABASE_ANON_KEY from supabase-client.js

// Function to fetch data from Supabase
async function fetchFromSupabase(table, query = '') {
    try {
        console.log(`Fetching from ${table}${query ? ' with query ' + query : ''}...`);

        // Use the Supabase client directly instead of fetch
        if (window.tctcSupabaseClient) {
            console.log(`Using Supabase client to fetch from ${table}...`);

            // Parse the query string to build the Supabase query
            let supabaseQuery = window.tctcSupabaseClient.from(table).select('*');

            // Parse the query parameters
            if (query) {
                const params = new URLSearchParams(query.substring(1));

                // Apply filters
                for (const [key, value] of params.entries()) {
                    if (key.startsWith('select')) continue;

                    if (key.includes('.')) {
                        const [field, operator] = key.split('.');
                        if (operator === 'eq') {
                            supabaseQuery = supabaseQuery.eq(field, value);
                            console.log(`Applied filter: ${field} = ${value}`);
                        }
                    }
                }
            }

            // Execute the query
            const { data, error } = await supabaseQuery;

            if (error) {
                console.error(`Supabase error fetching from ${table}:`, error);
                return [];
            }

            console.log(`Fetched ${data.length} items from ${table} using Supabase client`);
            console.log(`Sample data:`, data.slice(0, 2));

            return data;
        } else {
            // Fallback to fetch if Supabase client is not available
            console.log(`Falling back to fetch for ${table}...`);

            const response = await fetch(`${SUPABASE_URL}/rest/v1/${table}${query}`, {
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log(`Fetched ${data.length} items from ${table}`);
            console.log(`Sample data:`, data.slice(0, 2));

            return data;
        }
    } catch (error) {
        console.error(`Error fetching from ${table}: ${error.message}`);
        console.error(`Error stack:`, error.stack);
        return [];
    }
}

// Initialize the Dashboard API
window.dashboardAPI = {
    // Fetch page views from Supabase
    async fetchPageViews(dateRange) {
        try {
            return await fetchFromSupabase('tctc_user_flow', '?select=*&action_type=eq.page_view');
        } catch (error) {
            console.error('Error in fetchPageViews:', error);
            return [];
        }
    },

    // Fetch quiz starts from Supabase
    async fetchQuizStarts(dateRange) {
        try {
            return await fetchFromSupabase('tctc_user_flow', '?select=*&action_type=eq.quiz_started');
        } catch (error) {
            console.error('Error in fetchQuizStarts:', error);
            return [];
        }
    },

    // Fetch quiz completions from Supabase
    async fetchQuizCompletions(dateRange) {
        try {
            return await fetchFromSupabase('tctc_user_flow', '?select=*&action_type=eq.quiz_completed');
        } catch (error) {
            console.error('Error in fetchQuizCompletions:', error);
            return [];
        }
    },

    // Fetch applications from Supabase
    async fetchApplications(dateRange) {
        try {
            return await fetchFromSupabase('tctc_user_flow', '?select=*&action_type=eq.form_submitted');
        } catch (error) {
            console.error('Error in fetchApplications:', error);
            return [];
        }
    },

    // Fetch user journeys from Supabase
    async fetchUserJourneys(dateRange, filters = {}) {
        try {
            // Build the query
            let query = '?select=*';

            // Add niche filter if provided
            if (filters.niche && filters.niche !== 'all') {
                query += `&niche=eq.${filters.niche}`;
            }

            // Add source filter if provided
            if (filters.source && filters.source !== 'all') {
                query += `&original_source=eq.${filters.source}`;
            }

            // Order by timestamp
            query += '&order=timestamp.asc';

            // Fetch the data
            const data = await fetchFromSupabase('tctc_user_flow', query);

            // Group events by user_first_name and user_last_name (as a substitute for user_id)
            const journeys = {};
            data.forEach(event => {
                const userId = `${event.user_first_name || ''}_${event.user_last_name || ''}_${event.user_email || ''}`.toLowerCase();

                if (!userId || userId === '__') return;

                if (!journeys[userId]) {
                    journeys[userId] = [];
                }
                journeys[userId].push(event);
            });

            console.log(`Created ${Object.keys(journeys).length} user journeys`);
            return journeys;
        } catch (error) {
            console.error('Error in fetchUserJourneys:', error);
            return {};
        }
    },

    // Fetch quiz submissions from Supabase
    async fetchQuizSubmissions(dateRange) {
        try {
            // Use the tctc_user_flow table with action_type=form_submitted
            return await fetchFromSupabase('tctc_user_flow', '?select=*&action_type=eq.form_submitted');
        } catch (error) {
            console.error('Error in fetchQuizSubmissions:', error);
            return [];
        }
    }
};
