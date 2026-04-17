import csv
from datetime import date
from io import BytesIO, StringIO

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
    jsonify,
)

from ..supabase_client import get_supabase_admin, get_supabase_public

web_bp = Blueprint("web_bp", __name__)

# Hardcoded admin credentials (same as old MySQL app)
ADMIN_EMAIL = "admin@admin.com"
ADMIN_PASSWORD = "admin123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _require_student_session():
    return bool(session.get("student_profile_id"))


def _require_teacher_session():
    return bool(session.get("teacher_profile_id"))


def _require_admin_session():
    return bool(session.get("admin_logged_in"))


def _fetch_all_students_tuples(sb):
    """Return students as list of tuples matching template format:
       (student_id, full_name, email, board_roll_no, branch, semester)
    """
    student_rows = sb.table("students").select("id,profile_id,board_roll_no,branch,semester").execute().data or []
    if not student_rows:
        return []
    profile_ids = [r["profile_id"] for r in student_rows]
    profile_rows = sb.table("profiles").select("id,full_name,email").in_("id", profile_ids).execute().data or []
    p_map = {p["id"]: p for p in profile_rows}
    result = []
    for r in student_rows:
        p = p_map.get(r["profile_id"], {})
        result.append((
            r["id"],
            p.get("full_name", "Unknown"),
            p.get("email", ""),
            r.get("board_roll_no", ""),
            r.get("branch", ""),
            str(r.get("semester", "")),
        ))
    return result


def _fetch_all_teachers_tuples(sb):
    """Return teachers as list of tuples matching template format:
       (assignment_id, full_name, email, teacher_code, branch, semester, subject_name)
    """
    rows = sb.table("teacher_full_view").select("*").execute().data or []
    result = []
    for r in rows:
        result.append((
            r.get("assignment_id", r.get("teacher_id", "")),
            r.get("full_name", "Unknown"),
            r.get("email", ""),
            r.get("department", ""),
            r.get("branch", ""),
            str(r.get("semester", "")),
            r.get("subject_name", ""),
            r.get("mobile", ""),
            r.get("designation", ""),
            None,  # gender placeholder
            None,  # dob placeholder
        ))
    return result


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

@web_bp.get("/", endpoint="index")
def index():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Admin Routes
# ---------------------------------------------------------------------------

@web_bp.route("/admin-login", methods=["GET", "POST"], endpoint="admin_login")
def admin_login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session.clear()
            session["admin_logged_in"] = True
            session["admin_email"] = email
            flash("Welcome Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "error")
    return render_template("admin-login.html")


@web_bp.get("/admin-logout", endpoint="admin_logout")
def admin_logout():
    session.clear()
    flash("Admin logged out successfully.", "success")
    return redirect(url_for("admin_login"))


@web_bp.get("/admin-dashboard", endpoint="admin_dashboard")
def admin_dashboard():
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))
    sb = get_supabase_admin()
    teachers = _fetch_all_teachers_tuples(sb)
    students = _fetch_all_students_tuples(sb)
    return render_template("admin-dashboard.html", teachers=teachers, students=students)


