from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()
    
    teachers = sb.table("teachers").select("*").execute().data or []
    assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    ids_with = set(a["teacher_id"] for a in assignments)
    
    orphans = [t for t in teachers if t["id"] not in ids_with]
    print(f"Deleting {len(orphans)} orphan teachers with 0 assignments...")
    
    deleted = 0
    for o in orphans:
        print(f"  Deleting: {o['full_name']} ({o['email']})")
        # Delete profile
        profiles = sb.table("profiles").select("id").eq("email", o["email"]).execute().data or []
        for p in profiles:
            try:
                sb.auth.admin.delete_user(p["id"])
            except Exception:
                pass
            sb.table("profiles").delete().eq("id", p["id"]).execute()
        
        # Delete teacher
        sb.table("teachers").delete().eq("id", o["id"]).execute()
        deleted += 1
        
    print(f"Done. Deleted {deleted} orphans.")
    
    # Final check
    t_after = sb.table("teachers").select("id").execute().data or []
    print(f"Total teachers remaining: {len(t_after)}")
