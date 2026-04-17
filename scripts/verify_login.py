import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin, get_supabase_public
    sb = get_supabase_admin()
    sb_pub = get_supabase_public()

    test_email = "talvinder.mr@gmail.com"
    test_password = "ChangeMe@123"

    print(f"=== Testing Login for: {test_email} ===")

    # Step 1: Check profile exists
    profile = sb.table("profiles").select("id,email,role").ilike("email", test_email).execute().data
    print(f"Profile: {profile}")

    # Step 2: Check teacher record exists
    teacher = sb.table("teachers").select("id,email,full_name").ilike("email", test_email).execute().data
    print(f"Teacher record: {teacher}")

    # Step 3: Check teacher assignments
    if teacher:
        tid = teacher[0]["id"]
        assigns = sb.table("teacher_assignments").select("id,branch,semester,subject_name").eq("teacher_id", tid).execute().data
        print(f"Teacher assignments: {assigns}")

    # Step 4: Try to actually sign in
    print(f"\nAttempting sign-in with password '{test_password}'...")
    try:
        res = sb_pub.auth.sign_in_with_password({"email": test_email, "password": test_password})
        print(f"  LOGIN SUCCESS! User ID: {res.user.id}")
        # Sign out after test
        sb_pub.auth.sign_out()
    except Exception as e:
        print(f"  LOGIN FAILED: {e}")
        # If login fails with ChangeMe@123, try resetting directly  
        print(f"\nForcing password reset for {test_email}...")
        try:
            auth_users = []
            for i in range(1, 50):
                page = sb.auth.admin.list_users(page=i, per_page=100)
                users = getattr(page, 'users', page)
                auth_users.extend(users)
                if not users or len(users) < 100:
                    break
            matched = [u for u in auth_users if getattr(u, 'email', '').lower() == test_email.lower()]
            if matched:
                uid = matched[0].id
                sb.auth.admin.update_user_by_id(uid, {
                    "password": test_password,
                    "email_confirm": True
                })
                print(f"  Password force-reset done for {uid}")
                # Try login again
                res2 = sb_pub.auth.sign_in_with_password({"email": test_email, "password": test_password})
                print(f"  RETRY LOGIN SUCCESS! User ID: {res2.user.id}")
                sb_pub.auth.sign_out()
            else:
                print(f"  User not found in auth at all!")
        except Exception as e2:
            print(f"  Force reset also failed: {e2}")

    print("\n=== SUMMARY of teacher assignments ===")
    # Show all teachers without assignments
    all_teachers = sb.table("teachers").select("id,email,full_name").execute().data or []
    all_assigns = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    assigned_ids = {a["teacher_id"] for a in all_assigns}
    no_assign = [t for t in all_teachers if t["id"] not in assigned_ids]
    print(f"Teachers without assignments: {len(no_assign)}")
    for t in no_assign[:10]:
        print(f"  - {t['full_name']} ({t['email']})")