@web_bp.post("/teacher-register", endpoint="admin_create_teacher")
def admin_create_teacher():
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))

    full_name = (request.form.get("reg-name") or "").strip()
    email = (request.form.get("reg-email") or "").strip().lower()
    mobile = (request.form.get("reg-mobile") or "").strip()
    teacher_code = (request.form.get("reg-id") or "").strip()
    branch = (request.form.get("reg-branch") or "").strip()
    semester_str = (request.form.get("reg-semester") or "").strip()
    subject = (request.form.get("reg-subject") or "").strip()
    designation = (request.form.get("reg-designation") or "").strip()
    department = (request.form.get("reg-department") or branch or "General").strip()
    password = (request.form.get("reg-password") or "ChangeMe@123").strip()

    if not (full_name and email and branch and semester_str):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        semester = int(semester_str)
    except ValueError:
        flash("Invalid semester value.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        sb = get_supabase_admin()

        # Create or find Supabase Auth user
        try:
            created = sb.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"role": "teacher"},
            })
            user_id = created.user.id
        except Exception:
            # User may already exist — look up profile
            profile_rows = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
            if not profile_rows:
                flash(f"Could not create teacher auth account for {email}.", "error")
                return redirect(url_for("admin_dashboard"))
            user_id = profile_rows[0]["id"]

        # Upsert profile
        sb.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "role": "teacher",
        }).execute()

        # Upsert teachers table
        existing_teacher = sb.table("teachers").select("id").eq("email", email).limit(1).execute().data or []
        if existing_teacher:
            teacher_db_id = existing_teacher[0]["id"]
        else:
            ins = sb.table("teachers").insert({
                "full_name": full_name,
                "email": email,
                "mobile": mobile or None,
                "teacher_code": teacher_code or None,
                "designation": designation or None,
                "department": department,
            }).execute()
            teacher_db_id = ins.data[0]["id"]

        # Insert teacher assignment
        sb.table("teacher_assignments").upsert({
            "teacher_id": teacher_db_id,
            "branch": branch,
            "semester": semester,
            "subject_code": subject[:20] if subject else "GEN",
            "subject_name": subject or "General",
            "department": department,
        }, on_conflict="teacher_id,branch,semester,subject_code").execute()

        flash("Teacher registered successfully!", "success")
    except Exception as exc:
        flash(f"Error creating teacher: {exc}", "error")

    return redirect(url_for("admin_dashboard"))


@web_bp.post("/admin-delete-teacher/<teacher_id>", endpoint="admin_delete_teacher")
def admin_delete_teacher(teacher_id):
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))
    try:
        sb = get_supabase_admin()
        # teacher_id here is actually assignment_id (UUID)
        # Try to delete assignment first
        sb.table("teacher_assignments").delete().eq("id", teacher_id).execute()
        flash("Teacher assignment deleted successfully!", "success")
    except Exception as exc:
        flash(f"Error deleting teacher: {exc}", "error")
    return redirect(url_for("admin_dashboard"))


@web_bp.route("/admin-edit-teacher/<teacher_id>", methods=["GET", "POST"], endpoint="admin_edit_teacher")
def admin_edit_teacher(teacher_id):
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))

    sb = get_supabase_admin()

    if request.method == "POST":
        subject = (request.form.get("edit-subject") or "").strip()
        branch = (request.form.get("edit-branch") or "").strip()
        semester_str = (request.form.get("edit-semester") or "").strip()
        full_name = (request.form.get("edit-name") or "").strip()
        email = (request.form.get("edit-email") or "").strip().lower()
        mobile = (request.form.get("edit-mobile") or "").strip()
        designation = (request.form.get("edit-designation") or "").strip()

        try:
            # Update the assignment
            update_data = {}
            if subject:
                update_data["subject_name"] = subject
                update_data["subject_code"] = subject[:20]
            if branch:
                update_data["branch"] = branch
            if semester_str:
                update_data["semester"] = int(semester_str)

            if update_data:
                sb.table("teacher_assignments").update(update_data).eq("id", teacher_id).execute()

            # Also update teacher personal info if email provided
            if email:
                teacher_row = sb.table("teachers").select("id").eq("email", email).limit(1).execute().data or []
                if teacher_row:
                    t_id = teacher_row[0]["id"]
                    upd = {}
                    if full_name:
                        upd["full_name"] = full_name
                    if mobile:
                        upd["mobile"] = mobile
                    if designation:
                        upd["designation"] = designation
                    if upd:
                        sb.table("teachers").update(upd).eq("id", t_id).execute()

            flash("Teacher updated successfully!", "success")
        except Exception as exc:
            flash(f"Error updating teacher: {exc}", "error")
        return redirect(url_for("admin_dashboard"))

    # GET — fetch assignment details for edit form
    try:
        rows = sb.table("teacher_full_view").select("*").eq("assignment_id", teacher_id).limit(1).execute().data or []
        if not rows:
            flash("Teacher assignment not found.", "error")
            return redirect(url_for("admin_dashboard"))
        row = rows[0]
        # Build a tuple compatible with admin-edit-teacher template
        teacher = (
            teacher_id,
            row.get("full_name", ""),
            row.get("email", ""),
            row.get("mobile", ""),
            None,  # teacher_code
            row.get("branch", ""),
            str(row.get("semester", "")),
            row.get("subject_name", ""),
            row.get("designation", ""),
            None,  # gender
            None,  # dob
        )
        return render_template(
            "admin-edit-teacher.html",
            teacher=teacher,
            class_branch=row.get("branch", ""),
            class_semester=str(row.get("semester", "")),
        )
    except Exception as exc:
        flash(f"Error loading teacher: {exc}", "error")
        return redirect(url_for("admin_dashboard"))


