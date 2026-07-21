"""Privacy-safe S02 aggregate search over domain-owned records."""

import re
import uuid
from math import ceil

from django.core.exceptions import ValidationError
from django.db.models import Q

from sfpcl_credit.applications.models import ApplicationDocument, LoanApplication
from sfpcl_credit.applications.modules.application_authority import (
    evaluate_application_object_access,
)
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.loans.models import Repayment
from sfpcl_credit.loans.modules.loan_account_read import (
    LoanAccountReadPermissionDenied,
    scoped_account_candidates,
)
from sfpcl_credit.members.models import BankAccount, Member
from sfpcl_credit.members.modules.member_authority import member_scope_predicate
from sfpcl_credit.members.protected_identity import identity_hash
from sfpcl_credit.sap_workflow.models import SapCustomerCode
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.security_instruments.models import (
    BlankDatedCheque,
    CDSLSharePledge,
    SH4ShareTransferForm,
)


MEMBER_READ = "members.member.read"
APPLICATION_READ = "applications.loan_application.read"
ACCOUNT_READ = "finance.loan_account.read"
DOCUMENT_READ = "documents.loan_document.read"
AUDIT_READ = "audit.audit_log.read"
GROUPS = (
    "members",
    "loan_applications",
    "loan_accounts",
    "documents",
    "repayments",
    "compliance_records",
    "audit_logs",
)
MAX_PAGE_SIZE = 20
MAX_GROUP_RESULTS = 100
_PAN = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
_AADHAAR = re.compile(r"^[0-9]{12}$")
_AADHAAR_LAST4 = re.compile(r"^[0-9]{4}$")
_FORBIDDEN_SEARCH_CHARS = set("%*_?[]{}\\\x00\n\r\t")


def _empty_compliance_provider(*, actor, search, member_ids):
    return []


_compliance_provider = _empty_compliance_provider


def register_compliance_provider(provider):
    """Register the 011M3-owned provider without importing future compliance models."""
    global _compliance_provider
    _compliance_provider = provider


def search(*, actor, payload):
    request = _validate_payload(payload)
    query = request["search"]
    permissions = set(auth_service.effective_permission_codes(actor))
    pages = request["pages"]
    page_size = request["page_size"]
    groups = {}

    member_rows = _member_rows(actor, permissions, query)
    member_ids = {row.member_id for row in member_rows}
    application_rows = _application_rows(actor, permissions, query, member_ids)
    application_ids = {row.loan_application_id for row in application_rows}
    account_rows = _account_rows(actor, permissions, query, member_ids)
    account_group_authorised = account_rows is not None
    account_rows = account_rows or []
    account_ids = {row.loan_account_id for row in account_rows}

    if MEMBER_READ in permissions:
        groups["members"] = _page(
            [_member_card(row) for row in member_rows], pages["members"], page_size
        )
    if APPLICATION_READ in permissions:
        groups["loan_applications"] = _page(
            [_application_card(row, actor) for row in application_rows],
            pages["loan_applications"],
            page_size,
        )
    if ACCOUNT_READ in permissions and account_group_authorised:
        groups["loan_accounts"] = _page(
            [_account_card(row) for row in account_rows], pages["loan_accounts"], page_size
        )
        repayment_rows = list(
            Repayment.objects.select_related(
                "loan_account", "member", "captured_by_user"
            )
            .filter(loan_account_id__in=account_ids)
            .order_by("-created_at", "-repayment_id")[:MAX_GROUP_RESULTS]
        )
        groups["repayments"] = _page(
            [_repayment_card(row) for row in repayment_rows],
            pages["repayments"],
            page_size,
        )
    document_ids = set()
    if DOCUMENT_READ in permissions and APPLICATION_READ in permissions:
        document_cards, document_ids = _document_cards(query, application_ids)
        groups["documents"] = _page(
            document_cards, pages["documents"], page_size
        )
    if any(code.startswith("compliance.") and code.endswith(".read") for code in permissions):
        compliance_rows = list(
            _compliance_provider(actor=actor, search=query, member_ids=frozenset(member_ids))
        )[:MAX_GROUP_RESULTS]
        groups["compliance_records"] = _page(
            compliance_rows, pages["compliance_records"], page_size
        )
    if AUDIT_READ in permissions:
        entity_ids = member_ids | application_ids | account_ids | document_ids
        audit_rows = list(
            AuditLog.objects.select_related("actor_user")
            .filter(entity_id__in=entity_ids)
            .order_by("-created_at", "-audit_log_id")[:MAX_GROUP_RESULTS]
        )
        groups["audit_logs"] = _page(
            [_audit_card(row) for row in audit_rows], pages["audit_logs"], page_size
        )
    return {"groups": groups}


