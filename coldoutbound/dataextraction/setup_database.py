"""
Script to set up the Supabase database tables for the Contact Bot application.

This script creates the necessary tables in Supabase:
1. contacts - Stores contact information and processing status
2. contact_lists - Stores information about contact lists
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

def create_contacts_table():
    """Create the contacts table"""
    if not supabase:
        print("Supabase client not initialized.")
        return False
    
    try:
        # Create contacts table
        query = """
        CREATE TABLE IF NOT EXISTS contacts (
            id UUID PRIMARY KEY,
            name TEXT,
            email TEXT,
            company TEXT,
            website_url TEXT,
            linkedin_url TEXT,
            website_visited BOOLEAN,
            website_visited_message TEXT,
            contact_form_found BOOLEAN,
            contact_form_found_message TEXT,
            contact_form_submitted BOOLEAN,
            contact_form_submitted_message TEXT,
            linkedin_connected BOOLEAN,
            linkedin_connected_message TEXT,
            error TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            list_id UUID
        );
        """
        
        # Execute the query using the REST API
        response = supabase.rpc('execute_sql', {'query': query}).execute()
        print("Contacts table created successfully.")
        return True
    except Exception as e:
        print(f"Error creating contacts table: {e}")
        return False

def create_contact_lists_table():
    """Create the contact_lists table"""
    if not supabase:
        print("Supabase client not initialized.")
        return False
    
    try:
        # Create contact_lists table
        query = """
        CREATE TABLE IF NOT EXISTS contact_lists (
            id UUID PRIMARY KEY,
            name TEXT,
            filename TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE,
            status TEXT,
            total_contacts INTEGER DEFAULT 0,
            processed_contacts INTEGER DEFAULT 0,
            successful_contacts INTEGER DEFAULT 0,
            failed_contacts INTEGER DEFAULT 0,
            error_message TEXT
        );
        """
        
        # Execute the query using the REST API
        response = supabase.rpc('execute_sql', {'query': query}).execute()
        print("Contact lists table created successfully.")
        return True
    except Exception as e:
        print(f"Error creating contact_lists table: {e}")
        return False

if __name__ == "__main__":
    if supabase:
        create_contacts_table()
        create_contact_lists_table()
        print("Database setup complete.")
    else:
        print("Failed to initialize Supabase client. Database setup failed.")
