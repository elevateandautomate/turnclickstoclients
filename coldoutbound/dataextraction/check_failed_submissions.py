"""
Script to check for failed form submissions in the database
"""

from supabase import create_client
import json
from datetime import datetime

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"

def format_timestamp(timestamp_str):
    """Format timestamp string to readable format"""
    if not timestamp_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%b %d, %Y %I:%M %p')
    except:
        return timestamp_str

def check_failed_submissions():
    """Check for failed form submissions in the database"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")
        
        # Query for records with contact_form_submitted = false
        print(f"\nChecking for records with contact_form_submitted = false in {TABLE_NAME}...")
        response_false = supabase.table(TABLE_NAME).select(
            "id,name,company,website_url,niche,contact_form_submitted,contact_form_submitted_message,contact_form_submitted_timestamp"
        ).eq("contact_form_submitted", False).order("contact_form_submitted_timestamp", desc=True).limit(10).execute()
        
        if response_false.data:
            print(f"Found {len(response_false.data)} records with contact_form_submitted = false:")
            for i, record in enumerate(response_false.data):
                print(f"\nRecord {i+1}:")
                print(f"  ID: {record.get('id')}")
                print(f"  Name: {record.get('name')}")
                print(f"  Company: {record.get('company')}")
                print(f"  Website: {record.get('website_url')}")
                print(f"  Niche: {record.get('niche')}")
                print(f"  Error Message: {record.get('contact_form_submitted_message')}")
                print(f"  Timestamp: {format_timestamp(record.get('contact_form_submitted_timestamp'))}")
        else:
            print("No records found with contact_form_submitted = false")
        
        # Query for records with contact_form_submitted = NULL
        print(f"\nChecking for records with contact_form_submitted = NULL in {TABLE_NAME}...")
        response_null = supabase.table(TABLE_NAME).select(
            "id,name,company,website_url,niche,contact_form_submitted,contact_form_submitted_message,contact_form_submitted_timestamp"
        ).is_("contact_form_submitted", None).order("contact_form_submitted_timestamp", desc=True).limit(10).execute()
        
        if response_null.data:
            print(f"Found {len(response_null.data)} records with contact_form_submitted = NULL:")
            for i, record in enumerate(response_null.data):
                print(f"\nRecord {i+1}:")
                print(f"  ID: {record.get('id')}")
                print(f"  Name: {record.get('name')}")
                print(f"  Company: {record.get('company')}")
                print(f"  Website: {record.get('website_url')}")
                print(f"  Niche: {record.get('niche')}")
                print(f"  Error Message: {record.get('contact_form_submitted_message')}")
                print(f"  Timestamp: {format_timestamp(record.get('contact_form_submitted_timestamp'))}")
        else:
            print("No records found with contact_form_submitted = NULL")
            
        # Add a test record if no failed submissions found
        if not response_false.data and not response_null.data:
            print("\nNo failed submissions found. Would you like to add a test record? (y/n)")
            response = input().lower()
            if response == 'y':
                add_test_record(supabase)
        
        return True
    except Exception as e:
        print(f"Error checking failed submissions: {e}")
        return False

def add_test_record(supabase):
    """Add a test record with a failed form submission"""
    try:
        # Create test record
        test_record = {
            "name": f"Test Failed Contact {datetime.now().strftime('%H:%M:%S')}",
            "company": "Test Failed Company",
            "website_url": "https://testfailed.com",
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
    check_failed_submissions()
