/**
 * Dashboard Integration Test Script
 * 
 * This script tests the integration between the tracking system and the dashboard.
 * It creates test events in Supabase and verifies they appear in the dashboard.
 */

// Configuration
const SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64';
const DASHBOARD_URL = 'http://localhost/tracking-dashboard/index.html';

// Test data
const TEST_USER_ID = `test_user_${Date.now()}`;
const TEST_EVENTS = [
  {
    user_id: TEST_USER_ID,
    action_type: 'page_view',
    page_path: '/index.html',
    page_bucket: '',
    page_variant: '',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '',
    full_url: 'http://localhost/index.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'page_view',
    page_path: '/niches/cosmetic-dentistry-quiz.html',
    page_bucket: '',
    page_variant: '',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '',
    full_url: 'http://localhost/niches/cosmetic-dentistry-quiz.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'quiz_start',
    page_path: '/niches/cosmetic-dentistry-quiz.html',
    page_bucket: '',
    page_variant: '',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '',
    full_url: 'http://localhost/niches/cosmetic-dentistry-quiz.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'quiz_completion',
    page_path: '/niches/cosmetic-dentistry-quiz.html',
    page_bucket: 'foundation',
    page_variant: '',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '75',
    full_url: 'http://localhost/niches/cosmetic-dentistry-quiz.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'page_view',
    page_path: '/quiz-applications/cosmetic-dentistry/foundation/foundation-variant-a-solution.html',
    page_bucket: 'foundation',
    page_variant: 'a-solution',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '75',
    full_url: 'http://localhost/quiz-applications/cosmetic-dentistry/foundation/foundation-variant-a-solution.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'application_click',
    page_path: '/quiz-applications/cosmetic-dentistry/foundation/foundation-variant-a-solution.html',
    page_bucket: 'foundation',
    page_variant: 'a-solution',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '75',
    destination_url: 'http://localhost/universal-application-form.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'page_view',
    page_path: '/universal-application-form.html',
    page_bucket: 'foundation',
    page_variant: 'a-solution',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '75',
    full_url: 'http://localhost/universal-application-form.html',
    timestamp: new Date().toISOString()
  },
  {
    user_id: TEST_USER_ID,
    action_type: 'application_submit',
    page_path: '/universal-application-form.html',
    page_bucket: 'foundation',
    page_variant: 'a-solution',
    page_split: '0',
    user_first_name: 'Test',
    user_last_name: 'User',
    user_business_name: 'Test Business',
    original_source: 'test',
    track_source: 'dashboard_test',
    quiz_score: '75',
    full_url: 'http://localhost/universal-application-form.html',
    timestamp: new Date().toISOString()
  }
];

// Initialize Supabase client
let supabase;

// Main test function
async function runDashboardIntegrationTest() {
  console.log('Starting dashboard integration test...');
  
  try {
    // Initialize Supabase client
    supabase = await initializeSupabase();
    
    // Create test events
    await createTestEvents();
    
    // Open dashboard in new tab
    window.open(DASHBOARD_URL, '_blank');
    
    console.log('Test completed. Please check the dashboard to verify the test events appear.');
    console.log('Look for events with user_id:', TEST_USER_ID);
    
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Initialize Supabase client
async function initializeSupabase() {
  console.log('Initializing Supabase client...');
  
  if (typeof supabase === 'undefined') {
    throw new Error('Supabase client not available. Make sure to include the Supabase script.');
  }
  
  const client = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  
  // Test connection
  const { data, error } = await client.from('tctc_user_flow').select('*').limit(1);
  
  if (error) {
    throw new Error(`Supabase connection failed: ${error.message}`);
  }
  
  console.log('Supabase connection successful.');
  return client;
}

// Create test events in Supabase
async function createTestEvents() {
  console.log('Creating test events...');
  
  for (const event of TEST_EVENTS) {
    const { data, error } = await supabase.from('tctc_user_flow').insert([event]);
    
    if (error) {
      console.error(`Error creating event ${event.action_type}:`, error);
    } else {
      console.log(`Created ${event.action_type} event.`);
    }
    
    // Add a small delay between events
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  console.log('All test events created.');
}

// Clean up test events
async function cleanupTestEvents() {
  console.log('Cleaning up test events...');
  
  const { data, error } = await supabase
    .from('tctc_user_flow')
    .delete()
    .eq('user_id', TEST_USER_ID);
  
  if (error) {
    console.error('Error cleaning up test events:', error);
  } else {
    console.log(`Cleaned up ${data.length} test events.`);
  }
}

// Run the test when the script is loaded
document.addEventListener('DOMContentLoaded', function() {
  const runTestButton = document.createElement('button');
  runTestButton.textContent = 'Run Dashboard Integration Test';
  runTestButton.style.padding = '10px 20px';
  runTestButton.style.backgroundColor = '#3b82f6';
  runTestButton.style.color = 'white';
  runTestButton.style.border = 'none';
  runTestButton.style.borderRadius = '5px';
  runTestButton.style.cursor = 'pointer';
  runTestButton.style.margin = '20px';
  
  runTestButton.addEventListener('click', runDashboardIntegrationTest);
  
  const cleanupButton = document.createElement('button');
  cleanupButton.textContent = 'Clean Up Test Events';
  cleanupButton.style.padding = '10px 20px';
  cleanupButton.style.backgroundColor = '#ef4444';
  cleanupButton.style.color = 'white';
  cleanupButton.style.border = 'none';
  cleanupButton.style.borderRadius = '5px';
  cleanupButton.style.cursor = 'pointer';
  cleanupButton.style.margin = '20px';
  
  cleanupButton.addEventListener('click', cleanupTestEvents);
  
  document.body.appendChild(runTestButton);
  document.body.appendChild(cleanupButton);
});
