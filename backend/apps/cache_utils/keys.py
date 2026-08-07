"""
Centralized cache key builders, namespaces, versioning, and TTL constants for GrantLoop Enterprise Caching.
"""

# =============================================================================
# TTL Constants (in seconds)
# =============================================================================
TTL_30_SECONDS = 30
TTL_1_MINUTE = 60
TTL_5_MINUTES = 300
TTL_15_MINUTES = 900
TTL_1_HOUR = 3600

# =============================================================================
# Cache Namespaces
# =============================================================================
NAMESPACE_CAMPAIGNS = "campaigns"
NAMESPACE_ANALYTICS = "analytics"
NAMESPACE_REPORTS = "reports"
NAMESPACE_DASHBOARD = "dashboard"
NAMESPACE_LEADERBOARDS = "leaderboards"
NAMESPACE_NOTIFICATIONS = "notifications"
NAMESPACE_USERS = "users"
NAMESPACE_BENEFICIARIES = "beneficiaries"
NAMESPACE_MILESTONES = "milestones"
NAMESPACE_PAYOUTS = "payouts"
NAMESPACE_PARTNERS = "partners"

CACHE_VERSION = "v1"


class CacheKeyBuilder:
    """
    Enterprise-grade deterministic cache key generator ensuring collision-free namespace routing.
    """
    @staticmethod
    def build_key(namespace: str, identifier: str, version: str = CACHE_VERSION) -> str:
        """
        Constructs a structured cache key: grantloop:{version}:{namespace}:{identifier}
        """
        return f"grantloop:{version}:{namespace}:{identifier}"

    @staticmethod
    def pattern(namespace: str, version: str = CACHE_VERSION) -> str:
        """
        Returns a wildcard glob pattern matching all keys inside a namespace.
        """
        return f"grantloop:{version}:{namespace}:*"

    @classmethod
    def campaign_detail(cls, campaign_id: str) -> str:
        return cls.build_key(NAMESPACE_CAMPAIGNS, f"detail:{campaign_id}")

    @classmethod
    def campaign_list(cls, query_hash: str = "default") -> str:
        return cls.build_key(NAMESPACE_CAMPAIGNS, f"list:{query_hash}")

    @classmethod
    def analytics_dashboard(cls, role: str, user_id: str) -> str:
        return cls.build_key(NAMESPACE_DASHBOARD, f"{role}:{user_id}")

    @classmethod
    def analytics_leaderboards(cls, limit: int = 10) -> str:
        return cls.build_key(NAMESPACE_LEADERBOARDS, f"top:{limit}")

    @classmethod
    def reports_data(cls, report_type: str, user_id: str, params_hash: str) -> str:
        return cls.build_key(NAMESPACE_REPORTS, f"{report_type}:{user_id}:{params_hash}")

    @classmethod
    def notifications_user(cls, user_id: str) -> str:
        return cls.build_key(NAMESPACE_NOTIFICATIONS, f"list:{user_id}")
