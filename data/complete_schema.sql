-- ============================================================
-- GOVERNMENT POLYTECHNIC KANGRA
-- ATTENDANCE MANAGEMENT SYSTEM - COMPLETE DATABASE SETUP
-- Generated for: All Departments, All Semesters (1-6)
-- ============================================================

-- ============================================================
-- STEP 1: EXTENSIONS & ENUMS
-- ============================================================
create extension if not exists "pgcrypto";

do $$
begin
  if not exists (select 1 from pg_type where typname = 'user_role') then
    create type user_role as enum ('student', 'teacher', 'admin');
  end if;
end$$;

-- ============================================================
-- STEP 2: DROP OLD TABLES & VIEWS (clean slate)
-- ============================================================
drop view if exists public.teachers_computer cascade;
drop view if exists public.teachers_electronics cascade;
drop view if exists public.teachers_electrical cascade;
drop view if exists public.teachers_instrumentation cascade;
drop view if exists public.teachers_mechanical cascade;
drop view if exists public.teachers_civil_engineering cascade;
drop view if exists public.teacher_full_view cascade;
drop function if exists public.get_teachers_by_branch(text) cascade;
drop table if exists public.attendance cascade;
drop table if exists public.teacher_assignments cascade;
drop table if exists public.workshop_teachers cascade;
drop table if exists public.teachers cascade;
drop table if exists public.students cascade;
drop table if exists public.profiles cascade;

-- ============================================================
-- STEP 3: PROFILES TABLE (auth identity for all users)
-- ============================================================
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  email text not null unique,
  role user_role not null,
  department text,
  avatar_url text,
  created_at timestamptz not null default now()
);

-- ============================================================
-- STEP 4: TEACHERS TABLE (one row per teacher - personal info)
-- ============================================================
create table if not exists public.teachers (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  email text not null unique,
  mobile text,
  teacher_code text unique,
  designation text,
  qualification text,
  department text not null,
  is_workshop_staff boolean not null default false,
  created_at timestamptz not null default now()
);

-- ============================================================
-- STEP 5: TEACHER ASSIGNMENTS TABLE
-- (one row per teacher × branch × semester × subject)
-- ============================================================
create table if not exists public.teacher_assignments (
  id uuid primary key default gen_random_uuid(),
  teacher_id uuid not null references public.teachers(id) on delete cascade,
  branch text not null,
  semester integer not null check (semester between 1 and 6),
  subject_code text not null,
  subject_name text not null,
  department text not null,
  created_at timestamptz not null default now(),
  unique(teacher_id, branch, semester, subject_code)
);

-- ============================================================
-- STEP 6: STUDENTS TABLE
-- ============================================================
create table if not exists public.students (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null unique references public.profiles(id) on delete cascade,
  board_roll_no text not null,
  branch text not null,
  semester integer not null check (semester between 1 and 6),
  created_at timestamptz not null default now(),
  constraint students_roll_branch_semester_unique unique (board_roll_no, branch, semester)
);

-- ============================================================
-- STEP 7: ATTENDANCE TABLE
-- ============================================================
create table if not exists public.attendance (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.students(id) on delete cascade,
  assignment_id uuid not null references public.teacher_assignments(id) on delete restrict,
  class_branch text not null,
  class_semester integer not null,
  attendance_date date not null,
  status text not null check (status in ('present', 'absent', 'late')),
  remarks text,
  created_at timestamptz not null default now(),
  unique(student_id, assignment_id, attendance_date)
);

-- ============================================================
-- STEP 8: INDEXES
-- ============================================================
create index if not exists idx_students_branch_sem on public.students(branch, semester);
create index if not exists idx_teachers_dept on public.teachers(department);
create index if not exists idx_assignments_branch_sem on public.teacher_assignments(branch, semester);
create index if not exists idx_assignments_teacher on public.teacher_assignments(teacher_id);
create index if not exists idx_assignments_subject on public.teacher_assignments(subject_name);
create index if not exists idx_attendance_filters on public.attendance(class_branch, class_semester, attendance_date);
create index if not exists idx_attendance_student on public.attendance(student_id, attendance_date);

