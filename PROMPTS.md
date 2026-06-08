# PROMPTS.md — Build Order for Claude Code

Paste these into Claude Code **in order**. Each phase produces a working increment. After each
phase, run the app and check it before moving on. Every prompt assumes `SPEC.md` and `CLAUDE.md`
are in the repo root and should be followed exactly.

> Reminder of the golden rule for every prompt: build **only** what `SPEC.md` defines. If
> something seems missing or worth adding, ask first — don't expand scope.

---

## Phase 0 — Orientation

```
Read SPEC.md and CLAUDE.md fully before writing any code. Summarise back to me, in 5 bullet
points, exactly what we are building and what is explicitly out of scope. Do not write code yet.
```

## Phase 1 — Project skeleton + custom user

```
Create the Django project per SPEC.md §13.
- Project package: recruitment. Apps: accounts, jobs, api.
- In accounts, create the custom User model extending AbstractUser with a `role` field
  (candidate | employer) exactly as SPEC.md §5.1. Set AUTH_USER_MODEL before any migration.
- Configure settings to read SECRET_KEY and DATABASE_URL from environment (python-dotenv +
  dj-database-url), defaulting to SQLite locally. Add WhiteNoise and basic static config.
- Add a base.html template with a Bootstrap 5 (CDN) navbar and a messages block, and a simple
  job_list placeholder page at "/".
- Create requirements.txt and .env.example.
Run makemigrations + migrate and confirm the server starts.
```

## Phase 2 — Models, migrations, admin

```
Implement the remaining models exactly per SPEC.md §5: CompanyProfile, Job, Application
(with unique_together on job+candidate), Interview. Use the exact fields, choices, and
relationships listed. Then register all five models in the Django admin with list_display,
list_filter, and search_fields per SPEC.md §9. Make and apply migrations. Create a superuser
and confirm every model is manageable in /admin.
```

## Phase 3 — Auth + role-based access

```
Implement authentication and authorization per SPEC.md §8.
- Registration view/form that lets the user pick a role (candidate or employer) and creates the
  account. For employers, also create or prompt for a CompanyProfile.
- Use Django's built-in login/logout.
- Add accounts/decorators.py with a role_required decorator and a dashboard view that redirects
  to the correct role dashboard.
- Make the navbar links reflect auth state and role.
Confirm a candidate cannot reach employer URLs and vice versa (test by typing the URL directly).
```

## Phase 4 — Public job browsing + employer job CRUD

```
Implement per SPEC.md §6 and §10:
- Public job_list (active jobs as Bootstrap cards) with a simple search/filter on title/location,
  and job_detail.
- Employer job CRUD using ModelForms: list own jobs with applicant counts, create, edit, delete
  (with a JS confirm on delete). Enforce that employers can only edit/delete their own jobs.
Use named routes matching SPEC.md §6. Show success/error messages.
```

## Phase 5 — Candidate applications + employer applicant management

```
Implement per SPEC.md §6 and §8:
- Candidate: apply_to_job (create Application via ModelForm with cover_letter; block duplicate
  applications), my_applications (list own applications + status), withdraw_application.
- Employer: job_applicants (applicants for one of their jobs), update_status (change an
  application's status), schedule_interview (create/edit the Interview for an application).
Enforce object ownership in the views, not just templates. Add the candidate and employer
dashboards summarising their data.
```

## Phase 6 — Frontend polish

```
Do a templating pass per SPEC.md §10 only — do not add features.
- Ensure every page extends base.html and is responsive on mobile and desktop.
- Style forms, tables, and dashboards with Bootstrap.
- Add the minimal vanilla JS the spec allows (confirm-on-delete, optional client-side job filter).
Keep it clean and consistent; no new pages beyond SPEC.md §6.
```

## Phase 7 — REST API (DRF)

```
Add the API per SPEC.md §7 in the api app:
- GET /api/jobs/ (active jobs), GET /api/jobs/<id>/, GET /api/applications/ (current user's own
  applications only, permission-gated).
- Use serializers and DRF generic views or a ViewSet. Return correct status codes.
Confirm the endpoints work via the browser/DRF browsable API.
```

## Phase 8 — Cloud Postgres + deployment

```
Prepare for production per SPEC.md §11 and §12, then deploy.
- Connect to a cloud Postgres via DATABASE_URL (Neon or Supabase free tier).
- Production settings: DEBUG=False, SECRET_KEY from env, ALLOWED_HOSTS set, WhiteNoise static,
  gunicorn entry. Add a build step that runs collectstatic and migrate.
- Give me exact, copy-paste deployment steps for PythonAnywhere or Render (whichever you
  recommend for a free, reliable submission), including env vars and how to create the superuser
  on the host.
Then confirm the live URL works.
```

## Phase 9 — Finish & verify

```
Final pass, no new features:
- Write README.md (setup, run, env vars, live URL placeholder).
- Confirm requirements.txt and .env.example are complete and .gitignore excludes .env, db.sqlite3,
  __pycache__, staticfiles.
- Walk through SPEC.md §15 (Definition of Done) item by item and tell me which are met and which
  aren't. Fix any gaps.
```

---

## Notes for you (not for Claude Code)

- **Deploy early if you can.** If time is tight, run a stripped Phase 8 right after Phase 2 to
  prove hosting works (deploy a near-empty app), then redeploy at the end. Hosting is where days
  get lost — de-risk it first.
- **Screenshots + ER diagram** for the CW2 report come from the finished app — capture them after
  Phase 8.
- **Be able to explain it.** After each phase, skim the code Claude Code wrote and make sure you
  could walk a marker through it. That, not anything cosmetic, is what protects the grade.
