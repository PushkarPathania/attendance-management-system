import uuid

from flask import Blueprint, current_app, jsonify, request

from ..auth import require_auth
from ..supabase_client import get_supabase_admin

uploads_bp = Blueprint("uploads_bp", __name__, url_prefix="/api/uploads")


@uploads_bp.post("/profile-image")
@require_auth(roles=["student", "teacher", "admin"])
def upload_profile_image():
    file = request.files.get("file")
    profile_id = request.form.get("profile_id")

    if not file or not profile_id:
        return jsonify({"error": "file and profile_id are required"}), 400

    ext = (file.filename.rsplit(".", 1)[-1] if "." in file.filename else "bin").lower()
    object_path = f"{profile_id}/{uuid.uuid4()}.{ext}"
    content = file.read()

    sb = get_supabase_admin()
    bucket = current_app.config["SUPABASE_PROFILE_BUCKET"]
    sb.storage.from_(bucket).upload(
        object_path,
        content,
        {"content-type": file.mimetype or "application/octet-stream"},
    )
    public_url = sb.storage.from_(bucket).get_public_url(object_path)

    sb.table("profiles").update({"avatar_url": public_url}).eq("id", profile_id).execute()
    return jsonify({"avatar_url": public_url, "path": object_path}), 201
