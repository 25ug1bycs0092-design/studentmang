from flask import Blueprint, jsonify, request

from backend.app.controllers.records import create_course, list_courses, update_course
from backend.app.extensions import db
from backend.app.models import Course, Department, Enrollment, Student, Teacher
from backend.app.security import current_user, roles
from backend.app.serializers import serialize_course, serialize_student
from backend.app.validation import ApiError, json_object, required_text

courses_bp = Blueprint("courses", __name__)


@courses_bp.get("/courses")
@roles("admin", "teacher", "student")
def get_courses():
    courses = list_courses()
    user = current_user()
    if user.role == "teacher":
        allowed = {course.id for course in user.teacher.courses} if user.teacher else set()
        courses = [course for course in courses if course.id in allowed]
    if user.role == "student":
        enrolled = {enrollment.course_id for enrollment in user.student.enrollments} if user.student else set()
        courses = [course for course in courses if course.id in enrolled or course.name == user.student.course_name]
    return jsonify([serialize_course(course) for course in courses])


@courses_bp.post("/courses")
@roles("admin")
def add_course():
    course = create_course(json_object())
    db.session.add(course)
    db.session.commit()
    return jsonify(serialize_course(course)), 201


@courses_bp.get("/courses/<string:course_id>")
@roles("admin", "teacher", "student")
def get_course(course_id: str):
    course = db.session.get(Course, course_id)
    if course is None:
        raise ApiError("Course was not found.", 404)
    user = current_user()
    if user.role == "teacher" and (not user.teacher or course.teacher_id != user.teacher.id):
        raise ApiError("You may only access courses assigned to you.", 403)
    if user.role == "student" and (
        not user.student
        or (
            course.name != user.student.course_name
            and not Enrollment.query.filter_by(student_id=user.student.id, course_id=course.id).first()
        )
    ):
        raise ApiError("You may only access your enrolled courses.", 403)
    return jsonify(serialize_course(course))


@courses_bp.put("/courses/<string:course_id>")
@roles("admin")
def edit_course(course_id: str):
    course = db.session.get(Course, course_id)
    if course is None:
        raise ApiError("Course was not found.", 404)
    update_course(course, json_object())
    db.session.commit()
    return jsonify(serialize_course(course))


@courses_bp.delete("/courses/<string:course_id>")
@roles("admin")
def remove_course(course_id: str):
    course = db.session.get(Course, course_id)
    if course is None:
        raise ApiError("Course was not found.", 404)
    db.session.delete(course)
    db.session.commit()
    return "", 204


@courses_bp.get("/courses/<string:course_id>/enrollments")
@roles("admin", "teacher")
def list_enrollments(course_id: str):
    course = db.session.get(Course, course_id)
    if course is None:
        raise ApiError("Course was not found.", 404)
    user = current_user()
    if user.role == "teacher" and (not user.teacher or course.teacher_id != user.teacher.id):
        raise ApiError("You may only access courses assigned to you.", 403)
    return jsonify([serialize_student(enrollment.student, include_financials=False) for enrollment in course.enrollments])


@courses_bp.post("/courses/<string:course_id>/enrollments")
@roles("admin")
def enroll_student(course_id: str):
    course = db.session.get(Course, course_id)
    if course is None:
        raise ApiError("Course was not found.", 404)
    data = json_object()
    student_id = required_text(data, "student_id", "Student ID", 40)
    student = db.session.get(Student, student_id)
    if student is None:
        raise ApiError("Student was not found.", 404)
    if Enrollment.query.filter_by(course_id=course.id, student_id=student.id).first():
        raise ApiError("Student is already enrolled in this course.", 409)
    if Enrollment.query.filter_by(course_id=course.id).count() >= course.capacity:
        raise ApiError("This course has reached its enrollment capacity.", 409)
    enrollment = Enrollment(course=course, student=student)
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"id": enrollment.id, "course_id": course.id, "student_id": student.id, "enrolled_at": enrollment.enrolled_at.isoformat()}), 201


@courses_bp.delete("/courses/<string:course_id>/enrollments/<string:student_id>")
@roles("admin")
def drop_student(course_id: str, student_id: str):
    enrollment = Enrollment.query.filter_by(course_id=course_id, student_id=student_id).first()
    if enrollment is None:
        raise ApiError("Enrollment was not found.", 404)
    db.session.delete(enrollment)
    db.session.commit()
    return "", 204


@courses_bp.get("/departments")
@roles("admin", "teacher", "student")
def get_departments():
    return jsonify([{"id": item.id, "name": item.name} for item in Department.query.order_by(Department.name).all()])


@courses_bp.post("/departments")
@roles("admin")
def add_department():
    data = json_object()
    name = required_text(data, "name", "Department name", 100)
    if Department.query.filter(db.func.lower(Department.name) == name.lower()).first():
        raise ApiError("Department already exists.", 409)
    department = Department(name=name)
    db.session.add(department)
    db.session.commit()
    return jsonify({"id": department.id, "name": department.name}), 201


@courses_bp.put("/departments/<int:department_id>")
@roles("admin")
def edit_department(department_id: int):
    department = db.session.get(Department, department_id)
    if department is None:
        raise ApiError("Department was not found.", 404)
    name = required_text(json_object(), "name", "Department name", 100)
    duplicate = Department.query.filter(
        db.func.lower(Department.name) == name.lower(),
        Department.id != department.id,
    ).first()
    if duplicate:
        raise ApiError("Department already exists.", 409)
    department.name = name
    db.session.commit()
    return jsonify({"id": department.id, "name": department.name})


@courses_bp.delete("/departments/<int:department_id>")
@roles("admin")
def remove_department(department_id: int):
    department = db.session.get(Department, department_id)
    if department is None:
        raise ApiError("Department was not found.", 404)
    db.session.delete(department)
    db.session.commit()
    return "", 204
