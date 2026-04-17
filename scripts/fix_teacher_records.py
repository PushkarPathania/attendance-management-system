import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

NEW_PASSWORD = "ChangeMe@123"

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== Fetching all auth users ===")
    all_auth = []
    for i in range(1, 100):
        res = sb.auth.admin.list_users(page=i, per_page=100)
        page = getattr(res, 'users', res)
        all_auth.extend(page)
        if not page or len(page) < 100:
            break
    auth_by_email = {getattr(u, 'email', '').lower(): u for u in all_auth}
    print(f"Total auth users: {len(all_auth)}")

    print("\n=== Fetching all teacher profiles ===")
    profiles = sb.table("profiles").select("id,email,full_name,role").eq("role", "teacher").execute().data or []
    print(f"Teacher profiles: {len(profiles)}")

    print("\n=== Fetching all teachers table rows ===")
    teachers = sb.table("teachers").select("id,email,full_name").execute().data or []
    teacher_emails = {t["email"].lower(): t for t in teachers}
    print(f"Teachers table rows: {len(teachers)}")

    print("\n=== Fetching all teacher_assignments ===")
    assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    assigned_teacher_ids = {a["teacher_id"] for a in assignments}
    teachers_without_assignments = [t for t in teachers if t["id"] not in assigned_teacher_ids]
    print(f"Teachers without any assignment: {len(teachers_without_assignments)}")

    created_teachers = 0
    fixed_passwords = 0
    failed = 0

    print("\n=== Creating missing teachers table rows from profiles ===")
    for p in profiles:
        email = (p.get("email") or "").lower().strip()
        name = p.get("full_name") or "Unknown"
        if not email:
            continue

        if email not in teacher_emails:
            # Create the teachers table row
            try:
                ins = sb.table("teachers").insert({
                    "full_name": name,
                    "email": email,
                    "department": "General",
                    "teacher_code": "N/A",
                }).execute()
                teacher_id = ins.data[0]["id"]
                teacher_emails[email] = ins.data[0]
                print(f"  [TEACHER CREATED] {name} ({email})")
                created_teachers += 1
            except Exception as e:
                print(f"  [TEACHER FAIL] {name} ({email}): {e}")
                failed += 1
                continue
        
        # Also ensure password is reset
        auth_user = auth_by_email.get(email)
        if auth_user:
            try:
                sb.auth.admin.update_user_by_id(auth_user.id, {
                    "password": NEW_PASSWORD,
                    "email_confirm": True
                })
                fixed_passwords += 1
            except Exception as e:
                print(f"  [PWD FAIL] {name} ({email}): {e}")

    print(f"\n=== DONE ===")
    print(f"Teachers table rows created: {created_teachers}")
    print(f"Passwords reset:             {fixed_passwords}")
    print(f"Failures:                    {failed}")

    print("\n=== Teachers still without assignments (need admin to assign) ===")
    # Refresh
    assignments2 = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    assigned_ids2 = {a["teacher_id"] for a in assignments2}
    teachers2 = sb.table("teachers").select("id,email,full_name").execute().data or []
    no_assign = [t for t in teachers2 if t["id"] not in assigned_ids2]
    print(f"Count: {len(no_assign)}")
    for t in no_assign[:20]:
        print(f"  - {t['full_name']} ({t['email']})")
    if len(no_assign) > 20:
        print(f"  ... and {len(no_assign)-20} more")