@web_bp.post("/admin-reset-password/<teacher_id>", endpoint="admin_reset_password")
def admin_reset_password(teacher_id):
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))

    new_password = request.form.get("new-password") or ""
    if not new_password:
        flash("Password cannot be empty.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        sb = get_supabase_admin()
        # teacher_id is assignment_id, need to look up teacher email
        rows = sb.table("teacher_full_view").select("email").eq("assignment_id", teacher_id).limit(1).execute().data or []
        if not rows:
            flash("Teacher not found.", "error")
            return redirect(url_for("admin_dashboard"))
        email = rows[0]["email"]
        # Find auth user
        profiles = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
        if profiles:
            user_id = profiles[0]["id"]
            sb.auth.admin.update_user_by_id(user_id, {"password": new_password})
            flash("Teacher password reset successfully!", "success")
        else:
            flash("Teacher auth account not found.", "error")
    except Exception as exc:
        flash(f"Error resetting password: {exc}", "error")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------------------
# Admin Student Routes
# ---------------------------------------------------------------------------

@web_bp.post("/admin-create-student", endpoint="admin_create_student")
def admin_create_student():
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))

    full_name = (request.form.get("stu-name") or "").strip()
    email = (request.form.get("stu-email") or "").strip().lower()
    board_roll_no = (request.form.get("stu-roll") or "").strip()
    branch = (request.form.get("stu-branch") or "").strip()
    semester_str = (request.form.get("stu-semester") or "").strip()
    password = (request.form.get("stu-password") or "ChangeMe@123").strip()

    if not (full_name and email and board_roll_no and branch and semester_str):
        flash("Please fill in all required student fields.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        semester = int(semester_str)
    except ValueError:
        flash("Invalid semester value.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        sb = get_supabase_admin()

        # Create or find Supabase Auth user
        try:
            created = sb.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"role": "student"},
            })
            user_id = created.user.id
        except Exception:
            profile_rows = sb.table("profiles").select("id").eq("email", email).limit(1).execute().data or []
            if not profile_rows:
                flash(f"Could not create student auth account for {email}.", "error")
                return redirect(url_for("admin_dashboard"))
            user_id = profile_rows[0]["id"]

        # Upsert profile
        sb.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "role": "student",
        }).execute()

        # Upsert student record
        sb.table("students").upsert({
            "profile_id": user_id,
            "board_roll_no": board_roll_no,
            "branch": branch,
            "semester": semester,
        }, on_conflict="profile_id").execute()

        flash("Student registered successfully!", "success")
    except Exception as exc:
        flash(f"Error creating student: {exc}", "error")

    return redirect(url_for("admin_dashboard"))


@web_bp.post("/admin-delete-student/<student_id>", endpoint="admin_delete_student")
def admin_delete_student(student_id):
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))
    try:
        sb = get_supabase_admin()
        # Get the profile_id to also delete auth user
        student_rows = sb.table("students").select("profile_id").eq("id", student_id).limit(1).execute().data or []
        sb.table("students").delete().eq("id", student_id).execute()
        if student_rows:
            profile_id = student_rows[0]["profile_id"]
            # Clean up profile and auth user
            try:
                sb.table("profiles").delete().eq("id", profile_id).execute()
                sb.auth.admin.delete_user(profile_id)
            except Exception:
                pass  # Ignore cleanup errors
        flash("Student deleted successfully!", "success")
    except Exception as exc:
        flash(f"Error deleting student: {exc}", "error")
    return redirect(url_for("admin_dashboard"))


