"""
Production HTTP middlewares for Request Tracing, Security Headers, and API Deprecation.
"""
import logging
import threading
import time
import uuid
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

_thread_local = threading.local()


def get_current_request_id():
    return getattr(_thread_local, "request_id", "N/A")


class RequestIDLogFilter(logging.Filter):
    """
    Logging filter that injects the active thread-local request_id into every log record.
    """
    def filter(self, record):
        record.request_id = get_current_request_id()
        return True


class RequestIDMiddleware(MiddlewareMixin):
    """
    Ensures every HTTP request has an X-Request-ID attached for end-to-end distributed tracing.
    If the client provided X-Request-ID, it is preserved; otherwise, a UUIDv4 is generated.
    """
    def process_request(self, request):
        request_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        request.request_id = request_id
        request.META["HTTP_X_REQUEST_ID"] = request_id
        _thread_local.request_id = request_id

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None) or str(uuid.uuid4())
        response["X-Request-ID"] = request_id
        if hasattr(_thread_local, "request_id"):
            del _thread_local.request_id
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Attaches production-hardened HTTP security policy headers to all responses.
    """
    def process_response(self, request, response):
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault(
            "Permissions-Policy",
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        )
        return response


# Reusable registry of deprecated API route prefix mappings.
# Example entry format:
# "/api/v1/deprecated-route/": {
#     "deprecation": "true",
#     "sunset": "Sat, 01 Nov 2026 00:00:00 GMT",
#     "link": "https://docs.grantloop.example/api/v2-migration"
# }
DEPRECATED_ENDPOINTS = {
    # Prototyped test route entry to verify RFC 8594 header insertion in test harnesses
    "/api/v1/test-deprecated/": {
        "deprecation": "true",
        "sunset": "Sat, 01 Nov 2026 00:00:00 GMT",
        "link": "https://docs.grantloop.example/api/v2-migration"
    }
}


class APIDeprecationMiddleware(MiddlewareMixin):
    """
    Automates insertion of RFC 8594 API deprecation notifications (Deprecation, Sunset, and Link headers)
    for scheduled endpoint sunsets without changing controller business logic.
    """
    def process_response(self, request, response):
        path = request.path
        for prefix, config in DEPRECATED_ENDPOINTS.items():
            if path.startswith(prefix):
                if "deprecation" in config:
                    response["Deprecation"] = config["deprecation"]
                if "sunset" in config:
                    response["Sunset"] = config["sunset"]
                if "link" in config:
                    response["Link"] = f"<{config['link']}>; rel=\"deprecation\""
                break
        return response


monitoring_logger = logging.getLogger("grantloop.monitoring")


class RequestTimingMiddleware(MiddlewareMixin):
    """
    Records HTTP request duration, method, path, and response status code.
    Logs warnings for slow requests (> 500ms).
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        start_time = getattr(request, "start_time", None)
        if start_time is not None:
            duration_ms = (time.time() - start_time) * 1000.0
            response["X-Request-Duration-Ms"] = f"{duration_ms:.2f}"
            method = request.method
            path = request.path
            status_code = response.status_code

            # Log slow requests (> 500ms)
            if duration_ms > 500.0:
                monitoring_logger.warning(
                    f"SLOW_REQUEST_ALERT: {method} {path} status={status_code} completed in {duration_ms:.2f}ms (>500ms threshold)"
                )
            else:
                monitoring_logger.info(
                    f"HTTP_REQUEST: {method} {path} status={status_code} completed in {duration_ms:.2f}ms"
                )
        return response
