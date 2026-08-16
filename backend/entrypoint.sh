#!/bin/bash
set -e
mkdir -p /app/models
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
