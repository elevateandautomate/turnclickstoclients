# --- dental.py (Corrected FULL FINAL + Enhanced Supabase Error Logging) ---

# 1. IMPORTS AND SETUP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
import time
import json
import os
import traceback # For printing full tracebacks
from supabase import create_client, Client # Supabase client

# --- Supabase Configuration - YOU MUST REPLACE THESE WITH YOUR ACTUAL CREDENTIALS ---
# IMPORTANT: KEEP YOUR SERVICE_ROLE KEY SECRET!
SUPABASE_URL = "https://eumhqssfvkyuepyrtlqj.supabase.co"  # Replace with your Supabase project URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjU2MTQwMSwiZXhwIjoyMDYyMTM3NDAxfQ.hpiGyFGfFOhkbrfLNnp9uapkICXeeBY-md6QCV0C0ck" # Replace with your Supabase SERVICE_ROLE key
TABLE_NAME = "core_data" # The name of your table in Supabase (renamed from dentist)

# Initialize Supabase client
supabase: Client = None
try:
    # Check if URL and Key are provided (even if they match old placeholders)
    if SUPABASE_URL and SUPABASE_KEY: # Simplified check
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully initialized Supabase client (using provided URL and Key).")
    else:
        # This 'else' might now only trigger if one of them is an empty string or None
        print("CRITICAL: Supabase URL or Key is missing. Supabase integration will be disabled.")
        # Optionally, you might remove the next line if the URL/Key are truly the placeholder values but are intended to be used.
        # print("Please replace 'https://eumhqssfvkyuepyrtlqj.supabase.co' and 'YOUR_PLACEHOLDER_KEY' in the script.")
except Exception as e_supabase_init:
    print(f"Error initializing Supabase client: {e_supabase_init}")
    supabase = None # Ensure it's None if initialization fails

# --- General Configuration ---
TARGET_URL = "https://aacd.com/profiles?lat=40.4386612&lon=-79.99723519999999&place=Pittsburgh%2C+PA%2C+USA&radius=20000&name="
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MSEDGEDRIVER_LOG_PATH = os.path.join(BASE_DIR, 'msedgedriver.log')

# --- XPaths for Individual Profile Page ---
XPATHS_PROFILE_PAGE = {
    "dentist_name": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[1]/h1",
    "member_type": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[1]/a/p",
    "dentist_role": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[1]/div/p",
    "member_since": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[1]/div[2]/p",
    "business_name_profile": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div[2]/p",
    "business_address_full": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[3]/div[2]",
    "phone": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[4]/div[2]/p",
    "website_url": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[5]/div[2]/p/a",
    "about_us": "/html/body/div[3]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/p",
    "facebook_url": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[3]/a[1]",
    "youtube_url": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[3]/a[2]",
    "linkedin_url": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[3]/a[3]",
    "pinterest_url": "/html/body/div[3]/div[2]/div/div[1]/div[1]/div/div[3]/a[4]",
    "business_hours": "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[2]/p",
    "payment_methods": "/html/body/div[3]/div[2]/div/div[2]/div[3]/div[2]/table/tbody/tr[1]/td",
    "insurance_types": "/html/body/div[3]/div[2]/div/div[2]/div[3]/div[2]/table/tbody/tr[2]/td",
    "services_offered": "/html/body/div[3]/div[2]/div/div[2]/div[3]/div[2]/table/tbody/tr[3]/td",
}

# --- CSS Selectors for Main Search Results Page ---
SELECTOR_MEMBER_INFO_BLOCK = ".member-info"
SELECTOR_LISTING_IMAGE = ".member-image img"
SELECTOR_LISTING_NAME = ".member-name"
SELECTOR_LISTING_MEMBER_TYPES = ".member-types"
SELECTOR_LISTING_LOCATION_ALL = ".member-location"

