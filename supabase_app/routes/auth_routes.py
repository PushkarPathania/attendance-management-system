from flask import Blueprint, jsonify, request

from ..supabase_client import get_supabase_admin, get_supabase_public

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    role = (data.get("role") or "student").strip().lower()
    branch = (data.get("branch") or "").strip()
    semester = str(data.get("semester") or "").strip()

    if not email or not password or not full_name:
        return jsonify({"error": "email, password, full_name are required"}), 400
    if role not in {"student", "teacher"}:
        return jsonify({"error": "role must be student or teacher"}), 400

    sb_admin = get_supabase_admin()
    created = sb_admin.auth.admin.create_user(
        {
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {"role": role},
        }
    )
    user_id = created.user.id

    sb_admin.table("profiles").upsert(
        {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "role": role,
            "branch": branch or None,
            "semester": semester or None,
        }
    ).execute()

    if role == "student":
        sb_admin.table("students").upsert(
            {
                "profile_id": user_id,
                "board_roll_no": str(data.get("board_roll_no") or email),
                "branch": branch or "General",
                "semester": semester or "1",
            },
            on_conflict="profile_id",
        ).execute()
    else:
        sb_admin.table("teachers").upsert(
            {
                "profile_id": user_id,
                "branch": branch or "General",
                "semester": semester or "1",
                "subject": data.get("subject"),
                "department": data.get("department"),
            },
            on_conflict="profile_id,branch,semester",
        ).execute()

    return jsonify({"message": "Signup successful", "user_id": user_id}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    sb_public = get_supabase_public()
    auth_res = sb_public.auth.sign_in_with_password({"email": email, "password": password})
    if not auth_res or not auth_res.session:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify(
        {
            "access_token": auth_res.session.access_token,
            "refresh_token": auth_res.session.refresh_token,
            "user": {
                "id": auth_res.user.id,
                "email": auth_res.user.email,
            },
        }
    )
