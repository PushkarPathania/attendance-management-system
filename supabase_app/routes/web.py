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
)

from ..supabase_client import get_supabase_admin, get_supabase_public

web_bp = Blueprint("web_bp", __name__)


def _require_student_session():
    return bool(session.get("student_profile_id"))


def _require_teacher_session():
    return bool(session.get("teacher_profile_id"))


@web_bp.get("/", endpoint="index")
def index():
    return render_template("index.html")


@web_bp.route("/admin-login", methods=["GET", "POST"], endpoint="admin_login")
def admin_login():
    if request.method == "POST":
        flash("Admin flow will be migrated in next phase.", "error")
    return render_template("admin-login.html")


@web_bp.route("/student-registration", methods=["GET", "POST"], endpoint="student_registration")
def student_registration():
    if request.method == "GET":
        return render_template("student-registation.html")

    full_name = (request.form.get("fullName") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    board_roll_no = (request.form.get("boardRollNo") or "").strip()
    branch = (request.form.get("reg-branch") or "").strip()
    semester = (request.form.get("reg-semester") or "").strip()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirmPassword") or ""
    if password != confirm:
        flash("Password and confirm password do not match.", "error")
        return redirect(url_for("student_registration"))

    try:
        sb_admin = get_supabase_admin()
        created = sb_admin.auth.admin.create_user(
            {
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {"role": "student"},
            }
        )
        user_id = created.user.id
        sb_admin.table("profiles").upsert(
            {
                "id": user_id,
                "full_name": full_name,
                "email": email,
                "role": "student",
                "branch": branch,
                "semester": semester,
            }
        ).execute()
        sb_admin.table("students").upsert(
            {
                "profile_id": user_id,
                "board_roll_no": board_roll_no or email,
                "branch": branch or "General",
                "semester": semester or "1",
            },
            on_conflict="profile_id",
        ).execute()
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


@web_bp.route("/teacher-login", methods=["GET", "POST"], endpoint="teacher_login")
def teacher_login():
    try:
        sb_admin = get_supabase_admin()
        t_rows = sb_admin.table("teachers").select("branch,semester").execute().data or []
    except Exception as exc:
        flash(f"Configuration error: {exc}", "error")
        return render_template("teacher-login.html", branches=[], semesters=[])

    branches = sorted({row["branch"] for row in t_rows if row.get("branch")})
    semesters = sorted(
        {str(row["semester"]) for row in t_rows if row.get("semester")},
        key=lambda x: int(x) if x.isdigit() else x,
    )

    if request.method == "GET":
        return render_template("teacher-login.html", branches=branches, semesters=semesters)

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    branch = (request.form.get("branch") or "").strip()
    semester = str(request.form.get("semester") or "").strip()

    try:
        sb_public = get_supabase_public()
        auth_res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
        user_id = auth_res.user.id

        profile_rows = sb_admin.table("profiles").select("*").eq("id", user_id).limit(1).execute().data or []
        if not profile_rows or profile_rows[0].get("role") != "teacher":
            flash("Only teacher accounts can login here.", "error")
            return redirect(url_for("teacher_login"))

        # Try strict match first, then normalized semester fallback.
        teacher_rows = (
            sb_admin.table("teachers")
            .select("*")
            .eq("profile_id", user_id)
            .eq("branch", branch)
            .eq("semester", semester)
            .limit(1)
            .execute()
            .data
            or []
        )
        if not teacher_rows and semester.isdigit():
            teacher_rows = (
                sb_admin.table("teachers")
                .select("*")
                .eq("profile_id", user_id)
                .eq("branch", branch)
                .eq("semester", str(int(semester)))
                .limit(1)
                .execute()
                .data
                or []
            )
        if not teacher_rows:
            teacher_rows = (
                sb_admin.table("teachers")
                .select("*")
                .eq("profile_id", user_id)
                .ilike("branch", branch)
                .limit(1)
                .execute()
                .data
                or []
            )
        if not teacher_rows:
            flash("No teacher assignment found for selected branch/semester.", "error")
            return redirect(url_for("teacher_login"))

        teacher = teacher_rows[0]
        session.clear()
        session["access_token"] = auth_res.session.access_token
        session["refresh_token"] = auth_res.session.refresh_token
        session["teacher_profile_id"] = user_id
        session["teacher_id"] = teacher["id"]
        session["teacher_email"] = email
        session["teacher_name"] = profile_rows[0].get("full_name")
        session["teacher_branch"] = branch
        session["teacher_semester"] = semester
        session["teacher_subject"] = teacher.get("subject") or "General"
        return redirect(url_for("teacher_dashboard"))
    except Exception as exc:
        flash(f"Teacher login failed: {exc}", "error")
        return redirect(url_for("teacher_login"))


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
    attendance_rows = (
        sb_admin.table("attendance")
        .select("attendance_date,status,class_branch")
        .eq("student_id", student_row["id"])
        .order("attendance_date", desc=True)
        .execute()
        .data
        or []
    )
    attendance_history = [(r["attendance_date"], r["status"]) for r in attendance_rows]
    subjects = {}
    for row in attendance_rows:
        key = row.get("class_branch") or "General"
        stat = subjects.setdefault(key, {"name": key, "total_lectures": 0, "presents": 0, "absents": 0})
        stat["total_lectures"] += 1
        if row.get("status") == "present":
            stat["presents"] += 1
        elif row.get("status") == "absent":
            stat["absents"] += 1

    student = (
        profile.get("full_name"),
        profile.get("email"),
        student_row.get("board_roll_no"),
        student_row.get("branch"),
        student_row.get("semester"),
    )
    return render_template(
        "student_dashboard.html",
        student=student,
        attendance_history=attendance_history,
        subjects_data=list(subjects.values()),
    )


@web_bp.get("/teacher-dashboard", endpoint="teacher_dashboard")
def teacher_dashboard():
    if not _require_teacher_session():
        return redirect(url_for("teacher_login"))

    sb_admin = get_supabase_admin()
    branch = session.get("teacher_branch")
    semester = session.get("teacher_semester")
    teacher_id = session.get("teacher_id")
    teacher_subject = session.get("teacher_subject") or "General"

    student_rows = (
        sb_admin.table("students")
        .select("id,profile_id,board_roll_no,branch,semester")
        .eq("branch", branch)
        .eq("semester", semester)
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
        students.append((row["id"], p.get("full_name", "Unknown"), row.get("board_roll_no"), row.get("branch"), p.get("email", "")))
        student_id_list.append(row["id"])

    today_str = str(date.today())
    attendance_today_rows = []
    all_attendance_rows = []
    if student_id_list:
        attendance_today_rows = (
            sb_admin.table("attendance")
            .select("*")
            .in_("student_id", student_id_list)
            .eq("attendance_date", today_str)
            .execute()
            .data
            or []
        )
        all_attendance_rows = (
            sb_admin.table("attendance")
            .select("*")
            .in_("student_id", student_id_list)
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
    teacher_id = session.get("teacher_id")
    branch = session.get("teacher_branch")
    semester = session.get("teacher_semester")
    today_str = str(date.today())

    student_rows = (
        sb_admin.table("students")
        .select("id")
        .eq("branch", branch)
        .eq("semester", semester)
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
                "teacher_id": teacher_id,
                "class_branch": branch,
                "class_semester": semester,
                "attendance_date": today_str,
                "status": status,
            },
            on_conflict="student_id,attendance_date",
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

    student_rows = (
        sb_admin.table("students")
        .select("id,profile_id,board_roll_no")
        .eq("branch", branch)
        .eq("semester", semester)
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
        writer.writerow(
            [
                p.get("full_name", "Unknown"),
                p.get("email", ""),
                s.get("board_roll_no", ""),
                row.get("class_branch", ""),
                row.get("class_semester", ""),
                row.get("attendance_date", ""),
                row.get("status", ""),
            ]
        )

    csv_bytes = BytesIO(csv_buffer.getvalue().encode("utf-8"))
    csv_bytes.seek(0)
    return send_file(
        csv_bytes,
        mimetype="text/csv",
        as_attachment=True,
        download_name="attendance_export.csv",
    )


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