def scrape_individual_profile(driver):
    profile_data = {}
    wait = WebDriverWait(driver, 5)
    def get_element_text(xpath_key):
        try:
            element = wait.until(EC.presence_of_element_located((By.XPATH, XPATHS_PROFILE_PAGE[xpath_key])))
            return element.text.strip() if element.text else None
        except: return None
    def get_element_href(xpath_key):
        try:
            element = wait.until(EC.presence_of_element_located((By.XPATH, XPATHS_PROFILE_PAGE[xpath_key])))
            return element.get_attribute('href')
        except: return None

    profile_data['dentist_name_profile'] = get_element_text("dentist_name")
    profile_data['member_type_profile'] = get_element_text("member_type")
    profile_data['dentist_role_profile'] = get_element_text("dentist_role")
    profile_data['member_since_profile'] = get_element_text("member_since")
    profile_data['business_name_profile_page'] = get_element_text("business_name_profile")
    profile_data['business_address_full_profile'] = get_element_text("business_address_full")
    profile_data['phone_profile'] = get_element_text("phone")
    profile_data['website_url_profile'] = get_element_href("website_url")
    profile_data['about_us_profile'] = get_element_text("about_us")
    profile_data['facebook_url_profile'] = get_element_href("facebook_url")
    profile_data['youtube_url_profile'] = get_element_href("youtube_url")
    profile_data['linkedin_url_profile'] = get_element_href("linkedin_url")
    profile_data['pinterest_url_profile'] = get_element_href("pinterest_url")
    profile_data['business_hours_profile'] = get_element_text("business_hours")
    profile_data['payment_methods_profile'] = get_element_text("payment_methods")
    profile_data['insurance_types_profile'] = get_element_text("insurance_types")
    profile_data['services_offered_profile'] = get_element_text("services_offered")
    gallery_image_urls = []
    try:
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            src = img.get_attribute('src')
            if src and '/proxy.php?file=images/findadentist/portfolio' in src:
                full_image_url = src
                if src.startswith('/proxy.php'): full_image_url = "https://aacd.com" + src
                gallery_image_urls.append(full_image_url)
    except: pass
    profile_data['gallery_image_urls'] = gallery_image_urls # Keep as list for direct JSONB compatibility
    return profile_data

def dentist_exists_in_supabase(listing_name, listing_location):
    if not supabase:
        print("DEBUG: Supabase client not initialized, cannot check existence.")
        return False
    if not listing_name or not listing_location:
        print(f"DEBUG: Insufficient info for Supabase check (name: {listing_name}, loc: {listing_location}).")
        return False

    try:
        response = supabase.table(TABLE_NAME).select("id", count='exact').eq("listing_name", listing_name).eq("listing_actual_location", listing_location).execute()
        if (hasattr(response, 'count') and response.count is not None and response.count > 0) or \
           (response.data and len(response.data) > 0) :
            return True
    except Exception as e:
        print(f"Error checking Supabase for existing dentist ('{listing_name}', '{listing_location}'): {e}")
    return False

def save_to_supabase(data_dict):
    if not supabase:
        print("DEBUG: Supabase client not initialized, cannot save data.")
        return False
    try:
        payload = data_dict.copy()
        if 'id' in payload: del payload['id']
        if 'created_at' in payload: del payload['created_at']

        # Ensure gallery_image_urls is a list (it should be from scrape_individual_profile)
        # If it was accidentally converted to JSON string earlier, this would be an issue.
        # For JSONB, a Python list of strings is fine.
        if 'gallery_image_urls' in payload and isinstance(payload['gallery_image_urls'], str):
            try:
                payload['gallery_image_urls'] = json.loads(payload['gallery_image_urls'])
            except json.JSONDecodeError:
                print(f"Warning: Could not decode gallery_image_urls string back to list for {payload.get('listing_name')}. Saving as is or as empty list.")
                # Decide handling: save original string, or empty list, or None
                # payload['gallery_image_urls'] = [] # Or None, if preferred for invalid JSON string

        print(f"DEBUG: Attempting to insert into Supabase: {payload.get('listing_name')}")
        response = supabase.table(TABLE_NAME).insert(payload).execute()
        print(f"DEBUG: Supabase insert response for {payload.get('listing_name')}: {response}")

        if response.data and len(response.data) > 0:
            print(f"Successfully saved to Supabase: {payload.get('dentist_name_profile', payload.get('listing_name'))}")
            return True
        elif hasattr(response, 'error') and response.error:
             print(f"Supabase Error saving: {response.error.message}. Code: {response.error.code}. Details: {response.error.details if hasattr(response.error, 'details') else 'N/A'}")
        elif not response.data:
             print(f"Failed to save to Supabase (no data returned, check RLS/constraints/unique violations for {payload.get('listing_name')}).")
        else:
             print(f"Unknown issue saving to Supabase for {payload.get('listing_name')}. Raw Response: {response}")

    except Exception as e: # This is the block we modified
        print(f"EXCEPTION CAUGHT in save_to_supabase for {data_dict.get('listing_name')}:")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        print("Full traceback follows:")
        traceback.print_exc()
    return False


