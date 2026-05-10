"""Check remaining orphans and try to match Tamanna and Sanjeev."""
from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import uuid

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    teachers = sb.table("teachers").select("*").execute().data or []
    assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    ids_with = set(a["teacher_id"] for a in assignments)
    
    orphans = [t for t in teachers if t["id"] not in ids_with]
    active = [t for t in teachers if t["id"] in ids_with]
    
    print(f"=== {len(orphans)} ORPHANS REMAINING ===")
    for o in orphans:
        print(f"  {o['full_name']:30s} {o['email']:40s} id={o['id'][:8]}")
    
    print(f"\n=== ACTIVE TEACHERS (with assignments) ===")
    # Find Tamanna and Sanjeev in active
    for a in active:
        name = a['full_name'].lower()
        if 'tamanna' in name or 'sanjeev' in name:
            print(f"  {a['full_name']:30s} {a['email']:40s} id={a['id'][:8]}")
