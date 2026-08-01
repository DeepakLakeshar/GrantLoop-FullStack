import os

from .base import *  # noqa: F401,F403

# -----------------------------------------------------------------------------
# Production Settings
# -----------------------------------------------------------------------------

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# -----------------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------------

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

X_FRAME_OPTIONS = "DENY"

# -----------------------------------------------------------------------------
# Static Files
# -----------------------------------------------------------------------------

STATIC_ROOT = BASE_DIR / "staticfiles"

# -----------------------------------------------------------------------------
# WhiteNoise
# -----------------------------------------------------------------------------

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

# -----------------------------------------------------------------------------
# Production Database — dj-database-url PostgreSQL Enforcement (Phase 11 Step 6)
# -----------------------------------------------------------------------------
from django.core.exceptions import ImproperlyConfigured  # noqa: E402

_prod_db_url = os.environ.get("DATABASE_URL")
if not _prod_db_url:
    _db_name = os.environ.get("DB_NAME")
    _db_user = os.environ.get("DB_USER")
    _db_password = os.environ.get("DB_PASSWORD")
    _db_host = os.environ.get("DB_HOST")
    _db_port = os.environ.get("DB_PORT", "5432")
    if _db_name and _db_user and _db_password and _db_host:
        _prod_db_url = f"postgres://{_db_user}:{_db_password}@{_db_host}:{_db_port}/{_db_name}"
    else:
        raise ImproperlyConfigured(
            "DATABASE_URL or complete PostgreSQL environment variables (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST) "
            "must be explicitly configured in production. Never fall back to SQLite in production."
        )

_prod_db = get_database_config(  # noqa: F405
    default_url=_prod_db_url,
    conn_max_age=int(os.environ.get("CONN_MAX_AGE", 600)),
    ssl_require=os.environ.get("DB_SSL_REQUIRE", "False").lower() == "true",
)

if not _prod_db or "sqlite" in str(_prod_db.get("ENGINE", "")).lower() or "sqlite" in str(_prod_db.get("NAME", "")).lower():
    raise ImproperlyConfigured("SQLite database engine is strictly forbidden in production. PostgreSQL is required.")

DATABASES = {
    "default": _prod_db
}