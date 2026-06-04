#!/usr/bin/env python3
"""
Direct Setup - Create students for Major Project
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
    print("CREATING STUDENTS FOR MAJOR PROJECT CLASS")
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

    # Check if Rajeev Kumar's assignment exists
    print("\n✓ Checking Rajeev Kumar's Major Project assignment...")
    
    teacher = sb.table("teachers").select("id").eq("email", "Rajeev.kumar357@gmail.com").limit(1).execute().data or []
    if not teacher:
        print("ERROR: Rajeev Kumar not found!")
        sys.exit(1)
    
    teacher_id = teacher[0]["id"]
    
    assignment = sb.table("teacher_assignments").select("id").eq("teacher_id", teacher_id).eq("subject_code", "MAJOR-PROJECT").limit(1).execute().data or []
    if assignment:
        print("✓ Major Project assignment exists")
    else:
        print("ERROR: No Major Project assignment!")
        sys.exit(1)

    # Get existing students
    existing_students = sb.table("students").select("board_roll_no").eq("branch", "Computer Engineering").eq("semester", 6).execute().data or []
    existing_rolls = {s["board_roll_no"] for s in existing_students}
    
    print(f"\n✓ Existing students: {len(existing_students)}")

    # Create students
    created_count = 0
    skipped_count = 0
    
    for name, roll_no in students_list:
        if roll_no in existing_rolls:
            skipped_count += 1
            continue
        
        try:
            # Create a simple profile first
            profile_result = sb.table("profiles").insert({
                "full_name": name,
                "email": f"{name.lower().replace(' ', '')}.{roll_no}@student.edu",
                "role": "student",
            }).execute()
            
            profile_id = profile_result.data[0]["id"]
            
            # Create student record
            sb.table("students").insert({
                "profile_id": profile_id,
                "board_roll_no": roll_no,
                "branch": "Computer Engineering",
                "semester": 6,
            }).execute()
            
            created_count += 1
            print(f"  ✓ {name:25} - {roll_no}")
            
        except Exception as e:
            print(f"  ✗ {name:25} - {roll_no}: {str(e)[:60]}")

    # Verify
    print(f"\n" + "="*80)
    print(f"✓ Students created: {created_count}")
    print(f"✓ Students skipped: {skipped_count}")
    
    final_count = sb.table("students").select("*").eq("branch", "Computer Engineering").eq("semester", 6).execute().data or []
    print(f"✓ Total students in Computer Eng Sem 6: {len(final_count)}")
    
    print(f"\n" + "="*80)
    print("SETUP COMPLETE!")
    print("="*80)
    print(f"\nTeacher Login:")
    print(f"  Email: Rajeev.kumar357@gmail.com")
    print(f"  Password: ChangeMe@123")
    print(f"\nGo to: http://localhost:5000/teacher-login\n")
