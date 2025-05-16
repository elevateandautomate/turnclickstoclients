#!/usr/bin/env python3
"""
Test script to verify that the data enrichment functionality is working correctly
and updating the Supabase table with alternative contact information.
"""

import os
import sys
import json
import uuid
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
    """Main function to test the data enrichment functionality"""
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
        # Check if Supabase is initialized
        if not bot.supabase:
            print("❌ Supabase client not initialized. Exiting.")
            return

        print("✅ Supabase client initialized successfully.")

        # Check the structure of the core_data table
        print("\nChecking the structure of the core_data table...")
        try:
            # Try to get the table structure
            result = bot.supabase.table("core_data").select("*").limit(1).execute()
            print("✅ core_data table exists.")

            # Get the column names
            if result.data:
                columns = result.data[0].keys()
                print(f"Table columns: {', '.join(columns)}")
            else:
                print("Table exists but is empty.")
                # Try to get the columns using a different method
                try:
                    # This is a workaround to get column names when the table is empty
                    result = bot.supabase.table("core_data").select("count", count="exact").execute()
                    print("Table exists and has structure.")
                except Exception as e:
                    print(f"Error getting table structure: {e}")
        except Exception as e:
            print(f"❌ Error checking core_data table: {e}")
            print("The table might not exist or there might be permission issues.")
            return

        # Create a test contact in the database
        # Use a random integer ID instead of UUID
        import random
        test_contact_id = random.randint(10000000, 99999999)
        test_contact = {
            "id": test_contact_id,
            "listing_name": "Test Contact",  # Using listing_name instead of name
            "website_url_profile": "https://example.com/test",
            "niche": "test",
            "listing_actual_location": "Test Location",  # Required field
            "listing_business_name": "Test Business"  # Another potentially required field
        }

        print(f"\nCreating test contact with ID: {test_contact_id}")
        try:
            result = bot.supabase.table("core_data").insert(test_contact).execute()
            print("✅ Test contact created successfully.")
        except Exception as e:
            print(f"❌ Error creating test contact: {e}")
            print("Please check your Supabase setup and try again.")
            return

        # Test 1: Ensure the _update_alternative_contacts method exists
        print("\nTest 1: Checking if _update_alternative_contacts method exists...")
        if hasattr(bot, '_update_alternative_contacts'):
            print("✅ _update_alternative_contacts method exists.")
        else:
            print("❌ _update_alternative_contacts method does not exist.")
            return

        # Test 2: Test the _update_alternative_contacts method
        print("\nTest 2: Testing _update_alternative_contacts method...")

        # Create test alternative contacts
        alternative_contacts = {
            "Email": "alternative@example.com",
            "Phone": "+1234567890",
            "Facebook": "https://facebook.com/test",
            "Twitter": "https://twitter.com/test",
            "LinkedIn": "https://linkedin.com/in/test"
        }

        # Set the current contact ID
        bot.current_contact_id = test_contact_id

        # Call the _update_alternative_contacts method
        try:
            bot._update_alternative_contacts(test_contact_id, alternative_contacts)
            print("✅ _update_alternative_contacts method called successfully.")
        except Exception as e:
            print(f"❌ Error calling _update_alternative_contacts method: {e}")
            # If the method doesn't exist or has an error, try to update directly
            try:
                print("Trying to update directly using Supabase...")
                update_data = {**alternative_contacts, "updated_at": "now()"}
                bot.supabase.table("core_data").update(update_data).eq("id", test_contact_id).execute()
                print("✅ Direct update successful.")
            except Exception as direct_error:
                print(f"❌ Error updating directly: {direct_error}")
                return

        # Test 3: Verify that the data was updated in Supabase
        print("\nTest 3: Verifying data was updated in Supabase...")

        # First check the main core_data table
        try:
            result = bot.supabase.table("core_data").select("*").eq("id", test_contact_id).execute()

            if result.data and len(result.data) > 0:
                contact = result.data[0]
                print("✅ Retrieved contact from core_data table:")

                # Check if alternative contacts were added directly to the main table
                enriched_fields = {k: v for k, v in contact.items() if k.startswith("enriched_")}

                if enriched_fields:
                    print("✅ Alternative contacts were added to the main table:")
                    for field, value in enriched_fields.items():
                        print(f"  - {field}: {value}")
                else:
                    print("ℹ️ No enriched fields found in the main table. This is expected if using the contact_enrichment table.")
                    print("Main table data:", json.dumps(contact, indent=2))
            else:
                print(f"❌ Could not retrieve contact with ID {test_contact_id} from core_data table.")
        except Exception as e:
            print(f"❌ Error retrieving contact from core_data table: {e}")

        # Now check the contact_enrichment table
        print("\nChecking the contact_enrichment table...")
        try:
            result = bot.supabase.table("contact_enrichment").select("*").eq("contact_id", test_contact_id).execute()

            if result.data and len(result.data) > 0:
                enrichment = result.data[0]
                print("✅ Retrieved enrichment data from contact_enrichment table:")
                print(json.dumps(enrichment, indent=2))

                # Check if the expected data types are present
                expected_types = ["email", "phone", "facebook", "twitter", "linkedin"]
                found_types = []

                if "emails" in enrichment and enrichment["emails"]:
                    found_types.append("email")
                    print(f"  - Emails: {enrichment['emails']}")

                if "phone_numbers" in enrichment and enrichment["phone_numbers"]:
                    found_types.append("phone")
                    print(f"  - Phone numbers: {enrichment['phone_numbers']}")

                # Check for social media links in the social_media field
                if "social_media" in enrichment and enrichment["social_media"]:
                    try:
                        social_media = enrichment["social_media"]
                        if isinstance(social_media, str):
                            social_media = json.loads(social_media)

                        print(f"  - Social media: {json.dumps(social_media, indent=2)}")

                        if "facebook" in social_media and social_media["facebook"]:
                            found_types.append("facebook")
                            print(f"  - Facebook: {social_media['facebook']}")

                        if "twitter" in social_media and social_media["twitter"]:
                            found_types.append("twitter")
                            print(f"  - Twitter: {social_media['twitter']}")

                        if "linkedin" in social_media and social_media["linkedin"]:
                            found_types.append("linkedin")
                            print(f"  - LinkedIn: {social_media['linkedin']}")
                    except Exception as social_error:
                        print(f"  - Error parsing social media: {social_error}")
                        print(f"  - Social media (raw): {enrichment['social_media']}")

                missing_types = [t for t in expected_types if t not in found_types]
                if missing_types:
                    print(f"⚠️ Some expected data types were not found in the enrichment table: {missing_types}")
                else:
                    print("✅ All expected data types were found in the enrichment table.")
            else:
                print("❌ No enrichment data found in the contact_enrichment table.")

                # Try to check if the table exists
                try:
                    bot.supabase.table("contact_enrichment").select("count", count="exact").execute()
                    print("ℹ️ The contact_enrichment table exists but no data was inserted.")
                except Exception as table_error:
                    print(f"❌ Error checking contact_enrichment table: {table_error}")
                    print("The contact_enrichment table might not exist.")
        except Exception as e:
            print(f"❌ Error retrieving data from contact_enrichment table: {e}")

        # Clean up: Delete the test contact
        print("\nCleaning up: Deleting test contact...")
        try:
            bot.supabase.table("core_data").delete().eq("id", test_contact_id).execute()
            print("✅ Test contact deleted successfully.")
        except Exception as e:
            print(f"❌ Error deleting test contact: {e}")

    finally:
        # Close the browser
        print("\nClosing the browser...")
        bot.close()
        print("✅ Browser closed.")

if __name__ == "__main__":
    main()
