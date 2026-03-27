from flask import Blueprint, g, jsonify, request

from ..auth import require_auth
from ..supabase_client import get_supabase_admin

attendance_bp = Blueprint("attendance_bp", __name__, url_prefix="/api/attendance")


@attendance_bp.post("")
@require_auth(roles=["teacher", "admin"])
def mark_attendance():
    data = request.get_json(silent=True) or {}
    required = {"student_id", "teacher_id", "class_branch", "class_semester", "attendance_date", "status"}
    if not required.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400
    if data.get("status") not in {"present", "absent", "late"}:
        return jsonify({"error": "status must be present/absent/late"}), 400

    sb = get_supabase_admin()
    result = sb.table("attendance").upsert(
        data,
        on_conflict="student_id,attendance_date",
    ).execute()
    return jsonify(result.data), 201


@attendance_bp.get("")
@require_auth(roles=["student", "teacher", "admin"])
def list_attendance():
    sb = get_supabase_admin()
    q = sb.table("attendance").select("*")

    date = request.args.get("date")
    student_id = request.args.get("student_id")
    class_branch = request.args.get("class_branch")
    class_semester = request.args.get("class_semester")
    status = request.args.get("status")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if date:
        q = q.eq("attendance_date", date)
    if student_id:
        q = q.eq("student_id", student_id)
    if class_branch:
        q = q.eq("class_branch", class_branch)
    if class_semester:
        q = q.eq("class_semester", class_semester)
    if status:
        q = q.eq("status", status)
    if start_date:
        q = q.gte("attendance_date", start_date)
    if end_date:
        q = q.lte("attendance_date", end_date)

    # Restrict students to their own attendance
    if g.profile.get("role") == "student":
        s_rows = (
            sb.table("students")
            .select("id")
            .eq("profile_id", g.user_id)
            .limit(1)
            .execute()
            .data
        )
        if not s_rows:
            return jsonify({"error": "Student row not found"}), 404
        q = q.eq("student_id", s_rows[0]["id"])

    result = q.order("attendance_date", desc=True).execute()
    return jsonify(result.data)


@attendance_bp.put("/<attendance_id>")
@require_auth(roles=["teacher", "admin"])
def update_attendance(attendance_id):
    data = request.get_json(silent=True) or {}
    sb = get_supabase_admin()
    result = sb.table("attendance").update(data).eq("id", attendance_id).execute()
    return jsonify(result.data)


@attendance_bp.delete("/<attendance_id>")
@require_auth(roles=["teacher", "admin"])
def delete_attendance(attendance_id):
    sb = get_supabase_admin()
    sb.table("attendance").delete().eq("id", attendance_id).execute()
    return jsonify({"message": "Attendance deleted"})
