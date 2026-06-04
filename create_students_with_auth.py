#!/usr/bin/env python3
"""
Create students with proper auth accounts first
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
    print("CREATING 25 STUDENTS WITH AUTH ACCOUNTS")
    print("="*80)

    students_list = [
        ("AARUSH KOUNDAL", "230810404001"),
        ("ADITYA", "230810404004"),
        ("ADITYA", "230810404003"),
        ("ADITYA THAKUR", "230810404005"),
        ("ADITYA KATOCH", "230810404006"),
        ("ADITYA SHARMA", "230810404007"),
        ("AKARSHIT MEHRA", "230810404008"),
        ("AKSHARA THAKUR", "230810404009"),
        ("AKSHIT SHARMA", "230810404010"),
        ("ANKITA", "230810404011"),
        ("AREEN", "230810404015"),
        ("ARYAN DHIMAN", "230810404016"),
        ("ARYAN JAMWAL", "230810404017"),
        ("AYUSH", "230810404018"),
        ("BANSHUL KUMAR", "230810404019"),
        ("DIKSHA CHAUHAN", "230810404020"),
        ("DIVYANSHI", "230810404022"),
        ("HARSH", "230810404024"),
        ("HARSH", "230810404023"),
        ("HARSHIT KAPOOR", "230810404025"),
        ("ISHA KUMARI", "230810404026"),
        ("ISHAAN KUMAR", "230810404027"),
        ("MUSKAN CHOUDHARY", "230810404028"),
        ("PIYUSH", "230810404031"),
        ("PRIYA", "230810404032"),
    ]

    DEFAULT_PASSWORD = "Student@123"

    created_count = 0
    error_count = 0

    print(f"\nCreating {len(students_list)} students...\n")

    for idx, (name, roll_no) in enumerate(students_list, 1):
        try:
            # Generate email
            email = f"student.{roll_no}@gpkangra.edu.in"
            
            # Create auth user
            auth_user = sb.auth.admin.create_user({
                "email": email,
                "password": DEFAULT_PASSWORD,
                "email_confirm": True,
                "user_metadata": {"role": "student", "roll_no": roll_no},
            })
            
            user_id = auth_user.user.id
            
            # Create profile
            sb.table("profiles").insert({
                "id": user_id,
                "full_name": name,
                "email": email,
                "role": "student",
            }).execute()
            
            # Create student record
            sb.table("students").insert({
                "profile_id": user_id,
                "board_roll_no": roll_no,
                "branch": "Computer Engineering",
                "semester": 6,
            }).execute()
            
            print(f"  [{idx:2d}/25] ✓ {name:25} - {roll_no}")
            created_count += 1
            
        except Exception as e:
            err_str = str(e)
            if "already" in err_str.lower():
                print(f"  [{idx:2d}/25] ~ {name:25} - {roll_no} (already exists)")
            else:
                print(f"  [{idx:2d}/25] ✗ {name:25} - {roll_no}")
                print(f"       Error: {err_str[:60]}")
                error_count += 1

    # Verify
    print(f"\n" + "="*80)
    
    students_db = sb.table("students").select("*").eq("branch", "Computer Engineering").eq("semester", 6).execute().data or []
    print(f"✓ Students created: {created_count}")
    print(f"✓ Errors: {error_count}")
    print(f"✓ Total in database: {len(students_db)}")
    
    print(f"\n" + "="*80)
    print("✓ SETUP COMPLETE!")
    print("="*80)
    print(f"\nTeacher Login:")
    print(f"  Email: Rajeev.kumar357@gmail.com")
    print(f"  Password: ChangeMe@123")
    print(f"\nStudent Login (example):")
    print(f"  Email: student.230810404001@gpkangra.edu.in")
    print(f"  Password: {DEFAULT_PASSWORD}")
    print(f"\nGo to: http://localhost:5000/teacher-login\n")
