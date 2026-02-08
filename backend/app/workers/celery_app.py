"""Celery application configuration.

Redis + Celery are OPTIONAL for the MVP. The pipeline can be run manually via
`python -m app.pipeline` without any message broker. Celery is only needed for
automated scheduled runs in production.
"""

from loguru import logger

try:
    from celery import Celery

    from app.core.config import get_settings

    settings = get_settings()

    celery_app = Celery(
        "crowdpulse",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=[
            "app.workers.tasks",
        ],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Kolkata",
        enable_utc=True,
    )

    # Periodic task schedule
    celery_app.conf.beat_schedule = {
        "ingest-telegram-every-15min": {
            "task": "app.workers.tasks.ingest_telegram",
            "schedule": 900.0,  # 15 minutes
        },
        "ingest-youtube-every-hour": {
            "task": "app.workers.tasks.ingest_youtube",
            "schedule": 3600.0,  # 1 hour
        },
        "ingest-twitter-every-hour": {
            "task": "app.workers.tasks.ingest_twitter",
            "schedule": 3600.0,  # 1 hour
        },
        "fetch-market-data-every-15min": {
            "task": "app.workers.tasks.fetch_market_data",
            "schedule": 900.0,  # 15 minutes
        },
        "compute-signals-every-15min": {
            "task": "app.workers.tasks.compute_all_signals",
            "schedule": 900.0,  # 15 minutes
        },
    }

    CELERY_AVAILABLE = True

except ImportError:
    logger.warning("Celery not installed — scheduled pipeline disabled. Use `python -m app.pipeline` instead.")
    CELERY_AVAILABLE = False
    celery_app = None
