# Pre-Launch Testing Suite

This directory contains a comprehensive testing suite to ensure the website is ready for launch. The tests focus on tracking functionality, user flow, split testing, and dashboard integration.

## Test Files

- `tracking_test_plan.md`: Detailed plan for testing tracking and user flow
- `dashboard_testing_plan.md`: Detailed plan for testing dashboard functionality
- `pre_launch_checklist.md`: Comprehensive checklist for launch readiness
- `test_tracking.py`: Python script to test tracking functionality
- `test_split_variations.py`: Python script to test split test variations
- `test_supabase_tracking.py`: Python script to test Supabase tracking integration
- `test_dashboard_integration.js`: JavaScript to test dashboard integration
- `test_split_distribution.js`: JavaScript to test split test distribution
- `dashboard_integration_test.html`: HTML page to run dashboard integration tests
- `split_test_distribution.html`: HTML page to run split test distribution tests
- `run_all_tests.bat`: Batch file to run all tests

## Running the Tests

### Option 1: Run All Tests

1. Open a command prompt in this directory
2. Run `run_all_tests.bat`
3. This will run all Python tests and open browser-based tests in new tabs

### Option 2: Run Individual Tests

#### Python Tests

1. Open a command prompt in this directory
2. Run one of the following commands:
   - `python test_tracking.py` - Tests tracking functionality
   - `python test_split_variations.py` - Tests split test variations
   - `python test_supabase_tracking.py` - Tests Supabase tracking integration

#### Browser-Based Tests

1. Open one of the following HTML files in your browser:
   - `dashboard_integration_test.html` - Tests dashboard integration
   - `split_test_distribution.html` - Tests split test distribution

## Test Plans and Checklists

Before running the tests, review the following documents:

- `tracking_test_plan.md` - Detailed plan for testing tracking and user flow
- `dashboard_testing_plan.md` - Detailed plan for testing dashboard functionality
- `pre_launch_checklist.md` - Comprehensive checklist for launch readiness

## Interpreting Test Results

### Python Tests

The Python tests will output results to the console. Look for:

- ✅ Success messages
- ❌ Error messages
- ⚠️ Warning messages

### Browser-Based Tests

The browser-based tests will display results in the browser. Look for:

- Charts showing split test distribution
- Log messages indicating success or failure
- Verification that test events appear in the dashboard

## Dashboard Testing

To test the dashboard:

1. Run the dashboard integration test
2. Open the dashboard in a new tab
3. Verify that test events appear in the dashboard
4. Test filtering and date range functionality
5. Verify charts and metrics are displayed correctly

## Split Test Testing

To test split test functionality:

1. Run the split test distribution test
2. Verify that users are evenly distributed across split test variations
3. Check that split test content is displayed correctly
4. Verify that split test parameters are correctly passed through the user journey

## User Flow Testing

To test the complete user flow:

1. Run the tracking test
2. Follow the complete user journey: Homepage → Quiz → Results → Application
3. Verify all tracking events are recorded in Supabase
4. Check that parameters are correctly passed between pages

## Pre-Launch Checklist

Before launch, go through the pre-launch checklist:

1. Open `pre_launch_checklist.md`
2. Check off each item as you verify it
3. Address any issues found during testing
4. Create backups before launch
5. Set up monitoring for post-launch verification
