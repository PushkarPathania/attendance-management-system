from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    # The old schema has attendance.teacher_id -> teachers.id
    # But the new code uses assignment_id. Check what actual columns exist in attendance
    # by checking via the API
    
    # Check if teacher_full_view exists
    print("=== CHECKING teacher_full_view ===")
    try:
        tfv = sb.table("teacher_full_view").select("*").limit(1).execute().data
        if tfv:
            print("Columns:", list(tfv[0].keys()))
        else:
            print("View exists but empty")
    except Exception as e:
        print(f"ERROR: {e}")

    # Check teachers table columns
    print("\n=== TEACHERS TABLE ===")
    t = sb.table("teachers").select("*").limit(1).execute().data
    if t:
        print("Columns:", list(t[0].keys()))

    # Check if the students.semester field is stored as integer or text
    print("\n=== STUDENT SEMESTER TYPE ===")
    stu = sb.table("students").select("semester").limit(3).execute().data or []
    for s in stu:
        print(f"  semester={s['semester']!r}  type={type(s['semester']).__name__}")
