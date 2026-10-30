import logging
import os
import secrets

from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.app.config import Config, INSTANCE_PATH, PROJECT_ROOT
from backend.app.extensions import cors, db, jwt
from backend.app.routes import register_routes
from backend.app.validation import ApiError


def create_app(test_config: dict | None = None) -> Flask:
    INSTANCE_PATH.mkdir(parents=True, exist_ok=True)
    app = Flask(
        __name__,
        instance_path=str(INSTANCE_PATH),
        static_folder=None,
    )
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    production = os.getenv("FLASK_ENV", "").lower() == "production" or not app.debug and os.getenv("RENDER") == "true"
    if production and (not app.config.get("SECRET_KEY") or not app.config.get("JWT_SECRET_KEY")):
        raise RuntimeError("SECRET_KEY and JWT_SECRET_KEY must be configured in production.")
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = secrets.token_urlsafe(48)
    if not app.config.get("JWT_SECRET_KEY"):
        app.config["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
    if app.config.get("MAX_CONTENT_LENGTH") is None:
        app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:"):
        app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
        app.config["SQLALCHEMY_ENGINE_OPTIONS"].setdefault(
            "connect_args", {"check_same_thread": False}
        )
    else:
        app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
        app.config["SQLALCHEMY_ENGINE_OPTIONS"].setdefault("pool_pre_ping", True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "allow_headers": ["Authorization", "Content-Type"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            }
        },
    )
    register_routes(app)
    register_error_handlers(app)
    register_cli_commands(app)

    @app.get("/api/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            app.logger.exception("Database health check failed")
            return jsonify({"status": "unavailable", "message": "Database is not ready."}), 503
        return jsonify({"status": "ok", "database": "connected"})

    @app.get("/")
    def index():
        return send_from_directory(PROJECT_ROOT, "index.html")

    @app.get("/app.js")
    def frontend_javascript():
        return send_from_directory(PROJECT_ROOT, "app.js")

    @app.get("/styles.css")
    def frontend_styles():
        return send_from_directory(PROJECT_ROOT, "styles.css")

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        db.session.rollback()
        payload = {"error": error.message, "message": error.message}
        if error.details is not None:
            payload["details"] = error.details
        return jsonify(payload), error.status_code

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError):
        db.session.rollback()
        app.logger.info("Rejected request due to a database constraint: %s", error.orig)
        return jsonify({"error": "The request conflicts with an existing record.", "message": "The request conflicts with an existing record."}), 409

    @app.errorhandler(404)
    def handle_not_found(error):
        if app.request_class:
            from flask import request

            if request.path.startswith("/api/"):
                return jsonify({"error": "Resource was not found.", "message": "Resource was not found."}), 404
        return error

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        from flask import request

        if request.path.startswith("/api/"):
            return jsonify({"error": "Method not allowed.", "message": "Method not allowed."}), 405
        return error

    @app.errorhandler(413)
    def handle_too_large(_error):
        return jsonify({"error": "Request body is too large.", "message": "Request body is too large."}), 413

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        db.session.rollback()
        app.logger.exception("Unhandled request error", exc_info=error)
        return jsonify({"error": "An unexpected server error occurred.", "message": "An unexpected server error occurred."}), 500

    @jwt.unauthorized_loader
    def missing_token(reason: str):
        return jsonify({"error": "Authentication required.", "message": "Authentication required."}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason: str):
        return jsonify({"error": "Invalid authentication token.", "message": "Invalid authentication token."}), 401

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return jsonify({"error": "Authentication token expired.", "message": "Authentication token expired."}), 401


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command():
        """Create the configured database schema."""
        from backend.app import models  # noqa: F401

        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Insert realistic starter records; requires SEED_PASSWORD."""
        from backend.app.seed import seed_demo

        password = os.getenv("SEED_PASSWORD")
        if not password or len(password) < 10:
            raise SystemExit("Set SEED_PASSWORD to a unique password of at least 10 characters before seeding.")
        db.create_all()
        created = seed_demo(password)
        db.session.commit()
        print(f"Inserted {created} demo records. Change the seeded account passwords before production use.")


logging.getLogger("werkzeug").setLevel(logging.INFO)
