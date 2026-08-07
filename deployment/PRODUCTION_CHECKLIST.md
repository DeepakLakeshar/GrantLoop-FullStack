# GrantLoop Production Readiness Checklist

This checklist acts as the final gatekeeper prior to exposing the backend to live user traffic.

### Infrastructure
- [ ] OS is updated with latest security patches.
- [ ] Docker and Docker Compose v2 are installed and functioning.
- [ ] UFW/iptables firewall configured (Only ports 80, 443, and 22 open).

### Networking
- [ ] Domain A records successfully resolve to the server IP.
- [ ] Docker internal bridge network `grantloop-network` isolated properly.

### HTTPS
- [ ] Let's Encrypt certificates generated and mounted.
- [ ] HTTP-to-HTTPS automatic 301 redirection verified.

### Database
- [ ] Persistent `postgres_data` volume created.
- [ ] Strong password generated for `DATABASE_URL`.
- [ ] Initial database schema migrations executed successfully.

### Redis & Celery
- [ ] Redis persistent volume `redis_data` mounted.
- [ ] Celery worker boots and successfully connects to Redis.
- [ ] Celery beat boots and registers periodic tasks.

### Monitoring & Logging
- [ ] Sentry DSN active and capturing test exceptions.
- [ ] Prometheus scraping `GET /metrics` accurately.
- [ ] Gunicorn and Nginx logging outputting to rotational directories.

### Backups
- [ ] Automated database `pg_dump` cron configured.
- [ ] Media volume snapshot automation verified.

### CI/CD & Security
- [ ] `.env` securely injected via deployment pipeline.
- [ ] No `.env` secrets leaked into GitHub/GitLab repositories.

### Documentation
- [ ] All deployment markdown files (`README.md`, `SECURITY_CHECKLIST.md`) reviewed and accessible to DevOps engineers.
- [ ] Secret rotation strategy documented in emergency runbooks.

### Final Verification
- [ ] Execute `GET /api/health/` and verify `database_status: connected` and `celery_status: available`.
