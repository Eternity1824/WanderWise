"""
Simple database test using direct SQL
"""

import sqlite3
import sys
import os

# First, let's create the SQLite database file in the current directory
db_file = 'user_notes_test.db'

# Create a connection to the SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the user_notes table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    post_count INTEGER DEFAULT 0
)
''')
print("Created user_notes table")

# Add some test data
test_users = [
    ("user123", 5),
    ("alice", 10),
    ("bob", 3),
    ("charlie", 15),
    ("david", 7)
]

for user_id, count in test_users:
    cursor.execute("INSERT INTO user_notes (user_id, post_count) VALUES (?, ?)", (user_id, count))
    print(f"Added user {user_id} with post count {count}")

# Commit the changes
conn.commit()

# Update a user's count
cursor.execute("UPDATE user_notes SET post_count = post_count + 2 WHERE user_id = 'alice'")
conn.commit()
print("Updated alice's post count by adding 2")

# Query all users
print("\nAll users in the database:")
cursor.execute("SELECT id, user_id, post_count FROM user_notes")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, User ID: {row[1]}, Post Count: {row[2]}")

# Get a specific user's count
cursor.execute("SELECT post_count FROM user_notes WHERE user_id = 'alice'")
alice_count = cursor.fetchone()[0]
print(f"\nAlice's post count: {alice_count}")

# Close the connection
conn.close()
print("\nDatabase connection closed")
print(f"Database file created at: {os.path.abspath(db_file)}")