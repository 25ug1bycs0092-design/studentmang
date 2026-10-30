import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from werkzeug.exceptions import BadRequest

from flask import request

from backend.app.extensions import db
from backend.app.models import Department

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ATTENDANCE_STATUSES = {"Present", "Absent", "Late"}
ACTIVE_STATUSES = {"Active", "Inactive"}


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def json_object() -> dict[str, Any]:
    if not request.is_json:
        raise ApiError("Request body must be application/json.", 415)
    try:
        value = request.get_json(silent=False)
    except BadRequest:
        raise ApiError("Request body must contain valid JSON.") from None
    if not isinstance(value, dict):
        raise ApiError("JSON request body must be an object.")
    return value


def required_text(data: dict[str, Any], key: str, label: str | None = None, limit: int = 160) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ApiError(f"{label or key.replace('_', ' ').title()} is required.")
    value = value.strip()
    if len(value) > limit:
        raise ApiError(f"{label or key.replace('_', ' ').title()} must be {limit} characters or fewer.")
    return value


def optional_text(data: dict[str, Any], key: str, limit: int = 160) -> str | None:
    value = data.get(key)
    if value in (None, ""):
        return None
    if not isinstance(value, str) or len(value.strip()) > limit:
        raise ApiError(f"{key.replace('_', ' ').title()} must be {limit} characters or fewer.")
    return value.strip() or None


def email_value(data: dict[str, Any], key: str = "email") -> str:
    value = required_text(data, key, "Email address", 254).lower()
    if not EMAIL_RE.fullmatch(value):
        raise ApiError("A valid email address is required.")
    return value


def integer_value(value: Any, label: str, minimum: int = 0, maximum: int = 1000000) -> int:
    if isinstance(value, bool):
        raise ApiError(f"{label} must be an integer.")
    try:
        result = int(value)
    except (TypeError, ValueError):
        raise ApiError(f"{label} must be an integer.") from None
    if str(value).strip() not in (str(result), f"{result}.0"):
        raise ApiError(f"{label} must be an integer.")
    if not minimum <= result <= maximum:
        raise ApiError(f"{label} must be between {minimum} and {maximum}.")
    return result


def decimal_value(value: Any, label: str, minimum: Decimal = Decimal("0")) -> Decimal:
    if isinstance(value, bool):
        raise ApiError(f"{label} must be a valid amount.")
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ApiError(f"{label} must be a valid amount.") from None
    if not amount.is_finite() or amount < minimum:
        raise ApiError(f"{label} must be at least {minimum}.")
    return amount


def date_value(value: Any, label: str = "Date", default_today: bool = False) -> date:
    if value is None and default_today:
        return date.today()
    if not isinstance(value, str):
        raise ApiError(f"{label} must use YYYY-MM-DD format.")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ApiError(f"{label} must use YYYY-MM-DD format.") from None


def status_value(value: Any, allowed: set[str], label: str = "Status") -> str:
    if value not in allowed:
        options = ", ".join(sorted(allowed))
        raise ApiError(f"{label} must be one of: {options}.")
    return value


def department_for(value: Any) -> Department | None:
    if value in (None, ""):
        return None
    name = required_text({"department": value}, "department", "Department", 100)
    department = Department.query.filter(db.func.lower(Department.name) == name.lower()).first()
    if department is None:
        department = Department(name=name)
        db.session.add(department)
        db.session.flush()
    return department


def pagination() -> tuple[int, int]:
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 100))
    except ValueError:
        raise ApiError("page and per_page must be integers.") from None
    if page < 1 or per_page < 1 or per_page > 200:
        raise ApiError("page must be positive and per_page must be between 1 and 200.")
    return page, per_page