-- ============================================================
-- STEP 9: USEFUL VIEWS
-- ============================================================

-- Full teacher + assignment view (most used in app)
create or replace view public.teacher_full_view as
select
  t.id as teacher_id,
  t.full_name,
  t.email,
  t.mobile,
  t.designation,
  t.qualification,
  t.department,
  t.is_workshop_staff,
  a.id as assignment_id,
  a.branch,
  a.semester,
  a.subject_code,
  a.subject_name
from public.teachers t
join public.teacher_assignments a on a.teacher_id = t.id;

-- View: get all teachers for a specific branch + semester
create or replace view public.v_sem2_computer as
select * from public.teacher_full_view
where branch = 'Computer Engineering' and semester = 2;

create or replace view public.v_sem2_electrical as
select * from public.teacher_full_view
where branch = 'Electrical Engineering' and semester = 2;

create or replace view public.v_sem2_ece as
select * from public.teacher_full_view
where branch = 'Electronics & Communication Engineering' and semester = 2;

create or replace view public.v_sem2_instrumentation as
select * from public.teacher_full_view
where branch = 'Instrumentation Engineering' and semester = 2;

create or replace view public.v_sem2_mechanical as
select * from public.teacher_full_view
where branch = 'Mechanical Engineering' and semester = 2;

-- ============================================================
-- STEP 10: HELPER FUNCTION
-- ============================================================
create or replace function public.get_teachers_by_branch_semester(
  p_branch text,
  p_semester integer
)
returns table (
  teacher_id uuid,
  full_name text,
  email text,
  mobile text,
  subject_name text,
  subject_code text,
  department text
)
language sql stable as $$
  select
    t.id, t.full_name, t.email, t.mobile,
    a.subject_name, a.subject_code, t.department
  from public.teachers t
  join public.teacher_assignments a on a.teacher_id = t.id
  where lower(a.branch) = lower(p_branch)
    and a.semester = p_semester
  order by t.full_name;
$$;

-- ============================================================
-- STEP 11: INSERT TEACHERS DATA
-- ============================================================

-- -----------------------------------------------------------
-- A) APPLIED SCIENCES & HUMANITIES DEPARTMENT
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0001-000000000001', 'Kamlesh Chand',     'Kchand78@gmail.com',            '9418040815', 'HOD',           'M.Phil.',       'Applied Sciences & Humanities', false),
  ('00000000-0000-0000-0001-000000000002', 'Saroop Chand',      'Saroop2388@gmail.com',           '7018395980', 'Sr. Lecturer',  'M.Sc.',         'Applied Sciences & Humanities', false),
  ('00000000-0000-0000-0001-000000000003', 'Richa Sharma',      'Richathakur121@gmail.com',       '9418025600', 'Lecturer',      'M.Phil.',       'Applied Sciences & Humanities', false),
  ('00000000-0000-0000-0001-000000000004', 'Kumari Indu',       'kumariindu@gmail.com',           null,         'Lecturer',      'M.Sc.',         'Applied Sciences & Humanities', false),
  ('00000000-0000-0000-0001-000000000005', 'Reema Choudhary',   'reemachoudhary@gmail.com',       null,         'Lecturer',      'M.Sc.',         'Applied Sciences & Humanities', false),
  ('00000000-0000-0000-0001-000000000006', 'Vijay Thakur',      'Thakurviju454@gmail.com',        '8091742032', 'Lecturer',      'M.Sc. Physics', 'Applied Sciences & Humanities', false),
  ('00000000-0000-0000-0001-000000000007', 'Anil Kumar',        'prashanil77@gmail.com',          '9459206071', 'Lecturer',      'M.Sc. Chemistry','Applied Sciences & Humanities',false),
  ('00000000-0000-0000-0001-000000000008', 'Pritam Chand',      'pritam777018@gmail.com',         '7018028051', 'Lecturer',      'M.Sc.',         'Applied Sciences & Humanities', false);

