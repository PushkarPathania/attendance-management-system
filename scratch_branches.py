from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import json

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    print("=== STUDENT BRANCHES ===")
    students = sb.table("students").select("branch, semester").execute().data or []
    branches = set()
    for s in students:
        branches.add((s['branch'], str(s['semester'])))
    for b in sorted(branches):
        print(b)

    print("\n=== ASSIGNMENT BRANCHES ===")
    assignments = sb.table("teacher_assignments").select("branch, semester").execute().data or []
    abranches = set()
    for a in assignments:
        abranches.add((a['branch'], str(a['semester'])))
    for b in sorted(abranches):
        print(b)
