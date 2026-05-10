from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    # 1. Check if teacher_assignments has 'assignment_id' column or uses 'id'
    print("=== TEACHER ASSIGNMENTS (first row) ===")
    a = sb.table("teacher_assignments").select("*").limit(1).execute().data
    if a:
        print(dict(a[0]).keys())
        print(a[0])

    # 2. Check attendance table schema
    print("\n=== ATTENDANCE TABLE (first row) ===")
    att = sb.table("attendance").select("*").limit(1).execute().data
    if att:
        print(dict(att[0]).keys())
        print(att[0])
    else:
        print("EMPTY — no attendance records")

    # 3. Check students count per branch/semester
    print("\n=== STUDENTS PER BRANCH/SEM ===")
    students = sb.table("students").select("branch, semester").execute().data or []
    from collections import Counter
    c = Counter((s['branch'], str(s['semester'])) for s in students)
    for k, v in sorted(c.items()):
        print(f"  {k}: {v} students")

    # 4. Check teacher login example — does teacher_branch stored in session match students?
    # Check a specific teacher's assignments
    print("\n=== SAMPLE TEACHER ASSIGNMENT ===")
    assignments = sb.table("teacher_assignments").select("*").limit(3).execute().data or []
    for a in assignments:
        print(f"  branch={a.get('branch')}, semester={a.get('semester')}, subject={a.get('subject_name')}")
