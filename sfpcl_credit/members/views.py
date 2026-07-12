from django.core.exceptions import PermissionDenied, ValidationError
from django.views.decorators.http import require_GET, require_http_methods
from django.utils.dateparse import parse_date

from sfpcl_credit.api import (
    error_response,
    list_response,
    parse_json_body,
    request_ip,
    request_user_agent,
    success_response,
)
from sfpcl_credit.identity.modules import http_auth
from sfpcl_credit.members import services
from sfpcl_credit.members.modules import MemberRegistry
from sfpcl_credit.members.modules.active_member_status import (
    ActiveMemberObjectAccessDenied,
    ActiveMemberStatusConflict,
    ActiveMemberStatusModule,
)


def _serialize_member(member, user):
    pending_change = (
        member.identity_change_requests.filter(status="pending")
        .order_by("created_at")
        .first()
    )
    return services.serialize_member_profile(
        member,
        user,
        MemberRegistry.identity_approval_action(member, pending_change, user),
    )


@require_http_methods(["GET", "POST"])
def member_collection(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "POST":
        try:
            member = MemberRegistry.create(
                parse_json_body(request), user, request_ip(request), request_user_agent(request)
            )
        except PermissionDenied as exc:
            return error_response(request, 403, "FORBIDDEN", str(exc))
        except ValidationError as exc:
            return error_response(request, 400, "VALIDATION_ERROR", "Member payload failed validation.", services.validation_field_errors(exc))
        return success_response(_serialize_member(member, user), request)
    if not services.user_can_read_members(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read members.",
        )
    try:
        data, pagination = services.paginated_members(request.GET)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Member directory query failed validation.",
            services.validation_field_errors(exc),
        )
    return list_response(data, pagination, request)


