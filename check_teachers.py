#!/usr/bin/env python3
"""
Check what teachers are in the database
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_app import create_app

app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("=== Teachers in Database ===\n")

    teachers = sb.table("teachers").select("id,full_name,email,department").execute().data or []
    
    print(f"Total teachers: {len(teachers)}\n")
    
    # Show all teachers with "Rajeev" or similar
    rajeev_teachers = [t for t in teachers if 'rajeev' in t.get('full_name', '').lower() or 'rajeev' in t.get('email', '').lower()]
    
    print("Teachers with 'Rajeev' in name or email:")
    for t in rajeev_teachers:
        print(f"  - {t.get('full_name')} | {t.get('email')} | {t.get('department')}")
    
    print("\n\nAll Computer Engineering Teachers:")
    comp_teachers = [t for t in teachers if t.get('department') == 'Computer Engineering']
    for t in comp_teachers:
        print(f"  - {t.get('full_name')} | {t.get('email')}")
