from django.db import connections
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET


SERVICE_NAME = "sfpcl-credit-api"


def success_response(data, request):
    return JsonResponse(
        {
            "success": True,
            "data": data,
            "meta": {
                "request_id": request.headers.get("X-Request-ID"),
                "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
            },
        }
    )


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
