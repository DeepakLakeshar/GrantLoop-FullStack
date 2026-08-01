"""
Base settings shared by dev/prod. Never imported directly by manage.py —
DJANGO_SETTINGS_MODULE points at settings.dev or settings.prod, both of
which import * from this file.
"""
from datetime import timedelta
from pathlib import Path
import os
from grantloop.version import API_VERSION, API_TITLE

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "insecure-dev-key-override-in-prod")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "django_prometheus",
    # local apps
    "apps.accounts",
    "apps.campaigns",
    "apps.ngo_profiles",
    "apps.execution_partners",
    "apps.milestones",
    "apps.campaign_updates",
    "apps.documents",
    "apps.donations",
    "apps.notifications",
    "apps.beneficiaries",
    "apps.payouts",
    "apps.analytics",
    "apps.reports",
    "apps.health",
    "apps.common",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "grantloop.middleware.RequestIDMiddleware",
    "grantloop.middleware.RequestTimingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "grantloop.middleware.SecurityHeadersMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "grantloop.middleware.APIDeprecationMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "grantloop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "grantloop.wsgi.application"

# Database — PostgreSQL & dj-database-url Configuration (Phase 11 Step 6).
# Common database parsing supporting DATABASE_URL over individual DB_* variables.
import dj_database_url

