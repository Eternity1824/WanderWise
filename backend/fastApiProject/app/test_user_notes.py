"""
Script to add test data to the user_notes table
"""

import sys
import os
# Add the app directory to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.UserNoteService import user_note_service

def add_test_data():
    # First initialize/clear the table
    user_note_service.clear_database()
    print("Cleared user_notes table")
    
    # Add test users with different post counts
    test_users = [
        {"user_id": "user123", "count": 5},
        {"user_id": "alice", "count": 10},
        {"user_id": "bob", "count": 3},
        {"user_id": "charlie", "count": 15},
        {"user_id": "david", "count": 7}
    ]
    
    for user in test_users:
        result = user_note_service.add_or_update_user_note_count(user["user_id"], user["count"])
        print(f"Added user {user['user_id']} with post count {user['count']}")
    
    # Update a user's count to show incrementing works
    result = user_note_service.add_or_update_user_note_count("alice", 2)
    print(f"Updated 'alice' by adding 2 more posts, new count: {result.post_count}")
    
    # Retrieve all user records to show they were added correctly
    all_users = user_note_service.get_all_user_notes()
    print("\nAll users in the database:")
    for user in all_users:
        print(f"User ID: {user.user_id}, Post Count: {user.post_count}")
    
    # Test the get_user_note_count method
    alice_count = user_note_service.get_user_note_count("alice")
    print(f"\nAlice's post count: {alice_count}")
    
    # Test retrieving a non-existent user
    nonexistent_count = user_note_service.get_user_note_count("nonexistent_user")
    print(f"Nonexistent user's post count: {nonexistent_count}")

if __name__ == "__main__":
    add_test_data()