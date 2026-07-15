from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from sfpcl_credit.applications import views as application_views
from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.legal_documents.modules import document_generation
from sfpcl_credit.legal_documents.modules import document_checklist
from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.processes import document_checklist_actions as checklist_action_process
from sfpcl_credit.processes import staff_documentation_workspace
from sfpcl_credit.legal_documents.modules import stamp_notary
from sfpcl_credit.legal_documents.modules import signatures
from sfpcl_credit.legal_documents.modules import loan_document_verification
from sfpcl_credit.legal_documents.serializers import (
    LoanDocumentVerificationRequest,
    NotarisationRecordRequest,
    SignatureMismatchResolutionRequest,
    SignatureRecordRequest,
    StampDutyRecordRequest,
)


@require_POST
def verify_loan_document(request, loan_document_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        loan_document_verification.require_verify_actor(user)
        parsed = LoanDocumentVerificationRequest.parse(parse_json_body(request))
        data = loan_document_verification.verify(
            actor=user,
            loan_document_id=loan_document_id,
            payload=parsed,
            metadata=loan_document_verification.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except loan_document_verification.AccessDenied as exc:
        return error_response(
            request, 403, exc.error_code, "You do not have access to this loan document."
        )
    except loan_document_verification.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Loan document was not found.")
    except loan_document_verification.Conflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan document verification failed validation.",
            loan_document_verification.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_GET
def loan_document_collection(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data, pagination = document_generation.list_for_application(
            actor=user,
            application_id=loan_application_id,
            query_params=request.GET,
        )
    except document_generation.LegalDocumentAccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this loan application.",
        )
    except document_generation.LegalDocumentNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "Loan application was not found."
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan document query failed validation.",
            document_generation.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_POST
def generate_loan_document(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = document_generation.generate(
            actor=user,
            application_id=loan_application_id,
            payload=parse_json_body(request),
            metadata=document_generation.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except document_generation.LegalDocumentAccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this loan application.",
        )
    except document_generation.LegalDocumentNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "Loan application was not found."
        )
    except document_generation.InvalidGenerationState as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except document_generation.RendererProvenanceConflict as exc:
        return error_response(
            request,
            409,
            "CONFLICT",
            str(exc),
            details=exc.details,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan document generation failed validation.",
            document_generation.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_GET
def legal_document_checklist(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = document_checklist.read_for_application(
            actor=user,
            application_id=loan_application_id,
        )
    except document_checklist.PreSanctionChecklist:
        return application_views.loan_application_document_checklist(
            request, loan_application_id
        )
    except document_checklist.ChecklistAccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this document checklist.",
        )
    except document_checklist.ChecklistNotFound:
        return error_response(
            request, 404, "NOT_FOUND", "Document checklist was not found."
        )
    return success_response(data, request)


@require_GET
def documentation_workspace_queue(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = staff_documentation_workspace.list_queue(
            actor=user,
            query_params=request.GET,
        )
    except staff_documentation_workspace.AccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to the documentation queue.",
        )
    return list_response(data["items"], data["pagination"], request)


@require_GET
def documentation_workspace(request, loan_application_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = staff_documentation_workspace.read(actor=user, application_id=loan_application_id)
    except staff_documentation_workspace.AccessDenied as exc:
        return error_response(request, 403, exc.error_code, "You do not have access to this documentation workspace.")
    except staff_documentation_workspace.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Documentation workspace was not found.")
    return success_response(data, request)
@require_GET
def documentation_workspace_download(request, loan_application_id, item_code):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return response
    try:
        data = staff_documentation_workspace.download(actor=user, application_id=loan_application_id, item_code=item_code, request=request)
    except (staff_documentation_workspace.AccessDenied, staff_documentation_workspace.NotFound):
        return error_response(request, 404, "NOT_FOUND", "Document was not found.")
    if isinstance(data, staff_documentation_workspace.DocumentContent):
        response = HttpResponse(data.body, content_type=data.mime_type)
        response["Content-Disposition"] = f'attachment; filename="{data.file_name}"'
        response["Cache-Control"] = "no-store"; response["Pragma"] = "no-cache"
        return response
    return success_response(data, request)
def _checklist_action_metadata(request):
    return checklist_actions.RequestMetadata(
        request_id=request.headers.get("X-Request-ID"),
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )


def _run_checklist_action(request, recorder, target_id, label):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        data = recorder(
            actor=user,
            payload=parse_json_body(request),
            metadata=_checklist_action_metadata(request),
            **target_id,
        )
    except checklist_actions.AccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            f"You do not have access to this {label}.",
        )
    except checklist_actions.NotFound:
        return error_response(request, 404, "NOT_FOUND", f"{label.title()} was not found.")
    except checklist_actions.Conflict as exc:
        return error_response(request, 409, exc.error_code, str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            f"{label.title()} action failed validation.",
            checklist_actions.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_POST
def complete_checklist_item(request, checklist_item_id):
    return _run_checklist_action(
        request,
        checklist_action_process.complete_item,
        {"checklist_item_id": checklist_item_id},
        "checklist item",
    )


@require_POST
def approve_checklist_company_secretary(request, document_checklist_id):
    return _run_checklist_action(
        request,
        checklist_action_process.approve_company_secretary,
        {"document_checklist_id": document_checklist_id},
        "document checklist",
    )


@require_POST
def approve_checklist_credit_manager(request, document_checklist_id):
    return _run_checklist_action(
        request,
        checklist_action_process.approve_credit_manager,
        {"document_checklist_id": document_checklist_id},
        "document checklist",
    )


@require_POST
def approve_checklist_sanction_committee(request, document_checklist_id):
    return _run_checklist_action(
        request,
        checklist_action_process.approve_sanction_committee,
        {"document_checklist_id": document_checklist_id},
        "document checklist",
    )


@require_POST
def sign_checklist_disbursement_complete(request, document_checklist_id):
    return _run_checklist_action(
        request,
        checklist_action_process.sign_disbursement_complete,
        {"document_checklist_id": document_checklist_id},
        "document checklist",
    )


def _record_lifecycle(
    request, loan_document_id, recorder, authorizer, request_type, label
):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        authorizer(user)
        parsed_request = request_type.parse(parse_json_body(request))
        data = recorder(
            actor=user,
            loan_document_id=loan_document_id,
            payload=parsed_request,
            metadata=stamp_notary.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except stamp_notary.AccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this loan document.",
        )
    except stamp_notary.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Loan document was not found.")
    except stamp_notary.ProvenanceConflict:
        return error_response(
            request,
            409,
            "CONFLICT",
            "Retained output is not bound to the current renderer contract.",
        )
    except stamp_notary.ProjectionConflict as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            f"{label} failed validation.",
            stamp_notary.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_POST
def stamp_duty_record(request, loan_document_id):
    return _record_lifecycle(
        request,
        loan_document_id,
        stamp_notary.record_stamp,
        stamp_notary.require_stamp_actor,
        StampDutyRecordRequest,
        "Stamp duty record",
    )


@require_POST
def notarisation_record(request, loan_document_id):
    return _record_lifecycle(
        request,
        loan_document_id,
        stamp_notary.record_notary,
        stamp_notary.require_notary_actor,
        NotarisationRecordRequest,
        "Notarisation record",
    )


@require_POST
def signature_record(request, loan_document_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        signatures.require_record_actor(user)
        data = signatures.record(
            actor=user,
            loan_document_id=loan_document_id,
            payload=SignatureRecordRequest.parse(parse_json_body(request)),
            metadata=signatures.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except signatures.AccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this loan document.",
        )
    except signatures.NotFound:
        return error_response(request, 404, "NOT_FOUND", "Loan document was not found.")
    except signatures.ProvenanceConflict:
        return error_response(
            request,
            409,
            "CONFLICT",
            "Retained output is not bound to the current renderer contract.",
        )
    except signatures.SignatureMismatchUnresolved as exc:
        return error_response(
            request, 400, "SIGNATURE_MISMATCH_UNRESOLVED", str(exc)
        )
    except signatures.InvalidState as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Signature record failed validation.",
            signatures.validation_field_errors(exc),
        )
    return success_response(data, request)


@require_POST
def resolve_signature_mismatch(request, signature_record_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        signatures.require_resolve_actor(user)
        data = signatures.resolve_mismatch(
            actor=user,
            signature_record_id=signature_record_id,
            payload=SignatureMismatchResolutionRequest.parse(parse_json_body(request)),
            metadata=signatures.RequestMetadata(
                request_id=request.headers.get("X-Request-ID"),
                ip_address=request_ip(request),
                user_agent=request_user_agent(request),
            ),
        )
    except signatures.AccessDenied as exc:
        return error_response(
            request,
            403,
            exc.error_code,
            "You do not have access to this signature record.",
        )
    except signatures.NotFound:
        return error_response(
            request, 404, "NOT_FOUND", "Signature record was not found."
        )
    except signatures.ProvenanceConflict:
        return error_response(
            request,
            409,
            "CONFLICT",
            "Retained output is not bound to the current renderer contract.",
        )
    except (
        signatures.InvalidState,
        signatures.EvidenceConflict,
        signatures.ProjectionConflict,
    ) as exc:
        return error_response(request, 409, "CONFLICT", str(exc))
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Signature mismatch resolution failed validation.",
            signatures.validation_field_errors(exc),
        )
    return success_response(data, request)
