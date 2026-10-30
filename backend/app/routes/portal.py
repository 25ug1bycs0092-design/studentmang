from flask import Blueprint, jsonify

from backend.app.models import AcademicResult, Attendance, Course, Enrollment, FeeAccount, Student
from backend.app.security import current_user, roles
from backend.app.serializers import (
    serialize_attendance,
    serialize_course,
    serialize_fee_account,
    serialize_result,
    serialize_student,
)
from backend.app.validation import ApiError

portal_bp = Blueprint("portal", __name__)


@portal_bp.get("/portal/me")
@roles("student")
def my_portal():
    user = current_user()
    student: Student | None = user.student
    if student is None:
        raise ApiError("Student profile was not found.", 404)
    course_ids = {enrollment.course_id for enrollment in student.enrollments}
    courses = Course.query.filter(
        (Course.id.in_(course_ids)) | (Course.name == student.course_name)
    ).order_by(Course.name).all()
    attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(366).all()
    accounts = FeeAccount.query.filter_by(student_id=student.id).order_by(FeeAccount.period.desc()).all()
    results = AcademicResult.query.filter_by(student_id=student.id).order_by(AcademicResult.recorded_at.desc()).all()
    return jsonify(
        {
            "profile": serialize_student(student),
            "courses": [serialize_course(course) for course in courses],
            "attendance": [serialize_attendance(record) for record in attendance],
            "fees": [serialize_fee_account(account) for account in accounts],
            "results": [serialize_result(result) for result in results],
        }
    )
