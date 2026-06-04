#!/usr/bin/env python3
"""Test teacher login endpoint"""
import sys
from pathlib import Path
import requests
import json
import re

sys.path.insert(0, str(Path(__file__).parent))

def test_teacher_login():
    """Test teacher login with actual HTTP request"""
    
    print("Testing Teacher Login Endpoint")
    print("=" * 70)
    
    # Use a teacher we know exists
    test_email = "hsthakur09@gmail.com"
    test_password = "ChangeMe@123"  # From .env SEED_DEFAULT_PASSWORD
    
    print(f"\nTest credentials:")
    print(f"  Email: {test_email}")
    print(f"  Password: {test_password}")
    
    # Try the login endpoint
    login_url = "http://localhost:5000/teacher-login"
    
    print(f"\nAttempting login to: {login_url}")
    
    try:
        # Create session to handle cookies
        session = requests.Session()
        
        # First, try GET to see the form and get session
        response = session.get(login_url, timeout=5)
        print(f"\n[GET] Status: {response.status_code}")
        if response.status_code == 200:
            print("[OK] Form page loads successfully")
        
        # Now try POST with credentials
        data = {
            'email': test_email,
            'password': test_password
        }
        
        print(f"\n[POST] Sending login credentials...")
        response = session.post(login_url, data=data, allow_redirects=False, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code in [301, 302, 303, 307, 308]:
            print(f"[OK] Redirected to: {response.headers.get('Location', 'N/A')}")
            print("SUCCESS: Login appears to work!")
        elif response.status_code == 200:
            print("[ISSUE] Form page returned (login failed)")
            # Extract flash messages
            flash_pattern = r'<div class="alert[^>]*>([^<]+)</div>'
            flash_msgs = re.findall(flash_pattern, response.text)
            if flash_msgs:
                print("\nError messages found:")
                for msg in flash_msgs:
                    print(f"  - {msg.strip()}")
            else:
                print("\nNo flash messages found. Full response (first 2000 chars):")
                print(response.text[:2000])
        else:
            print(f"[ERROR] Unexpected status {response.status_code}")
            print("Response content (first 500 chars):")
            print(response.text[:500])
            
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] Cannot connect to localhost:5000")
        print(f"Make sure the Flask app is running!")
        print(f"Command: python run_supabase.py")
        print(f"Error: {e}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_teacher_login()
