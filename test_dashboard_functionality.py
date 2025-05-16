#!/usr/bin/env python3
"""
Script to test dashboard functionality.
This script creates test events in Supabase and verifies they appear in the dashboard.
"""

import sys
import time
import uuid
import random
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64'

# Available niches for testing
NICHES = [
    'cosmetic-dentistry',
    'child-care',
    'pmu-artists',
    'sleep-apnea',
    'hearing-aid-audiology',
    'dme-clinics',
    'non-surgical-body-contouring'
]

def initialize_supabase() -> Client:
    """Initialize Supabase client."""
    try:
        print("Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Successfully connected to Supabase")
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        sys.exit(1)

def generate_test_id():
    """Generate a unique test ID to track this test run."""
    return f"test_{uuid.uuid4().hex[:8]}"

def create_test_event(supabase, test_id, event_data):
    """Create a test event in Supabase."""
    try:
        # Add test_id to event data
        event_data['test_id'] = test_id
        event_data['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        
        response = supabase.table('tctc_user_flow').insert(event_data).execute()
        
        if response.data:
            print(f"✅ Successfully created test event: {event_data['action_type']}")
            return response.data[0]['id']
        else:
            print(f"❌ Failed to create test event: {event_data['action_type']}")
            return None
    except Exception as e:
        print(f"❌ Error creating test event: {e}")
        return None

def create_test_user_journey(supabase, test_id):
    """Create a series of test events representing a user journey."""
    print("\n🧪 Creating test user journey")
    
    # Generate random user data
    user_first_name = f"Test{random.randint(1, 100)}"
    user_last_name = f"User{random.randint(1, 100)}"
    user_business_name = f"Test Business {random.randint(1, 100)}"
    niche = random.choice(NICHES)
    bucket = random.choice(['foundation', 'growth', 'scaling'])
    variant = random.choice(['a-solution', 'b-problem', 'c-most-aware'])
    split = random.randint(1, 3)
    quiz_score = random.randint(50, 100)
    
    # Common data for all events
    common_data = {
        'user_id': test_id,
        'user_first_name': user_first_name,
        'user_last_name': user_last_name,
        'user_business_name': user_business_name,
        'original_source': 'test',
        'track_source': 'dashboard_test'
    }
    
    # 1. Homepage view
    homepage_event = {
        **common_data,
        'action_type': 'page_view',
        'page_path': '/index.html',
        'page_bucket': '',
        'page_variant': '',
        'page_split': '0',
        'quiz_score': '',
        'full_url': 'http://localhost:8000/index.html'
    }
    create_test_event(supabase, test_id, homepage_event)
    
    # 2. Quiz selection page view
    quiz_selection_event = {
        **common_data,
        'action_type': 'page_view',
        'page_path': '/quiz-start.html',
        'page_bucket': '',
        'page_variant': '',
        'page_split': '0',
        'quiz_score': '',
        'full_url': 'http://localhost:8000/quiz-start.html'
    }
    create_test_event(supabase, test_id, quiz_selection_event)
    
    # 3. Quiz page view
    quiz_event = {
        **common_data,
        'action_type': 'page_view',
        'page_path': f'/niches/{niche}-quiz.html',
        'page_bucket': '',
        'page_variant': '',
        'page_split': '0',
        'quiz_score': '',
        'full_url': f'http://localhost:8000/niches/{niche}-quiz.html'
    }
    create_test_event(supabase, test_id, quiz_event)
    
    # 4. Quiz start
    quiz_start_event = {
        **common_data,
        'action_type': 'quiz_start',
        'page_path': f'/niches/{niche}-quiz.html',
        'page_bucket': '',
        'page_variant': '',
        'page_split': '0',
        'quiz_score': '',
        'full_url': f'http://localhost:8000/niches/{niche}-quiz.html'
    }
    create_test_event(supabase, test_id, quiz_start_event)
    
    # 5. Quiz completion
    quiz_completion_event = {
        **common_data,
        'action_type': 'quiz_completion',
        'page_path': f'/niches/{niche}-quiz.html',
        'page_bucket': bucket,
        'page_variant': '',
        'page_split': '0',
        'quiz_score': str(quiz_score),
        'full_url': f'http://localhost:8000/niches/{niche}-quiz.html'
    }
    create_test_event(supabase, test_id, quiz_completion_event)
    
    # 6. Results page view
    results_event = {
        **common_data,
        'action_type': 'page_view',
        'page_path': f'/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html',
        'page_bucket': bucket,
        'page_variant': variant,
        'page_split': str(split),
        'quiz_score': str(quiz_score),
        'full_url': f'http://localhost:8000/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html'
    }
    create_test_event(supabase, test_id, results_event)
    
    # 7. Application click
    application_click_event = {
        **common_data,
        'action_type': 'application_click',
        'page_path': f'/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html',
        'page_bucket': bucket,
        'page_variant': variant,
        'page_split': str(split),
        'quiz_score': str(quiz_score),
        'destination_url': 'http://localhost:8000/universal-application-form.html',
        'full_url': f'http://localhost:8000/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html'
    }
    create_test_event(supabase, test_id, application_click_event)
    
    # 8. Application page view
    application_event = {
        **common_data,
        'action_type': 'page_view',
        'page_path': '/universal-application-form.html',
        'page_bucket': bucket,
        'page_variant': variant,
        'page_split': str(split),
        'quiz_score': str(quiz_score),
        'full_url': 'http://localhost:8000/universal-application-form.html'
    }
    create_test_event(supabase, test_id, application_event)
    
    # 9. Application submission
    application_submit_event = {
        **common_data,
        'action_type': 'application_submit',
        'page_path': '/universal-application-form.html',
        'page_bucket': bucket,
        'page_variant': variant,
        'page_split': str(split),
        'quiz_score': str(quiz_score),
        'full_url': 'http://localhost:8000/universal-application-form.html'
    }
    create_test_event(supabase, test_id, application_submit_event)
    
    print(f"✅ Successfully created test user journey for {niche}/{bucket}/{variant}")
    print(f"User: {user_first_name} {user_last_name}, Business: {user_business_name}")
    print(f"Quiz Score: {quiz_score}, Split: {split}")
    
    return {
        'niche': niche,
        'bucket': bucket,
        'variant': variant,
        'split': split,
        'user_first_name': user_first_name,
        'user_last_name': user_last_name,
        'user_business_name': user_business_name
    }

def cleanup_test_events(supabase, test_id):
    """Clean up test events from Supabase."""
    try:
        response = supabase.table('tctc_user_flow').delete().eq('test_id', test_id).execute()
        
        if response.data:
            print(f"✅ Successfully cleaned up {len(response.data)} test events")
            return True
        else:
            print("⚠️ No test events were cleaned up")
            return False
    except Exception as e:
        print(f"❌ Error cleaning up test events: {e}")
        return False

def main():
    """Main function to run tests."""
    print("🚀 Starting dashboard functionality test")
    
    # Initialize Supabase client
    supabase = initialize_supabase()
    
    # Generate test ID
    test_id = generate_test_id()
    print(f"📝 Test ID: {test_id}")
    
    # Create test user journey
    journey_data = create_test_user_journey(supabase, test_id)
    
    # Prompt user to check dashboard
    print("\n🔍 Please check the dashboard to verify the test events appear")
    print(f"Dashboard URL: http://localhost:8000/tracking-dashboard/index.html")
    print("Look for the following user journey:")
    print(f"  - Niche: {journey_data['niche']}")
    print(f"  - Bucket: {journey_data['bucket']}")
    print(f"  - Variant: {journey_data['variant']}")
    print(f"  - Split: {journey_data['split']}")
    print(f"  - User: {journey_data['user_first_name']} {journey_data['user_last_name']}")
    print(f"  - Business: {journey_data['user_business_name']}")
    
    # Ask if user wants to clean up test events
    cleanup = input("\nDo you want to clean up the test events? (y/n): ")
    if cleanup.lower() == 'y':
        cleanup_test_events(supabase, test_id)
    
    print("\n✅ Testing completed")

if __name__ == "__main__":
    main()
