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
