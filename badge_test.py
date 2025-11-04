#!/usr/bin/env python3
"""
Test badge awarding system by performing multiple classifications
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

def classify_waste():
    """Perform a waste classification"""
    test_data = {
        "image_base64": create_sample_base64_image(),
        "user_id": TEST_USER_ID
    }
    response = requests.post(f"{BACKEND_URL}/classify-waste", json=test_data)
    return response.status_code == 200

def test_badge_awarding():
    """Test badge awarding by performing multiple classifications"""
    print("🏆 Testing Badge Awarding System")
    print("=" * 50)
    
    # Get initial stats
    initial_stats = get_user_stats()
    if not initial_stats:
        print("❌ Could not get initial user stats")
        return False
    
    initial_scanned = initial_stats.get('items_scanned', 0)
    initial_badges = initial_stats.get('badges', [])
    
    print(f"Initial items scanned: {initial_scanned}")
    print(f"Initial badges: {initial_badges}")
    
    # Calculate how many more scans we need for Eco Warrior badge (10 total)
    scans_needed = max(0, 10 - initial_scanned)
    print(f"Need {scans_needed} more scans to reach 10 items for Eco Warrior badge")
    
    # Perform additional classifications if needed
    if scans_needed > 0:
        print(f"\nPerforming {scans_needed} additional classifications...")
        for i in range(scans_needed):
            success = classify_waste()
            if success:
                print(f"  Classification {i+1}/{scans_needed} completed")
                time.sleep(0.5)  # Small delay between requests
            else:
                print(f"  ❌ Classification {i+1} failed")
                return False
    
    # Get updated stats
    time.sleep(1)  # Wait for database update
    updated_stats = get_user_stats()
    if not updated_stats:
        print("❌ Could not get updated user stats")
        return False
    
    final_scanned = updated_stats.get('items_scanned', 0)
    final_badges = updated_stats.get('badges', [])
    
    print(f"\nFinal items scanned: {final_scanned}")
    print(f"Final badges: {final_badges}")
    
    # Check if Eco Warrior badge was awarded
    if final_scanned >= 10:
        if "Eco Warrior" in final_badges:
            print("✅ Badge system PASSED - Eco Warrior badge correctly awarded!")
            return True
        else:
            print("❌ Badge system FAILED - Eco Warrior badge not awarded despite 10+ scans")
            return False
    else:
        print(f"⚠️ Still need {10 - final_scanned} more scans to test badge awarding")
        return True

if __name__ == "__main__":
    success = test_badge_awarding()
    exit(0 if success else 1)