"""Shared HTTP API envelope and request helpers.

This is the single production implementation of the standard response
envelope (`docs/source/api-contracts.md` §6). Every backend endpoint —
health and auth — formats responses through the helpers here so the
`success`/`data`/`meta` and error shapes never drift apart.
"""

import json

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone


API_VERSION = "v1"
FORBIDDEN = "FORBIDDEN"
# Compatibility is intentionally confined to this envelope boundary so an older typed domain
# denial cannot leak the retired public code while downstream callers finish migrating.
_LEGACY_PERMISSION_DENIED = "PERMISSION_DENIED"


def public_error_code(code):
    if code == _LEGACY_PERMISSION_DENIED:
        return FORBIDDEN
    return code


def response_meta(request):
    return {
        "request_id": request.headers.get("X-Request-ID"),
        "timestamp": timezone.now().isoformat().replace("+00:00", "Z"),
        "api_version": API_VERSION,
    }


def success_response(data, request):
    return JsonResponse({"success": True, "data": data, "meta": response_meta(request)})


def list_response(data, pagination, request, **resource_metadata):
    return JsonResponse(
        {
            "success": True,
            "data": data,
            "pagination": pagination,
            "meta": response_meta(request),
            **resource_metadata,
        }
    )


def error_response(request, status, code, message, field_errors=None, details=None):
    return JsonResponse(
        {
            "success": False,
            "error": {
                "code": public_error_code(code),
                "message": message,
                "details": details or {},
                "field_errors": field_errors or {},
            },
            "meta": response_meta(request),
        },
        status=status,
    )


def parse_json_body(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError as exc:
        raise ValidationError("Request body must be valid JSON.") from exc
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
    return data


def request_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def request_user_agent(request):
    return request.headers.get("User-Agent", "")
