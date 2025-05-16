#!/bin/bash

# Supabase API details
SUPABASE_URL="https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64"

# Generate random IDs (since we're on Windows and don't have /proc/sys/kernel/random/uuid)
USER_ID="test-user-$(date +%s)"
SESSION_ID="test-session-$(date +%s)-$RANDOM"
FLOW_HASH="test-flow-$(date +%s)-$RANDOM"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

echo "Simulating quiz completion with user_id: $USER_ID"
echo "Session ID: $SESSION_ID"
echo "Flow Hash: $FLOW_HASH"
echo "Timestamp: $TIMESTAMP"

# 1. First, simulate a page view event
echo "Sending page view event..."
curl -X POST "$SUPABASE_URL/rest/v1/tctc_user_behavior" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"event_type\": \"page_view\",
    \"event_data\": {
      \"page_url\": \"http://localhost:8000/niches/child-care-centers-quiz.html\",
      \"page_title\": \"Child Care Center Growth Quiz | TurnClicksToClients\",
      \"time_on_page_start\": \"$TIMESTAMP\"
    },
    \"session_id\": \"$SESSION_ID\",
    \"user_id\": \"$USER_ID\",
    \"flow_hash\": \"$FLOW_HASH\",
    \"page_type\": \"quiz\",
    \"niche\": \"child-care-centers\",
    \"traffic_source\": \"test-script\",
    \"timestamp\": \"$TIMESTAMP\",
    \"user_agent\": \"Test Script\",
    \"screen_width\": 1920,
    \"screen_height\": 1080
  }"

sleep 1

# 2. Simulate a quiz start event
echo "Sending quiz start event..."
curl -X POST "$SUPABASE_URL/rest/v1/tctc_user_behavior" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"event_type\": \"quiz_started\",
    \"event_data\": {
      \"action\": \"start_quiz\",
      \"quiz_type\": \"Child Care Center Growth Quiz\"
    },
    \"session_id\": \"$SESSION_ID\",
    \"user_id\": \"$USER_ID\",
    \"flow_hash\": \"$FLOW_HASH\",
    \"page_type\": \"quiz\",
    \"niche\": \"child-care-centers\",
    \"traffic_source\": \"test-script\",
    \"timestamp\": \"$TIMESTAMP\",
    \"user_agent\": \"Test Script\",
    \"screen_width\": 1920,
    \"screen_height\": 1080
  }"

sleep 1

# 3. Simulate a quiz completion event
echo "Sending quiz completion event..."
curl -X POST "$SUPABASE_URL/rest/v1/tctc_user_behavior" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"event_type\": \"quiz_completed\",
    \"event_data\": {
      \"action\": \"submit_lead_form\",
      \"quiz_type\": \"Child Care Center Growth Quiz\"
    },
    \"session_id\": \"$SESSION_ID\",
    \"user_id\": \"$USER_ID\",
    \"flow_hash\": \"$FLOW_HASH\",
    \"page_type\": \"quiz\",
    \"niche\": \"child-care-centers\",
    \"traffic_source\": \"test-script\",
    \"timestamp\": \"$TIMESTAMP\",
    \"user_agent\": \"Test Script\",
    \"screen_width\": 1920,
    \"screen_height\": 1080
  }"

sleep 1

# 4. Simulate a quiz submission to the tctc_quiz_submission table
echo "Sending quiz submission..."
curl -X POST "$SUPABASE_URL/rest/v1/tctc_quiz_submission" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"first_name\": \"Test\",
    \"last_name\": \"User\",
    \"business_name\": \"Test Child Care Center\",
    \"email\": \"test@example.com\",
    \"phone\": \"555-123-4567\",
    \"growth_stifler_response\": \"Manual processes for enrollment and parent communication\",
    \"total_score\": 15,
    \"niche\": \"child-care-centers\",
    \"primary_outcome_hint\": \"practice\",
    \"source\": \"test-script\",
    \"submitted_at\": \"$TIMESTAMP\",
    \"quiz_answers\": [
      {
        \"question\": \"How would you describe your current enrollment inquiry and tour booking process?\",
        \"answer\": \"Partially digitized but still involves significant manual follow-up.\",
        \"score\": 2
      },
      {
        \"question\": \"How effectively are you communicating your unique programs and curriculum to prospective parents?\",
        \"answer\": \"We actively discuss it during tours and have informative materials available.\",
        \"score\": 3
      },
      {
        \"question\": \"How robust is your parent communication system for enrolled families?\",
        \"answer\": \"We use a dedicated app or platform, but could leverage it more effectively.\",
        \"score\": 3
      },
      {
        \"question\": \"How would you rate your staff satisfaction and retention?\",
        \"answer\": \"Good; most of our staff are happy and stay with us for a reasonable period.\",
        \"score\": 3
      },
      {
        \"question\": \"What is your child care center's primary growth goal for the next 1-3 years?\",
        \"answer\": \"Expanding our current facility or adding new programs/services.\",
        \"score\": 3
      },
      {
        \"question\": \"Growth stifler question\",
        \"answer\": \"Manual processes for enrollment and parent communication\",
        \"score\": null
      }
    ]
  }"

sleep 1

# 5. Simulate a redirection to the tctc_quiz_redirections table
echo "Sending quiz redirection..."
curl -X POST "$SUPABASE_URL/rest/v1/tctc_quiz_redirections" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"user_first_name\": \"Test\",
    \"user_last_name\": \"User\",
    \"user_business_name\": \"Test Child Care Center\",
    \"quiz_score\": 15,
    \"outcome_bucket\": \"practice\",
    \"awareness_variant\": \"a-solution\",
    \"redirect_url\": \"../quiz-applications/child-care/practice/practice-variant-a-solution.html\",
    \"source\": \"test-script\",
    \"redirected_at\": \"$TIMESTAMP\"
  }"

echo "Test completed. Check the dashboard to see if the data appears."
