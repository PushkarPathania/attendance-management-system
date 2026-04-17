import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

DEFAULT_PASSWORD = "ChangeMe@123"

app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    teachers = sb.table("teachers").select("id,full_name,email,department").execute().data or []
    print(f"Checking {len(teachers)} teachers for missing profiles...\n")

    # Fetch all pages of users
    print("Fetching all auth users...")
    all_auth_users = []
    try:
        for i in range(1, 100):
            res = sb.auth.admin.list_users(page=i, per_page=100)
            page_users = res.users if hasattr(res, 'users') else res
            all_auth_users.extend(page_users)
            if not page_users or len(page_users) < 100:
                break
    except Exception as e:
        print(f"Error fetching users: {e}")

    print(f"Total auth users found: {len(all_auth_users)}\n")

    fixed = 0
    skipped = 0
    failed = 0

    for t in teachers:
        email_orig = (t.get("email") or "").strip()
        email_lower = email_orig.lower()
        full_name = t.get("full_name", "Unknown")
        department = t.get("department", "General")

        if not email_lower:
            continue

        # Check if profile exists
        existing = sb.table("profiles").select("id").ilike("email", email_lower).limit(1).execute().data or []
        if existing:
            # We can still reset password to ensure they can login
            user_id = existing[0]["id"]
            try:
                sb.auth.admin.update_user_by_id(user_id, {"password": DEFAULT_PASSWORD})
            except Exception:
                pass
            skipped += 1
            continue

        # Missing profile, find auth user from the full fetched list
        matched_user = None
        for u in all_auth_users:
            u_email = (getattr(u, "email", "") or "").lower()
            if u_email == email_lower:
                matched_user = u
                break

        try:
            if matched_user:
                user_id = matched_user.id
                # Create profile
                sb.table("profiles").upsert({
                    "id": user_id,
                    "full_name": full_name,
                    "email": email_lower,
                    "role": "teacher"
                }).execute()
                # Reset password
                sb.auth.admin.update_user_by_id(user_id, {"password": DEFAULT_PASSWORD})
                print(f"  [FIXED]  {full_name} ({email_orig}) - profile created + password reset")
                fixed += 1
            else:
                # Need to create auth user
                result = sb.auth.admin.create_user({
                    "email": email_lower,
                    "password": DEFAULT_PASSWORD,
                    "email_confirm": True,
                    "user_metadata": {"role": "teacher"},
                })
                user_id = result.user.id
                sb.table("profiles").upsert({
                    "id": user_id,
                    "full_name": full_name,
                    "email": email_lower,
                    "role": "teacher"
                }).execute()
                print(f"  [NEW]    {full_name} ({email_orig}) - created from scratch")
                fixed += 1
        except Exception as e:
            print(f"  [FAIL]   {full_name} ({email_orig}) - {e}")
            failed += 1

    print(f"\n=== Done ===")
    print(f"  Fixed:   {fixed}")
    print(f"  Skipped (existing profiles, pwd reset): {skipped}")
    print(f"  Failed:  {failed}")
    print(f"\nAll reset to password: {DEFAULT_PASSWORD}")
