#!/usr/bin/env python3
"""
Fix teacher login by creating/updating teacher profiles
Links teachers to their profiles with the correct role
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def fix_teacher_profiles():
    """Create profiles for teachers with role='teacher'"""
    from supabase_app import create_app
    from supabase_app.supabase_client import get_supabase_admin
    
    app = create_app()
    
    with app.app_context():
        sb = get_supabase_admin()
        
        print("\n" + "="*70)
        print("FIXING TEACHER PROFILES")
        print("="*70)
        
        # Get all teachers
        teachers = sb.table("teachers").select("*").execute().data or []
        print(f"\nFound {len(teachers)} teachers in teachers table")
        
        if not teachers:
            print("No teachers to fix!")
            return False
        
        fixed_count = 0
        
        for teacher in teachers:
            teacher_id = teacher['id']
            teacher_email = teacher['email']
            teacher_name = teacher['full_name']
            
            print(f"\nProcessing: {teacher_name} ({teacher_email})")
            
            # Check if profile exists for this teacher
            profile_check = sb.table("profiles").select("id, role").ilike("email", teacher_email).limit(1).execute()
            
            if profile_check.data:
                profile = profile_check.data[0]
                profile_id = profile['id']
                current_role = profile.get('role')
                
                if current_role == 'teacher':
                    print(f"  [OK] Already has teacher profile (ID: {profile_id})")
                else:
                    # Update existing profile to teacher role
                    print(f"  [WARN] Has profile with role '{current_role}', updating to 'teacher'...")
                    try:
                        sb.table("profiles").update({"role": "teacher"}).eq("id", profile_id).execute()
                        print(f"  [OK] Updated profile role to 'teacher'")
                        fixed_count += 1
                    except Exception as e:
                        print(f"  [ERROR] Error updating profile: {e}")
            else:
                # No profile exists - need to create one
                print(f"  [WARN] No profile found, attempting to create...")
                
                # We need an auth user ID to create a profile
                # Check if there's an auth user with this email
                try:
                    auth_users = sb.auth.admin.list_users(per_page=1000)
                    # Handle both list and object cases
                    if hasattr(auth_users, 'users'):
                        users_list = auth_users.users
                    else:
                        users_list = list(auth_users) if hasattr(auth_users, '__iter__') else []
                    
                    auth_user = None
                    for u in users_list:
                        if u.email and u.email.lower() == teacher_email.lower():
                            auth_user = u
                            break
                    
                    if auth_user:
                        # Create profile for existing auth user
                        print(f"  Found auth user, creating profile...")
                        try:
                            sb.table("profiles").upsert({
                                "id": auth_user.id,
                                "full_name": teacher_name,
                                "email": teacher_email,
                                "role": "teacher",
                                "department": teacher.get('department', 'General')
                            }).execute()
                            print(f"  [OK] Created teacher profile for auth user {auth_user.id}")
                            fixed_count += 1
                        except Exception as e:
                            print(f"  [ERROR] Error creating profile: {e}")
                    else:
                        print(f"  [WARN] No auth user found for {teacher_email}")
                        print(f"     Teacher needs to be created as auth user first")
                        print(f"     Or create via admin dashboard")
                        
                except Exception as e:
                    print(f"  [ERROR] Error checking auth users: {e}")
        
        print("\n" + "="*70)
        print(f"COMPLETED: Fixed {fixed_count} teacher profile(s)")
        print("="*70)
        
        # Verify the fix
        print("\nVerifying fix...")
        teacher_profiles = sb.table("profiles").select("*").eq("role", "teacher").execute().data or []
        print(f"✓ Teachers with profiles now: {len(teacher_profiles)}")
        
        if teacher_profiles:
            print("\nTeacher profiles created/updated:")
            for p in teacher_profiles:
                print(f"  - {p['email']} (ID: {p['id']})")
        
        return fixed_count > 0 or len(teacher_profiles) > 0

if __name__ == "__main__":
    success = fix_teacher_profiles()
    sys.exit(0 if success else 1)
