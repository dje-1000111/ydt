#!/bin/sh
DJAPP_PORT=${PORT:-8000}
python manage.py makemigrations
python manage.py migrate --no-input
python manage.py collectstatic --no-input
# python manage.py loaddata fixtures/entire_dictation.json # backup
python manage.py loaddata fixtures/last_dictation_only.json # without users - first install

DJANGO_SUPERUSER_PASSWORD=$DB_PASSWD python manage.py createsuperuser --username $DB_USER --email $SUPERUSER_EMAIL --noinput

gunicorn config.wsgi:application --bind 0.0.0.0:${DJAPP_PORT}