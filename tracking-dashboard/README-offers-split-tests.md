# Offers & Split Tests Dashboard

This module adds functionality for creating and managing offers and split tests in the TurnClicksToClients tracking dashboard. It includes machine learning-based automatic split test creation based on user behavior data.

## Features

- **Offer Management**
  - Create and edit offers with headlines, descriptions, and CTAs
  - Target specific audience segments
  - View offer performance metrics
  - Filter and search offers

- **Split Test Management**
  - Create A/B tests with multiple variants
  - Set traffic distribution between variants
  - Track test performance in real-time
  - View detailed test results with charts
  - Pause, resume, and end tests

- **Machine Learning Integration**
  - Automatic generation of split test recommendations based on user behavior
  - AI-powered insights for optimizing offers
  - Audience segmentation based on quiz and application data
  - Confidence scoring for recommendations

## Setup Instructions

### 1. Database Setup

Run the SQL migration file to create the necessary tables:

```bash
cd supabase
supabase db push
```

Or manually run the SQL file:

```sql
-- From supabase/migrations/20250701000000_create_offers_and_tests_tables.sql
```

### 2. Supabase Configuration

Update the Supabase configuration in `tracking-dashboard/js/offers-split-tests.js`:

```javascript
// Supabase configuration
const SUPABASE_URL = 'https://your-supabase-url.supabase.co';
const SUPABASE_KEY = 'your-supabase-anon-key';
```

### 3. Include the JavaScript File

Make sure the JavaScript file is included in your dashboard HTML:

```html
<script src="js/offers-split-tests.js"></script>
```

### 4. Initialize the Module

Add the initialization code to your dashboard's main JavaScript:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the Offers & Split Tests tab when it's selected
    const offersTab = document.getElementById('offers-tab');
    if (offersTab) {
        offersTab.addEventListener('click', function() {
            initializeOffersAndTests();
        });
    }
});
```

## Usage Guide

### Creating an Offer

1. Navigate to the "Offers & Split Tests" tab
2. Click the "Create Offer" button
3. Fill in the offer details:
   - Name: A descriptive name for internal reference
   - Niche: Select the target niche
   - Headline: The main headline for the offer
   - Description: Detailed description of the offer
   - CTA Text: Call-to-action button text
   - Target Audience: Select the audience segment
4. Click "Create Offer"

### Creating a Split Test

1. Navigate to the "Offers & Split Tests" tab
2. Click the "Create Split Test" button
3. Fill in the test details:
   - Name: A descriptive name for the test
   - Niche: Select the target niche
   - Target Audience: Select the audience segment
   - Duration: Number of days the test should run
4. Configure variants:
   - Variant A is the control by default
   - Select an offer for each variant
   - Adjust traffic weights (must sum to 100%)
   - Add more variants if needed (up to 4)
5. Click "Create Test"

### Viewing Test Results

1. Navigate to the "Offers & Split Tests" tab
2. Find the test in the table
3. Click the "View" button
4. The results modal will show:
   - Test details and status
   - Performance metrics for each variant
   - Comparison to the control variant
   - Daily performance chart

### Using Machine Learning Features

The system automatically analyzes user behavior data and generates insights and recommendations:

1. **AI Recommendations Notification**: When new insights are available, a notification will appear
2. **View Insights**: Click to see detailed recommendations
3. **Apply Recommendations**: You can apply individual recommendations or all at once
4. **Auto-Generated Tests**: The system may suggest creating tests automatically based on user behavior patterns

## Machine Learning Data Flow

1. User quiz and application data is collected in Supabase
2. The ML system analyzes this data to identify patterns and opportunities
3. Insights are generated and stored in the `tctc_ml_insights` table
4. The dashboard checks for new insights and displays notifications
5. When insights are applied, they create offers or tests with the `is_auto_generated` flag set to true

## Troubleshooting

- **No offers showing**: Check that you have created offers and they are active
- **Test not starting**: Ensure you have selected valid offers for each variant
- **Charts not loading**: Make sure Chart.js is properly included in your project
- **Supabase errors**: Verify your Supabase URL and API key are correct

## Future Enhancements

- Enhanced audience targeting based on more detailed user behavior
- Multi-variate testing (testing more than one variable at once)
- Automatic winner selection and implementation
- Integration with email marketing systems
- Personalized offer recommendations for individual users
