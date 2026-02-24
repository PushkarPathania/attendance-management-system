from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import re
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pushkar2006'  # Enter your MySQL password here
app.config['MYSQL_DB'] = 'student_portal'

# Initialize MySQL
mysql = MySQL(app)

# Secret key for session
app.secret_key = 'pushkar2006'

# Admin credentials (default)
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASSWORD = 'admin123'
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/student-registation.html', methods=['GET', 'POST'])
def student_registration():
    if request.method == 'POST':
        # Get form data
        fullName = request.form['fullName']
        email = request.form['email']
        boardRollNo = request.form['boardRollNo']
        branch = request.form['reg-branch']
        semester = request.form['reg-semester']
        password = request.form['password']
        
        # Create cursor
        cur = mysql.connection.cursor()
        
        # Check if student already exists
        cur.execute('SELECT * FROM students WHERE email = %s OR board_roll_no = %s', (email, boardRollNo))
        student = cur.fetchone()
        
        if student:
            flash('Email or Board Roll No already exists!', 'error')
            return render_template('student-registation.html')
        
        # Insert new student
        cur.execute('INSERT INTO students (full_name, email, board_roll_no, branch, semester, password) VALUES (%s, %s, %s, %s, %s, %s)',
                   (fullName, email, boardRollNo, branch, semester, password))
        
        # Commit to DB
        mysql.connection.commit()
        
        # Close connection
        cur.close()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('index'))
        
    return render_template('student-registation.html')

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

    cur = mysql.connection.cursor()
    cur.execute('SELECT id, full_name, email, teacher_id, branch, semester, subject FROM teachers ORDER BY id DESC')
    teachers = cur.fetchall()
    cur.close()

    return render_template('admin-dashboard.html', teachers=teachers)


