#!/usr/bin/env bash

python manage.py collectstatic --noinput
python manage.py migrate --noinput

gunicorn --bind 0.0.0.0:8000 --workers 3 api.wsgi:application