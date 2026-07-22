from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, parse_json_body, success_response
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.recovery.modules.recovery_workflow import (
    RecoveryConflict,
    RecoveryNotFound,
    RecoveryPermissionDenied,
    RecoveryValidation,
    api_complete_recovery_action,
    api_create_non_payment_note,
    api_initiate_recovery_action,
    api_submit_non_payment_note,
)
from sfpcl_credit.recovery.modules.recovery_decision import (
    RecoveryDecisionConflict,
    RecoveryDecisionNotFound,
    RecoveryDecisionPermissionDenied,
    RecoveryDecisionValidation,
    api_create_recovery_decision,
)


@require_http_methods(["POST"])
def recovery_decision_create(request, default_case_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_create_recovery_decision(
                actor=actor,
                default_case_id=default_case_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except RecoveryDecisionValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Recovery Decision failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Recovery Decision failed validation.",
            {"body": exc.messages[0]},
        )
    except RecoveryDecisionPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Configured recovery decision authority is required.",
        )
    except RecoveryDecisionNotFound:
        return error_response(
            request,
            404,
            "NOT_FOUND",
            "The default or approval case was not found.",
        )
    except RecoveryDecisionConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def recovery_action_create(request, recovery_decision_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_initiate_recovery_action(
                actor=actor,
                recovery_decision_id=recovery_decision_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except RecoveryValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Recovery Action initiation failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Recovery Action initiation failed validation.",
            {"body": exc.messages[0]},
        )
    except RecoveryPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Company Secretary recovery initiation authority is required.",
        )
    except RecoveryNotFound:
        return error_response(
            request,
            404,
            "NOT_FOUND",
            "The Recovery Decision was not found or is inaccessible.",
        )
    except RecoveryConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def recovery_action_complete(request, recovery_action_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_complete_recovery_action(
                actor=actor,
                recovery_action_id=recovery_action_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except RecoveryValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Recovery Action completion failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Recovery Action completion failed validation.",
            {"body": exc.messages[0]},
        )
    except RecoveryPermissionDenied:
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "Company Secretary recovery completion authority is required.",
        )
    except RecoveryNotFound:
        return error_response(
            request,
            404,
            "NOT_FOUND",
            "The Recovery Action was not found or is inaccessible.",
        )
    except RecoveryConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def non_payment_note_create(request, default_case_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_create_non_payment_note(
                actor=actor,
                default_case_id=default_case_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except RecoveryValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Non-Payment Note failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Non-Payment Note failed validation.",
            {"body": exc.messages[0]},
        )
    except RecoveryPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Non-Payment Note creation permission is required."
        )
    except RecoveryNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The default case was not found or is inaccessible."
        )
    except RecoveryConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))


@require_http_methods(["POST"])
def non_payment_note_submit(request, non_payment_note_id):
    actor, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        return success_response(
            api_submit_non_payment_note(
                actor=actor,
                non_payment_note_id=non_payment_note_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except RecoveryValidation as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Non-Payment Note submission failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Non-Payment Note submission failed validation.",
            {"body": exc.messages[0]},
        )
    except RecoveryPermissionDenied:
        return error_response(
            request, 403, "FORBIDDEN", "Non-Payment Note submission permission is required."
        )
    except RecoveryNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "The Non-Payment Note was not found or is inaccessible."
        )
    except RecoveryConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
