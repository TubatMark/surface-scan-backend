#!/bin/bash

# Simple script to start both Gunicorn and Celery
set -e

echo "🚀 Starting both Gunicorn and Celery..."

# Start Celery worker in background
echo "🔄 Starting Celery worker..."
cd securityscanner && celery -A securityscanner worker --loglevel=info --concurrency=2 &
CELERY_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down..."
    kill $CELERY_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start Gunicorn in foreground
echo "🌐 Starting Gunicorn server on port ${PORT:-8000}..."
cd securityscanner && exec gunicorn securityscanner.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
