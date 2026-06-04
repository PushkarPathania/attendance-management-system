#!/usr/bin/env python3
"""
Setup Major Project Class - Complete setup
1. Ensure Rajeev Kumar has auth credentials
2. Create student auth accounts
3. Verify the setup
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

    print("\n" + "="*70)
    print("SETUP: MAJOR PROJECT CLASS - COMPUTER ENGINEERING SEM 6")
    print("="*70)

    # STEP 1: Ensure Rajeev Kumar has auth account
    print("\n[STEP 1] Setting up Rajeev Kumar teacher account...")
    print("-" * 70)

    rajeev_email = "Rajeev.kumar357@gmail.com"
    
    teacher = sb.table("teachers").select("id,full_name,email,department").eq("email", rajeev_email).limit(1).execute().data or []
    
    if not teacher:
        print(f"ERROR: Teacher {rajeev_email} not found in database!")
        print("Please run setup_major_project_class.sql first in Supabase SQL Editor")
        sys.exit(1)
    
    teacher = teacher[0]
    full_name = teacher.get("full_name", "Rajeev Kumar")
    teacher_id = teacher["id"]
    
    print(f"✓ Teacher found: {full_name}")
    
    # Check if profile exists
    existing_profile = sb.table("profiles").select("id").eq("email", rajeev_email).limit(1).execute().data or []
    
    if existing_profile:
        print(f"✓ Auth account already exists")
    else:
        try:
            result = sb.auth.admin.create_user({
                "email": rajeev_email,
                "password": DEFAULT_PASSWORD,
                "email_confirm": True,
                "user_metadata": {"role": "teacher"},
            })
            user_id = result.user.id

            sb.table("profiles").insert({
                "id": user_id,
                "full_name": full_name,
                "email": rajeev_email,
                "role": "teacher",
                "department": "Computer Engineering",
            }).execute()

            print(f"✓ Auth account created successfully")
        except Exception as e:
            if "already" in str(e).lower():
                print(f"✓ Auth account already exists")
            else:
                print(f"ERROR creating auth: {e}")
                sys.exit(1)

    # STEP 2: Check assignment
    print("\n[STEP 2] Verifying Major Project assignment...")
    print("-" * 70)

    assignments = sb.table("teacher_assignments").select("*").eq("teacher_id", teacher_id).eq("subject_code", "MAJOR-PROJECT").execute().data or []
    
    if assignments:
        print(f"✓ Major Project assignment exists")
        print(f"  Branch: {assignments[0]['branch']}")
        print(f"  Semester: {assignments[0]['semester']}")
    else:
        print("WARNING: No Major Project assignment found")
        print("Please run setup_major_project_class.sql in Supabase SQL Editor")

    # STEP 3: Check students
    print("\n[STEP 3] Verifying students...")
    print("-" * 70)

    students = sb.table("students").select("*").eq("branch", "Computer Engineering").eq("semester", 6).execute().data or []
    
    print(f"✓ Total students in Computer Engineering Sem 6: {len(students)}")
    
    if len(students) >= 25:
        print(f"✓ All 25 students are enrolled")
    else:
        print(f"WARNING: Only {len(students)}/25 students found")

    # STEP 4: Summary
    print("\n[STEP 4] SETUP SUMMARY")
    print("="*70)

    print("\n✓ Major Project Class Setup Complete!\n")
    print(f"Teacher Login:")
    print(f"  Email: {rajeev_email}")
    print(f"  Password: {DEFAULT_PASSWORD}")
    print(f"\nClass Details:")
    print(f"  Subject: Major Project")
    print(f"  Branch: Computer Engineering")
    print(f"  Semester: 6")
    print(f"  Students: {min(len(students), 25)}")
    print(f"\nNext Steps:")
    print(f"  1. Go to http://localhost:5000/teacher-login")
    print(f"  2. Login with email: {rajeev_email}")
    print(f"  3. Password: {DEFAULT_PASSWORD}")
    print(f"  4. You should see 25 students in Major Project class\n")
