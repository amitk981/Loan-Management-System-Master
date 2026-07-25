from django.conf import settings
from django.db import DatabaseError, connections
from django.db.migrations.executor import MigrationExecutor
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from sfpcl_credit.api import success_response
from sfpcl_credit.shared.encryption import (
    EncryptionConfigurationError,
    FieldEncryption,
)


SERVICE_NAME = "sfpcl-credit-api"


@require_GET
def deployment_live_health(request):
    return JsonResponse({"status": "live"})


def migration_check():
    connection = connections["default"]
    executor = MigrationExecutor(connection)
    return not executor.migration_plan(executor.loader.graph.leaf_nodes())


def critical_configuration_check():
    if not getattr(settings, "SECRET_KEY", None) or not (
        getattr(settings, "JWT_SIGNING_KEY", None)
        or getattr(settings, "SECRET_KEY", None)
    ):
        return False
    try:
        FieldEncryption.encrypt("deployment_readiness", "synthetic")
        FieldEncryption.hash_for_lookup("deployment_readiness", "synthetic")
    except EncryptionConfigurationError:
        return False
    return True


@require_GET
def deployment_ready_health(request):
    try:
        database_check()
        migrations_applied = migration_check()
    except DatabaseError:
        return JsonResponse(
            {"status": "not_ready", "reason": "database_unavailable"},
            status=503,
        )
    if not migrations_applied:
        return JsonResponse(
            {"status": "not_ready", "reason": "migrations_pending"},
            status=503,
        )
    if not critical_configuration_check():
        return JsonResponse(
            {"status": "not_ready", "reason": "configuration_missing"},
            status=503,
        )
    return JsonResponse({"status": "ready"})


def database_check():
    connections["default"].ensure_connection()
    return "ok"


@require_GET
def live_health(request):
    return success_response(
        {
            "status": "live",
            "service": SERVICE_NAME,
        },
        request,
    )


@require_GET
def ready_health(request):
    return success_response(
        {
            "status": "ready",
            "service": SERVICE_NAME,
            "checks": {
                "database": database_check(),
            },
        },
        request,
    )


@require_GET
def deep_health(request):
    return success_response(
        {
            "status": "ok",
            "service": SERVICE_NAME,
            "checks": {
                "database": database_check(),
            },
        },
        request,
    )