def _validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"non_field_errors": "Request body must be an object."})
    unknown = set(payload) - {"search", "page_size", "pages"}
    errors = {key: "Unknown field." for key in sorted(unknown)}
    value = payload.get("search")
    if not isinstance(value, str):
        errors["search"] = "Must be a string."
        value = ""
    value = value.strip()
    if len(value) < 2 or len(value) > 120:
        errors["search"] = "Must contain between 2 and 120 characters."
    elif any(char in value for char in _FORBIDDEN_SEARCH_CHARS):
        errors["search"] = "Wildcard and control characters are not allowed."
    page_size = payload.get("page_size", 10)
    if not isinstance(page_size, int) or isinstance(page_size, bool) or page_size < 1:
        errors["page_size"] = "Must be a positive integer."
        page_size = 10
    page_size = min(page_size, MAX_PAGE_SIZE)
    raw_pages = payload.get("pages", {})
    if not isinstance(raw_pages, dict):
        errors["pages"] = "Must be an object."
        raw_pages = {}
    unknown_pages = set(raw_pages) - set(GROUPS)
    if unknown_pages:
        errors["pages"] = "Contains an unknown group."
    pages = {}
    for group in GROUPS:
        page = raw_pages.get(group, 1)
        if not isinstance(page, int) or isinstance(page, bool) or page < 1:
            errors[f"pages.{group}"] = "Must be a positive integer."
            page = 1
        pages[group] = page
    if errors:
        raise ValidationError(errors)
    return {"search": value, "page_size": page_size, "pages": pages}


def validation_errors(exc):
    if hasattr(exc, "message_dict"):
        return {key: messages[0] for key, messages in exc.message_dict.items()}
    return {"non_field_errors": exc.messages[0]}


def _member_rows(actor, permissions, query):
    if MEMBER_READ not in permissions:
        return []
    related_ids = set()
    related_ids.update(
        SapCustomerCode.objects.filter(sap_customer_code__iexact=query).values_list(
            "member_id", flat=True
        )
    )
    related_ids.update(
        BankAccount.objects.filter(
            owner_party_type="member", account_number_last4=query
        ).values_list("owner_party_id", flat=True)
    )
    related_ids.update(
        BlankDatedCheque.objects.filter(
            cheque_number_hash=FieldEncryption.hash_for_lookup(
                "blank_cheque.cheque_number", query
            )
        ).values_list("member_id", flat=True)
    )
    related_ids.update(
        CDSLSharePledge.objects.filter(
            pledge_sequence_number__iexact=query
        ).values_list("pledgor_member_id", flat=True)
    )
    try:
        sh4_id = uuid.UUID(query)
    except (ValueError, TypeError, AttributeError):
        sh4_id = None
    if sh4_id:
        related_ids.update(
            SH4ShareTransferForm.objects.filter(pk=sh4_id).values_list(
                "member_id", flat=True
            )
        )
    related_ids.update(
        LoanApplication.objects.filter(
            application_reference_number__iexact=query
        ).values_list("member_id", flat=True)
    )
    from sfpcl_credit.loans.models import LoanAccount

    related_ids.update(
        LoanAccount.objects.filter(loan_account_number_normalized=query.upper()).values_list(
            "member_id", flat=True
        )
    )
    upper = query.upper()
    if _PAN.fullmatch(upper):
        predicate = Q(pan_hash=identity_hash(upper))
    elif _AADHAAR.fullmatch(query):
        predicate = Q(aadhaar_hash=identity_hash(query))
    elif _AADHAAR_LAST4.fullmatch(query):
        predicate = (
            Q(aadhaar_last4=query)
            | Q(number_of_shares=int(query))
            | Q(member_id__in=related_ids)
        )
    elif query.isdigit() and len(query) >= 10:
        predicate = Q(mobile_number=query) | Q(member_id__in=related_ids)
    elif "@" in query:
        predicate = Q(email__iexact=query) | Q(member_id__in=related_ids)
    else:
        predicate = (
            Q(legal_name__istartswith=query)
            | Q(display_name__istartswith=query)
            | Q(member_number__iexact=query)
            | Q(folio_number__iexact=query)
            | Q(member_id__in=related_ids)
        )
        if query.isdigit():
            predicate |= Q(number_of_shares=int(query))
    return list(
        Member.objects.select_related("created_by_user", "updated_by_user")
        .filter(is_deleted=False)
        .filter(member_scope_predicate(actor_user=actor, permission=MEMBER_READ))
        .filter(predicate)
        .order_by("legal_name", "member_id")[:MAX_GROUP_RESULTS]
    )


