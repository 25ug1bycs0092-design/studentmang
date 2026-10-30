from datetime import date

from flask import Blueprint, jsonify, request

from backend.app.controllers.attendance import attendance_for_date, mark_attendance
from backend.app.extensions import db
from backend.app.security import current_user, roles
from backend.app.serializers import serialize_attendance
from backend.app.validation import date_value, json_object

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.get("/attendance")
@roles("admin", "teacher", "student")
def get_attendance():
    selected_date = date_value(request.args.get("date", date.today().isoformat()))
    return jsonify([serialize_attendance(record) for record in attendance_for_date(selected_date)])


@attendance_bp.post("/attendance")
@roles("admin", "teacher")
def save_attendance():
    records = mark_attendance(json_object(), current_user().id)
    db.session.commit()
    return jsonify([serialize_attendance(record) for record in records])
