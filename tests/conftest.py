import pytest

from backend.app import create_app
from backend.app.extensions import db


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "JWT_ACCESS_TOKEN_EXPIRES": False,
            "CORS_ORIGINS": ["http://localhost:5000"],
        }
    )
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_token(client, seeded_records):
    response = client.post(
        "/api/auth/login",
        json={"role": "admin", "identity": "admin@campus.edu", "password": "admin123456"},
    )
    assert response.status_code == 200
    return response.json["token"]


@pytest.fixture()
def seeded_records(app):
    from backend.app.models import Course, Department, Student, Teacher, User

    with app.app_context():
        department = Department(name="Computer Science")
        db.session.add(department)
        db.session.flush()
        teacher = Teacher(
            id="TCH-1",
            name="Teacher One",
            email="teacher@example.edu",
            department=department,
            subject="Databases",
        )
        course = Course(
            id="CRS-1",
            name="B.Sc. Computer Science",
            department=department,
            teacher=teacher,
            capacity=30,
            duration="3 years",
        )
        student = Student(
            id="STU-1",
            name="Student One",
            email="student@example.edu",
            department=department,
            course_name=course.name,
            year="Year 1",
        )
        db.session.add_all([teacher, course, student])
        db.session.flush()
        admin = User(email="admin@campus.edu", role="admin")
        admin.set_password("admin123456")
        teacher_user = User(email=teacher.email, role="teacher", teacher_id=teacher.id)
        teacher_user.set_password("teacher123456")
        student_user = User(email=student.email, role="student", student_id=student.id)
        student_user.set_password("student123456")
        db.session.add_all([admin, teacher_user, student_user])
        db.session.commit()
        return {"student": student.id, "teacher": teacher.id, "course": course.id}


def bearer(token):
    return {"Authorization": f"Bearer {token}"}