if __name__ == "__main__":
    driver = None
    edge_service = None
    processed_count_this_session = 0
    try:
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

        try:
            edge_service = EdgeService(log_output=MSEDGEDRIVER_LOG_PATH, verbose=True)
            print(f"Attempting to start WebDriver with logging to: {MSEDGEDRIVER_LOG_PATH}")
            driver = webdriver.Edge(service=edge_service, options=edge_options)
        except Exception as service_init_error:
            print(f"Error initializing EdgeService with logging: {service_init_error}. Falling back.")
            driver = webdriver.Edge(options=edge_options)

        print("WebDriver started.")
        wait_long = WebDriverWait(driver, 15)
        print(f"Navigating to: {TARGET_URL}")
        driver.get(TARGET_URL)

        try:
            cookie_button_xpaths = [
                "//button[contains(translate(., 'ACDEFILMOPRSTUWY', 'acdefilmoprstuwy'), 'accept')]",
                "//button[contains(translate(., 'ACDEFILMOPRSTUWY', 'acdefilmoprstuwy'), 'allow')]",
                "//a[contains(translate(., 'ACDEFILMOPRSTUWY', 'acdefilmoprstuwy'), 'accept')]",
                "//a[contains(translate(., 'ACDEFILMOPRSTUWY', 'acdefilmoprstuwy'), 'allow')]"
            ]
            accepted_cookie = False
            for xpath_cookie in cookie_button_xpaths:
                try:
                    cookie_accept_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, xpath_cookie)))
                    if cookie_accept_button:
                        cookie_accept_button.click(); print(f"Clicked cookie button: {xpath_cookie}"); accepted_cookie = True; time.sleep(1); break
                except: continue
            if not accepted_cookie: print("No cookie button found/clicked.")
        except Exception as e: print(f"Cookie consent error: {e}")

        print("Starting infinite scroll...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        max_scrolls = 150; scroll_attempts = 0; profiles_found_count_on_scroll = 0; consecutive_no_new_content_scrolls = 0
        while scroll_attempts < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);"); time.sleep(2.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            current_profiles_on_page = driver.find_elements(By.CSS_SELECTOR, SELECTOR_MEMBER_INFO_BLOCK)
            new_profiles_found_count = len(current_profiles_on_page)
            if new_height == last_height: consecutive_no_new_content_scrolls += 1
            else: consecutive_no_new_content_scrolls = 0
            if consecutive_no_new_content_scrolls >= 2 and new_profiles_found_count > 10:
                print(f"Scroll end: {consecutive_no_new_content_scrolls} no-new-content scrolls. Profiles: {new_profiles_found_count}"); break
            last_height = new_height; profiles_found_count_on_scroll = new_profiles_found_count; scroll_attempts += 1
            if scroll_attempts % 10 == 0: print(f"Scroll attempt {scroll_attempts}, Profiles: {new_profiles_found_count}")
        print(f"Infinite scroll finished. Profiles on page: {profiles_found_count_on_scroll}")

        member_listings_on_search_page = driver.find_elements(By.CSS_SELECTOR, SELECTOR_MEMBER_INFO_BLOCK)
        total_listings_to_process = len(member_listings_on_search_page)
        print(f"Found {total_listings_to_process} member listings to process on page.")
        print("DEBUG: About to enter the main processing loop...")

        for i in range(total_listings_to_process):
            print(f"\nDEBUG: Top of loop for member index {i}...")
            current_dentist_data = {}
            listing_name_for_log = "Unknown (listing name not found)"
            listing_location_for_log = "Unknown (listing location not found)"

            try:
                print(f"DEBUG: Finding all member blocks for index {i}...")
                all_current_member_blocks_on_page = driver.find_elements(By.CSS_SELECTOR, SELECTOR_MEMBER_INFO_BLOCK)
                print(f"DEBUG: Found {len(all_current_member_blocks_on_page)} blocks for index {i}.")
                if i >= len(all_current_member_blocks_on_page): print(f"Error: Index {i} OOB. Skipping."); break
                member_block_to_click = all_current_member_blocks_on_page[i]
            except Exception as e: print(f"Crit error finding block {i+1}: {e}. Skipping."); continue

            try:
                listing_name_for_log = member_block_to_click.find_element(By.CSS_SELECTOR, SELECTOR_LISTING_NAME).text.strip()
                current_dentist_data['listing_name'] = listing_name_for_log

                locations = member_block_to_click.find_elements(By.CSS_SELECTOR, SELECTOR_LISTING_LOCATION_ALL)
                if len(locations) > 0:
                    listing_location_for_log = locations[0].text.strip()
                    current_dentist_data['listing_actual_location'] = listing_location_for_log
                if len(locations) > 1:
                    current_dentist_data['listing_business_name'] = locations[1].text.strip()

                try:
                    img_src = member_block_to_click.find_element(By.CSS_SELECTOR, SELECTOR_LISTING_IMAGE).get_attribute('src')
                    current_dentist_data['listing_image_url'] = "https://aacd.com" + img_src if img_src and img_src.startswith('/') else img_src
                except: current_dentist_data['listing_image_url'] = None
                try:
                    current_dentist_data['listing_member_types'] = member_block_to_click.find_element(By.CSS_SELECTOR, SELECTOR_LISTING_MEMBER_TYPES).text.strip()
                except: current_dentist_data['listing_member_types'] = None

            except Exception as e_listing:
                print(f"Warning: Could not get listing name/location for index {i}: {e_listing}.")
                current_dentist_data.setdefault('listing_name', None)
                current_dentist_data.setdefault('listing_actual_location', None)


            if supabase and current_dentist_data.get('listing_name') and current_dentist_data.get('listing_actual_location'):
                print(f"DEBUG: Checking Supabase for: '{current_dentist_data['listing_name']}' at '{current_dentist_data['listing_actual_location']}'")
                if dentist_exists_in_supabase(current_dentist_data['listing_name'], current_dentist_data['listing_actual_location']):
                    print(f"INFO: '{current_dentist_data['listing_name']}' at '{current_dentist_data['listing_actual_location']}' already in Supabase. Skipping.")
                    continue
                else:
                    print(f"INFO: '{current_dentist_data['listing_name']}' at '{current_dentist_data['listing_actual_location']}' not in Supabase. Scraping.")
            elif not supabase:
                 print("DEBUG: Supabase client not available. Cannot check for existing record.")
            else:
                 print(f"DEBUG: Insufficient listing info for Supabase check for index {i} (Name: {current_dentist_data.get('listing_name')}, Loc: {current_dentist_data.get('listing_actual_location')}). Proceeding to scrape details.")


            try:
                print(f"DEBUG: Attempting to click profile for: {listing_name_for_log}")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", member_block_to_click)
                time.sleep(0.25); driver.execute_script("arguments[0].click();", member_block_to_click)
                print(f"DEBUG: Click executed for: {listing_name_for_log}")
                print(f"DEBUG: Waiting for dentist name on profile for: {listing_name_for_log}")
                wait_long.until(EC.presence_of_element_located((By.XPATH, XPATHS_PROFILE_PAGE["dentist_name"])))
                print(f"DEBUG: Profile page loaded for: {listing_name_for_log}")

                detailed_profile_info = scrape_individual_profile(driver)
                for key, value in detailed_profile_info.items():
                    current_dentist_data[key] = value

                if supabase:
                    if not current_dentist_data.get('listing_name') or not current_dentist_data.get('listing_actual_location'):
                        print(f"CRITICAL: Missing listing_name or listing_actual_location before Supabase save for what should be '{listing_name_for_log}'. Data: {current_dentist_data}")
                    elif save_to_supabase(current_dentist_data):
                        processed_count_this_session += 1
                else:
                    print("Warning: Supabase not configured. Data for this dentist not saved to DB.")

                final_name_for_log = current_dentist_data.get('dentist_name_profile', listing_name_for_log)
                if (processed_count_this_session > 0 and processed_count_this_session % 10 == 0) or i == total_listings_to_process -1 :
                     print(f"Data processed for dentist {i+1} (Total this session: {processed_count_this_session}): {final_name_for_log}")

            except Exception as e_scrape_detail:
                print(f"Error clicking or scraping profile for member {i+1} ({listing_name_for_log}): {e_scrape_detail}")
                if TARGET_URL not in driver.current_url:
                    print("Attempting to navigate to main listings page after error during profile scrape...")
                    try: driver.get(TARGET_URL); time.sleep(2.5)
                    except Exception as e_nav: print(f"Failed to navigate to TARGET_URL: {e_nav}")
                continue

            try:
                if TARGET_URL not in driver.current_url:
                    print(f"DEBUG: Attempting to navigate back from profile of: {listing_name_for_log}")
                    time.sleep(0.25); driver.back(); print(f"DEBUG: driver.back() executed. Waiting for main list...")
                    wait_long.until(EC.presence_of_element_located((By.CSS_SELECTOR, SELECTOR_MEMBER_INFO_BLOCK)))
                    print(f"DEBUG: Main list elements found after driver.back()."); time.sleep(0.75)
            except Exception as e_back:
                print(f"Error navigating back for member {i+1} ({listing_name_for_log}): {e_back}. Reloading main page.")
                try:
                    print(f"Trying to reload TARGET_URL after driver.back() failure for member {i+1}.")
                    driver.get(TARGET_URL); time.sleep(3)
                    print("Main page reloaded. Continuing (scroll may be lost).")
                    continue
                except Exception as e_reload:
                    print(f"FATAL: Failed to reload main page after back() error: {e_reload}. Exiting loop.")
                    traceback.print_exc(); break

        print(f"\nLoop finished. Total dentists processed in this session and attempted to save to Supabase: {processed_count_this_session}")

    except Exception as e_main:
        print(f"An unexpected error occurred in the main script: {e_main}")
        traceback.print_exc()

    finally:
        print("\n--- SCRIPT SHUTDOWN ---")
        print(f"Total dentists processed in this session and attempted for Supabase: {processed_count_this_session}")
        if driver:
            print("Closing WebDriver.")
            try: driver.quit()
            except Exception as e_quit: print(f"Error during driver.quit(): {e_quit}")
        print("Script finished.")