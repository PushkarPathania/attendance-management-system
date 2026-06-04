#!/usr/bin/env python3
"""Quick check of teacher profile roles"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin

app = create_app()

with app.app_context():
    sb = get_supabase_admin()
    
    print("Checking teacher profile roles...")
    
    # Get count of teacher profiles
    teacher_profiles = sb.table("profiles").select("id, email, role").eq("role", "teacher").execute().data or []
    print(f"\nTeacher profiles with role='teacher': {len(teacher_profiles)}")
    
    if teacher_profiles:
        print("\nList of teacher profiles:")
        for p in teacher_profiles[:5]:
            print(f"  - {p['email']} (role: {p['role']})")
        if len(teacher_profiles) > 5:
            print(f"  ... and {len(teacher_profiles) - 5} more")
    
    # Get possible teacher email matches
    print("\n\nLooking for teacher accounts (checking teachers table for emails)...")
    teachers = sb.table("teachers").select("id, email, full_name").limit(5).execute().data or []
    print(f"\nTeachers in teachers table: {len(teachers)}")
    
    for t in teachers[:3]:
        email = t['email']
        # Check what profile they have
        profiles = sb.table("profiles").select("id, email, role").ilike("email", email).execute().data or []
        if profiles:
            p = profiles[0]
            print(f"\n{t['full_name']} ({email})")
            print(f"  Profile role: {p.get('role', 'N/A')}")
        else:
            print(f"\n{t['full_name']} ({email})")
            print(f"  Profile role: NOT FOUND")
