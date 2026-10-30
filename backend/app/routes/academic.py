from flask import Blueprint, jsonify, request
from backend.app.extensions import db
from backend.app.models import AcademicResult, Course, Student
from backend.app.security import current_user, roles
from backend.app.serializers import serialize_result
from backend.app.validation import ApiError, date_value, decimal_value, json_object, required_text

academic_bp = Blueprint("academic", __name__)


@academic_bp.get("/results")
@roles("admin", "teacher", "student")
def list_results():
    user = current_user()
    query = AcademicResult.query
    if user.role == "student":
        query = query.filter_by(student_id=user.student_id)
    elif user.role == "teacher":
        course_ids = [course.id for course in user.teacher.courses] if user.teacher else []
        query = query.filter(AcademicResult.course_id.in_(course_ids))
    student_id = request.args.get("student_id")
    course_id = request.args.get("course_id")
    if student_id:
        if user.role == "student" and student_id != user.student_id:
            raise ApiError("Students may only access their own results.", 403)
        query = query.filter_by(student_id=student_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    return jsonify([serialize_result(result) for result in query.order_by(AcademicResult.recorded_at.desc()).all()])


@academic_bp.post("/results")
@roles("admin", "teacher")
def add_result():
    data = json_object()
    student_id = required_text(data, "student_id", "Student ID", 40)
    course_id = required_text(data, "course_id", "Course ID", 40)
    student = db.session.get(Student, student_id)
    course = db.session.get(Course, course_id)
    if student is None or course is None:
        raise ApiError("A valid student and course are required.", 404)
    user = current_user()
    if user.role == "teacher" and (not user.teacher or course.teacher_id != user.teacher.id):
        raise ApiError("Teachers may only record results for their assigned courses.", 403)
    score = decimal_value(data.get("score"), "Score")
    max_score = decimal_value(data.get("max_score", 100), "Maximum score")
    if max_score <= 0 or score > max_score:
        raise ApiError("Score must be between zero and the maximum score.")
    result = AcademicResult(
        student=student,
        course=course,
        term=required_text(data, "term", "Term", 80),
        assessment=required_text(data, "assessment", "Assessment", 120),
        score=score,
        max_score=max_score,
        recorded_at=date_value(data["recorded_at"], "Recorded date") if data.get("recorded_at") else date_value(None, default_today=True),
    )
    db.session.add(result)
    db.session.commit()
    return jsonify(serialize_result(result)), 201


@academic_bp.delete("/results/<int:result_id>")
@roles("admin", "teacher")
def delete_result(result_id: int):
    result = db.session.get(AcademicResult, result_id)
    if result is None:
        raise ApiError("Academic result was not found.", 404)
    user = current_user()
    if user.role == "teacher" and (not user.teacher or result.course.teacher_id != user.teacher.id):
        raise ApiError("Teachers may only modify results for their assigned courses.", 403)
    db.session.delete(result)
    db.session.commit()
    return "", 204
