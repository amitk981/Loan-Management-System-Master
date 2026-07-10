from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
from sfpcl_credit.approvals.modules.sanction_handoff import SanctionHandoffModule
from sfpcl_credit.applications import services
from sfpcl_credit.credit.modules.common import (
    CreditModuleInvalidStateError,
    CreditModuleNotFound,
    CreditModuleObjectAccessDenied,
    CreditModulePermissionDenied,
    CreditModuleValidationError,
)
from sfpcl_credit.credit.modules.eligibility_assessment import EligibilityAssessmentModule
from sfpcl_credit.credit.modules.appraisal_workflow import AppraisalWorkflow
from sfpcl_credit.credit.modules.loan_limit_calculator import LoanLimitCalculator
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.workflows.guard import InvalidStateTransition


@require_http_methods(["GET", "POST"])
def loan_application_collection(request):
    if request.method == "GET":
        user, permissions, response = http_auth.authenticated_user_with_permissions(request)
        if response is not None:
            return response
        if not services.user_can_read_applications(user):
            return error_response(
                request,
                403,
                "FORBIDDEN",
                "You do not have permission to read loan applications.",
            )
        items, pagination = services.list_applications_for_staff(
            request.GET,
            user,
            permissions,
        )
        return list_response(items, pagination, request)

    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_create_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create loan applications.",
        )
    try:
        body = parse_json_body(request)
        application = services.create_draft(
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except services.LoanApplicationValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_application(application), request)


@require_http_methods(["GET"])
def loan_request_register_collection(request):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read loan applications.",
        )
    items, pagination = services.list_loan_request_register_for_staff(
        request.GET,
        user,
        permissions,
    )
    return list_response(items, pagination, request)


@require_http_methods(["GET", "PATCH"])
def loan_application_detail(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read loan applications.",
        )
    if request.method == "PATCH":
        if not services.user_can_update_applications(user):
            return error_response(
                request,
                403,
                "FORBIDDEN",
                "You do not have permission to update loan applications.",
            )
        application = services.get_application(loan_application_id)
        if application is None:
            return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
        object_access = services.evaluate_application_object_access(
            application,
            user,
            services.APPLICATION_UPDATE_PERMISSION,
            permissions,
        )
        if not object_access.allowed:
            return _object_access_denied_response(request, object_access)
        try:
            body = parse_json_body(request)
            application = services.update_draft(
                application,
                body,
                user,
                request_ip(request),
                request_user_agent(request),
                request.headers.get("X-Request-ID"),
            )
        except services.LoanApplicationValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Loan application payload failed validation.",
                services.validation_field_errors(exc),
            )
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Loan application payload failed validation.",
                services.validation_field_errors(exc),
            )
        return success_response(services.serialize_application(application), request)

    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_READ_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    return success_response(services.serialize_application_detail(application, user), request)


