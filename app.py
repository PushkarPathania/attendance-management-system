from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

# Common default password for seeded/admin-created users
DEFAULT_USER_PASSWORD = "2026"

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pushkar2006'  # Enter your MySQL password here
app.config['MYSQL_DB'] = 'student_portal'

# Initialize MySQL
mysql = MySQL(app)

# Secret key for session
app.secret_key = 'pushkar123'

# Admin credentials (default)
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASSWORD = 'admin123'


def slugify_branch(branch):
    if not branch:
        return ""
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', branch.strip().lower())
    return slug.strip('_')


def _is_safe_table_name(name):
    return bool(re.match(r'^[a-z0-9_]+$', name or ''))


def _class_table_names(branch_slug, semester):
    safe_slug = slugify_branch(branch_slug)
    sem = str(semester).strip()
    return {
        "students_table": f"students_{safe_slug}_sem{sem}",
        "teachers_table": f"teachers_{safe_slug}_sem{sem}",
        "attendance_table": f"attendance_{safe_slug}_sem{sem}",
    }


def ensure_meta_table():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS class_tables (
            id INT AUTO_INCREMENT PRIMARY KEY,
            branch VARCHAR(100) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            branch_slug VARCHAR(100) NOT NULL,
            students_table VARCHAR(128) NOT NULL,
            teachers_table VARCHAR(128) NOT NULL,
            attendance_table VARCHAR(128) NOT NULL,
            UNIQUE KEY uniq_branch_sem (branch, semester)
        )
        """
    )
    mysql.connection.commit()
    cur.close()


def _create_students_table(table_name):
    if not _is_safe_table_name(table_name):
        raise ValueError("Unsafe table name")
    cur = mysql.connection.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL,
            board_roll_no VARCHAR(40) NOT NULL,
            branch VARCHAR(100) NOT NULL,
            semester VARCHAR(20) NOT NULL,
            password VARCHAR(255) NOT NULL,
            UNIQUE KEY uniq_email (email),
            KEY idx_roll (board_roll_no)
        )
        """
    )
    cur.close()


def _create_teachers_table(table_name):
    if not _is_safe_table_name(table_name):
        raise ValueError("Unsafe table name")
    cur = mysql.connection.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(120) NOT NULL,
            mobile VARCHAR(30) NULL,
            teacher_id VARCHAR(50) NULL,
            branch VARCHAR(100) NULL,
            semester VARCHAR(20) NULL,
            subject VARCHAR(100) NULL,
            designation VARCHAR(100) NULL,
            gender VARCHAR(20) NULL,
            dob DATE NULL,
            password VARCHAR(255) NOT NULL,
            UNIQUE KEY uniq_email (email),
            KEY idx_teacher_id (teacher_id)
        )
        """
    )
    cur.close()


def _create_attendance_table(table_name):
    if not _is_safe_table_name(table_name):
        raise ValueError("Unsafe table name")
    cur = mysql.connection.cursor()
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            teacher_id INT NOT NULL,
            date DATE NOT NULL,
            status VARCHAR(20) NOT NULL,
            subject VARCHAR(100) NOT NULL,
            KEY idx_student_date (student_id, date),
            KEY idx_teacher_date (teacher_id, date)
        )
        """
    )
    cur.close()


def ensure_class_tables(branch, semester):
    ensure_meta_table()
    row = resolve_class_tables(branch, semester)
    if row:
        return row
    branch_slug = slugify_branch(branch)
    names = _class_table_names(branch_slug, semester)
    for name in names.values():
        if not _is_safe_table_name(name):
            raise ValueError("Unsafe table name")
    cur = mysql.connection.cursor()
    cur.execute(
        """
        INSERT INTO class_tables (branch, semester, branch_slug, students_table, teachers_table, attendance_table)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (branch, str(semester), branch_slug, names["students_table"], names["teachers_table"], names["attendance_table"]),
    )
    _create_students_table(names["students_table"])
    _create_teachers_table(names["teachers_table"])
    _create_attendance_table(names["attendance_table"])
    mysql.connection.commit()
    cur.close()
    return resolve_class_tables(branch, semester)


def get_class_tables():
    ensure_meta_table()
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT branch, semester, branch_slug, students_table, teachers_table, attendance_table
        FROM class_tables
        ORDER BY branch, semester
        """
    )
    rows = cur.fetchall()
    cur.close()
    result = []
    for row in rows:
        result.append(
            {
                "branch": row[0],
                "semester": row[1],
                "branch_slug": row[2],
                "students_table": row[3],
                "teachers_table": row[4],
                "attendance_table": row[5],
            }
        )
    return result


