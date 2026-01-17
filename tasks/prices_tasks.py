import os
import time
import uuid
from datetime import datetime, timezone
from typing import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed

import redis
import requests
from celery import shared_task
from celery.utils.log import get_task_logger

from app.core.logger import logger
from app.dependencies_sync import get_db
from app.models.token import Token
from app.services.prices_sync import create_http_session
from app.services.prices_sync import create_price_service_for_celery


task_logger = get_task_logger(__name__)

MAX_WORKERS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))
LOCK_TIMEOUT = int(os.getenv("TASK_LOCK_TIMEOUT", "300"))
LOCK_KEY = "celery:lock:update_all_tokens"
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "30"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class RedisLock:
    def __init__(
        self,
        redis_client: redis.Redis,
        lock_key: str,
        timeout: int,
    ):
        self.redis_client = redis_client
        self.lock_key = lock_key
        self.timeout = timeout
        self.task_id = str(uuid.uuid4())
        self.lock_acquired = False

    def __enter__(self):
        self.lock_acquired = self.redis_client.set(
            self.lock_key,
            self.task_id,
            nx=True,
            ex=self.timeout,
        )

        if not self.lock_acquired:
            current_lock = self.redis_client.get(self.lock_key)
            lock_ttl = self.redis_client.ttl(self.lock_key)
            task_logger.warning(
                f"Lock already held by {current_lock}, TTL: {lock_ttl}s"
            )
        else:
            task_logger.info(f"Lock acquired: {self.task_id}")

        return self.lock_acquired

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_acquired:
            try:
                current_lock = self.redis_client.get(self.lock_key)
                if current_lock and current_lock == self.task_id:
                    self.redis_client.delete(self.lock_key)
                    task_logger.info(f"Lock released: {self.task_id}")
            except Exception as e:
                task_logger.error(f"Error releasing lock: {e}")


class TaskStats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.warning = 0
        self.error = 0
        self.start_time = datetime.now(timezone.utc)

    @property
    def duration(self) -> float:
        return (datetime.now(timezone.utc) - self.start_time).total_seconds()

    @property
    def success_rate(self) -> str:
        if self.total == 0:
            return "0%"
        return f"{self.success / self.total * 100:.1f}%"

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "success_rate": self.success_rate,
            "duration_seconds": round(self.duration, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def save_to_redis(self, redis_client: redis.Redis):
        try:
            redis_client.hincrby(
                "metrics:price_updates",
                "total",
                self.total,
            )
            redis_client.hincrby(
                "metrics:price_updates",
                "success",
                self.success,
            )
            redis_client.hincrby(
                "metrics:price_updates",
                "warning",
                self.warning,
            )
            redis_client.hincrby(
                "metrics:price_updates",
                "error",
                self.error,
            )

            redis_client.hset(
                "metrics:last_update",
                mapping={
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration": str(round(self.duration, 2)),
                    "success_rate": self.success_rate,
                    "total": str(self.total),
                    "success": str(self.success),
                },
            )

            redis_client.expire("metrics:price_updates", 2592000)
            redis_client.expire("metrics:last_update", 2592000)

            task_logger.debug("Metrics saved to Redis")
        except Exception as e:
            task_logger.error(f"Error saving metrics to Redis: {e}")


def fetch_token_price(
    http_session: requests.Session,
    token_id: int,
    stats: TaskStats,
) -> dict:
    try:
        task_logger.debug(f"Fetching price for token {token_id}")

        price = create_price_service_for_celery(http_session, token_id)

        time.sleep(RATE_LIMIT_DELAY)

        if price and hasattr(price, "id") and price.id:
            stats.success += 1
            task_logger.info(f"Token {token_id}: Price {price.id} created")
            return {
                "status": "success",
                "token_id": token_id,
                "price_id": price.id,
            }
        else:
            stats.warning += 1
            task_logger.warning(f"Token {token_id}: Price not created")
            return {
                "status": "warning",
                "token_id": token_id,
                "message": "Price object is None or has no ID",
            }

    except requests.Timeout:
        stats.error += 1
        task_logger.error(f"Token {token_id}: Timeout")
        return {
            "status": "error",
            "token_id": token_id,
            "error": "Timeout",
        }
    except Exception as e:
        stats.error += 1
        task_logger.error(f"Token {token_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "token_id": token_id,
            "error": str(e),
        }


def fetch_all_tokens(
    token_ids: Sequence[int],
    stats: TaskStats,
) -> list[dict]:
    http_session = create_http_session()
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_token = {
            executor.submit(
                fetch_token_price,
                http_session,
                token_id,
                stats,
            ): token_id
            for token_id in token_ids
        }

        for future in as_completed(future_to_token):
            token_id = future_to_token[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                stats.error += 1
                task_logger.error(
                    f"Token {token_id}: Unhandled exception: {e}"
                )
                results.append(
                    {
                        "status": "error",
                        "token_id": token_id,
                        "error": str(e),
                    }
                )

    return results


def get_all_token_ids() -> list[int]:
    try:
        with get_db() as db:
            tokens = db.query(Token.id).all()
            token_ids = [t.id for t in tokens]

            if not token_ids:
                task_logger.warning("No tokens found in database")
                return []

            task_logger.info(f"Found {len(token_ids)} tokens to update")
            return token_ids

    except Exception as e:
        task_logger.error(f"Error fetching token IDs: {e}", exc_info=True)
        raise


def _update_all_tokens() -> dict:
    task_logger.info("Starting token price update")

    redis_client = redis.from_url(REDIS_URL, decode_responses=True)

    with RedisLock(redis_client, LOCK_KEY, LOCK_TIMEOUT) as lock_acquired:
        if not lock_acquired:
            return {
                "status": "skipped",
                "reason": "Task already running (lock held)",
            }

        try:
            token_ids = get_all_token_ids()

            if not token_ids:
                return {
                    "status": "completed",
                    "total": 0,
                    "success": 0,
                    "message": "No tokens to update",
                }

            stats = TaskStats()
            stats.total = len(token_ids)

            task_logger.info(f"Processing {stats.total} tokens...")
            results = fetch_all_tokens(token_ids, stats)
            logger.debug(f"Processed {len(results)} results")

            if stats.success > 0:
                stats.save_to_redis(redis_client)

            result = stats.to_dict()
            result["status"] = "completed"

            task_logger.info(f"Update completed: {result}")
            return result

        except Exception as e:
            task_logger.error(f"Update failed: {e}", exc_info=True)
            raise
        finally:
            redis_client.close()


@shared_task(
    name="update_all_tokens_task",
    bind=True,
    queue="prices",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3,
    time_limit=600,
    soft_time_limit=540,
    acks_late=True,
)
def update_all_tokens_task(self):
    task_logger.info(
        "Task started "
        f"[ID: {self.request.id}, "
        f"Retries: {self.request.retries}/{self.max_retries}]"
    )

    try:
        result = _update_all_tokens()

        task_logger.info(f"Task completed Result: {result}")
        return result

    except Exception as e:
        task_logger.error(f"Task failed: {e}", exc_info=True)

        if self.request.retries < self.max_retries:
            retry_countdown = min(10 ** self.request.retries, 300)
            task_logger.info(
                f"Retrying in {retry_countdown}s "
                f"(attempt {self.request.retries + 1}/{self.max_retries})"
            )
            raise self.retry(countdown=retry_countdown, exc=e)
        else:
            task_logger.error(
                f"Task failed permanently after {self.max_retries} retries"
            )
            raise
