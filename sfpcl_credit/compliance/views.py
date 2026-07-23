from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, success_response
from sfpcl_credit.compliance.modules import compliance_control_tracker as tracker
from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
from sfpcl_credit.compliance.modules.section186_tracker import Section186TrackerModule
from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
    NbfcPrincipalBusinessTestModule,
)
from sfpcl_credit.identity.modules import http_auth


def _actor(request):
    actor, response = http_auth.authenticated_user(request)
    if actor is not None:
        request.compliance_actor = actor
    return actor, response


def _error(request, exc, *, audit_denial=False):
    from django.core.exceptions import ObjectDoesNotExist
    if isinstance(exc, tracker.ComplianceDenied) or isinstance(exc, PermissionError):
        if audit_denial:
            from sfpcl_credit.api import request_ip, request_user_agent
            from sfpcl_credit.identity.models import AuditLog

            AuditLog.objects.create(
                actor_user=getattr(request, "compliance_actor", None),
                actor_type="user",
                action="compliance.access.denied",
                entity_type="statutory_tracker_endpoint",
                new_value_json={"method": request.method, "path": request.path},
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            )
        return error_response(request, 403, "FORBIDDEN", "Compliance authority is required.")
    if isinstance(exc, tracker.ComplianceMissing):
        return error_response(request, 404, "NOT_FOUND", "Compliance record was not found.")
    if isinstance(exc, ObjectDoesNotExist):
        return error_response(request, 404, "NOT_FOUND", "Compliance record was not found.")
    if isinstance(exc, tracker.ComplianceConflict) or isinstance(exc, ValueError):
        return error_response(request, 409, "COMPLIANCE_CONFLICT", str(exc))
    if isinstance(exc, tracker.ComplianceInvalid):
        return error_response(request, 400, "VALIDATION_ERROR", "Compliance request failed validation.", exc.field_errors)
    if isinstance(exc, ValidationError):
        return error_response(request, 400, "VALIDATION_ERROR", "Request body failed validation.")
    raise exc


@require_http_methods(["GET", "POST"])
def controls(request):
    actor, response = _actor(request)
    if response is not None: return response
    try:
        if request.method == "POST":
            return success_response(ComplianceTaskEngine.create_control(actor=actor, payload=parse_json_body(request)), request)
        data, pagination = ComplianceTaskEngine.list_controls(actor=actor, query=request.GET)
        return list_response(data, pagination, request)
    except Exception as exc:
        return _error(request, exc)


@require_http_methods(["PATCH"])
def control_detail(request, compliance_control_id):
    actor, response = _actor(request)
    if response is not None: return response
    try:
        return success_response(ComplianceTaskEngine.update_control(actor=actor, control_id=compliance_control_id, payload=parse_json_body(request)), request)
    except Exception as exc: return _error(request, exc)


@require_http_methods(["GET", "POST"])
def tasks(request):
    actor, response = _actor(request)
    if response is not None: return response
    try:
        if request.method == "POST":
            return success_response(ComplianceTaskEngine.create_task(actor=actor, payload=parse_json_body(request)), request)
        data, pagination = ComplianceTaskEngine.list_tasks(actor=actor, query=request.GET)
        return list_response(data, pagination, request)
    except Exception as exc: return _error(request, exc)


@require_http_methods(["PATCH"])
def task_detail(request, compliance_task_id):
    actor, response = _actor(request)
    if response is not None: return response
    try:
        return success_response(ComplianceTaskEngine.update_task(actor=actor, task_id=compliance_task_id, payload=parse_json_body(request)), request)
    except Exception as exc: return _error(request, exc)


@require_http_methods(["POST"])
def evidence_submit(request, compliance_task_id):
    actor, response = _actor(request)
    if response is not None: return response
    try:
        task = ComplianceTaskEngine.submit_evidence(actor=actor, task_id=compliance_task_id, payload=parse_json_body(request))
        return success_response(ComplianceTaskEngine.serialize_task(task, actor), request)
    except Exception as exc: return _error(request, exc)


