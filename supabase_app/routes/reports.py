from flask import Blueprint, jsonify, request

from ..auth import require_auth
from ..supabase_client import get_supabase_admin

reports_bp = Blueprint("reports_bp", __name__, url_prefix="/api/reports")


def _percentage(present_count, total_count):
    if total_count == 0:
        return 0.0
    return round((present_count / total_count) * 100, 2)


@reports_bp.get("/student/<student_id>")
@require_auth(roles=["teacher", "admin"])
def student_report(student_id):
    start_date = request.args.get("from")
    end_date = request.args.get("to")

    sb = get_supabase_admin()
    q = sb.table("attendance").select("status,attendance_date").eq("student_id", student_id)
    if start_date:
        q = q.gte("attendance_date", start_date)
    if end_date:
        q = q.lte("attendance_date", end_date)
    rows = q.execute().data or []

    total = len(rows)
    present = sum(1 for row in rows if row.get("status") == "present")
    absent = total - present
    return jsonify(
        {
            "student_id": student_id,
            "total_days": total,
            "present_days": present,
            "absent_days": absent,
            "attendance_percentage": _percentage(present, total),
        }
    )


@reports_bp.get("/class")
@require_auth(roles=["teacher", "admin"])
def class_report():
    branch = request.args.get("branch")
    semester = request.args.get("semester")
    start_date = request.args.get("from")
    end_date = request.args.get("to")

    sb = get_supabase_admin()
    q = sb.table("attendance").select("student_id,status,attendance_date")
    if branch:
        q = q.eq("class_branch", branch)
    if semester:
        q = q.eq("class_semester", semester)
    if start_date:
        q = q.gte("attendance_date", start_date)
    if end_date:
        q = q.lte("attendance_date", end_date)
    rows = q.execute().data or []

    per_student = {}
    for row in rows:
        sid = row["student_id"]
        cur = per_student.setdefault(sid, {"total": 0, "present": 0})
        cur["total"] += 1
        if row.get("status") == "present":
            cur["present"] += 1

    output = []
    for sid, metrics in per_student.items():
        output.append(
            {
                "student_id": sid,
                "total_days": metrics["total"],
                "present_days": metrics["present"],
                "attendance_percentage": _percentage(metrics["present"], metrics["total"]),
            }
        )

    return jsonify(
        {
            "branch": branch,
            "semester": semester,
            "students": output,
            "student_count": len(output),
        }
    )
