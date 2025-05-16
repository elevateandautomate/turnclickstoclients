#!/bin/bash

# Supabase API details
SUPABASE_URL="https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64"

echo "Directly querying Supabase API..."

# Query tctc_quiz_submission table
echo "Querying tctc_quiz_submission table..."
curl -X GET "$SUPABASE_URL/rest/v1/tctc_quiz_submission?select=id,first_name,last_name,business_name,niche,total_score,primary_outcome_hint,source,submitted_at" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"

echo -e "\n\nQuery completed."
