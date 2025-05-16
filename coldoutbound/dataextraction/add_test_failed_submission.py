"""
Script to add a test record with a failed form submission
"""

from supabase import create_client
from datetime import datetime

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"

def add_test_record():
    """Add a test record with a failed form submission"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")

        # Create test record
        test_record = {
            "listing_name": f"Test Failed Contact {datetime.now().strftime('%H:%M:%S')}",
            "listing_business_name": "Test Failed Company",
            "website_url_profile": "https://testfailed.com",  # Use the correct column name
            "listing_website": "https://testfailed-backup.com",  # Add a backup website field
            "niche": "dentist",
            "contact_form_submitted": False,
            "contact_form_submitted_message": "This is a test error message for tracking",
            "contact_form_submitted_timestamp": datetime.now().isoformat()
        }

        # Insert the record
        response = supabase.table(TABLE_NAME).insert(test_record).execute()

        if response.data:
            print(f"Successfully added test record with ID: {response.data[0].get('id')}")
            return True
        else:
            print("Failed to add test record")
            return False
    except Exception as e:
        print(f"Error adding test record: {e}")
        return False

if __name__ == "__main__":
    add_test_record()