@require_http_methods(["GET", "PATCH"])
def member_detail(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "PATCH":
        return _member_update_response(request, member_id, user, reverification=False)
    try:
        member = MemberRegistry.get(member_id, user)
    except PermissionDenied as exc:
        code = "FORBIDDEN" if str(exc).startswith("Missing required permission:") else "OBJECT_ACCESS_DENIED"
        return error_response(request, 403, code, str(exc))
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    return success_response(_serialize_member(member, user), request)


@require_http_methods(["POST"])
def member_reverification(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_update_members(user):
        return error_response(request, 403, "FORBIDDEN", "You do not have permission to update members.")
    return member_identity_change_requests(request, member_id)


@require_http_methods(["POST"])
def member_identity_change_requests(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return response
    try:
        change = MemberRegistry.request_identity_change(member_id, parse_json_body(request), user)
    except PermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", str(exc))
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Identity change request failed validation.", services.validation_field_errors(exc))
    if change is None: return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    return success_response({"identity_change_request_id": str(change.identity_change_request_id), "member_id": str(change.member_id), "status": change.status, "member_version": change.member_version}, request)


@require_http_methods(["POST"])
def approve_member_identity_change(request, request_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None: return response
    try:
        parse_json_body(request)
        member = MemberRegistry.approve_identity_change(request_id, user)
    except PermissionDenied as exc:
        code = "OBJECT_ACCESS_DENIED" if str(exc) == "You cannot access this member." else "FORBIDDEN"
        return error_response(request, 403, code, str(exc))
    except services.MemberWriteConflict as exc:
        return error_response(request, 409, exc.code, exc.message, exc.field_errors)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Approval payload failed validation.", services.validation_field_errors(exc))
    if member is None: return error_response(request, 404, "NOT_FOUND", "Identity change request was not found.")
    return success_response(_serialize_member(member, user), request)


def _member_update_response(request, member_id, user, reverification):
    try:
        member = MemberRegistry.update(member_id, parse_json_body(request), user, request_ip(request), request_user_agent(request))
    except PermissionDenied as exc:
        return error_response(request, 403, "FORBIDDEN", str(exc))
    except services.MemberWriteConflict as exc:
        if exc.audit_rejection:
            services.audit_identity_change_rejected(
                user, member_id, sorted(exc.field_errors), request_ip(request), request_user_agent(request)
            )
        return error_response(request, 409, exc.code, exc.message, exc.field_errors)
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Member payload failed validation.", services.validation_field_errors(exc))
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    return success_response(_serialize_member(member, user), request)


@require_http_methods(["POST"])
def reveal_sensitive_field(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    body = {}
    try:
        body = parse_json_body(request)
        field_name, reason = services.validate_sensitive_reveal_payload(body)
    except ValidationError as exc:
        audit_field_name = body.get("field_name") if isinstance(body.get("field_name"), str) else None
        audit_reason = body.get("reason") if isinstance(body.get("reason"), str) else None
        services.audit_sensitive_reveal_denied(
            user,
            member_id,
            audit_field_name,
            audit_reason,
            "validation_failed",
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Sensitive reveal payload failed validation.",
            services.validation_field_errors(exc),
        )

    if not services.user_can_read_members(user):
        services.audit_sensitive_reveal_denied(
            user,
            member_id,
            field_name,
            reason,
            "missing_base_read_permission",
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read members.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        services.audit_sensitive_reveal_denied(
            user,
            member_id,
            field_name,
            reason,
            "member_not_found",
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if not services.user_can_reveal_sensitive_field(user, field_name):
        services.audit_sensitive_reveal_denied(
            user,
            member.member_id,
            field_name,
            reason,
            "missing_field_permission",
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
        return error_response(
            request,
            403,
            "SENSITIVE_FIELD_ACCESS_DENIED",
            "You do not have permission to reveal this sensitive field.",
        )

    try:
        data = services.reveal_member_sensitive_field(
            member,
            field_name,
            reason,
            user,
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
    except ValidationError as exc:
        services.audit_sensitive_reveal_denied(
            user,
            member.member_id,
            field_name,
            reason,
            "source_value_unavailable",
            request_ip(request),
            request_user_agent(request),
            request.headers.get("X-Request-ID"),
        )
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Sensitive reveal payload failed validation.",
            services.validation_field_errors(exc),
        )
    response = success_response(data, request)
    response["Cache-Control"] = "no-store"
    response["Pragma"] = "no-cache"
    return response


@require_http_methods(["GET", "POST"])
def member_nominees(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_nominees(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read nominees.",
        )
    if request.method == "POST" and not services.user_can_create_nominees(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create nominees.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_nominees(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Nominee query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        nominee = services.create_nominee(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except services.NomineeValidationError as exc:
        return error_response(request, 400, exc.code, exc.message, exc.field_errors)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Nominee payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_nominee(nominee), request)


@require_http_methods(["GET", "POST"])
def member_shareholdings(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_shareholdings(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read shareholdings.",
        )
    if request.method == "POST" and not services.user_can_create_shareholdings(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create shareholdings.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_shareholdings(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Shareholding query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        shareholding = services.create_shareholding(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Shareholding payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_shareholding(shareholding), request)


@require_http_methods(["GET", "POST"])
def member_produce_supply_records(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_members(user):
        return error_response(request, 403, "FORBIDDEN", "You do not have permission to read produce supply records.")
    if request.method == "POST" and not services.user_can_capture_produce_supply(user):
        return error_response(request, 403, "FORBIDDEN", "You do not have permission to capture produce supply records.")
    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    if request.method == "GET":
        return success_response(
            [services.serialize_produce_supply_record(row, user) for row in member.produce_supply_records.all()],
            request,
        )
    try:
        record = services.create_produce_supply_record(
            member, parse_json_body(request), user, request_ip(request), request_user_agent(request)
        )
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Produce supply payload failed validation.", services.validation_field_errors(exc))
    except services.ProduceSupplyConflict as exc:
        return error_response(request, 409, exc.code, exc.message, exc.field_errors)
    return success_response(services.serialize_produce_supply_record(record, user), request)


@require_http_methods(["POST"])
def produce_supply_record_verify(request, record_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    try:
        body = parse_json_body(request)
        record = services.verify_produce_supply_record(
            record_id, body.get("version"), user, request_ip(request), request_user_agent(request)
        )
    except PermissionError as exc:
        return error_response(request, 403, "FORBIDDEN", str(exc))
    except ValidationError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Supply verification payload failed validation.", services.validation_field_errors(exc))
    except services.ProduceSupplyConflict as exc:
        return error_response(request, 409, exc.code, exc.message, exc.field_errors)
    if record is None:
        return error_response(request, 404, "NOT_FOUND", "Produce supply record was not found.")
    return success_response(services.serialize_produce_supply_record(record, user), request)


@require_http_methods(["POST"])
def active_member_status_verify(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    body = parse_json_body(request)
    if not isinstance(body, dict):
        return error_response(request, 400, "VALIDATION_ERROR", "Active-member verification payload failed validation.", {"non_field_errors": "This field must be an object."})
    allowed_fields = {"result_id", "as_of_date", "decision", "reason", "version"}
    unknown_fields = sorted(set(body) - allowed_fields)
    if unknown_fields:
        return error_response(
            request, 400, "VALIDATION_ERROR",
            "Active-member verification payload failed validation.",
            {field: "Unknown field." for field in unknown_fields},
        )
    if not body.get("as_of_date"):
        return error_response(
            request, 400, "VALIDATION_ERROR",
            "Active-member verification payload failed validation.",
            {"as_of_date": "This field is required."},
        )
    as_of_date = parse_date(body.get("as_of_date", "")) if body.get("as_of_date") else None
    if body.get("as_of_date") and as_of_date is None:
        return error_response(request, 400, "VALIDATION_ERROR", "Active-member verification payload failed validation.", {"as_of_date": "Enter a valid ISO date."})
    try:
        result = ActiveMemberStatusModule().verify(
            actor=user,
            member_id=member_id,
            result_id=body.get("result_id"),
            decision=body.get("decision"),
            reason=body.get("reason"),
            version=body.get("version"),
            as_of_date=as_of_date,
        )
    except PermissionError as exc:
        return error_response(request, 403, "FORBIDDEN", str(exc))
    except ActiveMemberObjectAccessDenied as exc:
        return error_response(request, 403, "OBJECT_ACCESS_DENIED", str(exc))
    except ValueError as exc:
        return error_response(request, 400, "VALIDATION_ERROR", "Active-member verification payload failed validation.", {"non_field_errors": str(exc)})
    except ActiveMemberStatusConflict as exc:
        return error_response(request, 409, exc.code, exc.message)
    except services.Member.DoesNotExist:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    return success_response(result, request)


@require_http_methods(["GET", "POST"])
def member_land_holdings(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_land_crop(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read member land and crop records.",
        )
    if request.method == "POST" and not services.user_can_create_land_crop(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create member land and crop records.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_land_holdings(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Land holding query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        land_holding = services.create_land_holding(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Land holding payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_land_holding(land_holding), request)


@require_http_methods(["GET", "POST"])
def member_crop_plans(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_land_crop(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read member land and crop records.",
        )
    if request.method == "POST" and not services.user_can_create_land_crop(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create member land and crop records.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_crop_plans(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Crop plan query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        crop_plan = services.create_crop_plan(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Crop plan payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_crop_plan(crop_plan), request)


@require_http_methods(["GET", "POST"])
def member_bank_accounts(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_bank_metadata(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read member bank account metadata.",
        )
    if request.method == "POST" and not services.user_can_create_bank_metadata(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create member bank account metadata.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_bank_accounts(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Bank account query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        bank_account = services.create_bank_account(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Bank account payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_bank_account(bank_account), request)


@require_http_methods(["GET", "POST"])
def member_cancelled_cheques(request, member_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_bank_metadata(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read member cancelled cheque metadata.",
        )
    if request.method == "POST" and not services.user_can_create_bank_metadata(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create member cancelled cheque metadata.",
        )

    member = services.get_accessible_member(member_id)
    if member is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")

    if request.method == "GET":
        try:
            data, pagination = services.paginated_cancelled_cheques(member, request.GET)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "Cancelled cheque query failed validation.",
                services.validation_field_errors(exc),
            )
        return list_response(data, pagination, request)

    try:
        body = parse_json_body(request)
        cancelled_cheque = services.create_cancelled_cheque(
            member,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "Cancelled cheque payload failed validation.",
            services.validation_field_errors(exc),
        )
    return success_response(services.serialize_cancelled_cheque(cancelled_cheque), request)


@require_http_methods(["GET", "POST"])
def kyc_profiles(request):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if request.method == "GET" and not services.user_can_read_kyc_profiles(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to read KYC profiles.",
        )
    if request.method == "POST" and not services.user_can_create_kyc_profiles(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to create KYC profiles.",
        )

    if request.method == "GET":
        try:
            party_type = request.GET.get("party_type")
            party_id = request.GET.get("party_id")
            if not party_type or not party_id:
                raise ValidationError(
                    {
                        "party_type": "This field is required.",
                        "party_id": "This field is required.",
                    }
                )
            member, profile = services.get_kyc_profile_for_member(party_type, party_id)
        except ValidationError as exc:
            return error_response(
                request,
                400,
                "VALIDATION_ERROR",
                "KYC profile query failed validation.",
                services.validation_field_errors(exc),
            )
        if member is None:
            return error_response(request, 404, "NOT_FOUND", "Member was not found.")
        if profile is None:
            return error_response(request, 404, "NOT_FOUND", "KYC profile was not found.")
        return success_response(services.serialize_kyc_profile(profile), request)

    try:
        body = parse_json_body(request)
        profile = services.create_kyc_profile(
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC profile payload failed validation.",
            services.validation_field_errors(exc),
        )
    if profile is None:
        return error_response(request, 404, "NOT_FOUND", "Member was not found.")
    return success_response(services.serialize_kyc_profile(profile), request)


@require_http_methods(["PATCH"])
def kyc_profile_detail(request, kyc_profile_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_update_kyc_profiles(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to update KYC profiles.",
        )
    try:
        body = parse_json_body(request)
        profile = services.update_kyc_profile(
            kyc_profile_id,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC profile payload failed validation.",
            services.validation_field_errors(exc),
        )
    if profile is None:
        return error_response(request, 404, "NOT_FOUND", "KYC profile was not found.")
    return success_response(services.serialize_kyc_profile(profile), request)


@require_http_methods(["POST"])
def kyc_profile_documents(request, kyc_profile_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_upload_kyc_documents(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to upload KYC documents.",
        )
    try:
        document = services.upload_kyc_document(kyc_profile_id, request, user)
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC document upload failed validation.",
            services.validation_field_errors(exc),
        )
    if document is None:
        return error_response(request, 404, "NOT_FOUND", "KYC profile was not found.")
    return success_response(services.serialize_kyc_document(document), request)


@require_http_methods(["POST"])
def kyc_document_verify(request, kyc_document_id):
    user, response = http_auth.authenticated_user(request)
    if response is not None:
        return response
    if not services.user_can_verify_kyc_documents(user):
        return error_response(
            request,
            403,
            "FORBIDDEN",
            "You do not have permission to verify KYC documents.",
        )
    try:
        body = parse_json_body(request)
        document = services.verify_kyc_document(
            kyc_document_id,
            body,
            user,
            request_ip(request),
            request_user_agent(request),
        )
    except ValidationError as exc:
        return error_response(
            request,
            400,
            "VALIDATION_ERROR",
            "KYC document verification failed validation.",
            services.validation_field_errors(exc),
        )
    if document is None:
        return error_response(request, 404, "NOT_FOUND", "KYC document was not found.")
    return success_response(services.serialize_kyc_document(document), request)
