# Job Recruitment System — Build Specification (Source of Truth)

**Module:** 5COSC017C Full Stack Web Development (WIUT)
**Covers:** CW1 Business Case Report (20%) and CW2 Development Portfolio (80%)
**Business case (from approved list):** *Job Recruitment System (Human Resources)* — an HR
agency portal where companies post vacancies and candidates apply, track status, and have
interviews scheduled.

---

## 0. How to use this document

This file is the **single source of truth** for the build.

- If a feature is described here, build it.
- If it is **not** here, it is **out of scope** — see §14. Do not add it.
- Every feature in §4 maps to a specific line in the CW2 marking scheme. The goal is to
  satisfy the rubric exactly: *no more, no less.*
- When in doubt, ask before adding anything. Scope creep costs time and weakens the work.

---

## 1. Goal in one sentence

A Django (MVT) web app with two user roles (Candidate, Employer), full CRUD on jobs and
applications, role-based auth, a Django admin panel, a small REST API, a cloud PostgreSQL
database, and a live deployment — built to be clean, idiomatic, and explainable by the author.

---

## 2. Roles & permissions

| Role | Can do |
|------|--------|
| **Candidate** | Register/login; browse & search jobs; view job detail; apply (one application per job); view own applications and their status; withdraw an application. |
| **Employer** | Register/login; create a company profile; create/edit/delete own job postings (CRUD); view applicants for own jobs; change an application's status; schedule an interview for an application. |
| **Admin (Django admin)** | The HR agency staff layer. Manage all users, companies, jobs, applications, interviews via the built-in admin. |

A user is **either** a Candidate **or** an Employer, chosen at registration. A Candidate must
never reach Employer-only pages and vice-versa (enforced server-side, see §8).

---

## 3. Tech stack (keep it boring and standard)

- Python 3.11+, Django 5.x
- Django REST Framework (the API only)
- PostgreSQL (cloud-hosted — the "external database")
- Bootstrap 5 (via CDN), minimal vanilla JavaScript
- gunicorn + WhiteNoise for serving in production
- `python-dotenv` for local env vars, `dj-database-url` + `psycopg[binary]` for the DB URL
- Deploy target: **PythonAnywhere** or **Render** (both acceptable per the brief). External
  DB: a free persistent Postgres (Neon or Supabase) if the host's own DB is limited.

> Pin versions in `requirements.txt`. Verify current free-tier terms of the chosen host/DB
> before relying on them.

---

## 4. Feature → Mark mapping (the contract)

This is the part that matters. Each row is a CW2 mark line and the concrete thing that earns it.

| CW2 mark line | Marks | What we build to earn it |
|---|---|---|
| Models & database integration | 10 | 5 related models (§5) with FKs, a one-to-one, and a unique constraint; migrations applied; cloud Postgres. |
| Views & URL routing | 15 | Public job list/detail; auth views; candidate dashboard + apply/withdraw; employer dashboard + job CRUD + applicant management + status update + interview scheduling. Clean `urls.py` with named routes (§6). |
| Templates & frontend (Bootstrap/CSS/JS) | 10 | `base.html` + responsive Bootstrap pages; job cards; styled forms; dashboards; a little JS (confirm-on-delete, client-side filter). |
| Forms & CRUD operations | 10 | Django `ModelForm`s: full CRUD on Job; create/withdraw on Application; status update form; interview form. |
| Authentication & authorization | 5 | Django built-in auth (register/login/logout) + role-based access control (§8). |
| Admin & data management | 5 | All models registered with `list_display`, `list_filter`, `search_fields`. |
| APIs & external DB connection | 10 | DRF read API for jobs & applications (§7) + cloud Postgres via `DATABASE_URL`. |
| Deployment | 15 | Live app on PythonAnywhere/Render; URL goes in the report. `DEBUG=False`, env-based secrets, `ALLOWED_HOSTS` set, static served. |
| Portfolio report | 20 | (Written separately — ER diagram, code snippets, screenshots, testing, deployment steps.) |

CW1 (the 2000-word report) is written from this same design: §2 → stakeholders/roles,
§4–§5 → requirements, §5–§8 → proposed technical solution, §6 → user flow, §12 → security,
and the build order in PROMPTS.md → implementation plan.

---

## 5. Data model

> Create the **custom user model first**, before the first migration. Changing the user model
> later is painful.

### 5.1 `User` (custom, extends `AbstractUser`)
- `role` — choice: `candidate` | `employer` (required at registration)
- inherits username, email, password, etc.

### 5.2 `CompanyProfile`
- `owner` — OneToOne → User (employer)
- `name` — char
- `description` — text
- `location` — char
- `website` — url (optional)

### 5.3 `Job`
- `company` — FK → CompanyProfile (on_delete=CASCADE)
- `title` — char
- `description` — text
- `location` — char
- `employment_type` — choice: full_time | part_time | contract | internship
- `salary_min`, `salary_max` — integer (optional)
- `is_active` — boolean (default True)
- `created_at` — datetime (auto)

### 5.4 `Application`
- `job` — FK → Job (on_delete=CASCADE)
- `candidate` — FK → User (on_delete=CASCADE)
- `cover_letter` — text
- `status` — choice: applied | under_review | interview | offered | rejected (default `applied`)
- `created_at` — datetime (auto)
- **constraint:** `unique_together (job, candidate)` — one application per job per candidate

### 5.5 `Interview`
- `application` — OneToOne → Application (on_delete=CASCADE)
- `scheduled_at` — datetime
- `mode` — choice: onsite | online
- `location_or_link` — char
- `notes` — text (optional)

Relationships to show on the ER diagram: User 1—1 CompanyProfile; CompanyProfile 1—* Job;
Job 1—* Application; User(candidate) 1—* Application; Application 1—1 Interview.

