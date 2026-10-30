from decimal import Decimal

from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models import (
    AcademicResult,
    Attendance,
    Course,
    Enrollment,
    FeeAccount,
    Payment,
    Student,
    Teacher,
)


def department_name(record) -> str:
    return record.department.name if record.department else ""


def student_attendance(student: Student) -> int:
    total = Attendance.query.filter_by(student_id=student.id).count()
    if total == 0:
        return 0
    attended = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.status.in_(("Present", "Late")),
    ).count()
    return round(attended * 100 / total)


def student_fees(student: Student) -> tuple[Decimal, Decimal]:
    total = db.session.query(func.coalesce(func.sum(FeeAccount.total_due), 0)).filter_by(
        student_id=student.id
    ).scalar()
    paid = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .join(FeeAccount, Payment.fee_account_id == FeeAccount.id)
        .filter(FeeAccount.student_id == student.id)
        .scalar()
    )
    return Decimal(str(total)), Decimal(str(paid))


def serialize_student(student: Student, include_financials: bool = True) -> dict:
    record = {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "phone": student.phone or "",
        "department": department_name(student),
        "course": student.course_name,
        "year": student.year or "",
        "status": student.status,
        "graduation_date": student.graduation_date.isoformat() if student.graduation_date else None,
        "attendance": student_attendance(student),
        "initials": "".join(part[0] for part in student.name.split()[:2]).upper(),
    }
    if include_financials:
        fee, paid = student_fees(student)
        record.update({"fee": float(fee), "paid": float(paid)})
    return record


def serialize_teacher(teacher: Teacher) -> dict:
    return {
        "id": teacher.id,
        "name": teacher.name,
        "email": teacher.email,
        "phone": teacher.phone or "",
        "department": department_name(teacher),
        "subject": teacher.subject,
        "experience": teacher.experience or "",
        "status": teacher.status,
        "initials": "".join(part[0] for part in teacher.name.split()[:2]).upper(),
    }


def serialize_course(course: Course) -> dict:
    enrolled = Enrollment.query.filter_by(course_id=course.id).count()
    return {
        "id": course.id,
        "name": course.name,
        "department": department_name(course),
        "teacher": course.teacher.name if course.teacher else "",
        "teacher_id": course.teacher_id,
        "students": enrolled,
        "capacity": course.capacity,
        "duration": course.duration or "",
        "status": course.status,
        "symbol": "".join(part[0] for part in course.name.split()[:2]).upper(),
    }


def serialize_attendance(record: Attendance) -> dict:
    return {
        "id": record.id,
        "student_id": record.student_id,
        "student_name": record.student.name,
        "date": record.date.isoformat(),
        "status": record.status,
    }


def serialize_fee_account(account: FeeAccount) -> dict:
    paid = sum((Decimal(payment.amount) for payment in account.payments), Decimal("0.00"))
    due = Decimal(account.total_due)
    return {
        "id": account.id,
        "student_id": account.student_id,
        "student_name": account.student.name,
        "period": account.period,
        "total_due": float(due),
        "paid": float(paid),
        "balance": float(max(Decimal("0.00"), due - paid)),
        "due_date": account.due_date.isoformat() if account.due_date else None,
        "status": "Paid" if paid >= due else "Partial" if paid > 0 else "Unpaid",
        "payments": [serialize_payment(payment) for payment in account.payments],
    }


def serialize_payment(payment: Payment) -> dict:
    return {
        "id": payment.id,
        "fee_account_id": payment.fee_account_id,
        "amount": float(payment.amount),
        "method": payment.method,
        "reference": payment.reference,
        "paid_at": payment.paid_at.isoformat(),
    }


def serialize_result(result: AcademicResult) -> dict:
    return {
        "id": result.id,
        "student_id": result.student_id,
        "student_name": result.student.name,
        "course_id": result.course_id,
        "course": result.course.name,
        "term": result.term,
        "assessment": result.assessment,
        "score": float(result.score),
        "max_score": float(result.max_score),
        "percentage": round(float(result.score) * 100 / float(result.max_score), 2),
        "recorded_at": result.recorded_at.isoformat(),
    }
