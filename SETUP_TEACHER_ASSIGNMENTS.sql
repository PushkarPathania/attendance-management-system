-- ============================================================
-- SETUP SCRIPT: INSERT ALL TEACHER ASSIGNMENTS
-- RUN THIS IN SUPABASE SQL EDITOR (Ace Editor)
-- This populates the teacher_assignments table for all teachers
-- ============================================================

-- Step 1: Verify teacher_assignments table exists
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'teacher_assignments') THEN
    RAISE EXCEPTION 'teacher_assignments table does not exist. Run schema setup first.';
  END IF;
END $$;

-- Step 2: Insert all subject assignments for teachers
-- This uses UNION ALL to dynamically link teachers by email
INSERT INTO public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department)
SELECT id, 'Computer Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Kchand78@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Saroop2388@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Surbhisharma.jmi@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Instrumentation Engineering' FROM public.teachers WHERE email = 'Varunknr72@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering' FROM public.teachers WHERE email = 'pragsharma@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Electrical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'kumariindu@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'adityasaklani@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering' FROM public.teachers WHERE email = 'satbirguru@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Kchand78@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Thakurviju454@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Avinash.acet@yahoo.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'Guptaina24@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'EM', 'Engineering Mechanics', 'Instrumentation Engineering' FROM public.teachers WHERE email = 'Ritika30purohit@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'kumariindu@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'jela.b89@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'EWS', 'Engineering Workshop', 'Workshop' FROM public.teachers WHERE email = 'Pawankumar64399@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'EM', 'Engineering Mechanics', 'Instrumentation Engineering' FROM public.teachers WHERE email = 'Pawanchandel13@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Mechanical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Thakurviju454@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'Guptaina24@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'EWS', 'Engineering Workshop', 'Workshop' FROM public.teachers WHERE email = 'workshopstaff@gpkangra.edu.in'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering' FROM public.teachers WHERE email = 'satbirguru@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'
ON CONFLICT (teacher_id, branch, semester, subject_code) DO NOTHING;

-- Step 3: Verify the insertion
SELECT 
  'Total assignments inserted/updated' as status,
  COUNT(*) as count
FROM public.teacher_assignments;

-- Step 4: Show assignments per teacher (sample)
SELECT 
  t.full_name,
  t.email,
  COUNT(ta.id) as assignment_count,
  STRING_AGG(ta.subject_name, ', ' ORDER BY ta.subject_name) as subjects
FROM public.teachers t
LEFT JOIN public.teacher_assignments ta ON t.id = ta.teacher_id
GROUP BY t.id, t.full_name, t.email
ORDER BY assignment_count DESC, t.full_name;
