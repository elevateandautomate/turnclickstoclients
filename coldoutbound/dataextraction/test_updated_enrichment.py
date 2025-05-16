#!/usr/bin/env python3
"""
Test script to verify that the updated enrichment methods work correctly.
"""

import os
import sys
import json
import random
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
    """Main function to test the updated enrichment methods"""
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
        
        # Create a test contact in the database
        # Use a random integer ID instead of UUID
        test_contact_id = random.randint(10000000, 99999999)
        test_contact = {
            "id": test_contact_id,
            "listing_name": "John Smith",  # Using listing_name instead of name
            "website_url_profile": "https://example.com/test",
            "niche": "dentist",
            "listing_actual_location": "Test Location",  # Required field
            "listing_business_name": "Test Business"  # Another potentially required field
        }
        
        print(f"\nCreating test contact with ID: {test_contact_id}")
        try:
            result = bot.supabase.table("core_data").insert(test_contact).execute()
            print("✅ Test contact created successfully.")
        except Exception as e:
            print(f"❌ Error creating test contact: {e}")
            return
        
        # Create test alternative contacts
        alternative_contacts = {
            "Email": "john.smith@example.com",
            "Phone": "+1234567890",
            "Facebook": "https://facebook.com/johnsmith",
            "Twitter": "https://twitter.com/johnsmith",
            "LinkedIn": "https://linkedin.com/in/johnsmith",
            "Instagram": "https://instagram.com/johnsmith",
            "Address": "123 Main St, Anytown, USA",
            "Business Hours": "Mon-Fri: 9am-5pm",
            "Contact Persons": "John Smith, Jane Doe"
        }
        
        # Set the current contact ID
        bot.current_contact_id = test_contact_id
        
        # Call the _update_alternative_contacts method
        print("\nTesting _update_alternative_contacts method...")
        try:
            bot._update_alternative_contacts(test_contact_id, alternative_contacts)
            print("✅ _update_alternative_contacts method called successfully.")
        except Exception as e:
            print(f"❌ Error calling _update_alternative_contacts method: {e}")
            return
        
        # Verify that the data was updated in Supabase
        print("\nVerifying data was updated in Supabase...")
        try:
            result = bot.supabase.table("core_data").select("*").eq("id", test_contact_id).execute()
            
            if result.data and len(result.data) > 0:
                contact = result.data[0]
                print("✅ Retrieved contact from Supabase:")
                
                # Check if enriched fields were added
                enriched_fields = {k: v for k, v in contact.items() if k.startswith("enriched_")}
                
                if enriched_fields:
                    print("✅ Enriched fields were added to the database:")
                    for field, value in enriched_fields.items():
                        print(f"  - {field}: {value}")
                    
                    # Check if the enriched_all_contacts field was added
                    if "enriched_all_contacts" in contact:
                        print("✅ enriched_all_contacts field was added successfully.")
                        try:
                            all_contacts = json.loads(contact["enriched_all_contacts"])
                            print(f"  - enriched_all_contacts: {json.dumps(all_contacts, indent=2)}")
                        except:
                            print(f"  - enriched_all_contacts: {contact['enriched_all_contacts']}")
                    else:
                        print("⚠️ enriched_all_contacts field was not added.")
                    
                    # Check if first_name and last_name were added
                    if "enriched_first_name" in contact:
                        print(f"✅ enriched_first_name field was added: {contact['enriched_first_name']}")
                    else:
                        print("⚠️ enriched_first_name field was not added.")
                    
                    if "enriched_last_name" in contact:
                        print(f"✅ enriched_last_name field was added: {contact['enriched_last_name']}")
                    else:
                        print("⚠️ enriched_last_name field was not added.")
                    
                    # Check if niche was added
                    if "enriched_niche" in contact:
                        print(f"✅ enriched_niche field was added: {contact['enriched_niche']}")
                    else:
                        print("⚠️ enriched_niche field was not added.")
                    
                    # Check for individual social media fields
                    social_media_fields = ["enriched_facebook", "enriched_twitter", "enriched_linkedin", "enriched_instagram"]
                    for field in social_media_fields:
                        if field in contact:
                            print(f"✅ {field} field was added: {contact[field]}")
                        else:
                            print(f"⚠️ {field} field was not added.")
                else:
                    print("❌ No enriched fields were added to the database.")
                    print("Contact data:", json.dumps(contact, indent=2))
            else:
                print(f"❌ Could not retrieve contact with ID {test_contact_id} from Supabase.")
        except Exception as e:
            print(f"❌ Error retrieving contact from Supabase: {e}")
        
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
