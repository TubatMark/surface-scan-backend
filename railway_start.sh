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

# Start both Gunicorn and Celery
echo "🚀 Starting both Gunicorn and Celery..."
exec ./start_both.sh
