#!/usr/bin/env python3
"""
Test script to verify that machine learning data is being stored in Supabase.
This script tests:
1. Connection to Supabase
2. Creation of the contact_bot_brain table if it doesn't exist
3. Adding a test training example
4. Retrieving and displaying the stored data
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from supabase import create_client
except ImportError:
    print("Error: supabase-py package not installed. Install it with: pip install supabase")
    sys.exit(1)

# Import the FormFieldClassifier if available
try:
    from ml.form_field_classifier import FormFieldClassifier
except ImportError:
    print("Warning: FormFieldClassifier not found. Creating a mock version for testing.")

    class FormFieldClassifier:
        """Mock FormFieldClassifier for testing"""
        def __init__(self):
            self.is_trained = False
            self.supabase = None
            self.table_name = "contact_bot_brain"

        def connect_to_supabase(self, url, key):
            """Connect to Supabase"""
            try:
                self.supabase = create_client(url, key)
                print("✅ Connected to Supabase successfully")
                return True
            except Exception as e:
                print(f"❌ Error connecting to Supabase: {e}")
                return False

        def ensure_table_exists(self):
            """Ensure the ML data table exists"""
            if not self.supabase:
                print("❌ Supabase client not initialized")
                return False

            try:
                # Check if table exists by trying to select from it
                self.supabase.table(self.table_name).select("count", count="exact").limit(1).execute()
                print(f"✅ Table '{self.table_name}' exists")
                return True
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"Table '{self.table_name}' does not exist. Attempting to create it...")
                    try:
                        # Create the table using RPC
                        sql = f"""
                        CREATE TABLE IF NOT EXISTS public.{self.table_name} (
                            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                            field_attributes JSONB NOT NULL,
                            field_type TEXT NOT NULL,
                            source TEXT,
                            success BOOLEAN DEFAULT true,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
                        );
                        """
                        self.supabase.rpc("exec_sql", {"query": sql}).execute()
                        print(f"✅ Created table '{self.table_name}'")
                        return True
                    except Exception as create_error:
                        print(f"❌ Error creating table: {create_error}")
                        print("Please create the table manually with the following columns:")
                        print("- id: UUID PRIMARY KEY DEFAULT uuid_generate_v4()")
                        print("- field_attributes: JSONB NOT NULL")
                        print("- field_type: TEXT NOT NULL")
                        print("- source: TEXT")
                        print("- success: BOOLEAN DEFAULT true")
                        print("- created_at: TIMESTAMP WITH TIME ZONE DEFAULT now()")
                        return False
                else:
                    print(f"❌ Error checking if table exists: {e}")
                    return False

        def add_training_example(self, field_attributes, field_type, source=None, success=True):
            """Add a training example to the database"""
            if not self.supabase:
                print("❌ Supabase client not initialized")
                return False

            try:
                # Insert the training example
                data = {
                    "field_attributes": json.dumps(field_attributes),
                    "field_type": field_type,
                    "source": source,
                    "success": success
                }
                result = self.supabase.table(self.table_name).insert(data).execute()
                print(f"✅ Added training example for field type '{field_type}'")
                return True
            except Exception as e:
                print(f"❌ Error adding training example: {e}")
                return False

        def get_training_examples(self, limit=10):
            """Get training examples from the database"""
            if not self.supabase:
                print("❌ Supabase client not initialized")
                return []

            try:
                # Get the training examples
                result = self.supabase.table(self.table_name).select("*").limit(limit).order("created_at", desc=True).execute()
                return result.data
            except Exception as e:
                print(f"❌ Error getting training examples: {e}")
                return []

def main():
    """Main function to test ML data storage in Supabase"""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("Supabase credentials not found in environment variables. Please check your .env file.")
        sys.exit(1)

    # Create the classifier
    classifier = FormFieldClassifier()

    # Connect to Supabase
    if not classifier.connect_to_supabase(supabase_url, supabase_key):
        print("❌ Failed to connect to Supabase. Exiting.")
        return

    # Ensure the table exists
    if not classifier.ensure_table_exists():
        print("❌ Failed to ensure table exists. Exiting.")
        return

    # Add a test training example
    test_field_attributes = {
        "id": "email",
        "name": "user_email",
        "class": "form-control",
        "type": "email",
        "placeholder": "Enter your email",
        "tag_name": "input",
        "aria-label": "Email"
    }

    if not classifier.add_training_example(
        field_attributes=test_field_attributes,
        field_type="email",
        source="https://test-website.com/contact",
        success=True
    ):
        print("❌ Failed to add test training example. Exiting.")
        return

    # Get and display the training examples
    examples = classifier.get_training_examples(limit=5)
    if examples:
        print(f"\n✅ Successfully retrieved {len(examples)} training examples:")
        for i, example in enumerate(examples):
            print(f"\nExample {i+1}:")
            print(f"  Field Type: {example.get('field_type')}")
            print(f"  Source: {example.get('source')}")
            print(f"  Success: {example.get('success')}")
            print(f"  Created At: {example.get('created_at')}")

            # Parse and display field attributes
            try:
                if isinstance(example.get('field_attributes'), str):
                    attrs = json.loads(example.get('field_attributes'))
                else:
                    attrs = example.get('field_attributes')
                print("  Field Attributes:")
                for key, value in attrs.items():
                    print(f"    {key}: {value}")
            except Exception as e:
                print(f"  Error parsing field attributes: {e}")
    else:
        print("❌ No training examples found or error retrieving them.")

if __name__ == "__main__":
    main()
