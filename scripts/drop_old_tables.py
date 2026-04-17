import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== Dropping old_teachers table via RPC ===")
    try:
        # Supabase doesn't expose DROP TABLE directly via the REST API.
        # We need to use rpc or direct SQL. Try rpc execute_sql if available.
        result = sb.rpc("execute_sql", {"sql": "DROP TABLE IF EXISTS old_teachers CASCADE;"}).execute()
        print("Dropped via RPC:", result)
    except Exception as e1:
        print(f"RPC failed: {e1}")
        # Fallback: delete all rows instead (cannot drop but can empty it)
        try:
            # Count rows first
            cnt = sb.table("old_teachers").select("*", count="exact").execute()
            print(f"old_teachers has {cnt.count} rows - deleting all...")
            sb.table("old_teachers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print("All rows deleted from old_teachers (table still exists but is empty)")
        except Exception as e2:
            print(f"Delete fallback also failed: {e2}")
            print("\nNOTE: To drop old_teachers, run this in Supabase SQL Editor:")
            print("  DROP TABLE IF EXISTS old_teachers CASCADE;")
