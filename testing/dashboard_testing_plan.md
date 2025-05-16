# Dashboard and Tracking Testing Plan

This document outlines the comprehensive testing plan for both the user flow tracking and dashboard functionality before launch.

## 1. Supabase Integration Testing

### 1.1 Supabase Connection
- [ ] Verify Supabase client is correctly initialized
- [ ] Test connection to Supabase from main website
- [ ] Test connection to Supabase from dashboard
- [ ] Verify correct API keys are being used

### 1.2 Database Schema
- [ ] Verify `tctc_user_flow` table exists and has correct columns
- [ ] Verify `tctc_user_behavior` table exists and has correct columns
- [ ] Verify `tctc_quiz_submission` table exists and has correct columns
- [ ] Verify any other required tables exist

## 2. User Flow Tracking Testing

### 2.1 Page View Tracking
- [ ] Test page view tracking on homepage
- [ ] Test page view tracking on quiz pages
- [ ] Test page view tracking on quiz results pages
- [ ] Test page view tracking on application pages
- [ ] Verify all required parameters are captured (niche, bucket, variant, split, etc.)

### 2.2 Quiz Interaction Tracking
- [ ] Test quiz start tracking
- [ ] Test quiz completion tracking
- [ ] Test quiz score tracking
- [ ] Verify quiz parameters are correctly passed to results pages

### 2.3 Application Tracking
- [ ] Test application click tracking
- [ ] Test application form submission tracking
- [ ] Verify application parameters are correctly captured

### 2.4 Parameter Persistence
- [ ] Verify user parameters persist throughout the entire journey
- [ ] Test with various UTM parameters to ensure tracking source is maintained
- [ ] Verify first name, last name, business name are passed correctly

## 3. Split Testing Functionality

### 3.1 Split Test Distribution
- [ ] Verify users are evenly distributed across split test variations
- [ ] Test each niche to ensure split test variations are working
- [ ] Verify URL parameters for split tests are correctly passed

### 3.2 Split Test Content
- [ ] Verify each split test variation displays the correct content
- [ ] Verify all three variations (split1, split2, split3) are accessible
- [ ] Verify split test variations maintain consistent styling and functionality

## 4. Dashboard Functionality Testing

### 4.1 Dashboard Access and Loading
- [ ] Verify dashboard loads correctly
- [ ] Test dashboard navigation between sections
- [ ] Verify date range picker functionality
- [ ] Test dashboard with different browsers

### 4.2 Dashboard Data Display
- [ ] Verify metrics are correctly displayed (total visitors, quiz starts, etc.)
- [ ] Test charts with real data
- [ ] Verify user flow visualization is accurate
- [ ] Test filtering functionality

### 4.3 Dashboard API
- [ ] Test all dashboard API endpoints
- [ ] Verify data fetching from Supabase
- [ ] Test error handling for API calls
- [ ] Verify data processing functions

## 5. End-to-End Testing Scenarios

### 5.1 Complete User Journeys
- [ ] Test complete journey: Homepage → Quiz → Results → Application → Dashboard Tracking
- [ ] Test journey with chat widget interaction
- [ ] Test journey with different quiz scores and buckets
- [ ] Verify all tracking events appear in the dashboard

### 5.2 Dashboard Data Accuracy
- [ ] Create test data with known values
- [ ] Verify dashboard displays the correct metrics for test data
- [ ] Test dashboard with different date ranges
- [ ] Verify filtering works correctly

## 6. Testing Scripts

### 6.1 User Flow Testing Script
```javascript
// Test script for user flow tracking
async function testUserFlow() {
  // 1. Visit homepage and verify page view tracking
  await visitPage('index.html');
  await verifyTracking('page_view', { page_path: '/index.html' });
  
  // 2. Start quiz and verify tracking
  await clickElement('#start-quiz-button');
  await verifyTracking('quiz_started', { niche: 'cosmetic-dentistry' });
  
  // 3. Complete quiz and verify tracking
  await completeQuiz();
  await verifyTracking('quiz_completed', { score: '75' });
  
  // 4. View results page and verify tracking
  await verifyTracking('page_view', { 
    page_path: '/quiz-applications/cosmetic-dentistry/foundation/foundation-variant-a-solution.html',
    page_bucket: 'foundation',
    page_variant: 'a-solution'
  });
  
  // 5. Click application button and verify tracking
  await clickElement('#apply-button');
  await verifyTracking('application_click', { 
    destination_url: '/universal-application-form.html'
  });
  
  // 6. Submit application and verify tracking
  await fillApplicationForm();
  await clickElement('#submit-application');
  await verifyTracking('application_submit', {});
  
  console.log('User flow test completed successfully!');
}
```

### 6.2 Dashboard Testing Script
```javascript
// Test script for dashboard functionality
async function testDashboard() {
  // 1. Load dashboard and verify connection
  await loadDashboard();
  await verifySupabaseConnection();
  
  // 2. Test navigation
  await clickElement('nav a[href="#user-flow"]');
  await verifyElementVisible('#user-flow.active');
  
  // 3. Test date range picker
  await selectOption('#date-range', '30days');
  await verifyDataLoaded();
  
  // 4. Test filters
  await selectOption('#flow-niche-filter', 'cosmetic-dentistry');
  await verifyFilteredData('cosmetic-dentistry');
  
  // 5. Verify charts
  await verifyChartRendered('#traffic-source-chart');
  await verifyChartRendered('#niche-conversion-chart');
  await verifyChartRendered('#activity-timeline-chart');
  await verifyChartRendered('#dropout-chart');
  
  console.log('Dashboard test completed successfully!');
}
```

## 7. Pre-Launch Checklist

### 7.1 Final Verification
- [ ] Verify all tracking events are being recorded correctly in Supabase
- [ ] Verify all split test variations are accessible and working
- [ ] Verify all user flows work as expected
- [ ] Verify dashboard displays correct data

### 7.2 Backup and Recovery
- [ ] Create backup of current database
- [ ] Document rollback procedure in case of issues
- [ ] Test rollback procedure

### 7.3 Launch Preparation
- [ ] Set up monitoring alerts for tracking failures
- [ ] Prepare launch announcement
- [ ] Schedule post-launch verification checks
