"""
Enterprise API response caching decorators supporting custom namespaces, vary header routing,
ETag cryptographic content hashing, HTTP 304 Not Modified negotiation, and integrated metrics.
"""
import hashlib
import json
from functools import wraps
from typing import Any, Callable, List, Optional
from django.http import HttpResponse, HttpResponseNotModified
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from apps.cache_utils.keys import CacheKeyBuilder
from apps.cache_utils.services import CacheService


def cached_endpoint(
    timeout: int,
    namespace: str = "endpoint",
    vary_headers: Optional[List[str]] = None,
    vary_on_user: bool = True,
    enable_etag: bool = True,
):
    """
    Enterprise API response caching decorator supporting custom namespace routing, ETag hashing,
    HTTP 304 Not Modified negotiation, vary headers, and CacheService metrics integration.
    Works transparently on both function-based controllers and class-based APIView methods.
    """
    if vary_headers is None:
        vary_headers = ["Accept", "Accept-Language"]

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(*args: Any, **kwargs: Any) -> Any:
            # Resolve request object across standalone function or class view self call signatures
            request = args[1] if len(args) > 1 and hasattr(args[1], "method") else args[0]

            if not hasattr(request, "method") or request.method != "GET":
                return view_func(*args, **kwargs)

            # Build deterministic cache identifier from URI path, query string, headers, and user identity
            key_parts = [request.path, request.GET.urlencode()]
            for header in sorted(vary_headers):
                val = request.META.get(f"HTTP_{header.upper().replace('-', '_')}", "")
                key_parts.append(f"{header}:{val}")

            if vary_on_user and hasattr(request, "user") and request.user and request.user.is_authenticated:
                key_parts.append(f"user:{getattr(request.user, 'pk', str(request.user))}")
            elif vary_on_user:
                key_parts.append("user:anonymous")

            identifier = hashlib.md5(("|".join(key_parts)).encode("utf-8")).hexdigest()
            cache_key = CacheKeyBuilder.build_key(namespace, f"resp:{identifier}")

            # Inspect cache storage
            cached_item = CacheService.get(cache_key)
            if cached_item is not None:
                etag = cached_item.get("etag")
                if enable_etag and etag and request.META.get("HTTP_IF_NONE_MATCH") == etag:
                    resp_304 = HttpResponseNotModified()
                    resp_304["ETag"] = etag
                    resp_304["X-Cache-Status"] = "HIT"
                    return resp_304

                if cached_item.get("is_drf") and "data" in cached_item:
                    hit_resp = Response(
                        data=cached_item["data"],
                        status=cached_item.get("status_code", 200),
                        content_type=cached_item.get("content_type", "application/json"),
                    )
                else:
                    hit_resp = HttpResponse(
                        content=cached_item.get("content", b""),
                        status=cached_item.get("status_code", 200),
                        content_type=cached_item.get("content_type", "application/json"),
                    )

                for k, v in cached_item.get("headers", {}).items():
                    hit_resp[k] = v
                hit_resp["X-Cache-Status"] = "HIT"
                if etag:
                    hit_resp["ETag"] = etag
                hit_resp.setdefault("Cache-Control", f"max-age={timeout}, public")
                return hit_resp

            # Cache miss: execute controller logic
            response = view_func(*args, **kwargs)

            # Avoid caching streaming responses (document downloads, CSV/XLSX exports)
            if getattr(response, "streaming", False):
                return response

            status_code = getattr(response, "status_code", 500)
            if status_code == 200:
                is_drf = hasattr(response, "data")
                content = None
                data_val = None
                etag_val = None

                if is_drf:
                    data_val = response.data
                    if enable_etag:
                        try:
                            stable_str = json.dumps(data_val, sort_keys=True, default=str)
                            etag_val = f'"{hashlib.md5(stable_str.encode("utf-8")).hexdigest()}"'
                        except Exception:
                            pass
                else:
                    content = getattr(response, "content", b"")
                    if enable_etag and content:
                        etag_val = f'"{hashlib.md5(content).hexdigest()}"'

                if etag_val and request.META.get("HTTP_IF_NONE_MATCH") == etag_val:
                    response["ETag"] = etag_val
                    response["X-Cache-Status"] = "MISS"
                    return HttpResponseNotModified()

                if etag_val:
                    response["ETag"] = etag_val
                response["X-Cache-Status"] = "MISS"
                response["Cache-Control"] = f"max-age={timeout}, public"

                headers_dict = {}
                if hasattr(response, "items"):
                    for k, v in response.items():
                        if k.lower() not in ("x-cache-status", "set-cookie", "etag"):
                            headers_dict[k] = v

                cache_payload = {
                    "is_drf": is_drf,
                    "status_code": status_code,
                    "content_type": getattr(response, "content_type", "application/json"),
                    "headers": headers_dict,
                    "etag": etag_val,
                }
                if is_drf:
                    cache_payload["data"] = data_val
                else:
                    cache_payload["content"] = content

                CacheService.set(
                    cache_key,
                    cache_payload,
                    timeout=timeout,
                )

            return response
        return _wrapped_view
    return decorator
