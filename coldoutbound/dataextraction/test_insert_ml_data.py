#!/usr/bin/env python3
"""
Script to test inserting data into the contact_bot_brain table.
"""

import os
import sys
import json
import requests
from datetime import datetime

def main():
    """Main function to test inserting data into the contact_bot_brain table"""
    # Get Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url:
        supabase_url = input("Enter your Supabase URL: ")
    
    if not supabase_key:
        supabase_key = input("Enter your Supabase API key: ")
    
    # Test inserting data using direct REST API
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Create test data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_data = {
            "model_name": "form_field_classifier",
            "field_attributes": json.dumps({
                "id": f"test-email-{timestamp}",
                "name": "your-email",
                "class": "form-control",
                "type": "email",
                "placeholder": "Your Email Address",
                "tag_name": "input"
            }),
            "field_type": "email",
            "source": "https://test-direct-api.com/contact",
            "success": True
        }
        
        print("Inserting test data:")
        print(json.dumps(test_data, indent=2))
        
        # Insert the data
        response = requests.post(
            f"{supabase_url}/rest/v1/contact_bot_brain",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 201:
            print("✅ Successfully inserted test data")
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed to insert test data. Status code: {response.status_code}")
            print("Response:")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
