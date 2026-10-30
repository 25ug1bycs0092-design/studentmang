from flask import Blueprint, g, jsonify
from flask_jwt_extended import create_access_token
from sqlalchemy import or_

from backend.app.controllers.records import create_user_account
from backend.app.extensions import db
from backend.app.models import User
from backend.app.security import current_user, roles
from backend.app.validation import ApiError, email_value, json_object, required_text

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    data = json_object()
    role = data.get("role")
    if role not in {"admin", "teacher", "student"}:
        raise ApiError("role must be admin, teacher, or student.")
    identity = required_text(data, "identity", "Email address or account ID", 254).strip()
    password = data.get("password")
    if not isinstance(password, str) or not password:
        raise ApiError("Password is required.")
    if role == "admin":
        identity = identity.lower()
    account_query = User.query.filter_by(role=role, active=True)
    if role == "student":
        account_query = account_query.filter(
            or_(User.email == identity.lower(), User.student_id == identity)
        )
    elif role == "teacher":
        account_query = account_query.filter(User.email == identity.lower())
    else:
        account_query = account_query.filter(User.email == identity.lower())
    account = account_query.first()
    if account is None or not account.check_password(password):
        raise ApiError("Invalid credentials.", 401)
    token = create_access_token(identity=str(account.id))
    return jsonify(
        {
            "token": token,
            "role": account.role,
            "name": account.display_name,
            "user_id": account.id,
            "student_id": account.student_id,
            "teacher_id": account.teacher_id,
        }
    )


@auth_bp.get("/auth/me")
@roles("admin", "teacher", "student")
def me():
    account = current_user()
    return jsonify(
        {
            "user_id": account.id,
            "email": account.email,
            "role": account.role,
            "name": account.display_name,
            "student_id": account.student_id,
            "teacher_id": account.teacher_id,
        }
    )


@auth_bp.post("/auth/users")
@roles("admin")
def create_account():
    data = json_object()
    account = create_user_account(data)
    db.session.commit()
    return (
        jsonify(
            {
                "user_id": account.id,
                "email": account.email,
                "role": account.role,
                "student_id": account.student_id,
                "teacher_id": account.teacher_id,
            }
        ),
        201,
    )
