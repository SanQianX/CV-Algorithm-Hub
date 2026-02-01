"""Task Orchestrator - Celery Application"""
import os
from celery import Celery

# Configure Celery
redis_host = os.getenv("CVHUB_REDIS_HOST", "redis")
redis_port = os.getenv("CVHUB_REDIS_PORT", "6379")

broker_url = f"redis://{redis_host}:{redis_port}/0"
result_backend = f"redis://{redis_host}:{redis_port}/0"

app = Celery("task_orchestrator", broker=broker_url, backend=result_backend)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)

# Import tasks
# from src.task_orchestrator import tasks

if __name__ == "__main__":
    app.start()