---

## 6. URL & view map

Use **function-based views** for clarity and easy explanation. Named routes throughout.

| URL | name | View | Access | Purpose |
|---|---|---|---|---|
| `/` | `job_list` | `job_list` | public | List active jobs + search/filter |
| `/jobs/<id>/` | `job_detail` | `job_detail` | public | Single job + "Apply" |
| `/register/` | `register` | `register` | anon | Register, choose role |
| `/login/`, `/logout/` | (Django auth) | built-in | — | Auth |
| `/dashboard/` | `dashboard` | `dashboard` | logged-in | Redirect to role dashboard |
| `/candidate/applications/` | `my_applications` | `my_applications` | candidate | List own applications + status |
| `/jobs/<id>/apply/` | `apply` | `apply_to_job` | candidate | Create application |
| `/applications/<id>/withdraw/` | `withdraw` | `withdraw_application` | candidate | Delete own application |
| `/employer/jobs/` | `employer_jobs` | `employer_jobs` | employer | Own jobs + applicant counts |
| `/employer/jobs/new/` | `job_create` | `job_create` | employer | Create job |
| `/employer/jobs/<id>/edit/` | `job_edit` | `job_edit` | employer | Update job |
| `/employer/jobs/<id>/delete/` | `job_delete` | `job_delete` | employer | Delete job |
| `/employer/jobs/<id>/applicants/` | `job_applicants` | `job_applicants` | employer | Applicants for a job |
| `/applications/<id>/status/` | `update_status` | `update_status` | employer | Change application status |
| `/applications/<id>/interview/` | `schedule_interview` | `schedule_interview` | employer | Create/edit interview |

---

## 7. REST API (Django REST Framework)

Keep it small. Read-focused is enough for the 10 marks; add write only if time allows.

- `GET /api/jobs/` — list active jobs (serialize id, title, company name, location, type, created_at)
- `GET /api/jobs/<id>/` — job detail
- `GET /api/applications/` — applications for the logged-in user (own only; permission-gated)

Use serializers + DRF generic views or a `ViewSet`. Return proper status codes. Validate input
if any write endpoints are added.

---

## 8. Authentication & authorization rules

- Use Django's built-in auth for register/login/logout (`LoginRequiredMixin` / `login_required`).
- Add a small `role_required` decorator (and/or mixin) that checks `request.user.role`.
- Employer-only views: job CRUD, applicants, status update, interview.
- Candidate-only views: apply, withdraw, my applications.
- Object ownership: an employer may only edit/delete **their own** jobs and act on applications
  to those jobs; a candidate may only withdraw **their own** applications. Enforce in the view,
  not just the template.

---

## 9. Admin configuration

Register all five models. For Job and Application set `list_display`, `list_filter`
(e.g. status, employment_type, is_active), and `search_fields` (e.g. title, company name).

---

## 10. Frontend / templates

- `base.html` with a Bootstrap navbar (links change by role / auth state), messages block,
  and a content block.
- Pages: job list (cards + a search box), job detail, register, login, candidate dashboard,
  employer dashboard, job form, applicants table, interview form.
- Responsive via Bootstrap grid. Minimal vanilla JS: confirm dialog on delete; optional
  client-side filter on the job list.
- Show Django `messages` (success/error) after actions.

---

## 11. External database & deployment

- Local dev may use SQLite, but the **graded** build connects to **cloud Postgres** via
  `DATABASE_URL` (`dj-database-url`). This is the "external database connection".
- Production settings: `DEBUG=False`, `SECRET_KEY` from env, `ALLOWED_HOSTS` set to the host
  domain, WhiteNoise for static files, `collectstatic` in the build step, gunicorn as the server.
- Put the **live URL** in the CW2 report.

---

## 12. Security & non-functional (for CW1 + sane practice)

- CSRF protection (Django default) on all forms.
- Passwords hashed by Django's default hasher.
- Secrets (SECRET_KEY, DB URL) in environment variables, never committed.
- Role-based access control as in §8.
- Input validation through ModelForms / serializers.
- HTTPS provided by the host.
- Non-functional notes for the report: usability (Bootstrap, clear nav), maintainability
  (MVT separation, named routes), scalability (stateless app + managed Postgres).

---

## 13. Project structure (target)

```
recruitment/                # project package (settings, urls, wsgi)
accounts/                   # custom User, register/login, role decorator
jobs/                       # Company, Job, Application, Interview + views/forms/templates
api/                        # DRF serializers + views (or keep inside jobs/)
templates/                  # base.html + shared templates
static/                     # css/js
requirements.txt
.env.example
manage.py
README.md
```

---

## 14. OUT OF SCOPE — do **not** build

These are tempting but not in the rubric. Skipping them is correct, not lazy.

- Messaging/chat between users
- Email or push notifications
- Payments or subscriptions
- Resume file parsing / AI matching / recommendations
- Social login (Google/LinkedIn OAuth)
- Real-time features (websockets), analytics dashboards, multi-language
- A separate JS frontend framework (React/Vue) — server-rendered templates only

If any of these seems "nice to have," it isn't. Stop and finish the rubric items first.

---

## 15. Definition of Done (check before submitting CW2)

- [ ] 5 models migrated; relationships and unique constraint in place
- [ ] All URLs in §6 work and are role-gated correctly
- [ ] Bootstrap templates render on mobile and desktop
- [ ] Full CRUD on Job; create/withdraw Application; status + interview work
- [ ] Register/login/logout work; wrong-role access is blocked server-side
- [ ] All 5 models registered in admin with list_display/filter/search
- [ ] DRF endpoints return correct data + status codes
- [ ] App connects to cloud Postgres
- [ ] App deployed; live URL works with `DEBUG=False`
- [ ] `requirements.txt`, `.env.example`, `README.md` present
