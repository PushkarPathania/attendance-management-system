create extension if not exists "pgcrypto";

do $$
begin
  if not exists (select 1 from pg_type where typname = 'user_role') then
    create type user_role as enum ('student', 'teacher', 'admin');
  end if;
end$$;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text not null,
  email text not null unique,
  role user_role not null,
  branch text,
  semester text,
  avatar_url text,
  created_at timestamptz not null default now()
);

create table if not exists public.students (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null unique references public.profiles(id) on delete cascade,
  board_roll_no text not null,
  branch text not null,
  semester text not null,
  created_at timestamptz not null default now(),
  unique(board_roll_no, branch, semester)
);

create table if not exists public.teachers (
  id uuid primary key default gen_random_uuid(),
  profile_id uuid not null references public.profiles(id) on delete cascade,
  branch text not null,
  semester text not null,
  subject text,
  department text,
  mobile text,
  teacher_code text,
  created_at timestamptz not null default now(),
  unique(profile_id, branch, semester)
);

create table if not exists public.attendance (
  id uuid primary key default gen_random_uuid(),
  student_id uuid not null references public.students(id) on delete cascade,
  teacher_id uuid not null references public.teachers(id) on delete restrict,
  class_branch text not null,
  class_semester text not null,
  attendance_date date not null,
  status text not null check (status in ('present', 'absent', 'late')),
  remarks text,
  created_at timestamptz not null default now(),
  unique(student_id, attendance_date)
);

create index if not exists idx_students_branch_sem on public.students(branch, semester);
create index if not exists idx_teachers_branch_sem on public.teachers(branch, semester);
create index if not exists idx_attendance_filters on public.attendance(class_branch, class_semester, attendance_date);
create index if not exists idx_attendance_student on public.attendance(student_id, attendance_date);

-- Branch-wise teacher views (separate logical tables for dashboards/reports)
create or replace view public.teachers_computer as
select * from public.teachers where lower(branch) = lower('Computer Science');

create or replace view public.teachers_electronics as
select * from public.teachers where lower(branch) = lower('Electronics');

create or replace view public.teachers_electrical as
select * from public.teachers where lower(branch) = lower('Electrical');

create or replace view public.teachers_instrumentation as
select * from public.teachers where lower(branch) = lower('Instrumentation');

create or replace view public.teachers_mechanical as
select * from public.teachers where lower(branch) = lower('Mechanical');

create or replace view public.teachers_civil_engineering as
select * from public.teachers where lower(branch) = lower('Civil Engineering');

-- Optional helper function for branch-wise teacher list
create or replace function public.get_teachers_by_branch(branch_name text)
returns setof public.teachers
language sql
stable
as $$
  select *
  from public.teachers
  where lower(branch) = lower(branch_name)
  order by created_at desc;
$$;
