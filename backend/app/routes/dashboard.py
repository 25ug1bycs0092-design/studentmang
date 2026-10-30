from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify
from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models import Attendance, Course, FeeAccount, Payment, Student, Teacher
from backend.app.security import current_user, roles

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard")
@roles("admin", "teacher")
def get_dashboard():
    user = current_user()
    assigned_courses = user.teacher.courses if user.role == "teacher" and user.teacher else []
    if user.role == "teacher":
        course_names = [course.name for course in assigned_courses]
        students = Student.query.filter(Student.course_name.in_(course_names)).all() if course_names else []
        total_students = len(students)
        total_teachers = 1 if user.teacher else 0
        total_courses = len([course for course in assigned_courses if course.status == "Active"])
        student_ids = [student.id for student in students]
        present_today = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.date == date.today(),
            Attendance.status == "Present",
        ).count()
        attendance_marked = Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.date == date.today(),
        ).count()
    else:
        total_students = Student.query.count()
        total_teachers = Teacher.query.filter_by(status="Active").count()
        total_courses = Course.query.filter_by(status="Active").count()
        present_today = Attendance.query.filter_by(date=date.today(), status="Present").count()
        attendance_marked = Attendance.query.filter_by(date=date.today()).count()
    attendance_percent = round(present_today * 100 / attendance_marked) if attendance_marked else 0
    if user.role == "admin":
        total_billed = db.session.query(func.coalesce(func.sum(FeeAccount.total_due), 0)).scalar()
        total_collected = db.session.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
    else:
        total_billed = 0
        total_collected = 0
    billed = Decimal(str(total_billed))
    collected = Decimal(str(total_collected))
    return jsonify(
        {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_courses": total_courses,
            "attendance": {
                "date": date.today().isoformat(),
                "marked": attendance_marked,
                "present": present_today,
                "percent": attendance_percent,
            },
            "fees": {
                "billed": float(billed),
                "collected": float(collected),
                "pending": float(max(Decimal("0.00"), billed - collected)),
            } if user.role == "admin" else None,
        }
    )
