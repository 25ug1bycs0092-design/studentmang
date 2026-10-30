from datetime import date, datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from backend.app.extensions import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(40))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id", ondelete="SET NULL"))
    course_name = db.Column(db.String(160), nullable=False)
    year = db.Column(db.String(40))
    status = db.Column(db.String(20), nullable=False, default="Active")
    graduation_date = db.Column(db.Date)
    department = db.relationship(Department)
    attendance_records = db.relationship(
        "Attendance", back_populates="student", cascade="all, delete-orphan"
    )
    fee_accounts = db.relationship(
        "FeeAccount", back_populates="student", cascade="all, delete-orphan"
    )
    enrollments = db.relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )
    academic_results = db.relationship(
        "AcademicResult", back_populates="student", cascade="all, delete-orphan"
    )


class Teacher(db.Model):
    __tablename__ = "teachers"

    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(40))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id", ondelete="SET NULL"))
    subject = db.Column(db.String(160), nullable=False)
    experience = db.Column(db.String(80))
    status = db.Column(db.String(20), nullable=False, default="Active")
    department = db.relationship(Department)
    courses = db.relationship("Course", back_populates="teacher")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)
    student_id = db.Column(db.String(40), db.ForeignKey("students.id", ondelete="CASCADE"), unique=True)
    teacher_id = db.Column(db.String(40), db.ForeignKey("teachers.id", ondelete="CASCADE"), unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    student = db.relationship(Student)
    teacher = db.relationship(Teacher)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self) -> str:
        if self.student:
            return self.student.name
        if self.teacher:
            return self.teacher.name
        return self.email.split("@", maxsplit=1)[0].replace(".", " ").title()


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id", ondelete="SET NULL"))
    teacher_id = db.Column(db.String(40), db.ForeignKey("teachers.id", ondelete="SET NULL"))
    capacity = db.Column(db.Integer, nullable=False, default=100)
    duration = db.Column(db.String(80))
    status = db.Column(db.String(20), nullable=False, default="Active")
    department = db.relationship(Department)
    teacher = db.relationship(Teacher, back_populates="courses")
    enrollments = db.relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )
    academic_results = db.relationship(
        "AcademicResult", back_populates="course", cascade="all, delete-orphan"
    )


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(40), db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.String(40), db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = db.Column(db.Date, nullable=False, default=date.today)
    student = db.relationship(Student, back_populates="enrollments")
    course = db.relationship(Course, back_populates="enrollments")


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (
        db.UniqueConstraint("student_id", "date", name="uq_attendance_student_date"),
        db.CheckConstraint("status IN ('Present', 'Absent', 'Late')", name="ck_attendance_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(40), db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(12), nullable=False)
    marked_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    student = db.relationship(Student, back_populates="attendance_records")


class FeeAccount(db.Model):
    __tablename__ = "fee_accounts"
    __table_args__ = (
        db.UniqueConstraint("student_id", "period", name="uq_fee_student_period"),
        db.CheckConstraint("total_due >= 0", name="ck_fee_total_nonnegative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(40), db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    period = db.Column(db.String(40), nullable=False)
    total_due = db.Column(db.Numeric(12, 2), nullable=False)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    student = db.relationship(Student, back_populates="fee_accounts")
    payments = db.relationship("Payment", back_populates="account", cascade="all, delete-orphan")


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    fee_account_id = db.Column(db.Integer, db.ForeignKey("fee_accounts.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    method = db.Column(db.String(40), nullable=False, default="Other")
    reference = db.Column(db.String(100), unique=True)
    paid_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    received_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    account = db.relationship(FeeAccount, back_populates="payments")


class AcademicResult(db.Model):
    __tablename__ = "academic_results"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(40), db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = db.Column(db.String(40), db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    term = db.Column(db.String(80), nullable=False)
    assessment = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Numeric(7, 2), nullable=False)
    max_score = db.Column(db.Numeric(7, 2), nullable=False, default=100)
    recorded_at = db.Column(db.Date, nullable=False, default=date.today, index=True)
    student = db.relationship(Student, back_populates="academic_results")
    course = db.relationship(Course, back_populates="academic_results")
