# GrantLoop Deployment & Infrastructure Configuration

## Overview

Welcome to the GrantLoop Deployment and Infrastructure configuration directory. This folder houses the reference templates, deployment manifests, and architectural documentation necessary to reliably orchestrate the GrantLoop backend across isolated staging and production environments.

The purpose of this directory is to centralize DevOps resources, provide strict environment variable contracts, and document deployment procedures while ensuring infrastructure-as-code (IaC) principles.

## Folder Structure

```text
deployment/
├── README.md               # Enterprise deployment and infrastructure documentation
├── production.env.example  # Master template for production environment variables
└── staging.env.example     # Master template for staging environment variables
```

## Environment Variables

The GrantLoop backend is designed as a 12-factor application, meaning all configuration is injected via environment variables.

### How to Create `.env` files
The application relies on a `.env` file located at the project root for local development or injected directly into the runtime context (via Docker, Kubernetes, or CI/CD pipelines) for deployed environments.

To deploy a new environment:
1. **Copy the appropriate template**:
   ```bash
   # For Staging
   cp deployment/staging.env.example .env

   # For Production
   cp deployment/production.env.example .env
   ```
2. **Replace Placeholder Values**: Open the generated `.env` file and replace all placeholder text (`secure_db_password_here`, etc.) with authentic secrets retrieved from your secure vault.
3. **Verify Settings**: Ensure that boolean values (`DEBUG`) and URLs are formatted correctly according to the inline template comments.

### Required Environment Variables
At a minimum, the deployment environment must supply:
- `DJANGO_SETTINGS_MODULE` (e.g., `grantloop.settings.prod`)
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DATABASE_URL` (PostgreSQL DSN)
- `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- **Integrations**: `SENTRY_DSN`, `STRIPE_SECRET_KEY`, `RAZORPAY_KEY_ID`, etc.

## Secrets Management

### Security Best Practices
1. **Never Commit Secrets**: Environment files containing real credentials (`.env`, `production.env`, etc.) MUST NOT be committed to version control.
2. **Secure Injection**: In production, secrets should be injected using a dedicated secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault, GitHub Secrets, or Docker Swarm Secrets) rather than relying on on-disk files.
3. **Least Privilege**: Database and external API credentials should possess only the minimum permissions necessary for application operation.

### Git Ignore Rules
The project `.gitignore` file enforces that real configuration files are excluded:
```gitignore
# Exclude real environment variables
.env
.env.*
!.env.example
!deployment/*.env.example
```
*Note: The `.env.example` templates inside this deployment directory are safe to commit as they contain placeholder data exclusively.*

## Production vs Staging

- **Production (`production.env.example`)**: Connects to live payment gateways (Live API keys), live databases, production email endpoints (Mailgun/SES), and uses the `production` environment tag in Sentry. `DEBUG` is strictly `False`.
- **Staging (`staging.env.example`)**: Connects to Sandbox/Test payment gateways (Test API keys), isolated staging databases, dummy email endpoints (Mailtrap), and uses the `staging` environment tag in Sentry. `DEBUG` is strictly `False` to maintain parity with production infrastructure behavior.

## Deployment Prerequisites

Before initiating a deployment, ensure the target infrastructure provides:
- **Docker & Docker Compose (v2)** installed.
- Access to a **managed PostgreSQL 16** instance (or deployed via Compose).
- Access to a **Redis 7** instance (or deployed via Compose).
- A reverse proxy (e.g., Nginx, Traefik, or an AWS ALB) handling SSL/TLS termination.
- Valid DNS records pointing to your host matching `ALLOWED_HOSTS`.

## Deployment Examples

### How Docker Compose Consumes Variables
The `docker-compose.yml` file is configured to automatically consume variables from the `.env` file in the project root.

```yaml
services:
  backend:
    build:
      context: ./backend
    env_file:
      - .env
    ports:
      - "8000:8000"
```

### Staging Deployment Execution
```bash
# 1. Prepare Staging Configuration
cp deployment/staging.env.example .env
nano .env  # Inject real staging credentials

# 2. Build and Start the Stack in detached mode
docker compose up --build -d

# 3. Verify Health & Telemetry
curl -X GET http://localhost:8000/api/health/
```

### Production Deployment Execution
```bash
# 1. Prepare Production Configuration
cp deployment/production.env.example .env
nano .env  # Inject real production credentials

# 2. Execute Infrastructure Update
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# 3. Apply Migrations (if applicable)
docker compose exec backend python manage.py migrate

# 4. Collect Static Assets
docker compose exec backend python manage.py collectstatic --noinput
```

## Troubleshooting

