"""
NOT one of the three real environments (dev/staging/prod). This exists
only so migrations and the test suite can run inside this sandbox, which
has no PostgreSQL server available. Every other setting is identical to
dev — only the database engine differs. Real local development still
uses settings.dev against a real Postgres instance per Architecture
Freeze v1.0; this file should not ship anywhere.
"""
from .dev import *  # noqa: F401,F403

import dj_database_url  # noqa: E402

_sandbox_db_url = f"sqlite:///{BASE_DIR / 'sandbox_test.sqlite3'}"  # noqa: F405
DATABASES = {
    "default": dj_database_url.parse(
        _sandbox_db_url,
        conn_max_age=0,
        conn_health_checks=False,
    )
}
DATABASES["default"]["TEST"] = {"NAME": ":memory:"}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

