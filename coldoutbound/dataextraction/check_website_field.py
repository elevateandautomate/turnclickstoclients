"""
Script to check the website field in the failed form submissions
"""

from supabase import create_client
import json

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"

def check_website_field():
    """Check the website field in the failed form submissions"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"Successfully initialized Supabase client.")
        
        # Get records with contact_form_submitted = false
        response = supabase.table(TABLE_NAME).select("*").eq("contact_form_submitted", False).limit(10).execute()
        
        if response.data:
            print(f"Found {len(response.data)} records with contact_form_submitted=false")
            
            for i, record in enumerate(response.data):
                print(f"\nRecord {i+1}:")
                
                # Check all fields that might contain website information
                website_fields = [
                    "listing_website", "website_url", "website", "url", 
                    "listing_url", "business_website", "practice_website"
                ]
                
                print("Website-related fields:")
                for field in website_fields:
                    if field in record:
                        print(f"  {field}: {record.get(field)}")
                
                # Print all fields and values for the record
                print("\nAll fields in the record:")
                for key, value in record.items():
                    print(f"  {key}: {value}")
                
                # Check if there's a field that looks like a website URL
                for key, value in record.items():
                    if isinstance(value, str) and ('http' in value.lower() or 'www.' in value.lower() or '.com' in value.lower()):
                        print(f"\nPossible website field found: {key}: {value}")
        else:
            print("No records found with contact_form_submitted=false")
            
    except Exception as e:
        print(f"Error checking website field: {e}")

if __name__ == "__main__":
    check_website_field()