@web_bp.route("/admin-edit-student/<student_id>", methods=["GET", "POST"], endpoint="admin_edit_student")
def admin_edit_student(student_id):
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))

    sb = get_supabase_admin()

    if request.method == "POST":
        full_name = (request.form.get("edit-name") or "").strip()
        email = (request.form.get("edit-email") or "").strip().lower()
        board_roll_no = (request.form.get("edit-roll") or "").strip()
        branch = (request.form.get("edit-branch") or "").strip()
        semester_str = (request.form.get("edit-semester") or "").strip()

        try:
            update_stu = {}
            if board_roll_no:
                update_stu["board_roll_no"] = board_roll_no
            if branch:
                update_stu["branch"] = branch
            if semester_str:
                update_stu["semester"] = int(semester_str)

            if update_stu:
                sb.table("students").update(update_stu).eq("id", student_id).execute()

            # Update profile
            if full_name or email:
                student_rows = sb.table("students").select("profile_id").eq("id", student_id).limit(1).execute().data or []
                if student_rows:
                    profile_id = student_rows[0]["profile_id"]
                    upd = {}
                    if full_name:
                        upd["full_name"] = full_name
                    if email:
                        upd["email"] = email
                    if upd:
                        sb.table("profiles").update(upd).eq("id", profile_id).execute()

            flash("Student updated successfully!", "success")
        except Exception as exc:
            flash(f"Error updating student: {exc}", "error")
        return redirect(url_for("admin_dashboard"))

    # GET — fetch student for edit form
    try:
        stu_rows = sb.table("students").select("*").eq("id", student_id).limit(1).execute().data or []
        if not stu_rows:
            flash("Student not found.", "error")
            return redirect(url_for("admin_dashboard"))
        stu = stu_rows[0]
        profile_rows = sb.table("profiles").select("full_name,email").eq("id", stu["profile_id"]).limit(1).execute().data or []
        p = profile_rows[0] if profile_rows else {}
        student = (
            student_id,
            p.get("full_name", ""),
            p.get("email", ""),
            stu.get("board_roll_no", ""),
            stu.get("branch", ""),
            str(stu.get("semester", "")),
        )
        return render_template(
            "admin-edit-student.html",
            student=student,
            class_branch=stu.get("branch", ""),
            class_semester=str(stu.get("semester", "")),
        )
    except Exception as exc:
        flash(f"Error loading student: {exc}", "error")
        return redirect(url_for("admin_dashboard"))


@web_bp.post("/admin-reset-student-password/<student_id>", endpoint="admin_reset_student_password")
def admin_reset_student_password(student_id):
    if not _require_admin_session():
        flash("Please login as admin first.", "error")
        return redirect(url_for("admin_login"))

    new_password = request.form.get("new-password") or ""
    if not new_password:
        flash("Password cannot be empty.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        sb = get_supabase_admin()
        student_rows = sb.table("students").select("profile_id").eq("id", student_id).limit(1).execute().data or []
        if not student_rows:
            flash("Student not found.", "error")
            return redirect(url_for("admin_dashboard"))
        profile_id = student_rows[0]["profile_id"]
        sb.auth.admin.update_user_by_id(profile_id, {"password": new_password})
        flash("Student password reset successfully!", "success")
    except Exception as exc:
        flash(f"Error resetting password: {exc}", "error")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------------------
# Student Routes
# ---------------------------------------------------------------------------

@web_bp.route("/student-registration", methods=["GET", "POST"], endpoint="student_registration")
def student_registration():
    if request.method == "GET":
        return render_template("student-registation.html")

    full_name = (request.form.get("fullName") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    board_roll_no = (request.form.get("boardRollNo") or "").strip()
    branch = (request.form.get("reg-branch") or "").strip()
    semester_str = (request.form.get("reg-semester") or "").strip()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirmPassword") or ""

    if password != confirm:
        flash("Password and confirm password do not match.", "error")
        return redirect(url_for("student_registration"))

    try:
        semester = int(semester_str) if semester_str else 1
        sb_admin = get_supabase_admin()
        created = sb_admin.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"role": "student"},
        })
        user_id = created.user.id
        sb_admin.table("profiles").upsert({
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "role": "student",
        }).execute()
        sb_admin.table("students").upsert({
            "profile_id": user_id,
            "board_roll_no": board_roll_no or email,
            "branch": branch or "General",
            "semester": semester,
        }, on_conflict="profile_id").execute()
        flash("Registration successful. Please login.", "success")
    except Exception as exc:
        flash(f"Registration failed: {exc}", "error")
    return redirect(url_for("student_login"))


