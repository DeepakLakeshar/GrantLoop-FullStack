# GrantLoop Operational Runbook

This runbook outlines standard operating procedures for managing, recovering, and diagnosing the GrantLoop backend production cluster.

## 🚀 Deployment Procedure
1. Verify CI/CD pipeline tests and security scans have passed.
2. SSH into the production host.
3. Pull the latest codebase or Docker images.
4. Run `docker compose -f docker-compose.prod.yml up --build -d`.
5. Execute schema migrations if applicable: `docker compose -f docker-compose.prod.yml exec backend python manage.py migrate`.
6. Run deployment verification script: `bash scripts/verify_deployment.sh`.
7. Run health check script: `bash scripts/health_check.sh`.

## ⏪ Rollback Procedure
If the deployment verification or health check fails:
1. Revert to the previously known good Git commit or Docker image tag.
2. Run `docker compose -f docker-compose.prod.yml up --build -d`.
3. If database schema was corrupted or migrated forward incompatibly, restore the database from the pre-deployment backup using `pg_restore`.
4. Validate rollback health via `scripts/smoke_test.sh`.

## 🔄 Restarting Services
- **Full Cluster Restart**: `docker compose -f docker-compose.prod.yml restart`
- **Restart Backend Application**: `docker compose -f docker-compose.prod.yml restart backend`
- **Restart Background Workers**: `docker compose -f docker-compose.prod.yml restart celery_worker celery_beat`

## 🕵️ Investigating Unhealthy Containers
If `verify_deployment.sh` flags an unhealthy container:
1. Inspect the container state: `docker inspect --format='{{json .State.Health}}' <container_name>`
2. View the last 100 log lines: `docker compose -f docker-compose.prod.yml logs --tail=100 <service_name>`
3. Connect inside the container for manual inspection: `docker exec -it <container_name> /bin/bash`

## 📉 Common Operational Incidents
- **Celery Worker Deadlock**: Usually caused by massive exports hitting memory limits. Fix: Scale workers (`--scale celery_worker=3`) and restart.
- **Nginx 502 Bad Gateway**: Means Gunicorn crashed or is rebooting. Check Gunicorn logs (`backend/logs/gunicorn_error.log`).
- **Redis OOM (Out of Memory)**: If session caching or Celery queues exceed RAM. Fix: Restart Redis container and review caching strategy.

## 📂 Log Locations
- **Aggregated Docker Logs**: `docker compose -f docker-compose.prod.yml logs`
- **Nginx Access**: `docker exec grantloop_prod_nginx cat /var/log/nginx/access.log`
- **Gunicorn Diagnostics**: `backend/logs/gunicorn_error.log`
- **Django Application Logs**: `backend/logs/backend.log` (Rotational handler).

## 📊 Monitoring Dashboard
- **Prometheus Metrics Feed**: `GET /metrics`
- **System Health Diagnostics**: `GET /api/health/`
- **Celery Queue Inspection**: Access the Flower Dashboard internally via Port `5555`.

## 🚑 Recovery Steps
1. Immediate triage: Restart the crashed component.
2. If unresolved, check disk space (`df -h`). Full disks crash PostgreSQL and Redis immediately.
3. If database is irrecoverable, initiate backup decryption and `pg_restore`.

## 🌋 Extended Disaster Recovery (Phase 13 Step 7)

### Target Objectives
- **Recovery Point Objective (RPO)**: 24 Hours (Maximum allowable data loss window, defined by daily snapshot frequency).
- **Recovery Time Objective (RTO)**: < 1 Hour (Maximum allowable downtime during recovery execution).

### 1. Complete Server Loss
If the entire host goes down (hardware failure or datacenter outage):
1. Provision a new server instance.
2. Clone the repository and inject the `.env` backup.
3. Download the latest encrypted backup archive from off-site S3 storage to the `backups/` directory.
4. Run `docker compose -f docker-compose.prod.yml up -d`.
5. Execute `bash scripts/restore_database.sh backups/<downloaded_file.sql.gz>`.
6. Repoint DNS `A` records to the new server IP.
7. Run `certbot certonly` to issue new SSL certificates.

### 2. PostgreSQL Corruption / Accidental Deletion
If a rogue script or compromised account drops critical tables:
1. Identify the exact time of the breach.
2. Locate the closest preceding backup file in `backups/`.
3. Verify integrity: `bash scripts/verify_backup.sh backups/<file.sql.gz>`.
4. Restore immediately: `bash scripts/restore_database.sh backups/<file.sql.gz>`.

### 3. Redis Corruption
Because Redis is utilized purely as an ephemeral message broker and cache layer (not source-of-truth storage):
1. Run `docker compose stop redis`.
2. Delete the corrupted persistent volume: `docker volume rm <project>_redis_data` (Check exact volume name via `docker volume ls`).
3. Restart the cluster: `docker compose -f docker-compose.prod.yml up -d redis backend celery_worker celery_beat`. All session data and queued tasks will be lost, but the system will self-heal immediately.
