from django.db import connections
from django.views.decorators.http import require_GET

from sfpcl_credit.api import success_response


SERVICE_NAME = "sfpcl-credit-api"


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
