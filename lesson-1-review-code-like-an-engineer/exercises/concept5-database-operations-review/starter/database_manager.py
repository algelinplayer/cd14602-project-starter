"""
Code Review Exercise 5: Simple Database Operations

Your task: Review this database code for security and structural issues.
Look for issues related to:
- Query construction and security
- Input validation
- Error handling
- Resource management

Instructions:
1. Identify security vulnerabilities
2. Look for missing input validation
3. Suggest basic improvements
4. Rate the overall code quality (Poor, Fair, Good, Excellent)
5. Provide your recommendation (Accept, Modify, Reject)
"""

import sqlite3

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_user_by_email(self, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"SELECT * FROM users WHERE email = '{email}'"
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        return result

    def create_user(self, name, email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"INSERT INTO users (name, email) VALUES ('{name}', '{email}')"
        cursor.execute(query)
        conn.commit()
        conn.close()
        
        return cursor.lastrowid

    def update_user_email(self, user_id, new_email):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = f"UPDATE users SET email = '{new_email}' WHERE id = {user_id}"
        cursor.execute(query)
        conn.commit()
        conn.close()