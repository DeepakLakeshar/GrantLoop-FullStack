"""
Comprehensive automated unit and integration test suite for Phase 10: API Documentation & Developer Portal.
Verifies OpenAPI schema feeds, Swagger/ReDoc portal accessibility, public health diagnostics, version feeds,
release changelogs, distributed request tracing middleware, and HTTP security policies.
"""
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from grantloop.version import API_RELEASE_DATE, API_TITLE, API_VERSION


class APIDocumentationAndTelemetryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.django_client = Client()

    def test_health_check_endpoint_success(self):
        """
        GET /api/health/ should return HTTP 200 OK without authentication, confirming database connectivity and uptime.
        """
        url = reverse("api-health")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["application"], API_TITLE)
        self.assertEqual(data["version"], API_VERSION)
        self.assertEqual(data["database"], "connected")
        self.assertIn("uptime_seconds", data)
        self.assertIn("git_commit", data)
        self.assertIn("timestamp", data)

    def test_version_endpoint_success(self):
        """
        GET /api/version/ should return lightweight semantic version compatibility string and release date.
        """
        url = reverse("api-version")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["api_version"], API_VERSION)
        self.assertEqual(data["released_at"], API_RELEASE_DATE)
        self.assertIn("build", data)

    def test_changelog_endpoint_success(self):
        """
        GET /api/changelog/ should return programmatic release evolution log from CHANGELOG.md.
        """
        url = reverse("api-changelog")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["version"], API_VERSION)
        self.assertIn("raw_changelog", data)

    def test_openapi_schema_generation_endpoint(self):
        """
        GET /api/schema/ should successfully build and stream the raw OpenAPI 3.0 YAML/JSON specification file.
        """
        url = reverse("schema")
        response = self.client.get(url, {"format": "json"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["openapi"][:3], "3.0")
        self.assertEqual(data["info"]["title"], API_TITLE)
        self.assertEqual(data["info"]["version"], API_VERSION)

    def test_swagger_ui_and_redoc_portal_endpoints(self):
        """
        GET /api/docs/ and GET /api/redoc/ should successfully render interactive interactive developer documentation portals.
        """
        swagger_url = reverse("swagger-ui")
        redoc_url = reverse("redoc")
        res_swagger = self.django_client.get(swagger_url)
        res_redoc = self.django_client.get(redoc_url)
        self.assertEqual(res_swagger.status_code, status.HTTP_200_OK)
        self.assertEqual(res_redoc.status_code, status.HTTP_200_OK)

    def test_request_id_tracing_middleware(self):
        """
        Every HTTP response must automatically emit a universally unique X-Request-ID header for distributed tracing.
        If provided in request by client, it should preserve and reflect the identifier.
        """
        url = reverse("api-health")
        # Test automatic generation
        res1 = self.client.get(url)
        self.assertIn("X-Request-ID", res1.headers)
        self.assertTrue(len(res1.headers["X-Request-ID"]) > 10)

        # Test reflection of custom client tracer ID
        custom_id = "test-distributed-trace-id-9999"
        res2 = self.client.get(url, HTTP_X_REQUEST_ID=custom_id)
        self.assertEqual(res2.headers["X-Request-ID"], custom_id)

    def test_security_headers_middleware(self):
        """
        All responses must contain production security policy headers: X-Content-Type-Options, Referrer-Policy, Permissions-Policy.
        """
        url = reverse("api-version")
        response = self.client.get(url)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("accelerometer=()", response.headers.get("Permissions-Policy", ""))

    def test_api_deprecation_headers_middleware_on_test_route(self):
        """
        Requests directed at route prefixes registered in DEPRECATED_ENDPOINTS must automatically emit RFC 8594 headers.
        """
        # We test against the configured prototype prefix /api/v1/test-deprecated/
        response = self.client.get("/api/v1/test-deprecated/some-resource/")
        # Note: even if route returns 404 from resolver, middleware processes response in reverse stack
        self.assertEqual(response.headers.get("Deprecation"), "true")
        self.assertEqual(response.headers.get("Sunset"), "Sat, 01 Nov 2026 00:00:00 GMT")
        self.assertIn('rel="deprecation"', response.headers.get("Link", ""))
