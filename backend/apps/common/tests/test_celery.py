from django.conf import settings
from django.test import TestCase
from grantloop.celery import app as celery_app, BaseTask

# Ensure tasks are imported so Celery registry autodiscover populates them
import apps.common.tasks as common_tasks
import apps.reports.tasks as reports_tasks
import apps.notifications.tasks as notifications_tasks
import apps.payouts.tasks as payouts_tasks


class CeleryProductionConfigurationTests(TestCase):
    """
    Validates Phase 11 Step 7: Production Celery configuration, task registration,
    automatic retry policies, queue routing separation, scheduled beat jobs, and graceful shutdown options.
    """

    def test_task_registration(self):
        """Verify all domain background tasks are discovered and registered in celery_app."""
        registered_tasks = celery_app.tasks.keys()
        self.assertIn("apps.common.tasks.send_email_task", registered_tasks)
        self.assertIn("apps.common.tasks.cleanup_old_notifications", registered_tasks)
        self.assertIn("apps.common.tasks.cleanup_expired_tokens", registered_tasks)
        self.assertIn("apps.common.tasks.recalculate_analytics_cache", registered_tasks)
        self.assertIn("apps.reports.tasks.generate_report_task", registered_tasks)
        self.assertIn("apps.notifications.tasks.dispatch_notification_task", registered_tasks)
        self.assertIn("apps.payouts.tasks.process_payout_task", registered_tasks)

    def test_retry_configuration(self):
        """Verify tasks inheriting from BaseTask enforce automatic exponential retry with jitter."""
        task = celery_app.tasks["apps.common.tasks.send_email_task"]
        self.assertTrue(issubclass(task.__class__, BaseTask))
        self.assertEqual(task.retry_backoff, True)
        self.assertEqual(task.retry_jitter, True)
        self.assertEqual(task.retry_kwargs, {"max_retries": 5})
        self.assertIn(Exception, task.autoretry_for)

    def test_queues_separation(self):
        """Verify queue separation defines default, emails, reports, notifications, and payouts queues."""
        queues = {q.name: q for q in getattr(settings, "CELERY_TASK_QUEUES", ())}
        self.assertIn("default", queues)
        self.assertIn("emails", queues)
        self.assertIn("reports", queues)
        self.assertIn("notifications", queues)
        self.assertIn("payouts", queues)

    def test_task_routing_configuration(self):
        """Verify task routing rules send domain tasks to their designated isolated queues."""
        routes = getattr(settings, "CELERY_TASK_ROUTES", {})
        self.assertEqual(routes.get("apps.common.tasks.send_email_task")["queue"], "emails")
        self.assertEqual(routes.get("apps.reports.tasks.*")["queue"], "reports")
        self.assertEqual(routes.get("apps.notifications.tasks.*")["queue"], "notifications")
        self.assertEqual(routes.get("apps.payouts.tasks.*")["queue"], "payouts")
        self.assertEqual(routes.get("*")["queue"], "default")

    def test_beat_schedule_configuration(self):
        """Verify scheduled beat maintenance jobs are properly configured in Celery beat schedule."""
        schedule = getattr(settings, "CELERY_BEAT_SCHEDULE", {})
        self.assertIn("cleanup-old-notifications-daily", schedule)
        self.assertIn("cleanup-expired-tokens-daily", schedule)
        self.assertIn("recalculate-analytics-cache-periodic", schedule)
        self.assertEqual(schedule["cleanup-old-notifications-daily"]["task"], "apps.common.tasks.cleanup_old_notifications")
        self.assertEqual(schedule["cleanup-expired-tokens-daily"]["task"], "apps.common.tasks.cleanup_expired_tokens")
        self.assertEqual(schedule["recalculate-analytics-cache-periodic"]["task"], "apps.common.tasks.recalculate_analytics_cache")

    def test_graceful_shutdown_and_resilience_settings(self):
        """Verify worker resilience, ack late, prefetch multiplier, and timeout boundaries are configured."""
        self.assertEqual(getattr(settings, "CELERY_WORKER_PREFETCH_MULTIPLIER"), 1)
        self.assertTrue(getattr(settings, "CELERY_TASK_ACKS_LATE"))
        self.assertTrue(getattr(settings, "CELERY_TASK_REJECT_ON_WORKER_LOST"))
        self.assertEqual(getattr(settings, "CELERY_WORKER_MAX_TASKS_PER_CHILD"), 1000)
        self.assertEqual(getattr(settings, "CELERY_TASK_TIME_LIMIT"), 1800)
        self.assertEqual(getattr(settings, "CELERY_TASK_SOFT_TIME_LIMIT"), 1500)

    def test_task_execution_side_effect_free(self):
        """Verify placeholder tasks execute cleanly without mutating database or failing."""
        res_email = common_tasks.send_email_task.apply(args=["donor@example.com", "Receipt", "Thank you!"])
        self.assertTrue(res_email.successful())
        self.assertEqual(res_email.result, "Email sent to donor@example.com")

        res_cleanup = common_tasks.cleanup_old_notifications.apply()
        self.assertTrue(res_cleanup.successful())

        res_report = reports_tasks.generate_report_task.apply(args=["donations", 1, "csv"])
        self.assertTrue(res_report.successful())
        self.assertEqual(res_report.result, "Report donations generated successfully.")
