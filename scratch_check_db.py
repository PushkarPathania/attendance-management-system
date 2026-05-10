from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import json

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    print("TEACHERS:")
    teachers = sb.table("teachers").select("*").execute().data
    print(f"Total teachers: {len(teachers)}")
    if teachers:
        print(json.dumps(teachers[0], indent=2))

    print("\nTEACHER ASSIGNMENTS:")
    assignments = sb.table("teacher_assignments").select("*").execute().data
    print(f"Total assignments: {len(assignments)}")
    if assignments:
        print(json.dumps(assignments[0], indent=2))

    print("\nPROFILES:")
    profiles = sb.table("profiles").select("*").eq("role", "teacher").execute().data
    print(f"Total teacher profiles: {len(profiles)}")
