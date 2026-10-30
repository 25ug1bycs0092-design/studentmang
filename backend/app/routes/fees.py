from flask import Blueprint, jsonify, request

from backend.app.controllers.finance import create_fee_account, record_payment
from backend.app.extensions import db
from backend.app.models import FeeAccount, Student
from backend.app.security import current_user, require_student_access, roles
from backend.app.serializers import serialize_fee_account, serialize_payment
from backend.app.validation import ApiError, json_object

fees_bp = Blueprint("fees", __name__)


@fees_bp.get("/fees")
@roles("admin", "student")
def list_fees():
    query = FeeAccount.query
    student_id = request.args.get("student_id")
    if current_user().role == "student":
        student_id = current_user().student_id
    if student_id:
        require_student_access(student_id)
        query = query.filter_by(student_id=student_id)
    return jsonify([serialize_fee_account(account) for account in query.order_by(FeeAccount.period.desc()).all()])


@fees_bp.post("/fees/accounts")
@roles("admin")
def add_fee_account():
    data = json_object()
    student_id = data.get("student_id")
    if not isinstance(student_id, str) or not student_id:
        raise ApiError("Student ID is required.")
    account = create_fee_account(student_id, data)
    db.session.commit()
    return jsonify(serialize_fee_account(account)), 201


@fees_bp.get("/fees/<string:student_id>")
@roles("admin", "student")
def student_fees(student_id: str):
    require_student_access(student_id)
    if db.session.get(Student, student_id) is None:
        raise ApiError("Student was not found.", 404)
    accounts = FeeAccount.query.filter_by(student_id=student_id).order_by(FeeAccount.period.desc()).all()
    return jsonify([serialize_fee_account(account) for account in accounts])


@fees_bp.post("/fees/<string:student_id>")
@roles("admin")
def add_payment(student_id: str):
    payment = record_payment(student_id, json_object(), current_user().id)
    db.session.commit()
    return jsonify(serialize_payment(payment)), 201
