from flask import Blueprint, jsonify, request

from ..auth import require_auth
from ..supabase_client import get_supabase_admin

students_bp = Blueprint("students_bp", __name__, url_prefix="/api/students")


@students_bp.get("")
@require_auth(roles=["teacher", "admin"])
def list_students():
    sb = get_supabase_admin()
    q = sb.table("students").select("*")
    branch = request.args.get("branch")
    semester = request.args.get("semester")
    if branch:
        q = q.eq("branch", branch)
    if semester:
        q = q.eq("semester", semester)
    return jsonify(q.order("created_at", desc=True).execute().data)


@students_bp.post("")
@require_auth(roles=["teacher", "admin"])
def create_student():
    data = request.get_json(silent=True) or {}
    required = {"profile_id", "board_roll_no", "branch", "semester"}
    if not required.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400
    sb = get_supabase_admin()
    result = sb.table("students").insert(data).execute()
    return jsonify(result.data), 201


@students_bp.get("/<student_id>")
@require_auth(roles=["student", "teacher", "admin"])
def get_student(student_id):
    sb = get_supabase_admin()
    result = sb.table("students").select("*").eq("id", student_id).limit(1).execute().data
    if not result:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(result[0])


@students_bp.put("/<student_id>")
@require_auth(roles=["teacher", "admin"])
def update_student(student_id):
    data = request.get_json(silent=True) or {}
    sb = get_supabase_admin()
    result = sb.table("students").update(data).eq("id", student_id).execute()
    return jsonify(result.data)


@students_bp.delete("/<student_id>")
@require_auth(roles=["teacher", "admin"])
def delete_student(student_id):
    sb = get_supabase_admin()
    sb.table("students").delete().eq("id", student_id).execute()
    return jsonify({"message": "Student deleted"})
