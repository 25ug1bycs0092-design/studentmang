from backend.app.routes.academic import academic_bp
from backend.app.routes.attendance import attendance_bp
from backend.app.routes.auth import auth_bp
from backend.app.routes.courses import courses_bp
from backend.app.routes.dashboard import dashboard_bp
from backend.app.routes.fees import fees_bp
from backend.app.routes.portal import portal_bp
from backend.app.routes.reports import reports_bp
from backend.app.routes.students import students_bp
from backend.app.routes.teachers import teachers_bp


def register_routes(app) -> None:
    for blueprint in (
        auth_bp,
        students_bp,
        teachers_bp,
        courses_bp,
        attendance_bp,
        fees_bp,
        portal_bp,
        dashboard_bp,
        reports_bp,
        academic_bp,
    ):
        app.register_blueprint(blueprint, url_prefix="/api")
