"""Clean up orphan teacher records that have no assignments and duplicate N/A teacher_codes."""
from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    teachers = sb.table("teachers").select("id, full_name, email, teacher_code").execute().data or []
    assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []

    teacher_ids_with_assignments = set(a["teacher_id"] for a in assignments)
    
    orphans = [t for t in teachers if t["id"] not in teacher_ids_with_assignments]
    print(f"Teachers: {len(teachers)}, With assignments: {len(teacher_ids_with_assignments)}, Orphans: {len(orphans)}")
    
    for o in orphans:
        print(f"  Orphan: {o['full_name']} ({o['email']}) code={o['teacher_code']}")

    # Also check for duplicate teacher_codes
    codes = {}
    for t in teachers:
        code = t.get("teacher_code", "")
        if code in codes:
            print(f"  DUPLICATE CODE '{code}': {t['full_name']} vs {codes[code]['full_name']}")
        else:
            codes[code] = t
