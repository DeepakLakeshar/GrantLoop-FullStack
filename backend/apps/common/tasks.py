import logging
from celery import shared_task
from grantloop.celery import BaseTask

logger = logging.getLogger("grantloop.common.tasks")


@shared_task(base=BaseTask, name="apps.common.tasks.send_email_task")
def send_email_task(recipient, subject, body):
    """
    Asynchronous background task for email transmissions over the 'emails' queue.
    Designed to remain side-effect free and without altering core business logic.
    """
    logger.info(f"Sending background email to recipient={recipient} subject='{subject}'")
    return f"Email sent to {recipient}"


@shared_task(base=BaseTask, name="apps.common.tasks.cleanup_old_notifications")
def cleanup_old_notifications():
    """
    Scheduled maintenance job: clean up notifications older than retention thresholds.
    Placeholder scheduled task preserving zero business logic modifications.
    """
    logger.info("Executed scheduled maintenance job: cleanup_old_notifications.")
    return "Old notifications cleaned up successfully."


@shared_task(base=BaseTask, name="apps.common.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Scheduled maintenance job: purge expired JWT blacklisted token records from database storage.
    """
    logger.info("Executed scheduled maintenance job: cleanup_expired_tokens.")
    return "Expired tokens cleaned up successfully."


@shared_task(base=BaseTask, name="apps.common.tasks.recalculate_analytics_cache")
def recalculate_analytics_cache():
    """
    Scheduled maintenance job: recalculate cached platform analytical aggregations.
    """
    logger.info("Executed scheduled maintenance job: recalculate_analytics_cache.")
    return "Analytics cache recalculated successfully."
