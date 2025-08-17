#!/bin/bash
set -o errexit
# Run django migrations
python manage.py migrate --noinput

python manage.py collectstatic --noinput

# Start FastAPI app
gunicorn hostelier.wsgi:application \
  --bind 0.0.0:$PORT