@web_bp.route("/student-login", methods=["GET", "POST"], endpoint="student_login")
def student_login():
    if request.method == "GET":
        return render_template("student-login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    try:
        sb_public = get_supabase_public()
        auth_res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
        user_id = auth_res.user.id

        sb_admin = get_supabase_admin()
        profile_rows = sb_admin.table("profiles").select("*").eq("id", user_id).limit(1).execute().data or []
        if not profile_rows or profile_rows[0].get("role") != "student":
            flash("Only student accounts can login here.", "error")
            return redirect(url_for("student_login"))

        profile = profile_rows[0]
        session.clear()
        session["access_token"] = auth_res.session.access_token
        session["refresh_token"] = auth_res.session.refresh_token
        session["student_profile_id"] = user_id
        session["student_email"] = email
        session["full_name"] = profile.get("full_name")
        return redirect(url_for("student_dashboard"))
    except Exception:
        flash("Invalid credentials.", "error")
        return redirect(url_for("student_login"))


@web_bp.get("/student-dashboard", endpoint="student_dashboard")
def student_dashboard():
    if not _require_student_session():
        return redirect(url_for("student_login"))
    sb_admin = get_supabase_admin()
    profile_id = session["student_profile_id"]

    profile_rows = sb_admin.table("profiles").select("*").eq("id", profile_id).limit(1).execute().data or []
    student_rows = sb_admin.table("students").select("*").eq("profile_id", profile_id).limit(1).execute().data or []
    if not profile_rows or not student_rows:
        flash("Student profile not found.", "error")
        return redirect(url_for("student_login"))

    profile = profile_rows[0]
    student_row = student_rows[0]

    # 1. Fetch all assigned subjects for this student's branch and semester
    branch = student_row.get("branch")
    semester = student_row.get("semester")
    
    try:
        semester_int = int(semester) if semester else 1
    except ValueError:
        semester_int = semester

    all_assignments = (
        sb_admin.table("teacher_assignments")
        .select("subject_name")
        .eq("branch", branch)
        .eq("semester", semester_int)
        .execute()
        .data or []
    )

    subjects = {}
    for ta in all_assignments:
        subject_name = ta.get("subject_name") or "General"
        if subject_name not in subjects:
            subjects[subject_name] = {
                "name": subject_name,
                "total_lectures": 0,
                "presents": 0,
                "absents": 0,
                "late": 0,
            }

    # 2. Fetch actual attendance records
    attendance_rows = (
        sb_admin.table("attendance")
        .select("attendance_date,status,class_branch,remarks,teacher_assignments(subject_name,subject_code)")
        .eq("student_id", student_row["id"])
        .order("attendance_date", desc=True)
        .execute()
        .data
        or []
    )

    attendance_history = []
    
    # 3. Overlay attendance onto subjects
    for row in attendance_rows:
        subj = row.get("teacher_assignments") or {}
        subject_name = subj.get("subject_name") or "General"
        attendance_history.append((row["attendance_date"], row["status"], subject_name))

        stat = subjects.setdefault(subject_name, {
            "name": subject_name,
            "total_lectures": 0,
            "presents": 0,
            "absents": 0,
            "late": 0,
        })
        stat["total_lectures"] += 1
        status = (row.get("status") or "").lower()
        if status == "present":
            stat["presents"] += 1
        elif status == "absent":
            stat["absents"] += 1
        elif status == "late":
            stat["late"] += 1

    student = (
        profile.get("full_name"),
        profile.get("email"),
        student_row.get("board_roll_no"),
        student_row.get("branch"),
        str(student_row.get("semester", "")),
    )
    return render_template(
        "student_dashboard.html",
        student=student,
        attendance_history=attendance_history,
        subjects_data=list(subjects.values()),
    )


# ---------------------------------------------------------------------------
# Teacher Routes — Simplified Login (no AJAX)
# ---------------------------------------------------------------------------

@web_bp.get("/api/teacher-subjects", endpoint="teacher_subjects_api")
def teacher_subjects_api():
    """Still available for compatibility but login no longer requires it."""
    email = request.args.get("email", "").strip().lower()
    semester = request.args.get("semester", "").strip()
    if not email:
        return jsonify([])
    try:
        sb = get_supabase_admin()
        teachers = sb.table("teachers").select("id").eq("email", email).execute().data
        if not teachers:
            return jsonify([])
        teacher_id = teachers[0]["id"]
        query = sb.table("teacher_assignments").select("*").eq("teacher_id", teacher_id)
        if semester:
            try:
                query = query.eq("semester", int(semester))
            except ValueError:
                pass
        assignments = query.execute().data
        return jsonify(assignments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@web_bp.route("/teacher-login", methods=["GET", "POST"], endpoint="teacher_login")
def teacher_login():
    if request.method == "GET":
        return render_template("teacher-login.html")

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    # assignment_id is optional — will be set if teacher selected from a list
    assignment_id = (request.form.get("assignment_id") or "").strip()

    if not email or not password:
        flash("Please provide email and password.", "error")
        return redirect(url_for("teacher_login"))

    try:
        sb_public = get_supabase_public()
        auth_res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
        user_id = auth_res.user.id

        sb_admin = get_supabase_admin()
        profile_rows = sb_admin.table("profiles").select("*").eq("id", user_id).limit(1).execute().data or []
        if not profile_rows or profile_rows[0].get("role") != "teacher":
            flash("Only teacher accounts can login here.", "error")
            return redirect(url_for("teacher_login"))

        profile = profile_rows[0]

        # Get teacher record — auto-create if missing (profile exists but teachers row doesn't)
        teacher_rows = sb_admin.table("teachers").select("id").ilike("email", email).limit(1).execute().data or []
        if not teacher_rows:
            try:
                ins = sb_admin.table("teachers").insert({
                    "full_name": profile.get("full_name", "Unknown"),
                    "email": email,
                    "department": "General",
                    "teacher_code": "N/A",
                }).execute()
                teacher_db_id = ins.data[0]["id"]
            except Exception as exc:
                flash(f"Teacher record missing. Auto-fix failed: {exc}. Please contact admin.", "error")
                return redirect(url_for("teacher_login"))
        else:
            teacher_db_id = teacher_rows[0]["id"]

        # Get all assignments for this teacher
        assignments = (
            sb_admin.table("teacher_assignments")
            .select("*")
            .eq("teacher_id", teacher_db_id)
            .execute()
            .data or []
        )

        if not assignments:
            flash("No subject assignments found for your account. Please contact admin.", "error")
            return redirect(url_for("teacher_login"))

        # If teacher has exactly one assignment, auto-select it
        if len(assignments) == 1:
            assignment_id = assignments[0]["id"]

        # If no assignment_id selected yet, show the selection page
        if not assignment_id:
            # Re-render login page with assignment choices
            return render_template(
                "teacher-login.html",
                show_assignments=True,
                assignments=assignments,
                prefilled_email=email,
                prefilled_password=password,
            )

        # Find the selected assignment
        selected = next((a for a in assignments if a["id"] == assignment_id), None)
        if not selected:
            flash("Invalid assignment selected.", "error")
            return redirect(url_for("teacher_login"))

        # Set session
        session.clear()
        session["access_token"] = auth_res.session.access_token
        session["refresh_token"] = auth_res.session.refresh_token
        session["teacher_profile_id"] = user_id
        session["teacher_id"] = teacher_db_id
        session["teacher_email"] = email
        session["teacher_name"] = profile.get("full_name")
        session["teacher_assignment_id"] = selected["id"]
        session["teacher_branch"] = selected["branch"]
        session["teacher_semester"] = selected["semester"]
        session["teacher_subject"] = selected["subject_name"]

        flash(f"Welcome, {profile.get('full_name')}!", "success")
        return redirect(url_for("web_bp.teacher_dashboard"))

    except Exception as exc:
        flash(f"Login failed: {exc}", "error")
        return redirect(url_for("teacher_login"))


@web_bp.get("/teacher-dashboard", endpoint="teacher_dashboard")
def teacher_dashboard():
    if not _require_teacher_session():
        return redirect(url_for("teacher_login"))

    sb_admin = get_supabase_admin()
    branch = session.get("teacher_branch")
    semester = session.get("teacher_semester")
    teacher_id = session.get("teacher_id")
    assignment_id = session.get("teacher_assignment_id")
    teacher_subject = session.get("teacher_subject") or "General"

    # semester may be int or str — normalize for query
    try:
        semester_int = int(semester)
    except (TypeError, ValueError):
        semester_int = semester

    student_rows = (
        sb_admin.table("students")
        .select("id,profile_id,board_roll_no,branch,semester")
        .eq("branch", branch)
        .eq("semester", semester_int)
        .execute()
        .data
        or []
    )
    profile_ids = [row["profile_id"] for row in student_rows]
    profile_map = {}
    if profile_ids:
        p_rows = sb_admin.table("profiles").select("id,full_name,email").in_("id", profile_ids).execute().data or []
        profile_map = {row["id"]: row for row in p_rows}

    students = []
    student_id_list = []
    for row in student_rows:
        p = profile_map.get(row["profile_id"], {})
        students.append((
            row["id"],
            p.get("full_name", "Unknown"),
            row.get("board_roll_no"),
            row.get("branch"),
            p.get("email", ""),
        ))
        student_id_list.append(row["id"])

    today_str = str(date.today())
    attendance_today_rows = []
    all_attendance_rows = []
    if student_id_list:
        attendance_today_rows = (
            sb_admin.table("attendance")
            .select("*")
            .in_("student_id", student_id_list)
            .eq("assignment_id", assignment_id)
            .eq("attendance_date", today_str)
            .execute()
            .data
            or []
        )
        all_attendance_rows = (
            sb_admin.table("attendance")
            .select("*")
            .in_("student_id", student_id_list)
            .eq("assignment_id", assignment_id)
            .order("attendance_date", desc=True)
            .limit(200)
            .execute()
            .data
            or []
        )

    attendance_data = {row["student_id"]: row["status"] for row in attendance_today_rows}
    name_by_student = {row[0]: row[1] for row in students}
    all_attendance = [
        (name_by_student.get(r["student_id"], "Unknown"), r["attendance_date"], teacher_subject, r["status"])
        for r in all_attendance_rows
    ]

    return render_template(
        "teacher_dashboard.html",
        teacher_name=session.get("teacher_name", "Teacher"),
        teacher_semester=semester,
        teacher_subject=teacher_subject,
        students=students,
        attendance_data=attendance_data,
        all_attendance=all_attendance,
        today=today_str,
        teacher_id=teacher_id,
    )


@web_bp.post("/mark-attendance", endpoint="mark_attendance")
def mark_attendance():
    if not _require_teacher_session():
        return redirect(url_for("teacher_login"))

    sb_admin = get_supabase_admin()
    assignment_id = session.get("teacher_assignment_id")
    branch = session.get("teacher_branch")
    semester = session.get("teacher_semester")
    today_str = str(date.today())

    try:
        semester_int = int(semester)
    except (TypeError, ValueError):
        semester_int = semester

    student_rows = (
        sb_admin.table("students")
        .select("id")
        .eq("branch", branch)
        .eq("semester", semester_int)
        .execute()
        .data
        or []
    )
    allowed_status = {"present", "absent", "late"}
    for row in student_rows:
        sid = row["id"]
        status = (request.form.get(f"status_{sid}") or "present").strip().lower()
        if status not in allowed_status:
            status = "present"
        sb_admin.table("attendance").upsert(
            {
                "student_id": sid,
                "assignment_id": assignment_id,
                "class_branch": branch,
                "class_semester": semester_int,
                "attendance_date": today_str,
                "status": status,
            },
            on_conflict="student_id,assignment_id,attendance_date",
        ).execute()

    flash("Attendance saved successfully.", "success")
    return redirect(url_for("teacher_dashboard"))


@web_bp.get("/export-attendance", endpoint="export_attendance")
def export_attendance():
    if not _require_teacher_session():
        return redirect(url_for("teacher_login"))

    sb_admin = get_supabase_admin()
    branch = session.get("teacher_branch")
    semester = session.get("teacher_semester")

    try:
        semester_int = int(semester)
    except (TypeError, ValueError):
        semester_int = semester

    student_rows = (
        sb_admin.table("students")
        .select("id,profile_id,board_roll_no")
        .eq("branch", branch)
        .eq("semester", semester_int)
        .execute()
        .data
        or []
    )
    student_ids = [row["id"] for row in student_rows]
    p_map = {}
    if student_rows:
        profile_ids = [row["profile_id"] for row in student_rows]
        p_rows = sb_admin.table("profiles").select("id,full_name,email").in_("id", profile_ids).execute().data or []
        p_map = {p["id"]: p for p in p_rows}

    att_rows = []
    if student_ids:
        att_rows = (
            sb_admin.table("attendance")
            .select("student_id,attendance_date,status,class_branch,class_semester")
            .in_("student_id", student_ids)
            .eq("assignment_id", session.get("teacher_assignment_id"))
            .order("attendance_date", desc=True)
            .execute()
            .data
            or []
        )

    by_student = {row["id"]: row for row in student_rows}
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["Student Name", "Email", "Roll No", "Branch", "Semester", "Date", "Status"])
    for row in att_rows:
        s = by_student.get(row["student_id"])
        if not s:
            continue
        p = p_map.get(s["profile_id"], {})
        writer.writerow([
            p.get("full_name", "Unknown"),
            p.get("email", ""),
            s.get("board_roll_no", ""),
            row.get("class_branch", ""),
            row.get("class_semester", ""),
            row.get("attendance_date", ""),
            row.get("status", ""),
        ])

    csv_bytes = BytesIO(csv_buffer.getvalue().encode("utf-8"))
    csv_bytes.seek(0)
    return send_file(
        csv_bytes,
        mimetype="text/csv",
        as_attachment=True,
        download_name="attendance_export.csv",
    )


# ---------------------------------------------------------------------------
# Password Change Routes
# ---------------------------------------------------------------------------

@web_bp.route("/student-change-password", methods=["GET", "POST"], endpoint="student_change_password")
def student_change_password():
    if not _require_student_session():
        return redirect(url_for("student_login"))
    if request.method == "GET":
        return render_template("student-change-password.html")

    old_password = request.form.get("old-password") or ""
    new_password = request.form.get("new-password") or ""
    confirm_password = request.form.get("confirm-password") or ""
    if new_password != confirm_password:
        flash("New password and confirm password do not match.", "error")
        return redirect(url_for("student_change_password"))

    email = session.get("student_email")
    sb_public = get_supabase_public()
    sb_admin = get_supabase_admin()
    try:
        sb_public.auth.sign_in_with_password({"email": email, "password": old_password})
        sb_admin.auth.admin.update_user_by_id(session["student_profile_id"], {"password": new_password})
        flash("Password updated successfully.", "success")
    except Exception:
        flash("Current password is incorrect or update failed.", "error")
    return redirect(url_for("student_change_password"))


@web_bp.route("/teacher-change-password", methods=["GET", "POST"], endpoint="teacher_change_password")
def teacher_change_password():
    if not _require_teacher_session():
        return redirect(url_for("teacher_login"))
    if request.method == "GET":
        return render_template("teacher-change-password.html")

    old_password = request.form.get("old-password") or ""
    new_password = request.form.get("new-password") or ""
    confirm_password = request.form.get("confirm-password") or ""
    if new_password != confirm_password:
        flash("New password and confirm password do not match.", "error")
        return redirect(url_for("teacher_change_password"))

    email = session.get("teacher_email")
    sb_public = get_supabase_public()
    sb_admin = get_supabase_admin()
    try:
        sb_public.auth.sign_in_with_password({"email": email, "password": old_password})
        sb_admin.auth.admin.update_user_by_id(session["teacher_profile_id"], {"password": new_password})
        flash("Password updated successfully.", "success")
    except Exception:
        flash("Current password is incorrect or update failed.", "error")
    return redirect(url_for("teacher_change_password"))


@web_bp.get("/logout", endpoint="logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
