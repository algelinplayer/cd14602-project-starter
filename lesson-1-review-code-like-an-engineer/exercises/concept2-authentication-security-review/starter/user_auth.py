"""
Code Review Exercise 2: User Authentication

Your task: Review this authentication code for security and structural issues.
Pay special attention to:
- Security vulnerabilities
- Error handling
- Code structure and coupling
- Input validation

Instructions:
1. Identify all security issues
2. Look for structural problems
3. Suggest specific security improvements
4. Rate the overall code quality (Poor, Fair, Good, Excellent)
5. Provide your recommendation (Accept, Modify, Reject)
"""

class UserAuth:
    def __init__(self):
        self.db_connection = connect_to_database()

    def login(self, username, password):
        user = self.db_connection.execute(
            f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        ).fetchone()

        if user:
            session_token = generate_random_string(32)
            return session_token
        else:
            return None


# Simple implementations to make the code runnable
import sqlite3
import random
import string

def connect_to_database():
    """Mock database connection for testing."""
    conn = sqlite3.connect(":memory:")  # In-memory database
    # Create users table with passwords
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    """)
    # Add test users
    conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
    conn.execute("INSERT INTO users (username, password) VALUES ('user1', 'secret')")
    conn.commit()
    return conn

def generate_random_string(length):
    """Generate random string for session tokens."""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

