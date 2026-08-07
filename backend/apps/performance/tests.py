from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.cache_utils.services import CacheService
from apps.performance.services import PerformanceTracker, check_detailed_redis_health

User = get_user_model()


class PerformanceMetricsTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@grantloop.org",
            password="admin_secret_password_123!",
            role="admin",
            is_active=True
        )
        self.donor_user = User.objects.create_user(
            email="donor@grantloop.org",
            password="donor_secret_password_123!",
            role="donor",
            is_active=True
        )
        self.url = reverse("performance-metrics")
        PerformanceTracker.reset_metrics()
        CacheService.reset_stats()

    def test_performance_endpoint_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_performance_endpoint_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.donor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_performance_endpoint_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        # Populate dummy performance data
        PerformanceTracker.record_http_request("/api/v1/campaigns/", duration_ms=120.0, queries_during_req=2)
        PerformanceTracker.record_http_request("/api/v1/reports/", duration_ms=650.0, queries_during_req=15)
        PerformanceTracker.record_sql_query("SELECT * FROM campaigns;", duration_ms=150.0)
        
        # Make a cache interaction
        CacheService.set("test_key", "test_val", 60)
        CacheService.get("test_key")  # hit
        CacheService.get("missing_key")  # miss

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertIn("cache_hit_ratio", data)
        self.assertIn("cache_misses", data)
        self.assertIn("redis_status", data)
        self.assertIn("average_response_time", data)
        self.assertIn("slow_endpoints", data)
        self.assertIn("query_count", data)
        self.assertIn("uptime", data)

        self.assertEqual(data["cache_misses"], 1)
        self.assertTrue(len(data["slow_endpoints"]) >= 1)
        self.assertEqual(data["slow_endpoints"][0]["endpoint"], "/api/v1/reports/")
        self.assertEqual(data["query_count"], 18)  # 2 + 15 + 1

    def test_detailed_redis_health(self):
        health = check_detailed_redis_health()
        self.assertIn("status", health)
        self.assertIn("redis_latency", health)
        self.assertIn("cache_connectivity", health)
        self.assertIn("memory_usage", health)
        self.assertIn("cache_status", health)
        self.assertIn("worker_connectivity", health)
