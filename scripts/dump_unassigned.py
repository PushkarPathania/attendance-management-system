import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_app import create_app
app = create_app()
with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()
    
    dummy = sb.table('teacher_assignments').select('teacher_id').eq('subject_code', 'GEN-101').execute().data or []
    t_ids = [d['teacher_id'] for d in dummy]
    
    if not t_ids:
        print('No unassigned teachers found.')
    else:
        res = sb.table('teachers').select('full_name, email').in_('id', t_ids).execute().data or []
        with open('unassigned_teachers.txt', 'w', encoding='utf-8') as f:
            for r in sorted(res, key=lambda x: x['full_name']):
                f.write(f"- {r['full_name']} ({r['email']})\n")
        print('Wrote unassigned_teachers.txt')
