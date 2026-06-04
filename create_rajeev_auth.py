#!/usr/bin/env python3
"""
Create auth account for Rajeev Kumar specifically
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_app import create_app

DEFAULT_PASSWORD = "ChangeMe@123"

app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== Creating Auth account for Rajeev Kumar ===\n")

    email = "Rajeev.kumar357@gmail.com"
    
    # Check if teacher exists in database
    teacher = sb.table("teachers").select("id,full_name,email,department").eq("email", email).limit(1).execute().data or []
    
    if not teacher:
        print(f"ERROR: Teacher {email} not found in database!")
        sys.exit(1)
    
    teacher = teacher[0]
    full_name = teacher.get("full_name", "Rajeev Kumar")
    teacher_id = teacher["id"]
    department = teacher.get("department", "Computer Engineering")
    
    print(f"Teacher found: {full_name}")
    print(f"Department: {department}\n")
    
    # Check if profile already exists
    existing_profile = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
    if existing_profile:
        print(f"✓ Auth account already exists for {email}")
        sys.exit(0)
    
    # Create Supabase Auth user
    try:
        result = sb.auth.admin.create_user({
            "email": email,
            "password": DEFAULT_PASSWORD,
            "email_confirm": True,
            "user_metadata": {"role": "teacher"},
        })
        user_id = result.user.id

        # Create profile entry
        sb.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "role": "teacher",
            "department": department,
        }).execute()

        print(f"✓ Auth account created successfully for {full_name}")
        print(f"✓ Profile linked to teacher record")
        print(f"\nLogin credentials:")
        print(f"  Email: {email}")
        print(f"  Password: {DEFAULT_PASSWORD}")
        
    except Exception as e:
        err_str = str(e)
        if "already been registered" in err_str or "already exists" in err_str.lower():
            print(f"✓ Auth account already exists for {email}")
        else:
            print(f"ERROR: {e}")
            sys.exit(1)
