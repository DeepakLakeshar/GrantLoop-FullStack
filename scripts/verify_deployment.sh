#!/bin/bash
# ==============================================================================
# GrantLoop Production Deployment Verification Script
# ==============================================================================
# Executes a strict verification of the Docker orchestration environment to 
# ensure all services are healthy before exposing the cluster to live traffic.
# ==============================================================================

set -e

echo "=> 1. Verifying Docker Daemon..."
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not reachable."
    exit 1
fi

echo "=> 2. Verifying Containers Running..."
CONTAINERS=("grantloop_prod_postgres" "grantloop_prod_redis" "grantloop_prod_backend" "grantloop_prod_celery_worker" "grantloop_prod_celery_beat" "grantloop_prod_flower" "grantloop_prod_nginx")
for container in "${CONTAINERS[@]}"; do
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "ERROR: Container $container is not running."
        exit 1
    fi
done

echo "=> 3. Verifying Container Health Statuses..."
for container in "grantloop_prod_postgres" "grantloop_prod_redis" "grantloop_prod_backend"; do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "unhealthy")
    if [ "$STATUS" != "healthy" ]; then
        echo "ERROR: Container $container is reporting as $STATUS."
        exit 1
    fi
done

echo "=> 4. Verifying Celery Worker & Beat..."
if ! docker exec grantloop_prod_backend celery -A grantloop inspect ping >/dev/null 2>&1; then
    echo "ERROR: Celery worker is not responding to pings."
    exit 1
fi
echo "Celery Beat is running (container verified)."

echo "=> 5. Verifying Flower Reachability..."
if ! curl -s -f http://localhost:5555 >/dev/null; then
    echo "WARNING: Flower dashboard is not reachable on port 5555. Check firewall or VPN if expected."
fi

echo "=> 6. Verifying Nginx Responding..."
if ! curl -s -f -I http://localhost >/dev/null; then
    echo "ERROR: Nginx is not responding on Port 80."
    exit 1
fi

echo "=> 7. Verifying SSL Certificates Directory..."
if ! ls -d /etc/letsencrypt/live/ >/dev/null 2>&1; then
    echo "WARNING: /etc/letsencrypt/live/ not accessible or does not exist. SSL may not be configured."
fi

echo "=> 8. Verifying Shared Volumes (Static/Media)..."
if ! docker exec grantloop_prod_nginx ls -l /usr/share/nginx/html/static >/dev/null 2>&1; then
    echo "ERROR: Static files volume not mounted in Nginx."
    exit 1
fi
if ! docker exec grantloop_prod_nginx ls -l /usr/share/nginx/html/media >/dev/null 2>&1; then
    echo "ERROR: Media files volume not mounted in Nginx."
    exit 1
fi

echo "✅ All deployment infrastructure checks passed successfully."
exit 0
