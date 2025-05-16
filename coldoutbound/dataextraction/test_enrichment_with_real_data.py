#!/usr/bin/env python3
"""
Script to test the enrichment functionality with real data from the database.
This script will:
1. Connect to Supabase
2. Get a sample of real contacts from the core_data table
3. Simulate finding alternative contact information
4. Update the contacts with the enriched data
5. Verify that the data was properly stored in the database
"""

import os
import sys
import json
import random
from typing import Dict, Any, List
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
    """Main function to test the enrichment functionality with real data"""
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
        
        # Get a sample of real contacts from the core_data table
        print("\nGetting a sample of real contacts from the core_data table...")
        try:
            result = bot.supabase.table("core_data").select("id, listing_name, niche, website_url_profile").limit(5).execute()
            
            if result.data and len(result.data) > 0:
                contacts = result.data
                print(f"✅ Retrieved {len(contacts)} contacts from the core_data table.")
                
                # Process each contact
                for contact in contacts:
                    contact_id = contact.get("id")
                    listing_name = contact.get("listing_name", "")
                    niche = contact.get("niche", "")
                    website_url = contact.get("website_url_profile", "")
                    
                    print(f"\nProcessing contact: {listing_name} (ID: {contact_id})")
                    print(f"  Niche: {niche}")
                    print(f"  Website: {website_url}")
                    
                    # Generate simulated alternative contact information
                    alternative_contacts = generate_simulated_contact_info(listing_name, niche)
                    
                    print(f"Generated simulated alternative contact information:")
                    for method, value in alternative_contacts.items():
                        print(f"  - {method}: {value}")
                    
                    # Set the current contact ID
                    bot.current_contact_id = contact_id
                    
                    # Call the _update_alternative_contacts method
                    print(f"Updating contact {contact_id} with enriched data...")
                    try:
                        bot._update_alternative_contacts(contact_id, alternative_contacts)
                        print(f"✅ Successfully updated contact {contact_id} with enriched data.")
                        
                        # Verify that the data was properly stored in the database
                        print(f"Verifying data was updated in Supabase...")
                        verify_result = bot.supabase.table("core_data").select("*").eq("id", contact_id).execute()
                        
                        if verify_result.data and len(verify_result.data) > 0:
                            updated_contact = verify_result.data[0]
                            
                            # Check if enriched fields were added
                            enriched_fields = {k: v for k, v in updated_contact.items() if k.startswith("enriched_")}
                            
                            if enriched_fields:
                                print(f"✅ Enriched fields were added to the database for contact {contact_id}:")
                                for field, value in enriched_fields.items():
                                    print(f"  - {field}: {value}")
                            else:
                                print(f"❌ No enriched fields were added to the database for contact {contact_id}.")
                        else:
                            print(f"❌ Could not retrieve updated contact {contact_id} from Supabase.")
                    except Exception as e:
                        print(f"❌ Error updating contact {contact_id} with enriched data: {e}")
            else:
                print("❌ No contacts found in the core_data table.")
        except Exception as e:
            print(f"❌ Error retrieving contacts from the core_data table: {e}")
    
    finally:
        # Close the browser
        print("\nClosing the browser...")
        bot.close()
        print("✅ Browser closed.")

def generate_simulated_contact_info(name: str, niche: str) -> Dict[str, str]:
    """Generate simulated alternative contact information
    
    Args:
        name: The name of the contact
        niche: The niche of the contact
        
    Returns:
        Dictionary of simulated alternative contact methods
    """
    # Parse name into first and last name
    name_parts = name.split() if name else ["John", "Doe"]
    first_name = name_parts[0] if name_parts else "John"
    last_name = name_parts[-1] if len(name_parts) > 1 else "Doe"
    
    # Generate a domain name based on the name
    domain = f"{first_name.lower()}{last_name.lower()}.com"
    
    # Generate simulated alternative contact information
    alternative_contacts = {
        "Email": f"{first_name.lower()}.{last_name.lower()}@{domain}",
        "Phone": f"+1{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}",
        "Facebook": f"https://facebook.com/{first_name.lower()}.{last_name.lower()}",
        "Twitter": f"https://twitter.com/{first_name.lower()}{last_name.lower()}",
        "LinkedIn": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{niche.lower().replace(' ', '-')}",
        "Instagram": f"https://instagram.com/{first_name.lower()}.{last_name.lower()}",
        "Address": f"{random.randint(100, 999)} Main St, {random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'])}, {random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'])} {random.randint(10000, 99999)}",
        "Business Hours": f"Mon-Fri: {random.choice(['8am', '9am', '10am'])}-{random.choice(['5pm', '6pm', '7pm'])}",
        "Contact Persons": f"{first_name} {last_name}, {random.choice(['Jane', 'John', 'Mary', 'David', 'Sarah'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Jones', 'Brown'])}"
    }
    
    return alternative_contacts

if __name__ == "__main__":
    main()
