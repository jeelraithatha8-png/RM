"""
API Test Suite for Nest & Found Backend.
Tests user registration, login, profile fetching, and match discovery.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"


def test_api():
    print("🚀 Starting API Test Suite for Nest & Found...")
    
    # 1. Test User Registration
    print("\n--- 1. Registering Users ---")
    user1_data = {
        "email": "user1@example.com",
        "name": "Alice",
        "age": 22,
        "password": "password123",
        "preferences": {
            "sleep_pref": "Morning",
            "guest_policy": "No Guests",
            "noise_tolerance": "Quiet"
        }
    }
    user2_data = {
        "email": "user2@example.com",
        "name": "Bobbie",
        "age": 23,
        "password": "password123",
        "preferences": {
            "sleep_pref": "Morning",
            "guest_policy": "No Guests",
            "noise_tolerance": "Quiet"
        }
    }
    
    res1 = requests.post(f"{BASE_URL}/auth/register", json=user1_data)
    res2 = requests.post(f"{BASE_URL}/auth/register", json=user2_data)
    
    print("User 1 Register Status:", res1.status_code)
    print("User 2 Register Status:", res2.status_code)
    
    if res1.status_code != 201:
        print("Registration failed. Exiting.")
        return

    # 2. Test Login
    print("\n--- 2. Logging in User 1 ---")
    login_data = {"username": "user1@example.com", "password": "password123"}
    res_login = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print("Login Status:", res_login.status_code)
    
    token = res_login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test Profile Fetching (correct endpoint: /users/me)
    print("\n--- 3. Fetching User Profile ---")
    res_me = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print("Profile Fetch Status:", res_me.status_code)
    print("Profile Data:", list(res_me.json().keys()))

    # 4. Test Match Endpoint
    print("\n--- 4. Fetching Matches ---")
    res_matches = requests.get(f"{BASE_URL}/matches", headers=headers)
    print("Matches Status:", res_matches.status_code)
    
    if res_matches.status_code == 200:
        matches = res_matches.json().get("matches", [])
        print(f"Found {len(matches)} matches!")
        if matches:
            print("Top Match Score:", matches[0]["compatibility_score"])
            print("Explanation:", matches[0]["explanation"])

    print("\n✅ API Test Suite completed.")


if __name__ == "__main__":
    test_api()
