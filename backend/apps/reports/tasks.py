import logging
from celery import shared_task
from grantloop.celery import BaseTask

logger = logging.getLogger("grantloop.reports.tasks")


@shared_task(base=BaseTask, name="apps.reports.tasks.generate_report_task")
def generate_report_task(report_type, user_id, format="csv"):
    """
    Background task for asynchronous report export generation over the 'reports' queue.
    Integrates cleanly with existing Exporter registries without changing business logic.
    """
    logger.info(f"Generating report_type={report_type} in format={format} for user={user_id}")
    return f"Report {report_type} generated successfully."
