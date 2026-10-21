import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery_app = Celery(
    "video_pipeline",
    broker=broker_url,
    backend=result_backend,
    include=["src.infrastructure.queue.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
    task_track_started=True
)

@celery_app.task(name="health_check_task")
def health_check_task():
    return {"status": "celery worker healthy"}
