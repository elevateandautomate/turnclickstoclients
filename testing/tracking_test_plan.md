# Tracking and User Flow Testing Plan

This document outlines the comprehensive testing plan to ensure all tracking, user flow, and split testing functionality is working correctly before launch.

## 1. Supabase Tracking Verification

### 1.1 Quiz Page Tracking
- [ ] Verify quiz page views are tracked in Supabase
- [ ] Verify quiz start events are tracked
- [ ] Verify quiz completion events are tracked
- [ ] Verify quiz scores are correctly recorded

### 1.2 Quiz Results Page Tracking
- [ ] Verify quiz results page views are tracked
- [ ] Verify variant (a/b/c) is correctly recorded
- [ ] Verify bucket (foundation/growth/etc.) is correctly recorded
- [ ] Verify split test variation (1/2/3) is correctly recorded
- [ ] Verify user parameters are passed correctly (name, business name, etc.)

### 1.3 Application Page Tracking
- [ ] Verify application page views are tracked
- [ ] Verify application starts are tracked
- [ ] Verify application completions are tracked
- [ ] Verify all user data is correctly passed from quiz results to application

### 1.4 CTA Click Tracking
- [ ] Verify "Apply Now" button clicks are tracked
- [ ] Verify chat widget interactions are tracked
- [ ] Verify other CTA elements are tracked

## 2. Split Testing Functionality

### 2.1 Split Test Distribution
- [ ] Verify users are evenly distributed across split test variations
- [ ] Test each niche to ensure split test variations are working
- [ ] Verify URL parameters for split tests are correctly passed

### 2.2 Split Test Content
- [ ] Verify each split test variation displays the correct content
- [ ] Verify all three variations (split1, split2, split3) are accessible
- [ ] Verify split test variations maintain consistent styling and functionality

## 3. User Flow Testing

### 3.1 Quiz Flow
- [ ] Test complete quiz flow for each niche
- [ ] Verify correct scoring and bucketing logic
- [ ] Verify users are directed to the correct results page based on score

### 3.2 Results to Application Flow
- [ ] Verify links from results pages to application form work correctly
- [ ] Verify all parameters are passed correctly in the URL
- [ ] Test application form submission
- [ ] Verify successful application redirects to the correct page

### 3.3 Error Handling
- [ ] Test form validation on quiz and application pages
- [ ] Verify error messages are displayed appropriately
- [ ] Test recovery from validation errors

## 4. Cross-Browser and Device Testing

### 4.1 Browser Compatibility
- [ ] Test on Chrome
- [ ] Test on Firefox
- [ ] Test on Safari
- [ ] Test on Edge

### 4.2 Device Compatibility
- [ ] Test on desktop (various screen sizes)
- [ ] Test on tablet (iOS and Android)
- [ ] Test on mobile (iOS and Android)
- [ ] Verify responsive design works correctly

## 5. Tracking Dashboard Verification

### 5.1 Data Visualization
- [ ] Verify tracking dashboard displays correct data
- [ ] Test filtering and sorting functionality
- [ ] Verify split test performance metrics are calculated correctly

### 5.2 Reporting
- [ ] Test report generation
- [ ] Verify data export functionality
- [ ] Verify real-time updates to dashboard

## 6. End-to-End Testing Scenarios

### 6.1 Complete User Journeys
- [ ] Test complete journey: Homepage → Quiz → Results → Application → Confirmation
- [ ] Test journey with chat widget interaction
- [ ] Test journey with different quiz scores and buckets

### 6.2 Parameter Persistence
- [ ] Verify user parameters persist throughout the entire journey
- [ ] Test with various UTM parameters to ensure tracking source is maintained

## 7. Testing Script

Below is a script to test the tracking functionality by simulating user journeys:

```bash
# Test script for tracking verification
# Run this for each niche to verify tracking

# 1. Access the quiz page with tracking parameters
curl -I "https://yourdomain.com/niches/cosmetic-dentistry-quiz.html?source=test&track_source=testing"

# 2. Submit quiz and verify results page tracking
# (Manual step - complete quiz and check Supabase for tracking event)

# 3. Verify application page tracking
# (Manual step - click Apply Now and check Supabase for tracking event)

# 4. Verify split test distribution
# Run multiple times and count distribution of split variations
for i in {1..30}; do
  curl -I "https://yourdomain.com/quiz-applications/cosmetic-dentistry/foundation/foundation-variant-a-solution.html" | grep -i location
done
```

## 8. Pre-Launch Checklist

### 8.1 Final Verification
- [ ] Verify all tracking events are being recorded correctly in Supabase
- [ ] Verify all split test variations are accessible and working
- [ ] Verify all user flows work as expected
- [ ] Verify dashboard displays correct data

### 8.2 Backup and Recovery
- [ ] Create backup of current database
- [ ] Document rollback procedure in case of issues
- [ ] Test rollback procedure

### 8.3 Launch Preparation
- [ ] Set up monitoring alerts for tracking failures
- [ ] Prepare launch announcement
- [ ] Schedule post-launch verification checks