-- -----------------------------------------------------------
-- B) COMPUTER ENGINEERING DEPARTMENT
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0002-000000000001', 'N.K. Sapehia',      'nareshshkumarsapehia@gmail.com', '9418479027', 'HOD',           'MCA',           'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000002', 'Talvinder Singh',   'Talvinder.mr@gmail.com',         '9418115042', 'Sr. Lecturer',  'M.Tech.',       'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000003', 'Surbhi Sharma',     'Surbhisharma.jmi@gmail.com',     '7380178778', 'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000004', 'Avinash Sharma',    'Avinash.acet@yahoo.com',         '8091251140', 'Lecturer',      'M.Tech.',       'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000005', 'Rajeev Kumar',      'Rajeev.kumar357@gmail.com',      '9298286002', 'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000006', 'Tamanna Chitra',    'Er.tamanna14@gmail.com',         '8894943678', 'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000007', 'Aashima Sharma',    'aashimasharma@gmail.com',        null,         'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000008', 'Bhupender Kumar',   'bhupenderkumar@gmail.com',       null,         'Computer Assistant','Diploma MCA','Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000009', 'Shweta Dhiman',     'Shweta.neetu@gmail.com',         '9736319180', 'Computer Assistant','Diploma',    'Computer Engineering', false),
  ('00000000-0000-0000-0002-000000000010', 'Dinesh Minhas',     'Dineshsingh744@gmail.com',       '9531484149', 'Computer Assistant','MCA',        'Computer Engineering', false);

-- -----------------------------------------------------------
-- C) ELECTRICAL ENGINEERING DEPARTMENT
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0003-000000000001', 'Rajesh Sharma',     'rdshan72@gmail.com',             '9418050231', 'HOD',           'B.Tech.',       'Electrical Engineering', false),
  ('00000000-0000-0000-0003-000000000002', 'Sudhir Dhiman',     'Sudhir.dhiman85@gmail.com',      '9459055519', 'Sr. Lecturer',  'M.Tech.',       'Electrical Engineering', false),
  ('00000000-0000-0000-0003-000000000003', 'Ina Gupta',         'Guptaina24@gmail.com',           '9418347063', 'Lecturer',      'M.Tech.',       'Electrical Engineering', false),
  ('00000000-0000-0000-0003-000000000004', 'Iela Bharti',       'jela.b89@gmail.com',             '9418347063', 'Lecturer',      'M.Tech.',       'Electrical Engineering', false),
  ('00000000-0000-0000-0004-000000000005', 'Aditya Saklani',    'adityasaklani@gmail.com',        null,         'Lecturer',      'M.Tech.',       'Electrical Engineering', false);

-- -----------------------------------------------------------
-- D) ELECTRONICS & COMMUNICATION ENGINEERING DEPARTMENT
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0004-000000000001', 'Hari Singh Thakur', 'Hsthakur0928@gmail.com',         '9418360465', 'HOD',           'B.Tech.',       'Electronics & Communication Engineering', false),
  ('00000000-0000-0000-0004-000000000002', 'Jagdeep Singh',     'jagdeep9900@gmail.com',          '9816068262', 'Sr. Lecturer',  'B.Tech.',       'Electronics & Communication Engineering', false),
  ('00000000-0000-0000-0004-000000000003', 'Nishant Kaushal',   'nishant125@gmail.com',           '9459125376', 'Lecturer',      'M.Tech.',       'Electronics & Communication Engineering', false),
  ('00000000-0000-0000-0004-000000000004', 'Sachin Sehota',     'sachin.sehotas@gmail.com',       '7018395980', 'Lecturer',      'B.Tech.',       'Electronics & Communication Engineering', false),
  ('00000000-0000-0000-0004-000000000006', 'Rohit Kumar',       'Rohit06@gmail.com',              '9110402870', 'Lecturer',      'M.Tech.',       'Electronics & Communication Engineering', false),
  ('00000000-0000-0000-0004-000000000007', 'Jaswinder Kumar',   'Jaswinder70477@gmail.com',       '8219979429', 'Instructor',    'Diploma',       'Electronics & Communication Engineering', false),
  ('00000000-0000-0000-0004-000000000008', 'Sanjeev Naryal',    'sanjeevnaryal@gmail.com',        '8219298300', 'Instructor',    'CTI NCVT',      'Electronics & Communication Engineering', false);

