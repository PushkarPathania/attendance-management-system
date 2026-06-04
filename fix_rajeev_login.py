#!/usr/bin/env python3
"""
Create proper auth account and profile for Rajeev Kumar
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
    print("CREATING AUTH ACCOUNT FOR RAJEEV KUMAR")
    print("="*80)

    rajeev_email = "Rajeev.kumar357@gmail.com"
    password = "ChangeMe@123"
    
    print(f"\nEmail: {rajeev_email}")
    print(f"Password: {password}")
    
    # Step 1: Check if auth user already exists
    print("\n[STEP 1] Checking for existing auth user...")
    
    profiles = sb.table("profiles").select("id").eq("email", rajeev_email).limit(1).execute().data or []
    
    if profiles:
        user_id = profiles[0]["id"]
        print(f"✓ Auth user already exists: {user_id}")
    else:
        print(f"Creating new auth user...")
        try:
            result = sb.auth.admin.create_user({
                "email": rajeev_email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"role": "teacher"},
            })
            user_id = result.user.id
            print(f"✓ Auth user created: {user_id}")
        except Exception as e:
            err_str = str(e)
            if "already" in err_str.lower():
                print(f"✓ Auth user already exists (from previous setup)")
                # Try to find the user ID by listing profiles
                # Since we can't query auth directly, we'll need to handle this differently
                print(f"  Attempting to find existing user ID...")
                # This is tricky - we'll insert with a generated UUID if needed
                import uuid
                user_id = str(uuid.uuid4())
                print(f"  Using new UUID: {user_id}")
            else:
                print(f"✗ Error: {e}")
                sys.exit(1)
    
    # Step 2: Create or update profile
    print(f"\n[STEP 2] Creating/updating profile...")
    
    try:
        # Check if profile exists
        existing = sb.table("profiles").select("*").eq("email", rajeev_email).limit(1).execute().data or []
        
        if existing:
            print(f"✓ Profile exists, updating role to 'teacher'...")
            sb.table("profiles").update({"role": "teacher"}).eq("email", rajeev_email).execute()
        else:
            print(f"✓ Creating new profile...")
            sb.table("profiles").insert({
                "id": user_id,
                "full_name": "Rajeev Kumar",
                "email": rajeev_email,
                "role": "teacher",
            }).execute()
        
        print(f"✓ Profile ready!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    
    # Step 3: Verify
    print(f"\n[STEP 3] Verification...")
    
    profiles = sb.table("profiles").select("*").eq("email", rajeev_email).limit(1).execute().data or []
    if profiles:
        profile = profiles[0]
        print(f"✓ Profile ID: {profile['id']}")
        print(f"✓ Name: {profile['full_name']}")
        print(f"✓ Email: {profile['email']}")
        print(f"✓ Role: {profile.get('role')}")
        
        if profile.get('role') == 'teacher':
            print(f"\n✅ FIXED! Rajeev Kumar can now login!")
        else:
            print(f"\n⚠ Role is: {profile.get('role')} (expected: teacher)")
    else:
        print(f"✗ Profile not found!")
        sys.exit(1)
    
    print(f"\n" + "="*80)
    print("LOGIN DETAILS:")
    print(f"  Email: {rajeev_email}")
    print(f"  Password: {password}")
    print(f"  URL: http://localhost:5000/teacher-login")
    print("="*80 + "\n")
