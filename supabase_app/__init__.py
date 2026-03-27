from pathlib import Path

from flask import Flask, jsonify

from .config import Config
from .routes.attendance import attendance_bp
from .routes.auth_routes import auth_bp
from .routes.reports import reports_bp
from .routes.students import students_bp
from .routes.teachers import teachers_bp
from .routes.uploads import uploads_bp
from .routes.web import web_bp


def create_app():
    project_root = Path(__file__).resolve().parents[1]
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )
    app.config.from_object(Config)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "supabase-attendance-api"})

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(teachers_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(web_bp)

    # Keep compatibility with existing templates that call unprefixed endpoints
    # like url_for('admin_login') from the previous non-blueprint app.
    for rule in list(app.url_map.iter_rules()):
        if not rule.endpoint.startswith("web_bp."):
            continue
        short_endpoint = rule.endpoint.split(".", 1)[1]
        if short_endpoint in app.view_functions:
            continue
        methods = sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"})
        app.add_url_rule(
            rule.rule,
            endpoint=short_endpoint,
            view_func=app.view_functions[rule.endpoint],
            methods=methods,
        )

    return app
