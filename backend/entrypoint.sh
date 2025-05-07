#!/bin/bash

echo "Applying database migrations"
if python manage.py migrate; then
    echo "Migrations applied successfully"
else
    echo "Error applying migrations" >&2
    exit 1
fi

if python manage.py migrate django_celery_beat; then
    echo "django_celery_beat migrations applied successfully"
else
    echo "Error applying django_celery_beat migrations" >&2
    exit 1
fi

exec "$@"
