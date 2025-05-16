"""
Test script to check if the exec_sql function exists in Supabase
"""

from supabase import create_client

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"

def test_exec_sql():
    """Test if the exec_sql function exists in Supabase"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")

        # Try to call the exec_sql function with a simple query
        test_sql = "SELECT 1 as test;"
        result = supabase.rpc("exec_sql", {"query": test_sql}).execute()

        print("Success! The exec_sql function exists and works.")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        print("\nThe exec_sql function may not exist in your Supabase project.")
        print("You need to create it with the following SQL:")
        print("""
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
END;
$$;
        """)
        return False

def check_niche_column():
    """Check if the niche column exists in the dentist table"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client.")

        # Try to get one record to check the structure
        sample = supabase.table(TABLE_NAME).select("*").limit(1).execute()

        if sample.data:
            columns = sample.data[0].keys()
            if "niche" in columns:
                print("✅ The 'niche' column already exists in the table.")

                # Check if all records have a niche value
                count_query = supabase.table(TABLE_NAME).select("count", count="exact").is_("niche", None).execute()
                null_count = count_query.count

                if null_count > 0:
                    print(f"⚠️ Found {null_count} records with NULL niche values.")
                    print("Run the SQL script to update these records to 'dentist'.")
                else:
                    print("✅ All records have a niche value set.")

                return True
            else:
                print("❌ The 'niche' column does not exist in the table.")
                print("Please run the SQL script to add this column.")
                return False
        else:
            print("No data found in the table. Cannot check structure.")
            return False
    except Exception as e:
        print(f"Error checking niche column: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing exec_sql function ===")
    test_exec_sql()
    print("\n=== Checking niche column ===")
    check_niche_column()
