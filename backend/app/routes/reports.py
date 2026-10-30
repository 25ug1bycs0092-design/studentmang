from collections import defaultdict
from datetime import date, timedelta

from flask import Blueprint, request
from sqlalchemy import case, func

from backend.app.extensions import db
from backend.app.models import AcademicResult, Attendance, Course, Enrollment, FeeAccount, Payment, Student
from backend.app.security import current_user, roles
from backend.app.serializers import serialize_result, student_attendance
from backend.app.validation import date_value

reports_bp = Blueprint("reports", __name__)


def _month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def _month_label(value: date) -> str:
    return value.strftime("%b")


def _start_of_month(value: date) -> date:
    return value.replace(day=1)


def _previous_month(value: date) -> date:
    return (value.replace(day=1) - timedelta(days=1)).replace(day=1)


@reports_bp.get("/reports/performance")
@roles("admin", "teacher")
def performance_report():
    user = current_user()
    assigned_courses = user.teacher.courses if user.role == "teacher" and user.teacher else []
    course_ids = [course.id for course in assigned_courses]
    results_query = AcademicResult.query
    if user.role == "teacher":
        results_query = results_query.filter(AcademicResult.course_id.in_(course_ids))
    results = results_query.order_by(AcademicResult.recorded_at).all()
    scores_by_month: dict[str, list[float]] = defaultdict(list)
    course_scores_by_month: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    labels: dict[str, date] = {}
    for result in results:
        key = _month_key(result.recorded_at)
        labels[key] = result.recorded_at
        percentage = float(result.score) * 100 / float(result.max_score)
        scores_by_month[key].append(percentage)
        course_scores_by_month[key][result.course_id].append(percentage)
    monthly_scores = [
        {
            "month": _month_label(labels[key]),
            "score": round(sum(values) / len(values), 2),
            "average": round(
                sum(sum(course_values) / len(course_values) for course_values in course_scores_by_month[key].values())
                / len(course_scores_by_month[key]),
                2,
            ),
            "period": key,
        }
        for key, values in sorted(scores_by_month.items())
    ]

    attendance_by_course = []
    courses = (
        Course.query.filter(Course.id.in_(course_ids)).order_by(Course.name).all()
        if user.role == "teacher"
        else Course.query.order_by(Course.name).all()
    )
    for course in courses:
        students = Student.query.filter(func.lower(Student.course_name) == course.name.lower()).all()
        if not students:
            students = [enrollment.student for enrollment in course.enrollments]
        if not students:
            continue
        attendance_by_course.append(
            {
                "course": course.name,
                "attendance": round(sum(student_attendance(student) for student in students) / len(students)),
            }
        )

    current = _start_of_month(date.today())
    months = []
    for _ in range(5, -1, -1):
        months.append(current)
        current = _previous_month(current)
    enrollment_trends = []
    for month in months:
        next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
        enrollment_query = Enrollment.query.filter(
            Enrollment.enrolled_at >= month,
            Enrollment.enrolled_at < next_month,
        )
        if user.role == "teacher":
            enrollment_query = enrollment_query.filter(Enrollment.course_id.in_(course_ids))
        enrollment_count = enrollment_query.count()
        graduate_query = Student.query.filter(
            Student.status == "Graduated",
            Student.graduation_date >= month,
            Student.graduation_date < next_month,
        )
        if user.role == "teacher":
            course_names = [course.name for course in assigned_courses]
            graduate_query = graduate_query.filter(Student.course_name.in_(course_names))
        graduates = graduate_query.count()
        enrollment_trends.append(
            {
                "month": _month_label(month),
                "period": _month_key(month),
                "enrollment": enrollment_count,
                "graduates": graduates,
            }
        )
    return {
        "monthly_scores": monthly_scores,
        "attendance_by_course": attendance_by_course,
        "enrollment_trends": enrollment_trends,
    }


@reports_bp.get("/reports/attendance")
@roles("admin", "teacher")
def attendance_report():
    start = date_value(request.args.get("start"), "Start date") if request.args.get("start") else date.today().replace(day=1)
    end = date_value(request.args.get("end"), "End date") if request.args.get("end") else date.today()
    if start > end:
        from backend.app.validation import ApiError

        raise ApiError("Start date must be on or before end date.")
    query = (
        db.session.query(
            Attendance.student_id,
            Student.name,
            Student.course_name,
            func.count(Attendance.id).label("days_marked"),
            func.sum(case((Attendance.status.in_(("Present", "Late")), 1), else_=0)).label("days_attended"),
        )
        .join(Student, Attendance.student_id == Student.id)
        .filter(Attendance.date.between(start, end))
    )
    user = current_user()
    if user.role == "teacher":
        names = [course.name for course in (user.teacher.courses if user.teacher else [])]
        query = query.filter(Student.course_name.in_(names))
    rows = (
        query
        .group_by(Attendance.student_id, Student.name, Student.course_name)
        .order_by(Student.name)
        .all()
    )
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "students": [
            {
                "student_id": row.student_id,
                "student_name": row.name,
                "days_marked": row.days_marked,
                "days_attended": int(row.days_attended or 0),
                "attendance_percent": round(int(row.days_attended or 0) * 100 / row.days_marked) if row.days_marked else 0,
            }
            for row in rows
        ],
    }


@reports_bp.get("/reports/academic")
@roles("admin", "teacher")
def academic_report():
    query = AcademicResult.query
    user = current_user()
    if user.role == "teacher":
        course_ids = [course.id for course in (user.teacher.courses if user.teacher else [])]
        query = query.filter(AcademicResult.course_id.in_(course_ids))
    results = query.order_by(AcademicResult.recorded_at.desc()).all()
    return {"results": [serialize_result(result) for result in results]}


@reports_bp.get("/reports/fees")
@roles("admin")
def fee_report():
    accounts = FeeAccount.query.order_by(FeeAccount.student_id, FeeAccount.period).all()
    report_rows = []
    for account in accounts:
        paid = sum(float(payment.amount) for payment in account.payments)
        billed = float(account.total_due)
        report_rows.append(
            {
                "student_id": account.student_id,
                "student_name": account.student.name,
                "period": account.period,
                "billed": billed,
                "paid": paid,
                "balance": max(0, billed - paid),
                "status": "Paid" if paid >= billed else "Partial" if paid else "Unpaid",
            }
        )
    return {"accounts": report_rows}
