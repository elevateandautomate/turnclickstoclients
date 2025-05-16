#!/usr/bin/env python3
"""
Script to check the data enrichment functionality in the production environment.
This script will:
1. Connect to Supabase
2. Check if the contact_enrichment table exists
3. Display the most recent enriched contacts
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("Error: supabase-py package not installed. Please install it with 'pip install supabase'.")
    sys.exit(1)

def main():
    """Main function to check data enrichment functionality"""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Supabase credentials not found in environment variables. Please check your .env file.")
        sys.exit(1)
    
    # Connect to Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully.")
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        sys.exit(1)
    
    # Check if the contact_enrichment table exists
    try:
        result = supabase.table("contact_enrichment").select("count", count="exact").execute()
        count = result.count
        print(f"✅ contact_enrichment table exists with {count} records.")
    except Exception as e:
        print(f"❌ Error checking contact_enrichment table: {e}")
        print("The contact_enrichment table might not exist.")
        sys.exit(1)
    
    # Get the most recent enriched contacts
    try:
        result = supabase.table("contact_enrichment").select("*").order("created_at", desc=True).limit(5).execute()
        
        if result.data and len(result.data) > 0:
            print(f"\nMost recent {len(result.data)} enriched contacts:")
            
            for i, enrichment in enumerate(result.data):
                print(f"\n--- Enriched Contact {i+1} ---")
                print(f"Contact ID: {enrichment.get('contact_id')}")
                print(f"Created at: {enrichment.get('created_at')}")
                
                # Display emails
                if "emails" in enrichment and enrichment["emails"]:
                    print(f"Emails: {', '.join(enrichment['emails'])}")
                
                # Display phone numbers
                if "phone_numbers" in enrichment and enrichment["phone_numbers"]:
                    print(f"Phone numbers: {', '.join(enrichment['phone_numbers'])}")
                
                # Display social media links
                if "social_media" in enrichment and enrichment["social_media"]:
                    social_media = enrichment["social_media"]
                    if isinstance(social_media, str):
                        try:
                            social_media = json.loads(social_media)
                        except:
                            pass
                    
                    print("Social media links:")
                    for platform, links in social_media.items():
                        if links:
                            print(f"  - {platform.capitalize()}: {', '.join(links)}")
                
                # Display additional data
                if "additional_data" in enrichment and enrichment["additional_data"]:
                    additional_data = enrichment["additional_data"]
                    if isinstance(additional_data, str):
                        try:
                            additional_data = json.loads(additional_data)
                        except:
                            pass
                    
                    if additional_data:
                        print("Additional data:")
                        for key, value in additional_data.items():
                            print(f"  - {key}: {value}")
                
                # Try to get the contact details from the core_data table
                try:
                    contact_result = supabase.table("core_data").select("listing_name, website_url_profile").eq("id", enrichment.get('contact_id')).execute()
                    if contact_result.data and len(contact_result.data) > 0:
                        contact = contact_result.data[0]
                        print(f"Contact name: {contact.get('listing_name')}")
                        print(f"Website: {contact.get('website_url_profile')}")
                except Exception as contact_error:
                    print(f"Could not retrieve contact details: {contact_error}")
        else:
            print("\nNo enriched contacts found.")
    except Exception as e:
        print(f"❌ Error retrieving enriched contacts: {e}")

if __name__ == "__main__":
    main()
