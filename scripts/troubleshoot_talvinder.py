import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD", "ChangeMe@123")
app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    email_lower = "talvinder.mr@gmail.com".lower()
    
    print(f"Checking {email_lower}...")
    
    # 1. Check if profile exists
    existing = sb.table("profiles").select("id").ilike("email", email_lower).limit(1).execute().data or []
    if existing:
        print(f"Profile exists with ID: {existing[0]['id']}")
    else:
        print("Profile does NOT exist.")

    # 2. Try to get user via list_users 
    try:
        auth_users_resp = sb.auth.admin.list_users()
        users = getattr(auth_users_resp, 'users', [])
        if not users and isinstance(auth_users_resp, list):
            users = auth_users_resp
            
        matched_user = None
        for u in users:
            u_email = (getattr(u, "email", "") or "").lower()
            if u_email == email_lower:
                matched_user = u
                break
                
        if matched_user:
            print(f"Auth user exists with ID: {matched_user.id}")
        else:
            print("Auth user does NOT exist in the first page of list_users().")
            
        # Try to just sign up / create user
        try:
            result = sb.auth.admin.create_user({
                "email": email_lower,
                "password": DEFAULT_PASSWORD,
                "email_confirm": True,
                "user_metadata": {"role": "teacher"},
            })
            print(f"Created new Auth user with ID: {result.user.id}")
        except Exception as e:
            print(f"Failed to create new Auth user: {e}")
            
    except Exception as e:
        print(f"Error accessing auth: {e}")
