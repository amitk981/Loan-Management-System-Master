from django.core.exceptions import ValidationError
from django.views.decorators.http import require_GET, require_POST

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.workflows import tasks


@require_GET
def task_list(request):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = tasks.task_inbox(actor=actor, query_params=request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Task inbox query failed validation.",
            tasks.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_POST
def task_reassign(request, task_id):
    return _task_action(
        request,
        task_id,
        lambda actor, payload, request_meta: tasks.reassign_task(
            actor=actor,
            task_id=task_id,
            assigned_to_user_id=payload.get("assigned_to_user_id"),
            request_meta=request_meta,
        ),
        permission_message="You do not have permission to reassign this task.",
        allowed_fields={"assigned_to_user_id"},
    )


@require_POST
def task_comment(request, task_id):
    return _task_action(
        request,
        task_id,
        lambda actor, payload, request_meta: tasks.add_task_comment(
            actor=actor,
            task_id=task_id,
            comment=payload.get("comment"),
            request_meta=request_meta,
        ),
        allowed_fields={"comment"},
    )


@require_POST
def task_block(request, task_id):
    return _task_action(
        request,
        task_id,
        lambda actor, payload, request_meta: tasks.set_task_blocked(
            actor=actor,
            task_id=task_id,
            blocked=True,
            reason=payload.get("reason"),
            request_meta=request_meta,
        ),
        allowed_fields={"reason"},
    )


@require_POST
def task_unblock(request, task_id):
    return _task_action(
        request,
        task_id,
        lambda actor, payload, request_meta: tasks.set_task_blocked(
            actor=actor,
            task_id=task_id,
            blocked=False,
            reason="",
            request_meta=request_meta,
        ),
        allowed_fields=set(),
    )


def _task_action(
    request, task_id, action, permission_message=None, allowed_fields=None
):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        unknown = sorted(set(payload) - set(allowed_fields or ()))
        if unknown:
            raise ValidationError(
                {field: "Unknown field." for field in unknown}
            )
        data = action(
            actor,
            payload,
            {
                "ip_address": request_ip(request),
                "user_agent": request_user_agent(request),
            },
        )
    except tasks.TaskPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            permission_message or "You do not have permission to change this task.",
        )
    except tasks.TaskNotFound:
        return error_response(request, 404, "NOT_FOUND", "Task was not found.")
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Task action failed validation.",
            tasks.validation_field_errors(exc),
        )
    return success_response(data, request)
