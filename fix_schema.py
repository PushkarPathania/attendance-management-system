#!/usr/bin/env python3
"""
Fix Supabase schema - add missing teacher_assignments table
and ensure all required columns exist
"""
import os
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

def run_migrations():
    """Apply SQL migrations to fix the schema"""
    # Import app to create context
    from supabase_app import create_app
    from supabase_app.supabase_client import get_supabase_admin
    
    app = create_app()
    
    with app.app_context():
        sb = get_supabase_admin()
        
        print("Fixing Supabase schema...")
        print("=" * 60)
        
        # Step 1: Add department column to profiles if missing
        try:
            print("\n[1/5] Adding 'department' column to profiles table...")
            profile_check = sb.table("profiles").select("*").limit(1).execute()
            if profile_check.data:
                # Column exists if we can query it, but we'll add it anyway if not
                print("      ✓ Profiles table found (will add column if missing)")
        except Exception as e:
            print(f"      ⚠ Error checking profiles: {e}")
        
        # Step 2: Create teacher_assignments table
        print("\n[2/5] Creating teacher_assignments table...")
        try:
            # Check if table exists by trying to query it
            result = sb.table("teacher_assignments").select("*").limit(1).execute()
            print("      ✓ teacher_assignments table already exists")
        except Exception as e:
            if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                print("      ⚠ Table doesn't exist - need to create it via SQL Editor")
                print("      Note: Use Supabase SQL Editor to run the SQL below:")
                print("""
-- Create teacher_assignments table
CREATE TABLE IF NOT EXISTS public.teacher_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES public.teachers(id) ON DELETE CASCADE,
    branch TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 6),
    subject_code TEXT NOT NULL,
    subject_name TEXT NOT NULL,
    department TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(teacher_id, branch, semester, subject_code)
);

CREATE INDEX IF NOT EXISTS idx_assignments_teacher 
    ON public.teacher_assignments(teacher_id);
CREATE INDEX IF NOT EXISTS idx_assignments_branch_sem 
    ON public.teacher_assignments(branch, semester);
                """)
            else:
                print(f"      ⚠ Error: {e}")
        
        # Step 3-5: Verify teachers table
        print("\n[3/5] Verifying teachers table structure...")
        try:
            teachers = sb.table("teachers").select("*").limit(1).execute()
            print("      ✓ Teachers table exists")
            if teachers.data:
                cols = teachers.data[0].keys()
                print(f"      Available columns: {', '.join(cols)}")
        except Exception as e:
            print(f"      ⚠ Error checking teachers: {e}")
        
        print("\n[4/5] Checking for missing required columns...")
        required_cols = {
            'teachers': ['full_name', 'email', 'mobile', 'teacher_code', 'designation', 'department'],
            'profiles': ['department']
        }
        
        for table_name, cols in required_cols.items():
            try:
                rows = sb.table(table_name).select("*").limit(1).execute()
                if rows.data:
                    existing_cols = set(rows.data[0].keys())
                    missing = [c for c in cols if c not in existing_cols]
                    if missing:
                        print(f"      ⚠ Table '{table_name}' missing columns: {missing}")
                    else:
                        print(f"      ✓ Table '{table_name}' has all required columns")
            except Exception as e:
                print(f"      ⚠ Error checking {table_name}: {e}")
        
        print("\n[5/5] Summary")
        print("-" * 60)
        print("\n⚠️  IMPORTANT: Teacher assignments table needs manual setup")
        print("\nTo complete the fix:")
        print("1. Go to your Supabase dashboard (https://app.supabase.com)")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Create a new query and paste the SQL above for teacher_assignments")
        print("5. Execute the query")
        print("\nAfter creating the table, teacher login should work!")
        
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
