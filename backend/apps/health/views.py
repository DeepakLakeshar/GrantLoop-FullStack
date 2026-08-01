"""
Public Read-only API Controllers for System Health Telemetry, Version Checking, and Release Changelogs.
"""
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.db import connections
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, OpenApiTypes, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from grantloop.version import API_RELEASE_DATE, API_TITLE, API_VERSION

SERVER_START_TIME = time.time()


def get_git_commit_hash() -> str:
    """
    Safely resolves the local git commit hash without executing external subprocesses.
    Returns 'unknown' if repository metadata is unavailable.
    """
    try:
        root_dir = settings.BASE_DIR.parent
        git_head = root_dir / ".git" / "HEAD"
        if git_head.exists():
            content = git_head.read_text().strip()
            if content.startswith("ref:"):
                ref_path = root_dir / ".git" / content.split("ref: ")[1].strip()
                if ref_path.exists():
                    return ref_path.read_text().strip()[:7]
            else:
                return content[:7]
    except Exception:
        pass
    return "unknown"


def check_db_connection() -> str:
    """
    Tests active relational database connectivity with an explicit lightweight ping.
    """
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1;")
        return "connected"
    except Exception:
        return "unreachable"


class HealthCheckView(APIView):
    """
    Public systemic diagnostic endpoint returning uptime telemetry, build signatures, and database connectivity.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Health"],
        summary="Public System Health Diagnostic & Telemetry Feed",
        description="Returns live system uptime status, database connectivity checks, environment indicators, and application git hash signatures without exposing sensitive infrastructure credentials.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="System diagnostic report generated successfully.",
                examples=[
                    OpenApiExample(
                        "Health Report",
                        value={
                            "status": "ok",
                            "application": API_TITLE,
                            "version": API_VERSION,
                            "environment": os.environ.get("DJANGO_ENV", "development"),
                            "timestamp": "2026-08-01T20:55:00Z",
                            "uptime_seconds": 3600.5,
                            "git_commit": "c4d12a9",
                            "database": "connected",
                        },
                    )
                ],
            ),
            500: OpenApiResponse(description="System database is unreachable or internal failure occurred."),
        },
    )
    def get(self, request):
        db_status = check_db_connection()
        status_code = 200 if db_status == "connected" else 500
        payload = {
            "status": "ok" if status_code == 200 else "degraded",
            "application": API_TITLE,
            "version": API_VERSION,
            "environment": os.environ.get("DJANGO_ENV", "development"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(time.time() - SERVER_START_TIME, 2),
            "git_commit": get_git_commit_hash(),
            "database": db_status,
        }
        return Response(payload, status=status_code)


class VersionView(APIView):
    """
    Lightweight public version compatibility feed designed specifically for instantaneous frontend release verification.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Health"],
        summary="Frontend Release Version Compatibility Feed",
        description="Returns lightweight API semantic versioning string, build git commit hash, and official release date.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Version compatibility metadata.",
                examples=[
                    OpenApiExample(
                        "Version Feed",
                        value={
                            "api_version": API_VERSION,
                            "build": "c4d12a9",
                            "released_at": API_RELEASE_DATE,
                        },
                    )
                ],
            )
        },
    )
    def get(self, request):
        return Response(
            {
                "api_version": API_VERSION,
                "build": get_git_commit_hash(),
                "released_at": API_RELEASE_DATE,
            },
            status=200,
        )


class ChangelogView(APIView):
    """
    Programmatic API release evolution feed reading from repository CHANGELOG.md.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Health"],
        summary="Programmatic API Evolution Release Changelog Feed",
        description="Returns structured semantic release logs, feature introductions, behavioral changes, and deprecation timeline records from repository CHANGELOG.md.",
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description="Changelog retrieved.",
                examples=[
                    OpenApiExample(
                        "Changelog Output",
                        value={
                            "version": API_VERSION,
                            "released_at": API_RELEASE_DATE,
                            "summary": "Full Phase 10 OpenAPI 3.0 Documentation & Developer Portal Release.",
                        },
                    )
                ],
            )
        },
    )
    def get(self, request):
        changelog_path = settings.BASE_DIR.parent / "CHANGELOG.md"
        content = (
            changelog_path.read_text(encoding="utf-8")
            if changelog_path.exists()
            else "CHANGELOG.md is currently initializing."
        )
        return Response(
            {
                "version": API_VERSION,
                "released_at": API_RELEASE_DATE,
                "raw_changelog": content,
            },
            status=200,
        )
