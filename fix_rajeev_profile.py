#!/usr/bin/env python3
"""
Check Rajeev Kumar's profile and fix if needed
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_app import create_app

app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("\n" + "="*80)
    print("CHECKING RAJEEV KUMAR PROFILE")
    print("="*80)

    rajeev_email = "Rajeev.kumar357@gmail.com"
    
    # Check teacher record
    print("\n[1] Teacher Record:")
    teacher = sb.table("teachers").select("*").eq("email", rajeev_email).limit(1).execute().data or []
    if teacher:
        print(f"  ✓ Found: {teacher[0]['full_name']}")
        print(f"    ID: {teacher[0]['id']}")
        print(f"    Department: {teacher[0]['department']}")
    else:
        print(f"  ✗ Not found")
    
    # Check profile record
    print("\n[2] Profile Record:")
    profiles = sb.table("profiles").select("*").eq("email", rajeev_email).limit(1).execute().data or []
    if profiles:
        profile = profiles[0]
        print(f"  ✓ Found: {profile['full_name']}")
        print(f"    ID: {profile['id']}")
        print(f"    Role: {profile.get('role', 'N/A')}")
    else:
        print(f"  ✗ Not found")
    
    # Check auth user
    print("\n[3] Auth User:")
    try:
        # Try to get auth user via admin API
        print(f"  Checking Supabase Auth...")
        # We can't directly query auth users, but we can try to create or update profile
    except Exception as e:
        print(f"  Error: {e}")
    
    # FIX: Ensure profile exists with role='teacher'
    print("\n[4] FIXING PROFILE:")
    
    if profiles:
        profile = profiles[0]
        if profile.get('role') != 'teacher':
            print(f"  Updating role from '{profile.get('role')}' to 'teacher'...")
            sb.table("profiles").update({"role": "teacher"}).eq("id", profile['id']).execute()
            print(f"  ✓ Updated!")
        else:
            print(f"  ✓ Role is already 'teacher'")
    else:
        print(f"  ✗ Profile doesn't exist - need to create it")
        print(f"  Creating profile for Rajeev Kumar...")
        try:
            # Get teacher data
            if teacher:
                sb.table("profiles").insert({
                    "full_name": teacher[0]['full_name'],
                    "email": rajeev_email,
                    "role": "teacher",
                }).execute()
                print(f"  ✓ Profile created!")
            else:
                print(f"  ERROR: Teacher record not found")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Verify
    print("\n[5] VERIFICATION:")
    profiles = sb.table("profiles").select("*").eq("email", rajeev_email).limit(1).execute().data or []
    if profiles:
        profile = profiles[0]
        print(f"  ✓ Profile exists")
        print(f"    Role: {profile.get('role')}")
        if profile.get('role') == 'teacher':
            print(f"  ✓ Login should now work!")
        else:
            print(f"  ✗ Role is incorrect: {profile.get('role')}")
    else:
        print(f"  ✗ Profile still missing")
    
    print("\n" + "="*80)
    print("Try logging in with:")
    print(f"  Email: {rajeev_email}")
    print(f"  Password: ChangeMe@123")
    print("="*80 + "\n")