-- -----------------------------------------------------------
-- E) INSTRUMENTATION ENGINEERING DEPARTMENT
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0005-000000000001', 'Pawan Chandel',     'Pawanchandel13@gmail.com',       '9418636497', 'HOD',           'B.Tech. MBA',   'Instrumentation Engineering', false),
  ('00000000-0000-0000-0005-000000000002', 'Karan Singh Thakur','Karansingh.thakur89@gmail.com',  '9411415029', 'Lecturer',      'M.Tech.',       'Instrumentation Engineering', false),
  ('00000000-0000-0000-0005-000000000003', 'Vikal Sharma',      'vikal.in@gmail.com',             '9411415029', 'Lecturer',      'B.Tech.',       'Instrumentation Engineering', false),
  ('00000000-0000-0000-0005-000000000004', 'Varun',             'Varunknr72@gmail.com',           '9459014868', 'Lecturer',      'M.Tech.',       'Instrumentation Engineering', false),
  ('00000000-0000-0000-0005-000000000005', 'Ritika Sharma',     'Ritika30purohit@gmail.com',      '9736167040', 'Lecturer',      'B.Tech.',       'Instrumentation Engineering', false),
  ('00000000-0000-0000-0005-000000000006', 'Munish Kumar',      'munishsharma198@gmail.com',      '9882856139', 'Lecturer',      'B.Tech.',       'Instrumentation Engineering', false);

-- -----------------------------------------------------------
-- F) MECHANICAL ENGINEERING DEPARTMENT
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0006-000000000001', 'Amandeep Sharma',   'amandeepsharma@gmail.com',       null,         'HOD',           'B.Tech.',       'Mechanical Engineering', false),
  ('00000000-0000-0000-0006-000000000002', 'Onkar Singh',       'onkar.singh26970@gmail.com',     '7018814985', 'Sr. Lecturer',  'M.Tech.',       'Mechanical Engineering', false),
  ('00000000-0000-0000-0006-000000000003', 'Santosh Kumar',     'Kumarsantosh9606@gmail.com',     '9817128854', 'Lecturer',      'B.Tech.',       'Mechanical Engineering', false),
  ('00000000-0000-0000-0006-000000000004', 'Satbir Singh',      'satbirguru@gmail.com',           '7018376686', 'Lecturer',      'M.Tech.',       'Mechanical Engineering', false),
  ('00000000-0000-0000-0006-000000000005', 'Prag Sharma',       'pragsharma@gmail.com',           null,         'Lecturer',      'B.Tech.',       'Mechanical Engineering', false),
  ('00000000-0000-0000-0006-000000000006', 'Subash Chand',      'swastiksneh@gmail.com',          '9960170687', 'Lecturer',      'B.Tech.',       'Mechanical Engineering', false),
  ('00000000-0000-0000-0006-000000000007', 'N.C. Kaul',         'Narinderkaul68@gmail.com',       '9418219268', 'Foreman Instructor','Diploma',    'Mechanical Engineering', false);

