#!/usr/bin/env python3
"""
Fix missing teacher assignments in Supabase
Inserts teacher assignments if they're missing
"""

from supabase import create_client
import os
import sys

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://uezgtcmzrnbwwtdaycmh.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVlemd0Y216cm5id3d0ZGF5Y21oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDk0MjMyODgsImV4cCI6MjAyNTAwMzI4OH0.X7zXq5g0D-1LTn1VHxu3Riwvma8nkEu_OwXS6tZaZ3c")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("[1] Checking teacher assignments...")

# Get all teachers
teachers = sb.table("teachers").select("id, email, full_name").execute().data or []
print(f"    Found {len(teachers)} teachers")

# Get existing assignments
assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
assigned_teacher_ids = {a["teacher_id"] for a in assignments}
print(f"    Found {len(assigned_teacher_ids)} teachers with assignments")

# Find teachers without assignments
unassigned = [t for t in teachers if t["id"] not in assigned_teacher_ids]
print(f"    Found {len(unassigned)} teachers without assignments")

if unassigned:
    print("\n[2] Teachers without assignments:")
    for t in unassigned:
        print(f"    - {t['full_name']} ({t['email']})")
    
    print("\n[3] Running insert_teachers_data.sql to fix assignments...")
    
    # Read the SQL file
    with open("data/insert_teachers_data.sql", "r") as f:
        sql_content = f.read()
    
    # Extract just the teacher_assignments insert part
    # Find the line starting with "INSERT INTO public.teacher_assignments"
    lines = sql_content.split('\n')
    insert_start = None
    insert_end = None
    
    for i, line in enumerate(lines):
        if 'INSERT INTO public.teacher_assignments' in line:
            insert_start = i
        if insert_start is not None and line.strip().endswith('DO NOTHING;'):
            insert_end = i + 1
            break
    
    if insert_start is not None and insert_end is not None:
        assignment_sql = '\n'.join(lines[insert_start:insert_end])
        
        try:
            # Execute via admin client to bypass RLS
            result = sb.rpc("sql_exec", {"sql": assignment_sql}).execute()
            print(f"    ✓ Executed assignment insert query")
            
            # Verify
            assignments_after = sb.table("teacher_assignments").select("teacher_id").execute().data or []
            assigned_after = {a["teacher_id"] for a in assignments_after}
            print(f"    ✓ Now have {len(assigned_after)} teachers with assignments")
            
            # Check unassigned teachers again
            still_unassigned = [t for t in unassigned if t["id"] not in assigned_after]
            if still_unassigned:
                print(f"\n⚠ Still {len(still_unassigned)} teachers without assignments:")
                for t in still_unassigned:
                    print(f"    - {t['full_name']} ({t['email']})")
            else:
                print("\n✓ All teachers now have assignments!")
                
        except Exception as e:
            print(f"    ✗ Error executing query: {e}")
            print(f"    Trying direct query execution...")
            try:
                sb.query(assignment_sql).execute()
                print(f"    ✓ Executed via direct query")
            except Exception as e2:
                print(f"    ✗ Direct query also failed: {e2}")
    else:
        print("    ✗ Could not find assignment insert section in SQL file")
else:
    print("\n✓ All teachers have assignments!")

print("\n[4] Summary:")
final_assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
final_assigned = {a["teacher_id"] for a in final_assignments}
final_unassigned = [t for t in teachers if t["id"] not in final_assigned]

print(f"    Total teachers: {len(teachers)}")
print(f"    With assignments: {len(final_assigned)}")
print(f"    Without assignments: {len(final_unassigned)}")

if final_unassigned:
    print(f"\n    Unassigned teachers:")
    for t in final_unassigned:
        print(f"    - {t['email']}")
