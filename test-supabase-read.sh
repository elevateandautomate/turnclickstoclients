#!/bin/bash

# Supabase API details
SUPABASE_URL="https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64"

echo "Testing Supabase read access..."

# 1. Try to read from tctc_user_behavior table
echo "Reading from tctc_user_behavior table..."
curl -X GET "$SUPABASE_URL/rest/v1/tctc_user_behavior?select=*&limit=1" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"

echo -e "\n\n"

# 2. Try to read from tctc_quiz_submission table
echo "Reading from tctc_quiz_submission table..."
curl -X GET "$SUPABASE_URL/rest/v1/tctc_quiz_submission?select=*&limit=1" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"

echo -e "\n\n"

# 3. Try to read from tctc_quiz_redirections table
echo "Reading from tctc_quiz_redirections table..."
curl -X GET "$SUPABASE_URL/rest/v1/tctc_quiz_redirections?select=*&limit=1" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"

echo -e "\n\n"

echo "Test completed."
