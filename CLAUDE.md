# CLAUDE.md

Guidance for working in this repository. Read `SPEC.md` first — it is the **source of truth**.
This file tells you *how* to work; `SPEC.md` tells you *what* to build.

## What this project is

A Django (MVT) **Job Recruitment System** for a university full-stack module (5COSC017C, CW2).
Two roles (Candidate, Employer), job + application CRUD, role-based auth, Django admin, a small
DRF API, cloud Postgres, and a live deployment. Full details and the feature→mark mapping are
in `SPEC.md §4`.

## Golden rules

1. **Build exactly the rubric — no more, no less.** Every feature must map to a line in
   `SPEC.md §4`. If something isn't in the spec, it's in `SPEC.md §14` (out of scope). Do not
   add features, libraries, or abstractions that aren't required.
2. **Ask before expanding scope.** If you think something is missing or worth adding, stop and
   ask rather than building it.
3. **Right-sized, idiomatic Django.** This is undergraduate full-stack coursework, not a
   production platform. Prefer Django's built-in tools over clever abstractions. Plain and
   correct beats fancy.
4. **The author must be able to explain every line.** Write code and comments so a student can
   read the file and explain in a demo *why* it works. Favour clarity over compression.

## Coding conventions

- **Views:** function-based views with `@login_required` / the project's `role_required`
  decorator. No class-based view hierarchies unless a single generic view is clearly simpler.
- **Forms:** Django `ModelForm`s for all create/update. Do CRUD through forms, not manual
  request parsing.
- **Auth:** Django's built-in auth system + a small custom `role_required` decorator
  (`accounts/decorators.py`). Do not hand-roll authentication.
- **Templates:** server-rendered Django templates extending `base.html`. Bootstrap 5 via CDN.
  Vanilla JS only, and only where the spec calls for it.
- **Models:** keep fields exactly as `SPEC.md §5`. Custom `User` model created **before** the
  first migration.
- **Comments:** short, purposeful comments explaining intent (the *why*), not narrating obvious
  syntax. Add a one-line docstring to each view describing what it does and who can access it.
- **Naming:** descriptive, lowercase_with_underscores for functions/vars, named URL patterns
  matching `SPEC.md §6`.
- **No secrets in code.** `SECRET_KEY` and `DATABASE_URL` come from environment variables.
  Keep `.env` out of git; provide `.env.example`.

## What NOT to do

- Don't over-engineer: no service layers, custom managers, signals, or generic mixins unless
  the spec needs them (it doesn't).
- Don't add anything from `SPEC.md §14`.
- Don't introduce a JS framework — templates only.
- Don't change the data model without updating `SPEC.md` and asking first.
- Don't commit `.env`, the SQLite db, `__pycache__`, or `staticfiles/`.

## Project layout (target)

See `SPEC.md §13`. Apps: `accounts` (user + auth), `jobs` (core domain + views/forms/templates),
`api` (DRF), with shared `templates/` and `static/`.

## Common commands

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations && python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
python manage.py collectstatic --noinput     # before deploy
```

## Definition of done

Before saying a phase is finished, check it against the relevant items in `SPEC.md §15`.
A feature isn't done until it works end-to-end in the browser (or via the API) and is gated to
the correct role.
