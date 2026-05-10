from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    # Check actual attendance columns by inserting a dry-run (inspection only via select)
    # Use a raw describe-like approach via a sentinel call
    print("=== ATTENDANCE TABLE COLUMNS ===")
    try:
        # Try with assignment_id
        r = sb.table("attendance").select("id, student_id, assignment_id, attendance_date, status").limit(1).execute()
        print("assignment_id column EXISTS")
        print(r.data)
    except Exception as e:
        print(f"assignment_id column MISSING: {e}")

    try:
        # Try with teacher_id
        r = sb.table("attendance").select("id, student_id, teacher_id, attendance_date, status").limit(1).execute()
        print("teacher_id column EXISTS")
        print(r.data)
    except Exception as e:
        print(f"teacher_id column MISSING: {e}")

    # What does teacher dashboard query look like for branch=Computer Science, sem=2?
    print("\n=== STUDENTS IN Computer Science Sem 2 ===")
    students = sb.table("students").select("id, profile_id, board_roll_no, branch, semester").eq("branch", "Computer Science").eq("semester", 2).execute().data or []
    print(f"Count: {len(students)}")
    if students:
        print("First:", students[0])

    # Also check if semester int vs text matters
    print("\n=== STUDENTS IN Computer Science Sem '2' (string) ===")
    students2 = sb.table("students").select("id").eq("branch", "Computer Science").eq("semester", "2").execute().data or []
    print(f"Count with string '2': {len(students2)}")
