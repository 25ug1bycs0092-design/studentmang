from datetime import date

from backend.app.extensions import db
from backend.app.models import AcademicResult, Attendance, FeeAccount, Payment, Student, User
from backend.app.seed import seed_demo
from backend.app.config import _database_url
from tests.conftest import bearer


def login(client, role, identity, password):
    response = client.post(
        "/api/auth/login",
        json={"role": role, "identity": identity, "password": password},
    )
    assert response.status_code == 200
    return response.json["token"]


def test_health_and_login_password_hash(client, app, seeded_records):
    assert client.get("/api/health").json["database"] == "connected"
    response = client.post(
        "/api/auth/login",
        json={"role": "student", "identity": seeded_records["student"], "password": "student123456"},
    )
    assert response.status_code == 200
    assert response.json["role"] == "student"
    assert response.json["student_id"] == seeded_records["student"]
    with app.app_context():
        user = db.session.execute(db.select(User).filter_by(role="student")).scalar_one()
        assert user.password_hash != "student123456"
        assert user.check_password("student123456")


def test_student_crud_search_and_forbidden_access(client, admin_token, seeded_records):
    admin = bearer(admin_token)
    created = client.post(
        "/api/students",
        headers=admin,
        json={
            "id": "STU-2",
            "name": "Second Student",
            "email": "second@example.edu",
            "department": "Computer Science",
            "course": "B.Sc. Computer Science",
            "fee": 1000,
            "paid": 200,
            "password": "student-preview-password",
        },
    )
    assert created.status_code == 201
    assert created.json["paid"] == 200
    assert login(client, "student", "STU-2", "student-preview-password")
    assert client.get("/api/students?q=Second", headers=admin).json[0]["id"] == "STU-2"
    assert client.put("/api/students/STU-2", headers=admin, json={"name": "Updated Student"}).json["name"] == "Updated Student"
    student_token = login(client, "student", "STU-1", "student123456")
    assert client.get("/api/students", headers=bearer(student_token)).status_code == 403
    assert client.get("/api/students/STU-2", headers=bearer(student_token)).status_code == 403
    assert client.delete("/api/students/STU-2", headers=admin).status_code == 204
    assert client.post(
        "/api/auth/login",
        json={"role": "student", "identity": "STU-2", "password": "student-preview-password"},
    ).status_code == 401


def test_teacher_and_course_management(client, admin_token, seeded_records):
    headers = bearer(admin_token)
    teacher = client.post(
        "/api/teachers",
        headers=headers,
        json={
            "id": "TCH-2",
            "name": "Another Teacher",
            "email": "another@example.edu",
            "department": "Business",
            "subject": "Finance",
        },
    )
    assert teacher.status_code == 201
    assert teacher.json["department"] == "Business"
    course = client.post(
        "/api/courses",
        headers=headers,
        json={
            "id": "CRS-2",
            "name": "Business Finance",
            "department": "Business",
            "teacher": "Another Teacher",
            "capacity": 20,
            "duration": "1 year",
        },
    )
    assert course.status_code == 201
    assert course.json["teacher"] == "Another Teacher"
    assert client.post(
        "/api/courses/CRS-2/enrollments",
        headers=headers,
        json={"student_id": seeded_records["student"]},
    ).status_code == 201
    assert client.get("/api/courses/CRS-2", headers=headers).json["students"] == 1


def test_attendance_mark_retrieve_and_teacher_scope(app, client, admin_token, seeded_records):
    headers = bearer(admin_token)
    marked = client.post(
        "/api/attendance",
        headers=headers,
        json={
            "date": date.today().isoformat(),
            "records": [
                {"student_id": seeded_records["student"], "status": "Present"},
                {"student_id": "MISSING", "status": "Absent"},
            ],
        },
    )
    assert marked.status_code == 404
    assert client.get("/api/attendance", headers=headers).json == []
    saved = client.post(
        "/api/attendance",
        headers=headers,
        json={
            "date": date.today().isoformat(),
            "records": [{"student_id": seeded_records["student"], "status": "Present"}],
        },
    )
    assert saved.status_code == 200
    assert saved.json[0]["status"] == "Present"
    assert client.get(f"/api/attendance?date={date.today().isoformat()}", headers=headers).json[0]["student_id"] == seeded_records["student"]
    assert client.post(
        "/api/attendance",
        headers=headers,
        json={"date": date.today().isoformat(), "records": [{"student_id": seeded_records["student"], "status": "Unknown"}]},
    ).status_code == 400
    with app.app_context():
        assert Attendance.query.count() == 1


def test_fees_dashboard_reports_and_portal(client, app, admin_token, seeded_records):
    headers = bearer(admin_token)
    account = client.post(
        "/api/fees/accounts",
        headers=headers,
        json={
            "student_id": seeded_records["student"],
            "period": str(date.today().year),
            "total_due": 1000,
        },
    )
    assert account.status_code == 201
    payment = client.post(
        f"/api/fees/{seeded_records['student']}",
        headers=headers,
        json={"amount": 400, "period": str(date.today().year), "method": "Card"},
    )
    assert payment.status_code == 201
    assert client.post(
        f"/api/fees/{seeded_records['student']}",
        headers=headers,
        json={"amount": 700, "period": str(date.today().year)},
    ).status_code == 400
    assert client.get("/api/dashboard", headers=headers).json["fees"]["pending"] == 600
    performance = client.get("/api/reports/performance", headers=headers)
    assert performance.status_code == 200
    assert {"monthly_scores", "attendance_by_course", "enrollment_trends"} <= set(performance.json)
    assert performance.json["attendance_by_course"] == [{"course": "B.Sc. Computer Science", "attendance": 0}]
    student_token = login(client, "student", "STU-1", "student123456")
    portal = client.get("/api/portal/me", headers=bearer(student_token))
    assert portal.status_code == 200
    assert portal.json["profile"]["id"] == seeded_records["student"]
    assert len(portal.json["fees"]) == 1
    assert client.post(
        f"/api/fees/{seeded_records['student']}",
        headers=bearer(student_token),
        json={"amount": 1},
    ).status_code == 403


