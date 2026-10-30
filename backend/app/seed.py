from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from backend.app.extensions import db
from backend.app.models import (
    AcademicResult,
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


def seed_demo(password: str) -> int:
    if User.query.first() or Student.query.first() or Teacher.query.first() or Course.query.first():
        raise RuntimeError("Demo seeding requires an empty database.")
    departments = {
        name: Department(name=name)
        for name in ("Computer Science", "Business", "Design")
    }
    db.session.add_all(departments.values())
    db.session.flush()

    teachers = [
        Teacher(id="TCH-1021", name="Dr. Alex Morgan", email="alex.morgan@campus.edu", phone="+1 555 010 1021", department=departments["Computer Science"], subject="Data Structures", experience="8 years"),
        Teacher(id="TCH-1022", name="Sofia Chen", email="sofia.chen@campus.edu", phone="+1 555 010 1022", department=departments["Business"], subject="Business Strategy", experience="6 years"),
        Teacher(id="TCH-1023", name="Ethan Brooks", email="ethan.brooks@campus.edu", phone="+1 555 010 1023", department=departments["Design"], subject="Visual Communication", experience="5 years"),
        Teacher(id="TCH-1024", name="Maya Patel", email="maya.patel@campus.edu", phone="+1 555 010 1024", department=departments["Computer Science"], subject="Web Development", experience="4 years"),
    ]
    courses = [
        Course(id="CRS-101", name="B.Sc. Computer Science", department=departments["Computer Science"], teacher=teachers[0], capacity=160, duration="3 years"),
        Course(id="CRS-102", name="BBA", department=departments["Business"], teacher=teachers[1], capacity=120, duration="3 years"),
        Course(id="CRS-103", name="B.Des. Visual Design", department=departments["Design"], teacher=teachers[2], capacity=100, duration="4 years"),
        Course(id="CRS-104", name="B.Sc. Data Analytics", department=departments["Computer Science"], teacher=teachers[3], capacity=100, duration="3 years"),
        Course(id="CRS-105", name="MBA", department=departments["Business"], teacher=teachers[1], capacity=80, duration="2 years"),
    ]
    students = [
        Student(id="STU-2401", name="Olivia Rhye", email="olivia.rhye@campus.edu", phone="+1 555 013 2041", department=departments["Computer Science"], course_name="B.Sc. Computer Science", year="Year 2"),
        Student(id="STU-2402", name="Phoenix Baker", email="phoenix.baker@campus.edu", phone="+1 555 013 2042", department=departments["Business"], course_name="BBA", year="Year 3"),
        Student(id="STU-2403", name="Lana Steiner", email="lana.steiner@campus.edu", phone="+1 555 013 2043", department=departments["Design"], course_name="B.Des. Visual Design", year="Year 1"),
        Student(id="STU-2404", name="Demi Wilkinson", email="demi.wilkinson@campus.edu", phone="+1 555 013 2044", department=departments["Computer Science"], course_name="B.Sc. Computer Science", year="Year 2"),
        Student(id="STU-2405", name="Candice Wu", email="candice.wu@campus.edu", phone="+1 555 013 2045", department=departments["Business"], course_name="BBA", year="Year 1"),
        Student(id="STU-2406", name="Natali Craig", email="natali.craig@campus.edu", phone="+1 555 013 2046", department=departments["Design"], course_name="B.Des. Visual Design", year="Year 3"),
    ]
    db.session.add_all(teachers + courses + students)
    db.session.flush()

    admin = User(email="admin@campus.edu", role="admin")
    admin.set_password(password)
    teacher_users = []
    for teacher in teachers:
        user = User(email=teacher.email, role="teacher", teacher_id=teacher.id)
        user.set_password(password)
        teacher_users.append(user)
    student_users = []
    for student in students:
        user = User(email=student.email, role="student", student_id=student.id)
        user.set_password(password)
        student_users.append(user)
    db.session.add_all([admin, *teacher_users, *student_users])

    now = date.today()
    attendance_statuses = {
        "STU-2401": "Present",
        "STU-2402": "Present",
        "STU-2403": "Late",
        "STU-2404": "Absent",
        "STU-2405": "Present",
        "STU-2406": "Present",
    }
    enrollments = []
    attendance = []
    fee_accounts = []
    academic_results = []
    for student in students:
        course = next(course for course in courses if course.name == student.course_name)
        enrollments.append(Enrollment(student=student, course=course, enrolled_at=now - timedelta(days=30)))
        for days_ago in range(4, -1, -1):
            marked_date = now - timedelta(days=days_ago)
            weekday_status = "Present" if marked_date.weekday() < 5 else "Absent"
            status = attendance_statuses[student.id] if days_ago == 0 else weekday_status
            attendance.append(Attendance(student=student, date=marked_date, status=status, marked_by=admin.id))
        total = {
            "STU-2401": Decimal("18500.00"),
            "STU-2402": Decimal("16200.00"),
            "STU-2403": Decimal("14800.00"),
            "STU-2404": Decimal("18500.00"),
            "STU-2405": Decimal("16200.00"),
            "STU-2406": Decimal("14800.00"),
        }[student.id]
        paid = {
            "STU-2401": Decimal("18500.00"),
            "STU-2402": Decimal("12200.00"),
            "STU-2403": Decimal("14800.00"),
            "STU-2404": Decimal("10000.00"),
            "STU-2405": Decimal("16200.00"),
            "STU-2406": Decimal("7800.00"),
        }[student.id]
        account = FeeAccount(student=student, period=str(now.year), total_due=total)
        fee_accounts.append(account)
        if paid:
            account.payments.append(Payment(amount=paid, method="Seeded ledger", paid_at=datetime.now(timezone.utc)))
        academic_results.append(
            AcademicResult(
                student=student,
                course=course,
                term="Fall semester",
                assessment="Midterm assessment",
                score=Decimal("78.00") + Decimal(str(students.index(student) * 2)),
                max_score=Decimal("100.00"),
                recorded_at=now,
            )
        )
    db.session.add_all(enrollments + attendance + fee_accounts + academic_results)
    db.session.flush()
    for record in attendance:
        record.marked_by = admin.id
    return 1 + len(teachers) + len(courses) + len(students) + len(enrollments) + len(attendance) + len(fee_accounts) + len(academic_results)