@app.route('/teacher-register', methods=['GET', 'POST'])
def admin_create_teacher():
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        # Collect form data
        full_name = request.form.get('reg-name')
        email = request.form.get('reg-email')
        mobile = request.form.get('reg-mobile')
        teacher_id = request.form.get('reg-id')
        branch = request.form.get('reg-branch')
        semester = request.form.get('reg-semester')
        subject = request.form.get('reg-subject') if semester == '1' else None
        designation = request.form.get('reg-designation')
        gender = request.form.get('reg-gender')
        dob = request.form.get('reg-dob')
        password = request.form.get('reg-password')

        # Basic validation
        if not (full_name and email and teacher_id and password):
            flash('Please fill in the required fields.', 'error')
            return render_template('admin-dashboard.html')

        # Hash the password before storing
        hashed_pwd = generate_password_hash(password)

        cur = mysql.connection.cursor()
        # Check duplicates by email or teacher id
        cur.execute('SELECT id FROM teachers WHERE email = %s OR teacher_id = %s', (email, teacher_id))
        exists = cur.fetchone()
        if exists:
            flash('Email or Teacher ID already exists.', 'error')
            cur.close()
            cur = mysql.connection.cursor()
            cur.execute('SELECT id, full_name, email, teacher_id, branch, semester, subject FROM teachers ORDER BY id DESC')
            teachers = cur.fetchall()
            cur.close()
            return render_template('admin-dashboard.html', teachers=teachers)

        # Insert teacher record
        cur.execute('''INSERT INTO teachers (full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob, password)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob, hashed_pwd))
        mysql.connection.commit()
        cur.close()

        flash('Teacher registered successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    cur = mysql.connection.cursor()
    cur.execute('SELECT id, full_name, email, teacher_id, branch, semester, subject FROM teachers ORDER BY id DESC')
    teachers = cur.fetchall()
    cur.close()
    return render_template('admin-dashboard.html', teachers=teachers)


@app.route('/admin-edit-teacher/<int:teacher_id>', methods=['GET', 'POST'])
def admin_edit_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Collect form data
        full_name = request.form.get('edit-name')
        email = request.form.get('edit-email')
        mobile = request.form.get('edit-mobile')
        branch = request.form.get('edit-branch')
        semester = request.form.get('edit-semester')
        subject = request.form.get('edit-subject') if semester == '1' else None
        designation = request.form.get('edit-designation')
        gender = request.form.get('edit-gender')
        dob = request.form.get('edit-dob')

        # Update teacher record
        cur.execute('''UPDATE teachers SET full_name = %s, email = %s, mobile = %s, branch = %s, 
                       semester = %s, subject = %s, designation = %s, gender = %s, dob = %s 
                       WHERE id = %s''',
                    (full_name, email, mobile, branch, semester, subject, designation, gender, dob, teacher_id))
        mysql.connection.commit()

        flash('Teacher updated successfully!', 'success')
        cur.close()
        return redirect(url_for('admin_dashboard'))

    # Fetch teacher details
    cur.execute('SELECT id, full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob FROM teachers WHERE id = %s', (teacher_id,))
    teacher = cur.fetchone()
    cur.close()

    if not teacher:
        flash('Teacher not found.', 'error')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin-edit-teacher.html', teacher=teacher)


@app.route('/admin-delete-teacher/<int:teacher_id>', methods=['POST'])
def admin_delete_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        flash('Please login as admin first.', 'error')
        return redirect(url_for('admin_login'))

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM teachers WHERE id = %s', (teacher_id,))
    mysql.connection.commit()
    cur.close()

    flash('Teacher deleted successfully!', 'success')
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

    hashed_pwd = generate_password_hash(new_password)

    cur = mysql.connection.cursor()
    cur.execute('UPDATE teachers SET password = %s WHERE id = %s', (hashed_pwd, teacher_id))
    mysql.connection.commit()
    cur.close()

    flash('Teacher password reset successfully!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin-logout')
def admin_logout():
    session.clear()
    flash('Admin logged out successfully.', 'success')
    return redirect(url_for('admin_login'))


# ========== TEACHER ROUTES ==========

@app.route('/teacher-login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'GET':
        return render_template('teacher-login.html')
    
    # Accept POST from teacher login form
    email = request.form.get('email')
    password = request.form.get('password')

    if not (email and password):
        flash('Please provide both email and password.', 'error')
        return render_template('teacher-login.html')

    cur = mysql.connection.cursor()
    # Fetch id, full_name and password hash for the given email
    cur.execute('SELECT id, full_name, password FROM teachers WHERE email = %s', (email,))
    row = cur.fetchone()
    cur.close()

    if row:
        # row[2] is password hash
        if check_password_hash(row[2], password):
            session['teacher_logged_in'] = True
            session['teacher_id'] = row[0]
            session['teacher_name'] = row[1]
            flash('Welcome, ' + row[1], 'success')
            return redirect(url_for('teacher_dashboard'))

    flash('Invalid teacher credentials.', 'error')
    return render_template('teacher-login.html')


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

        cur = mysql.connection.cursor()
        cur.execute('SELECT password FROM teachers WHERE id = %s', (session['teacher_id'],))
        teacher = cur.fetchone()

        if not teacher or not check_password_hash(teacher[0], old_password):
            flash('Old password is incorrect.', 'error')
            cur.close()
            return redirect(url_for('teacher_dashboard'))

        hashed_new_pwd = generate_password_hash(new_password)
        cur.execute('UPDATE teachers SET password = %s WHERE id = %s', (hashed_new_pwd, session['teacher_id']))
        mysql.connection.commit()
        cur.close()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('teacher_dashboard'))

    return render_template('teacher-change-password.html')


@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('teacher_logged_in'):
        cur = mysql.connection.cursor()
        # Fetch teacher's subject and semester
        cur.execute('SELECT semester, subject FROM teachers WHERE id = %s', (session['teacher_id'],))
        teacher_info = cur.fetchone()
        teacher_semester = teacher_info[0]
        teacher_subject = teacher_info[1]

        # Fetch students for teacher's semester
        cur.execute('SELECT id, full_name, board_roll_no, branch FROM students WHERE semester = %s', (teacher_semester,))
        students = cur.fetchall()

        # Fetch today's attendance for teacher's subject
        from datetime import date
        today = date.today()
        cur.execute('SELECT student_id, status FROM attendance WHERE date = %s AND subject = %s', (today, teacher_subject))
        attendance_data = {row[0]: row[1] for row in cur.fetchall()}

        # Fetch all attendance records for students in the teacher's semester
        cur.execute('''
            SELECT a.student_id, s.full_name, a.date, a.subject, a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE s.semester = %s
            ORDER BY a.date DESC, s.full_name
        ''', (teacher_semester,))
        all_attendance = cur.fetchall()

        cur.close()
        return render_template('teacher_dashboard.html', teacher_name=session.get('teacher_name'), students=students, attendance_data=attendance_data, today=today, teacher_subject=teacher_subject, all_attendance=all_attendance)
    return redirect(url_for('index'))

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        return render_template('student-login.html')
    
    # Handle POST (form submission from student-login.html)
    email = request.form.get('email')
    password = request.form.get('password')

    if not (email and password):
        flash('Please provide both email and password.', 'error')
        return render_template('student-login.html')

    # Create cursor
    cur = mysql.connection.cursor()

    # Get user by email
    cur.execute('SELECT * FROM students WHERE email = %s', [email])
    student = cur.fetchone()
    cur.close()

    if student and student[6] == password:  # Index 6 is password in the database
        # Create session data
        session['logged_in'] = True
        session['student_id'] = student[0]
        session['full_name'] = student[1]

        flash('Welcome ' + student[1], 'success')
        return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid student credentials', 'error')
        return render_template('student-login.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by email
        cur.execute('SELECT * FROM students WHERE email = %s', [email])
        student = cur.fetchone()

        if student and student[6] == password:  # Index 6 is password in the database
            # Create session data
            session['logged_in'] = True
            session['student_id'] = student[0]
            session['full_name'] = student[1]

            flash('Welcome ' + student[1], 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid login credentials', 'error')
            return redirect(url_for('index'))

    return redirect(url_for('index'))

@app.route('/student_dashboard')
def student_dashboard():
    if session.get('logged_in'):
        cur = mysql.connection.cursor()
        # Fetch student details including semester
        cur.execute('SELECT full_name, email, board_roll_no, branch, semester FROM students WHERE id = %s', (session['student_id'],))
        student = cur.fetchone()

        # Fetch attendance history
        cur.execute('SELECT `date`, status FROM attendance WHERE student_id = %s ORDER BY `date` DESC', (session['student_id'],))
        attendance_history = cur.fetchall()

        subjects_data = []
        if student[4] == 1:  # If 1st semester
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
                cur.execute('SELECT status FROM attendance WHERE student_id = %s AND subject = %s', (session['student_id'], subject))
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

        # Get teacher's subject from session or DB
        cur = mysql.connection.cursor()
        cur.execute('SELECT subject FROM teachers WHERE id = %s', (session['teacher_id'],))
        teacher_subject = cur.fetchone()[0]

        for key, value in request.form.items():
            if key.startswith('status_'):
                student_id = int(key.split('_')[1])
                status = value
                # Check if attendance already marked for today and subject
                cur.execute('SELECT id FROM attendance WHERE student_id = %s AND date = %s AND subject = %s', (student_id, today, teacher_subject))
                existing = cur.fetchone()
                if existing:
                    cur.execute('UPDATE attendance SET status = %s WHERE id = %s', (status, existing[0]))
                else:
                    cur.execute('INSERT INTO attendance (student_id, date, status, subject) VALUES (%s, %s, %s, %s)', (student_id, today, status, teacher_subject))
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
        # Create cursor
        cur = mysql.connection.cursor()
        
        # Fetch all attendance records with student and teacher info
        cur.execute('''
            SELECT 
                a.id, 
                s.full_name as student_name, 
                s.board_roll_no, 
                a.date, 
                a.status, 
                a.subject
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            ORDER BY a.date DESC, s.full_name
        ''')
        
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
