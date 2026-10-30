# studentmang

## Campusly Student Management

Student management system with a responsive frontend and Flask REST API. The API uses SQLAlchemy with SQLite locally and PostgreSQL on Render. It serves the frontend from the same origin by default, so the app uses `/api` without a production URL change.

## Local setup (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Set distinct `SECRET_KEY` and `JWT_SECRET_KEY` values in `.env`. For a disposable development database, initialize the schema:

```powershell
python -m flask --app backend:create_app init-db
```

Optional realistic starter records and user accounts are inserted only when explicitly requested. Set a strong local seed password; it will be used for the sample admin, teacher, and student accounts:

```powershell
$env:SEED_PASSWORD = "choose-a-unique-local-password"
python -m flask --app backend:create_app seed-demo
Remove-Item Env:SEED_PASSWORD
```

Seeded account identities are `admin@campus.edu`, `alex.morgan@campus.edu` (teacher), and `STU-2401` (student). Use the seed password entered above. The seed command refuses to run against a non-empty database. Do not seed demo accounts or use shared sample passwords in production.

Run the app and tests:

```powershell
python -m flask --app backend:create_app run --debug
python -m pytest -q
```

Open `http://127.0.0.1:5000`. The app creates no startup/sample records by itself. Use `init-db` for schema creation and `seed-demo` only for local testing.

## Database and production configuration

Copy `.env.example` and configure:

- `DATABASE_URL`: defaults to `sqlite:///campusly.sqlite`; for PostgreSQL, use `postgresql://user:password@host:5432/database`. Render's legacy `postgres://` URL is normalized.
- `SECRET_KEY` and `JWT_SECRET_KEY`: separate high-entropy secrets. Required in production.
- `CORS_ORIGINS`: comma-separated allowed browser origins when the frontend is hosted separately. Same-origin Render deployment does not require CORS.
- `JWT_ACCESS_TOKEN_MINUTES`: bearer token lifetime (default 60).
- `SEED_PASSWORD`: only for the explicit local `seed-demo` command.

`render.yaml` provisions a Render web service and PostgreSQL database. The web service creates the initial schema with `flask ... init-db` before starting Gunicorn. It serves the frontend and API on the same origin. Configure `CORS_ORIGINS` if you deploy the frontend elsewhere. Set database and secrets in Render's environment instead of committing `.env` files.

The schema initializer is idempotent for initial deployment; `create_all` is not a schema migration system. Use a reviewed database migration before changing an already-deployed schema.

## Authentication and authorization

`POST /api/auth/login` authenticates `admin`, `teacher`, or `student` accounts and returns a JWT. Send it on protected requests:

```http
Authorization: Bearer <token>
```

Passwords are stored as Werkzeug scrypt hashes. Admins control student, teacher, course, fee, and enrollment mutations; teachers can access their assigned course records and mark attendance or record results for those courses; students can access only their own portal, profile, attendance, fees, results, and enrolled courses. The backend enforces every role check; frontend navigation is not an authorization boundary.

An admin login account is created by the explicit seed command. Admins create linked teacher/student login accounts using `POST /api/auth/users`, after creating the corresponding profile. Profile creation can also include an optional `password` (at least 10 characters) to create a linked login. Never log passwords or JWTs.

## API features

- Authentication: `POST /api/auth/login`, `GET /api/auth/me`, admin-only `POST /api/auth/users`.
- Students: `GET/POST /api/students`, `GET/PUT/DELETE /api/students/{id}`. List filters include `q`, `department`, `course`, and `status`.
- Teachers: `GET/POST /api/teachers`, `GET/PUT/DELETE /api/teachers/{id}`.
- Courses/departments: `GET/POST /api/courses`, `GET/PUT/DELETE /api/courses/{id}`, course enrollment list/add/drop, and `GET/POST/PUT/DELETE /api/departments`.
- Attendance: `GET /api/attendance?date=YYYY-MM-DD`; `POST /api/attendance` upserts one record or a batch.
- Fees: `GET /api/fees`, `GET /api/fees/{student_id}`, admin `POST /api/fees/accounts`, and `POST /api/fees/{student_id}` to record a payment.
- Student portal: `GET /api/portal/me` returns the authenticated student's profile, enrollments, attendance, fee accounts, and academic results.
- Dashboard: `GET /api/dashboard` returns database-derived totals, today's attendance, and billed/collected/pending totals.
- Academic results: `GET/POST /api/results`, `DELETE /api/results/{id}`.
- Reports: `GET /api/reports/performance`, `/api/reports/attendance?start=YYYY-MM-DD&end=YYYY-MM-DD`, `/api/reports/academic`, and admin-only `/api/reports/fees`.

All responses and reports are calculated from committed database records; empty report ranges return empty arrays or zero counts rather than fabricated values. Student and teacher objects returned by the API match the frontend contract. Attendance values are `Present`, `Absent`, or `Late`; fee balances are derived from fee accounts minus payment records.

## Frontend API URL

The integrated frontend uses the same-origin `/api` URL, suitable for the included Render configuration. For a separately hosted frontend, set the API base before `app.js` in `index.html`:

```html
<script>window.CAMPUSLY_API_BASE = "https://your-api.example.com/api";</script>
<script src="app.js" defer></script>
```

Then configure the Flask `CORS_ORIGINS` value to the exact frontend origin. The frontend uses backend login and loads its student portal from `/api/portal/me`; it no longer accepts preview credentials as a successful login. Local unsynced preview data is retained for interface development only.

## API documentation and Postman

- OpenAPI 3 specification: [`docs/openapi.yaml`](./docs/openapi.yaml)
- Importable Postman collection: [`postman/Campusly.postman_collection.json`](./postman/Campusly.postman_collection.json)
- Configure collection variables `baseUrl`, `seedPassword`, and `attendanceDate`. Run the seed command first for sample account IDs.

The collection includes login, student search/create, teacher and course reads, attendance, fees, dashboard, student portal, and reports. OpenAPI describes authentication and all primary API resources.
