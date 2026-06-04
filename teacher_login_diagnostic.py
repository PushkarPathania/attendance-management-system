#!/usr/bin/env python3
"""
Comprehensive Teacher Login Diagnostic
Checks all tables, data, and identifies the exact login issue
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def run_diagnostics():
    """Run full diagnostics on teacher login"""
    from supabase_app import create_app
    from supabase_app.supabase_client import get_supabase_admin, get_supabase_public
    
    app = create_app()
    
    with app.app_context():
        sb_admin = get_supabase_admin()
        sb_public = get_supabase_public()
        
        print("\n" + "="*70)
        print("TEACHER LOGIN DIAGNOSTIC REPORT")
        print("="*70)
        
        # 1. Check profiles table
        print("\n[1] PROFILES TABLE")
        print("-" * 70)
        try:
            profiles = sb_admin.table("profiles").select("*").limit(5).execute()
            print(f"✓ Profiles table exists")
            print(f"  Total records: {len(profiles.data) if profiles.data else 0}")
            
            if profiles.data:
                print(f"  Columns: {list(profiles.data[0].keys())}")
                print(f"  Sample data:")
                for p in profiles.data[:3]:
                    print(f"    - {p.get('email', 'N/A')} | Role: {p.get('role', 'N/A')} | Department: {p.get('department', 'N/A')}")
                    
                # Check for teachers
                teacher_profiles = [p for p in profiles.data if p.get('role') == 'teacher']
                print(f"  Teacher profiles: {len(teacher_profiles)}")
            else:
                print(f"  ⚠ No profiles found!")
        except Exception as e:
            print(f"✗ Error reading profiles: {e}")
        
        # 2. Check teachers table
        print("\n[2] TEACHERS TABLE")
        print("-" * 70)
        try:
            teachers = sb_admin.table("teachers").select("*").limit(5).execute()
            print(f"✓ Teachers table exists")
            print(f"  Total records: {len(teachers.data) if teachers.data else 0}")
            
            if teachers.data:
                print(f"  Columns: {list(teachers.data[0].keys())}")
                print(f"  Sample data:")
                for t in teachers.data[:3]:
                    print(f"    - {t.get('full_name', 'N/A')} | Email: {t.get('email', 'N/A')} | Dept: {t.get('department', 'N/A')}")
            else:
                print(f"  ⚠ No teachers found!")
        except Exception as e:
            print(f"✗ Error reading teachers: {e}")
        
        # 3. Check teacher_assignments table
        print("\n[3] TEACHER_ASSIGNMENTS TABLE")
        print("-" * 70)
        try:
            assignments = sb_admin.table("teacher_assignments").select("*").limit(5).execute()
            print(f"✓ Teacher assignments table exists")
            print(f"  Total records: {len(assignments.data) if assignments.data else 0}")
            
            if assignments.data:
                print(f"  Columns: {list(assignments.data[0].keys())}")
                print(f"  Sample data:")
                for a in assignments.data[:3]:
                    print(f"    - Teacher ID: {a.get('teacher_id', 'N/A')} | Branch: {a.get('branch', 'N/A')} | Sem: {a.get('semester', 'N/A')} | Subject: {a.get('subject_name', 'N/A')}")
            else:
                print(f"  ⚠ No teacher assignments found!")
        except Exception as e:
            print(f"✗ Error reading teacher_assignments: {e}")
        
        # 4. Test actual teacher login flow
        print("\n[4] TEACHER LOGIN FLOW TEST")
        print("-" * 70)
        
        # Get a teacher email from profiles
        teacher_profiles_result = sb_admin.table("profiles").select("id, email, role").eq("role", "teacher").limit(1).execute()
        
        if not teacher_profiles_result.data:
            print("✗ No teacher profiles found in database!")
            print("  Action needed: Create teacher accounts first via admin dashboard")
            return False
        
        teacher_profile = teacher_profiles_result.data[0]
        teacher_email = teacher_profile['email']
        teacher_id = teacher_profile['id']
        
        print(f"Found test teacher: {teacher_email} (ID: {teacher_id})")
        
        # Check if this teacher has a matching row in teachers table
        teachers_result = sb_admin.table("teachers").select("id").ilike("email", teacher_email).limit(1).execute()
        if teachers_result.data:
            teacher_db_id = teachers_result.data[0]['id']
            print(f"✓ Teacher found in teachers table (ID: {teacher_db_id})")
        else:
            print(f"✗ Teacher NOT found in teachers table")
            print(f"  This is the problem! Profile exists but no teachers record")
            return False
        
        # Check if teacher has assignments
        assignments_result = sb_admin.table("teacher_assignments").select("*").eq("teacher_id", teacher_db_id).execute()
        if assignments_result.data and len(assignments_result.data) > 0:
            print(f"✓ Teacher has {len(assignments_result.data)} assignment(s)")
            for a in assignments_result.data:
                print(f"  - {a['branch']} | Sem {a['semester']} | {a['subject_name']}")
        else:
            print(f"✗ Teacher has NO assignments!")
            print(f"  This is the problem! Teacher needs at least one assignment")
            return False
        
        # 5. Check students table
        print("\n[5] STUDENTS TABLE")
        print("-" * 70)
        try:
            students = sb_admin.table("students").select("*").limit(3).execute()
            print(f"✓ Students table exists")
            print(f"  Total records: {len(students.data) if students.data else 0}")
            if students.data:
                print(f"  Sample: {students.data[0]}")
            else:
                print(f"  ⚠ No students found!")
        except Exception as e:
            print(f"✗ Error reading students: {e}")
        
        # 6. Check auth users
        print("\n[6] AUTH USERS (Supabase)")
        print("-" * 70)
        try:
            # List auth users - requires admin
            auth_users = sb_admin.auth.admin.list_users(per_page=5)
            print(f"✓ Found {len(auth_users.users) if auth_users.users else 0} auth users")
            if auth_users.users:
                print(f"  Sample users:")
                for u in auth_users.users[:3]:
                    role = u.user_metadata.get('role', 'N/A') if u.user_metadata else 'N/A'
                    print(f"    - {u.email} | Role: {role}")
        except Exception as e:
            print(f"⚠ Could not list auth users: {e}")
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        if not assignments_result.data or len(assignments_result.data) == 0:
            print("❌ PRIMARY ISSUE: Teacher has no subject assignments!")
            print("\nTo fix:")
            print("1. Go to Admin Dashboard")
            print("2. Edit the teacher")
            print("3. Assign them to at least one branch/semester/subject")
            print("4. Save changes")
            return False
        else:
            print("✓ All tables and data look correct!")
            print("\nThe database configuration appears fine.")
            print("Check the application error logs for specific login errors.")
            return True

if __name__ == "__main__":
    success = run_diagnostics()
    sys.exit(0 if success else 1)
