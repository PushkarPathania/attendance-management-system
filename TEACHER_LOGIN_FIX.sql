-- ============================================================
-- FIX SCRIPT FOR TEACHER LOGIN ISSUES
-- Run this in Supabase SQL Editor to fix teacher login
-- ============================================================

-- Step 1: Add missing 'department' column to profiles table
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS department TEXT;

-- Step 2: Verify teacher_assignments table has all needed columns
-- (It should already exist, but we ensure it here)
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

-- Step 3: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_assignments_teacher 
    ON public.teacher_assignments(teacher_id);

CREATE INDEX IF NOT EXISTS idx_assignments_branch_sem 
    ON public.teacher_assignments(branch, semester);

-- Step 4: Verify all required columns exist in teachers table
-- (These should already exist from the schema setup)
-- Just documenting expected columns:
-- - id (UUID, PK)
-- - full_name (TEXT)
-- - email (TEXT, UNIQUE)
-- - mobile (TEXT)
-- - teacher_code (TEXT, UNIQUE)
-- - designation (TEXT)
-- - department (TEXT)
-- - qualification (TEXT)
-- - is_workshop_staff (BOOLEAN)
-- - created_at (TIMESTAMPTZ)

-- Done! Your schema should now be complete for teacher login to work.
