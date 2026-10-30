from functools import wraps
from typing import Callable

from flask import g
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.app.extensions import db
from backend.app.models import User
from backend.app.validation import ApiError


def authenticated(view: Callable):
    @wraps(view)
    @jwt_required()
    def wrapped(*args, **kwargs):
        user = db.session.get(User, int(get_jwt_identity()))
        if user is None or not user.active:
            raise ApiError("This account is unavailable.", 401)
        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


def roles(*allowed_roles: str):
    def decorate(view: Callable):
        @wraps(view)
        @authenticated
        def wrapped(*args, **kwargs):
            if g.current_user.role not in allowed_roles:
                raise ApiError("You do not have permission to perform this action.", 403)
            return view(*args, **kwargs)

        return wrapped

    return decorate


def current_user() -> User:
    user = getattr(g, "current_user", None)
    if user is None:
        raise ApiError("Authentication is required.", 401)
    return user


def require_student_access(student_id: str) -> None:
    user = current_user()
    if user.role == "student" and user.student_id != student_id:
        raise ApiError("Students may only access their own records.", 403)


def require_teacher_access(teacher_id: str) -> None:
    user = current_user()
    if user.role == "teacher" and user.teacher_id != teacher_id:
        raise ApiError("Teachers may only access their own profile.", 403)
