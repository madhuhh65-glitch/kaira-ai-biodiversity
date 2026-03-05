import requests
import random
import string
import sys

BASE_URL = "http://localhost:8000"

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_registration_and_login():
    print("--- Starting Auth Flow Verification ---")
    
    # 1. Generate User Data
    random_str = generate_random_string()
    name = f"Test User {random_str}"
    email = f"test_{random_str}@example.com"
    password = "password123"
    
    print(f"Testing with:\n Name: {name}\n Email: {email}")

    # 2. Test Registration
    print("\n[1] Testing Registration...")
    register_url = f"{BASE_URL}/users/register"
    register_data = {
        "name": name,
        "email": email,
        "password": password,
        "confirm_password": password
    }
    
    try:
        # Note: In the user_routes.py, it expects Form data, not JSON for registration
        response = requests.post(register_url, data=register_data)
        
        if response.status_code == 200:
            print("✅ Registration Successful")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Registration Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Connection Error during Registration: {e}")
        return

    # 3. Test Login
    print("\n[2] Testing Login...")
    login_url = f"{BASE_URL}/users/login"
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        # Login expects JSON body
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login Successful")
                print(f"Token: {data['access_token'][:20]}...")
            else:
                print("❌ Login Failed: Token not found in response")
                print(f"Response: {data}")
        else:
            print(f"❌ Login Failed: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Connection Error during Login: {e}")

if __name__ == "__main__":
    test_registration_and_login()
