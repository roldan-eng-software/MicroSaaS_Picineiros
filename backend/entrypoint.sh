#!/usr/bin/env bash
set -euo pipefail

python manage.py migrate --noinput

if [ "${DJANGO_LOAD_BEAT_SCHEDULES:-true}" = "true" ]; then
  # Tenta criar/atualizar crons (idempotente)
  python manage.py setup_beat_schedules || true
fi

exec "$@"
