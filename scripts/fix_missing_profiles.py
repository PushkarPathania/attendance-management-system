"""
fix_missing_profiles.py
------------------------
Fixes teachers who have a Supabase Auth user but NO profile row.
This happens when auth user was created earlier but profile upsert failed.

Also resets passwords to ChangeMe@123.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD", "ChangeMe@123")
app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    teachers = sb.table("teachers").select("id,full_name,email,department").execute().data or []
    print(f"Checking {len(teachers)} teachers for missing profiles...\n")

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

        # Check if profile exists (case-insensitive)
        existing = sb.table("profiles").select("id").ilike("email", email_lower).limit(1).execute().data or []
        if existing:
            skipped += 1
            continue  # Profile already fine

        # Profile missing — find auth user via admin list
        try:
            # List users and find by email
            auth_users_resp = sb.auth.admin.list_users()
            auth_users = auth_users_resp if isinstance(auth_users_resp, list) else []
            
            matched_user = None
            for u in auth_users:
                u_email = (getattr(u, "email", "") or "").lower()
                if u_email == email_lower:
                    matched_user = u
                    break

            if matched_user:
                user_id = matched_user.id
                # Create profile
                sb.table("profiles").upsert({
                    "id": user_id,
                    "full_name": full_name,
                    "email": email_lower,
                    "role": "teacher",
                    "department": department,
                }).execute()
                # Reset password too
                sb.auth.admin.update_user_by_id(user_id, {"password": DEFAULT_PASSWORD})
                print(f"  [FIXED]  {full_name} ({email_orig}) — profile created + password reset")
                fixed += 1
            else:
                # Auth user doesn't exist at all — create fresh
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
                    "role": "teacher",
                    "department": department,
                }).execute()
                print(f"  [NEW]    {full_name} ({email_orig}) — created from scratch")
                fixed += 1

        except Exception as e:
            print(f"  [FAIL]   {full_name} ({email_orig}) — {e}")
            failed += 1

    print(f"\n=== Done ===")
    print(f"  Fixed:   {fixed}")
    print(f"  Skipped: {skipped} (already had profiles)")
    print(f"  Failed:  {failed}")
    print(f"\nLogin with: email (lowercase) + password: {DEFAULT_PASSWORD}")
