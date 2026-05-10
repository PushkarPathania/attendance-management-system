from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()
    
    a = sb.table("teacher_assignments").select("id").execute().data or []
    print(f"Total assignments: {len(a)}")
