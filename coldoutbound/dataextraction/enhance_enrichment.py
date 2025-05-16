#!/usr/bin/env python3
"""
Script to enhance the data enrichment functionality by adding more fields:
- Niche
- First Name
- Last Name

This script will:
1. Connect to Supabase
2. Check if the contact_enrichment table exists
3. Add new columns if needed
4. Update the _update_alternative_contacts method in contact_bot.py
"""

import os
import sys
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("Error: supabase-py package not installed. Please install it with 'pip install supabase'.")
    sys.exit(1)

def main():
    """Main function to enhance data enrichment functionality"""
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
        
        # Check the structure of the table
        result = supabase.table("contact_enrichment").select("*").limit(1).execute()
        if result.data:
            columns = result.data[0].keys()
            print(f"Current columns: {', '.join(columns)}")
            
            # Check if the new columns already exist
            new_columns = ["first_name", "last_name", "niche"]
            missing_columns = [col for col in new_columns if col not in columns]
            
            if missing_columns:
                print(f"Need to add columns: {', '.join(missing_columns)}")
                
                # Add the missing columns
                try:
                    for column in missing_columns:
                        # Use RPC to add columns
                        sql = f"ALTER TABLE public.contact_enrichment ADD COLUMN IF NOT EXISTS {column} TEXT;"
                        try:
                            supabase.rpc("exec_sql", {"query": sql}).execute()
                            print(f"✅ Added column {column} to contact_enrichment table.")
                        except Exception as e:
                            print(f"❌ Error adding column {column} using RPC: {e}")
                            print("Please add this column manually in the Supabase dashboard.")
                except Exception as e:
                    print(f"❌ Error adding columns: {e}")
            else:
                print("✅ All required columns already exist.")
        else:
            print("⚠️ Table exists but is empty. Cannot check structure.")
    except Exception as e:
        print(f"❌ Error checking contact_enrichment table: {e}")
        print("The contact_enrichment table might not exist.")
        sys.exit(1)
    
    # Check if the has_enrichment column exists in the core_data table
    try:
        # Try to update a record with has_enrichment
        try:
            # Use a test update that will likely fail but tells us if the column exists
            supabase.table("core_data").update({"has_enrichment": None}).eq("id", 0).execute()
            print("✅ has_enrichment column exists in core_data table.")
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                print("❌ has_enrichment column does not exist in core_data table.")
                
                # Try to add the column
                try:
                    sql = "ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS has_enrichment BOOLEAN DEFAULT FALSE;"
                    supabase.rpc("exec_sql", {"query": sql}).execute()
                    print("✅ Added has_enrichment column to core_data table.")
                except Exception as add_error:
                    print(f"❌ Error adding has_enrichment column: {add_error}")
                    print("Please add this column manually in the Supabase dashboard.")
            else:
                print("✅ has_enrichment column likely exists (got a different error).")
    except Exception as e:
        print(f"❌ Error checking has_enrichment column: {e}")
    
    # Now check the contact_bot.py file to see if we need to update it
    try:
        with open("contact_bot.py", "r", encoding="utf-8") as file:
            content = file.read()
        
        # Check if the _update_alternative_contacts method already handles these fields
        if "first_name" in content and "last_name" in content and "niche" in content and all(term in content for term in ["enrichment_data", "first_name", "last_name", "niche"]):
            print("✅ contact_bot.py already appears to handle the new fields.")
        else:
            print("⚠️ contact_bot.py needs to be updated to handle the new fields.")
            print("Please update the _update_alternative_contacts method to include first_name, last_name, and niche.")
            
            # Find the _update_alternative_contacts method
            method_pattern = r"def _update_alternative_contacts\(self, contact_id: str, alternative_contacts: Dict\[str, str\]\) -> None:"
            if re.search(method_pattern, content):
                print("✅ Found the _update_alternative_contacts method.")
                
                # Find where to insert the new code
                insert_pattern = r"# Prepare the enrichment data"
                if re.search(insert_pattern, content):
                    print("✅ Found the insertion point.")
                    print("\nHere's the code to add after '# Prepare the enrichment data':")
                    print("""
            # Get first name, last name, and niche from the main contact record
            try:
                contact_result = self.supabase.table(TABLE_NAME).select("listing_name, niche").eq("id", contact_id).execute()
                
                first_name = ""
                last_name = ""
                niche = ""
                
                if contact_result.data and len(contact_result.data) > 0:
                    contact = contact_result.data[0]
                    
                    # Extract first and last name from listing_name
                    if contact.get("listing_name"):
                        name_parts = contact.get("listing_name", "").split(" ", 1)
                        first_name = name_parts[0] if len(name_parts) > 0 else ""
                        last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    # Get niche
                    niche = contact.get("niche", "")
            except Exception as e:
                print(f"Error getting contact details for enrichment: {e}")
                first_name = ""
                last_name = ""
                niche = ""
                    """)
                    
                    # Find where to insert the new fields in the enrichment_data
                    insert_pattern2 = r"enrichment_data = \{"
                    if re.search(insert_pattern2, content):
                        print("\nAnd add these fields to the enrichment_data dictionary:")
                        print("""
                "first_name": first_name,
                "last_name": last_name,
                "niche": niche,""")
                    else:
                        print("❌ Could not find the enrichment_data dictionary.")
                else:
                    print("❌ Could not find the insertion point.")
            else:
                print("❌ Could not find the _update_alternative_contacts method.")
    except Exception as e:
        print(f"❌ Error checking contact_bot.py: {e}")

if __name__ == "__main__":
    main()
