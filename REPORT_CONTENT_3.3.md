## 3.3 Web-Based System Architecture

Our implemented architecture transforms the attendance workflow into a four-layer digital system using Flask, Supabase, and MySQL with role-based dashboards:

### Layer 1: Frontend - Responsive Dashboards

**Student Dashboard**
- Students authenticate via email/password and access personal attendance records
- View attendance status for assigned courses with real-time updates
- Display individual attendance percentages per subject and course
- Interactive alerts for low attendance (<75%)

**Teacher Dashboard**
- Teachers select their assigned classes and semesters
- Toggle digital checkboxes on dynamic student roster for attendance marking
- Submit attendance records with automatic timestamp logging
- View analytics and attendance reports for assigned classes

**Admin Dashboard**
- Manage user accounts (create, edit, delete students and teachers)
- Upload and process CSV/Excel student roster files
- Assign teachers to classes and manage course mappings
- Download attendance reports in CSV/Excel formats
- Monitor database integrity and system health

### Layer 2: Backend API - Flask with Role-Based Authentication

**API Endpoints Structure**

Authentication Routes (`/api/auth`):
- POST `/signup` - Create new student/teacher accounts
- POST `/login` - Generate JWT tokens for authenticated sessions
- GET `/logout` - Invalidate user sessions

Teachers Routes (`/api/teachers`):
- GET `/api/teachers` - List teachers by branch/semester
- POST `/api/teachers` - Create teacher records (admin only)
- PUT `/api/teachers/<id>` - Update teacher assignments

Students Routes (`/api/students`):
- GET `/api/students` - List students with filters
- POST `/api/students` - Add student records (admin only)
- PUT `/api/students/<id>` - Update student information

Attendance Routes (`/api/attendance`):
- POST `/api/attendance` - Submit teacher-marked attendance
- GET `/api/attendance` - Retrieve records (role-based filtering)
- GET `/api/attendance/stats` - Compute attendance percentages in real-time

Reports Routes (`/api/reports`):
- GET `/api/reports/class-summary` - Class-level attendance overview
- GET `/api/reports/student-summary` - Individual student statistics
- GET `/api/reports/export` - Export reports as CSV/PDF

Uploads Routes (`/api/uploads`):
- POST `/api/uploads/roster` - Validate and ingest CSV student rosters
  - Vectorized Pandas dataframe processing for batch operations
  - Auto-create student accounts from roster data
  - Map students to branch and semester assignments

**Authentication & Authorization**
- JWT tokens issued by Supabase Auth for secure credential management
- Bearer token validation on all protected API endpoints
- Role-Based Access Control (RBAC): admin, teacher, student roles
- Row-Level Security policies enforced at database level

### Layer 3: Data Pipeline - Dual Database Architecture

**Primary Database: Supabase (PostgreSQL)**
- `profiles` - User accounts with role assignments
- `students` - Student enrollment records linked to profiles
- `teachers` - Teacher records with subject and class assignments
- `attendance` - Individual attendance entries with timestamps
- Real-time query capabilities with instant data synchronization

**Local Database: MySQL**
- Fallback storage and backup for critical records
- Dynamic branch-specific tables:
  - `students_<branch>_sem<N>` - Branch-specific student rosters
  - `teachers_<branch>_sem<N>` - Branch-specific teacher assignments
  - `attendance_<branch>_sem<N>` - Branch-specific attendance logs
- Metadata table tracking dynamic schema creation

**Data Processing Workflow**

1. **Roster Ingestion**
   - Admins upload CSV/Excel files through the admin dashboard
   - Backend validates file format and data structure using Pandas
   - Records are vectorized for batch processing and optimization
   - Clean data is saved simultaneously to Supabase and MySQL

2. **Granular Marking**
   - Teachers log into their dashboard and select assigned class/semester
   - Dynamic student roster displays with digital checkboxes
   - Teachers toggle attendance status for each student
   - System records submission timestamp and teacher ID

3. **Instant Database Pipeline**
   - Attendance submissions trigger backend validation:
     - Verify student enrollment in branch/semester
     - Confirm teacher assignment to the class
     - Prevent duplicate submissions
     - Enforce referential integrity
   - Valid records immediately insert into Supabase and MySQL
   - Aggregate statistics auto-calculate in real-time

4. **Real-Time Metrics & Visualization**
   - Student dashboards query attendance data in real-time
   - Automated percentage calculation: (Present Days ÷ Total Days) × 100
   - Subject-wise attendance breakdown displayed
   - Interactive Chart.js graphs show attendance trends over time
   - Teacher dashboards display class averages and individual student statistics
   - Admin reports provide branch-level and semester-level compliance metrics

### Layer 4: Security & Data Integrity

**Authentication Layer**
- Supabase JWT tokens for secure session management
- Password hashing using industry-standard encryption
- Bearer token verification on every API request

**Authorization Layer**
- Admin: Full system access including user and roster management
- Teacher: Access only to assigned classes and marking permissions
- Student: Access only to personal attendance records

**Data Isolation**
- Branch and semester-based data partitioning
- Cross-tenant isolation preventing unauthorized data access
- Row-level security policies at database level

### Performance Characteristics

- Roster upload: ~100 records/second via vectorized Pandas operations
- Attendance submission: <100ms response time with indexed queries
- Dashboard load time: <500ms with Supabase real-time queries
- Report generation: <2 seconds for aggregated queries with filtering

### Technology Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | HTML/CSS/JavaScript + Jinja2 | Responsive role-based dashboards |
| Backend | Flask with Blueprints | REST API and request routing |
| Authentication | Supabase JWT | Secure token-based authentication |
| Primary Database | Supabase (PostgreSQL) | Cloud-hosted data with real-time queries |
| Local Database | MySQL | Fallback and branch-specific storage |
| Data Processing | Pandas | CSV parsing and vectorized operations |
| Data Visualization | Chart.js | Interactive attendance graphs |
| File Handling | Werkzeug | Secure file upload and validation |

### Workflow Impact

**Traditional Manual Process:**
- Paper rosters → Manual entry → Spreadsheets → Email → Storage delays
- Timeline: Days to weeks
- Error rate: High
- Data accessibility: Delayed and location-dependent

**Implemented Digital Process:**
- CSV upload → Instant validation → Real-time database → Live dashboards
- Timeline: Seconds to minutes
- Error rate: Low (automated validation)
- Data accessibility: Immediate, mobile-responsive, location-independent
