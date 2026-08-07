"""
Enterprise Performance Monitoring & Telemetry Service Layer.
Gathers cache diagnostics, slow request registries, Redis network health, query counters, and server uptime.
"""
import logging
import os
import time
import threading
from typing import Any, Dict, List
from django.conf import settings
from django.db import connection, connections
from apps.cache_utils.services import CacheService

logger = logging.getLogger("grantloop.monitoring")

SERVER_START_TIMESTAMP = time.time()

# Thread-safe real-time metric counters for HTTP requests and SQL query profiling
_perf_lock = threading.Lock()
_request_metrics = {
    "total_count": 0,
    "total_duration_ms": 0.0,
    "slow_endpoints_map": {},  # mapping path -> {"count": int, "total_duration_ms": float, "max_duration_ms": float}
    "query_count": 0,
    "slow_sql_count": 0,
}


class PerformanceTracker:
    @classmethod
    def record_http_request(cls, path: str, duration_ms: float, queries_during_req: int = 0) -> None:
        with _perf_lock:
            _request_metrics["total_count"] += 1
            _request_metrics["total_duration_ms"] += duration_ms
            _request_metrics["query_count"] += queries_during_req

            if duration_ms >= 500.0:
                entry = _request_metrics["slow_endpoints_map"].setdefault(
                    path, {"count": 0, "total_duration_ms": 0.0, "max_duration_ms": 0.0}
                )
                entry["count"] += 1
                entry["total_duration_ms"] += duration_ms
                entry["max_duration_ms"] = max(entry["max_duration_ms"], duration_ms)

    @classmethod
    def record_sql_query(cls, sql: str, duration_ms: float) -> None:
        with _perf_lock:
            _request_metrics["query_count"] += 1
            if duration_ms >= 100.0:
                _request_metrics["slow_sql_count"] += 1
        if duration_ms >= 100.0:
            logger.warning(f"SLOW_SQL_ALERT: Execution time={duration_ms:.2f}ms (>100ms threshold) query='{sql[:150]}'")

    @classmethod
    def get_slow_endpoints(cls) -> List[Dict[str, Any]]:
        with _perf_lock:
            results = []
            for path, data in _request_metrics["slow_endpoints_map"].items():
                avg_ms = round(data["total_duration_ms"] / data["count"], 2) if data["count"] > 0 else 0.0
                results.append({
                    "endpoint": path,
                    "count": data["count"],
                    "average_response_time": f"{avg_ms}ms",
                    "max_response_time": f"{round(data['max_duration_ms'], 2)}ms",
                })
            return sorted(results, key=lambda x: float(x["average_response_time"].replace("ms", "")), reverse=True)

    @classmethod
    def get_summary_metrics(cls) -> Dict[str, Any]:
        with _perf_lock:
            total = _request_metrics["total_count"]
            tot_duration = _request_metrics["total_duration_ms"]
            avg_duration = round(tot_duration / total, 2) if total > 0 else 0.0
            query_cnt = _request_metrics["query_count"]
            slow_sql = _request_metrics["slow_sql_count"]

        cache_stats = CacheService.stats()
        redis_health = check_detailed_redis_health()
        uptime_sec = round(time.time() - SERVER_START_TIMESTAMP, 2)

        return {
            "cache_hit_ratio": f"{cache_stats['hit_ratio_percent']}%",
            "cache_misses": cache_stats["misses"],
            "redis_status": redis_health["status"],
            "average_response_time": f"{avg_duration}ms",
            "slow_endpoints": cls.get_slow_endpoints(),
            "query_count": query_cnt,
            "slow_sql_count": slow_sql,
            "uptime": uptime_sec,
        }

    @classmethod
    def reset_metrics(cls) -> None:
        with _perf_lock:
            _request_metrics["total_count"] = 0
            _request_metrics["total_duration_ms"] = 0.0
            _request_metrics["slow_endpoints_map"].clear()
            _request_metrics["query_count"] = 0
            _request_metrics["slow_sql_count"] = 0


def check_detailed_redis_health() -> Dict[str, Any]:
    """
    Evaluates real-time Redis latency, memory footprint, cache network connectivity, and Celery worker availability.
    """
    result = {
        "status": "unreachable",
        "redis_latency": "N/A",
        "cache_connectivity": "unreachable",
        "memory_usage": "N/A",
        "cache_status": "degraded (fallback mode)",
        "worker_connectivity": "unavailable",
    }

    try:
        from redis import Redis
        redis_url = getattr(settings, "CELERY_BROKER_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
        start_time = time.time()
        r = Redis.from_url(redis_url, socket_timeout=0.5)
        if r.ping():
            latency_ms = round((time.time() - start_time) * 1000.0, 2)
            result["status"] = "connected"
            result["redis_latency"] = f"{latency_ms}ms"
            result["cache_connectivity"] = "connected"
            result["cache_status"] = "healthy"
            
            try:
                info = r.info("memory")
                mem_human = info.get("used_memory_human") or f"{info.get('used_memory', 0)} bytes"
                result["memory_usage"] = str(mem_human)
            except Exception:
                result["memory_usage"] = "unknown"
    except Exception:
        # Graceful fallback for offline dev/sandbox environments
        if not settings.DEBUG and not getattr(settings, "IS_TESTING", True):
            logger.warning("REDIS_HEALTH_ALERT: Primary Redis cluster is unreachable.")
        result["cache_connectivity"] = "connected (locmem fallback)"
        result["cache_status"] = "operational (local cache)"

    # Check worker connectivity
    try:
        from grantloop.celery import app as celery_app
        inspector = celery_app.control.inspect(timeout=0.4)
        stats = inspector.ping()
        if stats and len(stats) > 0:
            result["worker_connectivity"] = f"connected ({len(stats)} workers online)"
    except Exception:
        result["worker_connectivity"] = "offline or testing sandbox"

    return result
