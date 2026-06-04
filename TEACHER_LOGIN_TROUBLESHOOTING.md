# Teacher Login Fix Guide

## Problem Summary
- ✓ Student login works correctly
- ✗ Teacher login does NOT work on your laptop
- ✓ Teacher login works on your friend's laptop

## Root Cause
Your Supabase database schema is missing the `department` column in the `profiles` table. The teacher login flow requires this column.

## Solution

### Step 1: Apply the SQL Fix
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Login to your project
3. Navigate to **SQL Editor** (left sidebar → SQL Editor)
4. Click **New Query**
5. Copy and paste the entire contents of [TEACHER_LOGIN_FIX.sql](./TEACHER_LOGIN_FIX.sql)
6. Click **RUN** button (or press Ctrl+Enter)
7. Wait for it to complete (you should see "Success" messages)

### Step 2: Verify the Fix
Run this verification query in SQL Editor:

```sql
-- Check if department column exists in profiles
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'profiles' 
AND column_name = 'department';
```

You should see one row returned with `department`.

### Step 3: Test Teacher Login
1. Start your Flask app:
   ```bash
   python run_supabase.py
   # or: flask --app supabase_app run
   ```

2. Go to http://localhost:5000/teacher-login

3. Test with a teacher account:
   - **Email**: (one of your teacher accounts)
   - **Password**: (their password)

## If Teacher Login Still Fails

### Check 1: Verify Teacher Account Exists
In your Supabase **SQL Editor**, run:

```sql
-- List all teachers
SELECT id, full_name, email, department FROM public.teachers LIMIT 10;

-- List teacher assignments
SELECT t.full_name, ta.branch, ta.semester, ta.subject_name 
FROM public.teachers t
JOIN public.teacher_assignments ta ON ta.teacher_id = t.id
LIMIT 10;
```

If no results, you need to create teacher accounts first (admin can do this on the admin dashboard).

### Check 2: Verify Teacher Profile Exists
```sql
-- Find teacher profile
SELECT id, full_name, email, role, department 
FROM public.profiles 
WHERE role = 'teacher' 
LIMIT 10;
```

Make sure the teacher's profile has `role = 'teacher'`.

### Check 3: Check Application Logs
Look for error messages in your terminal where Flask is running. The error file might also contain clues:

```bash
# Windows
type err.txt

# Or check the output in terminal
```

## File Locations
- **SQL Fix Script**: `TEACHER_LOGIN_FIX.sql`
- **Verification Script**: `fix_schema.py` (run with `python fix_schema.py`)
- **Main App**: `run_supabase.py` or `app.py`
- **Teacher Login Route**: `supabase_app/routes/web.py` (search for `@web_bp.route("/teacher-login"`)

## Key Components
- **Teacher Login**: `/teacher-login` - requires teacher profile with valid assignment
- **Teacher Dashboard**: `/teacher-dashboard` - shows assigned students
- **Database Tables**:
  - `profiles`: User identity (all users)
  - `teachers`: Teacher personal info
  - `teacher_assignments`: Maps teachers to subjects/branches/semesters
  - `students`: Student info
  - `attendance`: Daily attendance records

## Environment Check
Make sure your `.env` file has correct Supabase credentials:

```bash
SUPABASE_URL=https://kwzexdurtmwqarpzigvz.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

Both your laptop and your friend's laptop should have the same `.env` credentials.

## After the Fix
Once teacher login works:
1. Create teacher accounts through the admin dashboard
2. Assign them to subjects/branches/semesters
3. Teachers can login and mark attendance

## Need More Help?
1. Check the error messages carefully - they often indicate what's missing
2. Run `python fix_schema.py` to get a diagnostic report
3. Verify all tables exist in Supabase dashboard → Tables section
4. Check that teacher data was properly seeded/created
