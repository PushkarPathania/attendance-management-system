#!/usr/bin/env python3
"""Test full teacher login flow with session"""
import sys
from pathlib import Path
import requests
from requests.cookies import RequestsCookieJar

sys.path.insert(0, str(Path(__file__).parent))

def test_full_login_flow():
    """Test the complete login flow"""
    
    print("Testing Full Teacher Login Flow  with Session")
    print("=" * 70)
    
    test_email = "hsthakur09@gmail.com"
    test_password = "ChangeMe@123"
    
    print(f"\nTest Email: {test_email}")
    print(f"Test Password: {test_password}")
    
    session = requests.Session()
    base_url = "http://localhost:5000"
    
    try:
        # Step 1: Get login page
        print(f"\n[Step 1] GET /teacher-login")
        r = session.get(f"{base_url}/teacher-login", timeout=10)
        print(f"  Status: {r.status_code}")
        if "csrf_token" in r.text.lower():
            print(f"  Contains CSRF token: Yes")
        else:
            print(f"  Contains CSRF token: No")
        
        # Step 2: Submit login form
        print(f"\n[Step 2] POST /teacher-login with email/password")
        data = {'email': test_email, 'password': test_password}
        r = session.post(f"{base_url}/teacher-login", data=data, timeout=10, allow_redirects=True)
        print(f"  Status: {r.status_code}")
        print(f"  URL: {r.url}")
        
        # Check if we got assignments selection page
        if "assignment" in r.text.lower() or "Step 2" in r.text:
            print(f"  [OK] Assignment selection page loaded!")
            
            # Extract assignment IDs
            import re
            assignment_ids = re.findall(r'value="([a-f0-9\-]{36})"', r.text)
            print(f"  Found {len(assignment_ids)} assignments: {assignment_ids[:2]}")
            
            if assignment_ids:
                # Step 3: Select first assignment and submit
                print(f"\n[Step 3] POST with assignment selection")
                data = {
                    'email': test_email,
                    'password': test_password,
                    'assignment_id': assignment_ids[0]
                }
                r = session.post(f"{base_url}/teacher-login", data=data, timeout=10, allow_redirects=False)
                print(f"  Status: {r.status_code}")
                if r.status_code in [301, 302, 303, 307, 308]:
                    redirect_url = r.headers.get('Location', 'N/A')
                    print(f"  Redirected to: {redirect_url}")
                    if 'teacher-dashboard' in redirect_url or 'teacher_dashboard' in redirect_url:
                        print(f"  [OK] Redirected to dashboard!")
                    else:
                        print(f"  [WARN] Unexpected redirect")
                else:
                    print(f"  Did not redirect")
                    if "dashboard" in r.text.lower():
                        print(f"  [OK] Dashboard content in response!")
                    else:
                        print(f"  First 200 chars: {r.text[:200]}")
        elif "teacher_dashboard" in r.text or "dashboard" in r.text:
            print(f"  [OK] Directly to teacher dashboard!")
        else:
            print(f"  [ISSUE] Not at dashboard")
            # Show what we got instead
            if "error" in r.text.lower():
                print(f"  Response contains 'error'")
            print(f"  First 300 chars of response:")
            print(f"  {r.text[:300]}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_login_flow()
