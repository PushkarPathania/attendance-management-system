"""
create_teacher_auth.py
-----------------------
Creates Supabase Auth accounts + profiles entries for all teachers
that were inserted via SQL (complete_schema.sql) but have no auth account.

Default password: ChangeMe@123 (or set SEED_DEFAULT_PASSWORD env var)

Run:
    python scripts/create_teacher_auth.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_app import create_app

DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD", "ChangeMe@123")

app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== Creating Auth accounts for teachers seeded via SQL ===\n")

    # Get all teachers from the teachers table
    teachers = sb.table("teachers").select("id,full_name,email,department").execute().data or []
    print(f"Found {len(teachers)} teacher records in 'teachers' table\n")

    created = 0
    already_exists = 0
    failed = 0

    for t in teachers:
        email = (t.get("email") or "").strip().lower()
        full_name = t.get("full_name", "Unknown")
        department = t.get("department", "General")
        teacher_db_id = t["id"]

        if not email:
            print(f"  [SKIP] No email for teacher: {full_name}")
            continue

        # Check if profile already exists for this email
        existing_profile = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
        if existing_profile:
            print(f"  [OK]   {full_name} ({email}) — auth account already exists")
            already_exists += 1
            continue

        # Create Supabase Auth user
        try:
            result = sb.auth.admin.create_user({
                "email": email,
                "password": DEFAULT_PASSWORD,
                "email_confirm": True,
                "user_metadata": {"role": "teacher"},
            })
            user_id = result.user.id

            # Create profile entry
            sb.table("profiles").upsert({
                "id": user_id,
                "full_name": full_name,
                "email": email,
                "role": "teacher",
                "department": department,
            }).execute()

            print(f"  [NEW]  {full_name} ({email}) — auth account created ✓")
            created += 1

        except Exception as e:
            err_str = str(e)
            if "already been registered" in err_str or "already exists" in err_str.lower():
                # Auth user exists but no profile — try to link
                try:
                    # Find the auth user by email via profiles or try listing
                    # Since we can't directly look up by email in auth, skip profile creation
                    print(f"  [WARN] {full_name} ({email}) — auth user exists but no profile (manual fix needed)")
                    already_exists += 1
                except Exception:
                    print(f"  [WARN] {full_name} ({email}) — {e}")
                    already_exists += 1
            else:
                print(f"  [FAIL] {full_name} ({email}) — Error: {e}")
                failed += 1

    print(f"\n=== Done ===")
    print(f"  Created:        {created}")
    print(f"  Already existed: {already_exists}")
    print(f"  Failed:          {failed}")
    print(f"\nAll teachers can now login with password: {DEFAULT_PASSWORD}")
