# GrantLoop Backend API Changelog

All notable structural changes, enhancements, and deprecations across the GrantLoop Backend SaaS platform are documented herein.
Semantic Versioning (`vMAJOR.MINOR.PATCH`) is adhered to across all releases.

---

## [1.0.0] - 2026-08-07

### Added
- **Authentication & Accounts**: JWT-based stateless authentication, RBAC (Role-Based Access Control) for Admins, NGOs, and Donors. Complete user onboarding and profile management.
- **NGO Profiles & Execution Partners**: Extensive verification schemas, document upload pipelines, and execution partner affiliations.
- **Campaigns & Beneficiaries**: Robust fundraising campaign creation workflows linking direct financial targets to granular beneficiary data.
- **Milestones & Documents**: Verifiable milestone tracking ensuring funds are strictly bound to accountable field execution, supported by immutable document evidence.
- **Donations & Payouts**: Idempotent processing of Stripe/Razorpay webhook events, asynchronous payout disbursal tracking, and strict platform zero-balance mathematical validation.
- **Notifications**: Centralized, scalable notification feeds with real-time unread badge calculation and multi-channel routing logic.
- **Analytics & Reports**: High-speed, role-isolated 12-month time-series data aggregation, paginated tabular views, and streaming binary exporters (CSV, Excel `.xlsx`, PDF).
- **Monitoring & Caching**: Prometheus telemetry feeds (`GET /metrics`), Sentry error capture, structural logging architectures, Request-ID distributed tracing, and an aggressive Redis-backed performance layer utilizing dynamic cache invalidation.
- **Docker, Celery & Nginx**: Full containerization via Docker Compose v2. Optimized Nginx reverse proxy serving static/media assets directly, rate-limiting, and routing dynamic traffic to a Gunicorn WSGI cluster. Asynchronous worker fleet executing Celery periodic beats and event-driven tasks.
- **Deployment, Security & Backups**: Automated Let's Encrypt SSL/TLS lifecycles, rigorous HTTP security header enforcement (CSP, HSTS), daily compressed PostgreSQL snapshots with SHA-256 integrity checks, and a comprehensive suite of shell scripts for deployment verification and disaster recovery rollbacks.
- **API Documentation**: Enterprise-grade OpenAPI 3.0 specification generated via `drf-spectacular` and presented through an interactive Swagger UI.

### Deprecated
- **Legacy Unversioned URL Routing**: Direct root API invocations outside the official `/api/v1/` namespace are deprecated. Scheduled for final sunsetting on November 1, 2026.

### Removed
- **Ad-hoc Inline ORM Queries in Controllers**: All database querying strictly migrated to modular domain service layers (`services.py`).