def get_database_config(default_url=None, conn_max_age=0, ssl_require=False):
    """
    Parses database configuration using dj-database-url everywhere.
    Supports DATABASE_URL (preferred), falling back to building a URL from
    individual DB_* environment variables, or default_url if neither exists.
    Configures CONN_MAX_AGE, health checks, SSL support, connection timeout, and atomic requests.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_host = os.environ.get("DB_HOST")
        db_port = os.environ.get("DB_PORT", "5432")
        if db_name and db_user and db_host:
            url = f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        elif default_url:
            url = default_url

    if not url:
        return None

    max_age = int(os.environ.get("CONN_MAX_AGE", conn_max_age))
    health_checks = os.environ.get("DB_CONN_HEALTH_CHECKS", "True").lower() == "true"
    ssl = ssl_require or os.environ.get("DB_SSL_REQUIRE", "False").lower() == "true"

    config = dj_database_url.parse(
        url,
        conn_max_age=max_age,
        conn_health_checks=health_checks,
        ssl_require=ssl,
    )

    # Configure atomic requests (DRF best practice for transaction safety)
    config["ATOMIC_REQUESTS"] = os.environ.get("DB_ATOMIC_REQUESTS", "True").lower() == "true"

    # Configure connection timeout for PostgreSQL engines and wrap with django_prometheus
    if config.get("ENGINE") == "django.db.backends.postgresql":
        options = config.setdefault("OPTIONS", {})
        options.setdefault("connect_timeout", int(os.environ.get("DB_CONNECT_TIMEOUT", 10)))
        config["ENGINE"] = "django_prometheus.db.backends.postgresql"
    elif config.get("ENGINE") == "django.db.backends.sqlite3":
        config["ENGINE"] = "django_prometheus.db.backends.sqlite3"

    return config


_base_fallback = f"postgres://{os.environ.get('DB_USER', 'grantloop')}:{os.environ.get('DB_PASSWORD', '')}@{os.environ.get('DB_HOST', 'localhost')}:{os.environ.get('DB_PORT', '5432')}/{os.environ.get('DB_NAME', 'grantloop')}"
DATABASES = {
    "default": get_database_config(default_url=_base_fallback, conn_max_age=0)
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom User (ADR-003: AbstractUser, no Profile table) — must be set
# before the first migration; this is that first migration.
AUTH_USER_MODEL = "accounts.User"

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# --- SimpleJWT --- (Architecture Freeze v1.0, section 6: 15min access /
# 7day refresh, rotation + blacklist)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# --- CORS ---
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173"
).split(",")
CORS_ALLOW_CREDENTIALS = True

# --- Email (password reset) — console backend for dev; SES wiring is a
# later infrastructure phase, not part of Backend Phase 1's scope. ---
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@grantloop.example"

# --- Password reset token signing (stateless, per the v1.1 auth
# architecture doc — no token table) ---
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24  # 24 hours, matches frontend copy

# --- OpenAPI 3.0 API Documentation & Portal via drf-spectacular ---
SPECTACULAR_SETTINGS = {
    "TITLE": API_TITLE,
    "DESCRIPTION": (
        "Production-grade OpenAPI 3.0 documentation for the GrantLoop SaaS platform.\n\n"
        "### Authentication & Authorization\n"
        "All secured endpoints require JWT Bearer Authentication (`Authorization: Bearer <access_token>`) "
        "or OAuth2 Bearer tokens for third-party application integrations.\n\n"
        "**Example Fake Test JWT Access Token:**\n"
        "`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6ImFkbWluQGdyYW50bG9vcC5leGFtcGxlIiwicm9sZSI6IkFETUlOIn0.fake_signature_hash_do_not_use_in_production`\n\n"
        "#### Step-by-Step JWT Token Refresh Flow:\n"
        "1. **Login:** Submit credentials via `POST /api/v1/auth/login/` to obtain an Access Token (15-min lifetime) and Refresh Token (7-day lifetime).\n"
        "2. **Authorize API Calls:** Attach header `Authorization: Bearer <access_token>` to all protected operations.\n"
        "3. **Token Expiry & Rotation:** When access token expires, submit `POST /api/v1/auth/refresh/` with `{\"refresh\": \"<your_refresh_token>\"}`.\n"
        "4. **Blacklisting:** The old refresh token is immediately blacklisted upon rotation; store and utilize the new returned token pair.\n\n"
        "### Role-Based Access Control (RBAC)\n"
        "Endpoints enforce strict tenancy and role isolation between **Admin**, **NGO**, **Donor**, and **Public** personas.\n\n"
        "### Pagination & Dynamic Filtering\n"
        "Standard JSON endpoint feeds utilize DRF PageNumberPagination (`?page=1&page_size=20`), returning structured wrappers (`count`, `next`, `previous`, `results`).\n"
        "Dynamic query filters are supported across search terms, ordering fields, status flags, date ranges, and UUID relationships.\n\n"
        "### Rate Limits & Throttles\n"
        "Intensive endpoints (such as streaming report file exports via `?format=csv|xlsx|pdf`) are protected by `ReportExportThrottle` (`100 requests/minute`).\n"
        "If exceeded, endpoints return HTTP `429 Too Many Requests` accompanied by the explicit `Retry-After: <seconds>` HTTP header indicating cooldown pause duration.\n\n"
        "### API Versioning & Deprecation Policy\n"
        "Current Stable Version: `v1` (`/api/v1/`). When future versions (`/api/v2/`) are introduced, legacy versions coexist with a guaranteed **6-month deprecation window** before sunsetting.\n"
        "During this period, responses automatically emit standard RFC 8594 `Deprecation`, `Sunset`, and `Link` HTTP response headers to notify consuming client SDKs."
    ),
    "VERSION": API_VERSION,
    "CONTACT": {"name": "GrantLoop Engineering Team", "email": "dev@grantloop.example"},
    "LICENSE": {"name": "Commercial SaaS License", "url": "https://grantloop.example/terms"},
    "SERVERS": [
        {"url": "http://localhost:8000", "description": "Local Development Sandbox Server"},
        {"url": "https://staging-api.grantloop.example", "description": "Staging Environment"},
        {"url": "https://api.grantloop.example", "description": "Production SaaS Platform"},
    ],
    "TAGS": [
        {"name": "Authentication", "description": "JWT token obtain, rotation, blacklist, logout, and stateless password reset workflows."},
        {"name": "Accounts", "description": "User account registration, profile queries, and persona management endpoints."},
        {"name": "Campaigns", "description": "Fundraising campaign creation, multi-tier approval lifecycles, updates, and public project discovery listings."},
        {"name": "Beneficiaries", "description": "Beneficiary eligibility onboarding, compliance verification, and bulk CSV file ingestion."},
        {"name": "Donations", "description": "Multi-currency donor contributions, payment intent confirmation, receipt rendering, and idempotent gateway webhooks."},
        {"name": "Notifications", "description": "In-app real-time alerts, automated delivery hooks, unread counters, and batch read state updates."},
        {"name": "Payouts", "description": "NGO withdrawal request lifecycles, gateway payout disbursement execution, and audit-ready balance tracking."},
        {"name": "Milestones", "description": "Project milestone creation, verification evidence submission review, and escrow tranche fund release tracking."},
        {"name": "Execution Partners", "description": "On-the-ground project implementation NGO partner registration and campaign associations."},
        {"name": "Analytics", "description": "Role-isolated interactive financial dashboards, time-series chart array feeds, and comparative performance leaderboards."},
        {"name": "Reports", "description": "Paginated tabular audit reporting feeds and raw streaming file export generator pipelines (CSV, Excel, and PDF)."},
        {"name": "Documents", "description": "Secure compliance file upload management, cryptographic verification status tracking, and binary stream retrieval."},
        {"name": "Health", "description": "Public system uptime monitoring, git build verification, database connectivity health diagnostics, and release changelog feeds."},
    ],
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "SORT_TAGS": False,
    "SCHEMA_PATH_PREFIX": r"/api/(?:v1/)?",
    "SECURITY_SCHEMES": {
        "jwtAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Provide a valid JWT access token obtained via POST /api/v1/auth/login/.",
        },
        "oauth2Auth": {
            "type": "oauth2",
            "description": "OAuth2 Security Scheme for third-party developer integration apps.",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://auth.grantloop.example/oauth/authorize/",
                    "tokenUrl": "https://auth.grantloop.example/oauth/token/",
                    "scopes": {
                        "read": "Read-only access to campaigns and public reports.",
                        "write": "Write access to donations and campaign updates.",
                    },
                },
                "clientCredentials": {
                    "tokenUrl": "https://auth.grantloop.example/oauth/token/",
                    "scopes": {
                        "webhooks": "Read and trigger event webhook notification feeds.",
                    },
                },
            },
        },
    },
}

# =============================================================================
# Celery Production Configuration & Background Jobs (Phase 11 Step 7)
# =============================================================================
from celery.schedules import crontab  # noqa: E402
from kombu import Exchange, Queue  # noqa: E402

# Broker & Result Backend URLs configured primarily via REDIS_URL
_default_redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", _default_redis_url)
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", _default_redis_url)

# Task Serialization & Content Handling
CELERY_TASK_TRACK_STARTED = True
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Timezone & UTC enforcement
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "UTC"

# Task Execution Time Boundaries (Hard & Soft limits)
CELERY_TASK_TIME_LIMIT = int(os.environ.get("CELERY_TASK_TIME_LIMIT", 1800))       # 30 minutes hard kill
CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get("CELERY_TASK_SOFT_TIME_LIMIT", 1500))  # 25 minutes soft signal

# Queue Separation & Routing Design
CELERY_TASK_DEFAULT_QUEUE = "default"
CELERY_TASK_QUEUES = (
    Queue("default", Exchange("default", type="direct"), routing_key="default"),
    Queue("emails", Exchange("emails", type="direct"), routing_key="emails"),
    Queue("reports", Exchange("reports", type="direct"), routing_key="reports"),
    Queue("notifications", Exchange("notifications", type="direct"), routing_key="notifications"),
    Queue("payouts", Exchange("payouts", type="direct"), routing_key="payouts"),
)

CELERY_TASK_ROUTES = {
    "apps.common.tasks.send_email_task": {"queue": "emails", "routing_key": "emails"},
    "apps.reports.tasks.*": {"queue": "reports", "routing_key": "reports"},
    "apps.notifications.tasks.*": {"queue": "notifications", "routing_key": "notifications"},
    "apps.payouts.tasks.*": {"queue": "payouts", "routing_key": "payouts"},
    "*": {"queue": "default", "routing_key": "default"},
}

# Scheduled Maintenance Jobs (Celery Beat Schedule)
CELERY_BEAT_SCHEDULE = {
    "cleanup-old-notifications-daily": {
        "task": "apps.common.tasks.cleanup_old_notifications",
        "schedule": crontab(hour=2, minute=0),  # Daily at 02:00 AM UTC
    },
    "cleanup-expired-tokens-daily": {
        "task": "apps.common.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=3, minute=0),  # Daily at 03:00 AM UTC
    },
    "recalculate-analytics-cache-periodic": {
        "task": "apps.common.tasks.recalculate_analytics_cache",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
}

# Worker Graceful Shutdown & Resilience Options
CELERY_WORKER_PREFETCH_MULTIPLIER = int(os.environ.get("CELERY_WORKER_PREFETCH_MULTIPLIER", 1))
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.environ.get("CELERY_WORKER_MAX_TASKS_PER_CHILD", 1000))

# =============================================================================
# Production Error Monitoring (Sentry) — Phase 11 Step 8
# =============================================================================
import sentry_sdk  # noqa: E402
from sentry_sdk.integrations.django import DjangoIntegration  # noqa: E402
from sentry_sdk.integrations.celery import CeleryIntegration  # noqa: E402

_sentry_dsn = os.environ.get("SENTRY_DSN", "").strip()
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
        send_default_pii=False,
    )

# =============================================================================
# Production Logging Infrastructure & Request Tracing — Phase 11 Step 8
# =============================================================================
import logging  # noqa: E402

_logs_dir = BASE_DIR / "logs"
os.makedirs(_logs_dir, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {
            "()": "grantloop.middleware.RequestIDLogFilter",
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] [request_id:%(request_id)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "filters": ["request_id"],
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(_logs_dir / "backend.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "verbose",
            "filters": ["request_id"],
        },
    },
    "loggers": {
        "apps": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "grantloop": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django": {
            "handlers": ["console", "file"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}