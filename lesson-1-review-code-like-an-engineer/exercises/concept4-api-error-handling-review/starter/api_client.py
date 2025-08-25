"""
Code Review Exercise 4: Simple API Client

Your task: Review this API client code for error handling and structural issues.
Look for issues related to:
- Network error handling
- HTTP response handling
- Input validation
- User experience

Instructions:
1. Identify missing error handling
2. Look for network error issues
3. Suggest basic improvements
4. Rate the overall code quality (Poor, Fair, Good, Excellent)
5. Provide your recommendation (Accept, Modify, Reject)
"""

import requests
import json

class APIClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_user_data(self, user_id):
        url = f"{self.base_url}/users/{user_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None

    def update_user(self, user_id, data):
        url = f"{self.base_url}/users/{user_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.put(url, headers=headers, data=json.dumps(data))
        
        return response.status_code == 200