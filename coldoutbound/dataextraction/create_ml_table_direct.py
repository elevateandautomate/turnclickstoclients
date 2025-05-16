#!/usr/bin/env python3
"""
Script to create the contact_bot_brain table in Supabase using direct SQL.
"""

import os
import sys
import requests
import json

def main():
    """Main function to create the contact_bot_brain table in Supabase"""
    # Get Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url:
        supabase_url = input("Enter your Supabase URL: ")
    
    if not supabase_key:
        supabase_key = input("Enter your Supabase API key: ")
    
    # Create the contact_bot_brain table using direct REST API
    try:
        # First check if the table exists
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Try to select from the table to see if it exists
        response = requests.get(
            f"{supabase_url}/rest/v1/contact_bot_brain?select=count&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Table 'contact_bot_brain' exists")
            
            # Check if it has the required columns
            try:
                response = requests.get(
                    f"{supabase_url}/rest/v1/contact_bot_brain?select=field_attributes&limit=1",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("✅ Table has the required columns")
                else:
                    print("❌ Table exists but doesn't have the required columns")
                    print("Please go to the Supabase dashboard and run the following SQL:")
                    print_create_table_sql()
            except Exception as e:
                print(f"❌ Error checking table columns: {e}")
                print("Please go to the Supabase dashboard and run the following SQL:")
                print_create_table_sql()
        else:
            print("❌ Table 'contact_bot_brain' does not exist")
            print("Please go to the Supabase dashboard and run the following SQL:")
            print_create_table_sql()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please go to the Supabase dashboard and run the following SQL:")
        print_create_table_sql()

def print_create_table_sql():
    """Print the SQL to create the contact_bot_brain table"""
    sql = """
CREATE TABLE IF NOT EXISTS public.contact_bot_brain (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name TEXT,
    field_attributes JSONB,
    field_type TEXT,
    source TEXT,
    success BOOLEAN DEFAULT true,
    model_data TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.contact_bot_brain ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users" ON public.contact_bot_brain
    FOR SELECT USING (true);
    
CREATE POLICY "Enable insert for authenticated users only" ON public.contact_bot_brain
    FOR INSERT WITH CHECK (auth.role() = 'authenticated' OR auth.role() = 'service_role');
    
CREATE POLICY "Enable update for authenticated users only" ON public.contact_bot_brain
    FOR UPDATE USING (auth.role() = 'authenticated' OR auth.role() = 'service_role');
"""
    print(sql)

if __name__ == "__main__":
    main()
