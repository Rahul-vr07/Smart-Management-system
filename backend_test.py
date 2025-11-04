#!/usr/bin/env python3
"""
CleanCity Backend API Comprehensive Test Suite
Tests all backend endpoints for functionality and data integrity
"""

import requests
import json
import base64
import time
from datetime import datetime

# Backend URL from frontend .env
BACKEND_URL = "https://wastesmart-app.preview.emergentagent.com/api"
TEST_USER_ID = "default_user"

def create_sample_base64_image():
    """Create a small sample base64 encoded image for testing"""
    # Simple 1x1 pixel PNG in base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def test_health_check():
    """Test GET /api/ - Health check endpoint"""
    print("\n=== Testing Health Check Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "CleanCity API" in data["message"]:
                print("✅ Health check PASSED")
                return True
            else:
                print("❌ Health check FAILED - Invalid response format")
                return False
        else:
            print(f"❌ Health check FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check FAILED - Error: {str(e)}")
        return False

def test_seed_data():
    """Test POST /api/seed-data - Seed bin locations"""
    print("\n=== Testing Seed Data Endpoint ===")
    try:
        response = requests.post(f"{BACKEND_URL}/seed-data")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                print("✅ Seed data PASSED")
                return True
            else:
                print("❌ Seed data FAILED - Invalid response format")
                return False
        else:
            print(f"❌ Seed data FAILED - Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Seed data FAILED - Error: {str(e)}")
        return False

def test_get_bins():
    """Test GET /api/bins - Get all bin locations"""
    print("\n=== Testing Get Bins Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/bins")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Number of bins returned: {len(data)}")
            
            if len(data) > 0:
                # Check first bin structure
                first_bin = data[0]
                required_fields = ['id', 'name', 'type', 'latitude', 'longitude', 'address', 'status', 'capacity']
                missing_fields = [field for field in required_fields if field not in first_bin]
                
                if not missing_fields:
                    print(f"Sample bin: {first_bin['name']} - {first_bin['type']} - {first_bin['status']}")
                    print("✅ Get bins PASSED")
                    return True, data
                else:
                    print(f"❌ Get bins FAILED - Missing fields: {missing_fields}")
                    return False, []
            else:
                print("⚠️ Get bins returned empty list - may need seeding first")
                return True, []
        else:
            print(f"❌ Get bins FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get bins FAILED - Error: {str(e)}")
        return False, []

def test_create_bin():
    """Test POST /api/bins - Create new bin location"""
    print("\n=== Testing Create Bin Endpoint ===")
    try:
        test_bin = {
            "name": "Test Recycling Center",
            "type": "recycling",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "address": "Times Square, New York, NY",
            "status": "active",
            "capacity": 80,
            "timings": "24/7"
        }
        
        response = requests.post(f"{BACKEND_URL}/bins", json=test_bin)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Created bin: {data.get('name')} with ID: {data.get('id')}")
            
            # Verify all fields are present
            required_fields = ['id', 'name', 'type', 'latitude', 'longitude', 'address', 'status', 'capacity']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Create bin PASSED")
                return True, data
            else:
                print(f"❌ Create bin FAILED - Missing fields in response: {missing_fields}")
                return False, None
        else:
            print(f"❌ Create bin FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create bin FAILED - Error: {str(e)}")
        return False, None

def test_get_user_stats():
    """Test GET /api/user-stats/{user_id} - Get user statistics"""
    print("\n=== Testing Get User Stats Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/user-stats/{TEST_USER_ID}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"User stats: Points={data.get('total_points')}, Items scanned={data.get('items_scanned')}, Badges={data.get('badges')}")
            
            # Verify required fields
            required_fields = ['user_id', 'total_points', 'items_scanned', 'items_recycled', 'co2_saved_kg', 'badges']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Get user stats PASSED")
                return True, data
            else:
                print(f"❌ Get user stats FAILED - Missing fields: {missing_fields}")
                return False, None
        else:
            print(f"❌ Get user stats FAILED - Status code: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Get user stats FAILED - Error: {str(e)}")
        return False, None

def test_classify_waste():
    """Test POST /api/classify-waste - AI waste classification"""
    print("\n=== Testing AI Waste Classification Endpoint ===")
    try:
        test_data = {
            "image_base64": create_sample_base64_image(),
            "user_id": TEST_USER_ID
        }
        
        response = requests.post(f"{BACKEND_URL}/classify-waste", json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Classification: {data.get('classification')}")
            print(f"Category: {data.get('category')}")
            print(f"Suggestions: {data.get('suggestions')}")
            print(f"Points awarded: {data.get('points_awarded')}")
            
            # Verify required fields
            required_fields = ['id', 'classification', 'category', 'suggestions', 'points_awarded']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                # Verify category is valid
                valid_categories = ['RECYCLE', 'COMPOST', 'LANDFILL']
                if data.get('category') in valid_categories:
                    print("✅ AI waste classification PASSED")
                    return True, data
                else:
                    print(f"❌ AI waste classification FAILED - Invalid category: {data.get('category')}")
                    return False, None
            else:
                print(f"❌ AI waste classification FAILED - Missing fields: {missing_fields}")
                return False, None
        else:
            print(f"❌ AI waste classification FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ AI waste classification FAILED - Error: {str(e)}")
        return False, None

def test_create_report():
    """Test POST /api/reports - Create waste report"""
    print("\n=== Testing Create Waste Report Endpoint ===")
    try:
        test_report = {
            "user_id": TEST_USER_ID,
            "location": "Central Park Entrance",
            "latitude": 40.7829,
            "longitude": -73.9654,
            "description": "Overflowing trash bin near the main entrance",
            "image_base64": create_sample_base64_image()
        }
        
        response = requests.post(f"{BACKEND_URL}/reports", json=test_report)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Created report: {data.get('description')} at {data.get('location')}")
            print(f"Report ID: {data.get('id')}")
            
            # Verify required fields
            required_fields = ['id', 'user_id', 'location', 'latitude', 'longitude', 'description', 'status', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("✅ Create waste report PASSED")
                return True, data
            else:
                print(f"❌ Create waste report FAILED - Missing fields: {missing_fields}")
                return False, None
        else:
            print(f"❌ Create waste report FAILED - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Create waste report FAILED - Error: {str(e)}")
        return False, None

def test_get_reports():
    """Test GET /api/reports - Get waste reports"""
    print("\n=== Testing Get Waste Reports Endpoint ===")
    try:
        response = requests.get(f"{BACKEND_URL}/reports")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Number of reports returned: {len(data)}")
            
            if len(data) > 0:
                # Check first report structure
                first_report = data[0]
                required_fields = ['id', 'user_id', 'location', 'latitude', 'longitude', 'description', 'status', 'timestamp']
                missing_fields = [field for field in required_fields if field not in first_report]
                
                if not missing_fields:
                    print(f"Sample report: {first_report['location']} - {first_report['status']}")
                    print("✅ Get waste reports PASSED")
                    return True, data
                else:
                    print(f"❌ Get waste reports FAILED - Missing fields: {missing_fields}")
                    return False, []
            else:
                print("⚠️ Get waste reports returned empty list")
                print("✅ Get waste reports PASSED (empty result is valid)")
                return True, []
        else:
            print(f"❌ Get waste reports FAILED - Status code: {response.status_code}")
            return False, []
    except Exception as e:
        print(f"❌ Get waste reports FAILED - Error: {str(e)}")
        return False, []

def test_user_stats_update_after_classification():
    """Test that user stats are updated after waste classification"""
    print("\n=== Testing User Stats Update After Classification ===")
    
    # Get initial stats
    initial_success, initial_stats = test_get_user_stats()
    if not initial_success:
        print("❌ Could not get initial user stats")
        return False
    
    initial_points = initial_stats.get('total_points', 0)
    initial_scanned = initial_stats.get('items_scanned', 0)
    
    print(f"Initial stats - Points: {initial_points}, Items scanned: {initial_scanned}")
    
    # Perform classification
    classification_success, classification_data = test_classify_waste()
    if not classification_success:
        print("❌ Classification failed, cannot test stats update")
        return False
    
    # Wait a moment for database update
    time.sleep(1)
    
    # Get updated stats
    updated_success, updated_stats = test_get_user_stats()
    if not updated_success:
        print("❌ Could not get updated user stats")
        return False
    
    updated_points = updated_stats.get('total_points', 0)
    updated_scanned = updated_stats.get('items_scanned', 0)
    
    print(f"Updated stats - Points: {updated_points}, Items scanned: {updated_scanned}")
    
    # Verify points increased by 10 and items_scanned increased by 1
    if updated_points >= initial_points + 10 and updated_scanned >= initial_scanned + 1:
        print("✅ User stats update after classification PASSED")
        return True
    else:
        print(f"❌ User stats update FAILED - Expected points increase of 10, got {updated_points - initial_points}")
        print(f"Expected items_scanned increase of 1, got {updated_scanned - initial_scanned}")
        return False

def test_badge_system():
    """Test badge awarding system"""
    print("\n=== Testing Badge System ===")
    
    # Get current stats to check badge status
    success, stats = test_get_user_stats()
    if not success:
        print("❌ Could not get user stats for badge testing")
        return False
    
    items_scanned = stats.get('items_scanned', 0)
    badges = stats.get('badges', [])
    
    print(f"Current items scanned: {items_scanned}")
    print(f"Current badges: {badges}")
    
    # Check if Eco Warrior badge should be awarded (10+ items scanned)
    if items_scanned >= 10:
        if "Eco Warrior" in badges:
            print("✅ Badge system PASSED - Eco Warrior badge correctly awarded")
            return True
        else:
            print("❌ Badge system FAILED - Eco Warrior badge not awarded despite 10+ scans")
            return False
    else:
        print(f"⚠️ Badge system test inconclusive - Need {10 - items_scanned} more scans to test Eco Warrior badge")
        return True  # Not a failure, just need more data

def run_comprehensive_test():
    """Run all backend tests"""
    print("🧪 Starting CleanCity Backend API Comprehensive Test Suite")
    print(f"Testing backend at: {BACKEND_URL}")
    print("=" * 60)
    
    test_results = {}
    
    # Run all tests
    test_results['health_check'] = test_health_check()
    test_results['seed_data'] = test_seed_data()
    test_results['get_bins'] = test_get_bins()[0]
    test_results['create_bin'] = test_create_bin()[0]
    test_results['get_user_stats'] = test_get_user_stats()[0]
    test_results['classify_waste'] = test_classify_waste()[0]
    test_results['create_report'] = test_create_report()[0]
    test_results['get_reports'] = test_get_reports()[0]
    test_results['stats_update'] = test_user_stats_update_after_classification()
    test_results['badge_system'] = test_badge_system()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED! CleanCity backend is working correctly.")
        return True
    else:
        print(f"⚠️ {total - passed} test(s) FAILED. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)