def test_validation_and_authentication(client, admin_token):
    assert client.get("/api/students").status_code == 401
    assert client.post("/api/students", headers=bearer(admin_token), json={"name": ""}).status_code == 400
    duplicate = client.post(
        "/api/students",
        headers=bearer(admin_token),
        json={"id": "DUP", "name": "A", "email": "bad", "course": "Course"},
    )
    assert duplicate.status_code == 400


def test_records_are_backed_by_database(app, client, admin_token):
    response = client.post(
        "/api/students",
        headers=bearer(admin_token),
        json={"id": "PERSIST", "name": "Persisted", "email": "persist@example.edu", "course": "New Course"},
    )
    assert response.status_code == 201
    with app.app_context():
        assert db.session.get(Student, "PERSIST") is not None
        assert FeeAccount.query.count() == 0
        assert Payment.query.count() == 0


def test_teacher_scope_and_sensitive_fields(client, admin_token, seeded_records):
    headers = bearer(admin_token)
    created = client.post(
        "/api/students",
        headers=headers,
        json={
            "id": "STU-OTHER",
            "name": "Business Student",
            "email": "business@example.edu",
            "department": "Business",
            "course": "Business Administration",
        },
    )
    assert created.status_code == 201
    teacher_token = login(client, "teacher", "teacher@example.edu", "teacher123456")
    teacher_headers = bearer(teacher_token)
    assert [row["id"] for row in client.get("/api/students", headers=teacher_headers).json] == ["STU-1"]
    assert client.get("/api/students/STU-OTHER", headers=teacher_headers).status_code == 403
    assert client.post(
        "/api/attendance",
        headers=teacher_headers,
        json={"date": date.today().isoformat(), "records": [{"student_id": "STU-OTHER", "status": "Present"}]},
    ).status_code == 403
    assert "fee" not in client.get("/api/students/STU-1", headers=teacher_headers).json
    assert client.get("/api/dashboard", headers=teacher_headers).json["fees"] is None
    assert [row["id"] for row in client.get("/api/teachers", headers=teacher_headers).json] == ["TCH-1"]


def test_academic_and_attendance_reports_are_database_derived(client, app, admin_token, seeded_records):
    headers = bearer(admin_token)
    result = client.post(
        "/api/results",
        headers=headers,
        json={
            "student_id": seeded_records["student"],
            "course_id": seeded_records["course"],
            "term": "Fall",
            "assessment": "Midterm",
            "score": 85,
            "max_score": 100,
            "recorded_at": date.today().isoformat(),
        },
    )
    assert result.status_code == 201
    attendance = client.post(
        "/api/attendance",
        headers=headers,
        json={"date": date.today().isoformat(), "records": [{"student_id": "STU-1", "status": "Late"}]},
    )
    assert attendance.status_code == 200
    report = client.get(
        f"/api/reports/attendance?start={date.today().isoformat()}&end={date.today().isoformat()}",
        headers=headers,
    )
    assert report.status_code == 200
    assert report.json["students"][0]["attendance_percent"] == 100
    assert client.get("/api/reports/academic", headers=headers).json["results"][0]["score"] == 85
    performance = client.get("/api/reports/performance", headers=headers).json
    assert performance["monthly_scores"][0]["score"] == 85
    assert performance["monthly_scores"][0]["average"] == 85


def test_seed_demo_initializes_actual_records_and_password_hashes(app, client):
    with app.app_context():
        count = seed_demo("Local-only-campus-password")
        db.session.commit()
        assert count > 20
        assert Student.query.count() == 6
        assert Attendance.query.count() == 30
        assert FeeAccount.query.count() == 6
        assert Payment.query.count() == 6
    login_response = client.post(
        "/api/auth/login",
        json={
            "role": "admin",
            "identity": "admin@campus.edu",
            "password": "Local-only-campus-password",
        },
    )
    assert login_response.status_code == 200
    assert login_response.json["role"] == "admin"


def test_api_validation_and_cors_preflight(client):
    malformed = client.post(
        "/api/auth/login",
        data="{invalid json",
        content_type="application/json",
    )
    assert malformed.status_code == 400
    assert malformed.json["message"] == "Request body must contain valid JSON."
    preflight = client.options(
        "/api/students",
        headers={
            "Origin": "http://localhost:5000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["Access-Control-Allow-Origin"] == "http://localhost:5000"


def test_frontend_served_without_exposing_backend_source(client):
    assert client.get("/").status_code == 200
    assert client.get("/app.js").status_code == 200
    assert client.get("/styles.css").status_code == 200
    assert client.get("/backend/app/models.py").status_code == 404


def test_postgres_url_normalization_and_production_secret_requirement(monkeypatch):
    from backend.app import create_app

    monkeypatch.setenv("DATABASE_URL", "postgres://campus:secret@example.test/campusly")
    assert _database_url() == "postgresql://campus:secret@example.test/campusly"
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    try:
        create_app({"SECRET_KEY": None, "JWT_SECRET_KEY": None})
    except RuntimeError as error:
        assert "must be configured in production" in str(error)
    else:
        raise AssertionError("Production startup must reject missing secrets.")
