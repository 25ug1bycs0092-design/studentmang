from datetime import date
from decimal import Decimal

from sqlalchemy import func

from backend.app.extensions import db
from backend.app.models import FeeAccount, Payment, Student
from backend.app.validation import ApiError, decimal_value, optional_text, required_text


def record_payment(student_id: str, data: dict, received_by: int) -> Payment:
    student = db.session.get(Student, student_id)
    if student is None:
        raise ApiError("Student was not found.", 404)
    amount = decimal_value(data.get("amount"), "Payment amount", minimum=Decimal("0.01"))
    period = optional_text(data, "period", 40) or str(date.today().year)
    account = FeeAccount.query.filter_by(student_id=student.id, period=period).with_for_update().first()
    if account is None:
        if data.get("total_due") in (None, ""):
            raise ApiError("No fee account exists for this period. Create one before recording a payment.", 404)
        from backend.app.validation import date_value

        due_date = date_value(data["due_date"], "Due date") if data.get("due_date") else None
        account = FeeAccount(
            student=student,
            period=period,
            total_due=decimal_value(data["total_due"], "Total fee"),
            due_date=due_date,
        )
        db.session.add(account)
        db.session.flush()
    paid = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.fee_account_id == account.id)
        .scalar()
    )
    if Decimal(str(paid)) + amount > Decimal(account.total_due):
        raise ApiError("Payment exceeds the outstanding fee balance.")
    payment = Payment(
        account=account,
        amount=amount,
        method=optional_text(data, "method", 40) or "Other",
        reference=optional_text(data, "reference", 100),
        received_by=received_by,
    )
    db.session.add(payment)
    return payment


def create_fee_account(student_id: str, data: dict) -> FeeAccount:
    student = db.session.get(Student, student_id)
    if student is None:
        raise ApiError("Student was not found.", 404)
    period = required_text(data, "period", "Fee period", 40)
    if FeeAccount.query.filter_by(student_id=student_id, period=period).first():
        raise ApiError("A fee account already exists for this student and period.", 409)
    from backend.app.validation import date_value

    account = FeeAccount(
        student=student,
        period=period,
        total_due=decimal_value(data.get("total_due"), "Total fee"),
        due_date=date_value(data["due_date"], "Due date") if data.get("due_date") else None,
    )
    db.session.add(account)
    return account
