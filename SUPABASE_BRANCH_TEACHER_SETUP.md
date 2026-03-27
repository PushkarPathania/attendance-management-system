# Supabase Branch-wise Teacher Setup

This project now includes:

- `sql/supabase_schema.sql` for PostgreSQL schema on Supabase
- `scripts/seed_to_supabase.py` to extract and seed from `teachers_data`/`students_data`

## 1) Apply schema in Supabase

1. Open Supabase Dashboard -> SQL Editor
2. Run `sql/supabase_schema.sql`

This creates:

- `profiles`, `students`, `teachers`, `attendance`
- UUID-based PK/FK relations
- branch-wise teacher views:
  - `teachers_computer`
  - `teachers_electronics`
  - `teachers_electrical`
  - `teachers_instrumentation`
  - `teachers_mechanical`
  - `teachers_civil_engineering`

## 2) Seed users from your test data

Set environment variables first:

```powershell
$env:SUPABASE_URL="https://YOUR_PROJECT.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="YOUR_SERVICE_ROLE_KEY"
$env:SEED_DEFAULT_PASSWORD="ChangeMe@123"
```

Run the script:

```powershell
python scripts/seed_to_supabase.py --test-file "C:\Users\HP\Desktop\test.py" --teacher-map "data/teacher_assignments.csv"
```

## 3) Query teachers by branch (separate logical tables)

Computer teachers:

```sql
select * from public.teachers_computer;
```

Electronics teachers:

```sql
select * from public.teachers_electronics;
```

Or generic function:

```sql
select * from public.get_teachers_by_branch('Computer Science');
select * from public.get_teachers_by_branch('Electronics');
```

## 4) Notes

- `scripts/seed_to_supabase.py` reuses branch inference similar to your existing MySQL seed script.
- Teacher rows are stored per `(profile_id, branch, semester)` so one teacher can be assigned to multiple branches/semesters cleanly.
- If a Supabase Auth user already exists, the script falls back to profile lookup by email.
