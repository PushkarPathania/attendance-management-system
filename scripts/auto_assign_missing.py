import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== Finding teachers without assignments ===")
    
    # Get all teachers
    teachers = sb.table("teachers").select("id,email,full_name,department").execute().data or []
    
    # Get all assigned teacher ids
    assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    assigned_ids = {a["teacher_id"] for a in assignments}
    
    # Identify missing
    missing_teachers = [t for t in teachers if t["id"] not in assigned_ids]
    
    print(f"Adding default 'General' assignments for {len(missing_teachers)} teachers...")
    
    fixed = 0
    failed = 0
    
    for t in missing_teachers:
        try:
            sb.table("teacher_assignments").upsert({
                "teacher_id": t["id"],
                "branch": "General",
                "semester": 1,
                "subject_code": "GEN-101",
                "subject_name": "General Assignment",
                "department": t.get("department", "General") or "General"
            }).execute()
            fixed += 1
            print(f"  [ASSIGNED] {t['full_name']} ({t['email']})")
        except Exception as e:
            failed += 1
            print(f"  [ERROR] {t['full_name']}: {e}")
            
    print(f"\nCompleted! Fixed: {fixed}, Failed: {failed}")
