#!/usr/bin/env python3
"""
Test script to verify that the ContactBot._record_field_training_example method
is working correctly and storing data in Supabase.
"""

import os
import sys
import time
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the ContactBot class
try:
    from contact_bot import ContactBot
except ImportError:
    print("Error: contact_bot.py not found in the current directory.")
    sys.exit(1)

def main():
    """Main function to test the ContactBot._record_field_training_example method"""
    # Get Supabase credentials from environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("Supabase credentials not found in environment variables. Please check your .env file.")
        sys.exit(1)

    # Create the ContactBot instance
    print("Initializing ContactBot...")
    bot = ContactBot(
        headless=True,  # Run in headless mode for testing
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )

    try:
        # Check if the field_classifier is initialized
        if not bot.field_classifier:
            print("❌ Field classifier not initialized. Make sure the FormFieldClassifier class is available.")
            return

        print("✅ Field classifier initialized successfully.")

        # Create a test field attributes dictionary
        test_field_attributes = {
            "id": "contact-email",
            "name": "your-email",
            "class": "wpcf7-form-control",
            "type": "email",
            "placeholder": "Your Email Address",
            "tag_name": "input",
            "aria-label": "Email"
        }

        # Test recording a training example
        print("\nTesting _record_field_training_example method...")
        try:
            # Record a test example
            bot._record_field_training_example(
                field_attributes=test_field_attributes,
                field_type="email",
                success=True
            )
            print("✅ Successfully called _record_field_training_example method.")
        except Exception as e:
            print(f"❌ Error calling _record_field_training_example method: {e}")
            return

        # Test retraining the model
        print("\nTesting retrain_field_classifier method...")
        try:
            result = bot.retrain_field_classifier()
            if result:
                print("✅ Successfully retrained field classifier.")
            else:
                print("⚠️ Field classifier retraining returned False.")
        except Exception as e:
            print(f"❌ Error retraining field classifier: {e}")

        # Verify the data was stored by retrieving it
        print("\nVerifying data was stored in Supabase...")
        try:
            # Get the table name from the field_classifier
            table_name = getattr(bot.field_classifier, "table_name", "contact_bot_brain")

            # Query the table for the most recent entries
            result = bot.supabase.table(table_name).select("*").order("created_at", desc=True).limit(5).execute()

            if result.data:
                print(f"✅ Successfully retrieved {len(result.data)} training examples:")
                for i, example in enumerate(result.data):
                    print(f"\nExample {i+1}:")
                    print(f"  Field Type: {example.get('field_type')}")
                    print(f"  Source: {example.get('source')}")
                    print(f"  Success: {example.get('success')}")
                    print(f"  Created At: {example.get('created_at')}")
            else:
                print("❌ No training examples found in the database.")
        except Exception as e:
            print(f"❌ Error retrieving training examples: {e}")

    finally:
        # Close the browser
        print("\nClosing the browser...")
        bot.close()
        print("✅ Browser closed.")

if __name__ == "__main__":
    main()
