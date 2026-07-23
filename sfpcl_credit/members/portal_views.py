import uuid

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_http_methods

from sfpcl_credit.api import error_response, list_response, parse_json_body, request_ip, request_user_agent, success_response
from sfpcl_credit.applications import services as application_services
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.members import portal_services
from sfpcl_credit.members.modules import kyc_correction_requests
from sfpcl_credit.members.modules.member_authority import MemberObjectAccessDenied
from sfpcl_credit.processes import portal_documentation_actions as portal_documentation_process
from sfpcl_credit.processes import portal_deficiency_response as portal_deficiency_process
from sfpcl_credit.processes import portal_disbursement_status
from sfpcl_credit.processes import portal_loan_servicing
from sfpcl_credit.processes import portal_communications
from sfpcl_credit.workflows.guard import InvalidStateTransition


def _portal_member_or_response(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return None, None, response
    member = portal_services.portal_member_for_user(user)
    if member is None:
        return None, None, error_response(
            request,
            403,
            "FORBIDDEN",
            portal_services.PORTAL_PERMISSION_ERROR,
        )
    claimed_member_id = request.GET.get("member_id")
    if claimed_member_id and claimed_member_id != str(member.member_id):
        if "/portal/kyc-corrections/" in request.path:
            try:
                denied_entity_id = uuid.UUID(claimed_member_id)
            except (TypeError, ValueError, AttributeError):
                denied_entity_id = member.pk
            AuditLog.objects.create(
                actor_user=user,
                actor_type="portal_account",
                action="portal.kyc_correction.access_denied",
                entity_type="member",
                entity_id=denied_entity_id,
                new_value_json={
                    "authenticated_member_id": str(member.pk),
                    "outcome": "denied",
                    "reason": "cross_member_read",
                },
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            )
        return None, None, error_response(
            request,
            403,
            "OBJECT_ACCESS_DENIED",
            "You cannot access this member.",
        )
    return member, user, None


@require_GET
def portal_dashboard(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.dashboard_summary(member), request)


@require_GET
def portal_profile(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.profile(member, user), request)


@require_http_methods(["GET", "POST"])
def portal_grievances(request):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        if request.method == "POST":
            key = request.headers.get("Idempotency-Key")
            if not key:
                from sfpcl_credit.compliance.modules.compliance_control_tracker import ComplianceInvalid

                raise ComplianceInvalid({"Idempotency-Key": "This header is required."})
            return success_response(
                portal_communications.create_grievance(
                    actor=user,
                    payload=parse_json_body(request),
                    idempotency_key=key,
                ),
                request,
            )
        rows, pagination = portal_communications.list_grievances(
            actor=user, query=request.GET
        )
        return list_response(rows, pagination, request)
    except Exception as exc:
        return _portal_communications_error(request, exc)


@require_GET
def portal_grievance_detail(request, grievance_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        return success_response(
            portal_communications.grievance_detail(
                actor=user, grievance_id=grievance_id
            ),
            request,
        )
    except Exception as exc:
        return _portal_communications_error(request, exc, detail=True)


@require_GET
def portal_notifications(request):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        rows, pagination = portal_communications.list_notifications(
            actor=user, query=request.GET
        )
        return list_response(rows, pagination, request)
    except Exception as exc:
        return _portal_communications_error(request, exc)


@require_http_methods(["POST"])
def portal_notification_mark_read(request, notification_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        return success_response(
            portal_communications.mark_notification_read(
                actor=user,
                notification_id=notification_id,
                payload=parse_json_body(request),
                request=request,
            ),
            request,
        )
    except Exception as exc:
        return _portal_communications_error(request, exc, detail=True)


@require_GET
def portal_notices(request):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        rows, pagination = portal_communications.list_notices(
            actor=user, query=request.GET
        )
        return list_response(rows, pagination, request)
    except Exception as exc:
        return _portal_communications_error(request, exc)


@require_GET
def portal_notice_download(request, communication_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        return success_response(
            portal_communications.download_notice(
                actor=user,
                communication_id=communication_id,
                request=request,
            ),
            request,
        )
    except Exception as exc:
        return _portal_communications_error(request, exc, detail=True)


@require_GET
def portal_closures(request):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        rows, pagination = portal_communications.list_closures(
            actor=user, query=request.GET
        )
        return list_response(rows, pagination, request)
    except Exception as exc:
        return _portal_communications_error(request, exc)


def _portal_communications_error(request, exc, *, detail=False):
    from django.core.exceptions import ObjectDoesNotExist
    from sfpcl_credit.compliance.modules.compliance_control_tracker import (
        ComplianceConflict,
        ComplianceDenied,
        ComplianceInvalid,
    )
    from sfpcl_credit.communications.services import StaleWriteError

    if isinstance(exc, StaleWriteError):
        return error_response(
            request,
            409,
            "STALE_WRITE",
            "Notification read state changed. Refresh and try again.",
        )
    if isinstance(exc, ObjectDoesNotExist):
        return error_response(request, 404, "NOT_FOUND", "The notification was not found.")
    if isinstance(exc, ValidationError):
        field_errors = getattr(exc, "message_dict", {"request": exc.messages})
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Portal notification failed validation.",
            {field: messages[0] for field, messages in field_errors.items()},
        )

    if isinstance(exc, ComplianceInvalid):
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Portal grievance failed validation.",
            exc.field_errors,
        )
    if isinstance(exc, ComplianceConflict):
        return error_response(request, 409, "CONFIGURATION_REQUIRED", str(exc))
    if isinstance(exc, (ComplianceDenied, PermissionError)):
        if detail:
            return error_response(
                request, 404, "NOT_FOUND", "The grievance was not found."
            )
        return error_response(
            request, 403, "FORBIDDEN", portal_services.PORTAL_PERMISSION_ERROR
        )
    raise exc


@require_http_methods(["GET", "POST"])
def portal_kyc_corrections(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if request.method == "GET":
        return success_response(
            {
                "items": kyc_correction_requests.list_for_portal(
                    user=user, member=member
                )
            },
            request,
        )
    metadata = {
        "ip_address": request_ip(request),
        "user_agent": request_user_agent(request),
    }
    try:
        payload = parse_json_body(request)
        kyc_correction_requests.enforce_member_claim(
            user=user, member=member, payload=payload, request_metadata=metadata
        )
        data = kyc_correction_requests.submit(
            user=user,
            member=member,
            payload=payload,
            request_metadata=metadata,
        )
    except kyc_correction_requests.PortalKycCorrectionAccessDenied as exc:
        return error_response(request, 403, "OBJECT_ACCESS_DENIED", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC correction request failed validation.",
            kyc_correction_requests.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_kyc_correction_evidence(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data = kyc_correction_requests.upload_evidence(
            user=user, member=member, request=request
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC correction evidence failed validation.",
            {
                field: messages[0]
                for field, messages in getattr(exc, "message_dict", {}).items()
            },
        )
    return success_response(data, request)


@require_GET
def staff_kyc_correction_queue(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = {"items": kyc_correction_requests.list_for_staff(actor=user)}
    except PermissionError:
        return error_response(
            request, 403, "FORBIDDEN", "You do not have authority for KYC corrections."
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def staff_kyc_correction_review(request, correction_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    payload, parse_response = _staff_correction_payload(request)
    if parse_response is not None:
        return parse_response
    return _staff_kyc_correction_action(
        request,
        lambda: kyc_correction_requests.start_review(
            actor=user,
            correction_id=correction_id,
            internal_notes=payload.get("internal_notes"),
            request_metadata=_request_metadata(request),
        ),
    )


@require_http_methods(["POST"])
def staff_kyc_correction_approve(request, correction_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    _payload, parse_response = _staff_correction_payload(request)
    if parse_response is not None:
        return parse_response
    return _staff_kyc_correction_action(
        request,
        lambda: kyc_correction_requests.approve(
            actor=user,
            correction_id=correction_id,
            request_metadata=_request_metadata(request),
        ),
    )


@require_http_methods(["POST"])
def staff_kyc_correction_reject(request, correction_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    payload, parse_response = _staff_correction_payload(request)
    if parse_response is not None:
        return parse_response
    return _staff_kyc_correction_action(
        request,
        lambda: kyc_correction_requests.reject(
            actor=user,
            correction_id=correction_id,
            rejection_reason=payload.get("rejection_reason"),
            request_metadata=_request_metadata(request),
        ),
    )


def _staff_kyc_correction_action(request, action):
    try:
        data = action()
    except (PermissionError, PermissionDenied):
        return error_response(
            request, 403, "FORBIDDEN", "You do not have authority for this KYC correction."
        )
    except MemberObjectAccessDenied:
        return error_response(
            request, 403, "OBJECT_ACCESS_DENIED", "You cannot access this member."
        )
    except kyc_correction_requests.KycCorrectionConflict as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC correction decision failed validation.",
            {
                field: messages[0]
                for field, messages in getattr(exc, "message_dict", {}).items()
            },
        )
    if data is None:
        return error_response(request, 404, "NOT_FOUND", "KYC correction was not found.")
    return success_response(data, request)


def _staff_correction_payload(request):
    try:
        return parse_json_body(request), None
    except ValidationError as exc:
        return None, error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC correction request body is invalid.",
            kyc_correction_requests.validation_field_errors(exc),
        )


def _request_metadata(request):
    return {
        "ip_address": request_ip(request),
        "user_agent": request_user_agent(request),
    }


@require_GET
def portal_produce_supply(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    return success_response(portal_services.produce_supply(member), request)


@require_GET
def portal_loan_accounts(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data, pagination = portal_loan_servicing.list_accounts(
            member=member, query_params=request.GET
        )
    except portal_loan_servicing.PortalLoanQueryInvalid as exc:
        return _portal_loan_query_error(request, exc)
    return list_response(data, pagination, request)


@require_GET
def portal_loan_account_detail(request, loan_account_id):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if request.GET:
        return _portal_loan_query_error(
            request,
            portal_loan_servicing.PortalLoanQueryInvalid(
                {field: "Unknown query parameter." for field in sorted(request.GET)}
            ),
        )
    return _portal_loan_result(
        request,
        lambda: portal_loan_servicing.account_detail(
            member=member, loan_account_id=loan_account_id
        ),
    )


@require_GET
def portal_loan_account_schedule(request, loan_account_id):
    return _portal_loan_collection(request, loan_account_id, portal_loan_servicing.schedule)


@require_GET
def portal_loan_account_repayments(request, loan_account_id):
    return _portal_loan_collection(
        request, loan_account_id, portal_loan_servicing.repayment_history
    )


@require_GET
def portal_loan_account_invoices(request, loan_account_id):
    return _portal_loan_collection(request, loan_account_id, portal_loan_servicing.invoices)


@require_GET
def portal_loan_account_direct_instructions(request, loan_account_id):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if request.GET:
        return _portal_loan_query_error(
            request,
            portal_loan_servicing.PortalLoanQueryInvalid(
                {field: "Unknown query parameter." for field in sorted(request.GET)}
            ),
        )
    return _portal_loan_result(
        request,
        lambda: portal_loan_servicing.direct_instructions(
            member=member, loan_account_id=loan_account_id
        ),
    )


def _portal_loan_collection(request, loan_account_id, resolver):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data, pagination = resolver(
            member=member,
            loan_account_id=loan_account_id,
            query_params=request.GET,
        )
    except portal_loan_servicing.PortalLoanQueryInvalid as exc:
        return _portal_loan_query_error(request, exc)
    except portal_loan_servicing.PortalLoanNotFound:
        return _portal_loan_not_found(request)
    return list_response(data, pagination, request)


def _portal_loan_result(request, resolver):
    try:
        return success_response(resolver(), request)
    except portal_loan_servicing.PortalLoanNotFound:
        return _portal_loan_not_found(request)


def _portal_loan_not_found(request):
    return error_response(
        request, 404, "NOT_FOUND", "The loan account was not found or is inaccessible."
    )


def _portal_loan_query_error(request, exc):
    return error_response(
        request,
        400,
        "VALIDATION_ERROR",
        "Portal loan query failed validation.",
        exc.field_errors,
    )


@require_GET
def portal_application_limit_projection(request):
    member, _user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        projection = portal_services.application_limit_projection(
            member,
            requested_amount=request.GET.get("requested_amount"),
        )
    except ValidationError as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(projection, request)


@require_http_methods(["GET", "POST"])
def portal_applications(request):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if request.method == "GET":
        return success_response(portal_services.list_applications(member), request)
    try:
        body = parse_json_body(request)
        data = portal_services.create_application(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    except (application_services.LoanApplicationValidationError, ValidationError) as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(data, request)


@require_http_methods(["GET", "PATCH"])
def portal_application_detail(request, loan_application_id):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        application = portal_services.get_application_for_member(member, loan_application_id)
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    if request.method == "GET":
        return success_response(portal_services.application_detail(application), request)
    try:
        body = parse_json_body(request)
        data = portal_services.update_application(
            application,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    except (application_services.LoanApplicationValidationError, ValidationError) as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_application_submit(request, loan_application_id):
    member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        application = portal_services.get_application_for_member(member, loan_application_id)
    except portal_services.PortalObjectAccessError as exc:
        return _portal_object_access_denied(request, exc)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    try:
        parse_json_body(request)
        data = portal_services.submit_application(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (application_services.LoanApplicationValidationError, ValidationError) as exc:
        return _portal_application_validation_error(request, exc)
    except (application_services.LoanApplicationInvalidStateError, InvalidStateTransition) as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(data, request)


@require_GET
def portal_application_deficiencies(request, loan_application_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data = portal_deficiency_process.get_projection(
            actor=user,
            application_id=loan_application_id,
            request=request,
        )
    except portal_deficiency_process.PortalDeficiencyNotFound:
        portal_deficiency_process.audit_access_denied(
            actor=user,
            application_id=loan_application_id,
            attempted_action="view",
            request=request,
        )
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    return success_response(data, request)


@require_GET
def portal_application_deficiency_note(request, loan_application_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data = portal_deficiency_process.deficiency_note(
            actor=user, application_id=loan_application_id, request=request
        )
    except portal_deficiency_process.PortalDeficiencyNotFound:
        portal_deficiency_process.audit_access_denied(
            actor=user, application_id=loan_application_id, attempted_action="download_note", request=request
        )
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    response = HttpResponse(data.body, content_type=data.mime_type)
    response["Content-Disposition"] = f'attachment; filename="{data.file_name}"'
    return response


@require_http_methods(["POST"])
def portal_application_deficiency_draft(request, loan_application_id, deficiency_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data = portal_deficiency_process.save_draft(
            actor=user,
            application_id=loan_application_id,
            deficiency_id=deficiency_id,
            payload=parse_json_body(request),
            request=request,
        )
    except portal_deficiency_process.PortalDeficiencyNotFound:
        portal_deficiency_process.audit_access_denied(
            actor=user, application_id=loan_application_id, attempted_action="save_draft", request=request
        )
        return error_response(request, 404, "NOT_FOUND", "Deficiency was not found.")
    except portal_deficiency_process.PortalDeficiencyUnavailable as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except portal_deficiency_process.PortalDeficiencyValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Draft validation failed.", exc.field_errors)
    except ValidationError as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_application_deficiency_upload(request, loan_application_id, deficiency_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data = portal_deficiency_process.upload(
            actor=user,
            application_id=loan_application_id,
            deficiency_id=deficiency_id,
            request=request,
        )
    except portal_deficiency_process.PortalDeficiencyNotFound:
        portal_deficiency_process.audit_access_denied(
            actor=user,
            application_id=loan_application_id,
            attempted_action="upload",
            request=request,
        )
        return error_response(request, 404, "NOT_FOUND", "Deficiency was not found.")
    except portal_deficiency_process.PortalDeficiencyUnavailable as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Portal deficiency upload failed validation.",
            application_services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_application_deficiency_resubmit(request, loan_application_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        if payload:
            raise ValidationError(
                {field: "Unknown field." for field in sorted(payload.keys())}
            )
        data = portal_deficiency_process.resubmit(
            actor=user,
            application_id=loan_application_id,
            request=request,
        )
    except portal_deficiency_process.PortalDeficiencyNotFound:
        portal_deficiency_process.audit_access_denied(
            actor=user,
            application_id=loan_application_id,
            attempted_action="resubmit",
            request=request,
        )
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    except portal_deficiency_process.PortalDeficiencyUnavailable as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except portal_deficiency_process.PortalDeficiencyValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Every mandatory deficiency must be addressed before resubmission.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return _portal_application_validation_error(request, exc)
    return success_response(data, request)


@require_GET
def portal_application_deficiency_download(request, loan_application_id, deficiency_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        data = portal_deficiency_process.download(
            actor=user,
            application_id=loan_application_id,
            deficiency_id=deficiency_id,
            request=request,
        )
    except portal_deficiency_process.PortalDeficiencyNotFound:
        portal_deficiency_process.audit_access_denied(
            actor=user,
            application_id=loan_application_id,
            attempted_action="download",
            request=request,
        )
        return error_response(request, 404, "NOT_FOUND", "Document was not found.")
    if isinstance(data, portal_deficiency_process.PortalDeficiencyContent):
        return _no_store_content_response(data)
    return success_response(data, request)


@require_GET
def portal_documentation_actions(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = portal_documentation_process.get_projection(
            actor=user,
            application_id=loan_application_id,
        )
    except portal_documentation_process.PortalDocumentationNotFound:
        return error_response(
            request,
            404,
            "NOT_FOUND",
            "Loan application was not found.",
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_documentation_action_upload(request, loan_application_id, action_code):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = portal_documentation_process.upload(
            actor=user,
            application_id=loan_application_id,
            action_code=action_code,
            request=request,
        )
    except portal_documentation_process.PortalDocumentationNotFound:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    except portal_documentation_process.PortalDocumentationUnavailable as exc:
        return error_response(request, 409, "ACTION_UNAVAILABLE", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Portal documentation upload failed validation.",
            application_services.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_GET
def portal_documentation_action_download(request, loan_application_id, action_code):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = portal_documentation_process.download(
            actor=user,
            application_id=loan_application_id,
            action_code=action_code,
            request=request,
        )
    except portal_documentation_process.PortalDocumentationNotFound:
        return error_response(request, 404, "NOT_FOUND", "Document was not found.")
    if isinstance(data, portal_documentation_process.PortalDocumentContent):
        return _no_store_content_response(data)
    return success_response(data, request)


@require_GET
def portal_application_disbursement_status(request, loan_application_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if request.GET:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Disbursement status does not accept query parameters.",
            {field: "Unknown query parameter." for field in sorted(request.GET)},
        )
    try:
        data = portal_disbursement_status.get_projection(
            actor=user, application_id=loan_application_id
        )
    except portal_disbursement_status.PortalDisbursementNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "Loan application was not found."
        )
    return success_response(data, request)


@require_http_methods(["POST"])
def portal_disbursement_advice_capability(request, loan_application_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    try:
        payload = parse_json_body(request)
        if payload:
            raise ValidationError(
                {field: "Unknown field." for field in sorted(payload)}
            )
        data = portal_disbursement_status.issue_advice_capability(
            actor=user, application_id=loan_application_id, request=request
        )
    except ValidationError as exc:
        return _portal_application_validation_error(request, exc)
    except portal_disbursement_status.PortalDisbursementNotFound:
        return error_response(request, 404, "NOT_FOUND", "Advice was not found.")
    return success_response(data, request)


@require_GET
def portal_disbursement_advice_content(request, loan_application_id):
    _member, user, response = _portal_member_or_response(request)
    if response is not None:
        return response
    if set(request.GET) != {"capability"}:
        portal_disbursement_status.record_download_denial(
            actor=user, application_id=loan_application_id, request=request
        )
        return error_response(request, 404, "NOT_FOUND", "Advice was not found.")
    try:
        content = portal_disbursement_status.read_advice(
            actor=user,
            application_id=loan_application_id,
            capability=request.GET.get("capability", ""),
            request=request,
        )
    except portal_disbursement_status.PortalDisbursementNotFound:
        portal_disbursement_status.record_download_denial(
            actor=user, application_id=loan_application_id, request=request
        )
        return error_response(request, 404, "NOT_FOUND", "Advice was not found.")
    return _no_store_content_response(content)


def _portal_object_access_denied(request, exc):
    return error_response(request, 403, "OBJECT_ACCESS_DENIED", str(exc))


def _no_store_content_response(content):
    response = HttpResponse(content.body, content_type=content.mime_type)
    response["Content-Disposition"] = f'attachment; filename="{content.file_name}"'
    response["Cache-Control"] = "no-store"
    response["Pragma"] = "no-cache"
    response["X-Content-Type-Options"] = "nosniff"
    return response


def _portal_application_validation_error(request, exc):
    return error_response(
        request,
        400,
        "VALIDATION_ERROR",
        "Portal application payload failed validation.",
        application_services.validation_field_errors(exc),
    )
