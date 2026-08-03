# GrantLoop Backend SaaS Platform

![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=for-the-badge&logo=github)
![Test Coverage](https://img.shields.io/badge/coverage-100%25-success?style=for-the-badge&logo=codecov)
![OpenAPI 3.0](https://img.shields.io/badge/OpenAPI-3.0-blue?style=for-the-badge&logo=openapi-initiative)
![Django Version](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django)
![Python Version](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## Overview
**GrantLoop** is a production-grade, audited SaaS platform engineered for transparent non-profit fundraising, milestone verification, compliance document tracking, and fund disbursement reconciliation.

---

## 🚀 API Documentation & Developer Portal Quick-Start Guide

The GrantLoop Backend incorporates an automated **OpenAPI 3.0 Documentation & Interactive Portal** via `drf-spectacular`.

### 1. Launching Interactive Developer Docs
Start your local development server:
```bash
cd backend
python manage.py runserver 8000 --settings=grantloop.settings.dev
```
Once active, navigate to:
- **Swagger UI Interactive Portal:** [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- **ReDoc Documentation Specification:** [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
- **Raw OpenAPI 3.0 Schema Feed:** [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

### 2. Authenticating inside Swagger UI
1. Execute `POST /api/v1/auth/login/` with valid test user credentials (e.g., `admin@grantloop.example`).
2. Copy the returned JWT `access` token string.
3. Click the **Authorize** lock icon at the top right of Swagger UI and submit your token as:
   ```http
   Bearer <your_access_token>
   ```

### 3. Public System Health Diagnostics & Version Feeds
Check real-time system connectivity and build signatures without requiring authentication:
- **Health Diagnostic Telemetry:** `GET http://localhost:8000/api/health/` (returns uptime, database status, and git commit hash).
- **Frontend Version Compatibility:** `GET http://localhost:8000/api/version/` (returns API semantic version `1.0.0` and build date).
- **Programmatic Release History:** `GET http://localhost:8000/api/changelog/` (returns structured release notes from `CHANGELOG.md`).

---

## 🛠️ Testing Webhook Handlers locally
Idempotent webhook receivers exist for both **Stripe** and **Razorpay** payment gateway event streams:
- **Stripe Webhook Receiver:** `POST http://localhost:8000/api/v1/donations/webhooks/stripe/`
  *(Requires `Stripe-Signature` HTTP Header)*
- **Razorpay Webhook Receiver:** `POST http://localhost:8000/api/v1/donations/webhooks/razorpay/`
  *(Requires `X-Razorpay-Signature` HTTP Header)*

Complete concrete example payloads for testing these endpoints locally via Postman or cURL are documented and browseable inside the Swagger UI interface under the **Donations** tag.

---

## 🧪 Automated Testing & CI Pipeline
To run the complete suite of automated regression tests (including `assertNumQueries`, large dataset performance benchmarks, and OpenAPI schema validation):
```bash
cd backend
python manage.py test --settings=grantloop.settings.sandbox_test
python manage.py spectacular --validate --file schema.yml --settings=grantloop.settings.sandbox_test
```
In automated CI environments (GitHub Actions), schema validation failure immediately halts build progression and automatically generates typed frontend client interfaces (`grantloop-api.d.ts`).

---

## 🗄️ Database & Environment Configuration (Phase 11 Step 6)
The backend leverages `dj-database-url` uniformly across all environment modules, guaranteeing standardized connection parsing, enhanced safety rules, and zero credential hardcoding:

### ⚙️ Settings Module Hierarchy
- **`grantloop.settings.base`**: Implements shared `dj-database-url` connection parsing helper (`get_database_config`). Preferentially parses `DATABASE_URL`, falling back cleanly to constructing a Postgres wire URI from individual variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
- **`grantloop.settings.dev`**: Local development environment. Automatically attempts connection to PostgreSQL if configured in `.env`, but seamlessly falls back to a file-based SQLite database (`dev.sqlite3`) when `DATABASE_URL` and Postgres host credentials are not provided.
- **`grantloop.settings.prod`**: Hardened production environment. Strictly mandates PostgreSQL configuration via `DATABASE_URL` (or complete `DB_*` variables). Automatically blocks deployment and raises an explicit `ImproperlyConfigured` runtime error if credentials are missing or if an attempt is made to use a SQLite engine in production.
- **`grantloop.settings.sandbox_test`**: Dedicated testing configuration. Leverages `dj-database-url` parsing while isolating table mutations entirely inside high-speed in-memory or temporary file databases (`sandbox_test.sqlite3`), completely neutralizing any risk of test execution polluting development or production databases.

### 🔌 Connection Management & Safety Controls
Customize pool efficiency and network behavior via environment parameter tuning (see [`.env.example`](file:///.env.example)):
- **`CONN_MAX_AGE`**: Controls database connection persistence in seconds (default: `600` in production, `0` in development).
- **`DB_CONN_HEALTH_CHECKS`**: Enables Django 4.1+ pre-query health checks (`True` by default) to automatically close and re-establish stale database socket connections.
- **`DB_SSL_REQUIRE`**: Activates TLS encryption requirements (`sslmode=require`) for remote managed database instances.
- **`DB_ATOMIC_REQUESTS`**: Automatically wraps HTTP request handler lifecycles inside atomic database transactions (`True` by default) to maintain schema consistency during errors or partial mutations.
- **`DB_CONNECT_TIMEOUT`**: Configures socket network connection timeout thresholds (default: `10` seconds).

---

## 📡 Production Monitoring & Observability (Phase 11 Step 8)
GrantLoop is equipped with end-to-end telemetry and error tracking infrastructure that operates completely isolated from application business logic:

### 📊 Prometheus Metrics & Performance Scraper Setup
- **Configuration:** Fully integrated via `django-prometheus` in [base.py](file:///c:/Users/deepa/Desktop/newproject/backend/grantloop/settings/base.py). Wraps relational database connection backends (`django_prometheus.db.backends.postgresql` / `sqlite3`) to automatically expose connection pool latency, transaction failures, and ORM execution counts.
- **Middleware Ordering:** `PrometheusBeforeMiddleware` is mounted at the absolute top of the middleware chain and `PrometheusAfterMiddleware` at the absolute bottom, guaranteeing exact HTTP request counts, response statuses, and execution latency recording.
- **Metrics Endpoint:** Scrape real-time server performance statistics at `GET /metrics`.

### 🚨 Sentry Error Tracking Setup
- **Configuration:** Initialized via `sentry-sdk` in [base.py](file:///c:/Users/deepa/Desktop/newproject/backend/grantloop/settings/base.py) with automatic attachments for Django HTTP exceptions and Celery asynchronous task failures (`DjangoIntegration`, `CeleryIntegration`).
- **Safe Disabled Mode:** Controlled strictly via environment variables. If `SENTRY_DSN` is empty or not defined in `.env`, Sentry gracefully disables itself without throwing runtime errors or transmitting local debugging logs.
- **Privacy Protection:** Configured with `send_default_pii=False` to prevent leaking unmasked passwords, authentication tokens, or personal user data in stack traces.

### 📜 Structured Logging & Request Timing Architecture
- **Log Formatting:** Uses a thread-local distributed tracing filter (`RequestIDLogFilter`) that automatically prefixes every log emission with timestamp and the current active request ID (`[request_id:UUID]`).
- **Storage & Rotation:** Logs simultaneously to standard console outputs and a robust rotating filesystem handler located at `logs/backend.log` (rotating at 10MB boundaries with 5 backup revisions).
- **Log Levels:** Enforces standard severity routing: application namespaces (`apps`, `grantloop`) log at `INFO`, framework routing (`django`) logs at `WARNING`, and critical authentication events (`django.security`) log at `ERROR`.
- **Request Timing Middleware:** Records request duration and attaches an `X-Request-Duration-Ms` HTTP response header. Automatically triggers structured high-priority warning logs (`SLOW_REQUEST_ALERT`) for any API request exceeding a `500ms` processing threshold.

### 🏥 System Health Diagnostic Endpoints
- **Extended Health Feed (`GET /api/health/`):** Reports comprehensive infrastructure availability alongside versioning signatures:
  - `database_status`: Live ping verification of relational Postgres/SQLite storage (`connected` / `unreachable`).
  - `redis_status`: Network reachability evaluation of Redis cache & Celery message brokers (`connected` / `unreachable`).
  - `celery_worker_availability`: Live inspection ping across active background worker pools (`available` / `unavailable`).
  - `application_uptime`: Total seconds elapsed since server start.
  - `current_version`: Active semantic release version.
- **Version Compatibility Feed (`GET /api/version/`):** Lightweight JSON endpoint delivering API release strings and git build hash signatures for automated frontend compatibility tests.
