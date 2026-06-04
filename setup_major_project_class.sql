-- ============================================================
-- SETUP: Major Project Class - Computer Engineering Sem 6
-- Teacher: Rajeev Kumar (Rajeev.kumar357@gmail.com)
-- Students: 25 students
-- Run this in Supabase SQL Editor
-- ============================================================

-- ============================================================
-- STEP 1: Ensure Rajeev Kumar teacher record exists
-- ============================================================
INSERT INTO public.teachers (full_name, email, mobile, designation, qualification, department, is_workshop_staff)
VALUES ('Rajeev Kumar', 'Rajeev.kumar357@gmail.com', '9298286002', 'Lecturer', 'B.Tech.', 'Computer Engineering', false)
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- STEP 2: Create Major Project assignment for Rajeev Kumar
-- ============================================================
INSERT INTO public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department)
SELECT 
  id,
  'Computer Engineering',
  6,
  'MAJOR-PROJECT',
  'Major Project',
  'Computer Engineering'
FROM public.teachers 
WHERE email = 'Rajeev.kumar357@gmail.com'
ON CONFLICT (teacher_id, branch, semester, subject_code) DO NOTHING;

-- ============================================================
-- STEP 3: Create student profiles (25 students)
-- ============================================================
INSERT INTO public.profiles (full_name, email, role, department, created_at)
VALUES
  ('AARUSH KOUNDAL', 'aarush.koundal.230810404001@student.edu', 'student', 'Computer Engineering', now()),
  ('ADITYA', 'aditya.230810404004@student.edu', 'student', 'Computer Engineering', now()),
  ('ADITYA', 'aditya.230810404003@student.edu', 'student', 'Computer Engineering', now()),
  ('ADITYA THAKUR', 'aditya.thakur.230810404005@student.edu', 'student', 'Computer Engineering', now()),
  ('ADITYA KATOCH', 'aditya.katoch.230810404006@student.edu', 'student', 'Computer Engineering', now()),
  ('ADITYA SHARMA', 'aditya.sharma.230810404007@student.edu', 'student', 'Computer Engineering', now()),
  ('AKARSHIT MEHRA', 'akarshit.mehra.230810404008@student.edu', 'student', 'Computer Engineering', now()),
  ('AKSHARA THAKUR', 'akshara.thakur.230810404009@student.edu', 'student', 'Computer Engineering', now()),
  ('AKSHIT SHARMA', 'akshit.sharma.230810404010@student.edu', 'student', 'Computer Engineering', now()),
  ('ANKITA', 'ankita.230810404011@student.edu', 'student', 'Computer Engineering', now()),
  ('AREEN', 'areen.230810404015@student.edu', 'student', 'Computer Engineering', now()),
  ('ARYAN DHIMAN', 'aryan.dhiman.230810404016@student.edu', 'student', 'Computer Engineering', now()),
  ('ARYAN JAMWAL', 'aryan.jamwal.230810404017@student.edu', 'student', 'Computer Engineering', now()),
  ('AYUSH', 'ayush.230810404018@student.edu', 'student', 'Computer Engineering', now()),
  ('BANSHUL KUMAR', 'banshul.kumar.230810404019@student.edu', 'student', 'Computer Engineering', now()),
  ('DIKSHA CHAUHAN', 'diksha.chauhan.230810404020@student.edu', 'student', 'Computer Engineering', now()),
  ('DIVYANSHI', 'divyanshi.230810404022@student.edu', 'student', 'Computer Engineering', now()),
  ('HARSH', 'harsh.230810404024@student.edu', 'student', 'Computer Engineering', now()),
  ('HARSH', 'harsh.230810404023@student.edu', 'student', 'Computer Engineering', now()),
  ('HARSHIT KAPOOR', 'harshit.kapoor.230810404025@student.edu', 'student', 'Computer Engineering', now()),
  ('ISHA KUMARI', 'isha.kumari.230810404026@student.edu', 'student', 'Computer Engineering', now()),
  ('ISHAAN KUMAR', 'ishaan.kumar.230810404027@student.edu', 'student', 'Computer Engineering', now()),
  ('MUSKAN CHOUDHARY', 'muskan.choudhary.230810404028@student.edu', 'student', 'Computer Engineering', now()),
  ('PIYUSH', 'piyush.230810404031@student.edu', 'student', 'Computer Engineering', now()),
  ('PRIYA', 'priya.230810404032@student.edu', 'student', 'Computer Engineering', now())
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- STEP 4: Create student records with board roll numbers
-- ============================================================
INSERT INTO public.students (profile_id, board_roll_no, branch, semester)
SELECT p.id, '230810404001', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aarush.koundal.230810404001@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404004', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aditya.230810404004@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404003', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aditya.230810404003@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404005', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aditya.thakur.230810404005@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404006', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aditya.katoch.230810404006@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404007', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aditya.sharma.230810404007@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404008', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'akarshit.mehra.230810404008@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404009', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'akshara.thakur.230810404009@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404010', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'akshit.sharma.230810404010@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404011', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'ankita.230810404011@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404015', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'areen.230810404015@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404016', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aryan.dhiman.230810404016@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404017', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'aryan.jamwal.230810404017@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404018', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'ayush.230810404018@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404019', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'banshul.kumar.230810404019@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404020', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'diksha.chauhan.230810404020@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404022', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'divyanshi.230810404022@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404024', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'harsh.230810404024@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404023', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'harsh.230810404023@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404025', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'harshit.kapoor.230810404025@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404026', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'isha.kumari.230810404026@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404027', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'ishaan.kumar.230810404027@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404028', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'muskan.choudhary.230810404028@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404031', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'piyush.230810404031@student.edu' LIMIT 1
UNION ALL SELECT p.id, '230810404032', 'Computer Engineering', 6 FROM public.profiles p WHERE p.email = 'priya.230810404032@student.edu' LIMIT 1
ON CONFLICT (board_roll_no, branch, semester) DO NOTHING;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
SELECT '✓ TEACHER' as check_type, COUNT(*) as count FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com';

SELECT '✓ ASSIGNMENT' as check_type, COUNT(*) as count FROM public.teacher_assignments 
WHERE subject_code = 'MAJOR-PROJECT' AND branch = 'Computer Engineering' AND semester = 6;

SELECT '✓ STUDENTS' as check_type, COUNT(*) as count FROM public.students 
WHERE branch = 'Computer Engineering' AND semester = 6;

SELECT '✓ CLASS INFO' as check_type,
  (SELECT full_name FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com') as teacher,
  'Major Project' as subject,
  'Computer Engineering' as branch,
  6 as semester,
  COUNT(*) as student_count
FROM public.students 
WHERE branch = 'Computer Engineering' AND semester = 6
GROUP BY teacher, subject, branch, semester;
