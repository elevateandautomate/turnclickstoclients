#!/usr/bin/env python3
"""
Script to check the schema of Supabase tables.
"""

import sys
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64'

def initialize_supabase() -> Client:
    """Initialize Supabase client."""
    try:
        print("Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Successfully connected to Supabase")
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

def check_table_schema(supabase, table_name):
    """Check the schema of a table in Supabase."""
    try:
        print(f"Checking schema of table '{table_name}'...")
        
        # Get a sample record to see the columns
        response = supabase.table(table_name).select('*').limit(1).execute()
        
        if response.data:
            print(f"✅ Table '{table_name}' has the following columns:")
            for column in response.data[0].keys():
                print(f"  - {column}")
        else:
            print(f"⚠️ Table '{table_name}' exists but has no records")
            
            # Try to get the schema from the database
            try:
                # This is a workaround to get the schema when there are no records
                # Create a dummy record with minimal data
                dummy_data = {'id': 'test'}
                insert_response = supabase.table(table_name).insert(dummy_data).execute()
                
                if insert_response.data:
                    print(f"✅ Created dummy record to check schema")
                    
                    # Delete the dummy record
                    delete_response = supabase.table(table_name).delete().eq('id', 'test').execute()
                    
                    if delete_response.data:
                        print(f"✅ Deleted dummy record")
                    else:
                        print(f"⚠️ Failed to delete dummy record")
                else:
                    print(f"⚠️ Failed to create dummy record")
            except Exception as e:
                print(f"⚠️ Could not determine schema: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to check schema of table '{table_name}': {e}")
        return False

def main():
    """Main function to run tests."""
    print("🚀 Starting Supabase schema check")
    
    # Initialize Supabase client
    supabase = initialize_supabase()
    
    # Check schema of tracking tables
    tables_to_check = ['tctc_user_flow', 'tctc_user_behavior', 'tctc_quiz_submission']
    
    for table in tables_to_check:
        check_table_schema(supabase, table)
    
    print("\n✅ Supabase schema check completed")

if __name__ == "__main__":
    main()
