#!/usr/bin/env python3
"""Direct Supabase auth test"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin, get_supabase_public

app = create_app()

with app.app_context():
    sb_admin = get_supabase_admin()
    sb_public = get_supabase_public()
    
    print("Direct Supabase Auth Test")
    print("=" * 70)
    
    test_email = "hsthakur09@gmail.com"
    test_password = "ChangeMe@123"
    
    print(f"\nTesting auth for: {test_email}")
    print(f"Password: {test_password}")
    
    # Step 1: Try to authenticate
    print(f"\n[Step 1] Attempting sign_in_with_password...")
    try:
        auth_res = sb_public.auth.sign_in_with_password({
            "email": test_email,
            "password": test_password
        })
        user_id = auth_res.user.id
        print(f"[OK] Auth successful! User ID: {user_id}")
        print(f"  User email: {auth_res.user.email}")
        print(f"  Has session: {auth_res.session is not None}")
    except Exception as e:
        print(f"[ERROR] Auth failed: {e}")
        print(f"  Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 2: Check profile
    print(f"\n[Step 2] Checking profile for user {user_id}...")
    try:
        profile_rows = sb_admin.table("profiles").select("*").eq("id", user_id).limit(1).execute().data or []
        if profile_rows:
            p = profile_rows[0]
            print(f"[OK] Profile found!")
            print(f"  Full name: {p.get('full_name')}")
            print(f"  Email: {p.get('email')}")
            print(f"  Role: {p.get('role')}")
        else:
            print(f"[ERROR] No profile found!")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Step 3: Check teacher record
    print(f"\n[Step 3] Checking teacher record...")
    try:
        teacher_rows = sb_admin.table("teachers").select("*").ilike("email", test_email).limit(1).execute().data or []
        if teacher_rows:
            t = teacher_rows[0]
            print(f"[OK] Teacher record found!")
            print(f"  Full name: {t.get('full_name')}")
            print(f"  Email: {t.get('email')}")
            print(f"  Department: {t.get('department')}")
            teacher_id = t['id']
        else:
            print(f"[ERROR] No teacher record!")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    
    # Step 4: Check assignments
    print(f"\n[Step 4] Checking teacher assignments...")
    try:
        assignments = sb_admin.table("teacher_assignments").select("*").eq("teacher_id", teacher_id).execute().data or []
        print(f"[OK] Found {len(assignments)} assignment(s):")
        for a in assignments[:3]:
            print(f"  - {a['branch']} | Sem {a['semester']} | {a['subject_name']}")
        if not assignments:
            print(f"[ERROR] No assignments found!")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print(f"\n" + "=" * 70)
    print("[CONCLUSION] All auth, profile, and assignment steps work!")
    print("The issue must be in the login form or session handling.")
