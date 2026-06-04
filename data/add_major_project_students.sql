-- ============================================================
-- ADD 25 STUDENTS TO RAJEEV KUMAR'S MAJOR PROJECT (SEM 6 - COMPUTER ENGINEERING)
-- Run this in Supabase SQL Editor
-- ============================================================

-- ============================================================
-- STEP 1: Ensure Rajeev Kumar has Major Project assignment
-- ============================================================
INSERT INTO public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department)
SELECT 
  (SELECT id FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com'),
  'Computer Engineering',
  6,
  'MAJOR-PROJECT',
  'Major Project',
  'Computer Engineering'
WHERE NOT EXISTS (
  SELECT 1 FROM public.teacher_assignments 
  WHERE teacher_id = (SELECT id FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com')
  AND branch = 'Computer Engineering'
  AND semester = 6
  AND subject_code = 'MAJOR-PROJECT'
);

-- ============================================================
-- STEP 2 & 3: Create profiles and students in one transaction
-- Using CTE to ensure proper linking
-- ============================================================
WITH new_profiles AS (
  INSERT INTO public.profiles (full_name, email, role, department, created_at)
  VALUES
    ('AARUSH KOUNDAL', 'aarush.koundal230810404001@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ADITYA', 'aditya230810404004@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ADITYA', 'aditya230810404003@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ADITYA THAKUR', 'aditya.thakur230810404005@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ADITYA KATOCH', 'aditya.katoch230810404006@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ADITYA SHARMA', 'aditya.sharma230810404007@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('AKARSHIT MEHRA', 'akarshit.mehra230810404008@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('AKSHARA THAKUR', 'akshara.thakur230810404009@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('AKSHIT SHARMA', 'akshit.sharma230810404010@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ANKITA', 'ankita230810404011@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('AREEN', 'areen230810404015@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ARYAN DHIMAN', 'aryan.dhiman230810404016@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ARYAN JAMWAL', 'aryan.jamwal230810404017@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('AYUSH', 'ayush230810404018@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('BANSHUL KUMAR', 'banshul.kumar230810404019@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('DIKSHA CHAUHAN', 'diksha.chauhan230810404020@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('DIVYANSHI', 'divyanshi230810404022@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('HARSH', 'harsh230810404024@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('HARSH', 'harsh230810404023@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('HARSHIT KAPOOR', 'harshit.kapoor230810404025@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ISHA KUMARI', 'isha.kumari230810404026@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('ISHAAN KUMAR', 'ishaan.kumar230810404027@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('MUSKAN CHOUDHARY', 'muskan.choudhary230810404028@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('PIYUSH', 'piyush230810404031@student.gpkangra.edu.in', 'student', 'Computer Engineering', now()),
    ('PRIYA', 'priya230810404032@student.gpkangra.edu.in', 'student', 'Computer Engineering', now())
  ON CONFLICT (email) DO UPDATE SET full_name = EXCLUDED.full_name
  RETURNING id, email
)
INSERT INTO public.students (profile_id, board_roll_no, branch, semester)
VALUES
  ((SELECT id FROM new_profiles WHERE email = 'aarush.koundal230810404001@student.gpkangra.edu.in'), '230810404001', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aditya230810404004@student.gpkangra.edu.in'), '230810404004', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aditya230810404003@student.gpkangra.edu.in'), '230810404003', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aditya.thakur230810404005@student.gpkangra.edu.in'), '230810404005', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aditya.katoch230810404006@student.gpkangra.edu.in'), '230810404006', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aditya.sharma230810404007@student.gpkangra.edu.in'), '230810404007', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'akarshit.mehra230810404008@student.gpkangra.edu.in'), '230810404008', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'akshara.thakur230810404009@student.gpkangra.edu.in'), '230810404009', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'akshit.sharma230810404010@student.gpkangra.edu.in'), '230810404010', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'ankita230810404011@student.gpkangra.edu.in'), '230810404011', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'areen230810404015@student.gpkangra.edu.in'), '230810404015', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aryan.dhiman230810404016@student.gpkangra.edu.in'), '230810404016', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'aryan.jamwal230810404017@student.gpkangra.edu.in'), '230810404017', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'ayush230810404018@student.gpkangra.edu.in'), '230810404018', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'banshul.kumar230810404019@student.gpkangra.edu.in'), '230810404019', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'diksha.chauhan230810404020@student.gpkangra.edu.in'), '230810404020', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'divyanshi230810404022@student.gpkangra.edu.in'), '230810404022', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'harsh230810404024@student.gpkangra.edu.in'), '230810404024', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'harsh230810404023@student.gpkangra.edu.in'), '230810404023', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'harshit.kapoor230810404025@student.gpkangra.edu.in'), '230810404025', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'isha.kumari230810404026@student.gpkangra.edu.in'), '230810404026', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'ishaan.kumar230810404027@student.gpkangra.edu.in'), '230810404027', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'muskan.choudhary230810404028@student.gpkangra.edu.in'), '230810404028', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'piyush230810404031@student.gpkangra.edu.in'), '230810404031', 'Computer Engineering', 6),
  ((SELECT id FROM new_profiles WHERE email = 'priya230810404032@student.gpkangra.edu.in'), '230810404032', 'Computer Engineering', 6)
ON CONFLICT (board_roll_no, branch, semester) DO NOTHING;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- Check that assignment was created
SELECT 'Teacher Assignment' as check_type, COUNT(*) as count FROM public.teacher_assignments 
WHERE subject_code = 'MAJOR-PROJECT' 
AND branch = 'Computer Engineering' 
AND semester = 6;

-- Check that students were created
SELECT 'Total Students' as check_type, COUNT(*) as count FROM public.students 
WHERE branch = 'Computer Engineering' AND semester = 6;

-- Show students linked to Rajeev Kumar's Major Project class
SELECT 
  'Student List' as check_type,
  s.board_roll_no,
  p.full_name,
  s.branch,
  s.semester
FROM public.students s
JOIN public.profiles p ON s.profile_id = p.id
WHERE s.branch = 'Computer Engineering' AND s.semester = 6
ORDER BY s.board_roll_no;
