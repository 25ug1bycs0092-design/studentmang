from flask import Blueprint, jsonify, request

from backend.app.controllers.records import create_student, list_students, update_student
from backend.app.extensions import db
from backend.app.models import Student
from backend.app.security import current_user, require_student_access, roles
from backend.app.serializers import serialize_student
from backend.app.validation import ApiError, json_object

students_bp = Blueprint("students", __name__)


@students_bp.get("/students")
@roles("admin", "teacher")
def get_students():
    user = current_user()
    students = list_students()
    if user.role == "teacher":
        course_names = {course.name.lower() for course in user.teacher.courses} if user.teacher else set()
        students = [student for student in students if student.course_name.lower() in course_names]
    return jsonify([serialize_student(student, include_financials=user.role == "admin") for student in students])


@students_bp.post("/students")
@roles("admin")
def add_student():
    student = create_student(json_object())
    db.session.commit()
    return jsonify(serialize_student(student)), 201


@students_bp.get("/students/<string:student_id>")
@roles("admin", "teacher", "student")
def get_student(student_id: str):
    require_student_access(student_id)
    student = db.session.get(Student, student_id)
    if student is None:
        raise ApiError("Student was not found.", 404)
    user = current_user()
    if user.role == "teacher":
        course_names = {course.name.lower() for course in user.teacher.courses} if user.teacher else set()
        if student.course_name.lower() not in course_names:
            raise ApiError("You may only access students enrolled in your courses.", 403)
    return jsonify(serialize_student(student, include_financials=user.role != "teacher"))


@students_bp.put("/students/<string:student_id>")
@roles("admin")
def edit_student(student_id: str):
    student = db.session.get(Student, student_id)
    if student is None:
        raise ApiError("Student was not found.", 404)
    update_student(student, json_object())
    db.session.commit()
    return jsonify(serialize_student(student))


@students_bp.delete("/students/<string:student_id>")
@roles("admin")
def remove_student(student_id: str):
    student = db.session.get(Student, student_id)
    if student is None:
        raise ApiError("Student was not found.", 404)
    db.session.delete(student)
    db.session.commit()
    return "", 204
