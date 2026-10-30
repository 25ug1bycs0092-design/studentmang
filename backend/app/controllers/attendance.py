from datetime import date

from flask import request

from backend.app.extensions import db
from backend.app.models import Attendance, Student, Teacher
from backend.app.security import current_user
from backend.app.validation import ATTENDANCE_STATUSES, ApiError, date_value, status_value


def attendance_for_date(selected_date: date) -> list[Attendance]:
    query = Attendance.query.filter_by(date=selected_date)
    user = current_user()
    if user.role == "student":
        query = query.filter_by(student_id=user.student_id)
    elif user.role == "teacher":
        teacher: Teacher | None = user.teacher
        allowed_courses = {course.name.lower() for course in (teacher.courses if teacher else [])}
        students = Student.query.all()
        allowed_ids = [student.id for student in students if student.course_name.lower() in allowed_courses]
        query = query.filter(Attendance.student_id.in_(allowed_ids))
    student_id = request.args.get("student_id")
    if student_id:
        if user.role == "student" and user.student_id != student_id:
            raise ApiError("Students may only access their own attendance.", 403)
        query = query.filter_by(student_id=student_id)
    return query.order_by(Attendance.student_id).all()


def mark_attendance(data: dict, user_id: int) -> list[Attendance]:
    selected_date = date_value(data.get("date"), default_today=True)
    records = data.get("records")
    if records is None:
        records = [data]
    if not isinstance(records, list) or not records:
        raise ApiError("records must be a non-empty array.")
    if len(records) > 500:
        raise ApiError("At most 500 attendance records can be submitted at once.")
    seen: set[str] = set()
    saved: list[Attendance] = []
    user = current_user()
    allowed_courses = {
        course.name.lower() for course in (user.teacher.courses if user.role == "teacher" and user.teacher else [])
    }
    for entry in records:
        if not isinstance(entry, dict):
            raise ApiError("Each attendance record must be an object.")
        student_id = entry.get("student_id") or entry.get("studentId")
        if not isinstance(student_id, str) or not student_id.strip():
            raise ApiError("Every attendance record must include student_id.")
        student_id = student_id.strip()
        if student_id in seen:
            raise ApiError(f"Duplicate attendance entry for student {student_id}.")
        seen.add(student_id)
        if user.role == "student" and user.student_id != student_id:
            raise ApiError("Students may only mark their own attendance.", 403)
        student = db.session.get(Student, student_id)
        if student is None:
            raise ApiError(f"Student {student_id} was not found.", 404)
        if user.role == "teacher" and student.course_name.lower() not in allowed_courses:
            raise ApiError(f"You are not assigned to student {student_id}'s course.", 403)
        entry_date = date_value(entry.get("date", selected_date.isoformat()))
        if entry_date != selected_date:
            raise ApiError("All attendance records must use the same date.")
        status = status_value(entry.get("status"), ATTENDANCE_STATUSES, "Attendance status")
        attendance = Attendance.query.filter_by(student_id=student_id, date=selected_date).first()
        if attendance is None:
            attendance = Attendance(student_id=student_id, date=selected_date)
            db.session.add(attendance)
        attendance.status = status
        attendance.marked_by = user_id
        saved.append(attendance)
    db.session.flush()
    return saved
