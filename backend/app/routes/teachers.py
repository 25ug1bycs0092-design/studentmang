from flask import Blueprint, jsonify

from backend.app.controllers.records import create_teacher, list_teachers, update_teacher
from backend.app.extensions import db
from backend.app.models import Teacher
from backend.app.security import current_user, require_teacher_access, roles
from backend.app.serializers import serialize_teacher
from backend.app.validation import ApiError, json_object

teachers_bp = Blueprint("teachers", __name__)


@teachers_bp.get("/teachers")
@roles("admin", "teacher")
def get_teachers():
    user = current_user()
    teachers = list_teachers()
    if user.role == "teacher":
        teachers = [teacher for teacher in teachers if user.teacher and teacher.id == user.teacher.id]
    return jsonify([serialize_teacher(teacher) for teacher in teachers])


@teachers_bp.post("/teachers")
@roles("admin")
def add_teacher():
    teacher = create_teacher(json_object())
    db.session.commit()
    return jsonify(serialize_teacher(teacher)), 201


@teachers_bp.get("/teachers/<string:teacher_id>")
@roles("admin", "teacher")
def get_teacher(teacher_id: str):
    require_teacher_access(teacher_id)
    teacher = db.session.get(Teacher, teacher_id)
    if teacher is None:
        raise ApiError("Teacher was not found.", 404)
    return jsonify(serialize_teacher(teacher))


@teachers_bp.put("/teachers/<string:teacher_id>")
@roles("admin")
def edit_teacher(teacher_id: str):
    teacher = db.session.get(Teacher, teacher_id)
    if teacher is None:
        raise ApiError("Teacher was not found.", 404)
    update_teacher(teacher, json_object())
    db.session.commit()
    return jsonify(serialize_teacher(teacher))


@teachers_bp.delete("/teachers/<string:teacher_id>")
@roles("admin")
def remove_teacher(teacher_id: str):
    teacher = db.session.get(Teacher, teacher_id)
    if teacher is None:
        raise ApiError("Teacher was not found.", 404)
    db.session.delete(teacher)
    db.session.commit()
    return "", 204
