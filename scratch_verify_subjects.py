from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    # Pick a sample from each branch/semester and list expected subjects
    test_cases = [
        ("Computer Science", 2),
        ("Computer Science", 4),
        ("Computer Science", 6),
        ("Electrical", 2),
        ("Electronics", 2),
        ("Instrumentation", 4),
        ("Mechanical", 6),
    ]

    for branch, sem in test_cases:
        subjects = (
            sb.table("teacher_assignments")
            .select("subject_name")
            .eq("branch", branch)
            .eq("semester", sem)
            .execute()
            .data or []
        )
        names = list(set(s['subject_name'] for s in subjects))
        print(f"\n[{branch} - Sem {sem}] ({len(names)} subjects)")
        for n in sorted(names):
            print(f"  - {n}")
