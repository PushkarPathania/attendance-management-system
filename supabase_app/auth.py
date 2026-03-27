from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .supabase_client import get_supabase_admin


def _decode_jwt(token):
    return jwt.decode(
        token,
        current_app.config["SUPABASE_JWT_SECRET"],
        algorithms=["HS256"],
        options={"verify_aud": False},
    )


def _token_from_header():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def require_auth(roles=None):
    roles = roles or []

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            token = _token_from_header()
            if not token:
                return jsonify({"error": "Missing bearer token"}), 401
            try:
                payload = _decode_jwt(token)
                user_id = payload.get("sub")
                if not user_id:
                    return jsonify({"error": "Invalid token payload"}), 401

                sb = get_supabase_admin()
                profile_res = (
                    sb.table("profiles").select("*").eq("id", user_id).limit(1).execute()
                )
                rows = profile_res.data or []
                if not rows:
                    return jsonify({"error": "Profile not found"}), 403

                profile = rows[0]
                if roles and profile.get("role") not in roles:
                    return jsonify({"error": "Forbidden"}), 403

                g.user_id = user_id
                g.profile = profile
                g.jwt_payload = payload
            except Exception as exc:
                return jsonify({"error": "Invalid token", "details": str(exc)}), 401
            return fn(*args, **kwargs)

        return wrapper

    return decorator
