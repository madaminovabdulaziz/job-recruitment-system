"""WSGI entry-point alias.

Some hosts default to running `gunicorn app:app`. This exposes the project's
WSGI application (defined in recruitment/wsgi.py) under that name so the default
start command works without extra configuration.
"""

from recruitment.wsgi import application as app
