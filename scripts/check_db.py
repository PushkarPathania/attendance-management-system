import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    # Search for Talvinder by name (case-insensitive)
    teachers = sb.table("teachers").select("id,full_name,email,department").execute().data or []
    talvinder = [t for t in teachers if "talvinder" in (t.get("full_name") or "").lower() or "talvinder" in (t.get("email") or "").lower()]
    print(f"Talvinder records: {talvinder}")

    # Show ALL teacher emails to check format
    print(f"\nTotal teachers: {len(teachers)}")
    print("\nAll teacher emails:")
    for t in teachers:
        print(f"  '{t.get('email')}' — {t.get('full_name')}")

    # Check profiles
    profiles = sb.table("profiles").select("id,full_name,email,role").eq("role", "teacher").execute().data or []
    print(f"\nTotal teacher profiles: {len(profiles)}")
    print("Sample profiles:")
    for p in profiles[:5]:
        print(f"  '{p.get('email')}' — {p.get('full_name')}")
