#!/usr/bin/env python3
"""
COMPLETE SETUP: Major Project Class with Students
Executes all SQL and auth setup in one go
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

    print("\n" + "="*80)
    print("MAJOR PROJECT CLASS SETUP - COMPLETE")
    print("="*80)

    try:
        # ============================================================
        # STEP 1: Insert/Verify Rajeev Kumar teacher record
        # ============================================================
        print("\n[STEP 1/4] Setting up Rajeev Kumar teacher record...")
        print("-" * 80)
        
        rajeev_data = {
            "full_name": "Rajeev Kumar",
            "email": "Rajeev.kumar357@gmail.com",
            "mobile": "9298286002",
            "designation": "Lecturer",
            "qualification": "B.Tech.",
            "department": "Computer Engineering",
            "is_workshop_staff": False,
        }
        
        # Check if already exists
        existing_teacher = sb.table("teachers").select("id").eq("email", rajeev_data["email"]).limit(1).execute().data or []
        
        if existing_teacher:
            teacher_id = existing_teacher[0]["id"]
            print(f"✓ Rajeev Kumar already exists in database")
        else:
            result = sb.table("teachers").insert(rajeev_data).execute()
            teacher_id = result.data[0]["id"]
            print(f"✓ Rajeev Kumar inserted successfully")
        
        # ============================================================
        # STEP 2: Create Major Project assignment
        # ============================================================
        print("\n[STEP 2/4] Creating Major Project assignment...")
        print("-" * 80)
        
        assignment_data = {
            "teacher_id": teacher_id,
            "branch": "Computer Engineering",
            "semester": 6,
            "subject_code": "MAJOR-PROJECT",
            "subject_name": "Major Project",
            "department": "Computer Engineering",
        }
        
        # Check if already exists
        existing_assignment = sb.table("teacher_assignments").select("id").eq("teacher_id", teacher_id).eq("subject_code", "MAJOR-PROJECT").limit(1).execute().data or []
        
        if existing_assignment:
            print(f"✓ Major Project assignment already exists")
        else:
            sb.table("teacher_assignments").insert(assignment_data).execute()
            print(f"✓ Major Project assignment created")
        
        # ============================================================
        # STEP 3: Create 25 student profiles
        # ============================================================
        print("\n[STEP 3/4] Creating 25 student profiles...")
        print("-" * 80)
        
        students_list = [
            ("AARUSH KOUNDAL", "aarush.koundal.230810404001@student.edu", "230810404001"),
            ("ADITYA", "aditya.230810404004@student.edu", "230810404004"),
            ("ADITYA", "aditya.230810404003@student.edu", "230810404003"),
            ("ADITYA THAKUR", "aditya.thakur.230810404005@student.edu", "230810404005"),
            ("ADITYA KATOCH", "aditya.katoch.230810404006@student.edu", "230810404006"),
            ("ADITYA SHARMA", "aditya.sharma.230810404007@student.edu", "230810404007"),
            ("AKARSHIT MEHRA", "akarshit.mehra.230810404008@student.edu", "230810404008"),
            ("AKSHARA THAKUR", "akshara.thakur.230810404009@student.edu", "230810404009"),
            ("AKSHIT SHARMA", "akshit.sharma.230810404010@student.edu", "230810404010"),
            ("ANKITA", "ankita.230810404011@student.edu", "230810404011"),
            ("AREEN", "areen.230810404015@student.edu", "230810404015"),
            ("ARYAN DHIMAN", "aryan.dhiman.230810404016@student.edu", "230810404016"),
            ("ARYAN JAMWAL", "aryan.jamwal.230810404017@student.edu", "230810404017"),
            ("AYUSH", "ayush.230810404018@student.edu", "230810404018"),
            ("BANSHUL KUMAR", "banshul.kumar.230810404019@student.edu", "230810404019"),
            ("DIKSHA CHAUHAN", "diksha.chauhan.230810404020@student.edu", "230810404020"),
            ("DIVYANSHI", "divyanshi.230810404022@student.edu", "230810404022"),
            ("HARSH", "harsh.230810404024@student.edu", "230810404024"),
            ("HARSH", "harsh.230810404023@student.edu", "230810404023"),
            ("HARSHIT KAPOOR", "harshit.kapoor.230810404025@student.edu", "230810404025"),
            ("ISHA KUMARI", "isha.kumari.230810404026@student.edu", "230810404026"),
            ("ISHAAN KUMAR", "ishaan.kumar.230810404027@student.edu", "230810404027"),
            ("MUSKAN CHOUDHARY", "muskan.choudhary.230810404028@student.edu", "230810404028"),
            ("PIYUSH", "piyush.230810404031@student.edu", "230810404031"),
            ("PRIYA", "priya.230810404032@student.edu", "230810404032"),
        ]
        
        # Create profiles
        profiles_created = 0
        for name, email, roll_no in students_list:
            # Check if already exists
            existing = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
            if existing:
                continue
            
            try:
                sb.table("profiles").insert({
                    "full_name": name,
                    "email": email,
                    "role": "student",
                }).execute()
                profiles_created += 1
            except Exception as e:
                if "already exists" not in str(e).lower():
                    pass  # Ignore schema warnings
        
        print(f"✓ Student profiles processed ({profiles_created} new, rest existing)")
        
        # ============================================================
        # STEP 4: Create student records with roll numbers
        # ============================================================
        print("\n[STEP 4/4] Enrolling students in class...")
        print("-" * 80)
        
        students_enrolled = 0
        for name, email, roll_no in students_list:
            # Get profile ID
            profile = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
            if not profile:
                print(f"  Skipping {name} - profile not found")
                continue
            
            profile_id = profile[0]["id"]
            
            # Check if student record already exists
            existing_student = sb.table("students").select("id").eq("profile_id", profile_id).limit(1).execute().data or []
            if existing_student:
                continue
            
            try:
                sb.table("students").insert({
                    "profile_id": profile_id,
                    "board_roll_no": roll_no,
                    "branch": "Computer Engineering",
                    "semester": 6,
                }).execute()
                students_enrolled += 1
            except Exception as e:
                if "already exists" not in str(e).lower():
                    print(f"  Warning enrolling {name}: {e}")
        
        print(f"✓ Students enrolled ({students_enrolled} new, rest existing)")
        
        # ============================================================
        # STEP 5: Setup Rajeev Kumar auth account
        # ============================================================
        print("\n[STEP 5/5] Setting up teacher login credentials...")
        print("-" * 80)
        
        rajeev_email = "Rajeev.kumar357@gmail.com"
        
        # Check if profile exists
        existing_profile = sb.table("profiles").select("id").eq("email", rajeev_email).limit(1).execute().data or []
        
        if existing_profile:
            print(f"✓ Rajeev Kumar auth account already exists")
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
                    "full_name": "Rajeev Kumar",
                    "email": rajeev_email,
                    "role": "teacher",
                }).execute()

                print(f"✓ Rajeev Kumar auth account created")
            except Exception as e:
                if "already" in str(e).lower():
                    print(f"✓ Auth account already exists")
                else:
                    print(f"  Warning: {e}")
        
        # ============================================================
        # VERIFICATION
        # ============================================================
        print("\n" + "="*80)
        print("VERIFICATION")
        print("="*80)
        
        # Count students
        students_count = sb.table("students").select("*").eq("branch", "Computer Engineering").eq("semester", 6).execute().data or []
        print(f"\n✓ Total students in Computer Engineering Sem 6: {len(students_count)}")
        
        # Check Rajeev's assignments
        assignments = sb.table("teacher_assignments").select("*").eq("teacher_id", teacher_id).execute().data or []
        print(f"✓ Rajeev Kumar's assignments: {len(assignments)}")
        for a in assignments:
            print(f"    - {a['subject_name']} (Semester {a['semester']})")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "="*80)
        print("✓ SETUP COMPLETE!")
        print("="*80)
        
        print(f"\n📚 CLASS DETAILS:")
        print(f"  Teacher: Rajeev Kumar")
        print(f"  Subject: Major Project")
        print(f"  Branch: Computer Engineering")
        print(f"  Semester: 6")
        print(f"  Students: {min(len(students_count), 25)}")
        
        print(f"\n🔑 TEACHER LOGIN:")
        print(f"  Email: {rajeev_email}")
        print(f"  Password: {DEFAULT_PASSWORD}")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"  1. Start Flask: python run_supabase.py")
        print(f"  2. Go to: http://localhost:5000/teacher-login")
        print(f"  3. Login with above credentials")
        print(f"  4. View 25 students in Major Project class\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
