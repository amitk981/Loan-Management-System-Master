"""Privacy-safe S02 aggregate search over domain-owned records."""

import uuid
from math import ceil

from django.core.cache import cache
from django.core.exceptions import ValidationError

from sfpcl_credit.applications.modules import search_facade as application_search
from sfpcl_credit.documents import search_facade as document_search
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.identity.modules import search_facade as audit_search
from sfpcl_credit.loans.modules import search_facade as loan_search
from sfpcl_credit.members import search_facade as member_search
from sfpcl_credit.sap_workflow.modules import search_facade as sap_search
from sfpcl_credit.security_instruments import search_facade as security_search

# Retain the original review probe's patch target; production access is exclusively
# delegated to ``security_search`` below and never queries this compatibility alias.
BlankDatedCheque = security_search.BlankDatedCheque


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
CONTINUATION_TTL_SECONDS = 300
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
    continuation = request["continuation"]
    query = request["search"]
    if continuation:
        retained = cache.get(_continuation_key(actor, continuation))
        if not retained:
            raise ValidationError(
                {"continuation": "Search continuation is invalid or expired."}
            )
        query = retained["query"]
        if request["page_size"] not in (None, retained["page_size"]):
            raise ValidationError(
                {"page_size": "Cannot change page size for a continued search."}
            )
        page_size = retained["page_size"]
    else:
        continuation = uuid.uuid4().hex
        page_size = request["page_size"]
        cache.set(
            _continuation_key(actor, continuation),
            {"query": query, "page_size": page_size},
            CONTINUATION_TTL_SECONDS,
        )
    permissions = set(auth_service.effective_permission_codes(actor))
    pages = request["pages"]
    groups = {}
    input_kind = _input_kind(query)
    direct_domain_match = input_kind == "generic"

    related_member_ids = set()
    if input_kind in {"security", "numeric"}:
        related_member_ids.update(security_search.matching_member_ids(
            actor=actor, permissions=permissions, query=query
        ))
    if input_kind == "sap":
        related_member_ids.update(
            sap_search.matching_member_ids(permissions=permissions, query=query)
        )
    if input_kind == "numeric" and len(query) == 4:
        related_member_ids.update(
        member_search.matching_bank_member_ids(
            actor=actor, permissions=permissions, query=query
        )
        )
    if input_kind in {"member_sensitive", "numeric"}:
        related_member_ids.update(
            member_search.matching_sensitive_member_ids(
                actor=actor, permissions=permissions, query=query
            )
        )
    if direct_domain_match:
        related_member_ids.update(loan_search.matching_member_ids(
            actor=actor, permissions=permissions, query=query
        ))
    application_rows = application_search.matching_applications(
        actor=actor,
        permissions=permissions,
        query=query,
        related_member_ids=related_member_ids,
        allow_direct_match=direct_domain_match,
        limit=MAX_GROUP_RESULTS,
    )
    application_ids = {row.loan_application_id for row in application_rows}
    account_rows = loan_search.matching_accounts(
        actor=actor,
        permissions=permissions,
        query=query,
        related_member_ids=related_member_ids,
        allow_direct_match=direct_domain_match,
        limit=MAX_GROUP_RESULTS,
    )
    account_group_authorised = account_rows is not None
    account_rows = account_rows or []
    account_ids = {row.loan_account_id for row in account_rows}
    related_member_ids.update(row.member_id for row in application_rows)
    related_member_ids.update(row.member_id for row in account_rows)
    member_rows = member_search.matching_members(
        actor=actor,
        permissions=permissions,
        query=query,
        related_member_ids=related_member_ids,
        limit=MAX_GROUP_RESULTS,
    )
    member_ids = {row.member_id for row in member_rows}

    if MEMBER_READ in permissions:
        groups["members"] = paginate_group(
            [_member_card(row) for row in member_rows], pages["members"], page_size
        )
    if APPLICATION_READ in permissions:
        groups["loan_applications"] = paginate_group(
            [_application_card(row, actor) for row in application_rows],
            pages["loan_applications"],
            page_size,
        )
    if ACCOUNT_READ in permissions and account_group_authorised:
        groups["loan_accounts"] = paginate_group(
            [_account_card(row, permissions) for row in account_rows],
            pages["loan_accounts"],
            page_size,
        )
        repayment_rows = loan_search.matching_repayments(
            permissions=permissions,
            account_ids=account_ids,
            limit=MAX_GROUP_RESULTS,
        )
        groups["repayments"] = paginate_group(
            [_repayment_card(row) for row in repayment_rows],
            pages["repayments"],
            page_size,
        )
    document_ids = set()
    if DOCUMENT_READ in permissions and APPLICATION_READ in permissions:
        document_rows, document_ids = document_search.matching_documents(
            permissions=permissions,
            query=query,
            application_ids=application_ids,
            limit=MAX_GROUP_RESULTS,
        )
        application_documents, loan_documents = document_rows
        document_cards = [_application_document_card(row) for row in application_documents]
        document_cards.extend(_loan_document_card(row) for row in loan_documents)
        document_cards.sort(key=lambda row: (row["last_updated_at"], row["id"]), reverse=True)
        groups["documents"] = paginate_group(
            document_cards[:MAX_GROUP_RESULTS], pages["documents"], page_size
        )
    if any(code.startswith("compliance.") and code.endswith(".read") for code in permissions):
        compliance_rows = list(
            _compliance_provider(actor=actor, search=query, member_ids=frozenset(member_ids))
        )[:MAX_GROUP_RESULTS]
        groups["compliance_records"] = paginate_group(
            compliance_rows, pages["compliance_records"], page_size
        )
    if AUDIT_READ in permissions:
        entity_ids = member_ids | application_ids | account_ids | document_ids
        audit_rows = audit_search.matching_audit_logs(
            permissions=permissions, entity_ids=entity_ids, limit=MAX_GROUP_RESULTS
        )
        groups["audit_logs"] = paginate_group(
            [_audit_card(row) for row in audit_rows], pages["audit_logs"], page_size
        )
    return {"groups": groups, "continuation": continuation}


