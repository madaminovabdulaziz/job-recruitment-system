#!/usr/bin/env bash
# Build step for deployment (e.g. Render). Run on every deploy.
set -o errexit  # stop on first error

pip install -r requirements.txt
python manage.py collectstatic --no-input   # gather static files for WhiteNoise
python manage.py migrate                     # apply migrations to the cloud DB
