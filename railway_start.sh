#!/bin/bash

# Railway startup script for Django backend
set -e

echo "🚀 Starting Railway deployment..."

# Set default port if not provided
PORT=${PORT:-8000}

echo "📋 Environment check:"
echo "  - PORT: $PORT"
echo "  - SECRET_KEY: ${SECRET_KEY:0:10}..."
echo "  - DEBUG: $DEBUG"
echo "  - REDIS_URL: ${REDIS_URL:0:20}..."

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files (if needed)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (optional)
# echo "👤 Creating superuser..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'admin')
# "

# Start the application
echo "🚀 Starting Gunicorn server on port $PORT..."
exec gunicorn securityscanner.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
