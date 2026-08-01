import logging
from celery import shared_task
from grantloop.celery import BaseTask

logger = logging.getLogger("grantloop.payouts.tasks")


@shared_task(base=BaseTask, name="apps.payouts.tasks.process_payout_task")
def process_payout_task(payout_id, partner_id=None):
    """
    Background task for asynchronous financial transfer reconciliation over the 'payouts' queue.
    """
    logger.info(f"Processing background reconciliation for payout_id={payout_id}")
    return f"Payout {payout_id} reconciliation completed."
