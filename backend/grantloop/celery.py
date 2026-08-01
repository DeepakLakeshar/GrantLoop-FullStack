import logging
import os
from celery import Celery, Task
from celery.signals import task_failure, task_prerun, task_retry, worker_ready

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grantloop.settings.dev")

app = Celery("grantloop")

# Configure broker and result backend primarily from REDIS_URL or environment variable overrides
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL", redis_url)
app.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", redis_url)
app.conf.enable_utc = True
app.conf.timezone = "UTC"

# Using a string here means the worker doesn't have to serialize the configuration object to child processes.
# Namespace 'CELERY' means all celery-related configuration keys should have a `CELERY_` prefix in Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


class BaseTask(Task):
    """
    Reusable production base task class providing automatic exponential backoff retry behaviors
    with jitter to prevent thundering herd scenarios during transient database or network outages.
    """

    autoretry_for = (Exception,)
    retry_backoff = True
    retry_jitter = True
    retry_kwargs = {"max_retries": 5}


# -----------------------------------------------------------------------------
# Structured Celery Event Logging Strategy (Worker Startup, Executions, Failures, Retries)
# -----------------------------------------------------------------------------
logger = logging.getLogger("grantloop.celery")


@worker_ready.connect
def handle_worker_ready(sender=None, **kwargs):
    """Log structured announcement when Celery worker finishes initializing queues."""
    logger.info(
        f"CELERY_WORKER_READY: Worker {sender} fully initialized and monitoring asynchronous queues."
    )


@task_prerun.connect
def handle_task_prerun(sender=None, task_id=None, task=None, args=None, kwargs=None, **other):
    """Log structured audit trail right before a background task executes."""
    logger.info(
        f"CELERY_TASK_EXECUTE: Initiating execution for task_name={sender.name} task_id={task_id} args={args} kwargs={kwargs}"
    )


@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, args=None, kwargs=None, **other):
    """Log structured diagnostic failure trace when a task raises an unhandled exception after exhausting retries."""
    logger.error(
        f"CELERY_TASK_FAILURE: Task task_name={sender.name} task_id={task_id} failed with exception={exception}",
        exc_info=True,
    )


@task_retry.connect
def handle_task_retry(sender=None, task_id=None, reason=None, einfo=None, **kwargs):
    """Log structured warning whenever automatic exponential retry logic is triggered."""
    logger.warning(
        f"CELERY_TASK_RETRY: Task task_name={sender.name} task_id={task_id} scheduling retry due to reason={reason}"
    )
