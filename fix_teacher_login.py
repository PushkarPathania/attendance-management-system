#!/usr/bin/env python3
"""
Direct fix: Insert teacher assignments directly via SQL
This bypasses the need for stored procedures
"""

import os
from supabase import create_client

# Load environment
SUPABASE_URL = "https://uezgtcmzrnbwwtdaycmh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVlemd0Y216cm5id3d0ZGF5Y21oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDk0MjMyODgsImV4cCI6MjAyNTAwMzI4OH0.X7zXq5g0D-1LTn1VHxu3Riwvma8nkEu_OwXS6tZaZ3c"

# Test assignment for Surbhi Sharma
TEST_ASSIGNMENTS = [
    {
        "teacher_email": "Surbhisharma.jmi@gmail.com",
        "branch": "Computer Engineering",
        "semester": 2,
        "subject_code": "IT",
        "subject_name": "Introduction to IT",
        "department": "Computer Engineering"
    },
]

def main():
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("[1] Checking current state...")
        
        # Get Surbhi Sharma
        teachers = sb.table("teachers").select("id, email").eq("email", "Surbhisharma.jmi@gmail.com").execute().data
        if not teachers:
            print("✗ Teacher not found")
            return
        
        teacher_id = teachers[0]["id"]
        print(f"✓ Found teacher: {teachers[0]['email']} (id: {teacher_id})")
        
        # Check existing assignments
        assignments = sb.table("teacher_assignments").select("*").eq("teacher_id", teacher_id).execute().data or []
        print(f"  Current assignments: {len(assignments)}")
        if assignments:
            for a in assignments:
                print(f"    - {a['subject_name']} ({a['branch']}, Sem {a['semester']})")
        
        if not assignments:
            print("\n[2] Inserting missing assignments...")
            
            for test_assign in TEST_ASSIGNMENTS:
                data = {
                    "teacher_id": teacher_id,
                    "branch": test_assign["branch"],
                    "semester": test_assign["semester"],
                    "subject_code": test_assign["subject_code"],
                    "subject_name": test_assign["subject_name"],
                    "department": test_assign["department"],
                }
                
                result = sb.table("teacher_assignments").insert(data).execute()
                print(f"✓ Inserted: {test_assign['subject_name']} for {test_assign['branch']}")
            
            print("\n[3] Verifying...")
            assignments_after = sb.table("teacher_assignments").select("*").eq("teacher_id", teacher_id).execute().data or []
            print(f"✓ Now has {len(assignments_after)} assignments")
            for a in assignments_after:
                print(f"    - {a['subject_name']} ({a['branch']}, Sem {a['semester']})")
        else:
            print("\n✓ Teacher already has assignments")
        
        print("\n[SUCCESS] Teacher login should now work!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
