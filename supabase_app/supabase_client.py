from flask import current_app
from supabase import create_client


def get_supabase_admin():
    supabase_url = current_app.config.get("SUPABASE_URL", "").strip()
    service_role_key = current_app.config.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not supabase_url or not service_role_key:
        raise RuntimeError(
            "Supabase config missing. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env."
        )
    return create_client(
        supabase_url,
        service_role_key,
    )


def get_supabase_public():
    supabase_url = current_app.config.get("SUPABASE_URL", "").strip()
    anon_key = current_app.config.get("SUPABASE_ANON_KEY", "").strip()
    if not supabase_url or not anon_key:
        raise RuntimeError(
            "Supabase config missing. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env."
        )
    return create_client(
        supabase_url,
        anon_key,
    )
