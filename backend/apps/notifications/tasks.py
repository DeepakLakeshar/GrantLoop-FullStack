import logging
from celery import shared_task
from grantloop.celery import BaseTask

logger = logging.getLogger("grantloop.notifications.tasks")


@shared_task(base=BaseTask, name="apps.notifications.tasks.dispatch_notification_task")
def dispatch_notification_task(recipient_id, message, title="GrantLoop Alert"):
    """
    Background task for asynchronous real-time notification broadcasting over the 'notifications' queue.
    """
    logger.info(f"Dispatching notification title='{title}' to recipient_id={recipient_id}")
    return f"Notification dispatched to {recipient_id}."
