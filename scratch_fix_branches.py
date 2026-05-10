from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

# Mapping from assignment branches (new data) -> student branches (existing DB)
BRANCH_MAP = {
    "Computer Engineering": "Computer Science",
    "Electrical Engineering": "Electrical",
    "ECE": "Electronics",
    "Instrumentation Engineering": "Instrumentation",
    "Mechanical Engineering": "Mechanical",
}

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    assignments = sb.table("teacher_assignments").select("id, branch").execute().data or []
    print(f"Total assignments: {len(assignments)}")

    updated = 0
    for a in assignments:
        old_branch = a['branch']
        new_branch = BRANCH_MAP.get(old_branch)
        if new_branch:
            sb.table("teacher_assignments").update({"branch": new_branch}).eq("id", a['id']).execute()
            updated += 1

    print(f"Updated {updated} assignments.")

    # Verify
    abranches = set(
        a['branch']
        for a in sb.table("teacher_assignments").select("branch").execute().data or []
    )
    print("Assignment branches after fix:", sorted(abranches))