def _continuation_key(actor, continuation):
    return f"global-search-continuation:{actor.user_id}:{continuation}"


def _input_kind(query):
    upper = query.upper()
    if upper.startswith(("CHEQUE-", "CDSL-")):
        return "security"
    if upper.startswith("SAP-"):
        return "sap"
    try:
        uuid.UUID(query)
    except (ValueError, TypeError, AttributeError):
        pass
    else:
        return "security"
    if (
        (len(upper) == 10 and upper[:5].isalpha() and upper[5:9].isdigit() and upper[-1].isalpha())
        or (len(query) == 12 and query.isdigit())
        or "@" in query
    ):
        return "member_sensitive"
    if query.isdigit():
        return "numeric"
    return "generic"


def _validate_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError({"non_field_errors": "Request body must be an object."})
    unknown = set(payload) - {"search", "continuation", "page_size", "pages"}
    errors = {key: "Unknown field." for key in sorted(unknown)}
    value = payload.get("search")
    continuation = payload.get("continuation")
    if (value is None) == (continuation is None):
        errors["non_field_errors"] = "Provide exactly one of search or continuation."
    if value is not None:
        if not isinstance(value, str):
            errors["search"] = "Must be a string."
            value = ""
        value = value.strip()
        if len(value) < 2 or len(value) > 120:
            errors["search"] = "Must contain between 2 and 120 characters."
        elif any(char in value for char in _FORBIDDEN_SEARCH_CHARS):
            errors["search"] = "Wildcard and control characters are not allowed."
    if continuation is not None:
        if (
            not isinstance(continuation, str)
            or len(continuation) != 32
            or any(char not in "0123456789abcdef" for char in continuation)
        ):
            errors["continuation"] = "Must be an opaque search continuation."
            continuation = None
    page_size = payload.get("page_size")
    if page_size is None:
        page_size = None if continuation is not None else 10
    elif not isinstance(page_size, int) or isinstance(page_size, bool) or page_size < 1:
        errors["page_size"] = "Must be a positive integer."
        page_size = 10
    if page_size is not None:
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
    return {
        "search": value,
        "continuation": continuation,
        "page_size": page_size,
        "pages": pages,
    }


def validation_errors(exc):
    if hasattr(exc, "message_dict"):
        return {key: messages[0] for key, messages in exc.message_dict.items()}
    return {"non_field_errors": exc.messages[0]}


def paginate_group(rows, page, page_size):
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


def _account_card(row, permissions):
    updater = row.loan_application.updated_by_user or row.loan_application.received_by_user
    identifier = (
        row.sap_customer_code.sap_customer_code
        if row.sap_customer_code_id and sap_search.READ_PERMISSION in permissions
        else row.loan_account_number
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
    "paginate_group",
    "register_compliance_provider",
    "search",
    "validation_errors",
]
