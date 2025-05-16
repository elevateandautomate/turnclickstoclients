// Shared Supabase Client for TurnClicksToClients
// This script initializes a single Supabase client instance that can be used by all other scripts
console.log('supabase-client.js loading...');

// Supabase configuration
const SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64';

console.log('Supabase URL:', SUPABASE_URL);
console.log('Supabase library available:', typeof supabase !== 'undefined');

// Initialize the Supabase client only if it doesn't already exist
if (typeof window.tctcSupabaseClient === 'undefined') {
    try {
        // Check if Supabase is available
        if (typeof supabase !== 'undefined' && supabase.createClient) {
            // Create the client
            window.tctcSupabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
            console.log('Supabase client initialized');

            // Test the client
            window.tctcSupabaseClient.from('tctc_user_behavior').select('*')
                .limit(1)
                .then(result => {
                    if (result.error) {
                        console.error('Error testing Supabase connection:', result.error);
                    } else {
                        console.log('Supabase connection test successful. Data:', result.data);
                    }
                })
                .catch(error => {
                    console.error('Exception during Supabase connection test:', error);
                });
        } else {
            console.error('Supabase library not available. Make sure to include the Supabase script before this one.');
        }
    } catch (error) {
        console.error('Error initializing Supabase client:', error);
    }
} else {
    // Client already exists, no need to log anything
}

// Export the client for use in other scripts
const getSupabaseClient = () => {
    return window.tctcSupabaseClient;
};
