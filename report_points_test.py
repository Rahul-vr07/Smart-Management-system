#!/usr/bin/env python3
"""
Test that waste reports award 5 points correctly
"""

import requests
import time

BACKEND_URL = "https://wastesmart-app.preview.emergentagent.com/api"
TEST_USER_ID = "default_user"

def create_sample_base64_image():
    """Create a small sample base64 encoded image for testing"""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def get_user_stats():
    """Get current user stats"""
    response = requests.get(f"{BACKEND_URL}/user-stats/{TEST_USER_ID}")
    if response.status_code == 200:
        return response.json()
    return None

def create_waste_report():
    """Create a waste report"""
    test_report = {
        "user_id": TEST_USER_ID,
        "location": "Test Location for Points",
        "latitude": 40.7580,
        "longitude": -73.9855,
        "description": "Testing points awarding for waste reports",
        "image_base64": create_sample_base64_image()
    }
    response = requests.post(f"{BACKEND_URL}/reports", json=test_report)
    return response.status_code == 200

def test_report_points():
    """Test that waste reports award 5 points"""
    print("📊 Testing Waste Report Points Awarding")
    print("=" * 45)
    
    # Get initial stats
    initial_stats = get_user_stats()
    if not initial_stats:
        print("❌ Could not get initial user stats")
        return False
    
    initial_points = initial_stats.get('total_points', 0)
    print(f"Initial points: {initial_points}")
    
    # Create a waste report
    print("Creating waste report...")
    success = create_waste_report()
    if not success:
        print("❌ Failed to create waste report")
        return False
    
    # Wait for database update
    time.sleep(1)
    
    # Get updated stats
    updated_stats = get_user_stats()
    if not updated_stats:
        print("❌ Could not get updated user stats")
        return False
    
    updated_points = updated_stats.get('total_points', 0)
    points_gained = updated_points - initial_points
    
    print(f"Updated points: {updated_points}")
    print(f"Points gained: {points_gained}")
    
    # Verify 5 points were awarded
    if points_gained >= 5:
        print("✅ Waste report points PASSED - 5 points correctly awarded!")
        return True
    else:
        print(f"❌ Waste report points FAILED - Expected 5 points, got {points_gained}")
        return False

if __name__ == "__main__":
    success = test_report_points()
    exit(0 if success else 1)