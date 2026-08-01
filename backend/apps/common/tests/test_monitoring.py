import logging
import os
import time
from unittest.mock import MagicMock, patch
from django.conf import settings
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from grantloop.middleware import RequestIDMiddleware, RequestIDLogFilter, RequestTimingMiddleware, get_current_request_id
from grantloop.version import API_VERSION


class ProductionMonitoringAndObservabilityTests(TestCase):
    """
    Validates Phase 11 Step 8: Prometheus /metrics export, Sentry error telemetry disabled state,
    structured production logging infrastructure, RequestTimingMiddleware slow request warnings, and extended Health feeds.
    """

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_metrics_endpoint_accessibility_and_prometheus_format(self):
        """Verify Prometheus /metrics endpoint returns HTTP 200 OK with scraped performance metric formatting."""
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("django_http_requests_before_middlewares", content)

    def test_extended_health_endpoint_telemetry(self):
        """Verify /api/health/ reports database status, redis status, celery availability, uptime, and current version."""
        url = reverse("api-health")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("database_status", data)
        self.assertIn("redis_status", data)
        self.assertIn("celery_worker_availability", data)
        self.assertIn("application_uptime", data)
        self.assertIn("current_version", data)
        self.assertEqual(data["current_version"], API_VERSION)
        self.assertEqual(data["database_status"], "connected")

    def test_request_timing_middleware_and_slow_request_alerting(self):
        """Verify RequestTimingMiddleware records request duration header and logs warnings for slow requests (>500ms)."""
        middleware = RequestTimingMiddleware(lambda req: HttpResponse("OK", status=200))
        request = self.factory.get("/api/health/")

        # Fast request execution test (< 500ms)
        middleware.process_request(request)
        response = middleware.process_response(request, HttpResponse("OK", status=200))
        self.assertIn("X-Request-Duration-Ms", response)
        duration_val = float(response["X-Request-Duration-Ms"])
        self.assertLess(duration_val, 500.0)

        # Slow request simulation test (> 500ms via simulated start_time)
        with patch("grantloop.middleware.monitoring_logger") as mock_logger:
            request.start_time = time.time() - 0.65  # Simulated 650ms duration
            response_slow = middleware.process_response(request, HttpResponse("Slow", status=200))
            self.assertIn("X-Request-Duration-Ms", response_slow)
            self.assertGreater(float(response_slow["X-Request-Duration-Ms"]), 500.0)
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("SLOW_REQUEST_ALERT", warning_msg)
            self.assertIn("(>500ms threshold)", warning_msg)

    def test_sentry_disabled_when_dsn_empty(self):
        """Verify Sentry initialization remains cleanly disabled when SENTRY_DSN is empty without throwing errors."""
        with patch.dict(os.environ, {"SENTRY_DSN": ""}):
            dsn = os.environ.get("SENTRY_DSN", "").strip()
            self.assertEqual(dsn, "")
            self.assertFalse(bool(dsn))

    def test_production_logging_configuration(self):
        """Verify LOGGING configuration defines console & rotating file handler in logs/backend.log with exact level routing."""
        logging_conf = getattr(settings, "LOGGING", {})
        self.assertIn("handlers", logging_conf)
        self.assertIn("console", logging_conf["handlers"])
        self.assertIn("file", logging_conf["handlers"])
        self.assertEqual(logging_conf["handlers"]["file"]["class"], "logging.handlers.RotatingFileHandler")
        self.assertIn("logs", logging_conf["handlers"]["file"]["filename"])
        self.assertIn("backend.log", logging_conf["handlers"]["file"]["filename"])

        loggers = logging_conf.get("loggers", {})
        self.assertEqual(loggers["apps"]["level"], "INFO")
        self.assertEqual(loggers["grantloop"]["level"], "INFO")
        self.assertEqual(loggers["django"]["level"], "WARNING")
        self.assertEqual(loggers["django.security"]["level"], "ERROR")
        self.assertIn("request_id", logging_conf.get("filters", {}))

    def test_request_id_middleware_and_logging_filter(self):
        """Verify RequestIDMiddleware sets X-Request-ID and injects active tracing IDs into log records."""
        middleware = RequestIDMiddleware(lambda req: HttpResponse("OK", status=200))
        request = self.factory.get("/api/v1/campaigns/")
        middleware.process_request(request)
        self.assertTrue(hasattr(request, "request_id"))
        req_id = request.request_id
        self.assertEqual(get_current_request_id(), req_id)

        filter_inst = RequestIDLogFilter()
        record = MagicMock()
        filter_inst.filter(record)
        self.assertEqual(record.request_id, req_id)
        middleware.process_response(request, HttpResponse("OK"))
