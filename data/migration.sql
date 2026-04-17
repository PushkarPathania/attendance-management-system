-- ============================================================
-- SAFE DATABASE MIGRATION SCRIPT
-- RUN THIS IN SUPABASE SQL EDITOR
-- ============================================================

-- 1. DROP EXISTING VIEWS AND CONFLICTING FUNCTIONS TO FREE UP DEPENDENCIES
drop view if exists public.teachers_computer cascade;
drop view if exists public.teachers_electronics cascade;
drop view if exists public.teachers_electrical cascade;
drop view if exists public.teachers_instrumentation cascade;
drop view if exists public.teachers_mechanical cascade;
drop view if exists public.teachers_civil_engineering cascade;
drop view if exists public.teacher_full_view cascade;
drop function if exists public.get_teachers_by_branch(text) cascade;
drop function if exists public.get_teachers_by_branch_semester(text, integer) cascade;

-- 2. RENAME OLD TEACHERS TABLE TO PRESERVE DATA
alter table if exists public.teachers rename to old_teachers;

-- 3. CREATE NEW GLOBAL TEACHERS TABLE
create table if not exists public.teachers (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  email text not null unique,
  mobile text,
  teacher_code text unique,
  designation text,
  qualification text,
  department text,
  is_workshop_staff boolean not null default false,
  created_at timestamptz not null default now()
);

-- 4. MIGRATE DISTINCT TEACHERS FROM OLD_TEACHERS & PROFILES INTO NEW TEACHERS
insert into public.teachers (id, full_name, email, mobile, teacher_code, department)
select distinct on (o.profile_id)
  o.profile_id,               -- Map the original profile_id as the new teacher ID for consistency
  p.full_name,
  p.email,
  o.mobile,
  o.teacher_code,
  COALESCE(o.department, 'Unknown Department')
from public.old_teachers o
join public.profiles p on p.id = o.profile_id;

-- 5. CREATE TEACHER ASSIGNMENTS TABLE
create table if not exists public.teacher_assignments (
  id uuid primary key default gen_random_uuid(),
  teacher_id uuid not null references public.teachers(id) on delete cascade,
  branch text not null,
  semester integer not null check (semester between 1 and 8),
  subject_code text not null,
  subject_name text not null,
  department text not null,
  created_at timestamptz not null default now(),
  unique(teacher_id, branch, semester, subject_code)
);

-- 6. MIGRATE OLD_TEACHERS RECORDS INTO TEACHER_ASSIGNMENTS
-- *We map the old_teachers.id to assignment.id so the existing attendance table foreign key requires minimal changes*
insert into public.teacher_assignments (id, teacher_id, branch, semester, subject_code, subject_name, department)
select 
  o.id,                       -- Re-use the existing assignment ID to maintain attendance links
  o.profile_id,               -- This matches the newly populated teachers.id
  o.branch,
  NULLIF(REGEXP_REPLACE(o.semester, '[^0-9]', '', 'g'), '')::integer,
  COALESCE(o.subject, 'VARIOUS'),
  COALESCE(o.subject, 'Various Assigned Subjects'),
  COALESCE(o.department, 'Unknown Department')
from public.old_teachers o;

-- 7. UPDATE STUDENTS TABLE CONSTRAINTS & DATA TYPES
alter table public.students drop constraint if exists students_roll_branch_semester_unique;
alter table public.students alter column semester type integer using (NULLIF(REGEXP_REPLACE(semester, '[^0-9]', '', 'g'), '')::integer);
alter table public.students add constraint students_roll_branch_semester_unique unique (board_roll_no, branch, semester);

-- 8. UPDATE ATTENDANCE TABLE FOREIGN KEYS & DATA TYPES
-- Drop constraints
alter table public.attendance drop constraint if exists attendance_teacher_id_fkey;
alter table public.attendance drop constraint if exists attendance_student_id_attendance_date_key;

-- Rename teacher_id and attach to assignments table
alter table public.attendance rename column teacher_id to assignment_id;
alter table public.attendance add constraint attendance_assignment_id_fkey foreign key (assignment_id) references public.teacher_assignments(id) on delete restrict;

-- Convert class_semester to integer to match assignments
alter table public.attendance alter column class_semester type integer using (NULLIF(REGEXP_REPLACE(class_semester, '[^0-9]', '', 'g'), '')::integer);

-- Re-apply proper unique constraint
alter table public.attendance add constraint attendance_unique_session unique(student_id, assignment_id, attendance_date);

-- 9. RECREATE REQUISITE VIEWS FOR THE APPLICATION
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

-- 10. SAFE CLEANUP
-- You can manually drop the old_teachers table later if you wish
-- drop table public.old_teachers;
