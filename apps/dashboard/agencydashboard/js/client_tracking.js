const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client
const supabaseUrl = 'https://ehveemvdrzmnernsuuxv.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVodmVlbXZkcnptbmVybnN1dXh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0NjA2NTEsImV4cCI6MjA2MDAzNjY1MX0.A43KWW3G0kE_NgptszpaqC2-wFDGVPzGfcS7LFskV1E';
const supabase = createClient(supabaseUrl, supabaseKey);

// Function to fetch client tracking data
async function fetchClientTrackingData(filters = {}) {
    try {
        let query = supabase
            .from('client_metrics_enhanced')
            .select(`
                id,
                brand,
                subaccount_name,
                client_name,
                health_score,
                leads,
                confirmed_appointments,
                unconfirmed_appointments,
                appointment_showed,
                appointment_no_showed,
                lead_to_booked_percent,
                show_rate_percent,
                no_show_rate_percent,
                cpl,
                roas,
                ad_status,
                created_at,
                updated_at
            `);

        // Apply filters
        if (filters.brand && filters.brand !== 'all') {
            query = query.eq('brand', filters.brand);
        }
        if (filters.subaccount && filters.subaccount !== 'all') {
            query = query.eq('subaccount_name', filters.subaccount);
        }
        if (filters.dateRange) {
            const { startDate, endDate } = getDateFilterRange(filters.dateRange);
            if (startDate && endDate) {
                query = query.gte('created_at', startDate.toISOString())
                           .lte('created_at', endDate.toISOString());
            }
        }
        if (filters.adStatus && filters.adStatus !== 'all') {
            query = query.eq('ad_status', filters.adStatus);
        }
        if (filters.healthScore && filters.healthScore !== 'all') {
            // Convert health score ranges to numeric values
            let scoreRange;
            switch (filters.healthScore.toLowerCase()) {
                case 'excellent':
                    scoreRange = [60, 100];
                    break;
                case 'good':
                    scoreRange = [40, 59.99];
                    break;
                case 'warning':
                    scoreRange = [15, 39.99];
                    break;
                case 'critical':
                    scoreRange = [0, 14.99];
                    break;
                default:
                    scoreRange = null;
            }
            
            if (scoreRange) {
                query = query.gte('health_score', scoreRange[0])
                           .lte('health_score', scoreRange[1]);
            }
        }

        const { data, error } = await query;
        
        if (error) throw error;
        
        // Return data (all metrics are now pre-calculated in the database)
        return data;
    } catch (error) {
        console.error('Error fetching client tracking data:', error);
        throw error;
    }
}

// Helper function to get date range based on filter
function getDateFilterRange(dateRange) {
    const now = new Date();
    let startDate, endDate;

    switch (dateRange) {
        case 'today':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            endDate = now;
            break;
        case 'yesterday':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
            endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            break;
        case 'last7days':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
            endDate = now;
            break;
        case 'last30days':
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30);
            endDate = now;
            break;
        case 'alltime':
            startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
            endDate = now;
            break;
        default:
            startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            endDate = now;
    }

    return { startDate, endDate };
}

// Function to get unique brands
async function getUniqueBrands() {
    try {
        const { data, error } = await supabase
            .from('client_metrics_enhanced')
            .select('brand')
            .not('brand', 'is', null)
            .order('brand');
            
        if (error) throw error;
        
        return [...new Set(data.map(item => item.brand))];
    } catch (error) {
        console.error('Error fetching unique brands:', error);
        throw error;
    }
}

// Function to get unique subaccounts
async function getUniqueSubaccounts() {
    try {
        const { data, error } = await supabase
            .from('client_metrics_enhanced')
            .select('subaccount_name')
            .not('subaccount_name', 'is', null)
            .order('subaccount_name');
            
        if (error) throw error;
        
        return [...new Set(data.map(item => item.subaccount_name))];
    } catch (error) {
        console.error('Error fetching unique subaccounts:', error);
        throw error;
    }
}

// Function to get unique ad statuses
async function getUniqueAdStatuses() {
    try {
        const { data, error } = await supabase
            .from('client_metrics_enhanced')
            .select('ad_status')
            .not('ad_status', 'is', null)
            .order('ad_status');
            
        if (error) throw error;
        
        // If no ad statuses found, return default values
        if (!data.length) {
            return ['Active', 'Paused'];
        }
        
        return [...new Set(data.map(item => item.ad_status))];
    } catch (error) {
        console.error('Error fetching unique ad statuses:', error);
        throw error;
    }
}

// Function to get health score ranges
async function getHealthScores() {
    return [
        { label: 'Excellent', range: [60, 100] },
        { label: 'Good', range: [40, 59.99] },
        { label: 'Warning', range: [15, 39.99] },
        { label: 'Critical', range: [0, 14.99] }
    ];
}

module.exports = {
    fetchClientTrackingData,
    getUniqueBrands,
    getUniqueSubaccounts,
    getUniqueAdStatuses,
    getHealthScores
}; 