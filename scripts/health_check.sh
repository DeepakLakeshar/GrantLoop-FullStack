#!/bin/bash
# ==============================================================================
# GrantLoop Backend Health Check Script
# ==============================================================================
# Validates the application-level health metrics provided by the telemetry feed.
# ==============================================================================

set -e

HEALTH_URL="http://localhost/api/health/"
echo "=> Executing HTTP GET $HEALTH_URL..."

# Fetch HTTP status code and response body
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$HEALTH_URL")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS:" | awk -F':' '{print $2}')
JSON_BODY=$(echo "$RESPONSE" | sed -e 's/HTTP_STATUS:.*//g')

if [ "$HTTP_STATUS" != "200" ]; then
    echo "ERROR: Health endpoint returned HTTP $HTTP_STATUS"
    exit 1
fi

echo "=> Verifying Telemetry Properties..."

if ! echo "$JSON_BODY" | grep -q '"database_status": "connected"'; then
    echo "ERROR: Database is not connected."
    exit 1
fi

if ! echo "$JSON_BODY" | grep -q '"redis_status": "connected"'; then
    echo "ERROR: Redis is not connected."
    exit 1
fi

if ! echo "$JSON_BODY" | grep -q '"celery_worker_availability": "available"'; then
    echo "ERROR: Celery worker is unavailable."
    exit 1
fi

if ! echo "$JSON_BODY" | grep -q '"application_uptime"'; then
    echo "ERROR: Application uptime metric is missing."
    exit 1
fi

echo "✅ Application health check passed. Telemetry is fully connected."
exit 0
