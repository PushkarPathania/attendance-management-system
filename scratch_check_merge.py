from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()
with app.app_context():
    sb = get_supabase_admin()
    
    # Check assignments for Rajesh Sharma
    a = sb.table("teacher_assignments").select("*").eq("teacher_id", "06ade1e4-966d-4913-b541-4c1265ca592e").execute().data or []
    print(f"Rajesh Sharma assignments: {len(a)}")
    
    # Check if there are other teachers with this email
    t = sb.table("teachers").select("id, full_name, email").eq("email", "rsharma72@gmail.com").execute().data or []
    print(f"Teachers with rsharma72@gmail.com:")
    for x in t:
        print(f"  {x['full_name']} id={x['id']} has {len(sb.table('teacher_assignments').select('*').eq('teacher_id', x['id']).execute().data or [])} assignments")