-- -----------------------------------------------------------
-- G) WORKSHOP STAFF (for EWS subject)
-- -----------------------------------------------------------
insert into public.teachers (id, full_name, email, mobile, designation, qualification, department, is_workshop_staff) values
  ('00000000-0000-0000-0007-000000000001', 'Vikas Kandoria',    'vikash40at1579@gmail.com',       '9418161414', 'WSI Turning',   'Diploma',       'Workshop', true),
  ('00000000-0000-0000-0007-000000000002', 'Ishwar Dass',       'Ishwardas15051968@gmail.com',    '9418645828', 'WSI Fitting',   'Diploma',       'Workshop', true),
  ('00000000-0000-0000-0007-000000000003', 'Pawan Kumar',       'Pawankumar64399@gmail.com',      '9418864399', 'WSI Welding',   'JTS Part-II',   'Workshop', true),
  ('00000000-0000-0000-0007-000000000004', 'Varinder Kumar',    'Varinderkumar723@gmail.com',     '9816873723', 'WSI Smithy',    'NCVT',          'Workshop', true),
  ('00000000-0000-0000-0007-000000000005', 'Sanjay Kumar',      'Sanjaykapilsanjaykapil1@gmail.com','7018943485','WSI Carpentry','Diploma',       'Workshop', true),
  ('00000000-0000-0000-0007-000000000006', 'Aneesh Kumar',      'Aneeshmalhotra45@gmail.com',     '9882025448', 'WSI Sheet Metal','NCVT',         'Workshop', true),
  ('00000000-0000-0000-0007-000000000007', 'Shivam Bhatia',     'Shiyambhatia2003@gmail.com',     '8219175710', 'WSI Electrical','Diploma',       'Workshop', true),
  ('00000000-0000-0000-0007-000000000008', 'Manish Thakur',     'Thakurmanish993@gmail.com',      '8219339225', 'WSI Machinist', 'B.Tech.',       'Workshop', true),
  ('00000000-0000-0000-0007-000000000009', 'Workshop Staff',    'workshopstaff@gpkangra.edu.in',  null,         'Workshop Staff','',              'Workshop', true);

-- ============================================================
-- STEP 12: TEACHER ASSIGNMENTS
-- Format: (teacher_id, branch, semester, subject_code, subject_name, department)
-- Department for Sem 1 & 2 (all branches) = 'Applied Sciences & Humanities'
-- ============================================================

-- ===========================
-- SEM 2 - COMPUTER ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  -- Math-II: Kamlesh Chand
  ('00000000-0000-0000-0001-000000000001', 'Computer Engineering', 2, 'MATH-II',  'Mathematics-II',               'Applied Sciences & Humanities'),
  -- App Physics-II: Saroop Chand
  ('00000000-0000-0000-0001-000000000002', 'Computer Engineering', 2, 'PHY-II',   'Applied Physics-II',           'Applied Sciences & Humanities'),
  -- Intro to IT: Surbhi Sharma
  ('00000000-0000-0000-0002-000000000003', 'Computer Engineering', 2, 'IT',       'Introduction to IT',           'Computer Engineering'),
  -- FEEE: Varun
  ('00000000-0000-0000-0005-000000000004', 'Computer Engineering', 2, 'FEEE',     'Fundamentals of EEE',          'Instrumentation Engineering'),
  -- Engg Mechanics: Prag Sharma
  ('00000000-0000-0000-0006-000000000005', 'Computer Engineering', 2, 'EM',       'Engineering Mechanics',        'Mechanical Engineering'),
  -- EVS: Anil Kumar
  ('00000000-0000-0000-0001-000000000007', 'Computer Engineering', 2, 'EVS',      'Environmental Science',        'Applied Sciences & Humanities'),
  -- SCA: Saroop Chand
  ('00000000-0000-0000-0001-000000000002', 'Computer Engineering', 2, 'SCA',      'Student Centered Activities',  'Applied Sciences & Humanities');

-- ===========================
-- SEM 2 - ELECTRICAL ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0001-000000000005', 'Electrical Engineering', 2, 'MATH-II', 'Mathematics-II',              'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000004', 'Electrical Engineering', 2, 'PHY-II',  'Applied Physics-II',          'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0002-000000000005', 'Electrical Engineering', 2, 'IT',      'Introduction to IT',          'Computer Engineering'),
  ('00000000-0000-0000-0004-000000000005', 'Electrical Engineering', 2, 'FEEE',    'Fundamentals of EEE',         'Electrical Engineering'),
  ('00000000-0000-0000-0006-000000000004', 'Electrical Engineering', 2, 'EM',      'Engineering Mechanics',       'Mechanical Engineering'),
  ('00000000-0000-0000-0001-000000000007', 'Electrical Engineering', 2, 'EVS',     'Environmental Science',       'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000007', 'Electrical Engineering', 2, 'SCA',     'Student Centered Activities', 'Applied Sciences & Humanities');

