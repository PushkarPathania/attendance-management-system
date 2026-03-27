from flask import Blueprint, jsonify, request

from ..auth import require_auth
from ..supabase_client import get_supabase_admin

teachers_bp = Blueprint("teachers_bp", __name__, url_prefix="/api/teachers")


@teachers_bp.get("")
@require_auth(roles=["teacher", "admin"])
def list_teachers():
    sb = get_supabase_admin()
    q = sb.table("teachers").select("*")
    branch = request.args.get("branch")
    semester = request.args.get("semester")
    if branch:
        q = q.eq("branch", branch)
    if semester:
        q = q.eq("semester", semester)
    return jsonify(q.order("created_at", desc=True).execute().data)


@teachers_bp.post("")
@require_auth(roles=["admin"])
def create_teacher():
    data = request.get_json(silent=True) or {}
    required = {"profile_id", "branch", "semester"}
    if not required.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400
    sb = get_supabase_admin()
    result = sb.table("teachers").insert(data).execute()
    return jsonify(result.data), 201


@teachers_bp.get("/<teacher_id>")
@require_auth(roles=["teacher", "admin"])
def get_teacher(teacher_id):
    sb = get_supabase_admin()
    result = sb.table("teachers").select("*").eq("id", teacher_id).limit(1).execute().data
    if not result:
        return jsonify({"error": "Teacher not found"}), 404
    return jsonify(result[0])


@teachers_bp.put("/<teacher_id>")
@require_auth(roles=["admin"])
def update_teacher(teacher_id):
    data = request.get_json(silent=True) or {}
    sb = get_supabase_admin()
    result = sb.table("teachers").update(data).eq("id", teacher_id).execute()
    return jsonify(result.data)


@teachers_bp.delete("/<teacher_id>")
@require_auth(roles=["admin"])
def delete_teacher(teacher_id):
    sb = get_supabase_admin()
    sb.table("teachers").delete().eq("id", teacher_id).execute()
    return jsonify({"message": "Teacher deleted"})