def _application_rows(actor, permissions, query, member_ids):
    if APPLICATION_READ not in permissions:
        return []
    candidates = (
        LoanApplication.objects.select_related(
            "member", "received_by_user", "created_by_user", "updated_by_user"
        )
        .filter(
            Q(application_reference_number__iexact=query) | Q(member_id__in=member_ids)
        )
        .order_by("-created_at", "-loan_application_id")[:MAX_GROUP_RESULTS]
    )
    return [
        row
        for row in candidates
        if evaluate_application_object_access(
            application=row,
            actor=actor,
            required_permission=APPLICATION_READ,
            actor_permissions=permissions,
        ).allowed
    ]


def _account_rows(actor, permissions, query, member_ids):
    if ACCOUNT_READ not in permissions:
        return None
    try:
        queryset = scoped_account_candidates(actor=actor)
    except LoanAccountReadPermissionDenied:
        return None
    return list(
        queryset.select_related(
            "member", "loan_application", "loan_application__updated_by_user",
            "loan_application__received_by_user", "sap_customer_code", "current_dpd_status",
        )
        .filter(
            Q(loan_account_number_normalized=query.upper())
            | Q(sap_customer_code__sap_customer_code__iexact=query)
            | Q(member_id__in=member_ids)
        )
        .order_by("-created_at", "-loan_account_id")[:MAX_GROUP_RESULTS]
    )


def _document_cards(query, application_ids):
    application_documents = list(
        ApplicationDocument.objects.select_related(
            "loan_application", "loan_application__member", "document_file",
            "created_by_user", "updated_by_user",
        )
        .filter(loan_application_id__in=application_ids)
        .filter(
            Q(document_file__file_name__istartswith=query)
            | Q(loan_application_id__in=application_ids)
        )
        .order_by("-created_at", "-application_document_id")[:MAX_GROUP_RESULTS]
    )
    loan_documents = list(
        LoanDocument.objects.select_related(
            "loan_application", "loan_application__member", "document",
            "verified_by_user",
        )
        .filter(loan_application_id__in=application_ids)
        .filter(
            Q(document__file_name__istartswith=query)
            | Q(loan_application_id__in=application_ids)
        )
        .order_by("-created_at", "-loan_document_id")[:MAX_GROUP_RESULTS]
    )
    cards = [_application_document_card(row) for row in application_documents]
    cards.extend(_loan_document_card(row) for row in loan_documents)
    cards.sort(key=lambda row: (row["last_updated_at"], row["id"]), reverse=True)
    ids = {row.application_document_id for row in application_documents}
    ids.update(row.loan_document_id for row in loan_documents)
    return cards[:MAX_GROUP_RESULTS], ids


def _page(rows, page, page_size):
    rows = list(rows)[:MAX_GROUP_RESULTS]
    total = len(rows)
    pages = ceil(total / page_size) if total else 1
    page = min(page, pages)
    start = (page - 1) * page_size
    return {
        "items": rows[start : start + page_size],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total,
            "total_pages": pages,
            "has_next": page < pages,
            "has_previous": page > 1,
        },
    }


def build_result_card(*, row_id, result_type, title, identifier, status, risk_status,
                      amount, owner, updated_at, updated_by, quick_actions):
    """Build the shared S02 card contract, including future compliance results."""
    return {
        "id": str(row_id),
        "result_type": result_type,
        "title": title,
        "identifier": identifier,
        "status": status,
        "risk_status": risk_status,
        "amount": f"{amount:.2f}" if amount is not None else None,
        "owner": owner,
        "last_updated_at": updated_at.isoformat().replace("+00:00", "Z"),
        "last_updated_by": updated_by,
        "quick_actions": quick_actions,
    }


