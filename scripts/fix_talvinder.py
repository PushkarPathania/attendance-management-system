import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app
app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print(f"Fixing Talvinder...")

    profiles = sb.table('profiles').select('*').ilike('email', '%talvinder%').execute().data
    print(f"Profiles:")
    for p in profiles: print(p)

    teachers = sb.table('teachers').select('*').ilike('email', '%talvinder.mr%').execute().data
    print(f"Teachers:")
    for t in teachers: print(t)

    if profiles:
        user_id = profiles[0]['id']
        print(f"Found User ID in profiles: {user_id}. Resetting password...")
        try:
            res = sb.auth.admin.update_user_by_id(user_id, {"password": "ChangeMe@123"})
            print(f"Password reset success!")
        except Exception as e:
            print(f"Password reset failed: {e}")
    else:
        print("Profile not found.")
