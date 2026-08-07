from django.apps import AppConfig


class CacheUtilsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cache_utils"
    verbose_name = "Enterprise Caching & Performance Utility Infrastructure"

    def ready(self):
        try:
            import apps.cache_utils.signals  # noqa: F401
        except ImportError:
            pass
