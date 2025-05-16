"""
Script to check if specific tables exist in the Supabase database.
"""

import os
import json
from supabase import create_client, Client

# Load settings
def load_settings():
    """Load settings from file"""
    settings_file = 'settings.json'
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
    return {}

# Get Supabase credentials
settings = load_settings()
SUPABASE_URL = settings.get('supabase_url', "https://eumhqssfvkyuepyrtlqj.supabase.co")
SUPABASE_KEY = settings.get('supabase_key', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck")

# Initialize Supabase client
supabase = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")
    else:
        print("CRITICAL: Supabase URL or Key is missing.")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

def check_table(table_name):
    """Check if a table exists by trying to select from it"""
    if not supabase:
        print("Supabase client not initialized.")
        return False
    
    try:
        # Try to select from the table
        response = supabase.table(table_name).select("*").limit(1).execute()
        print(f"Table '{table_name}' exists.")
        return True
    except Exception as e:
        print(f"Table '{table_name}' does not exist or is not accessible: {e}")
        return False

if __name__ == "__main__":
    if supabase:
        # Check for the contacts table
        check_table("contacts")
        
        # Check for the contact_lists table
        check_table("contact_lists")
        
        # Check for other possible table names
        check_table("Contacts")
        check_table("ContactLists")
        check_table("contact_list")
        check_table("contactlist")
    else:
        print("Failed to initialize Supabase client.")
