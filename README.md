# Job Recruitment System

A Django (MVT) job recruitment portal. Employers post vacancies and manage applicants;
candidates browse jobs, apply, and track their applications.

## Features

- Two roles — **Candidate** and **Employer** — chosen at registration, enforced server-side.
- Job browsing with search (public), and full **job CRUD** for employers.
- **Applications**: apply (one per job), withdraw, and track status.
- **Applicant management**: employers view applicants, change status, and schedule interviews.
- Django **admin** for the HR-agency staff layer (all five models registered).
- A small read-only **REST API** (Django REST Framework).
- Cloud **PostgreSQL** in production; SQLite locally.

## Tech stack

Python 3.11 · Django 5.1 · Django REST Framework · Bootstrap 5 (CDN) ·
gunicorn · WhiteNoise · PostgreSQL (`dj-database-url` + `psycopg`).

## Local setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env                # then edit values as needed

# 4. Set up the database (SQLite by default)
python manage.py migrate
python manage.py createsuperuser

# 5. Run
python manage.py runserver
```

Visit http://127.0.0.1:8000/. The admin is at `/admin/`, the API at `/api/`.

## Environment variables

Configured in `.env` locally (see `.env.example`) and in the host's dashboard in production.

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | a long random string |
| `DEBUG` | `True` locally, `False` in production | `False` |
| `ALLOWED_HOSTS` | comma-separated hosts | `myapp.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | comma-separated HTTPS origins | `https://myapp.onrender.com` |
| `DATABASE_URL` | cloud Postgres URL (blank = local SQLite) | `postgres://user:pass@host:5432/db` |

## REST API (read-only)

| Endpoint | Access | Returns |
|---|---|---|
| `GET /api/jobs/` | public | list of active jobs |
| `GET /api/jobs/<id>/` | public | one job's detail |
| `GET /api/applications/` | authenticated | the logged-in user's own applications |

Browse them via the DRF browsable API; use the "Log in" link there to test the gated
applications endpoint.

## Deployment (Render)

The repo includes `Procfile`, `build.sh`, and `runtime.txt`.

1. Create a **PostgreSQL** instance (Render, Neon, or Supabase) and copy its connection URL.
2. Create a **Web Service** from this repo with:
   - **Build command:** `./build.sh` (installs deps, runs `collectstatic`, applies migrations)
   - **Start command:** `gunicorn recruitment.wsgi`
3. Set the environment variables from the table above, with:
   - `DEBUG=False`
   - `ALLOWED_HOSTS` = your Render domain
   - `CSRF_TRUSTED_ORIGINS` = `https://<your-domain>`
   - `DATABASE_URL` = the Postgres URL from step 1
   - `SECRET_KEY` = a fresh random value
4. Deploy, then create an admin user via the host's shell:
   `python manage.py createsuperuser`.

When `DEBUG=False`, the app serves static files through WhiteNoise and forces HTTPS
(secure cookies + SSL redirect). HTTPS itself is provided by the host.

> **PythonAnywhere** is also supported: use the same env vars and run
> `pip install -r requirements.txt`, `collectstatic`, and `migrate` manually, with the WSGI
> file pointing at `recruitment.wsgi`.

## Project layout

```
recruitment/   project package (settings, urls, wsgi)
accounts/      custom User model, registration, role_required decorator
jobs/          Company, Job, Application, Interview + views/forms/templates
api/           DRF serializers + views
templates/     base.html + shared templates
static/        project static assets
```
