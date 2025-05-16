#!/usr/bin/env python3
"""
Script to create the contact_bot_brain table in Supabase.
"""

import os
import sys
from supabase import create_client

def main():
    """Main function to create the contact_bot_brain table in Supabase"""
    # Get Supabase credentials
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url:
        supabase_url = input("Enter your Supabase URL: ")
    
    if not supabase_key:
        supabase_key = input("Enter your Supabase API key: ")
    
    # Connect to Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully")
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return
    
    # Create the contact_bot_brain table
    try:
        # Check if the table exists
        try:
            supabase.table("contact_bot_brain").select("count", count="exact").limit(1).execute()
            print("✅ Table 'contact_bot_brain' already exists")
            
            # Check if it has the required columns
            try:
                # Try to select a specific column to see if it exists
                supabase.table("contact_bot_brain").select("field_attributes").limit(1).execute()
                print("✅ Table has the required columns")
            except Exception as e:
                if "column" in str(e).lower() and "does not exist" in str(e).lower():
                    print("❌ Table exists but doesn't have the required columns. Recreating...")
                    # Drop the table
                    supabase.rpc("exec_sql", {"query": "DROP TABLE IF EXISTS public.contact_bot_brain;"}).execute()
                    print("✅ Dropped existing table")
                    # Create the table with the correct schema
                    create_table(supabase)
                else:
                    print(f"❌ Error checking table columns: {e}")
        except Exception as e:
            if "does not exist" in str(e).lower():
                print("❌ Table 'contact_bot_brain' does not exist. Creating...")
                create_table(supabase)
            else:
                print(f"❌ Error checking if table exists: {e}")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

def create_table(supabase):
    """Create the contact_bot_brain table with the correct schema"""
    try:
        # Create the table using RPC
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
        """
        supabase.rpc("exec_sql", {"query": sql}).execute()
        print("✅ Created table 'contact_bot_brain'")
        
        # Set up RLS policies
        rls_sql = """
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
        supabase.rpc("exec_sql", {"query": rls_sql}).execute()
        print("✅ Set up RLS policies")
        
        return True
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    main()
