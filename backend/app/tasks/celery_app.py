from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ai_appointment_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        "send-reminders-every-5m": {
            "task": "send_appointment_reminders",
            "schedule": 300.0,
        },
        "run-winback-campaigns-daily": {
            "task": "run_winback_campaigns",
            "schedule": 86400.0,
        },
    },
)

celery_app.autodiscover_tasks(['app.tasks'])

