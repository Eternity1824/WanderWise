"""
Script to test the user_notes API endpoints
"""

import requests
import json

def test_api_endpoints():
    # Define base URL for your API
    BASE_URL = "http://localhost:8000"
    
    # Step 1: Initialize the user_notes table
    print("Step 1: Initializing user_notes table")
    init_response = requests.get(f"{BASE_URL}/user/notes/init")
    print(f"Response: {init_response.status_code} - {init_response.text}")
    print("-" * 50)
    
    # Step 2: Add some test users
    test_users = [
        {"user_id": "user123", "count": 5},
        {"user_id": "alice", "count": 10},
        {"user_id": "bob", "count": 3}
    ]
    
    print("Step 2: Adding test users")
    for user in test_users:
        add_response = requests.post(f"{BASE_URL}/user/{user['user_id']}/notes/add?count={user['count']}")
        print(f"Added {user['user_id']} - Response: {add_response.status_code}")
        print(f"Data: {add_response.json()}")
    print("-" * 50)
    
    # Step 3: Get count for a specific user
    user_to_check = "alice"
    print(f"Step 3: Getting count for user '{user_to_check}'")
    count_response = requests.get(f"{BASE_URL}/user/{user_to_check}/notes/count")
    print(f"Response: {count_response.status_code}")
    print(f"Count: {count_response.text}")
    print("-" * 50)
    
    # Step 4: Update a user's count
    user_to_update = "bob"
    update_count = 2
    print(f"Step 4: Updating user '{user_to_update}' with {update_count} more posts")
    update_response = requests.post(f"{BASE_URL}/user/{user_to_update}/notes/add?count={update_count}")
    print(f"Response: {update_response.status_code}")
    print(f"Updated data: {update_response.json()}")
    print("-" * 50)
    
    # Step 5: Get all users
    print("Step 5: Getting all users")
    all_users_response = requests.get(f"{BASE_URL}/users/notes")
    print(f"Response: {all_users_response.status_code}")
    users = all_users_response.json()
    print("All users in database:")
    for user in users:
        print(f"  User ID: {user['user_id']}, Post Count: {user['post_count']}")
    print("-" * 50)
    
    # Step 6: Try to get count for a non-existent user
    nonexistent_user = "nonexistent_user"
    print(f"Step 6: Getting count for non-existent user '{nonexistent_user}'")
    nonexistent_response = requests.get(f"{BASE_URL}/user/{nonexistent_user}/notes/count")
    print(f"Response: {nonexistent_response.status_code}")
    print(f"Count: {nonexistent_response.text}")
    print("-" * 50)

if __name__ == "__main__":
    test_api_endpoints()