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
]

MIDDLEWARE = [
    "grantloop.middleware.RequestIDMiddleware",
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

# Database — PostgreSQL (Architecture Freeze v1.0, section 15). Configured
# entirely from environment variables; dev/prod settings differ only in
# where those variables come from (.env locally, Secrets Manager in prod),
# never in the engine itself.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "grantloop"),
        "USER": os.environ.get("DB_USER", "grantloop"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
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