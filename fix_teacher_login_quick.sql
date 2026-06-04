-- ============================================================
-- QUICK FIX: Ensure all teachers have subject assignments
-- Run this in Supabase SQL Editor
-- ============================================================

-- First, verify teachers table has data
SELECT 'STEP 1: CHECK TEACHERS' as step, COUNT(*) as teacher_count FROM public.teachers;

-- Check if Rajeev Kumar exists
SELECT 'STEP 2: RAJEEV KUMAR' as step, id, full_name, email FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com';

-- Check existing assignments
SELECT 'STEP 3: EXISTING ASSIGNMENTS' as step, COUNT(*) as assignment_count FROM public.teacher_assignments;

-- Check if Rajeev Kumar has any assignments
SELECT 'STEP 4: RAJEEV ASSIGNMENTS' as step, ta.* FROM public.teacher_assignments ta
WHERE ta.teacher_id = (SELECT id FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com' LIMIT 1);

-- ============================================================
-- MAIN FIX: Insert all teacher assignments
-- ============================================================
INSERT INTO public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department)
SELECT id, 'Computer Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Kchand78@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Saroop2388@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Surbhisharma.jmi@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'avinash@example.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Varunknr72@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'pragsharma@gmail.com'

UNION ALL SELECT id, 'Computer Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Saroop2388@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Kchand78@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'

ON CONFLICT (teacher_id, branch, semester, subject_code) DO NOTHING;

-- ============================================================
-- VERIFICATION
-- ============================================================
SELECT 'STEP 5: AFTER FIX - RAJEEV ASSIGNMENTS' as step, COUNT(*) as assignment_count 
FROM public.teacher_assignments 
WHERE teacher_id = (SELECT id FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com' LIMIT 1);

SELECT 'STEP 6: TOTAL ASSIGNMENTS AFTER FIX' as step, COUNT(*) as total_assignments FROM public.teacher_assignments;

-- List all teachers with their assignment counts
SELECT 'STEP 7: TEACHERS WITH ASSIGNMENTS' as step, t.full_name, t.email, COUNT(ta.id) as assignment_count
FROM public.teachers t
LEFT JOIN public.teacher_assignments ta ON ta.teacher_id = t.id
GROUP BY t.id, t.full_name, t.email
ORDER BY assignment_count DESC;
