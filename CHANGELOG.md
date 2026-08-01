# GrantLoop Backend API Changelog

All notable structural changes, enhancements, and deprecations across the GrantLoop Backend SaaS platform are documented herein.
Semantic Versioning (`vMAJOR.MINOR.PATCH`) is adhered to across all releases.

---

## [v1.0.0] - 2026-08-01

### Added
- **API Documentation & Developer Portal**: Enterprise-grade OpenAPI 3.0 specification generation via `drf-spectacular`.
- **Interactive Document Interfaces**: Live Swagger UI explorer positioned at `/api/docs/` and Redoc presentation at `/api/redoc/`.
- **System Diagnostics & Uptime Telemetry**: Public system health monitor (`/api/health/`), frontend semantic version feed (`/api/version/`), and programmatic evolution log endpoint (`/api/changelog/`).
- **Distributed Tracing & Security Policy**: Automated attachment of universally unique `X-Request-ID` tracing headers and production-hardened HTTP security headers (`X-Content-Type-Options: nosniff`, `Referrer-Policy`, and `Permissions-Policy`).
- **Phase 9 Reports & Export System**: Paginated JSON tabular audit reporting feeds and unpaginated streaming binary file exporters (CSV, Excel `.xlsx` with frozen headers/currency formatting, and ReportLab PDF with numbered footers and branding).
- **Phase 8 Analytics & Financial Dashboard**: Role-isolated interactive analytics feeds, monthly 12-month time-series chart array endpoints, and comparative leaderboards.
- **Phase 7 Payout & Fund Disbursement**: NGO withdrawal request workflows, gateway reference execution tracking, and immutable platform accounting zero-balance validation (`Donations - Refunds - Completed Payouts = Platform Balance`).

### Changed
- **Content Negotiation Handling**: Overridden custom DRF negotiation on report export streaming controllers to prevent file format parameter conflicts (`?format=csv|xlsx|pdf`) from causing HTTP 404 renderer errors.
- **Notification API Read-State Tracking**: Streamlined batch mark-all-as-read state mutations and badge unread counter calculations within domain service layer.

### Deprecated
- **Legacy Unversioned URL Routing**: Direct root API invocations outside the official `/api/v1/` domain namespace are deprecated. Scheduled for final sunsetting on **November 1, 2026**, accompanied by automated RFC 8594 HTTP response notification headers (`Sunset`, `Deprecation`, and `Link`).

### Removed
- **Ad-hoc Inline ORM Queries in Controllers**: Completely excised direct database querying within views and serializers; 100% of business logic and state transitions are strictly restricted to modular domain service layers (`services.py`).
