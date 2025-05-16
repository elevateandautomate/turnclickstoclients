// Generate test data for the dashboard
// This script will generate test data for the tctc_user_flow table

// Supabase configuration
const SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64';

// Initialize Supabase client
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Generate random data
const niches = [
    'cosmetic-dentists',
    'hearing-aid-audiology-clinics',
    'pmu-artists',
    'child-care-centers',
    'non-surgical-body-contouring',
    'weight-loss-clinics',
    'high-end-chiropractors'
];

const sources = [
    'organic',
    'facebook',
    'google',
    'direct',
    'referral'
];

const actionTypes = [
    'page_view',
    'quiz_started',
    'quiz_completed',
    'form_submitted'
];

const buckets = [
    'foundation',
    'growth',
    'scaling',
    'clients',
    'patients',
    'practice',
    'operations',
    'enrollment',
    'future',
    'studio',
    'referrals'
];

const variants = [
    'a-solution',
    'b-problem',
    'c-most-aware'
];

// Generate random user data
function generateRandomUser() {
    const firstNames = ['John', 'Jane', 'Bob', 'Alice', 'David', 'Sarah', 'Michael', 'Emily', 'Robert', 'Jessica'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor'];
    const businessNames = ['Dental Care', 'Hearing Solutions', 'Beauty Studio', 'Child Care Center', 'Body Contouring', 'Weight Loss Clinic', 'Chiropractic Care'];
    
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const businessName = businessNames[Math.floor(Math.random() * businessNames.length)] + ' ' + lastName;
    const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`;
    
    return {
        firstName,
        lastName,
        businessName,
        email
    };
}

// Generate random events for a user
async function generateUserEvents(user, count = 10) {
    const events = [];
    const niche = niches[Math.floor(Math.random() * niches.length)];
    const source = sources[Math.floor(Math.random() * sources.length)];
    
    // Generate page view events
    for (let i = 0; i < count; i++) {
        const actionType = actionTypes[Math.floor(Math.random() * actionTypes.length)];
        const bucket = buckets[Math.floor(Math.random() * buckets.length)];
        const variant = variants[Math.floor(Math.random() * variants.length)];
        
        const event = {
            user_first_name: user.firstName,
            user_last_name: user.lastName,
            user_business_name: user.businessName,
            user_email: user.email,
            action_type: actionType,
            niche: niche,
            page_bucket: bucket,
            page_variant: variant,
            original_source: source,
            track_source: source,
            timestamp: new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000)).toISOString()
        };
        
        events.push(event);
    }
    
    // Insert events into Supabase
    const { data, error } = await supabase.from('tctc_user_flow').insert(events);
    
    if (error) {
        console.error('Error inserting events:', error);
        return false;
    }
    
    console.log(`Inserted ${events.length} events for user ${user.firstName} ${user.lastName}`);
    return true;
}

// Generate test data
async function generateTestData(userCount = 10, eventsPerUser = 10) {
    console.log(`Generating test data for ${userCount} users with ${eventsPerUser} events each...`);
    
    for (let i = 0; i < userCount; i++) {
        const user = generateRandomUser();
        await generateUserEvents(user, eventsPerUser);
    }
    
    console.log('Test data generation complete!');
}

// Run the script
generateTestData(10, 10)
    .then(() => {
        console.log('Script completed successfully');
        process.exit(0);
    })
    .catch(error => {
        console.error('Script failed:', error);
        process.exit(1);
    });
