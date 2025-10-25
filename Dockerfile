# =========================
# Stage 1: Builder
# =========================
FROM python:3.11-slim as builder

ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc g++ libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev \
    libjpeg-dev libpng-dev curl && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# =========================
# Stage 2: Runtime
# =========================
FROM python:3.11-slim as runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=securityscanner.settings

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl3 libffi8 libxml2 libxslt1.1 zlib1g libjpeg62-turbo libpng16-16 curl \
    && rm -rf /var/lib/apt/lists/* && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create app user and working directory
RUN groupadd -r app && useradd -r -g app app && \
    mkdir -p /app/static /app/media /app/logs && chown -R app:app /app

WORKDIR /app

# Copy all files to container
COPY --chown=app:app . .

USER app

# Collect static files
RUN python securityscanner/manage.py collectstatic --noinput

# Health check (for Railway)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Expose Django port
EXPOSE 8000

# Run Gunicorn using Django’s WSGI app
# Adjusted to reflect that manage.py and wsgi.py are under securityscanner/
CMD ["gunicorn", "securityscanner.wsgi:application", "--chdir", "securityscanner", "--bind", "0.0.0.0:8000", "--timeout", "120"]
