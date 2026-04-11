#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating cache table..."
python manage.py createcachetable

echo "Starting server..."
exec gunicorn eshcIntranet.wsgi:application --bind 0.0.0.0:8000 --log-level=info
