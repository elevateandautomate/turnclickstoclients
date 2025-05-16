import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: Supabase credentials not found in environment variables.")
    print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file.")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# SQL to add last_updated column
sql = """
ALTER TABLE public.core_data ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT now();
"""

try:
    # Execute the SQL
    result = supabase.table("core_data").execute(sql)
    print("Successfully added last_updated column to core_data table.")
except Exception as e:
    print(f"Error adding last_updated column: {e}")
