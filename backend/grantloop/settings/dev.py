from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# In development, fall back to local SQLite database when DATABASE_URL or explicit Postgres host is absent.
_dev_url = os.environ.get("DATABASE_URL")
if not _dev_url and not (os.environ.get("DB_HOST") and os.environ.get("DB_NAME") and os.environ.get("DB_USER")):
    _dev_url = f"sqlite:///{BASE_DIR / 'dev.sqlite3'}"

DATABASES = {
    "default": get_database_config(default_url=_dev_url, conn_max_age=0, ssl_require=False)  # noqa: F405
}