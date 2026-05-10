from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    # Simulate what happens when a teacher logs in
    # Get a sample teacher who has assignments
    assignments = sb.table("teacher_assignments").select("*").limit(1).execute().data or []
    if not assignments:
        print("NO ASSIGNMENTS FOUND")
    else:
        a = assignments[0]
        print(f"Assignment: branch={a['branch']!r}, semester={a['semester']!r}, type(semester)={type(a['semester']).__name__}")

        # Simulate the teacher_dashboard query using the exact same values from session
        branch = a['branch']
        semester = a['semester']
        try:
            semester_int = int(semester)
        except (TypeError, ValueError):
            semester_int = semester
        
        print(f"\nQuerying students with branch={branch!r}, semester={semester_int!r}")
        students = (
            sb.table("students")
            .select("id,profile_id,board_roll_no,branch,semester")
            .eq("branch", branch)
            .eq("semester", semester_int)
            .execute()
            .data or []
        )
        print(f"Students found: {len(students)}")
        if students:
            print("First student:", students[0])

    # Also check the student dashboard issue
    # What does the student dashboard query for subjects look like?
    print("\n=== STUDENT SUBJECTS QUERY ===")
    # Pick a student
    stu = sb.table("students").select("*").limit(1).execute().data or []
    if stu:
        s = stu[0]
        branch = s['branch']
        sem = s['semester']
        print(f"Student branch={branch!r}, semester={sem!r}")
        
        subjects = (
            sb.table("teacher_assignments")
            .select("subject_name")
            .eq("branch", branch)
            .eq("semester", sem)
            .execute()
            .data or []
        )
        unique_subjects = list(set(x['subject_name'] for x in subjects))
        print(f"Subjects found ({len(unique_subjects)}): {unique_subjects}")
