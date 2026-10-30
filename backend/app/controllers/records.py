import secrets
from datetime import date
from decimal import Decimal

from sqlalchemy import or_

from backend.app.extensions import db
from backend.app.models import (
    Attendance,
    Course,
    Department,
    Enrollment,
    FeeAccount,
    Payment,
    Student,
    Teacher,
    User,
)
from backend.app.validation import (
    ACTIVE_STATUSES,
    ApiError,
    decimal_value,
    department_for,
    email_value,
    integer_value,
    optional_text,
    required_text,
    status_value,
)


def _new_id(prefix: str, model) -> str:
    while True:
        candidate = f"{prefix}-{secrets.token_hex(4).upper()}"
        if db.session.get(model, candidate) is None:
            return candidate


def requested_term() -> str:
    from flask import request

    return request.args.get("q", "").strip()


def list_students():
    from flask import request

    query = Student.query
    term = requested_term()
    if term:
        pattern = f"%{term}%"
        query = query.filter(or_(Student.id.ilike(pattern), Student.name.ilike(pattern), Student.email.ilike(pattern), Student.course_name.ilike(pattern)))
    department = request.args.get("department")
    if department:
        query = query.join(Student.department).filter(db.func.lower(Department.name) == department.lower())
    course = request.args.get("course")
    if course:
        query = query.filter(Student.course_name.ilike(f"%{course}%"))
    status = request.args.get("status")
    if status:
        query = query.filter(Student.status == status)
    return query.order_by(Student.name).all()


def create_student(data: dict) -> Student:
    student_id = optional_text(data, "id", 40) or _new_id("STU", Student)
    if db.session.get(Student, student_id):
        raise ApiError("A student with this ID already exists.", 409)
    email = email_value(data)
    if (
        Student.query.filter_by(email=email).first()
        or Teacher.query.filter_by(email=email).first()
        or User.query.filter_by(email=email).first()
    ):
        raise ApiError("An account with this email already exists.", 409)
    course_name = required_text(data, "course", "Course", 160)
    student = Student(
        id=student_id,
        name=required_text(data, "name"),
        email=email,
        phone=optional_text(data, "phone", 40),
        department=department_for(data.get("department")),
        course_name=course_name,
        year=optional_text(data, "year", 40),
        status=status_value(data.get("status", "Active"), ACTIVE_STATUSES | {"Graduated"}),
    )
    db.session.add(student)
    db.session.flush()
    _sync_course_enrollment(student)
    if data.get("fee") not in (None, ""):
        total = decimal_value(data["fee"], "Fee")
        account = FeeAccount(student=student, period=str(date.today().year), total_due=total)
        db.session.add(account)
        initial_paid = decimal_value(data.get("paid", 0), "Amount paid")
        if initial_paid > total:
            raise ApiError("Amount paid cannot exceed the fee total.")
        if initial_paid:
            db.session.add(Payment(account=account, amount=initial_paid, method="Opening balance"))
    _create_linked_user("student", student_id, student.email, data.get("password"))
    return student


def update_student(student: Student, data: dict) -> Student:
    if "name" in data:
        student.name = required_text(data, "name")
    if "email" in data:
        new_email = email_value(data)
        if new_email != student.email and (
            Student.query.filter_by(email=new_email).first()
            or Teacher.query.filter_by(email=new_email).first()
            or User.query.filter_by(email=new_email).first()
        ):
            raise ApiError("An account with this email already exists.", 409)
        student.email = new_email
    if "phone" in data:
        student.phone = optional_text(data, "phone", 40)
    if "department" in data:
        student.department = department_for(data["department"])
    if "course" in data:
        student.course_name = required_text(data, "course", "Course", 160)
        _sync_course_enrollment(student)
    if "year" in data:
        student.year = optional_text(data, "year", 40)
    if "status" in data:
        student.status = status_value(data["status"], ACTIVE_STATUSES | {"Graduated"})
        if student.status == "Graduated":
            from backend.app.validation import date_value

            student.graduation_date = date_value(data["graduation_date"], "Graduation date") if data.get("graduation_date") else date.today()
    linked_user = User.query.filter_by(student_id=student.id).first()
    if linked_user:
        linked_user.email = student.email
        if data.get("password"):
            linked_user.set_password(_validated_password(data["password"]))
    return student


def list_teachers():
    from flask import request

    query = Teacher.query
    term = requested_term()
    if term:
        pattern = f"%{term}%"
        query = query.filter(or_(Teacher.id.ilike(pattern), Teacher.name.ilike(pattern), Teacher.email.ilike(pattern), Teacher.subject.ilike(pattern)))
    if request.args.get("department"):
        query = query.join(Teacher.department).filter(db.func.lower(Department.name) == request.args["department"].lower())
    if request.args.get("status"):
        query = query.filter(Teacher.status == request.args["status"])
    return query.order_by(Teacher.name).all()


def create_teacher(data: dict) -> Teacher:
    teacher_id = optional_text(data, "id", 40) or _new_id("TCH", Teacher)
    if db.session.get(Teacher, teacher_id):
        raise ApiError("A teacher with this ID already exists.", 409)
    email = email_value(data)
    if (
        Teacher.query.filter_by(email=email).first()
        or Student.query.filter_by(email=email).first()
        or User.query.filter_by(email=email).first()
    ):
        raise ApiError("An account with this email already exists.", 409)
    teacher = Teacher(
        id=teacher_id,
        name=required_text(data, "name"),
        email=email,
        phone=optional_text(data, "phone", 40),
        department=department_for(data.get("department")),
        subject=required_text(data, "subject", "Assigned subject"),
        experience=optional_text(data, "experience", 80),
        status=status_value(data.get("status", "Active"), ACTIVE_STATUSES),
    )
    db.session.add(teacher)
    db.session.flush()
    _create_linked_user("teacher", teacher_id, teacher.email, data.get("password"))
    return teacher