- **502 Bad Gateway**: Verify that the backend container is running and healthy (`docker compose ps`). Check Nginx routing configurations.
- **Database Connection Errors**: Verify `DATABASE_URL` credentials and ensure PostgreSQL network visibility from the backend container.
- **CSRF / CORS Errors**: Confirm that `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` exactly match the frontend domains (including `https://`).
- **Static Files 404**: Ensure `python manage.py collectstatic` was successfully executed and volumes are mounted correctly.

## HTTPS Deployment

To ensure secure transit of all financial and user data, the GrantLoop backend requires HTTPS in production.

### Obtaining Certificates
Before starting Nginx with HTTPS enabled, you must obtain a valid certificate from Let's Encrypt. Nginx is configured to serve the ACME challenge on port 80.
```bash
certbot certonly --webroot -w /var/www/certbot -d grantloop.com -d api.grantloop.com
```

### Installing Certificates
Once obtained, the certificates will be stored in `/etc/letsencrypt/live/grantloop.com/`. 
Uncomment the TLS/SSL blocks in `nginx/conf.d/default.conf` so Nginx listens on Port 443 and mounts these files:
```nginx
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/grantloop.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/grantloop.com/privkey.pem;
```

### Renewing Certificates
Run the automated renewal script provided in `deployment/ssl/certbot-renew.sh` via a daily cron job. It automatically verifies expiration and restarts Nginx gracefully without downtime.

### Testing HTTPS & Verifying Redirects
After installing the certificates and starting the stack:
1. Execute `curl -I http://grantloop.com` and verify the `301 Moved Permanently` response pointing to `https://`.
2. Execute `curl -I https://grantloop.com/api/health/` to verify a `200 OK` response over TLS.

### Browser Verification
Navigate to the Swagger UI at `https://api.grantloop.com/api/docs/` in a modern web browser. 
1. Verify the padlock icon indicates a valid connection.
2. Open Developer Tools -> Network -> Headers and verify the presence of `Strict-Transport-Security` and `Content-Security-Policy` headers.

## Deployment Verification & Smoke Testing

Before exposing a new deployment to live traffic, always validate the infrastructure via the provided scripts located in the `scripts/` directory.

### 1. Verification Script
The `verify_deployment.sh` script comprehensively checks the Docker daemon, container statuses, shared volume mounts, and network reachability of critical services (Redis, PostgreSQL, Celery, Nginx).
```bash
bash scripts/verify_deployment.sh
```

### 2. Health Check
The `health_check.sh` script executes a live HTTP ping against the `/api/health/` endpoint, validating that the Django application is not just responding to HTTP, but has active connections to its database and message brokers.
```bash
bash scripts/health_check.sh
```

### 3. Smoke Testing
The `smoke_test.sh` script simulates lightweight user interactions (Swagger UI, authentication endpoints, static asset resolution) to verify that the application layer is functionally intact.
```bash
bash scripts/smoke_test.sh http://grantloop.com
```

### Rollback Checklist
If any of the verification scripts fail post-deployment, initiate a rollback immediately:
1. Identify the failing component via `docker compose logs`.
2. Revert to the previously known good Git commit or image tag.
3. Restart the cluster: `docker compose -f docker-compose.prod.yml up -d`.
4. Run `verify_deployment.sh` again to confirm stability.

## Database Backup & Restore Automation (Phase 13 Step 7)

A robust suite of bash scripts is located in `scripts/` to automate PostgreSQL disaster recovery.

### 1. Backup Schedule
The `scripts/backup_database.sh` script executes a live, non-blocking `pg_dump` of the PostgreSQL container, compresses it using gzip, and calculates a SHA-256 checksum for cryptographic integrity.
**Recommendation**: Run this via a daily cron job (e.g., at 03:00 AM UTC).

### 2. Cleanup Policy (Retention)
The `scripts/cleanup_backups.sh` script automatically purges stale archives to prevent disk exhaustion. It strictly enforces:
- **30 Days Daily Retention**: Keeps the last 30 daily backups.
- **12 Months Monthly Retention**: Keeps the 1st backup of each month for one year.
**Recommendation**: Run this sequentially after the backup script.

### 3. Verification Procedure
To ensure a backup is viable before attempting a restore, execute the verification script. It validates file existence, checksum matches, and scans the GZIP archive for the internal PostgreSQL EOF marker.
```bash
bash scripts/verify_backup.sh backups/grantloop_backup_YYYY-MM-DD_HH-MM.sql.gz
```

### 4. Restore Procedure
To execute a bare-metal restoration of a backup archive over the live production database:
```bash
bash scripts/restore_database.sh backups/grantloop_backup_YYYY-MM-DD_HH-MM.sql.gz
```
*Note: This script strictly requires interactive user confirmation, forces active connections to terminate, drops the existing schema, and recreates it before importing the archive.*
