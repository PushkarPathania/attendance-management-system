import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

NEW_PASSWORD = "ChangeMe@123"

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== STEP 1: Fetch all auth users ===")
    all_auth = []
    for i in range(1, 100):
        res = sb.auth.admin.list_users(page=i, per_page=100)
        page = getattr(res, 'users', res)
        all_auth.extend(page)
        if not page or len(page) < 100:
            break
    print(f"Total auth users: {len(all_auth)}")
    auth_by_email = {getattr(u, 'email', '').lower(): u for u in all_auth}

    print("\n=== STEP 2: Fetch teachers ===")
    teachers = sb.table("teachers").select("id,email,full_name").execute().data or []
    print(f"Teachers in DB: {len(teachers)}")

    print("\n=== STEP 3: Check existing profiles ===")
    profiles = sb.table("profiles").select("id,email,role").execute().data or []
    profile_by_email = {p["email"].lower(): p for p in profiles}
    teacher_profiles = [p for p in profiles if p.get("role") == "teacher"]
    print(f"Total profiles: {len(profiles)}, Teacher profiles: {len(teacher_profiles)}")

    fixed = 0
    already_ok = 0
    failed = 0

    print("\n=== STEP 4: Fix all teachers ===")
    for t in teachers:
        email_orig = (t.get("email") or "").strip()
        email = email_orig.lower()
        name = t.get("full_name", "Unknown")
        if not email:
            continue

        auth_user = auth_by_email.get(email)

        if auth_user:
            uid = auth_user.id
            # Ensure profile exists with correct role
            profile = profile_by_email.get(email)
            if not profile:
                try:
                    sb.table("profiles").upsert({
                        "id": uid,
                        "full_name": name,
                        "email": email,
                        "role": "teacher"
                    }).execute()
                    print(f"  [PROFILE CREATED] {name} ({email})")
                except Exception as e:
                    print(f"  [PROFILE FAIL] {name} ({email}): {e}")
                    failed += 1
                    continue
            elif profile.get("role") != "teacher":
                try:
                    sb.table("profiles").update({"role": "teacher"}).eq("id", uid).execute()
                    print(f"  [ROLE FIXED] {name} ({email})")
                except Exception as e:
                    print(f"  [ROLE FIX FAIL] {name} ({email}): {e}")

            # Reset password
            try:
                sb.auth.admin.update_user_by_id(uid, {
                    "password": NEW_PASSWORD,
                    "email_confirm": True
                })
                fixed += 1
            except Exception as e:
                print(f"  [PWD FAIL] {name} ({email}): {e}")
                failed += 1
        else:
            # Auth user missing — create from scratch
            try:
                res = sb.auth.admin.create_user({
                    "email": email,
                    "password": NEW_PASSWORD,
                    "email_confirm": True,
                    "user_metadata": {"role": "teacher"}
                })
                uid = res.user.id
                sb.table("profiles").upsert({
                    "id": uid,
                    "full_name": name,
                    "email": email,
                    "role": "teacher"
                }).execute()
                print(f"  [AUTH+PROFILE CREATED] {name} ({email})")
                fixed += 1
            except Exception as e:
                print(f"  [CREATE FAIL] {name} ({email}): {e}")
                failed += 1

    print(f"\n=== DONE ===")
    print(f"Fixed / Password reset:  {fixed}")
    print(f"Failed:                  {failed}")
    print(f"\nAll working teachers can now login with password: {NEW_PASSWORD}")