def update_teacher(teacher: Teacher, data: dict) -> Teacher:
    if "name" in data:
        teacher.name = required_text(data, "name")
    if "email" in data:
        new_email = email_value(data)
        if new_email != teacher.email and (
            Teacher.query.filter_by(email=new_email).first()
            or Student.query.filter_by(email=new_email).first()
            or User.query.filter_by(email=new_email).first()
        ):
            raise ApiError("An account with this email already exists.", 409)
        teacher.email = new_email
    if "phone" in data:
        teacher.phone = optional_text(data, "phone", 40)
    if "department" in data:
        teacher.department = department_for(data["department"])
    if "subject" in data:
        teacher.subject = required_text(data, "subject", "Assigned subject")
    if "experience" in data:
        teacher.experience = optional_text(data, "experience", 80)
    if "status" in data:
        teacher.status = status_value(data["status"], ACTIVE_STATUSES)
    linked_user = User.query.filter_by(teacher_id=teacher.id).first()
    if linked_user:
        linked_user.email = teacher.email
        if data.get("password"):
            linked_user.set_password(_validated_password(data["password"]))
    return teacher


def list_courses():
    from flask import request

    query = Course.query
    term = requested_term()
    if term:
        pattern = f"%{term}%"
        query = query.filter(or_(Course.id.ilike(pattern), Course.name.ilike(pattern)))
    if request.args.get("department"):
        query = query.join(Course.department).filter(db.func.lower(Department.name) == request.args["department"].lower())
    if request.args.get("status"):
        query = query.filter(Course.status == request.args["status"])
    return query.order_by(Course.name).all()


def create_course(data: dict) -> Course:
    course_id = optional_text(data, "id", 40) or _new_id("CRS", Course)
    if db.session.get(Course, course_id):
        raise ApiError("A course with this ID already exists.", 409)
    teacher = _teacher_from_value(data.get("teacher") or data.get("teacher_id"))
    return Course(
        id=course_id,
        name=required_text(data, "name", "Course name"),
        department=department_for(data.get("department")),
        teacher=teacher,
        capacity=integer_value(data.get("capacity", 100), "Capacity", minimum=1),
        duration=optional_text(data, "duration", 80),
        status=status_value(data.get("status", "Active"), ACTIVE_STATUSES),
    )


def update_course(course: Course, data: dict) -> Course:
    if "name" in data:
        course.name = required_text(data, "name", "Course name")
    if "department" in data:
        course.department = department_for(data["department"])
    if "teacher" in data or "teacher_id" in data:
        course.teacher = _teacher_from_value(data.get("teacher") or data.get("teacher_id"))
    if "capacity" in data:
        course.capacity = integer_value(data["capacity"], "Capacity", minimum=1)
    if "duration" in data:
        course.duration = optional_text(data, "duration", 80)
    if "status" in data:
        course.status = status_value(data["status"], ACTIVE_STATUSES)
    return course


def _teacher_from_value(value) -> Teacher | None:
    if value in (None, ""):
        return None
    teacher = db.session.get(Teacher, str(value))
    if teacher is None:
        teacher = Teacher.query.filter_by(name=value).first()
    if teacher is None:
        raise ApiError("Assigned teacher was not found.", 404)
    return teacher


def _sync_course_enrollment(student: Student) -> None:
    course = Course.query.filter(db.func.lower(Course.name) == student.course_name.lower()).first()
    if course is None:
        return
    if Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first():
        return
    if Enrollment.query.filter_by(course_id=course.id).count() >= course.capacity:
        raise ApiError("The selected course has reached its enrollment capacity.", 409)
    db.session.add(Enrollment(student_id=student.id, course_id=course.id))


def _validated_password(value) -> str:
    if not isinstance(value, str) or len(value) < 10 or len(value) > 256:
        raise ApiError("Passwords must be between 10 and 256 characters.")
    return value


def _create_linked_user(role: str, record_id: str, email: str, password) -> User | None:
    if password in (None, ""):
        return None
    user = User(email=email, role=role)
    user.set_password(_validated_password(password))
    if role == "student":
        user.student_id = record_id
    else:
        user.teacher_id = record_id
    db.session.add(user)
    return user


def create_user_account(data: dict) -> User:
    role = data.get("role")
    if role not in {"teacher", "student"}:
        raise ApiError("New accounts must have the teacher or student role.")
    email = email_value(data)
    if User.query.filter_by(email=email).first():
        raise ApiError("An account with this email already exists.", 409)
    password = _validated_password(data.get("password"))
    user = User(email=email, role=role)
    user.set_password(password)
    if role == "student":
        student_id = required_text(data, "student_id", "Student ID", 40)
        student = db.session.get(Student, student_id)
        if student is None or student.email != email:
            raise ApiError("The student ID and email must match an existing student record.", 404)
        if User.query.filter_by(student_id=student_id).first():
            raise ApiError("This student already has a login account.", 409)
        user.student_id = student_id
    else:
        teacher_id = required_text(data, "teacher_id", "Teacher ID", 40)
        teacher = db.session.get(Teacher, teacher_id)
        if teacher is None or teacher.email != email:
            raise ApiError("The teacher ID and email must match an existing teacher record.", 404)
        if User.query.filter_by(teacher_id=teacher_id).first():
            raise ApiError("This teacher already has a login account.", 409)
        user.teacher_id = teacher_id
    db.session.add(user)
    return user
