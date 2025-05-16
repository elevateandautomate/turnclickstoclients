from dotenv import load_dotenv
import os
from supabase import create_client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL or SUPABASE_KEY environment variables are not set.")
    exit(1)

try:
    supabase = create_client(supabase_url, supabase_key)
    print("Successfully initialized Supabase client.")
    
    # Reset last_processed_contact_id to None
    response = supabase.table('outreach_settings').update({'value': None}).eq('key', 'last_processed_contact_id').execute()
    print(f"Successfully reset last_processed_contact_id to None: {response}")
    
except Exception as e:
    print(f"Error: {e}")
