#!/usr/bin/env python3
"""
Script to output the methods needed for enhanced data enrichment.
"""

def main():
    """Main function to output the methods"""
    # _check_and_create_column method
    print("\n=== _check_and_create_column Method ===")
    print("""
def _check_and_create_column(self, column_name: str) -> bool:
    \"\"\"Check if a column exists in the main table and create it if it doesn't

    Args:
        column_name: Name of the column to check/create

    Returns:
        True if the column exists or was created, False otherwise
    \"\"\"
    try:
        # Try to update a record with this column to see if it exists
        try:
            # Use a test update that will likely fail but tells us if the column exists
            self.supabase.table(TABLE_NAME).update({column_name: None}).eq("id", 0).execute()
            return True  # Column exists
        except Exception as e:
            if "column" in str(e).lower() and "does not exist" in str(e).lower():
                # Column doesn't exist, try to create it
                try:
                    sql = f"ALTER TABLE public.{TABLE_NAME} ADD COLUMN IF NOT EXISTS {column_name} TEXT;"
                    self.supabase.rpc("exec_sql", {"query": sql}).execute()
                    print(f"Created new column: {column_name}")
                    return True
                except Exception as create_error:
                    print(f"Error creating column {column_name}: {create_error}")
                    return False
            else:
                # Some other error, but column likely exists
                return True
    except Exception as e:
        print(f"Error checking/creating column {column_name}: {e}")
        return False
""")

    # _update_enriched_data_columns method
    print("\n=== _update_enriched_data_columns Method ===")
    print("""
def _update_enriched_data_columns(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
    \"\"\"Update enriched data columns directly in the main table

    Args:
        contact_id: Contact ID
        alternative_contacts: Dictionary of alternative contact methods
    \"\"\"
    try:
        print(f"Updating enriched data columns for contact {contact_id}...")

        # Try to get the record to check the structure
        sample = self.supabase.table(TABLE_NAME).select("*").eq("id", contact_id).limit(1).execute()
        if not sample.data:
            print(f"Contact {contact_id} not found in database")
            return

        columns = sample.data[0].keys()

        # Prepare update data
        update_data = {"last_updated": "now()"}

        # Store all alternative contacts in a single JSON field for easy access
        if self._check_and_create_column("enriched_all_contacts"):
            update_data["enriched_all_contacts"] = json.dumps(alternative_contacts)
            print("Added all alternative contacts to enriched_all_contacts JSON field")

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

        # Process each type of alternative contact
        for method, value in alternative_contacts.items():
            if not value:  # Skip empty values
                continue

            # Create a valid column name with enriched_ prefix
            column_name = f"enriched_{method.lower().replace(' ', '_').replace('/', '_')}"
            
            # Check if the column exists or can be created
            if self._check_and_create_column(column_name):
                update_data[column_name] = value
                print(f"Added {method} to {column_name} column")
            else:
                print(f"Could not add {method} to {column_name} column")

        # Special handling for social media platforms - create individual columns
        social_media_platforms = {
            "Facebook": alternative_contacts.get("Facebook", ""),
            "Twitter": alternative_contacts.get("Twitter", ""),
            "LinkedIn": alternative_contacts.get("LinkedIn", ""),
            "Instagram": alternative_contacts.get("Instagram", ""),
            "YouTube": alternative_contacts.get("YouTube", ""),
            "Pinterest": alternative_contacts.get("Pinterest", "")
        }
        
        for platform, url in social_media_platforms.items():
            if url:
                column_name = f"enriched_{platform.lower()}"
                if self._check_and_create_column(column_name):
                    update_data[column_name] = url
                    print(f"Added {platform} URL to {column_name} column")

        # Set a flag to indicate alternative contacts were found
        if self._check_and_create_column("alternative_contact_found"):
            update_data["alternative_contact_found"] = True
            print("Set alternative_contact_found flag to True")

        # If we have data to update, perform the update
        if len(update_data) > 1:  # More than just last_updated
            try:
                # Try to update all fields at once
                self.supabase.table(TABLE_NAME) \\
                    .update(update_data) \\
                    .eq("id", contact_id) \\
                    .execute()
                print(f"Successfully updated all enriched data columns for contact {contact_id}")
            except Exception as update_error:
                print(f"Error updating all fields at once: {update_error}")

                # Try updating one field at a time
                print("Trying to update one field at a time...")
                success_count = 0
                for key, value in update_data.items():
                    if key == "last_updated":
                        continue  # Skip the timestamp field
                    try:
                        self.supabase.table(TABLE_NAME) \\
                            .update({key: value}) \\
                            .eq("id", contact_id) \\
                            .execute()
                        success_count += 1
                        print(f"Updated {key} field individually")
                    except Exception as field_error:
                        print(f"Error updating {key} field: {field_error}")

                print(f"Updated {success_count} out of {len(update_data)-1} fields individually")
        else:
            print("No data to update for enriched columns")
    except Exception as e:
        print(f"Error updating enriched data columns: {e}")
        # Fallback to the legacy method as last resort
        print("Falling back to legacy method...")
        self._legacy_update_alternative_contacts(contact_id, alternative_contacts)
""")

    # _update_alternative_contacts method
    print("\n=== _update_alternative_contacts Method ===")
    print("""
def _update_alternative_contacts(self, contact_id: str, alternative_contacts: Dict[str, str]) -> None:
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
""")

    print("\nTo implement these changes:")
    print("1. Add the _check_and_create_column method to the ContactBot class")
    print("2. Replace the existing _update_enriched_data_columns method with the new one")
    print("3. Replace the existing _update_alternative_contacts method with the new one")
    print("4. Make sure to import json if it's not already imported")

if __name__ == "__main__":
    main()
