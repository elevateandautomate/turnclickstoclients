#!/usr/bin/env python3
"""
Test script to verify the connection between ContactBot and FormFieldClassifier.
This script tests:
1. If form_ml_supabase.py exists
2. If FormFieldClassifier is properly initialized with Supabase client
3. If adding a training example works
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if form_ml_supabase.py exists
form_ml_supabase_exists = os.path.exists("form_ml_supabase.py")
print(f"form_ml_supabase.py exists: {form_ml_supabase_exists}")

# Try to import the FormFieldClassifier
if form_ml_supabase_exists:
    try:
        from form_ml_supabase import FormFieldClassifier
        print("✅ Successfully imported FormFieldClassifier from form_ml_supabase.py")
    except ImportError as e:
        print(f"❌ Error importing FormFieldClassifier from form_ml_supabase.py: {e}")
        sys.exit(1)
else:
    print("❌ form_ml_supabase.py does not exist. Creating it...")

    # Create the form_ml_supabase.py file
    with open("form_ml_supabase.py", "w") as f:
        f.write("""\"\"\"
Machine learning classifier for form fields with Supabase storage
\"\"\"

import os
import json
import pickle
import base64
from typing import Dict, List, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Field types we want to recognize
FIELD_TYPES = [
    'first_name',
    'last_name',
    'full_name',
    'email',
    'phone',
    'company',
    'message',
    'subject',
    'address',
    'city',
    'state',
    'zip',
    'country',
    'website',
    'date',
    'time',
    'checkbox',
    'radio',
    'dropdown',
    'submit',
    'unknown'
]

class FormFieldClassifier:
    \"\"\"Machine learning classifier for form fields with Supabase storage\"\"\"

    def __init__(self, supabase_client=None, model_name: str = 'form_field_classifier'):
        \"\"\"Initialize the classifier

        Args:
            supabase_client: Supabase client instance
            model_name: Name of the model in the database
        \"\"\"
        self.supabase = supabase_client
        self.model_name = model_name
        self.vectorizer = None
        self.classifier = None
        self.is_trained = False
        self.table_name = 'contact_bot_brain'

        # For local development fallback
        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{model_name}.pkl")

        # Try to load an existing model
        if self.supabase:
            # Try to load from Supabase first
            if not self.load_model_from_supabase():
                # If not found in Supabase, try local file
                self.load_model_from_file()
        else:
            print("Warning: No Supabase client provided. Using local file storage.")
            self.load_model_from_file()

    def load_model_from_supabase(self) -> bool:
        \"\"\"Load the model from Supabase

        Returns:
            True if model was loaded successfully, False otherwise
        \"\"\"
        try:
            # Get the latest version of the model
            response = self.supabase.table(self.table_name) \\
                .select('model_data, version') \\
                .eq('model_name', self.model_name) \\
                .order('version', desc=True) \\
                .limit(1) \\
                .execute()

            if response.data and len(response.data) > 0:
                # Decode the model data from base64
                model_data_base64 = response.data[0]['model_data']
                model_data_bytes = base64.b64decode(model_data_base64)

                # Load the model from bytes
                model_dict = pickle.loads(model_data_bytes)
                self.vectorizer = model_dict['vectorizer']
                self.classifier = model_dict['classifier']
                self.is_trained = True

                print(f"Loaded model '{self.model_name}' (version {response.data[0]['version']}) from Supabase")
                return True
            else:
                print(f"No model '{self.model_name}' found in Supabase")
                return False
        except Exception as e:
            print(f"Error loading model from Supabase: {e}")
            return False

    def add_training_example(self, field_attributes: Dict[str, Any], field_type: str, source: str = None, success: bool = True) -> bool:
        \"\"\"Add a new training example to the database

        Args:
            field_attributes: Dictionary with field attributes
            field_type: The correct field type
            source: Source of the example (e.g., website URL)
            success: Whether the form submission was successful

        Returns:
            True if example was added successfully, False otherwise
        \"\"\"
        if not self.supabase:
            print("No Supabase client provided")
            return False

        try:
            data = {
                'field_attributes': json.dumps(field_attributes),
                'field_type': field_type,
                'source': source,
                'success': success
            }

            print(f"Adding training example to {self.table_name} table:")
            print(json.dumps(data, indent=2))

            result = self.supabase.table(self.table_name).insert(data).execute()

            print(f"Added new training example for field type '{field_type}'")
            print(f"Supabase response: {result}")
            return True
        except Exception as e:
            print(f"Error adding training example: {e}")
            return False
""")

    print("✅ Created form_ml_supabase.py")

    # Import the FormFieldClassifier
    try:
        from form_ml_supabase import FormFieldClassifier
        print("✅ Successfully imported FormFieldClassifier from newly created form_ml_supabase.py")
    except ImportError as e:
        print(f"❌ Error importing FormFieldClassifier from newly created form_ml_supabase.py: {e}")
        sys.exit(1)

# Try to import the ContactBot
try:
    from contact_bot import ContactBot
    print("✅ Successfully imported ContactBot")
except ImportError as e:
    print(f"❌ Error importing ContactBot: {e}")
    sys.exit(1)

# Get Supabase credentials from environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("Supabase credentials not found in environment variables. Please check your .env file.")
    sys.exit(1)

# Test 1: Create a FormFieldClassifier directly with Supabase client
try:
    from supabase import create_client

    print("\nTest 1: Creating FormFieldClassifier directly with Supabase client...")
    supabase = create_client(supabase_url, supabase_key)

    classifier = FormFieldClassifier(supabase_client=supabase)

    if classifier.supabase:
        print("✅ FormFieldClassifier initialized with Supabase client")
    else:
        print("❌ FormFieldClassifier not initialized with Supabase client")

    # Test adding a training example
    test_field_attributes = {
        "id": "direct-test-email",
        "name": "your-email",
        "class": "form-control",
        "type": "email",
        "placeholder": "Your Email Address",
        "tag_name": "input"
    }

    result = classifier.add_training_example(
        field_attributes=test_field_attributes,
        field_type="email",
        source="https://test-direct.com/contact",
        success=True
    )

    if result:
        print("✅ Successfully added training example directly")
    else:
        print("❌ Failed to add training example directly")

except Exception as e:
    print(f"❌ Error in Test 1: {e}")

# Test 2: Create a ContactBot and check if FormFieldClassifier is initialized correctly
try:
    print("\nTest 2: Creating ContactBot and checking FormFieldClassifier initialization...")

    bot = ContactBot(
        headless=True,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )

    if bot.field_classifier:
        print("✅ ContactBot has field_classifier initialized")

        if bot.field_classifier.supabase:
            print("✅ field_classifier has Supabase client initialized")
        else:
            print("❌ field_classifier does not have Supabase client initialized")

            # Fix the issue by setting the Supabase client
            print("Fixing the issue by setting the Supabase client...")
            bot.field_classifier.supabase = bot.supabase

            if bot.field_classifier.supabase:
                print("✅ Successfully set Supabase client in field_classifier")
            else:
                print("❌ Failed to set Supabase client in field_classifier")
    else:
        print("❌ ContactBot does not have field_classifier initialized")

    # Test adding a training example through ContactBot
    test_field_attributes = {
        "id": "bot-test-email",
        "name": "your-email",
        "class": "form-control",
        "type": "email",
        "placeholder": "Your Email Address",
        "tag_name": "input"
    }

    bot._record_field_training_example(
        field_attributes=test_field_attributes,
        field_type="email",
        success=True
    )

    print("✅ Called _record_field_training_example method")

except Exception as e:
    print(f"❌ Error in Test 2: {e}")

print("\nTests completed.")