-- ===========================
-- SEM 2 - ELECTRONICS & COMMUNICATION ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0001-000000000001', 'Electronics & Communication Engineering', 2, 'MATH-II', 'Mathematics-II',              'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000006', 'Electronics & Communication Engineering', 2, 'PHY-II',  'Applied Physics-II',          'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0002-000000000004', 'Electronics & Communication Engineering', 2, 'IT',      'Introduction to IT',          'Computer Engineering'),
  ('00000000-0000-0000-0003-000000000003', 'Electronics & Communication Engineering', 2, 'FEEE',    'Fundamentals of EEE',         'Electrical Engineering'),
  ('00000000-0000-0000-0005-000000000004', 'Electronics & Communication Engineering', 2, 'EM',      'Engineering Mechanics',       'Instrumentation Engineering'),
  ('00000000-0000-0000-0001-000000000007', 'Electronics & Communication Engineering', 2, 'EVS',     'Environmental Science',       'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000006', 'Electronics & Communication Engineering', 2, 'SCA',     'Student Centered Activities', 'Applied Sciences & Humanities');

-- ===========================
-- SEM 2 - INSTRUMENTATION ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0001-000000000005', 'Instrumentation Engineering', 2, 'MATH-II', 'Mathematics-II',              'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000004', 'Instrumentation Engineering', 2, 'PHY-II',  'Applied Physics-II',          'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0003-000000000004', 'Instrumentation Engineering', 2, 'FEEE',    'Fundamentals of EEE',         'Electrical Engineering'),
  ('00000000-0000-0000-0007-000000000003', 'Instrumentation Engineering', 2, 'EWS',     'Engineering Workshop',        'Workshop'),
  ('00000000-0000-0000-0005-000000000001', 'Instrumentation Engineering', 2, 'EM',      'Engineering Mechanics',       'Instrumentation Engineering'),
  ('00000000-0000-0000-0001-000000000007', 'Instrumentation Engineering', 2, 'EVS',     'Environmental Science',       'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000004', 'Instrumentation Engineering', 2, 'SCA',     'Student Centered Activities', 'Applied Sciences & Humanities');

-- ===========================
-- SEM 2 - MECHANICAL ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0001-000000000005', 'Mechanical Engineering', 2, 'MATH-II', 'Mathematics-II',               'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000006', 'Mechanical Engineering', 2, 'PHY-II',  'Applied Physics-II',           'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0003-000000000003', 'Mechanical Engineering', 2, 'FEEE',    'Fundamentals of EEE',          'Electrical Engineering'),
  ('00000000-0000-0000-0007-000000000009', 'Mechanical Engineering', 2, 'EWS',     'Engineering Workshop',         'Workshop'),
  ('00000000-0000-0000-0006-000000000004', 'Mechanical Engineering', 2, 'EM',      'Engineering Mechanics',        'Mechanical Engineering'),
  ('00000000-0000-0000-0001-000000000007', 'Mechanical Engineering', 2, 'EVS',     'Environmental Science',        'Applied Sciences & Humanities'),
  ('00000000-0000-0000-0001-000000000005', 'Mechanical Engineering', 2, 'SCA',     'Student Centered Activities',  'Applied Sciences & Humanities');

-- ===========================
-- SEM 4 - COMPUTER ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0002-000000000005', 'Computer Engineering', 4, 'DBMS',    'Database Management System',   'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000001', 'Computer Engineering', 4, 'DSA',     'Data Structures & Algorithms', 'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000006', 'Computer Engineering', 4, 'PE-I',    'Professional Elective-I',      'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000007', 'Computer Engineering', 4, 'PE-II',   'Professional Elective-II',     'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000007', 'Computer Engineering', 4, 'EIKT',    'Emerging ICT',                 'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000006', 'Computer Engineering', 4, 'SCA',     'Student Centered Activities',  'Computer Engineering');

