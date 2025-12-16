# syntax=docker/dockerfile:1.4

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Create app dir
WORKDIR /app

# Install Python deps first (layer cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy project
COPY . /app

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh || true

# Optional: collect static if using staticfiles in prod
# Will not fail if collectstatic not configured
RUN python manage.py collectstatic --noinput || true

# Set default envs (can be overridden by compose)
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose Django port
EXPOSE 8000

# Default command is defined in docker-compose for web/worker/beat
CMD ["bash", "-lc", "python manage.py check && gunicorn config.wsgi:application -b 0.0.0.0:8000 --workers 3 --timeout 120"]
