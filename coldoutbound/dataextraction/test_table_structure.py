#!/usr/bin/env python3
"""
Script to test the structure of the contact_bot_brain table.
"""

import os
import sys
import json
import requests

def main():
    """Main function to test the structure of the contact_bot_brain table"""
    # Get Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url:
        supabase_url = input("Enter your Supabase URL: ")
    
    if not supabase_key:
        supabase_key = input("Enter your Supabase API key: ")
    
    # Test the table structure using direct REST API
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Get the table structure
        print("Getting table structure...")
        response = requests.get(
            f"{supabase_url}/rest/v1/",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Successfully connected to Supabase")
            
            # Check if the contact_bot_brain table exists
            print("\nChecking if contact_bot_brain table exists...")
            response = requests.get(
                f"{supabase_url}/rest/v1/contact_bot_brain?select=id&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ contact_bot_brain table exists")
                
                # Check if the field_attributes column exists
                print("\nChecking if field_attributes column exists...")
                response = requests.get(
                    f"{supabase_url}/rest/v1/contact_bot_brain?select=field_attributes&limit=1",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("✅ field_attributes column exists")
                    
                    # Try to insert a test record
                    print("\nInserting a test record...")
                    test_data = {
                        "model_name": "form_field_classifier",
                        "field_attributes": {
                            "id": "test-email",
                            "name": "your-email",
                            "class": "form-control",
                            "type": "email",
                            "placeholder": "Your Email Address",
                            "tag_name": "input"
                        },
                        "field_type": "email",
                        "source": "https://test-structure.com/contact",
                        "success": True
                    }
                    
                    response = requests.post(
                        f"{supabase_url}/rest/v1/contact_bot_brain",
                        headers={**headers, "Prefer": "return=representation"},
                        json=test_data
                    )
                    
                    if response.status_code == 201:
                        print("✅ Successfully inserted test record")
                        print("Response:")
                        print(json.dumps(response.json(), indent=2))
                        
                        # Get the inserted record
                        record_id = response.json()[0]["id"]
                        print(f"\nGetting the inserted record (ID: {record_id})...")
                        
                        response = requests.get(
                            f"{supabase_url}/rest/v1/contact_bot_brain?id=eq.{record_id}&select=*",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            print("✅ Successfully retrieved the inserted record")
                            print("Record:")
                            print(json.dumps(response.json(), indent=2))
                        else:
                            print(f"❌ Failed to retrieve the inserted record. Status code: {response.status_code}")
                            print("Response:")
                            print(response.text)
                    else:
                        print(f"❌ Failed to insert test record. Status code: {response.status_code}")
                        print("Response:")
                        print(response.text)
                else:
                    print(f"❌ field_attributes column does not exist. Status code: {response.status_code}")
                    print("Response:")
                    print(response.text)
            else:
                print(f"❌ contact_bot_brain table does not exist. Status code: {response.status_code}")
                print("Response:")
                print(response.text)
        else:
            print(f"❌ Failed to connect to Supabase. Status code: {response.status_code}")
            print("Response:")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