-- ===========================
-- SEM 4 - ELECTRICAL ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0003-000000000001', 'Electrical Engineering', 4, 'EPT&D',   'Electrical Power Trans & Dist','Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000002', 'Electrical Engineering', 4, 'BM&MHPP','BM & Mini Hydro Power Plant',  'Electrical Engineering'),
  ('00000000-0000-0000-0004-000000000005', 'Electrical Engineering', 4, 'IS&SEM',  'Industrial Safety & Energy Mgmt','Electrical Engineering'),
  ('00000000-0000-0000-0004-000000000005', 'Electrical Engineering', 4, 'FPE',     'FPE',                          'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000003', 'Electrical Engineering', 4, 'MINOR',   'Minor Project',                'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000004', 'Electrical Engineering', 4, 'EIKT',    'Emerging ICT',                 'Electrical Engineering'),
  ('00000000-0000-0000-0004-000000000005', 'Electrical Engineering', 4, 'SCA',     'Student Centered Activities',  'Electrical Engineering');

-- ===========================
-- SEM 4 - ELECTRONICS & COMMUNICATION ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0004-000000000003', 'Electronics & Communication Engineering', 4, 'MSA',    'Microprocessors & Applications','Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000001', 'Electronics & Communication Engineering', 4, 'CE',     'Consumer Electronics',          'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000002', 'Electronics & Communication Engineering', 4, 'IE',     'Industrial Electronics',        'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000006', 'Electronics & Communication Engineering', 4, 'BMI',    'Biomedical Instrumentation',    'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0001-000000000007', 'Electronics & Communication Engineering', 4, 'DCS',    'Digital Communication Systems', 'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000006', 'Electronics & Communication Engineering', 4, 'MINOR',  'Minor Project',                 'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000007', 'Electronics & Communication Engineering', 4, 'SCA',    'Student Centered Activities',   'Electronics & Communication Engineering');

-- ===========================
-- SEM 4 - INSTRUMENTATION ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0005-000000000003', 'Instrumentation Engineering', 4, 'CS',      'Control Systems',              'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000002', 'Instrumentation Engineering', 4, 'PC-I',    'Process Control-I',            'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000006', 'Instrumentation Engineering', 4, 'PE-I',    'Professional Elective-I',      'Instrumentation Engineering'),
  ('00000000-0000-0000-0001-000000000003', 'Instrumentation Engineering', 4, 'EIKT',    'Emerging ICT',                 'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000005', 'Instrumentation Engineering', 4, 'MINOR',   'Minor Project',                'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000003', 'Instrumentation Engineering', 4, 'SCA',     'Student Centered Activities',  'Instrumentation Engineering');

-- ===========================
-- SEM 4 - MECHANICAL ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0006-000000000004', 'Mechanical Engineering', 4, 'PE-II',   'PE-II (PPE)',                  'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000003', 'Mechanical Engineering', 4, 'PE-I',    'PE-I (AE)',                    'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000005', 'Mechanical Engineering', 4, 'SOM',     'Strength of Materials',        'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000006', 'Mechanical Engineering', 4, 'TE-II',   'Thermal Engineering-II',       'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000006', 'Mechanical Engineering', 4, 'CADM',    'CADM Practice',                'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000002', 'Mechanical Engineering', 4, 'MINOR',   'Minor Project',                'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000007', 'Mechanical Engineering', 4, 'SCA',     'Student Centered Activities',  'Mechanical Engineering');