def resolve_class_tables(branch, semester):
    ensure_meta_table()
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT branch, semester, branch_slug, students_table, teachers_table, attendance_table
        FROM class_tables
        WHERE branch = %s AND semester = %s
        """,
        (branch, str(semester)),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        return None
    return {
        "branch": row[0],
        "semester": row[1],
        "branch_slug": row[2],
        "students_table": row[3],
        "teachers_table": row[4],
        "attendance_table": row[5],
    }


def _sort_semester_key(value):
    try:
        return int(str(value))
    except ValueError:
        return str(value)


def fetch_all_teachers():
    teachers = []
    class_rows = get_class_tables()
    cur = mysql.connection.cursor()
    for row in class_rows:
        table = row["teachers_table"]
        if not _is_safe_table_name(table):
            continue
        cur.execute(
            f"""
            SELECT id, full_name, email, teacher_id, branch, semester, subject,
                   mobile, designation, gender, dob
            FROM {table}
            ORDER BY id DESC
            """
        )
        teachers.extend(cur.fetchall())
    cur.close()
    return teachers


def fetch_all_students():
    students = []
    class_rows = get_class_tables()
    cur = mysql.connection.cursor()
    for row in class_rows:
        table = row["students_table"]
        if not _is_safe_table_name(table):
            continue
        cur.execute(
            f"""
            SELECT id, full_name, email, board_roll_no, branch, semester
            FROM {table}
            ORDER BY id DESC
            """
        )
        students.extend(cur.fetchall())
    cur.close()
    return students


def find_student_by_email(email):
    class_rows = get_class_tables()
    cur = mysql.connection.cursor()
    for row in class_rows:
        table = row["students_table"]
        if not _is_safe_table_name(table):
            continue
        cur.execute(
            f'''SELECT id, full_name, email, board_roll_no, branch, semester, password
                FROM {table} WHERE email = %s LIMIT 1''',
            (email,),
        )
        student = cur.fetchone()
        if student:
            cur.close()
            return student, row
    cur.close()
    return None, None
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/student-registation.html', methods=['GET', 'POST'])
def student_registration():
    flash('Student registration is handled by the admin.', 'error')
    return redirect(url_for('index'))

# ========== ADMIN ROUTES ==========
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_email'] = email
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
            return render_template('admin-login.html')

    return render_template('admin-login.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    teachers = fetch_all_teachers()
    students = fetch_all_students()

    return render_template('admin-dashboard.html', teachers=teachers, students=students)


@app.route('/teacher-register', methods=['GET', 'POST'])
def admin_create_teacher():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        # Collect form data
        full_name = request.form.get('reg-name')
        email = (request.form.get('reg-email') or '').lower()
        mobile = request.form.get('reg-mobile')
        teacher_id = request.form.get('reg-id')
        branch = request.form.get('reg-branch')
        semester = request.form.get('reg-semester')
        subject = request.form.get('reg-subject')
        designation = request.form.get('reg-designation')
        gender = request.form.get('reg-gender')
        dob = request.form.get('reg-dob')
        password = request.form.get('reg-password') or DEFAULT_USER_PASSWORD

        # Basic validation
        if not (full_name and email and branch and semester and subject):
            flash('Please fill in the required fields.', 'error')
            return redirect(url_for('admin_dashboard'))

        # Hash the password before storing
        hashed_pwd = generate_password_hash(password)

        class_row = ensure_class_tables(branch, semester)
        if not class_row:
            flash('Invalid branch or semester.', 'error')
            return redirect(url_for('admin_dashboard'))

        teachers_table = class_row["teachers_table"]
        cur = mysql.connection.cursor()
        # Check duplicates by email or teacher id within class
        if teacher_id:
            cur.execute(
                f'SELECT id FROM {teachers_table} WHERE email = %s OR teacher_id = %s',
                (email, teacher_id),
            )
        else:
            cur.execute(
                f'SELECT id FROM {teachers_table} WHERE email = %s',
                (email,),
            )
        exists = cur.fetchone()
        if exists:
            flash('Email or Teacher ID already exists for this class.', 'error')
            cur.close()
            return redirect(url_for('admin_dashboard'))

        # Insert teacher record
        cur.execute(
            f'''INSERT INTO {teachers_table} (full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob, hashed_pwd),
        )
        mysql.connection.commit()
        cur.close()

        flash('Teacher registered successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return redirect(url_for('admin_dashboard'))


@app.route('/admin-create-student', methods=['POST'])
def admin_create_student():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    full_name = request.form.get('stu-name')
    email = (request.form.get('stu-email') or '').lower()
    board_roll_no = request.form.get('stu-roll')
    branch = request.form.get('stu-branch')
    semester = request.form.get('stu-semester')
    password = request.form.get('stu-password') or DEFAULT_USER_PASSWORD

    if not (full_name and email and board_roll_no and branch and semester):
        flash('Please fill in all required student fields.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = ensure_class_tables(branch, semester)
    if not class_row:
        flash('Invalid branch or semester.', 'error')
        return redirect(url_for('admin_dashboard'))

    students_table = class_row["students_table"]
    hashed_pwd = generate_password_hash(password)

    cur = mysql.connection.cursor()
    cur.execute(
        f'SELECT id FROM {students_table} WHERE email = %s OR board_roll_no = %s',
        (email, board_roll_no),
    )
    exists = cur.fetchone()
    if exists:
        flash('Student email or roll number already exists in this class.', 'error')
        cur.close()
        return redirect(url_for('admin_dashboard'))

    cur.execute(
        f'''INSERT INTO {students_table}
            (full_name, email, board_roll_no, branch, semester, password)
            VALUES (%s, %s, %s, %s, %s, %s)''',
        (full_name, email, board_roll_no, branch, semester, hashed_pwd),
    )
    mysql.connection.commit()
    cur.close()

    flash('Student registered successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin-edit-teacher/<int:teacher_id>', methods=['GET', 'POST'])
def admin_edit_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    branch = request.args.get('branch') or request.form.get('edit-branch-original')
    semester = request.args.get('semester') or request.form.get('edit-semester-original')
    if not branch or not semester:
        flash('Missing class information for teacher.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid class selection.', 'error')
        return redirect(url_for('admin_dashboard'))

    teachers_table = class_row["teachers_table"]
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Collect form data
        full_name = request.form.get('edit-name')
        email = (request.form.get('edit-email') or '').lower()
        mobile = request.form.get('edit-mobile')
        branch = request.form.get('edit-branch')
        semester = request.form.get('edit-semester')
        subject = request.form.get('edit-subject')
        designation = request.form.get('edit-designation')
        gender = request.form.get('edit-gender')
        dob = request.form.get('edit-dob')

        original_branch = request.form.get('edit-branch-original')
        original_semester = request.form.get('edit-semester-original')
        original_class = resolve_class_tables(original_branch, original_semester)
        if not original_class:
            flash('Invalid original class.', 'error')
            cur.close()
            return redirect(url_for('admin_dashboard'))

        original_table = original_class["teachers_table"]

        # Fetch current password to preserve
        cur.execute(f'SELECT password FROM {original_table} WHERE id = %s', (teacher_id,))
        pwd_row = cur.fetchone()
        current_password = pwd_row[0] if pwd_row else None

        # If class changed, move record to new class table
        if branch != original_branch or semester != original_semester:
            target_class = ensure_class_tables(branch, semester)
            target_table = target_class["teachers_table"]

            cur.execute(
                f'''INSERT INTO {target_table}
                    (full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (full_name, email, mobile, request.form.get('edit-id'), branch, semester, subject, designation, gender, dob, current_password),
            )
            cur.execute(f'DELETE FROM {original_table} WHERE id = %s', (teacher_id,))
        else:
            # Update teacher record in same table
            cur.execute(
                f'''UPDATE {original_table} SET full_name = %s, email = %s, mobile = %s, branch = %s,
                    semester = %s, subject = %s, designation = %s, gender = %s, dob = %s
                    WHERE id = %s''',
                (full_name, email, mobile, branch, semester, subject, designation, gender, dob, teacher_id),
            )

        mysql.connection.commit()
        cur.close()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # Fetch teacher details
    cur.execute(
        f'''SELECT id, full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob
            FROM {teachers_table} WHERE id = %s''',
        (teacher_id,),
    )
    teacher = cur.fetchone()
    cur.close()

    if not teacher:
        flash('Teacher not found.', 'error')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin-edit-teacher.html', teacher=teacher, class_branch=branch, class_semester=semester)


@app.route('/admin-edit-student/<int:student_id>', methods=['GET', 'POST'])
def admin_edit_student(student_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    branch = request.args.get('branch') or request.form.get('edit-branch-original')
    semester = request.args.get('semester') or request.form.get('edit-semester-original')
    if not branch or not semester:
        flash('Missing class information for student.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid class selection.', 'error')
        return redirect(url_for('admin_dashboard'))

    students_table = class_row["students_table"]
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        full_name = request.form.get('edit-name')
        email = (request.form.get('edit-email') or '').lower()
        board_roll_no = request.form.get('edit-roll')
        branch = request.form.get('edit-branch')
        semester = request.form.get('edit-semester')

        original_branch = request.form.get('edit-branch-original')
        original_semester = request.form.get('edit-semester-original')
        original_class = resolve_class_tables(original_branch, original_semester)
        if not original_class:
            flash('Invalid original class.', 'error')
            cur.close()
            return redirect(url_for('admin_dashboard'))

        original_table = original_class["students_table"]
        cur.execute(f'SELECT password FROM {original_table} WHERE id = %s', (student_id,))
        pwd_row = cur.fetchone()
        current_password = pwd_row[0] if pwd_row else None

        if branch != original_branch or semester != original_semester:
            target_class = ensure_class_tables(branch, semester)
            target_table = target_class["students_table"]
            cur.execute(
                f'''INSERT INTO {target_table}
                    (full_name, email, board_roll_no, branch, semester, password)
                    VALUES (%s, %s, %s, %s, %s, %s)''',
                (full_name, email, board_roll_no, branch, semester, current_password),
            )
            cur.execute(f'DELETE FROM {original_table} WHERE id = %s', (student_id,))
        else:
            cur.execute(
                f'''UPDATE {original_table}
                    SET full_name = %s, email = %s, board_roll_no = %s, branch = %s, semester = %s
                    WHERE id = %s''',
                (full_name, email, board_roll_no, branch, semester, student_id),
            )

        mysql.connection.commit()
        cur.close()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cur.execute(
        f'''SELECT id, full_name, email, board_roll_no, branch, semester
            FROM {students_table} WHERE id = %s''',
        (student_id,),
    )
    student = cur.fetchone()
    cur.close()

    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin-edit-student.html', student=student, class_branch=branch, class_semester=semester)


@app.route('/admin-delete-teacher/<int:teacher_id>', methods=['POST'])
def admin_delete_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    branch = request.args.get('branch') or request.form.get('branch')
    semester = request.args.get('semester') or request.form.get('semester')
    if not branch or not semester:
        flash('Missing class information for delete.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid class selection.', 'error')
        return redirect(url_for('admin_dashboard'))

    teachers_table = class_row["teachers_table"]
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM {teachers_table} WHERE id = %s', (teacher_id,))
    mysql.connection.commit()
    cur.close()

    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin-delete-student/<int:student_id>', methods=['POST'])
def admin_delete_student(student_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    branch = request.args.get('branch') or request.form.get('branch')
    semester = request.args.get('semester') or request.form.get('semester')
    if not branch or not semester:
        flash('Missing class information for delete.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid class selection.', 'error')
        return redirect(url_for('admin_dashboard'))

    students_table = class_row["students_table"]
    cur = mysql.connection.cursor()
    cur.execute(f'DELETE FROM {students_table} WHERE id = %s', (student_id,))
    mysql.connection.commit()
    cur.close()

    flash('Student deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin-reset-password/<int:teacher_id>', methods=['POST'])
def admin_reset_password(teacher_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    new_password = request.form.get('new-password')

    if not new_password:
        flash('Password cannot be empty.', 'error')
        return redirect(url_for('admin_dashboard'))

    branch = request.args.get('branch') or request.form.get('branch')
    semester = request.args.get('semester') or request.form.get('semester')
    if not branch or not semester:
        flash('Missing class information for reset.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid class selection.', 'error')
        return redirect(url_for('admin_dashboard'))

    hashed_pwd = generate_password_hash(new_password)

    cur = mysql.connection.cursor()
    cur.execute(
        f'UPDATE {class_row["teachers_table"]} SET password = %s WHERE id = %s',
        (hashed_pwd, teacher_id),
    )
    mysql.connection.commit()
    cur.close()

    flash('Teacher password reset successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin-reset-student-password/<int:student_id>', methods=['POST'])
def admin_reset_student_password(student_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    new_password = request.form.get('new-password')
    if not new_password:
        flash('Password cannot be empty.', 'error')
        return redirect(url_for('admin_dashboard'))

    branch = request.args.get('branch') or request.form.get('branch')
    semester = request.args.get('semester') or request.form.get('semester')
    if not branch or not semester:
        flash('Missing class information for reset.', 'error')
        return redirect(url_for('admin_dashboard'))

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid class selection.', 'error')
        return redirect(url_for('admin_dashboard'))

    hashed_pwd = generate_password_hash(new_password)
    cur = mysql.connection.cursor()
    cur.execute(
        f'UPDATE {class_row["students_table"]} SET password = %s WHERE id = %s',
        (hashed_pwd, student_id),
    )
    mysql.connection.commit()
    cur.close()

    flash('Student password reset successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin-logout')
def admin_logout():
    session.clear()
    flash('Admin logged out successfully.', 'success')
    return redirect(url_for('admin_login'))


# ========== TEACHER ROUTES ==========

@app.route('/teacher-login', methods=['GET', 'POST'])
def teacher_login():
    class_rows = get_class_tables()
    branches = sorted({row["branch"] for row in class_rows if row["branch"]})
    semesters = sorted({row["semester"] for row in class_rows if row["semester"]}, key=_sort_semester_key)

    if request.method == 'GET':
        return render_template('teacher-login.html', branches=branches, semesters=semesters)
    
    # Accept POST from teacher login form
    email = (request.form.get('email') or '').lower()
    password = request.form.get('password')
    branch = request.form.get('branch')
    semester = request.form.get('semester')

    if not (email and password and branch and semester):
        flash('Please provide email, password, branch, and semester.', 'error')
        return render_template('teacher-login.html', branches=branches, semesters=semesters)

    class_row = resolve_class_tables(branch, semester)
    if not class_row:
        flash('Invalid branch or semester selection.', 'error')
        return render_template('teacher-login.html', branches=branches, semesters=semesters)

    teachers_table = class_row["teachers_table"]
    cur = mysql.connection.cursor()
    # Fetch id, full_name, password hash, subject for the given email
    cur.execute(
        f'SELECT id, full_name, password, subject FROM {teachers_table} WHERE email = %s',
        (email,),
    )
    row = cur.fetchone()
    cur.close()

    if row:
        # row[2] is password hash
        if check_password_hash(row[2], password):
            session['teacher_logged_in'] = True
            session['teacher_id'] = row[0]
            session['teacher_name'] = row[1]
            session['teacher_subject'] = row[3]
            session['teacher_branch'] = branch
            session['teacher_semester'] = semester
            session['teacher_table'] = teachers_table
            session['students_table'] = class_row["students_table"]
            session['attendance_table'] = class_row["attendance_table"]
            flash('Welcome, ' + row[1], 'success')
            return redirect(url_for('teacher_dashboard'))

    flash('Invalid teacher credentials.', 'error')
    return render_template('teacher-login.html', branches=branches, semesters=semesters)


@app.route('/teacher-change-password', methods=['GET', 'POST'])
def teacher_change_password():
    if not session.get('teacher_logged_in'):
        flash('Please login as teacher first.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')

        if not (old_password and new_password and confirm_password):
            flash('All fields are required.', 'error')
            return redirect(url_for('teacher_dashboard'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('teacher_dashboard'))

        teacher_table = session.get('teacher_table')
        if not teacher_table or not _is_safe_table_name(teacher_table):
            flash('Invalid teacher session. Please login again.', 'error')
            return redirect(url_for('teacher_login'))

        cur = mysql.connection.cursor()
        cur.execute(f'SELECT password FROM {teacher_table} WHERE id = %s', (session['teacher_id'],))
        teacher = cur.fetchone()

        if not teacher or not check_password_hash(teacher[0], old_password):
            flash('Old password is incorrect.', 'error')
            cur.close()
            return redirect(url_for('teacher_dashboard'))

        hashed_new_pwd = generate_password_hash(new_password)
        cur.execute(
            f'UPDATE {teacher_table} SET password = %s WHERE id = %s',
            (hashed_new_pwd, session['teacher_id']),
        )
        mysql.connection.commit()
        cur.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))

    return render_template('teacher-change-password.html')


@app.route('/student-change-password', methods=['GET', 'POST'])
def student_change_password():
    if not session.get('logged_in'):
        flash('Please login as student first.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')

        if not (old_password and new_password and confirm_password):
            flash('All fields are required.', 'error')
            return redirect(url_for('student_dashboard'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('student_dashboard'))

        student_table = session.get('student_table')
        if not student_table or not _is_safe_table_name(student_table):
            flash('Invalid student session. Please login again.', 'error')
            return redirect(url_for('student_login'))

        cur = mysql.connection.cursor()
        cur.execute(f'SELECT password FROM {student_table} WHERE id = %s', (session['student_id'],))
        student = cur.fetchone()

        if not student or not check_password_hash(student[0], old_password):
            flash('Old password is incorrect.', 'error')
            cur.close()
            return redirect(url_for('student_dashboard'))

        hashed_new_pwd = generate_password_hash(new_password)
        cur.execute(
            f'UPDATE {student_table} SET password = %s WHERE id = %s',
            (hashed_new_pwd, session['student_id']),
        )
        mysql.connection.commit()
        cur.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('student-change-password.html')


@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('teacher_logged_in'):
        teacher_semester = session.get('teacher_semester')
        teacher_subject = session.get('teacher_subject')
        students_table = session.get('students_table')
        attendance_table = session.get('attendance_table')

        if not students_table or not attendance_table:
            flash('Invalid teacher session. Please login again.', 'error')
            return redirect(url_for('teacher_login'))

        cur = mysql.connection.cursor()
        # Fetch students for teacher's class
        cur.execute(
            f'SELECT id, full_name, board_roll_no, branch, email FROM {students_table} ORDER BY board_roll_no',
        )
        students = cur.fetchall()

        # Fetch today's attendance for teacher's subject
        from datetime import date
        today = date.today()
        cur.execute(
            f'SELECT student_id, status FROM {attendance_table} WHERE date = %s AND subject = %s',
            (today, teacher_subject),
        )
        attendance_data = {row[0]: row[1] for row in cur.fetchall()}

        # Fetch all attendance records for students in the teacher's semester
        cur.execute(
            f'''
            SELECT a.student_id, s.full_name, a.date, a.subject, a.status
            FROM {attendance_table} a
            JOIN {students_table} s ON a.student_id = s.id
            ORDER BY a.date DESC, s.full_name
        '''
        )
        all_attendance = cur.fetchall()

        cur.close()
        return render_template('teacher_dashboard.html', teacher_name=session.get('teacher_name'), teacher_semester=teacher_semester, students=students, attendance_data=attendance_data, today=today, teacher_subject=teacher_subject, all_attendance=all_attendance)
    return redirect(url_for('index'))

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        return render_template('student-login.html')
    
    # Handle POST (form submission from student-login.html)
    email = (request.form.get('email') or '').lower()
    password = request.form.get('password')

    if not (email and password):
        flash('Please provide both email and password.', 'error')
        return render_template('student-login.html')

    student, class_row = find_student_by_email(email)

    if student and check_password_hash(student[6], password):
        # Create session data
        session['logged_in'] = True
        session['student_id'] = student[0]
        session['full_name'] = student[1]
        session['student_table'] = class_row["students_table"] if class_row else None
        session['attendance_table'] = class_row["attendance_table"] if class_row else None
        session['student_branch'] = student[4]
        session['student_semester'] = student[5]

        flash('Welcome ' + student[1], 'success')
        return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid student credentials', 'error')
        return render_template('student-login.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email'].lower()
        password = request.form['password']

        student, class_row = find_student_by_email(email)

        if student and check_password_hash(student[6], password):
            # Create session data
            session['logged_in'] = True
            session['student_id'] = student[0]
            session['full_name'] = student[1]
            session['student_table'] = class_row["students_table"] if class_row else None
            session['attendance_table'] = class_row["attendance_table"] if class_row else None
            session['student_branch'] = student[4]
            session['student_semester'] = student[5]

            flash('Welcome ' + student[1], 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid login credentials', 'error')
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('logged_in'):
        students_table = session.get('student_table')
        attendance_table = session.get('attendance_table')
        if not students_table or not attendance_table:
            flash('Invalid student session. Please login again.', 'error')
            return redirect(url_for('student_login'))

        cur = mysql.connection.cursor()
        # Fetch student details including semester
        cur.execute(
            f'SELECT full_name, email, board_roll_no, branch, semester FROM {students_table} WHERE id = %s',
            (session['student_id'],),
        )
        student = cur.fetchone()
        if not student:
            cur.close()
            flash('Student not found. Please login again.', 'error')
            return redirect(url_for('student_login'))

        # Fetch attendance history
        cur.execute(
            f'SELECT `date`, status FROM {attendance_table} WHERE student_id = %s ORDER BY `date` DESC',
            (session['student_id'],),
        )
        attendance_history = cur.fetchall()

        subjects_data = []
        semester_value = student[4]
        if str(semester_value) == '1':  # If 1st semester
            subjects = [
                'Applied Math-1',
                'Applied Physics-1',
                'Applied Chemistry',
                'Engineering Graphics',
                'CSIE',
                'SCA',
                'Sports & Yoga',
                'Workshops'
            ]
            for subject in subjects:
                # Fetch attendance for this subject
                cur.execute(
                    f'SELECT status FROM {attendance_table} WHERE student_id = %s AND subject = %s',
                    (session['student_id'], subject),
                )
                subject_attendance = cur.fetchall()
                total_lectures = len(subject_attendance)
                presents = sum(1 for row in subject_attendance if row[0] == 'present')
                absents = total_lectures - presents
                subjects_data.append({
                    'name': subject,
                    'total_lectures': total_lectures,
                    'presents': presents,
                    'absents': absents
                })

        cur.close()
        return render_template('student_dashboard.html', student=student, attendance_history=attendance_history, subjects_data=subjects_data)
    return redirect(url_for('index'))

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if session.get('teacher_logged_in'):
        from datetime import date
        today = date.today()

        teacher_subject = session.get('teacher_subject')
        attendance_table = session.get('attendance_table')
        students_table = session.get('students_table')
        teacher_id = session.get('teacher_id')

        if not attendance_table or not students_table:
            flash('Invalid teacher session. Please login again.', 'error')
            return redirect(url_for('teacher_login'))

        if not teacher_subject:
            teacher_table = session.get('teacher_table')
            if teacher_table and _is_safe_table_name(teacher_table):
                cur = mysql.connection.cursor()
                cur.execute(f'SELECT subject FROM {teacher_table} WHERE id = %s', (teacher_id,))
                row = cur.fetchone()
                teacher_subject = row[0] if row else None
                cur.close()
        if not teacher_subject:
            flash('Teacher subject not set. Please contact admin.', 'error')
            return redirect(url_for('teacher_dashboard'))

        cur = mysql.connection.cursor()

        for key, value in request.form.items():
            if key.startswith('status_'):
                student_id = int(key.split('_')[1])
                status = value
                # Check if attendance already marked for today and subject
                cur.execute(
                    f'SELECT id FROM {attendance_table} WHERE student_id = %s AND date = %s AND subject = %s',
                    (student_id, today, teacher_subject),
                )
                existing = cur.fetchone()
                if existing:
                    cur.execute(
                        f'UPDATE {attendance_table} SET status = %s WHERE id = %s',
                        (status, existing[0]),
                    )
                else:
                    cur.execute(
                        f'INSERT INTO {attendance_table} (student_id, teacher_id, date, status, subject) VALUES (%s, %s, %s, %s, %s)',
                        (student_id, teacher_id, today, status, teacher_subject),
                    )
        mysql.connection.commit()
        cur.close()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/export_attendance', methods=['GET'])
def export_attendance():
    """
    Fetch all attendance records from the database and export to Excel file.
    Only accessible to logged-in teachers.
    """
    if not session.get('teacher_logged_in'):
        flash('You must be logged in as a teacher to export attendance.', 'error')
        return redirect(url_for('index'))
    
    try:
        attendance_table = session.get('attendance_table')
        students_table = session.get('students_table')
        if not attendance_table or not students_table:
            flash('Invalid teacher session. Please login again.', 'error')
            return redirect(url_for('teacher_login'))

        # Create cursor
        cur = mysql.connection.cursor()
        # Fetch all attendance records with student info for this class
        cur.execute(
            f'''
            SELECT 
                a.id, 
                s.full_name as student_name, 
                s.board_roll_no, 
                a.date, 
                a.status, 
                a.subject
            FROM {attendance_table} a
            JOIN {students_table} s ON a.student_id = s.id
            ORDER BY a.date DESC, s.full_name
            '''
        )

        # Fetch all records
        records = cur.fetchall()
        cur.close()
        
        if not records:
            flash('No attendance records found.', 'warning')
            return redirect(url_for('teacher_dashboard'))
        
        # Convert to DataFrame with proper column names
        df = pd.DataFrame(records, columns=['Attendance ID', 'Student Name', 'Board Roll No', 'Date', 'Status', 'Subject'])
        
        # Format the date column
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Attendance', index=False)
            
            # Get workbook and worksheet to format headers
            workbook = writer.book
            worksheet = writer.sheets['Attendance']
            
            # Format header row (bold, colored background)
            from openpyxl.styles import Font, PatternFill, Alignment
            header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
            header_font = Font(bold=True, color='FFFFFF')
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Adjust column widths
            column_widths = [15, 20, 15, 15, 12, 20]
            for i, width in enumerate(column_widths, 1):
                worksheet.column_dimensions[chr(64 + i)].width = width
        
        # Seek to the beginning of the BytesIO object
        output.seek(0)
        
        # Generate filename with timestamp
        filename = f"Attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Send the file
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'Error exporting attendance: {str(e)}', 'error')
        return redirect(url_for('teacher_dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
