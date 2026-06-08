"""Gunicorn configuration.

Gunicorn auto-loads this file when started from the project root (e.g. the
host's default `gunicorn app:app`). It runs collectstatic and migrate once at
startup, so the app deploys correctly even when the host uses its default build
and start commands (i.e. without running build.sh).
"""


def on_starting(server):
    """Prepare the app before workers start: gather static files (for WhiteNoise)
    and apply any pending database migrations."""
    import os

    import django
    from django.core.management import call_command

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recruitment.settings")
    django.setup()

    call_command("collectstatic", "--no-input")
    call_command("migrate", "--no-input")
