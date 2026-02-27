#!/bin/bash
set -e

echo "🔄 Running migrations..."
python manage.py migrate --noinput
python manage.py migrate --database=mongo --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo "🚀 Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