@require_http_methods(["GET", "POST"])
def loan_application_witnesses(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    required_permission = (
        services.WITNESS_READ_PERMISSION
        if request.method == "GET"
        else services.WITNESS_CREATE_PERMISSION
    )
    has_permission = (
        services.user_can_read_witnesses(user)
        if request.method == "GET"
        else services.user_can_create_witnesses(user)
    )
    if not has_permission:
        return error_response(request, 403, "FORBIDDEN", "You do not have permission to access witnesses.")
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application, user, required_permission, permissions
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    if request.method == "GET":
        items = services.list_witnesses(application)
        return list_response(
            items,
            {
                "page": 1,
                "page_size": len(items) or 20,
                "total_count": len(items),
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
            },
            request,
        )
    try:
        witness = services.create_witness(
            application,
            parse_json_body(request),
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except services.WitnessValidationError as exc:
        status = 404 if exc.code == "NOT_FOUND" else 400
        return error_response(request, status, exc.code, exc.message, exc.field_errors)
    except ValidationError:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Witness payload failed validation.",
        )
    return success_response(services.serialize_witness(witness), request)


@require_http_methods(["POST"])
def loan_application_submit(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_submit_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to submit loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_SUBMIT_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        parse_json_body(request)
        application = services.submit_application(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
            permissions,
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    except (services.LoanApplicationInvalidStateError, InvalidStateTransition) as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_application(application), request)


@require_http_methods(["POST"])
def loan_application_generate_reference(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to complete-check loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        parse_json_body(request)
        application = services.generate_reference_after_completeness_pass(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
            permissions,
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan application payload failed validation.",
            services.validation_field_errors(exc),
        )
    except (services.LoanApplicationInvalidStateError, InvalidStateTransition) as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_application(application), request)


@require_http_methods(["GET", "POST"])
def loan_application_documents(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read loan applications.",
        )
    if request.method == "POST" and not services.user_can_upload_application_documents(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to upload application documents.",
        )

    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    required_permission = (
        services.APPLICATION_READ_PERMISSION
        if request.method == "GET"
        else services.APPLICATION_DOCUMENT_UPLOAD_PERMISSION
    )
    object_access = services.evaluate_application_object_access(
        application,
        user,
        required_permission,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)

    if request.method == "GET":
        documents = [
            services.serialize_application_document(application_document)
            for application_document in services.list_application_documents(application)
        ]
        return success_response(
            {"loan_application_id": str(application.loan_application_id), "items": documents},
            request,
        )

    try:
        body = parse_json_body(request)
        application_document = services.attach_application_document(
            application,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Application document payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_application_document(application_document), request)


@require_http_methods(["POST"])
def application_document_verify(request, application_document_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_verify_application_documents(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to verify application documents.",
        )
    application_document = services.get_application_document(application_document_id)
    if application_document is None:
        return error_response(request, 404, "NOT_FOUND", "Application document was not found.")
    object_access = services.evaluate_application_object_access(
        application_document.loan_application,
        user,
        services.APPLICATION_DOCUMENT_VERIFY_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        body = parse_json_body(request)
        application_document = services.verify_application_document(
            application_document,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Application document payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_application_document(application_document), request)


@require_http_methods(["GET", "POST"])
def loan_application_document_checklist(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_READ_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    if request.method == "POST":
        try:
            parse_json_body(request)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Application document payload failed validation.",
                services.validation_field_errors(exc),
            )
    return success_response(services.build_document_checklist(application), request)


@require_http_methods(["GET"])
def loan_application_completeness_check(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_READ_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    return success_response(services.build_completeness_workbench(application), request)


@require_http_methods(["POST"])
def loan_application_completeness_pass(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to complete-check loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        parse_json_body(request)
        invalid_state_message = services.completeness_pass_invalid_state_message(application)
        if invalid_state_message:
            return error_response(
                request,
                409,
                "INVALID_STATE_TRANSITION",
                invalid_state_message,
            )
        services.validate_completeness_ready_for_reference(application)
        application = services.generate_reference_after_completeness_pass(
            application,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
            permissions,
        )
    except services.LoanApplicationValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Completeness check failed validation.",
            services.validation_field_errors(exc),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Completeness check failed validation.",
            services.validation_field_errors(exc),
        )
    except InvalidStateTransition as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_application(application), request)


@require_http_methods(["GET"])
def loan_application_eligibility_assessment(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = EligibilityAssessmentModule().get(
            actor=user,
            application_id=loan_application_id,
            actor_permissions=permissions,
        )
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def loan_application_eligibility_assessment_run(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        parse_json_body(request)
        result = EligibilityAssessmentModule().run(
            actor=user,
            application_id=loan_application_id,
            request_meta=_credit_request_meta(request),
            actor_permissions=permissions,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Eligibility assessment payload failed validation.",
            services.validation_field_errors(exc),
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def loan_application_loan_limit_calculate(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = LoanLimitCalculator().calculate_for_application(
            actor=user,
            application_id=loan_application_id,
            payload=lambda: parse_json_body(request),
            request_meta=_credit_request_meta(request),
            actor_permissions=permissions,
        )
    except CreditModuleValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan-limit calculation failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Loan-limit calculation failed validation.",
            services.validation_field_errors(exc),
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["GET"])
def loan_application_sanction_case(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = SanctionHandoffModule().get_pending(
            actor=user,
            application_id=loan_application_id,
            actor_permissions=permissions,
        )
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["GET"])
def loan_application_loan_limit_assessment(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = LoanLimitCalculator().get_assessment(
            actor=user,
            application_id=loan_application_id,
            actor_permissions=permissions,
        )
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["GET", "POST", "PATCH"])
def loan_application_appraisal_note(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        if request.method == "GET":
            result = AppraisalWorkflow().get(
                actor=user,
                application_id=loan_application_id,
                actor_permissions=permissions,
            )
        else:
            result = AppraisalWorkflow().create_or_update(
                actor=user,
                application_id=loan_application_id,
                payload=parse_json_body(request),
                partial=request.method == "PATCH",
                request_meta=_credit_request_meta(request),
                actor_permissions=permissions,
            )
    except CreditModuleValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Appraisal note payload failed validation.",
            exc.field_errors,
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def appraisal_note_submit_for_review(request, loan_appraisal_note_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = AppraisalWorkflow().submit_for_review(
            actor=user,
            appraisal_id=loan_appraisal_note_id,
            payload=parse_json_body(request),
            request_meta=_credit_request_meta(request),
            actor_permissions=permissions,
        )
    except CreditModuleValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Appraisal submission failed validation.",
            exc.field_errors,
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def appraisal_note_review(request, loan_appraisal_note_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    payload = parse_json_body(request)
    try:
        result = AppraisalWorkflow().review(
            actor=user,
            appraisal_id=loan_appraisal_note_id,
            decision=payload.get("decision"),
            comments=payload.get("review_comments"),
            payload_fields=payload,
            request_meta=_credit_request_meta(request),
            actor_permissions=permissions,
        )
    except CreditModuleValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Appraisal review failed validation.",
            exc.field_errors,
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def appraisal_note_revalidate_prerequisites(request, loan_appraisal_note_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = AppraisalWorkflow().revalidate_prerequisites(
            actor=user,
            appraisal_id=loan_appraisal_note_id,
            payload=parse_json_body(request),
            request_meta=_credit_request_meta(request),
            actor_permissions=permissions,
        )
    except CreditModuleValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Appraisal prerequisite revalidation failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Appraisal prerequisite revalidation failed validation.",
            services.validation_field_errors(exc),
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def loan_application_submit_to_sanction(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    try:
        result = AppraisalWorkflow().submit_to_sanction(
            actor=user,
            application_id=loan_application_id,
            payload=parse_json_body(request),
            request_meta=_credit_request_meta(request),
            actor_permissions=permissions,
        )
    except CreditModuleValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Sanction submission failed validation.",
            exc.field_errors,
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Sanction submission failed validation.",
            services.validation_field_errors(exc),
        )
    except CreditModuleInvalidStateError as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    except (
        CreditModuleNotFound,
        CreditModuleObjectAccessDenied,
        CreditModulePermissionDenied,
    ) as exc:
        return _credit_module_error_response(request, exc)
    return success_response(result.snapshot, request)


@require_http_methods(["POST"])
def loan_application_return_with_deficiencies(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to complete-check loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        body = parse_json_body(request)
        result = services.return_application_with_deficiencies(
            application,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except services.LoanApplicationValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Deficiency return failed validation.",
            services.validation_field_errors(exc),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Deficiency return failed validation.",
            services.validation_field_errors(exc),
        )
    except (services.LoanApplicationInvalidStateError, InvalidStateTransition) as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_returned_deficiencies(result), request)


@require_http_methods(["GET"])
def loan_application_deficiencies(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_read_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_READ_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    deficiencies = [
        services.serialize_application_deficiency(deficiency)
        for deficiency in services.list_application_deficiencies(application)
    ]
    return success_response(
        {"loan_application_id": str(application.loan_application_id), "items": deficiencies},
        request,
    )


@require_http_methods(["POST"])
def application_deficiency_resolve(request, deficiency_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to complete-check loan applications.",
        )
    deficiency = services.get_application_deficiency(deficiency_id)
    if deficiency is None:
        return error_response(request, 404, "NOT_FOUND", "Deficiency was not found.")
    object_access = services.evaluate_application_object_access(
        deficiency.loan_application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        body = parse_json_body(request)
        deficiency = services.resolve_application_deficiency(
            deficiency,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Deficiency resolution failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_application_deficiency(deficiency), request)


@require_http_methods(["POST"])
def loan_application_rejection_note(request, loan_application_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to complete-check loan applications.",
        )
    application = services.get_application(loan_application_id)
    if application is None:
        return error_response(request, 404, "NOT_FOUND", "Loan application was not found.")
    object_access = services.evaluate_application_object_access(
        application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        body = parse_json_body(request)
        rejection_note = services.create_rejection_note(
            application,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Rejection note payload failed validation.",
            services.validation_field_errors(exc),
        )
    except (services.LoanApplicationInvalidStateError, InvalidStateTransition) as exc:
        return error_response(request, 409, "INVALID_STATE_TRANSITION", str(exc))
    return success_response(services.serialize_rejection_note(rejection_note), request)


@require_http_methods(["POST"])
def rejection_note_send(request, rejection_note_id):
    user, permissions, response = http_auth.authenticated_user_with_permissions(request)
    if response is not None:
        return response
    if not services.user_can_complete_check_applications(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to complete-check loan applications.",
        )
    rejection_note = services.get_rejection_note(rejection_note_id)
    if rejection_note is None:
        return error_response(request, 404, "NOT_FOUND", "Rejection note was not found.")
    object_access = services.evaluate_application_object_access(
        rejection_note.loan_application,
        user,
        services.APPLICATION_COMPLETE_CHECK_PERMISSION,
        permissions,
    )
    if not object_access.allowed:
        return _object_access_denied_response(request, object_access)
    try:
        body = parse_json_body(request)
        rejection_note = services.send_rejection_note(
            rejection_note,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except (services.LoanApplicationValidationError, ValidationError) as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Rejection note payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_rejection_note(rejection_note), request)


def _object_access_denied_response(request, object_access):
    return error_response(
        request,
        403,
        object_access.error_code or "OBJECT_ACCESS_DENIED",
        "You do not have access to this loan application.",
    )


def _credit_request_meta(request):
    return {
        "request_id": request.headers.get("X-Request-ID"),
        "ip_address": request_ip(request),
        "user_agent": request_user_agent(request),
    }


def _credit_module_error_response(request, exc):
    if isinstance(exc, CreditModuleObjectAccessDenied):
        return _object_access_denied_response(request, exc.object_access)
    if isinstance(exc, CreditModulePermissionDenied):
        return error_response(request, 403, "FORBIDDEN", exc.message)
    if isinstance(exc, CreditModuleNotFound):
        return error_response(request, 404, "NOT_FOUND", exc.message)
    raise exc
