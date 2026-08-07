# GrantLoop Operations Manual

## Managing Services
- **Starting**: `docker compose -f docker-compose.prod.yml up -d`
- **Stopping**: `docker compose -f docker-compose.prod.yml stop`
- **Restarting Everything**: `docker compose -f docker-compose.prod.yml restart`
- **Restarting Backend**: `docker compose -f docker-compose.prod.yml restart backend`

## Application Tasks
- **Running Migrations**: `docker compose -f docker-compose.prod.yml exec backend python manage.py migrate`
- **Collecting Static Files**: `docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput`

## Celery Operations
- **Scaling Workers**: `docker compose -f docker-compose.prod.yml up -d --scale celery_worker=3`
- **Inspecting Queues**: Access the Flower UI at `http://<server>:5555/`.

## Backup & Restore
- **Backup**: `bash scripts/backup_database.sh`
- **Restore**: `bash scripts/restore_database.sh backups/<filename>`

## Monitoring & Troubleshooting
- **Live Logs**: `docker compose -f docker-compose.prod.yml logs -f --tail=100`
- **Container Health**: `bash scripts/verify_deployment.sh`
- **Application Health**: `bash scripts/health_check.sh`