@require_http_methods(["POST"])
def evidence_review(request, compliance_evidence_id):
    from sfpcl_credit.compliance.models import ComplianceEvidence
    actor, response = _actor(request)
    if response is not None: return response
    try:
        tracker.require(actor, "compliance.evidence.review")
        evidence = ComplianceEvidence.objects.get(pk=compliance_evidence_id)
        payload = parse_json_body(request)
        task = ComplianceTaskEngine.review_evidence(actor=actor, task_id=evidence.task_id,
            decision=payload.get("review_status"), comments=payload.get("review_comments"),
            evidence_id=evidence.pk)
        return success_response(ComplianceTaskEngine.serialize_task(task, actor), request)
    except ComplianceEvidence.DoesNotExist:
        return error_response(request, 404, "NOT_FOUND", "Compliance evidence was not found.")
    except Exception as exc: return _error(request, exc)


@require_http_methods(["POST"])
def money_lending_review(request):
    actor, response = _actor(request)
    if response is not None: return response
    try:
        return success_response(
            ComplianceTaskEngine.create_money_lending_review(actor=actor, payload=parse_json_body(request)), request
        )
    except Exception as exc: return _error(request, exc)


@require_http_methods(["POST"])
def section_186_trackers(request):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        period_id = payload.pop("compliance_task_id", None)
        row = Section186TrackerModule.calculate(
            actor=actor, period_id=period_id, payload=payload
        )
        return success_response(Section186TrackerModule.serialize(row, actor), request)
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["POST"])
def section_186_tracker_submit(request, section_186_tracker_id):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        if parse_json_body(request):
            raise tracker.ComplianceInvalid({"request": "Submit request must be empty."})
        return success_response(
            Section186TrackerModule.submit_for_review(
                actor=actor, tracker_id=section_186_tracker_id
            ),
            request,
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["GET"])
def section_186_tracker_detail(request, section_186_tracker_id):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        return success_response(
            Section186TrackerModule.retrieve(
                actor=actor, tracker_id=section_186_tracker_id
            ),
            request,
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["POST"])
def section_186_tracker_review(request, section_186_tracker_id):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        return success_response(
            Section186TrackerModule.review(
                actor=actor,
                tracker_id=section_186_tracker_id,
                decision=payload.get("decision"),
                comments=payload.get("comments"),
                presented_to_board_flag=payload.get("presented_to_board_flag"),
                board_document_id=payload.get("board_document_id"),
            ),
            request,
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["POST"])
def nbfc_principal_tests(request):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        period_id = payload.pop("compliance_task_id", None)
        row = NbfcPrincipalBusinessTestModule.calculate(
            actor=actor, period_id=period_id, payload=payload
        )
        return success_response(
            NbfcPrincipalBusinessTestModule.serialize(row, actor), request
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["GET"])
def nbfc_principal_test_detail(request, nbfc_principal_test_id):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        return success_response(
            NbfcPrincipalBusinessTestModule.retrieve(
                actor=actor, result_id=nbfc_principal_test_id
            ),
            request,
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["POST"])
def nbfc_principal_test_submit(request, nbfc_principal_test_id):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        if parse_json_body(request):
            raise tracker.ComplianceInvalid({"request": "Submit request must be empty."})
        return success_response(
            NbfcPrincipalBusinessTestModule.submit_for_review(
                actor=actor, result_id=nbfc_principal_test_id
            ),
            request,
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)


@require_http_methods(["POST"])
def nbfc_principal_test_review(request, nbfc_principal_test_id):
    actor, response = _actor(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        return success_response(
            NbfcPrincipalBusinessTestModule.review(
                actor=actor,
                result_id=nbfc_principal_test_id,
                decision=payload.get("decision"),
                comments=payload.get("comments"),
                presented_to_board_flag=payload.get("presented_to_board_flag"),
                board_document_id=payload.get("board_document_id"),
            ),
            request,
        )
    except Exception as exc:
        return _error(request, exc, audit_denial=True)
