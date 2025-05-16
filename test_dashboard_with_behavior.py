#!/usr/bin/env python3
"""
Script to test dashboard functionality using the tctc_user_behavior table.
This script creates test events in Supabase and verifies they appear in the dashboard.
"""

import sys
import time
import uuid
import random
import json
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
        response = supabase.table('tctc_user_behavior').insert(event_data).execute()
        
        if response.data:
            print(f"✅ Successfully created test event: {event_data['event_type']}")
            return response.data[0]['id']
        else:
            print(f"❌ Failed to create test event: {event_data['event_type']}")
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
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    flow_hash = f"flow_{uuid.uuid4().hex[:8]}"
    
    # Common data for all events
    common_data = {
        'user_id': test_id,
        'session_id': session_id,
        'flow_hash': flow_hash,
        'user_first_name': user_first_name,
        'user_last_name': user_last_name,
        'user_business_name': user_business_name,
        'traffic_source': 'test',
        'utm_medium': 'dashboard_test',
        'utm_campaign': 'testing',
        'user_agent': 'Python Test Script',
        'screen_width': 1920,
        'screen_height': 1080,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    
    # 1. Homepage view
    homepage_event = {
        **common_data,
        'event_type': 'page_view',
        'page_type': 'homepage',
        'niche': '',
        'bucket': '',
        'variant': '',
        'event_data': json.dumps({
            'page_url': 'http://localhost:8000/index.html',
            'referrer': ''
        })
    }
    create_test_event(supabase, test_id, homepage_event)
    
    # 2. Quiz selection page view
    quiz_selection_event = {
        **common_data,
        'event_type': 'page_view',
        'page_type': 'quiz_selection',
        'niche': '',
        'bucket': '',
        'variant': '',
        'event_data': json.dumps({
            'page_url': 'http://localhost:8000/quiz-start.html',
            'referrer': 'http://localhost:8000/index.html'
        })
    }
    create_test_event(supabase, test_id, quiz_selection_event)
    
    # 3. Quiz page view
    quiz_event = {
        **common_data,
        'event_type': 'page_view',
        'page_type': 'quiz',
        'niche': niche,
        'bucket': '',
        'variant': '',
        'event_data': json.dumps({
            'page_url': f'http://localhost:8000/niches/{niche}-quiz.html',
            'referrer': 'http://localhost:8000/quiz-start.html'
        })
    }
    create_test_event(supabase, test_id, quiz_event)
    
    # 4. Quiz start
    quiz_start_event = {
        **common_data,
        'event_type': 'quiz_start',
        'page_type': 'quiz',
        'niche': niche,
        'bucket': '',
        'variant': '',
        'event_data': json.dumps({
            'page_url': f'http://localhost:8000/niches/{niche}-quiz.html',
            'quiz_id': niche
        })
    }
    create_test_event(supabase, test_id, quiz_start_event)
    
    # 5. Quiz completion
    quiz_completion_event = {
        **common_data,
        'event_type': 'quiz_completion',
        'page_type': 'quiz',
        'niche': niche,
        'bucket': bucket,
        'variant': '',
        'event_data': json.dumps({
            'page_url': f'http://localhost:8000/niches/{niche}-quiz.html',
            'quiz_id': niche,
            'score': quiz_score,
            'bucket': bucket
        })
    }
    create_test_event(supabase, test_id, quiz_completion_event)
    
    # 6. Results page view
    results_event = {
        **common_data,
        'event_type': 'page_view',
        'page_type': 'results',
        'niche': niche,
        'bucket': bucket,
        'variant': variant,
        'event_data': json.dumps({
            'page_url': f'http://localhost:8000/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html',
            'referrer': f'http://localhost:8000/niches/{niche}-quiz.html',
            'split': split,
            'score': quiz_score
        })
    }
    create_test_event(supabase, test_id, results_event)
    
    # 7. Application click
    application_click_event = {
        **common_data,
        'event_type': 'application_click',
        'page_type': 'results',
        'niche': niche,
        'bucket': bucket,
        'variant': variant,
        'event_data': json.dumps({
            'page_url': f'http://localhost:8000/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html',
            'destination_url': 'http://localhost:8000/universal-application-form.html',
            'split': split,
            'score': quiz_score
        })
    }
    create_test_event(supabase, test_id, application_click_event)
    
    # 8. Application page view
    application_event = {
        **common_data,
        'event_type': 'page_view',
        'page_type': 'application',
        'niche': niche,
        'bucket': bucket,
        'variant': variant,
        'event_data': json.dumps({
            'page_url': 'http://localhost:8000/universal-application-form.html',
            'referrer': f'http://localhost:8000/quiz-applications/{niche}/{bucket}/{bucket}-variant-{variant}.html',
            'split': split,
            'score': quiz_score
        })
    }
    create_test_event(supabase, test_id, application_event)
    
    # 9. Application submission
    application_submit_event = {
        **common_data,
        'event_type': 'application_submit',
        'page_type': 'application',
        'niche': niche,
        'bucket': bucket,
        'variant': variant,
        'event_data': json.dumps({
            'page_url': 'http://localhost:8000/universal-application-form.html',
            'split': split,
            'score': quiz_score,
            'form_data': {
                'name': f"{user_first_name} {user_last_name}",
                'business_name': user_business_name,
                'email': f"{user_first_name.lower()}.{user_last_name.lower()}@example.com",
                'phone': f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            }
        })
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
        'user_business_name': user_business_name,
        'user_id': test_id
    }

def cleanup_test_events(supabase, user_id):
    """Clean up test events from Supabase."""
    try:
        response = supabase.table('tctc_user_behavior').delete().eq('user_id', user_id).execute()
        
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
        cleanup_test_events(supabase, journey_data['user_id'])
    
    print("\n✅ Testing completed")

if __name__ == "__main__":
    main()