-- ===========================
-- SEM 6 - COMPUTER ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0002-000000000003', 'Computer Engineering', 6, 'OE-II',   'Open Elective-II',             'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000002', 'Computer Engineering', 6, 'E&SU',    'Embedded Systems & Unix',      'Computer Engineering'),
  ('00000000-0000-0000-0004-000000000001', 'Computer Engineering', 6, 'IC',      'Industrial Communication',     'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000004', 'Computer Engineering', 6, 'SL',      'Soft Computing / SL',          'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000006', 'Computer Engineering', 6, 'MAJOR',   'Major Project',                'Computer Engineering'),
  ('00000000-0000-0000-0002-000000000002', 'Computer Engineering', 6, 'SCA',     'Student Centered Activities',  'Computer Engineering');

-- ===========================
-- SEM 6 - ELECTRICAL ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0001-000000000003', 'Electrical Engineering', 6, 'IC',      'Industrial Communication',     'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000004', 'Electrical Engineering', 6, 'E&SU',    'Energy & Smart Utilities',     'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000002', 'Electrical Engineering', 6, 'BE',      'BE (Subject)',                 'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000004', 'Electrical Engineering', 6, 'IT&M',    'IT & Management',              'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000003', 'Electrical Engineering', 6, 'PP&C',    'Power Plant & Control',        'Electrical Engineering'),
  ('00000000-0000-0000-0003-000000000002', 'Electrical Engineering', 6, 'MAJOR',   'Major Project',                'Electrical Engineering'),
  ('00000000-0000-0000-0004-000000000005', 'Electrical Engineering', 6, 'SCA',     'Student Centered Activities',  'Electrical Engineering');

-- ===========================
-- SEM 6 - ELECTRONICS & COMMUNICATION ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0001-000000000007', 'Electronics & Communication Engineering', 6, 'CN&CC',  'Computer Networks & Cloud Comp','Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000006', 'Electronics & Communication Engineering', 6, 'E&SU',   'E&SU',                          'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000002', 'Electronics & Communication Engineering', 6, 'OE-II',  'Open Elective-II',              'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000001', 'Electronics & Communication Engineering', 6, 'IC',     'Industrial Communication',      'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000003', 'Electronics & Communication Engineering', 6, 'MAJOR',  'Major Project',                 'Electronics & Communication Engineering'),
  ('00000000-0000-0000-0004-000000000008', 'Electronics & Communication Engineering', 6, 'SCA',    'Student Centered Activities',   'Electronics & Communication Engineering');

-- ===========================
-- SEM 6 - INSTRUMENTATION ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0005-000000000001', 'Instrumentation Engineering', 6, 'LC&DCS', 'LC&DCS',                       'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000005', 'Instrumentation Engineering', 6, 'OE-II',  'Open Elective-II',             'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000002', 'Instrumentation Engineering', 6, 'AUEA',   'AUEA',                         'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000003', 'Instrumentation Engineering', 6, 'E&SU',   'Energy & Smart Utilities',     'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000001', 'Instrumentation Engineering', 6, 'MAJOR',  'Major Project',                'Instrumentation Engineering'),
  ('00000000-0000-0000-0005-000000000006', 'Instrumentation Engineering', 6, 'SCA',    'Student Centered Activities',  'Instrumentation Engineering');

-- ===========================
-- SEM 6 - MECHANICAL ENGINEERING
-- ===========================
insert into public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department) values
  ('00000000-0000-0000-0006-000000000006', 'Mechanical Engineering', 6, 'CADCAM',  'CAD/CAM Lab',                  'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000002', 'Mechanical Engineering', 6, 'DoME',    'Design of Machine Elements',   'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000001', 'Mechanical Engineering', 6, 'WT',      'Welding Technology',           'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000003', 'Mechanical Engineering', 6, 'OE-II',   'Open Elective-II',             'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000005', 'Mechanical Engineering', 6, 'E&SU',    'Energy & Smart Utilities',     'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000001', 'Mechanical Engineering', 6, 'MAJOR',   'Major Project',                'Mechanical Engineering'),
  ('00000000-0000-0000-0006-000000000007', 'Mechanical Engineering', 6, 'SCA',     'Student Centered Activities',  'Mechanical Engineering');

-- ============================================================
-- END OF SQL
-- ============================================================