def _action(label, page, entity_id):
    return {"label": label, "page": page, "entity_id": str(entity_id)}


def _member_card(row):
    actor = row.updated_by_user or row.created_by_user
    return build_result_card(
        row_id=row.member_id, result_type="member", title=row.display_name,
        identifier=row.folio_number, status=row.membership_status,
        risk_status=row.default_status, amount=None,
        owner=actor.full_name if actor else None,
        updated_at=row.updated_at or row.created_at,
        updated_by=actor.full_name if actor else None,
        quick_actions=[_action("Open", "members/profile", row.member_id)],
    )


def _application_card(row, actor):
    updater = row.updated_by_user or row.received_by_user
    actions = [_action("Open", "applications/detail", row.loan_application_id)]
    permissions = set(auth_service.effective_permission_codes(actor))
    if DOCUMENT_READ in permissions:
        actions.append(_action("View documents", "documentation", row.loan_application_id))
    return build_result_card(
        row_id=row.loan_application_id, result_type="loan_application",
        title=row.member.display_name,
        identifier=row.application_reference_number or str(row.loan_application_id),
        status=row.current_stage, risk_status=row.application_status,
        amount=row.required_loan_amount,
        owner=updater.full_name if updater else None,
        updated_at=row.updated_at or row.created_at,
        updated_by=updater.full_name if updater else None,
        quick_actions=actions,
    )


def _account_card(row):
    updater = row.loan_application.updated_by_user or row.loan_application.received_by_user
    identifier = (
        row.sap_customer_code.sap_customer_code
        if row.sap_customer_code_id else row.loan_account_number
    )
    return build_result_card(
        row_id=row.loan_account_id, result_type="loan_account",
        title=row.loan_account_number, identifier=identifier,
        status=row.loan_account_status,
        risk_status=(row.current_dpd_status.sop_bucket if row.current_dpd_status_id else None),
        amount=row.total_outstanding, owner="Loan Servicing",
        updated_at=row.created_at,
        updated_by=updater.full_name if updater else None,
        quick_actions=[_action("View loan account", "loan-accounts/detail", row.loan_account_id)],
    )


def _application_document_card(row):
    updater = row.updated_by_user or row.created_by_user
    return build_result_card(
        row_id=row.application_document_id, result_type="document",
        title=row.document_file.file_name,
        identifier=row.loan_application.application_reference_number,
        status=row.verification_status, risk_status=None, amount=None,
        owner=updater.full_name if updater else None,
        updated_at=row.updated_at or row.created_at,
        updated_by=updater.full_name if updater else None,
        quick_actions=[_action("View documents", "documentation", row.loan_application_id)],
    )


def _loan_document_card(row):
    title = row.document.file_name if row.document_id else row.document_type.replace("_", " ").title()
    return build_result_card(
        row_id=row.loan_document_id, result_type="document", title=title,
        identifier=row.loan_application.application_reference_number,
        status=row.verification_status, risk_status=row.execution_status,
        amount=None, owner=row.verified_by_user.full_name if row.verified_by_user_id else None,
        updated_at=row.verified_at or row.created_at,
        updated_by=row.verified_by_user.full_name if row.verified_by_user_id else None,
        quick_actions=[_action("View documents", "documentation", row.loan_application_id)],
    )


def _repayment_card(row):
    return build_result_card(
        row_id=row.repayment_id, result_type="repayment",
        title=f"Repayment for {row.loan_account.loan_account_number}",
        identifier=row.loan_account.loan_account_number,
        status=row.allocation_status, risk_status=row.sap_posting_status,
        amount=row.amount_received, owner=row.captured_by_user.full_name,
        updated_at=row.created_at, updated_by=row.captured_by_user.full_name,
        quick_actions=[_action("View loan account", "loan-accounts/detail", row.loan_account_id)],
    )


def _audit_card(row):
    actor = row.actor_user.full_name if row.actor_user_id else "System"
    return build_result_card(
        row_id=row.audit_log_id, result_type="audit_log", title=row.action,
        identifier=row.entity_type, status="recorded", risk_status=None,
        amount=None, owner=actor, updated_at=row.created_at, updated_by=actor,
        quick_actions=[],
    )


__all__ = [
    "build_result_card",
    "register_compliance_provider",
    "search",
    "validation_errors",
]
