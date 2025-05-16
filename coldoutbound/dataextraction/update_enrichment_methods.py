#!/usr/bin/env python3
"""
Script to update the _update_enriched_data_columns and _update_alternative_contacts methods
in contact_bot.py to add support for first_name, last_name, and niche fields,
and to store data directly in the main table.
"""

import os
import sys
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to update the methods"""
    try:
        # Read the contact_bot.py file
        with open("contact_bot.py", "r", encoding="utf-8") as file:
            content = file.read()
        
        # Check if the methods exist
        if "_update_enriched_data_columns" not in content:
            print("❌ _update_enriched_data_columns method not found in contact_bot.py")
            return
        
        if "_update_alternative_contacts" not in content:
            print("❌ _update_alternative_contacts method not found in contact_bot.py")
            return
        
        # Update the _update_enriched_data_columns method
        print("Updating _update_enriched_data_columns method...")
        
        # Find the _update_enriched_data_columns method
        enriched_data_pattern = r"def _update_enriched_data_columns\(self, contact_id: str, alternative_contacts: Dict\[str, str\]\) -> None:.*?(?=\n    def )"
        enriched_data_match = re.search(enriched_data_pattern, content, re.DOTALL)
        
        if not enriched_data_match:
            print("❌ Could not find the _update_enriched_data_columns method in the expected format")
            return
        
        # Get the current method
        current_enriched_data_method = enriched_data_match.group(0)
        
        # Check if the method already has the first_name, last_name, and niche fields
        if "first_name" in current_enriched_data_method and "last_name" in current_enriched_data_method and "niche" in current_enriched_data_method:
            print("✅ _update_enriched_data_columns method already has first_name, last_name, and niche fields")
        else:
            print("Adding first_name, last_name, and niche fields to _update_enriched_data_columns method...")
            
            # Add the code to get first_name, last_name, and niche
            new_code = """
            # Get first name, last name, and niche from the main contact record
            try:
                contact_result = self.supabase.table(TABLE_NAME).select("listing_name, niche").eq("id", contact_id).execute()
                
                if contact_result.data and len(contact_result.data) > 0:
                    contact = contact_result.data[0]
                    
                    # Extract first and last name from listing_name
                    if contact.get("listing_name"):
                        name_parts = contact.get("listing_name", "").split(" ", 1)
                        first_name = name_parts[0] if len(name_parts) > 0 else ""
                        last_name = name_parts[1] if len(name_parts) > 1 else ""
                        
                        # Add first and last name to enriched data
                        if first_name and self._check_and_create_column("enriched_first_name"):
                            update_data["enriched_first_name"] = first_name
                        
                        if last_name and self._check_and_create_column("enriched_last_name"):
                            update_data["enriched_last_name"] = last_name
                    
                    # Get niche and add to enriched data
                    niche = contact.get("niche", "")
                    if niche and self._check_and_create_column("enriched_niche"):
                        update_data["enriched_niche"] = niche
            except Exception as e:
                print(f"Error getting contact details for enrichment: {e}")
            """
            
            # Find where to insert the new code
            insert_point = "# Store all alternative contacts in a single JSON field for easy access"
            if insert_point in current_enriched_data_method:
                # Insert the new code before the insert point
                new_enriched_data_method = current_enriched_data_method.replace(
                    insert_point,
                    new_code + "\n            " + insert_point
                )
                
                # Update the content
                content = content.replace(current_enriched_data_method, new_enriched_data_method)
                print("✅ Added first_name, last_name, and niche fields to _update_enriched_data_columns method")
            else:
                print("❌ Could not find the insertion point in _update_enriched_data_columns method")
        
        # Update the _update_alternative_contacts method
        print("\nUpdating _update_alternative_contacts method...")
        
        # Find the _update_alternative_contacts method
        alternative_contacts_pattern = r"def _update_alternative_contacts\(self, contact_id: str, alternative_contacts: Dict\[str, str\]\) -> None:.*?(?=\n    def )"
        alternative_contacts_match = re.search(alternative_contacts_pattern, content, re.DOTALL)
        
        if not alternative_contacts_match:
            print("❌ Could not find the _update_alternative_contacts method in the expected format")
            return
        
        # Get the current method
        current_alternative_contacts_method = alternative_contacts_match.group(0)
        
        # Create the new method
        new_alternative_contacts_method = """    def _update_alternative_contacts(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
        \"\"\"Update alternative contacts in the database

        Args:
            contact_id: Contact ID
            alternative_contacts: Dictionary of alternative contact methods
        \"\"\"
        if not self.supabase:
            print("Supabase client not initialized. Cannot update alternative contacts.")
            return

        # Use the direct method to add columns to the main table
        self._update_enriched_data_columns(contact_id, alternative_contacts)
        print("Data enrichment completed and saved directly to main table with enriched_ prefix")
"""
        
        # Update the content
        content = content.replace(current_alternative_contacts_method, new_alternative_contacts_method)
        print("✅ Updated _update_alternative_contacts method to use _update_enriched_data_columns directly")
        
        # Write the updated content back to the file
        with open("contact_bot.py", "w", encoding="utf-8") as file:
            file.write(content)
        
        print("\n✅ Successfully updated contact_bot.py")
        
    except Exception as e:
        print(f"❌ Error updating methods: {e}")

if __name__ == "__main__":
    main()
