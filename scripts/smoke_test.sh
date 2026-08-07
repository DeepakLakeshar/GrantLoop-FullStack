#!/bin/bash
# ==============================================================================
# GrantLoop Smoke Test Script
# ==============================================================================
# Executes lightweight, non-mutating HTTP assertions against the live environment.
# ==============================================================================

set -e

DOMAIN=${1:-"http://localhost"}
echo "=> Initiating Smoke Test against $DOMAIN..."

echo "1. Checking Health Endpoint..."
curl -s -f "$DOMAIN/api/health/" > /dev/null

echo "2. Checking API Version Endpoint..."
curl -s -f "$DOMAIN/api/version/" > /dev/null

echo "3. Checking Swagger Interactive UI Reachability..."
curl -s -f "$DOMAIN/api/docs/" > /dev/null

echo "4. Checking Authentication Endpoint Form Reachability (Login)..."
# Just verifying the endpoint answers to an OPTIONS or GET (if browsable API is on)
# We will just verify HTTP status isn't 500. A 405 Method Not Allowed or 200 OK is fine.
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DOMAIN/api/v1/auth/login/")
if [ "$STATUS" == "500" ] || [ "$STATUS" == "502" ]; then
    echo "ERROR: Auth endpoint returned 50x server error."
    exit 1
fi

echo "5. Checking Static Assets Accessibility..."
# Assumes swagger static files or drf-spectacular are accessible, or just admin css
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$DOMAIN/static/admin/css/base.css")
if [ "$STATUS" == "404" ] || [ "$STATUS" == "500" ]; then
    echo "WARNING: Static asset (admin/css/base.css) returned $STATUS. Did you run collectstatic?"
fi

echo "✅ Smoke test completed successfully. No critical faults detected."
exit 0
