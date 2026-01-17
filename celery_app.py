import os
from celery import Celery
from kombu import Exchange, Queue

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

celery_app = Celery(
    "crypto_price_tracker",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_BACKEND_URL", "redis://localhost:6379/1"),
)

default_exchange = Exchange("default", type="direct")

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    worker_pool="prefork",
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    task_autoretry_for=(Exception,),
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_retry_jitter=True,
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    task_default_queue="default",
    task_queues=(
        Queue("default", exchange=default_exchange, routing_key="default"),
        Queue("prices", exchange=default_exchange, routing_key="prices"),
        Queue("monitoring", exchange=default_exchange,
              routing_key="monitoring"),
    ),
    beat_schedule={
        "update-prices-periodic": {
            "task": "update_all_tokens_task",
            "schedule": 10.0,
            "options": {
                "queue": "prices",
                "expires": 50,
            },
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
