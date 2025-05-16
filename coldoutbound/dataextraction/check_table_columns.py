"""
Script to check the column names in the core_data table
"""

from supabase import create_client
import json

# Constants
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck"
TABLE_NAME = "core_data"

def check_table_columns():
    """Check the column names in the core_data table"""
    try:
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"Successfully initialized Supabase client.")
        
        # Get the column information using a SQL query
        sql = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = '{TABLE_NAME}'
        ORDER BY ordinal_position;
        """
        
        response = supabase.rpc("exec_sql", {"query": sql}).execute()
        
        if hasattr(response, 'data') and response.data:
            print(f"\nColumns in the {TABLE_NAME} table:")
            for column in response.data:
                print(f"  {column['column_name']} ({column['data_type']}, nullable: {column['is_nullable']})")
            return response.data
        else:
            # If exec_sql doesn't work, try a different approach
            print(f"Could not get column information using exec_sql. Trying a different approach...")
            
            # Try to get one record to see the columns
            response = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            
            if response.data:
                columns = list(response.data[0].keys())
                print(f"\nColumns in the {TABLE_NAME} table (from sample record):")
                for column in columns:
                    print(f"  {column}")
                return columns
            else:
                print(f"No data found in the {TABLE_NAME} table.")
                return []
    except Exception as e:
        print(f"Error checking table columns: {e}")
        
        # Try a different approach if the first one fails
        try:
            print(f"Trying a different approach...")
            
            # Try to get one record to see the columns
            response = supabase.table(TABLE_NAME).select("*").limit(1).execute()
            
            if response.data:
                columns = list(response.data[0].keys())
                print(f"\nColumns in the {TABLE_NAME} table (from sample record):")
                for column in columns:
                    print(f"  {column}")
                return columns
            else:
                print(f"No data found in the {TABLE_NAME} table.")
                return []
        except Exception as e2:
            print(f"Error with second approach: {e2}")
            return []

def suggest_api_changes(columns):
    """Suggest changes to the API based on the actual column names"""
    if not columns:
        return
    
    # Expected columns in the API
    expected_columns = [
        "id", "name", "company", "website_url", "contact_form_submitted", 
        "contact_form_submitted_message", "contact_form_submitted_timestamp", "niche"
    ]
    
    # Check which expected columns are missing
    if isinstance(columns, list):
        # If columns is a simple list of column names
        column_names = columns
    else:
        # If columns is a list of dictionaries with column_name key
        column_names = [col.get('column_name') for col in columns]
    
    missing_columns = [col for col in expected_columns if col not in column_names]
    
    if missing_columns:
        print(f"\nMissing columns in the {TABLE_NAME} table:")
        for col in missing_columns:
            print(f"  {col}")
        
        print("\nSuggested changes to the API:")
        for col in missing_columns:
            # Look for similar column names
            similar_columns = []
            for actual_col in column_names:
                # Check if the expected column name is a substring of the actual column name
                if col.lower() in actual_col.lower():
                    similar_columns.append(actual_col)
            
            if similar_columns:
                print(f"  Instead of '{col}', use one of these columns: {', '.join(similar_columns)}")
            else:
                print(f"  No similar column found for '{col}'")
    else:
        print("\nAll expected columns are present in the table.")

if __name__ == "__main__":
    columns = check_table_columns()
    suggest_api_changes(columns)
