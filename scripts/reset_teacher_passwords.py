"""
reset_teacher_passwords.py
--------------------------
Ensures every teacher in the 'teachers' table has:
  1. A Supabase Auth account
  2. A profile entry
  3. Password set to ChangeMe@123 (or SEED_DEFAULT_PASSWORD env var)

This is idempotent - safe to run multiple times.
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
    print(f"Processing {len(teachers)} teachers...\n")

    created = 0
    reset = 0
    failed = 0

    for t in teachers:
        email_orig = (t.get("email") or "").strip()
        email_lower = email_orig.lower()
        full_name = t.get("full_name", "Unknown")
        department = t.get("department", "General")

        if not email_lower:
            continue

        # Check profile using case-insensitive search (ilike)
        existing = sb.table("profiles").select("id").ilike("email", email_lower).limit(1).execute().data or []

        if existing:
            # Auth user exists — reset their password
            user_id = existing[0]["id"]
            try:
                sb.auth.admin.update_user_by_id(user_id, {"password": DEFAULT_PASSWORD})
                print(f"  [RESET] {full_name} ({email_orig})")
                reset += 1
            except Exception as e:
                print(f"  [FAIL-RESET] {full_name} ({email_orig}) — {e}")
                failed += 1
        else:
            # No auth account — create one
            try:
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
                print(f"  [NEW]   {full_name} ({email_orig})")
                created += 1
            except Exception as e:
                print(f"  [FAIL]  {full_name} ({email_orig}) — {e}")
                failed += 1

    print(f"\n=== Done ===")
    print(f"  Password reset: {reset}")
    print(f"  New accounts:   {created}")
    print(f"  Failed:         {failed}")
    print(f"\nAll teachers now use password: {DEFAULT_PASSWORD}")
    print("Login email is case-insensitive (enter as lowercase)")
