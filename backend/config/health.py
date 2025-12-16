from django.db import connection
from django.http import JsonResponse
from django.conf import settings
import redis


def health_view(_request):
    # Check DB
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            db_ok = True
    except Exception:
        db_ok = False

    # Check Redis
    redis_ok = True
    try:
        url = settings.CELERY_BROKER_URL
        client = redis.from_url(url)
        client.ping()
    except Exception:
        redis_ok = False

    status = 200 if (db_ok and redis_ok) else 503
    return JsonResponse({"db": db_ok, "redis": redis_ok, "status": status}, status=status)
