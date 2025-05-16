#!/usr/bin/env python3
"""
Script to test Supabase tracking integration.
This script verifies that tracking events are correctly recorded in Supabase.
"""

import os
import sys
import time
import json
import uuid
import random
import requests
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = 'https://eumhqssfvkyuepyrtlqj.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1bWhxc3Nmdmt5dWVweXJ0bHFqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY1NjE0MDEsImV4cCI6MjA2MjEzNzQwMX0.w-UzQq1G6GIinBdlIcW34KBSoeaAK-knNs4AvL8ct64'

# Base URL for the website (update with your actual domain when deployed)
BASE_URL = 'http://localhost'  # Change to your actual domain when deployed

# Available niches for testing
NICHES = [
    'cosmetic-dentistry',
    'child-care',
    'pmu-artists',
    'weight-loss-clinics',
    'high-end-chiropractors',
    'sleep-apnea',
    'hearing-aid-audiology',
    'dme-clinics',
    'non-surgical-body-contouring'
]

def initialize_supabase() -> Client:
    """Initialize Supabase client."""
    try:
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

def verify_event_exists(supabase, event_id):
    """Verify that an event exists in Supabase."""
    try:
        response = supabase.table('tctc_user_flow').select('*').eq('id', event_id).execute()
        
        if response.data:
            print(f"✅ Successfully verified event exists: {event_id}")
            return True
        else:
            print(f"❌ Failed to verify event exists: {event_id}")
            return False
    except Exception as e:
        print(f"❌ Error verifying event: {e}")
        return False

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

def test_page_view_tracking(supabase, test_id):
    """Test page view tracking."""
    print("\n🧪 Testing page view tracking")
    
    # Create test event
    event_data = {
        'action_type': 'page_view',
        'page_path': '/test/page',
        'page_bucket': 'foundation',
        'page_variant': 'a-solution',
        'page_split': '1',
        'user_first_name': 'Test',
        'user_last_name': 'User',
        'user_business_name': 'Test Business',
        'original_source': 'test',
        'track_source': 'testing',
        'quiz_score': '75',
        'full_url': f"{BASE_URL}/test/page?test_id={test_id}"
    }
    
    event_id = create_test_event(supabase, test_id, event_data)
    
    if event_id:
        # Verify event exists
        return verify_event_exists(supabase, event_id)
    else:
        return False

def test_application_click_tracking(supabase, test_id):
    """Test application click tracking."""
    print("\n🧪 Testing application click tracking")
    
    # Create test event
    event_data = {
        'action_type': 'application_click',
        'page_path': '/test/results',
        'page_bucket': 'foundation',
        'page_variant': 'a-solution',
        'page_split': '1',
        'user_first_name': 'Test',
        'user_last_name': 'User',
        'user_business_name': 'Test Business',
        'original_source': 'test',
        'track_source': 'testing',
        'quiz_score': '75',
        'destination_url': f"{BASE_URL}/application?test_id={test_id}"
    }
    
    event_id = create_test_event(supabase, test_id, event_data)
    
    if event_id:
        # Verify event exists
        return verify_event_exists(supabase, event_id)
    else:
        return False

def test_application_submit_tracking(supabase, test_id):
    """Test application submission tracking."""
    print("\n🧪 Testing application submission tracking")
    
    # Create test event
    event_data = {
        'action_type': 'application_submit',
        'page_path': '/application',
        'page_bucket': 'foundation',
        'page_variant': 'a-solution',
        'page_split': '1',
        'user_first_name': 'Test',
        'user_last_name': 'User',
        'user_business_name': 'Test Business',
        'original_source': 'test',
        'track_source': 'testing',
        'quiz_score': '75',
        'application_data': json.dumps({
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '555-123-4567',
            'business_name': 'Test Business',
            'niche': random.choice(NICHES)
        })
    }
    
    event_id = create_test_event(supabase, test_id, event_data)
    
    if event_id:
        # Verify event exists
        return verify_event_exists(supabase, event_id)
    else:
        return False

def test_chat_interaction_tracking(supabase, test_id):
    """Test chat interaction tracking."""
    print("\n🧪 Testing chat interaction tracking")
    
    # Create test event
    event_data = {
        'action_type': 'chat_open',
        'page_path': '/test/results',
        'page_bucket': 'foundation',
        'page_variant': 'a-solution',
        'page_split': '1',
        'user_first_name': 'Test',
        'user_last_name': 'User',
        'user_business_name': 'Test Business',
        'original_source': 'test',
        'track_source': 'testing',
        'quiz_score': '75'
    }
    
    event_id = create_test_event(supabase, test_id, event_data)
    
    if event_id:
        # Verify event exists
        return verify_event_exists(supabase, event_id)
    else:
        return False

def test_query_functionality(supabase, test_id):
    """Test query functionality for tracking data."""
    print("\n🧪 Testing query functionality")
    
    try:
        # Query by test_id
        response = supabase.table('tctc_user_flow').select('*').eq('test_id', test_id).execute()
        
        if response.data:
            print(f"✅ Successfully queried {len(response.data)} test events")
            
            # Test filtering by action_type
            action_response = supabase.table('tctc_user_flow') \
                .select('*') \
                .eq('test_id', test_id) \
                .eq('action_type', 'page_view') \
                .execute()
            
            if action_response.data:
                print(f"✅ Successfully filtered by action_type: {len(action_response.data)} events")
            else:
                print("❌ Failed to filter by action_type")
            
            return True
        else:
            print("❌ Failed to query test events")
            return False
    except Exception as e:
        print(f"❌ Error querying test events: {e}")
        return False

def main():
    """Main function to run tests."""
    print("🚀 Starting Supabase tracking integration tests")
    
    # Initialize Supabase
    supabase = initialize_supabase()
    
    # Generate test ID
    test_id = generate_test_id()
    print(f"📝 Test ID: {test_id}")
    
    # Run tests
    results = {}
    
    # Test page view tracking
    results['page_view'] = test_page_view_tracking(supabase, test_id)
    
    # Test application click tracking
    results['application_click'] = test_application_click_tracking(supabase, test_id)
    
    # Test application submission tracking
    results['application_submit'] = test_application_submit_tracking(supabase, test_id)
    
    # Test chat interaction tracking
    results['chat_interaction'] = test_chat_interaction_tracking(supabase, test_id)
    
    # Test query functionality
    results['query'] = test_query_functionality(supabase, test_id)
    
    # Clean up test events
    cleanup_test_events(supabase, test_id)
    
    # Summary
    print("\n📊 Test Summary:")
    for test, result in results.items():
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{status}: {test}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n⚠️ Some tests failed!")
    
    print("\n✅ Testing completed")

if __name__ == "__main__":
    main()
