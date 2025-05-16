#!/usr/bin/env python3
"""
Script to test Supabase connection and verify tracking tables.
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

def check_table_exists(supabase, table_name):
    """Check if a table exists in Supabase."""
    try:
        print(f"Checking if table '{table_name}' exists...")
        response = supabase.table(table_name).select('*').limit(1).execute()
        print(f"✅ Table '{table_name}' exists")
        return True
    except Exception as e:
        print(f"❌ Table '{table_name}' does not exist or is not accessible: {e}")
        return False

def count_records(supabase, table_name):
    """Count the number of records in a table."""
    try:
        print(f"Counting records in table '{table_name}'...")
        response = supabase.table(table_name).select('*', count='exact').execute()
        count = len(response.data)
        print(f"✅ Table '{table_name}' has {count} records")
        return count
    except Exception as e:
        print(f"❌ Failed to count records in table '{table_name}': {e}")
        return 0

def main():
    """Main function to run tests."""
    print("🚀 Starting Supabase connection test")
    
    # Initialize Supabase client
    supabase = initialize_supabase()
    
    # Check if tracking tables exist
    tables_to_check = ['tctc_user_flow', 'tctc_user_behavior', 'tctc_quiz_submission']
    
    all_tables_exist = True
    for table in tables_to_check:
        if not check_table_exists(supabase, table):
            all_tables_exist = False
    
    if all_tables_exist:
        print("\n✅ All required tables exist in Supabase")
    else:
        print("\n❌ Some required tables are missing in Supabase")
    
    # Count records in each table
    print("\nCounting records in each table:")
    for table in tables_to_check:
        count_records(supabase, table)
    
    print("\n✅ Supabase connection test completed")

if __name__ == "__main__":
    main()
