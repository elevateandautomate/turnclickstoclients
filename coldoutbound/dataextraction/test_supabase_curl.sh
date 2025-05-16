#!/bin/bash
# Test script to verify Supabase connection and data storage using curl

# Check if jq is installed (for pretty-printing JSON)
if ! command -v jq &> /dev/null; then
    echo "Warning: jq is not installed. JSON output will not be formatted."
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Get Supabase credentials
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "Error: Supabase credentials not found in environment variables. Please check your .env file."
    exit 1
fi

echo "Using Supabase URL: $SUPABASE_URL"

# Table name
TABLE_NAME="contact_bot_brain"

# Test 1: Check if the table exists
echo "Test 1: Checking if table '$TABLE_NAME' exists..."
RESPONSE=$(curl -s -X GET \
    "$SUPABASE_URL/rest/v1/$TABLE_NAME?select=count" \
    -H "apikey: $SUPABASE_KEY" \
    -H "Authorization: Bearer $SUPABASE_KEY")

if [[ $RESPONSE == *"does not exist"* ]]; then
    echo "❌ Table '$TABLE_NAME' does not exist."

    # Ask if we should create the table
    echo -n "Do you want to create the table? (y/n): "
    read CREATE_TABLE

    if [[ $CREATE_TABLE == "y" || $CREATE_TABLE == "Y" ]]; then
        echo "Creating table '$TABLE_NAME'..."

        # Create the table using the SQL API
        SQL_QUERY="CREATE TABLE IF NOT EXISTS public.$TABLE_NAME (id UUID PRIMARY KEY DEFAULT uuid_generate_v4(), field_attributes JSONB NOT NULL, field_type TEXT NOT NULL, source TEXT, success BOOLEAN DEFAULT true, created_at TIMESTAMP WITH TIME ZONE DEFAULT now());"

        RESPONSE=$(curl -s -X POST \
            "$SUPABASE_URL/rest/v1/rpc/exec_sql" \
            -H "apikey: $SUPABASE_KEY" \
            -H "Authorization: Bearer $SUPABASE_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"query\": \"$SQL_QUERY\"}")

        if [[ $RESPONSE == *"error"* ]]; then
            echo "❌ Error creating table: $RESPONSE"
            echo "Please create the table manually with the following columns:"
            echo "- id: UUID PRIMARY KEY DEFAULT uuid_generate_v4()"
            echo "- field_attributes: JSONB NOT NULL"
            echo "- field_type: TEXT NOT NULL"
            echo "- source: TEXT"
            echo "- success: BOOLEAN DEFAULT true"
            echo "- created_at: TIMESTAMP WITH TIME ZONE DEFAULT now()"
            exit 1
        else
            echo "✅ Table created successfully."
        fi
    else
        echo "Skipping table creation."
        exit 1
    fi
else
    echo "✅ Table '$TABLE_NAME' exists."
fi

# Test 2: Insert a test record
echo -e "\nTest 2: Inserting a test record..."

# Create a timestamp for the test record
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create the test record
TEST_RECORD="{\"field_attributes\": {\"id\": \"test-email-$TIMESTAMP\", \"name\": \"email\", \"class\": \"form-control\", \"type\": \"email\", \"placeholder\": \"Enter your email\", \"tag_name\": \"input\"}, \"field_type\": \"email\", \"source\": \"https://test-website.com/contact\", \"success\": true}"

# Insert the record
RESPONSE=$(curl -s -X POST \
    "$SUPABASE_URL/rest/v1/$TABLE_NAME" \
    -H "apikey: $SUPABASE_KEY" \
    -H "Authorization: Bearer $SUPABASE_KEY" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=representation" \
    -d "$TEST_RECORD")

if [[ $RESPONSE == *"error"* ]]; then
    echo "❌ Error inserting test record: $RESPONSE"
    exit 1
else
    echo "✅ Test record inserted successfully."

    # Pretty-print the response if jq is available
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Response:"
        echo "$RESPONSE" | jq .
    else
        echo "Response: $RESPONSE"
    fi
fi

# Test 3: Retrieve the records
echo -e "\nTest 3: Retrieving records..."

RESPONSE=$(curl -s -X GET \
    "$SUPABASE_URL/rest/v1/$TABLE_NAME?select=*&order=created_at.desc&limit=5" \
    -H "apikey: $SUPABASE_KEY" \
    -H "Authorization: Bearer $SUPABASE_KEY")

if [[ $RESPONSE == *"error"* ]]; then
    echo "❌ Error retrieving records: $RESPONSE"
    exit 1
else
    echo "✅ Records retrieved successfully."

    # Pretty-print the response if jq is available
    if [ "$JQ_AVAILABLE" = true ]; then
        echo "Records:"
        echo "$RESPONSE" | jq .
    else
        echo "Records: $RESPONSE"
    fi
fi

echo -e "\nAll tests completed successfully!"
