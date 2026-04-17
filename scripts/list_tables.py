import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app

app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()
    tables_to_check = [
        'profiles', 'teachers', 'students', 'teacher_assignments', 'attendance',
        'teacher_full_view', 'old_teachers', 'users', 'teacher_data'
    ]
    for tbl in tables_to_check:
        try:
            r = sb.table(tbl).select('*').limit(1).execute()
            print(f'EXISTS: {tbl}')
        except Exception as e:
            err = str(e)
            if 'schema cache' in err or 'relation' in err or 'does not exist' in err:
                print(f'MISSING: {tbl}')
            else:
                print(f'ERROR: {tbl} -> {err[:100]}')
