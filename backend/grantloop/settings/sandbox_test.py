"""
NOT one of the three real environments (dev/staging/prod). This exists
only so migrations and the test suite can run inside this sandbox, which
has no PostgreSQL server available. Every other setting is identical to
dev — only the database engine differs. Real local development still
uses settings.dev against a real Postgres instance per Architecture
Freeze v1.0; this file should not ship anywhere.
"""
from .dev import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "sandbox_test.sqlite3",  # noqa: F405
        "TEST": {
            "NAME": ":memory:",
        },
    }
}

