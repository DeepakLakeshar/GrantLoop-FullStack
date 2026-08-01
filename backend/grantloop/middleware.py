"""
Production HTTP middlewares for Request Tracing, Security Headers, and API Deprecation.
"""
import uuid
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    """
    Ensures every HTTP request has an X-Request-ID attached for end-to-end distributed tracing.
    If the client provided X-Request-ID, it is preserved; otherwise, a UUIDv4 is generated.
    """
    def process_request(self, request):
        request_id = request.META.get("HTTP_X_REQUEST_ID") or str(uuid.uuid4())
        request.request_id = request_id
        request.META["HTTP_X_REQUEST_ID"] = request_id

    def process_response(self, request, response):
        request_id = getattr(request, "request_id", None) or str(uuid.uuid4())
        response["X-Request-ID"] = request_id
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
